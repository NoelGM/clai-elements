from fastapi import Depends
from pydantic import BaseModel


def _pull_params(filter_value: str, secondary_node: str):
    return {
        "filter_value": filter_value,
        "secondary_node": secondary_node
    }


def _push_params(data: str):
    return {
        "data": data
    }


class _PullModel(BaseModel):
    filter_value: str
    secondary_node: str


class _PushModel(BaseModel):
    data: str


pull_model: _PullModel = Depends(_pull_params)
push_model: _PushModel = Depends(_push_params)