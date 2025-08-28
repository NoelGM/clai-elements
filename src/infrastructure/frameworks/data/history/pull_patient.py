from src.domain.services.data.pull_sync import PullSync
from src.domain.services.service import Service
from src.infrastructure.adapters.dao.neo4j_stream import MAIN_NODE, SECONDARY_NODE, FILTER_FIELD, FILTER_VALUE, \
    PARAMETERS
from src.infrastructure.frameworks.conversion import SYMBOLS
from src.infrastructure.frameworks.framework import Framework, NEO4J, stream


class PullPatientFramework(Framework):

    def __init__(self, input_stream: str = NEO4J):
        service: Service = PullSync(stream(input_stream, args=SYMBOLS))
        super().__init__(service, input_stream=input_stream)

    def run(self, data: dict) -> dict:
        return self._service.run(self._parse(data))

    def _parse(self, data: dict) -> dict:
        result: dict = {}
        if self._input_stream == NEO4J:
            result = {
                MAIN_NODE: "Patient",
                SECONDARY_NODE: data.get('property', ''),
                FILTER_FIELD: "id",
                FILTER_VALUE: data.get('identifier', ''),
                PARAMETERS: {}
            }
        return result
