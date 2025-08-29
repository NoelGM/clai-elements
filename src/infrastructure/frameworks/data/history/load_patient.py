from src.domain.ports.conversion.graph_converter import GraphConverter
from src.domain.services.conversion.resource2neo4j import Resource2Neo4j
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

        #   2.- Extract data from FHIR server. For that, invoke FHIR microservice.

        fhir_service: GetFHIRResources = GetFHIRPatients(self._data_uri)

        data = fhir_service.run(token, resource_id=identifier)

        #   3.- Convert data from origin. For that, invoke conversion microservice.

        conversion_service: SyncService = Resource2Neo4j(self._converter)
        payload = conversion_service.run(data)

        #   4.- Save data and return response. Invoke framework-owned microservice.

        output_params = {
            "node": payload.get("resource_type"),
            "parameters": {}
        }

        return self._service.run(payload, output_params)