import os
import json
import random
from faker import Faker
from bson import ObjectId
from collections import OrderedDict

# Initialize Faker
faker = Faker()

# Load config
with open("config.json", "r") as config_file:
    config = json.load(config_file)

ehr_id_suffix = config["ehrID_suffix"]
ehr_id_range = config["ehrID_range"]

# Load schemas
def load_schemas(schema_config):
    schemas = {}
    for name, path in schema_config.items():
        with open(path, "r", encoding="utf-8") as schema_file:
            schemas[name] = json.load(schema_file)
    return schemas

schemas = load_schemas(config["schemas"])

# Assign ehrID dynamically
def assign_ehr_id():
    random_number = random.randint(1, ehr_id_range)
    return f"{ehr_id_suffix}{random_number}"

# Generator functions
def generate_minimal_evaluation(schema):
    schema["_id"] = str(ObjectId())
    schema["_ehrID"] = assign_ehr_id()
    schema["context"]["start_time"]["value"] = faker.date_time_this_year().isoformat()
    schema["composer"]["name"] = faker.name()
    schema["content"][0]["data"]["items"][0]["value"]["magnitude"] = round(random.uniform(50, 100), 1)
    return schema

def generate_corona_composition(schema):
    schema["_id"] = str(ObjectId())
    schema["_ehrID"] = assign_ehr_id()
    schema["context"]["start_time"]["value"] = faker.date_time_this_year().isoformat()
    schema["composer"]["name"] = faker.email()
    schema["content"][0]["data"]["events"][0]["data"]["items"][0]["value"]["value"] = faker.text(max_nb_chars=50)
    schema["content"][1]["items"][0]["data"]["events"][0]["data"]["items"][0]["items"][0]["value"]["value"] = "Northern Italy"
    return schema

def generate_immunization_composition(schema):
    """
    This function generates synthetic immunization composition data based on a predefined schema.
    """
    schema["_id"] = str(ObjectId())  # Assign a unique MongoDB ObjectId
    schema["_ehrID"] = assign_ehr_id()  # Assign a random EHR ID

    # Randomize context start time
    schema["context"]["start_time"]["value"] = faker.date_time_this_year().isoformat()

    # Randomize defining_code for "other_context"
    schema["context"]["other_context"]["items"][1]["items"][3]["items"][0]["value"]["defining_code"]["code_string"] = faker.random_element(
        ["H43001830", "L33001834", "K43221830"]
    )

    # Randomize composer identifier
    schema["composer"]["identifiers"][0]["id"] = faker.uuid4()

    # Randomize time in the description
    schema["content"][0]["items"][0]["time"]["value"] = faker.date_time_this_year().isoformat()

    # Randomize performer identifiers
    schema["content"][0]["items"][0]["other_participations"][0]["performer"]["identifiers"][2]["id"] = faker.random_element(
        ["43086845K", "33001834T", "43221834T", "43676845K", "39999834T", "55521834T"]
    )

    # Randomize immunization item (vaccine type)
    schema["content"][0]["items"][0]["description"]["items"][0]["value"]["value"] = faker.random_element(
        ["COVID-19 Vaccine", "Hepatitis B Vaccine", "Flu Vaccine"]
    )

    # Randomize manufacturer name
    schema["content"][0]["items"][0]["description"]["items"][1]["items"][0]["value"]["value"] = faker.random_element(
        ["Pfizer", "Moderna", "AstraZeneca"]
    )

    return schema

def generate_laboratory_composition(schema):
    schema["_id"] = str(ObjectId())
    schema["_ehrID"] = assign_ehr_id()
    schema["context"]["start_time"]["value"] = faker.date_time_this_year().isoformat()
    schema["composer"]["identifiers"][0]["id"] = faker.uuid4()
    schema["content"][0]["items"][0]["data"]["events"][0]["data"]["items"][0]["value"]["value"] = faker.random_element(
        ["Blood Test", "Urine Test", "COVID PCR"]
    )
    schema["content"][0]["items"][0]["data"]["events"][0]["data"]["items"][1]["items"][0]["value"]["value"] = faker.random_element(
        ["Normal", "Abnormal"]
    )
    return schema

