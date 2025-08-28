from src.domain.services.conversion.bundle2neo4j import Bundle2Neo4j
from src.domain.services.data.push_sync import PushSync
from src.domain.services.service import Service
from src.domain.services.sync_service import SyncService
from src.infrastructure.adapters.conversion.fhir2neo4j import FHIR2Neo4jConverter
from src.infrastructure.frameworks.framework import Framework, stream, NEO4J_PATIENT


class InsertPatientsFramework(Framework):

    def __init__(self, output_stream: str = NEO4J_PATIENT):
        service: Service = PushSync(stream(output_stream))
        super().__init__(service, output_stream=output_stream)

    def run(self, data: dict) -> dict:

        #   Convert data from origin.

        conversion_service: SyncService = Bundle2Neo4j(FHIR2Neo4jConverter())
        payload = conversion_service.run(data)

        #   Save data and return response.

        output_params = {
            "node": payload.get("resource_type"),
            "parameters": {}
        }

        try:
            output_params["patientId"] = data["entry"][0]["resource"]["id"]
        except Exception as e:
            self._logger.warning(f'Error while parsing service data: {str(e)}. Patient id will be not included in the params.')

        return self._service.run(payload, output_params)




