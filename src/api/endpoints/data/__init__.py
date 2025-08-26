from src.api.endpoints import BASE

GROUP: str = BASE + '/data'

SYMBOLS: list = [
    "Patient",
    "id",
    "AllergyIntolerance",
    "text"
]

#################
#   Summaries   #
#################

_ds_summaries: dict = {
    'questionnaire': 'Extract a FHIR questionnaire given by its id.'
}

_fhir_summaries: dict = {
    'get_patients': 'Get a patient or a patients boundle from a FHIR server.'
}

_history_summaries: dict = {
    'pull_patient': 'Extract patient data from the project database.',
    'push_patient': 'Insert patient data into the project database.'
}

summaries: dict = {
    'ds': _ds_summaries,
    'fhir': _fhir_summaries,
    'history': _history_summaries
}

####################
#   Descriptions   #
####################

_ds_descriptions: dict = {
    'questionnaire': """
        Extract a questionnaire resource from a FHIR server, from its questionnaire id.
        \n\t- Input: the questionnaire id.
        \n\t- Output: contents of the questionnaire.
    """,
}

_fhir_descriptions: dict = {
    'get_patients': """
        Send query to a FHIR server to obtain data from a patient or a patients bundle.
        \n\t- Input: the following optional parameters:
        \n\t\t- the patient id (if not provided, patient boundle will be return)
        \n\t\t- the patient name (if provided, patient boundle matching such name will be return)
        \n\t\t- the patient family name (if provided, patient boundle matching such family name will be return)
        \n\t- Output: response from the FHIR server.
    """
}

_history_descriptions: dict = {
    'pull_patient': """
        Get data from a patient from the project database stipulating filters and secondary node. TODO: Completa @Martin.
    """,
    'push_patient': """
        Insert a new patient to the project database given by an string included the json formatted patient data. TODO: Completa @Martin.
    """
}

descriptions: dict = {
    'ds': _ds_descriptions,
    'fhir': _fhir_descriptions,
    'history': _history_descriptions
}