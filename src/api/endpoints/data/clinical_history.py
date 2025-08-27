from fastapi import APIRouter

from src.api.endpoints.data import GROUP, summaries, descriptions
from src.api.model.data.clinical_history import pull_model
from src.config.config import config
from src.domain.ports.dao.data_stream import DataStream
from src.domain.services.data.push_sync import PushSync
from src.domain.services.service import Service
from src.infrastructure.adapters.dao.neo4j_stream import Neo4jStream, PARAMETERS, NODE
from src.infrastructure.frameworks.data.history.pull_patient import PullPatientFramework
from src.infrastructure.frameworks.data.history.push_patient import PushPatientFramework
from src.infrastructure.frameworks.framework import NEO4J

router = APIRouter()

tags: list[str] = ["Clinical history"]


@router.get(
    f"{GROUP}/patient",
    tags=tags,
    summary=summaries['history']['pull_patient'],
    description=descriptions['history']['pull_patient']
)
def pull_patient(params=pull_model):
    input_params: dict = {
        'property': params['property'],
        'identifier': params['identifier']
    }
    framework = PullPatientFramework(input_stream=NEO4J)
    return framework.run(input_params)


@router.post(
    f"{GROUP}/patient",
    tags=tags,
    summary=summaries['history']['push_patient'],
    description=descriptions['history']['push_patient']
)
def push_patient(data: dict):

    # adapter: DataStream = Neo4jStream(
    #     uri=config.database.neo4j.uri,
    #     user=config.database.neo4j.user,
    #     password=config.database.neo4j.password
    # )
    #
    # output_params = {
    #     NODE: "Patient",
    #     PARAMETERS: {}
    # }
    #
    # service: Service = PushSync(adapter)
    #
    # return service.run(data, output_params)

    framework = PushPatientFramework(output_stream=NEO4J)
    return framework.run(data)


