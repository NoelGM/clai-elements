from src.domain.services.conversion.bundle2neo4j import Bundle2Neo4j
from src.domain.services.data.push_sync import PushSync
from src.domain.services.service import Service
from src.domain.services.sync_service import SyncService
from src.infrastructure.frameworks.framework import Framework, stream, NEO4J_PATIENT


class InsertPatientsFramework(Framework):

    def __init__(self, output_stream: str = NEO4J_PATIENT):
        service: Service = PushSync(stream(output_stream))
        self._output_stream: str = output_stream
        super().__init__(service)

    def run(self, data: dict) -> dict:

        conversion_service: SyncService = Bundle2Neo4j()

        payload = conversion_service.run(data)

        output_params = {
            "node": payload.get("resource_type"),
            "parameters": {}
        }

        try:
            output_params["patientId"] = data["entry"][0]["resource"]["id"]
        except Exception as e:
            pass

        return self._service.run(payload, output_params)




