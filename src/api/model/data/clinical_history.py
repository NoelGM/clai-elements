from fastapi import Depends
from pydantic import BaseModel


def _pull_params(identifier: str, property: str):
    return {
        "identifier": identifier,
        "property": property
    }


def _push_params(data: str):
    return {
        "data": data
    }

def _load_resource_params(identifier: str, token: str):
    return {
        'identifier': identifier,
        'token': token
    }


class _PullModel(BaseModel):
    identifier: str
    property: str


class _PushModel(BaseModel):
    data: str


class _LoadResourceModel(BaseModel):
    identifier: str
    token: str = None
    #   TODO poner la lista de recursos FHIR que se quieren insertar junto con el paciente


pull_model: _PullModel = Depends(_pull_params)
push_model: _PushModel = Depends(_push_params)
load_resource_model: _LoadResourceModel = Depends(_load_resource_params)