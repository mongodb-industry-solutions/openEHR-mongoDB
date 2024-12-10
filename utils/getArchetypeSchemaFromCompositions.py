import os
import json


def extract_composition_structure(data, depth=0):
    """
    Recursively extracts the structure of an openEHR composition.
    """
    structure = []
    prefix = "    " * depth

    if not isinstance(data, dict):
        print(f"Unexpected structure at depth {depth}: {type(data)} - {data}")
        return structure

    # Extract archetype details for the current item
    if "_type" in data and "archetype_details" in data:
        archetype_id = data["archetype_details"].get("archetype_id", {}).get("value", "Unknown")
        name = data.get("name", {}).get("value", "Unknown")
        structure.append(f"{prefix}{archetype_id} // {name}")

    # Traverse content or items recursively
    if "content" in data:
        for item in data["content"]:
            structure.extend(extract_composition_structure(item, depth + 1))
    elif "items" in data:
        for item in data["items"]:
            structure.extend(extract_composition_structure(item, depth + 1))

    return structure


def process_compositions(folder_path):
    """
    Reads all JSON files in the folder and generates a schema for each.
    """
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    print(f"Schema for {file_name}:")
                    
                    # Handle lists of compositions
                    if isinstance(data, list):
                        for i, composition in enumerate(data):
                            print(f"Processing composition {i + 1} in {file_name}")
                            schema = extract_composition_structure(composition)
                            print("\n".join(schema))
                    else:
                        schema = extract_composition_structure(data)
                        print("\n".join(schema))

                    print("\n" + "=" * 50 + "\n")
                except Exception as e:
                    print(f"Failed to process {file_name}: {e}")


# Path to the folder containing composition JSON files
folder_path = "compositionExamples"

if __name__ == "__main__":
    process_compositions(folder_path)