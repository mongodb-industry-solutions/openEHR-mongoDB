import re

def aql_path_to_mql(aql_path):
    """
    Convert an AQL path to a MongoDB query format.

    Args:
        aql_path (str): The AQL path to convert.
    
    Returns:
        dict: The equivalent MongoDB query.
    """
    print(f"Input AQL Path: {aql_path}")
    
    # Remove the initial `c/` if present
    if aql_path.startswith('c/'):
        aql_path = aql_path[2:]  # Remove the first 2 characters

    # Normalize predicates without explicit keys
    normalized_path = re.sub(r'\[([a-zA-Z0-9_.-]+)\]', r'[archetype_node_id : "\1"]', aql_path)
    
    # Define a regular expression to extract path components
    predicate_pattern = re.compile(r'(?P<path>[a-zA-Z0-9_.-]+)\[archetype_node_id : "(?P<value>[a-zA-Z0-9_.-]+)"\]')
    path_parts = normalized_path.split('/')
    mql_conditions = {}

    # Iterate through each part of the path
    current_path = []
    for part in path_parts:
        match = predicate_pattern.search(part)
        if match:
            # Extract and map the archetype_node_id
            path = match.group("path")
            value = match.group("value")
            current_path.append(path)
            mongo_path = '.'.join(current_path) + ".archetype_node_id"
            mql_conditions[mongo_path] = value
        elif any(op in part for op in ['>=', '<=', '=', '>', '<']):
            # Handle comparison operators
            for operator, mongo_op in [(">=", "$gte"), ("<=", "$lte"), ("=", ""), (">", "$gt"), ("<", "$lt")]:
                if operator in part:
                    field_path, field_value = part.split(operator, 1)
                    clean_path = '.'.join(current_path + field_path.strip().split('/'))
                    clean_value = field_value.strip().strip("'\"")
                    if mongo_op:
                        mql_conditions[clean_path] = {mongo_op: clean_value}
                    else:
                        mql_conditions[clean_path] = clean_value
                    break
        else:
            # Regular path segment
            current_path.append(part)
    
    print("Translated path to conditions", mql_conditions)
    return mql_conditions

# Example usage
aql_example = (
    "c/context/other_context[at0004]/items[openEHR-EHR-CLUSTER.admin_salut.v0]/items[at0007]/items[at0014]/value/defining_code/code_string = 'E08553936'"
)

# Convert the AQL path
mql_result = aql_path_to_mql(aql_example)
print("MongoDB Query:")
print(mql_result)