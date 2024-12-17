from pymongo import MongoClient
import json
import os
from bson import json_util
import certifi
import time
import csv

mongo_uri = os.getenv("MONGO_URI")
csv_file_path = "../testData/compositionLevel/HC3 Immunization List v0.5/Compositions/PREPRO_500k_extraccionVacunas.csv"
processed_folder_path = "processed"
batch_size = 1000  # Adjust batch size for performance

def load_config(config_file):
    """Load configuration from a JSON file."""
    try:
        with open(config_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Config file {config_file} not found.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding config file: {e}")
        exit(1)

def process_csv_and_upload(connection_string, database_name, collection_name, csv_file, batch_size=1000):
    """
    Process CSV file with UUID and JSON columns and upload to MongoDB in bulk.

    Args:
        connection_string (str): MongoDB connection string.
        database_name (str): Name of the database.
        collection_name (str): Name of the collection.
        csv_file (str): Path to the CSV file.
        batch_size (int): Number of documents to upload in each batch.
    """
    try:
        client = MongoClient(connection_string, tlsCAFile=certifi.where())
        db = client[database_name]
        collection = db[collection_name]

        os.makedirs(processed_folder_path, exist_ok=True)

        batch = []
        total_docs = 0
        total_time = 0

        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    uuid = row[0]  # First column as UUID
                    json_data = json.loads(row[1])  # Second column as JSON string

                    # Add the UUID as _id and prepare the document
                    document = {"_id": uuid, **json_data}
                    batch.append(json_util.loads(json.dumps(document)))  # BSON safe format

                    # Insert batch when it reaches the specified size
                    if len(batch) >= batch_size:
                        start_time = time.time()
                        collection.insert_many(batch)
                        elapsed_time = time.time() - start_time
                        total_time += elapsed_time
                        total_docs += len(batch)

                        avg_time_per_1000 = (total_time / total_docs) * 1000
                        print(f"Uploaded {total_docs} documents so far: "
                              f"Average {avg_time_per_1000:.2f} seconds per 1000 documents.")
                        batch.clear()
                except Exception as e:
                    print(f"Error processing row: {row} -> {e}")

        # Insert any remaining documents
        if batch:
            start_time = time.time()
            collection.insert_many(batch)
            elapsed_time = time.time() - start_time
            total_time += elapsed_time
            total_docs += len(batch)

            avg_time_per_1000 = (total_time / total_docs) * 1000
            print(f"Uploaded {total_docs} documents: Average {avg_time_per_1000:.2f} seconds per 1000 documents.")

        print("CSV file processing completed successfully.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    CONFIG_FILE = "../config.json"
    config = load_config(CONFIG_FILE)

    # Ensure MongoDB connection URI is provided
    if not mongo_uri:
        print("MongoDB connection URI (MONGO_URI) is not set in the environment.")
        exit(1)

    process_csv_and_upload(
        mongo_uri,
        config["database_name"],
        config["collection_name"],
        csv_file_path,
        batch_size
    )