from src.domain.ports.conversion.graph_converter import GraphConverter
from src.domain.services.sync_service import SyncService


class Resource2Neo4j(SyncService):
    def __init__(
            self,
            converter: GraphConverter,
            logger_=None
    ):
        super().__init__("Resource2Neo4j", logger_)
        self._converter: GraphConverter = converter

    def run(self, data: dict) -> dict:

        resource_type, resource_data = self._converter.node(data)

        node_edges, node_dates = self._converter.edges(data)

        payload = {
            "resource_data": resource_data,
            "resource_type": resource_type,
            "node_edges": node_edges,
            "node_dates": node_dates
        }

        self._logger.info('Service Resource2Neo4j finish.')

        return payload