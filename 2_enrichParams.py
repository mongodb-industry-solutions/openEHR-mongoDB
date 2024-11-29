import os
import json
import shutil

def extract_paths_and_values(data, current_path="", aql_params=None):
    """
    Recursively extracts all paths and values from the provided JSON object.
    Args:
        data (dict): JSON object to extract paths and values from.
        current_path (str): The current hierarchical path.
        aql_params (dict): A dictionary to store AQLSearchParams.
    Returns:
        dict: A dictionary of extracted paths and values.
    """
    if aql_params is None:
        aql_params = {}

    if isinstance(data, dict):
        for key, value in data.items():
            if key in ("_type", "name"):  # Skip metadata keys unless required
                continue
            
            # Construct the new path
            new_path = f"{current_path}>{key}" if current_path else key
            
            if isinstance(value, dict) or isinstance(value, list):
                extract_paths_and_values(value, new_path, aql_params)
            else:
                # Process openEHR objects with archetype_node_id
                if "archetype_node_id" in data:
                    node_id = data["archetype_node_id"]
                    aql_params.setdefault(current_path, {})
                    aql_params[current_path][node_id] = {
                        "value": value,
                        "units": data.get("units"),
                        "code": data.get("code"),
                        "magnitude": data.get("magnitude"),
                    }
                # Capture nested archetype_id
                if "archetype_id" in data:
                    archetype_id = data["archetype_id"].get("value")
                    aql_params.setdefault(current_path, {})
                    aql_params[current_path]["archetype_id"] = archetype_id
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            new_path = f"{current_path}>{idx}" if current_path else str(idx)
            extract_paths_and_values(item, new_path, aql_params)

    return aql_params


def create_mongo_document(composition):
    """
    Creates a MongoDB-compatible document with canonicalJSON and AQLSearchParams.
    Adds important metadata fields to the root level for easier filtering.
    Args:
        composition (dict): The original composition JSON object.
    Returns:
        dict: A MongoDB-compatible document.
    """
    aql_search_params = extract_paths_and_values(composition)

    # Extract composition-level metadata
    root_data = {
        "template_id": composition.get("archetype_details", {}).get("template_id", {}).get("value"),
        "archetype_id": composition.get("archetype_details", {}).get("archetype_id", {}).get("value"),
        "uid": composition.get("uid", {}).get("value"),
        "ehr_id": composition.get("_ehrID"),
        "composition_name": composition.get("name", {}).get("value"),
        "creation_time": composition.get("context", {}).get("start_time", {}).get("value"),
        "author": composition.get("composer", {}).get("name"),
    }

    return {
        **{key: value for key, value in root_data.items() if value is not None},  
        "canonicalJSON": composition, 
        "AQLSearchParams": aql_search_params
    }


def process_folder(folder_path, output_folder):
    """
    Processes all JSON files in the specified folder and generates MongoDB-compatible documents.
    Clears the output folder before saving new files.
    Args:
        folder_path (str): Path to the folder containing JSON files.
        output_folder (str): Path to the folder where processed files will be saved.
    """
    # Clear the output folder if it exists
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)  # Deletes the entire folder and its contents
    os.makedirs(output_folder)  # Recreate the folder

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                composition = json.load(file)
            
            # Create MongoDB-compatible document
            mongo_document = create_mongo_document(composition)
            
            # Save the processed document
            output_file_path = os.path.join(output_folder, filename)
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                json.dump(mongo_document, output_file, indent=4)

            print(f"Processed and saved: {filename}")


# Example usage
input_folder = "./output" 
output_folder = "./enriched_output" 
process_folder(input_folder, output_folder)