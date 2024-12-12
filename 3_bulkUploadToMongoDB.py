from pymongo import MongoClient
import json
import os
from bson import json_util
import certifi
import time
import shutil

mongo_uri = os.getenv("MONGO_URI")
folder_path = "output"
processed_folder_path = os.path.join(folder_path, "processed")

def load_config(config_file):
    """
    Load configuration from a JSON file.

    Args:
        config_file (str): Path to the config file.

    Returns:
        dict: Configuration dictionary.
    """
    try:
        with open(config_file, "r", encoding="utf-8") as file:
            config = json.load(file)
            return config
    except FileNotFoundError:
        print(f"Config file {config_file} not found.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding config file: {e}")
        exit(1)

def upload_documents_to_mongodb(connection_string, database_name, collection_name, folder_path, batch_size=100):
    """
    Upload JSON documents to a MongoDB collection in bulk.

    Args:
        connection_string (str): MongoDB connection string.
        database_name (str): Name of the database.
        collection_name (str): Name of the collection.
        folder_path (str): Path to the folder containing JSON files.
        batch_size (int): Number of documents to upload in each batch.
    """
    try:
        client = MongoClient(connection_string, tlsCAFile=certifi.where())
        db = client[database_name]
        collection = db[collection_name]

        # Ensure processed folder exists
        os.makedirs(processed_folder_path, exist_ok=True)

        batch = []
        total_docs = 0
        total_time = 0

        # Iterate through files in the folder
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, "r", encoding="utf-8") as file:
                    try:
                        document = json.load(file)

                        # Add documents to the batch
                        if isinstance(document, list):
                            for item in document:
                                bson_doc = json_util.loads(json.dumps(item))
                                batch.append(bson_doc)
                                total_docs += 1

                                # Upload batch if it reaches the batch size
                                if len(batch) == batch_size:
                                    start_time = time.time()
                                    collection.insert_many(batch)
                                    elapsed_time = time.time() - start_time
                                    total_time += elapsed_time

                                    avg_time_per_1000 = (total_time / total_docs) * 1000
                                    print(f"Processed and uploaded {total_docs} documents in {total_time:.2f} seconds: "
                                          f"Average of {avg_time_per_1000:.2f} seconds per 1000 documents.")
                                    batch.clear()
                        elif isinstance(document, dict):
                            bson_doc = json_util.loads(json.dumps(document))
                            batch.append(bson_doc)
                            total_docs += 1

                            # Upload batch if it reaches the batch size
                            if len(batch) == batch_size:
                                start_time = time.time()
                                collection.insert_many(batch)
                                elapsed_time = time.time() - start_time
                                total_time += elapsed_time

                                avg_time_per_1000 = (total_time / total_docs) * 1000
                                print(f"Processed and uploaded {total_docs} documents in {total_time:.2f} seconds: "
                                      f"Average of {avg_time_per_1000:.2f} seconds per 1000 documents.")
                                batch.clear()
                        else:
                            print(f"Unsupported document format in {filename}: {type(document)}")
                            continue

                        # Move the processed file to the processed folder
                        shutil.move(file_path, os.path.join(processed_folder_path, filename))
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in {filename}: {e}")
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")

        # Upload remaining documents in the batch
        if batch:
            start_time = time.time()
            collection.insert_many(batch)
            elapsed_time = time.time() - start_time
            total_time += elapsed_time

            avg_time_per_1000 = (total_time / total_docs) * 1000
            print(f"Processed and uploaded {total_docs} documents in {total_time:.2f} seconds: "
                  f"Average of {avg_time_per_1000:.2f} seconds per 1000 documents.")

        if total_docs == 0:
            print("No documents uploaded.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    CONFIG_FILE = "config.json"
    config = load_config(CONFIG_FILE)

    # Ensure MongoDB connection URI is provided
    if not mongo_uri:
        print("MongoDB connection URI (MONGO_URI) is not set in the environment.")
        exit(1)

    upload_documents_to_mongodb(
        mongo_uri,
        config["database_name"],
        config["collection_name"],
        folder_path
    )