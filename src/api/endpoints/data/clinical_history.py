from fastapi import APIRouter, Request

from src.api.endpoints.data import GROUP, summaries, descriptions
from src.api.model.data.clinical_history import pull_model, load_resource_model
from src.config.config import config
from src.infrastructure.frameworks.data.history.load_patient import LoadPatientFramework, FHIR2NEO4J
from src.infrastructure.frameworks.data.history.pull_patient import PullPatientFramework
from src.infrastructure.frameworks.data.history.push_patient import PushPatientFramework
from src.infrastructure.frameworks.framework import NEO4J, NEO4J_PATIENT, Framework

router = APIRouter()

tags: list[str] = ["Clinical history"]

#   NGM: Se ha acordado no exponer este servicio
# @router.get(
#     f"{GROUP}/patient",
#     tags=tags,
#     summary=summaries['history']['pull_patient'],
#     description=descriptions['history']['pull_patient']
# )
def pull_patient(params=pull_model):
    input_params: dict = {
        'property': params['property'],
        'identifier': params['identifier']
    }
    framework = PullPatientFramework(input_stream=NEO4J)
    return framework.run(input_params)


#   NGM: Se ha acordado no exponer este servicio
# @router.post(
#     f"{GROUP}/patient",
#     tags=tags,
#     summary=summaries['history']['push_patient'],
#     description=descriptions['history']['push_patient']
# )
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

    #   Instantiate the framework.

    framework: Framework = LoadPatientFramework(config.fhir.uri, converter=FHIR2NEO4J, output_stream=NEO4J_PATIENT)

    #   Call framework to execute business processes and return result.

    params: dict = {
        'token': token,
        'identifier': identifier
    }

    return framework.run(params)
