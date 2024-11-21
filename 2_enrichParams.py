import os
import json
import shutil
import traceback


def extract_params_recursive(items, parent_key=""):
    """
    Recursively extracts parameters from nested items in the composition.

    Args:
        items (list): List of `CLUSTER`, `ELEMENT`, or other items.
        parent_key (str): Parent key to maintain hierarchy in keys.

    Returns:
        dict: Extracted AQLSearchParams.
    """
    params = {}
    if not isinstance(items, list):
        print(f"[DEBUG] Expected list in extract_params_recursive, got {type(items).__name__}: {items}")
        return params

    for item in items:
        if not isinstance(item, dict):
            print(f"[DEBUG] Skipping non-dictionary item: {item}")
            continue

        item_type = item.get("_type", "UNKNOWN_TYPE")
        name = item.get("name", {}).get("value", "").strip()
        archetype_node_id = item.get("archetype_node_id", "")

        try:
            if item_type == "ELEMENT":
                # Process ELEMENT
                value = item.get("value", {})
                key = f"{parent_key}.{name.lower().replace(' ', '_').replace('/', '_')}" if parent_key else name.lower().replace(' ', '_').replace('/', '_')
                if isinstance(value, dict):
                    if value.get("_type") == "DV_CODED_TEXT":
                        params[key] = value.get("value")
                        params[f"{key}_code"] = value.get("defining_code", {}).get("code_string")
                    elif value.get("_type") == "DV_QUANTITY":
                        params[key] = value.get("magnitude")
                        params[f"{key}_unit"] = value.get("units")
                        if "normal_range" in value:
                            normal_range = value["normal_range"]
                            params[f"{key}_normal_range_lower"] = normal_range.get("lower", {}).get("magnitude")
                            params[f"{key}_normal_range_upper"] = normal_range.get("upper", {}).get("magnitude")
                    elif value.get("_type") == "DV_DATE_TIME":
                        params[key] = value.get("value")
                    elif value.get("_type") == "DV_URI":
                        params[key] = value.get("value")
                    elif value.get("_type") == "CODE_PHRASE":
                        params[key] = value.get("code_string")
                        params[f"{key}_terminology_id"] = value.get("terminology_id", {}).get("value")
                elif isinstance(value, str):
                    params[key] = value

            elif item_type in ["CLUSTER", "ITEM_TREE", "SECTION"]:
                # Process nested structures
                cluster_name = name.lower().replace(' ', '_').replace('/', '_')
                nested_key = f"{parent_key}.{cluster_name}" if parent_key else cluster_name
                nested_items = item.get("items", [])
                nested_params = extract_params_recursive(nested_items, nested_key)
                params.update(nested_params)

            elif item_type in ["OBSERVATION", "EVALUATION"]:
                # Process OBSERVATION or EVALUATION
                observation_key = f"{parent_key}.{name.lower().replace(' ', '_')}" if parent_key else name.lower().replace(' ', '_')
                data_items = item.get("data", {}).get("items", [])
                event_items = item.get("data", {}).get("events", [])
                nested_params = extract_params_recursive(data_items, observation_key)
                for event in event_items:
                    event_params = extract_params_recursive(event.get("data", {}).get("items", []), observation_key)
                    params.update(event_params)
                params.update(nested_params)

        except Exception as e:
            print(f"[ERROR] Error processing item with _type: {item_type} and name: {name}")
            print(traceback.format_exc())
            continue

    return params


def transform_composition(data):
    """
    Transforms input composition(s) to enriched format with `AQLSearchParams`.

    Args:
        data (dict or list): Single composition or a list of compositions.

    Returns:
        list: Transformed compositions with enriched data.
    """
    if isinstance(data, dict):
        data = [data]
    elif not isinstance(data, list):
        raise ValueError("Input JSON must be a list or a single object.")

    transformed_data = []

    for composition in data:
        if not isinstance(composition, dict):
            print(f"[DEBUG] Skipping non-dictionary composition: {composition}")
            continue

        transformed_entry = {
            "_id": composition.get("_ehrID", "unknown_id"),
            "CanonicalJSON": composition,
            "AQLSearchParams": {}
        }

        try:
            # Add UID versioning
            uid = composition.get("uid", {}).get("value")
            if uid:
                transformed_entry["AQLSearchParams"]["composition.uid.value"] = uid

            # Add context metadata
            context = composition.get("context", {})
            if isinstance(context, dict):
                start_time = context.get("start_time", {}).get("value")
                if start_time:
                    transformed_entry["AQLSearchParams"]["composition.context.start_time"] = start_time
                setting = context.get("setting", {}).get("value")
                if setting:
                    transformed_entry["AQLSearchParams"]["composition.context.setting"] = setting

            # Add language and territory
            language = composition.get("language", {}).get("code_string")
            if language:
                transformed_entry["AQLSearchParams"]["composition.language.code"] = language
            territory = composition.get("territory", {}).get("code_string")
            if territory:
                transformed_entry["AQLSearchParams"]["composition.territory.code"] = territory

            # Add category
            category = composition.get("category", {}).get("value")
            if category:
                transformed_entry["AQLSearchParams"]["composition.category"] = category
            category_code = composition.get("category", {}).get("defining_code", {}).get("code_string")
            if category_code:
                transformed_entry["AQLSearchParams"]["composition.category_code"] = category_code

            # Add composition-level metadata to AQLSearchParams
            archetype_details = composition.get("archetype_details", {})
            if isinstance(archetype_details, dict):
                for key in ["archetype_id", "template_id", "rm_version"]:
                    if isinstance(archetype_details.get(key), dict):
                        value = archetype_details[key].get("value")
                        if value:
                            transformed_entry["AQLSearchParams"][f"composition.{key}"] = value
                    else:
                        transformed_entry["AQLSearchParams"][f"composition.{key}"] = archetype_details.get(key)

            # Add feeder_audit data
            feeder_audit = composition.get("feeder_audit", {})
            if isinstance(feeder_audit, dict):
                for field, value in feeder_audit.items():
                    if isinstance(value, list):
                        ids = [v.get("id") for v in value if isinstance(v, dict)]
                        transformed_entry["AQLSearchParams"][f"composition.feeder_audit.{field}"] = ids

            # Process `content` for observations and clusters
            content = composition.get("content", [])
            if isinstance(content, list):
                for section in content:
                    if isinstance(section, dict) and section.get("_type") == "SECTION":
                        section_key = section.get("name", {}).get("value", "").lower().replace(' ', '_')
                        for item in section.get("items", []):
                            if isinstance(item, dict):
                                item_params = extract_params_recursive([item], section_key)
                                transformed_entry["AQLSearchParams"].update(item_params)

            transformed_data.append(transformed_entry)

        except Exception as e:
            print(f"[ERROR] Error processing composition with ID: {composition.get('_ehrID', 'unknown_id')}")
            print(traceback.format_exc())
            continue

    return transformed_data


def process_files(input_folder, output_folder):
    """
    Processes JSON files in the input folder, enriches them, and saves to the output folder.

    Args:
        input_folder (str): Path to the folder containing input JSON files.
        output_folder (str): Path to the folder for saving enriched JSON files.
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