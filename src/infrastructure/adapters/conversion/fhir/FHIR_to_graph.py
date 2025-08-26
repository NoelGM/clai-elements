import re

from src.infrastructure.adapters.conversion.fhir.FHIR_to_string import FHIR_to_string

camel_pattern1 = re.compile(r'(.)([A-Z][a-z]+)')
camel_pattern2 = re.compile(r'([a-z0-9])([A-Z])')

def split_camel(text):
    new_text = camel_pattern1.sub(r'\1_\2', text.strip())
    new_text = camel_pattern2.sub(r'\1_\2', new_text.strip())
    return new_text.lower().strip()

def flatten_fhir(nested_json):
    out = {}

    # Fields we want to exclude from the graph
    EXCLUDED_SUFFIXES = [
        '_url', '_reference_reference', '_boolean', '_coding_0_system',
        '_use', 'meta'
    ]

    # Specific redundant keys that don't add value
    REDUNDANT_KEYS = [
        # 'resource_type', 'name_1_text', 'identifier_1_type_text',
        # 'identifier_1_type_coding_0_display', 'identifier_1_type_coding_0_code'
    ]

    def flatten(json_to_flatten, name=''):
        if name == 'text_':
            return
        elif isinstance(json_to_flatten, dict):
            for sub_attribute in json_to_flatten:
                flatten(json_to_flatten[sub_attribute], name + split_camel(sub_attribute) + '_')
        elif isinstance(json_to_flatten, list):
            for i, sub_json in enumerate(json_to_flatten):
                flatten(sub_json, name + str(i) + '_')
        else:
            attrib_name = name[:-1]
            if (
                not any(excluded in attrib_name.lower() for excluded in EXCLUDED_SUFFIXES)
                and attrib_name not in REDUNDANT_KEYS
            ):
                out[attrib_name] = json_to_flatten

    flatten(nested_json)
    return out

def flat_fhir_to_json_str(flat_fhir, name, fhir_str):
    import ollama 
    
    def translate_to_spanish(text):
        response = ollama.chat(model="lauchacarro/qwen2.5-translator:latest", messages=[
            {"role": "system", "content": "You are a professional translator from English to Spanish. Do not change date formats — leave them as yyyy-mm-dd."},
            {"role": "user", "content": text}])
        translated_text = response['message']['content'] if 'message' in response else text
        return translated_text.replace('"', '\\"')
    
    output = '{' + f'name: "{name}",'

    if fhir_str is not None:
        fhir_str = ' '.join(fhir_str)
        fhir_str = translate_to_spanish(fhir_str)
        # print(fhir_str)
        output += f'text: "{fhir_str}",'

    for attrib in flat_fhir:
        output += f'{attrib}: "{flat_fhir[attrib]}",'

    output = output[:-1]  
    output += '}'

    return output

# def text_summary(text):
#
#     summarize_tool = SummarizeTool()
#     summary = summarize_tool.execute(text)
#     escaped_summary = summary.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
#     return escaped_summary


def id_to_property_str(id):
    return "{id: '" + id + "'}"

def npi_to_property_str(id):
    return "{identifier_0_value: '" + id + "', identifier_0_system: 'http://hl7.org/fhir/sid/us-npi'}"

def extract_id(value: str):
    if value.startswith('urn:uuid:'):
        return id_to_property_str(value[9:])

    # Identify common delimiters
    delimiters = ['|', '/']
    delimiter = next((d for d in delimiters if d in value), None)

    # If a delimiter exists, extract the part after it
    if delimiter:
        index = value.index(delimiter)
        return id_to_property_str(value[index + 1:])

    # Handle local references (e.g., '#')
    elif value.startswith('#'):
        return None

    # Assume the last segment of an alphanumeric string is the ID
    elif any(char.isdigit() for char in value):
        parts = value.split(delimiter) if delimiter else [value]
        return id_to_property_str(parts[-1])

    else:
        print(f'Unrecognized reference: {value}')
        return None


date_containing_fields=[
    'effectiveDateTime', 'recordedDate', 'issued',
    'start', 'end', 'authoredOn', 'onsetDateTime',
    'abatementDateTime', 'occurrenceDateTime', 'created'
]
date_pattern = re.compile(r'([0-9]+)-([0-9]+)-([0-9]+)')
def extract_date(value: str):
    data_parts = date_pattern.findall(value)[0]
    return f'{data_parts[1]}/{data_parts[2]}/{data_parts[0]}' #Formateo de date mm/dd/aaaa

