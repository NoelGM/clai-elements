from src.domain.ports.conversion.graph_converter import GraphConverter
from src.domain.services.sync_service import SyncService


class Bundle2Neo4j(SyncService):
    def __init__(
            self,
            converter: GraphConverter,
            logger_=None
    ):
        super().__init__("Bundle2Neo4j", logger_)
        self._converter: GraphConverter = converter

    def run(self, data: dict) -> dict:

        self._logger.info('Running Bundle2Neo4j service...')

        nodes = []
        edges = []
        dates = set()
        resource_types = []

        if 'entry' not in data.keys():
            self._logger.warning('Non entry node in input data.')

        for entry in data.get('entry', []):

            resource = entry.get('resource')

            if not resource:
                self._logger.warning('Non resource found.')
                continue

            if resource.get('resourceType') == 'Bundle':
                for sub_entry in resource.get('entry', []):
                    sub_resource = sub_entry.get('resource')
                    if not sub_resource:
                        self._logger.warning('Non sub-resource found.')
                        continue
                    resource_type, resource_data = self._converter.node(sub_resource)
                    node_edges, node_dates = self._converter.edges(sub_resource)
                    nodes.append(resource_data)
                    edges.extend(node_edges)
                    dates.update(node_dates)
                    resource_types.append(resource_type)
            else:
                try:
                    resource_type, resource_data = self._converter.node(resource)
                    node_edges, node_dates = self._converter.edges(resource)
                    nodes.append(resource_data)
                    edges.extend(node_edges)
                    dates.update(node_dates)
                    resource_types.append(resource_type)
                except Exception as e:
                    self._logger.warning(f'Error while converting patient: {str(e)}. {str(resource)}')

        payload = {
            "resource_data": nodes,
            "node_edges": edges,
            "node_dates": list(dates),
            "resource_type": resource_types,
        }

        self._logger.info('Service Bundle2Neo4j finish.')

        return payload