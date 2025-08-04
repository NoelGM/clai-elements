from fastapi import Depends
from pydantic import BaseModel


def _get_patient_params(identifier: str, topic: str):
    return {
        "identifier": identifier,
        "topic": topic
    }

class _GetPatientModel(BaseModel):
    identifier: str
    topic: str

get_patient_model: _GetPatientModel = Depends(_get_patient_params)