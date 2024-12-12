import re
from aql_path_to_mql_converter import aql_path_to_mql

def transform_where_clause(aql_query):
    """
    Extract the WHERE clause from an AQL query and convert it into a MongoDB $match block.

    Args:
        aql_query (str): The AQL query string.
    
    Returns:
        dict: MongoDB $match block.
    """
    # Extract the WHERE clause
    where_match = re.search(r"WHERE\s+\((.*?)\)\s+ORDER", aql_query, re.DOTALL)
    if not where_match:
        return {}
    
    where_clause = where_match.group(1)
    conditions = where_clause.split("AND")
    match_conditions = []

    for condition in conditions:
        condition = condition.strip()
        print("Processing condition:", condition)
        transformed_condition = aql_path_to_mql(condition)
        print("Tranlated path to conditions", transformed_condition)
        match_conditions.append(transformed_condition)

    return {"$match": {"$and": match_conditions}}

# Example AQL query
aql_query = """
SELECT c/context/other_context[at0004]/items[openEHR-EHR-CLUSTER.admin_salut.v0]/items[at0007]/items[at0014]/value/defining_code/code_string AS Centro,
 c/content[openEHR-EHR-SECTION.immunisation_list.v0]/items[openEHR-EHR-ACTION.medication.v1]/other_participations/performer AS Profesional,
 c/content[openEHR-EHR-SECTION.immunisation_list.v0]/items[openEHR-EHR-ACTION.medication.v1]/description[at0017]/items[openEHR-EHR-CLUSTER.medication.v2]/items[at0132]/value/mappings/target/code_string AS MarcaComercial,
 c/content[openEHR-EHR-SECTION.immunisation_list.v0]/items[openEHR-EHR-ACTION.medication.v1]/description[at0017]/items[openEHR-EHR-CLUSTER.medication.v2]/items[at0150]/value AS CodiNacional,
 c/content[openEHR-EHR-SECTION.immunisation_list.v0]/items[openEHR-EHR-ACTION.medication.v1]/time AS FechaAdmin,
 c/content[openEHR-EHR-SECTION.immunisation_list.v0]/items[openEHR-EHR-ACTION.medication.v1]/ism_transition/current_state/value AS Estado,
 c/feeder_audit/originating_system_item_ids AS cpc,
 c/content[openEHR-EHR-SECTION.immunisation_list.v0]/items[openEHR-EHR-ACTION.medication.v1]/description[at0017]/items[at0020] AS NombreGenerico,
 c/content[openEHR-EHR-SECTION.immunisation_list.v0]/items[openEHR-EHR-ACTION.medication.v1]/description[at0017]/items[openEHR-EHR-CLUSTER.medication.v2]/items[at0150] AS Lote,
 c/content[openEHR-EHR-SECTION.immunisation_list.v0]/items[openEHR-EHR-ACTION.medication.v1]/description[at0017]/items[openEHR-EHR-CLUSTER.medication.v2]/items[at0003] AS Caducidad,
 c/content[openEHR-EHR-SECTION.immunisation_list.v0]/items[openEHR-EHR-ACTION.medication.v1]/description[at0017]/items[at0140]/items[at0147] AS ViaAdmin,
 c/content[openEHR-EHR-SECTION.immunisation_list.v0]/items[openEHR-EHR-ACTION.medication.v1]/description[at0017]/items[at0140]/items[at0141] AS LocalizAdmin 
 FROM EHR e
      CONTAINS COMPOSITION c[openEHR-EHR-COMPOSITION.vaccination_list.v0] 
 WHERE (c/content[openEHR-EHR-SECTION.immunisation_list.v0]/items[openEHR-EHR-ACTION.medication.v1]/time >= '2020-02-15' 
      AND c/content[openEHR-EHR-SECTION.immunisation_list.v0]/items[openEHR-EHR-ACTION.medication.v1]/time <= '2022-03-15' 
      AND c/context/other_context[at0004]/items[openEHR-EHR-CLUSTER.admin_salut.v0]/items[at0007]/items[at0014]/value/defining_code/code_string = 'E08553936' 
      AND c/content[openEHR-EHR-SECTION.immunisation_list.v0]/items[openEHR-EHR-ACTION.medication.v1]/other_participations/performer/identifiers/id = '47958034K') 
 ORDER BY c/content[openEHR-EHR-SECTION.immunisation_list.v0]/items[openEHR-EHR-ACTION.medication.v1]/time AS FechaAdmin DESC
 LIMIT 100
"""

# Generate the $match block
match_block = transform_where_clause(aql_query)
print("Generated $match Block:")
print(match_block)