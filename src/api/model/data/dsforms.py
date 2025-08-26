from fastapi import Depends
from pydantic import BaseModel


def _dsforms_params(
        id: str = None
):
    return {
        'id': id
    }

class _DsFormsModel(BaseModel):
    id: str = None


dsforms_model: _DsFormsModel = Depends(_dsforms_params)