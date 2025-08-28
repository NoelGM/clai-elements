from src.domain.services.data.push_sync import PushSync
from src.domain.services.service import Service
from src.infrastructure.adapters.dao.neo4j_stream import NODE, PARAMETERS
from src.infrastructure.frameworks.framework import Framework, NEO4J, stream


class PushPatientFramework(Framework):

    def __init__(self, output_stream: str = NEO4J):
        service: Service = PushSync(stream(output_stream))
        super().__init__(service, output_stream=output_stream)

    def run(self, data: dict) -> dict:
        output_params = {
            NODE: "Patient",
            PARAMETERS: {}
        }
        return self._service.run(data, output_params)
