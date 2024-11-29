import os
import json
import shutil
import traceback


def transform_path(original_path):
    """
    Transform the original path by replacing dots with '>' and keeping the last field as an object.

    Args:
        original_path (str): The original path in openEHR notation.

    Returns:
        str: Transformed path with '>' replacing dots and object notation at the end.
    """
    segments = original_path.split("/")
    formatted_segments = []

    for segment in segments[:-1]:
        formatted_segments.append(segment.replace(".", ">"))

    # Keep the last field as it is
    formatted_segments.append(segments[-1])
    return ">".join(formatted_segments)


def map_values_recursive(items, parent_path=""):
    """
    Recursively maps values from nested items in the composition.

    Args:
        items (list): List of nested items in the composition.
        parent_path (str): Path representing the parent section for context.

    Returns:
        dict: Mapped paths and their corresponding values.
    """
    mapped_values = {}
    if not isinstance(items, list):
        return mapped_values

    for item in items:
        if not isinstance(item, dict):
            continue

        name = item.get("name", {}).get("value", "").strip()
        archetype_node_id = item.get("archetype_node_id", "")
        current_path = f"{parent_path}/{archetype_node_id}" if parent_path else archetype_node_id

        try:
            if "_type" in item and item["_type"] == "ELEMENT":
                # Map ELEMENT values
                value = item.get("value", {})
                transformed_path = transform_path(current_path)

                if isinstance(value, dict):
                    mapped_values[transformed_path] = {}
                    if "magnitude" in value:
                        mapped_values[transformed_path]["magnitude"] = value.get("magnitude")
                    if "unit" in value:
                        mapped_values[transformed_path]["unit"] = value.get("unit")
                    if "value" in value:
                        mapped_values[transformed_path]["value"] = value.get("value")
                    if "code_string" in value:
                        mapped_values[transformed_path]["code"] = value.get("code_string")

            elif "_type" in item and item["_type"] in ["CLUSTER", "ITEM_TREE", "SECTION"]:
                # Recursively map nested structures
                nested_items = item.get("items", [])
                nested_mapped = map_values_recursive(nested_items, parent_path=current_path)
                mapped_values.update(nested_mapped)

            elif "_type" in item and item["_type"] in ["OBSERVATION", "EVALUATION"]:
                # Map OBSERVATION or EVALUATION values
                data_items = item.get("data", {}).get("items", [])
                event_items = item.get("data", {}).get("events", [])

                # Map data section
                mapped_values.update(map_values_recursive(data_items, parent_path=current_path))

                # Map event section
                for event in event_items:
                    event_data = event.get("data", {}).get("items", [])
                    mapped_values.update(map_values_recursive(event_data, parent_path=current_path))

        except Exception as e:
            print(f"[ERROR] Error processing item with name: {name}")
            print(traceback.format_exc())
            continue

    return mapped_values


def transform_composition(data):
    """
    Transforms input composition(s) into the desired format.

    Args:
        data (dict or list): Single composition or a list of compositions.

    Returns:
        list: Transformed compositions with mapped paths and values, alongside full structure.
    """
    if isinstance(data, dict):
        data = [data]
    elif not isinstance(data, list):
        raise ValueError("Input JSON must be a list or a single object.")

    transformed_data = []

    for composition in data:
        if not isinstance(composition, dict):
            continue

        try:
            # Keep the original structure
            transformed_entry = {
                "CanonicalJSON": composition,
                "AQLSearchParams": {}
            }

            content = composition.get("content", [])
            transformed_entry["AQLSearchParams"] = map_values_recursive(content)

            transformed_data.append(transformed_entry)

        except Exception as e:
            print(f"[ERROR] Error processing composition with ID: {composition.get('_ehrID', 'unknown_id')}")
            print(traceback.format_exc())
            continue

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