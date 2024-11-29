from pymongo import MongoClient
import json
import os
from bson import json_util
import certifi
from pymongo import MongoClient

mongo_uri = os.getenv("MONGO_URI")
folder_path = "enriched_output"

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

def upload_documents_to_mongodb(connection_string, database_name, collection_name, folder_path):
    """
    Upload JSON documents to a MongoDB collection.

    Args:
        connection_string (str): MongoDB connection string.
        database_name (str): Name of the database.
        collection_name (str): Name of the collection.
        folder_path (str): Path to the folder containing JSON files.
    """
    try:
        client = MongoClient(connection_string, tlsCAFile=certifi.where())
        db = client[database_name]
        collection = db[collection_name]

        # Iterate through files in the folder
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, "r", encoding="utf-8") as file:
                    try:
                        document = json.load(file)

                        # Check if the document is a list
                        if isinstance(document, list):
                            for item in document:
                                # Ensure it's converted to BSON for MongoDB
                                bson_doc = json_util.loads(json.dumps(item))
                                collection.insert_one(bson_doc)
                        elif isinstance(document, dict):
                            bson_doc = json_util.loads(json.dumps(document))
                            collection.insert_one(bson_doc)
                        else:
                            print(f"Unsupported document format in {filename}: {type(document)}")
                            continue

                        print(f"Uploaded: {filename}")
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in {filename}: {e}")
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")

        print("All documents uploaded successfully.")
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