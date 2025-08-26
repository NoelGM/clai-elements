from fastapi import APIRouter, Request

from src.api.endpoints.data import GROUP, summaries, descriptions
from src.api.model.data.dsforms import dsforms_model
from src.config.config import config
from src.domain.services.data.dsforms.get_ds_form_questionnaire import GetDsFormQuestionnaire
from src.domain.services.data.fhir.get_fhir_resources import GetFHIRResources

router = APIRouter()

SUBGROUP: str = '/ds'

tags: list[str] = ["DS Forms"]


@router.get(
    f"{GROUP}{SUBGROUP}/questionnaire",
    tags=tags,
    summary=summaries['ds']['questionnaire'],
    description=descriptions['ds']['questionnaire']
)
def questionnaire(request: Request, params=dsforms_model):

    token = request.headers.get('Authorization')

    query: str = '_format=json'

    resource_id: str = params.get('id') if params.get('id') is not None else ''

    service: GetFHIRResources = GetDsFormQuestionnaire(config.dsforms.uri)

    response = service.run(token, resource_id=resource_id, query=query)

    return response