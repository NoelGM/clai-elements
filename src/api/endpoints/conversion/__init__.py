from src.api.endpoints import BASE

GROUP: str = BASE + '/conversion'

summaries: dict = {
    'insert_patient': 'Convert FHIR patient data to Neo4j and insert into clinical history database.',
    'insert_patients': 'Convert FHIR patients boundle to Neo4j and insert into clinical history database.'
}

descriptions: dict = {
    'insert_patient': """
    Convert patient data arising from a FHIR server to an specific database base format (at this moment Neo4j) an insert into such database.
    \n\t- Input: a json text with FHIR format patient data.
    \n\t- Output: response from the persistence operation.
    """,
    'insert_patients': """
    Convert a patient boundle data arising from a FHIR server to an specific database base format (at this moment Neo4j) an insert into such database.
    \n\t- Input: a json text with FHIR format patient boundle data.
    \n\t- Output: response from the persistence operation.
    """
}
