from src.domain.services.sync_service import SyncService
from src.infrastructure.adapters.conversion.fhir.FHIR_to_graph import resource_to_edges, resource_to_node


class Bundle2Neo4j(SyncService):
    def __init__(
            self,
            logger_=None
    ):
        super().__init__("Bundle2Neo4j", logger_)

    def run(self, data: dict) -> dict:

        nodes = []
        edges = []
        dates = set()
        resource_types = []

        for entry in data.get('entry', []):
            resource = entry.get('resource')
            if not resource:
                continue
            # Si el recurso es un Bundle, procesar sus entries internos
            if resource.get('resourceType') == 'Bundle':
                for sub_entry in resource.get('entry', []):
                    sub_resource = sub_entry.get('resource')
                    if not sub_resource:
                        continue
                    resource_type, resource_data = resource_to_node(sub_resource)
                    node_edges, node_dates = resource_to_edges(sub_resource)
                    nodes.append(resource_data)
                    edges.extend(node_edges)
                    dates.update(node_dates)
                    resource_types.append(resource_type)
            else:
                resource_type, resource_data = resource_to_node(resource)
                node_edges, node_dates = resource_to_edges(resource)
                nodes.append(resource_data)
                edges.extend(node_edges)
                dates.update(node_dates)
                resource_types.append(resource_type)

        payload = {
            "resource_data": nodes,
            "node_edges": edges,
            "node_dates": list(dates),
            "resource_type": resource_types,
        }

        return payload