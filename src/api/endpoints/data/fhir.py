from fastapi import APIRouter, Request

from src.api.endpoints.data import GROUP, summaries, descriptions
from src.api.model.data.fhir import patient_model
from src.config.config import config
from src.domain.services.data.fhir.get_fhir_patients import GetFHIRPatients
from src.domain.services.data.fhir.get_fhir_resources import GetFHIRResources

router = APIRouter()

SUBGROUP: str = '/fhir'

tags: list[str] = ["FHIR Server"]


@router.get(
    f"{GROUP}{SUBGROUP}/Patient",
    tags=tags,
    summary=summaries['fhir']['patient'],
    description=descriptions['fhir']['patient']
)
def patient(request: Request, params=patient_model):

    #   Get the token.

    token = params['token'] if params['token'] is not None else request.headers.get('Authorization')

    #   Create the query params from the input.

    query: str = "".join([f"{key}={params.get(key)}&" for key in list(
        filter(lambda x: params.get(x) is not None and x not in ['id', 'token'], params.keys()))])
    query=query[:-1]

    resource_id: str = params.get('id') if params.get('id') is not None else ''

    #   Instantiate business logic.

    service: GetFHIRResources = GetFHIRPatients(config.fhir.uri)

    #   Execute service and return response.

    response = service.run(token, resource_id=resource_id, query=query)

    return response
