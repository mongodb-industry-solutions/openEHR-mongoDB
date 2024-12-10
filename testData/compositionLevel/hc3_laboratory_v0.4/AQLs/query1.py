import json
from pymongo import MongoClient
import os

# Load configuration from the config file
def load_config(config_path="../../config.json"):
    """
    Load configuration from a JSON file.

    Args:
        config_path (str): Path to the config file.

    Returns:
        dict: Configuration dictionary.
    """
    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        print(f"Config file {config_path} not found.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding config file: {e}")
        exit(1)

# Load config
config = load_config()

# MongoDB connection details
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    print("MongoDB connection URI (MONGO_URI) is not set in the environment.")
    exit(1)

client = MongoClient(mongo_uri)
db = client[config["database_name"]]
collection = db[config["collection_name"]]

# MongoDB Query Pipeline
pipeline = [
    # Match compositions of the correct type
    {
        "$match": {
            "AQLSearchParams.openEHR-EHR-COMPOSITION.report-result.v1": {
                "$exists": True
            }
        }
    }
]

# Execute the query
results = collection.aggregate(pipeline)

# Display results
for result in results:
    print(result)