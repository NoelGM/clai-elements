from fastapi import Depends
from pydantic import BaseModel


def _patient_params(
        given: str = None,
        family: str = None,
        id: str = None
):
    return {
        'given': given,
        'family': family,
        'id': id
    }

class _PatientModel(BaseModel):
    given: str = None
    family: str = None
    id: str = None


patient_model: _PatientModel = Depends(_patient_params)