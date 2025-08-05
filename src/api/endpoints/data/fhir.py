import requests
from fastapi import APIRouter

from src.api import RESP500
from src.api.endpoints.data import GROUP
from src.config.config import config

router = APIRouter()

SUBGROUP: str = '/fhir'


@router.get(f"{GROUP}{SUBGROUP}/Patient")
def get_patients():

    uri: str = config.fhir.uri + '/Patient'

    token: str = ''

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    try:

        response = requests.get(uri, headers=headers)
        response.raise_for_status()
        return response.json()

    except Exception as e:

        return RESP500
