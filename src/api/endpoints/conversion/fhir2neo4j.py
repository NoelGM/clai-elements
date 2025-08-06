from fastapi import APIRouter

from src.api.endpoints.conversion import GROUP
from src.config.config import config
from src.domain.ports.dao.data_stream import DataStream
from src.domain.services.data.push_sync import PushSync
from src.domain.services.service import Service
from src.infrastructure.adapters.conversion.fhir.FHIR_to_graph import resource_to_node
from src.infrastructure.adapters.dao.neo4j_stream import Neo4jStream

router = APIRouter()


@router.post(f"{GROUP}/resource")
def insert_resource(data: dict):

    resource_type, resource_data = resource_to_node(data)

    adapter: DataStream = Neo4jStream(
        uri=config.database.neo4j.uri,
        user=config.database.neo4j.user,
        password=config.database.neo4j.password
    )

    output_params = {
        "node": resource_type,
        "parameters": {}
    }

    service: Service = PushSync(adapter)

    return service.run(resource_data, output_params)
