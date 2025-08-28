from fastapi import Depends
from pydantic import BaseModel


def _patient_params(
        given: str = None,
        family: str = None,
        id: str = None,
        token: str = None
):
    return {
        'given': given,
        'family': family,
        'id': id,
        'token': token
    }

class _PatientModel(BaseModel):
    given: str = None
    family: str = None
    id: str = None
    token: str = None


patient_model: _PatientModel = Depends(_patient_params)