def resource_to_edges(resource):
    resource_type = resource['resourceType']
    resource_id = resource['id']

    references = []
    dates = []
    def search(json_to_flatten, name=''):
        if name == 'text_':
            return
        elif type(json_to_flatten) is dict:
            for sub_attribute in json_to_flatten:
                if sub_attribute == 'reference':
                    relation = name[:-1]
                    if relation.endswith('subject') or relation.endswith('patient'):
                        relation = 'patient'
                    reference_id_str = extract_id(json_to_flatten[sub_attribute])
                    if reference_id_str is not None:
                        cypher = f'''
                            MATCH (n1 {id_to_property_str(resource_id)}), (n2 {reference_id_str})
                            CREATE (n2)-[:{relation}]->(n1)
                        '''
                        references.append(cypher)
                elif resource_type == 'PractitionerRole' and sub_attribute == 'practitioner':
                    relation = 'practitioner'
                    reference_id_str = npi_to_property_str(json_to_flatten[sub_attribute]['identifier']['value'])
                    if reference_id_str is not None:
                        cypher = f'''
                            MATCH (n1 {id_to_property_str(resource_id)}), (n2 {reference_id_str})
                            CREATE (n2)-[:{relation}]->(n1)
                        '''
                        references.append(cypher)
                elif resource_type == 'PractitionerRole' and sub_attribute == 'organization':
                    relation = 'organization'
                    reference_id_str = id_to_property_str(json_to_flatten[sub_attribute]['identifier']['value'])
                    if reference_id_str is not None:
                        cypher = f'''
                            MATCH (n1 {id_to_property_str(resource_id)}), (n2 {reference_id_str})
                            CREATE (n2)-[:{relation}]->(n1)
                        '''
                        references.append(cypher)
                elif sub_attribute in date_containing_fields:
                    relation = name + split_camel(sub_attribute)
                    date_str = extract_date(json_to_flatten[sub_attribute])
                    if date_str is not None:
                        dates.append(date_str)
                        cypher = f'''
                            MATCH (n1 {id_to_property_str(resource_id)}), (n2 {id_to_property_str(date_str)})
                            MERGE (n1)-[:{relation}]->(n2)
                        '''
                        references.append(cypher)
                else:
                    search(json_to_flatten[sub_attribute], name + split_camel(sub_attribute) + '_')
        elif type(json_to_flatten) is list:
            for i, sub_json in enumerate(json_to_flatten):
                search(sub_json, name + str(i) + '_')

    search(resource)
    return references, dates

def resource_to_node(resource):
    resource_type = resource['resourceType']
    flat_resource = flat_fhir_to_json_str(flatten_fhir(resource), resource_name(resource), FHIR_to_string(resource))
    # summary = text_summary(flatten_fhir(resource))
    # if flat_resource.endswith('}'):
    #     flat_resource = flat_resource[:-1] + f', summary: "{summary}"}}'
    # else:
    #     flat_resource = f'{{summary: "{summary}"}}'

    # return f'CREATE (:{resource_type}:resource {flat_resource})'
    return resource_type, flat_resource


def resource_name(resource): #Metodo para obtener el nombre del paciente, cambia estructura entre synthea y servidor ehr
    
    rt = resource['resourceType']
    if rt == 'Patient':        
        
        name_data = resource["name"][0]
        # First, check if 'text' exists, which may already contain the full name
        if "text" in name_data:
            return name_data["text"]
        
        # Extract given name
        given_name = name_data.get("given", ["Unknown"])[0]
        
        # Extract family name from the 'extension' field
        family_names = []
        for ext in resource["name"][0].get("extension", []):
            if "valueString" in ext:
                family_names.append(ext["valueString"])
        
        # Join family names if found, otherwise return "Unknown"
        family_name = " ".join(family_names) if family_names else "Unknown"
        
        return f'{given_name} {family_name}' 
    else:
        return rt
    
# def resource_name(resource):
#     rt = resource['resourceType']
#     if rt == 'Patient':
#         return f'{resource["name"][0]["given"][0]} {resource["name"][0]["family"]}'
#     else:
#         return rt
