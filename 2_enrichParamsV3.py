import os
import json
import shutil
import traceback

def flatten_json(data, base_path=""):
    """
    Recursively flattens a nested JSON object into a dictionary with AQL-style paths as keys.

    Args:
        data (dict or list): The JSON data to flatten.
        base_path (str): The base path accumulated so far.

    Returns:
        dict: A flat dictionary with full paths as keys and values as their corresponding values.
    """
    flat_dict = {}

    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{base_path}/{key}" if base_path else f"/{key}"
            if isinstance(value, (dict, list)):
                # Recurse into nested dictionaries or lists
                flat_dict.update(flatten_json(value, new_path))
            else:
                # Add leaf value to flat_dict
                flat_dict[new_path] = value

    elif isinstance(data, list):
        for index, item in enumerate(data):
            indexed_path = f"{base_path}[{index}]"
            if isinstance(item, (dict, list)):
                # Recurse into nested dictionaries or lists
                flat_dict.update(flatten_json(item, indexed_path))
            else:
                # Add list item value to flat_dict
                flat_dict[indexed_path] = item

    return flat_dict

def filter_aql_relevant_keys(flat_data):
    """
    Filters AQL-relevant keys from the flattened JSON.
    
    Args:
        flat_data (dict): Flattened JSON data with full paths as keys.

    Returns:
        dict: Filtered AQL-relevant key-value pairs.
    """
    aql_relevant_keys = {}
    for key, value in flat_data.items():
        if (
            "archetype_node_id" in key or
            "value" in key or
            "code_string" in key or
            "defining_code" in key or
            "terminology_id" in key or
            "identifiers" in key
        ):
            aql_relevant_keys[key] = value
    return aql_relevant_keys

def extract_archetypes(flat_data):
    """
    Extracts archetype IDs and their corresponding paths from the flattened data.

    Args:
        flat_data (dict): Flattened JSON data with full paths as keys.

    Returns:
        list: A list of dictionaries with archetype IDs and their corresponding paths.
    """
    archetypes = []
    for path, value in flat_data.items():
        if "archetype_node_id" in path or "archetype_id" in path:
            archetypes.append({"archetypeID": value, "path": path})
            
def transform_composition(data):
    """
    Transforms a composition into a flat structure with AQL-compatible paths and values.

    Args:
        data (dict): The original composition data.

    Returns:
        dict: The transformed composition structure.
    """
    # Flatten the JSON data
    flat_data = flatten_json(data)
    
    # Filter only AQL-relevant keys
    aql_filtered_data = filter_aql_relevant_keys(flat_data)

    # Extract archetypes
    archetypes = extract_archetypes(flat_data)

    # Extract compositionUid and templateId from the canonical structure
    composition_uid = data.get("uid", {}).get("value", "unknown_uid")
    template_id = data.get("archetype_details", {}).get("template_id", {}).get("value", "unknown_template")

    # Generate the transformed structure
    transformed_data = {
        "AQLSearchParams": {
            "compositionUid": composition_uid,
            "compTemplate": template_id,
            "paths": aql_filtered_data,
        },
        "archetypes": archetypes,
        "CanonicalJSON": data,
    }

    return transformed_data

def process_files(input_folder, output_folder):
    """
    Processes JSON files in the input folder, transforms them, and saves to the output folder.

    Args:
        input_folder (str): Path to the folder containing input JSON files.
        output_folder (str): Path to the folder for saving transformed JSON files.
    """
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename)

            try:
                with open(input_file_path, "r") as infile:
                    data = json.load(infile)

                transformed_data = transform_composition(data)

                with open(output_file_path, "w") as outfile:
                    json.dump(transformed_data, outfile, indent=4)

                print(f"[INFO] Processed {filename} -> {output_file_path}")

            except Exception as e:
                print(f"[ERROR] Error processing file: {filename}")
                print(traceback.format_exc())
                continue

    print("[INFO] Processing complete.")

# Paths
input_folder = "output"
output_folder = "enriched_output"

# Run the processing function
process_files(input_folder, output_folder)