def generate_laboratory_composition_short(schema):
    """
    Generates a synthetic laboratory composition while maintaining the schema's size and structure.
    Only modifies existing fields without adding new elements.
    """
    from copy import deepcopy

    # Deep copy the schema to preserve the original
    schema = deepcopy(schema)

    # Assign basic randomized fields
    schema["_id"] = str(ObjectId())
    schema["_ehrID"] = f"ehr_{random.randint(1, 100)}"

    # Update specific nested fields without duplicating structure
    def update_nested_structure(node):
        if isinstance(node, dict):
            # Update fields based on their keys
            if "value" in node and isinstance(node["value"], str):
                if node["value"] == "Test result":
                    node["value"] = f"Result {random.randint(1, 100)}"
                elif node["value"] in ["Blood Test", "Urine Test", "COVID PCR"]:
                    node["value"] = random.choice(["Blood Test", "Urine Test", "COVID PCR"])
            elif "magnitude" in node and isinstance(node["magnitude"], (int, float)):
                # Update numeric test results
                node["magnitude"] = round(random.uniform(50, 150), 2)
        elif isinstance(node, list):
            # Recursively update list elements
            for item in node:
                update_nested_structure(item)

    # Apply updates only where necessary
    update_nested_structure(schema.get("content", []))

    return schema
    

def generate_virology_finding_with_specimen(schema):
    schema["_id"] = str(ObjectId())
    schema["_ehrID"] = assign_ehr_id()
    schema["context"]["start_time"]["value"] = faker.date_time_this_year().isoformat()
    schema["composer"]["name"] = faker.name()
    schema["content"][0]["data"]["events"][0]["data"]["items"][0]["value"]["value"] = faker.random_element(
        ["Positive", "Negative", "Indeterminate"]
    )
    return schema

def generate_obs_inst(schema):
    schema["_id"] = str(ObjectId())
    schema["_ehrID"] = assign_ehr_id()
    schema["context"]["start_time"]["value"] = faker.date_time_this_year().isoformat()
    schema["composer"]["name"] = faker.name()
    schema["content"][0]["data"]["events"][0]["data"]["items"][0]["value"]["value"] = faker.text(max_nb_chars=100)
    return schema

def generate_minimal_observation(schema):
    schema["_id"] = str(ObjectId())
    schema["_ehrID"] = assign_ehr_id()
    schema["context"]["start_time"]["value"] = faker.date_time_this_year().isoformat()
    schema["composer"]["name"] = faker.name()
    schema["content"][0]["data"]["events"][0]["data"]["items"][0]["value"]["value"] = faker.text(max_nb_chars=50)
    return schema

# Generator mapping
generators = {
    "minimal_evaluation": generate_minimal_evaluation,
    "Corona_composition": generate_corona_composition,
    "Immunization_composition": generate_immunization_composition,
    "Laboratory_composition": generate_laboratory_composition,
    "Laboratory_composition_short": generate_laboratory_composition_short,
    "virology_finding_with_specimen": generate_virology_finding_with_specimen,
    "obs_inst": generate_obs_inst,
    "minimal_observation": generate_minimal_observation
}

def generate_data(num_docs, schemas, generators):
    documents = []
    schema_names = list(schemas.keys())
    count_per_schema = num_docs // len(schema_names)

    for schema_name in schema_names:
        generator = generators.get(schema_name)
        if generator:
            for _ in range(count_per_schema):
                documents.append(generator(schemas[schema_name].copy()))

    # Handle any remaining documents
    remaining = num_docs - len(documents)
    for _ in range(remaining):
        random_schema = random.choice(schema_names)
        generator = generators[random_schema]
        documents.append(generator(schemas[random_schema].copy()))

    return documents


def save_to_files(documents, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for i, doc in enumerate(documents):
        # Reorder keys: Move _id and _ehrID to the beginning
        ordered_doc = OrderedDict([
            ("_id", doc["_id"]),
            ("_ehrID", doc["_ehrID"]),
        ] + [(k, v) for k, v in doc.items() if k not in ["_id", "_ehrID"]])

        filename = os.path.join(output_dir, f"{doc['_ehrID']}_composition_{i + 1}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(ordered_doc, f, ensure_ascii=False, indent=4)
    print(f"Saved {len(documents)} files to '{output_dir}'.")

if __name__ == "__main__":
    num_documents = config["num_documents"]  
    output_folder = "output"

    generated_data = generate_data(num_documents, schemas, generators)
    save_to_files(generated_data, output_folder)