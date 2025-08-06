
from fastapi import APIRouter, Request

from src.api import RESP500
from src.api.endpoints.data import GROUP
from src.api.model.data.fhir import patient_model
from src.config.config import config
from src.domain.services.data.fhir.get_fhir_patients import GetFHIRPatients
from src.domain.services.data.fhir.get_fhir_resources import GetFHIRResources
from src.domain.services.service import Service

router = APIRouter()

SUBGROUP: str = '/fhir'


@router.get(f"{GROUP}{SUBGROUP}/Patient")
def get_patients(request: Request, params=patient_model):

    token = request.headers.get('Authorization')

    query: str = "".join([f"{key}={params.get(key)}&" for key in list(filter(lambda x: params.get(x) is not None and x != 'id', params.keys()))])
    query=query[:-1]

    resource_id: str = params.get('id') if params.get('id') is not None else ''

    service: GetFHIRResources = GetFHIRPatients(config.fhir.uri)

    response = service.run(token, resource_id=resource_id, query=query)

    return response
