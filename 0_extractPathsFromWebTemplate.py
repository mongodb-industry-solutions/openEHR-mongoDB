import json

def extract_aql_paths(data, paths=None):
    """
    Recursively extract all 'aqlPath' values from the given JSON data.
    :param data: The JSON data as a dictionary.
    :param paths: The list to store extracted paths (default is None, initializes to an empty list).
    :return: List of all 'aqlPath' values.
    """
    if paths is None:
        paths = []
    
    # If the current node has an aqlPath, add it to the paths list
    if "aqlPath" in data:
        paths.append(data["aqlPath"])
    
    # If the current node has children, recursively extract paths from them
    if "children" in data:
        for child in data["children"]:
            extract_aql_paths(child, paths)
    
    return paths

# Prompt the user to provide the path to the web template file
file_path = "/Users/francesc.mateu/Documents/GitHub/openEHR-MongoDB/testData/Original/WebTemplates/HC3 Immunization List v0.5.json"

try:
    # Load the web template JSON file
    with open(file_path, 'r', encoding='utf-8') as file:
        web_template = json.load(file)

    # Extract aqlPaths from the tree structure
    aql_paths = extract_aql_paths(web_template["tree"])

    # Output all extracted paths
    print("Extracted aqlPaths:")
    for path in aql_paths:
        print(path)

except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
except json.JSONDecodeError:
    print(f"Error: Failed to parse the file at {file_path}. Ensure it's a valid JSON file.")