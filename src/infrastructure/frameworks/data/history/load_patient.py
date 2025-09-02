from src.domain.ports.conversion.graph_converter import GraphConverter
from src.domain.services.conversion.bundle2neo4j import Bundle2Neo4j
from src.domain.services.data.fhir.get_fhir_patients import GetFHIRPatients
from src.domain.services.data.fhir.get_fhir_resources import GetFHIRResources
from src.domain.services.data.push_sync import PushSync
from src.domain.services.service import Service
from src.domain.services.sync_service import SyncService
from src.infrastructure.adapters.conversion.fhir2neo4j import FHIR2Neo4jConverter
from src.infrastructure.frameworks.framework import NEO4J_PATIENT, Framework, stream

FHIR2NEO4J: str = 'fhir2neo4j'

def converter_(label: str) -> GraphConverter:
    if label == FHIR2NEO4J:
        return FHIR2Neo4jConverter()
    return FHIR2Neo4jConverter()


class LoadPatientFramework(Framework):

    def __init__(
            self,
            data_uri: str,
            converter: str = FHIR2NEO4J,
            output_stream: str = NEO4J_PATIENT
    ):
        service: Service = PushSync(stream(output_stream))
        super().__init__(service, output_stream=output_stream)
        self._data_uri: str = data_uri
        self._converter: GraphConverter = converter_(converter)

    def run(self, params: dict) -> dict:

        #   1.- Extract params.

        token: str = params['token']
        identifier: str = params['identifier']

        #   2.- Extract patient data from FHIR server. For that, invoke FHIR microservice.

        fhir_patient_service: GetFHIRResources = GetFHIRPatients(self._data_uri)

        patient_data = fhir_patient_service.run(token, resource_id=identifier)

        #   2.1.- Create resource Bundle and set patient data

        bundle = {
            "resourceType": "Bundle",
            "type": "batch-response",
            "entry": [
                {
                    "resource": patient_data
                }
            ]
        }

        #   2.2.- Extract the resources data associated with the patient

        resource_types = [
                ("Encounters", "Encounter"),
                ("Observations", "Observation"),
                ("Immunizations", "Immunization"),
                ("Conditions", "Condition"),
                ("MedicationRequests", "MedicationRequest"),
                ("DocumentReferences", "DocumentReference"),
                ("DiagnosticReports", "DiagnosticReport"),
                ("Procedures", "Procedure"),
                ("ExplanationOfBenefits", "ExplanationOfBenefit"),
                ("Claims", "Claim"),
                ("AllergyIntolerances", "AllergyIntolerance")
            ]

        for service_name, resource_type in resource_types:
            fhir_resource_service: GetFHIRResources = GetFHIRResources(service_name, self._data_uri, resource_type)
            resource_data = fhir_resource_service.run(token, query=f"patient=Patient/{identifier}&_count=200&_sort=-_lastUpdated")
            bundle["entry"].append({"resource": resource_data})

        #   3.- Convert data from origin. For that, invoke conversion microservice.

        conversion_service: SyncService = Bundle2Neo4j(self._converter)
        payload = conversion_service.run(bundle)

        #   4.- Save data and return response. Invoke framework-owned microservice.

        output_params = {
            "node": payload.get("resource_type"),
            "parameters": {}
        }

        return self._service.run(payload, output_params)