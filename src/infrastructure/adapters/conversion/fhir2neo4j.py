from typing import Any

from src.domain.ports.conversion.graph_converter import GraphConverter
from src.infrastructure.utils.fhir.FHIR_to_graph import resource_to_node, resource_to_edges


class FHIR2Neo4jConverter(GraphConverter):

    def node(self, data: Any) -> (Any, Any):
        resource_type, resource_data = resource_to_node(data)
        return resource_type, resource_data

    def edges(self, data: Any) -> (Any, Any):
        node_edges, node_dates = resource_to_edges(data)
        return node_edges, node_dates