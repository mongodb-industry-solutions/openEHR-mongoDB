import os
import json
import shutil
import xxhash


def clear_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

def shorten_path(path, prefix_to_remove):
    """
    Shorten a path by removing a specified prefix.
    
    :param path: The full path to be shortened.
    :param prefix_to_remove: The prefix to be removed from the path.
    :return: The shortened path.
    """
    if path.startswith(prefix_to_remove):
        return path[len(prefix_to_remove):]
    return path


def extract_paths(data, parent_path="", paths={}, target_archetype=None):
    """
    Recursively extract paths and values from a specific archetype within a composition.

    :param data: The JSON data (composition).
    :param parent_path: The current path prefix.
    :param paths: The dictionary to store extracted paths and values.
    :param target_archetype: The target archetype to filter paths from.
    :return: A dictionary with paths and values.
    """
    if paths is None:
        paths = {}

    if isinstance(data, dict):
        # Check if the current node matches the target archetype
        archetype_node_id = data.get("archetype_node_id")
        if target_archetype and archetype_node_id == target_archetype:
            # Start extracting paths from this point
            parent_path = f"[{archetype_node_id}]"
        elif target_archetype and parent_path == "":
            # If we haven't reached the target archetype, skip this branch
            for key, value in data.items():
                extract_paths(value, parent_path, paths, target_archetype)
            return paths

        # Use "archetype_node_id" or "name.value" for meaningful path names
        identifier = data.get("archetype_node_id") or (data.get("name", {}).get("value") if isinstance(data.get("name"), dict) else None)
        new_parent_path = f"{parent_path}[{identifier}]" if identifier else parent_path

        for key, value in data.items():
            if key not in ["_type", "archetype_node_id", "name"]:
                new_path = f"{new_parent_path}/{key}" if new_parent_path else key
                extract_paths(value, new_path, paths, target_archetype)

    elif isinstance(data, list):
        for item in data:
            extract_paths(item, parent_path, paths, target_archetype)

    else:
        # Store the value for a leaf node
        paths[parent_path] = data

    return paths


def hash_path(path):
    hash_value = xxhash.xxh64(path).hexdigest()
    checksum = xxhash.xxh32(path).hexdigest()[:2]
    return f"{hash_value}{checksum}"


def collect_archetypes(data, archetypes):
    if archetypes is None:
        archetypes = set()

    if isinstance(data, dict):
        archetype_id = data.get("archetype_node_id")
        if archetype_id and archetype_id.startswith("openEHR-") and archetype_id not in archetypes:
            archetypes.add(archetype_id)
        for value in data.values():
            collect_archetypes(value, archetypes)
    elif isinstance(data, list):
        for item in data:
            collect_archetypes(item, archetypes)


def parse_composition(composition, use_hashed_paths=False, target_archetype=None):
    """
    Parse a composition and extract key-value pairs for AQL search parameters.

    :param composition: The composition JSON data.
    :param use_hashed_paths: Whether to use hashed paths for storage.
    :param target_archetype: The specific archetype to extract paths from.
    :return: A dictionary of AQL search parameters.
    """
    aql_search_params = {
        "compositionUid": composition.get("uid", {}).get("value"),
        "compositionTemplate": composition.get("archetype_details", {}).get("template_id", {}).get("value"),
        "archetypes": [],
        "paths": {}
    }

    # Collect all unique relevant archetypes
    archetypes = set()
    collect_archetypes(composition, archetypes)
    aql_search_params["archetypes"] = list(archetypes)

    # Extract paths specifically from the target archetype
    extracted_paths = extract_paths(composition, target_archetype=target_archetype)
    prefix_to_remove = f"[{target_archetype}][{target_archetype}]/" if target_archetype else ""

    for path, value in extracted_paths.items():
        shortened_path = shorten_path(path, prefix_to_remove)
        final_path = hash_path(shortened_path) if use_hashed_paths else shortened_path
        aql_search_params["paths"][final_path] = value

    return aql_search_params


def process_compositions(input_folder, output_folder, use_hashed_paths=False, target_archetype=None):
    """
    Process all composition JSON files in the input folder and save enriched results.

    :param input_folder: Path to the folder containing input composition files.
    :param output_folder: Path to the folder to save enriched composition files.
    :param use_hashed_paths: Whether to use hashed paths for storage.
    :param target_archetype: The specific archetype to extract paths from.
    """
    clear_folder(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            with open(input_path, "r", encoding="utf-8") as file:
                composition_data = json.load(file)

            ehr_id = composition_data.get("_ehrID")
            enriched_data = {
                "AQLSearchParams": parse_composition(composition_data, use_hashed_paths, target_archetype),
                "relatedEntities": {
                    "ehr_id": ehr_id
                },
                "CanonicalJSON": composition_data
            }

            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(enriched_data, file, indent=4)

    print(f"Processed all files. Enriched compositions are in '{output_folder}'.")


# Define input and output folders
input_folder = "output_2"
output_folder = "output_enriched_complete_2"
use_hashed_paths = True  # Set to True to use hashed paths
target_archetype = "openEHR-EHR-COMPOSITION.vaccination_list.v0"

# Process compositions
process_compositions(input_folder, output_folder, use_hashed_paths, target_archetype)