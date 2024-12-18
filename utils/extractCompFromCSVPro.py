import os
import json
import logging
import certifi
import csv
from pymongo import MongoClient, errors
from datetime import datetime

# Logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="error_log.log"
)

def load_config(config_path):
    """Load configuration from JSON file."""
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading config file: {e}")
        exit(1)

def convert_dates(document):
    """Recursively convert DV_DATE_TIME fields to ISODate."""
    if isinstance(document, dict):
        for key, value in document.items():
            if isinstance(value, dict) and "_type" in value and value["_type"] == "DV_DATE_TIME":
                # Parse the date string into a Python datetime object
                value["value"] = datetime.fromisoformat(value["value"].replace("Z", "+00:00"))
            else:
                convert_dates(value)
    elif isinstance(document, list):
        for item in document:
            convert_dates(item)

def process_csv_and_upload(config):
    """Process CSV file and upload in batches to MongoDB."""
    # MongoDB Connection
    connection_string = os.getenv("MONGO_URI")
    database_name = config["database_name"]
    collection_name = config["collection_name"]
    jsonl_file = "/Users/francesc.mateu/Documents/GitHub/openEHR-MongoDB/testData/compositionLevel/HC3 Immunization List v0.5/Compositions/PRO_1M_extraevacunas_anonim.csv"
    batch_size = config["batch_size"]

    client = MongoClient(connection_string, tlsCAFile=certifi.where())
    db = client[database_name]
    collection = db[collection_name]

    batch = []
    total_uploaded = 0
    total_duplicates = 0
    total_errors = 0
    progress_interval = 100  # Print progress every N documents

    try:
        print("Starting JSONL file processing...")

        # Process file line-by-line
        with open(jsonl_file, "r", encoding="utf-8") as file:
            for row_number, line in enumerate(file, start=1):
                try:
                    # Parse the JSON line
                    data = json.loads(line.strip())

                    # Check for 'CanonicalJSON' key
                    if "CanonicalJSON" not in data:
                        logging.error(f"Row {row_number}: Missing 'CanonicalJSON' key.")
                        total_errors += 1
                        continue

                    # Transform dates in CanonicalJSON
                    convert_dates(data["CanonicalJSON"])
                    
                    # Add full document to the batch
                    batch.append(data)

                    # Upload batch to MongoDB when it reaches batch_size
                    if len(batch) >= batch_size:
                        try:
                            result = collection.insert_many(batch, ordered=False)
                            total_uploaded += len(result.inserted_ids)
                            print(f"Chunk Processed - Uploaded: {len(result.inserted_ids)}, Total Uploaded: {total_uploaded}")
                        except errors.BulkWriteError as bwe:
                            for error in bwe.details['writeErrors']:
                                if error['code'] == 11000:  # Duplicate key error
                                    total_duplicates += 1
                                    logging.warning(f"Duplicate key skipped: {error['keyValue']}")
                                else:
                                    total_errors += 1
                                    logging.error(f"Insert error: {error['errmsg']}")
                        batch.clear()

                except json.JSONDecodeError as e:
                    logging.error(f"Row {row_number}: JSON decoding error: {e}")
                    total_errors += 1

                except Exception as e:
                    logging.error(f"Row {row_number}: Unexpected error: {e}")
                    total_errors += 1

        # Upload any remaining documents
        if batch:
            try:
                result = collection.insert_many(batch, ordered=False)
                total_uploaded += len(result.inserted_ids)
                print(f"Final Chunk Processed - Uploaded: {len(result.inserted_ids)}, Total Uploaded: {total_uploaded}")
            except errors.BulkWriteError as bwe:
                for error in bwe.details['writeErrors']:
                    if error['code'] == 11000:  # Duplicate key error
                        total_duplicates += 1
                        logging.warning(f"Duplicate key skipped: {error['keyValue']}")
                    else:
                        total_errors += 1
                        logging.error(f"Insert error: {error['errmsg']}")

    except Exception as e:
        logging.error(f"Error processing file: {e}")

    finally:
        client.close()
        print(f"JSONL processing completed. Total Uploaded: {total_uploaded} | Skipped Duplicates: {total_duplicates} | Errors: {total_errors}")

if __name__ == "__main__":
    CONFIG_FILE = "../config.json"
    config = load_config(CONFIG_FILE)

    # Verify MongoDB URI is set
    if not os.getenv("MONGO_URI"):
        print("MongoDB connection URI (MONGO_URI) is not set in the environment. Exiting.")
        exit(1)

    process_csv_and_upload(config)