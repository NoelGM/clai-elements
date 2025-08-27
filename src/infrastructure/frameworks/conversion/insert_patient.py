from typing import Any

from src.domain.services.data.push_sync import PushSync
from src.domain.services.service import Service
from src.infrastructure.adapters.conversion.fhir.FHIR_to_graph import resource_to_node
from src.infrastructure.frameworks.framework import Framework, NEO4J, stream


class InsertPatientFramework(Framework):

    def __init__(self, output_stream: str = NEO4J):
        service: Service = PushSync(stream(output_stream))
        super().__init__(service, output_stream=output_stream)

    def run(self, data: dict) -> dict:
        resource_data, output_params = self._parse(data)
        return self._service.run(resource_data, output_params)

    def _parse(self, data) -> (Any, Any):
        resource_data, output_params = None, None
        if self._output_stream == NEO4J:
            resource_type, resource_data = resource_to_node(data)
            output_params = {
                "node": resource_type,
                "parameters": {}
            }
        return resource_data, output_params


