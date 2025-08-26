from fastapi import APIRouter

from src.api.endpoints.data import GROUP, SYMBOLS, summaries, descriptions
from src.api.model.data.clinical_history import pull_model
from src.config.config import config
from src.domain.ports.dao.data_stream import DataStream
from src.domain.services.data.pull_sync import PullSync
from src.domain.services.data.push_sync import PushSync
from src.domain.services.service import Service
from src.infrastructure.adapters.dao.neo4j_stream import Neo4jStream

router = APIRouter()

tags: list[str] = ["Clinical history"]


@router.get(
    f"{GROUP}/patient",
    tags=tags,
    summary=summaries['history']['pull_patient'],
    description=descriptions['history']['pull_patient']
)
def pull_patient(params=pull_model):

    adapter: DataStream = Neo4jStream(
        uri=config.database.neo4j.uri,
        user=config.database.neo4j.user,
        password=config.database.neo4j.password,
        symbols=SYMBOLS
    )

    input_params = {
        "main_node": "Patient",
        "secondary_node": params['secondary_node'],
        "filter_field": "id",
        "filter_value": params['filter_value'],
        "parameters": {}
    }

    service: Service = PullSync(adapter)

    return service.run(input_params)


@router.post(
    f"{GROUP}/patient",
    tags=tags,
    summary=summaries['history']['push_patient'],
    description=descriptions['history']['push_patient']
)
def push_patient(data: dict):

    adapter: DataStream = Neo4jStream(
        uri=config.database.neo4j.uri,
        user=config.database.neo4j.user,
        password=config.database.neo4j.password
    )

    output_params = {
        "node": "Patient",
        "parameters": {}
    }

    service: Service = PushSync(adapter)

    return service.run(data, output_params)
