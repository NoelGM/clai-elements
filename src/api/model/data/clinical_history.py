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


class _PullModel(BaseModel):
    identifier: str
    property: str


class _PushModel(BaseModel):
    data: str


pull_model: _PullModel = Depends(_pull_params)
push_model: _PushModel = Depends(_push_params)