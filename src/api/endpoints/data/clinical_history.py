from fastapi import APIRouter, Request

from src.api.endpoints.data import GROUP, summaries, descriptions
from src.api.model.data.clinical_history import pull_model, load_resource_model
from src.config.config import config
from src.domain.ports.conversion.graph_converter import GraphConverter
from src.domain.services.conversion.resource2neo4j import Resource2Neo4j
from src.domain.services.data.fhir.get_fhir_patients import GetFHIRPatients
from src.domain.services.data.fhir.get_fhir_resources import GetFHIRResources
from src.domain.services.data.push_sync import PushSync
from src.domain.services.service import Service
from src.domain.services.sync_service import SyncService
from src.infrastructure.adapters.conversion.fhir2neo4j import FHIR2Neo4jConverter
from src.infrastructure.frameworks.data.history.load_patient import LoadPatientFramework, FHIR2NEO4J
from src.infrastructure.frameworks.data.history.pull_patient import PullPatientFramework
from src.infrastructure.frameworks.data.history.push_patient import PushPatientFramework
from src.infrastructure.frameworks.framework import NEO4J, NEO4J_PATIENT, stream, Framework

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
    framework = PushPatientFramework(output_stream=NEO4J)
    return framework.run(data)


@router.post(
    f"{GROUP}/load/patient",
    tags=tags,
    summary=summaries['history']['load'],
    description=descriptions['history']['load']
)
def load_patient(request: Request, params=load_resource_model):

    #   Extract data from query.

    token = params['token'] if params['token'] is not None else request.headers.get('Authorization')

    identifier: str = params['identifier']

    #   TODO gestionar tambien la lista de recursos FHIR que se van a insertar junto con el paciente

    #   Instantiate the framework.

    framework: Framework = LoadPatientFramework(config.fhir.uri, converter=FHIR2NEO4J, output_stream=NEO4J_PATIENT)

    #   Call framework to execute business processes and return result.

    params: dict = {
        'token': token,
        'identifier': identifier
    }

    return framework.run(params)
