import os
import json
import logging
import certifi
from pymongo import MongoClient, errors

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

def process_csv_and_upload(config):
    """Process CSV file and upload in batches to MongoDB."""
    # MongoDB Connection
    connection_string = os.getenv("MONGO_URI")
    database_name = config["database_name"]
    collection_name = config["collection_name"]
    csv_file = "/Users/francesc.mateu/Documents/GitHub/openEHR-MongoDB/testData/compositionLevel/HC3 Immunization List v0.5/Compositions/PREPRO_500k_extraccionVacunas.csv"
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
        # Process file line-by-line
        with open(csv_file, "r", encoding="utf-8") as file:
            for row_number, line in enumerate(file, start=1):
                try:
                    # Split on the first comma
                    first_comma_index = line.find(",")
                    if first_comma_index == -1:
                        logging.warning(f"Row {row_number}: Missing comma, skipped.")
                        total_errors += 1
                        continue

                    # Extract UUID and JSON content
                    uuid = line[:first_comma_index].strip().strip('"')  # First column
                    raw_json = line[first_comma_index + 1:].strip()

                    # Remove outer quotes from JSON content
                    if raw_json.startswith('"') and raw_json.endswith('"'):
                        cleaned_json = raw_json[1:-1]
                    else:
                        cleaned_json = raw_json

                    # Parse cleaned JSON
                    json_data = json.loads(cleaned_json)
                    document = {"_id": uuid, **json_data}

                    # Add document to batch
                    batch.append(document)

                    # Upload batch to MongoDB when it reaches batch_size
                    if len(batch) >= batch_size:
                        try:
                            result = collection.insert_many(batch, ordered=False)  # Proceed with unordered insert
                            inserted_count = len(result.inserted_ids)  # Count successful insertions
                            total_uploaded += inserted_count
                            print(f"Progress - Uploaded: {total_uploaded}, Skipped: {total_duplicates}, Errors: {total_errors}")
                        except errors.BulkWriteError as bwe:
                            duplicate_ids = set()  # Use a set to avoid duplicate log entries
                            for error in bwe.details['writeErrors']:
                                if error['code'] == 11000:  # Duplicate key error
                                    duplicate_id = error['keyValue']['_id']
                                    if duplicate_id not in duplicate_ids:
                                        duplicate_ids.add(duplicate_id)
                                        total_duplicates += 1
                                        logging.warning(f"Row {row_number}: Duplicate key: {duplicate_id}")
                                else:
                                    total_errors += 1
                                    logging.error(f"Row {row_number}: Insert error: {error['errmsg']}")
                            
                            # Calculate successful insertions: Total attempted - failed inserts
                            failed_inserts = len(bwe.details['writeErrors'])
                            successful_inserts = len(batch) - failed_inserts
                            total_uploaded += successful_inserts
                            print(f"Progress - Uploaded: {total_uploaded}, Skipped: {total_duplicates}, Errors: {total_errors}")
                        batch.clear()

                        # Show progress every N documents
                        if total_uploaded % progress_interval == 0:
                            print(f"Progress - Uploaded: {total_uploaded}, Skipped: {total_duplicates}, Errors: {total_errors}")

                except json.JSONDecodeError as e:
                    logging.error(f"Row {row_number}: JSON decoding error: {e}")
                    total_errors += 1

                except Exception as e:
                    logging.error(f"Row {row_number}: Unexpected error: {e}")
                    total_errors += 1

        # Upload any remaining documents
        if batch:
            try:
                collection.insert_many(batch, ordered=False)
                total_uploaded += len(batch)
                print(f"Uploaded final batch. Total Uploaded: {total_uploaded} | Skipped: {total_duplicates} | Errors: {total_errors}")
            except errors.BulkWriteError as bwe:
                for error in bwe.details['writeErrors']:
                    if error['code'] == 11000:  # Duplicate key error
                        total_duplicates += 1
                        logging.info(f"Duplicate key skipped: {error['keyValue']}")
                    else:
                        total_errors += 1
                        logging.error(f"Insert error: {error['errmsg']}")

    except Exception as e:
        logging.error(f"Error processing file: {e}")

    finally:
        client.close()
        print(f"CSV processing completed. Total Uploaded: {total_uploaded} | Skipped Duplicates: {total_duplicates} | Errors: {total_errors}")

if __name__ == "__main__":
    CONFIG_FILE = "../config.json"
    config = load_config(CONFIG_FILE)

    # Verify MongoDB URI is set
    if not os.getenv("MONGO_URI"):
        print("MongoDB connection URI (MONGO_URI) is not set in the environment. Exiting.")
        exit(1)

    process_csv_and_upload(config)