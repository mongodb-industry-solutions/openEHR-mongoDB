def generate_path_value_map(data, current_path=""):
    """
    Recursively generates a map of paths to their values from a nested dictionary or list.

    Args:
        data (dict | list): Input JSON object.
        current_path (str): Current path (used for recursion).

    Returns:
        dict: A map of paths to their corresponding values.
    """
    path_value_map = {}

    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{current_path}/{key}" if current_path else f"/{key}"
            if isinstance(value, (dict, list)):
                path_value_map.update(generate_path_value_map(value, new_path))
            else:
                path_value_map[new_path] = value

    elif isinstance(data, list):
        for index, item in enumerate(data):
            new_path = f"{current_path}/{index}"
            if isinstance(item, (dict, list)):
                path_value_map.update(generate_path_value_map(item, new_path))
            else:
                path_value_map[new_path] = item

    return path_value_map

# Simulate the large JSON structure here (truncated for this environment).
composition_data = {
    "_id": "ehr_2",
    "CanonicalJSON": {
        "_ehrID": "ehr_2",
        "_type": "COMPOSITION",
        "name": {"_type": "DV_TEXT", "value": "HC3 Laboratory Short"},
        "archetype_details": {
            "archetype_id": {"value": "openEHR-EHR-COMPOSITION.report-result.v1"},
            "template_id": {"value": "hc3_laboratory_v0.4"},
            "rm_version": "1.0.4"
        },
        "context": {
            "start_time": {"_type": "DV_DATE_TIME", "value": "2024-11-20T17:53:42.756+01:00"},
            "setting": {
                "_type": "DV_CODED_TEXT",
                "value": "other care",
                "defining_code": {
                    "terminology_id": {"_type": "TERMINOLOGY_ID", "value": "openehr"},
                    "code_string": "238"
                }
            },
        },
        "content": [
            {
                "_type": "SECTION",
                "name": {"_type": "DV_TEXT", "value": "Laboratory test results list"},
                "items": [
                    {
                        "_type": "OBSERVATION",
                        "name": {"_type": "DV_TEXT", "value": "Laboratory test results"},
                        "data": {
                            "events": [
                                {
                                    "_type": "POINT_EVENT",
                                    "data": {
                                        "items": [
                                            {
                                                "_type": "ELEMENT",
                                                "name": {"_type": "DV_TEXT", "value": "Test name"},
                                                "value": {"_type": "DV_CODED_TEXT", "value": "LABE"}
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
}

# Generate the full path-value mapping
path_value_map = generate_path_value_map(composition_data)

import json
path_value_map_json = json.dumps(path_value_map, indent=4)
path_value_map_json