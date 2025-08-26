from fastapi import APIRouter

from src.api.endpoints.conversion import GROUP, summaries, descriptions
from src.infrastructure.frameworks.conversion.insert_patient import InsertPatientFramework
from src.infrastructure.frameworks.conversion.insert_patients import InsertPatientsFramework
from src.infrastructure.frameworks.framework import NEO4J, NEO4J_PATIENT

router = APIRouter()

tags: list[str] = ["Data Conversion"]


@router.post(
    f"{GROUP}/patient",
    tags=tags,
    summary=summaries['insert_patient'],
    description=descriptions['insert_patient']
)
def insert_patient(data: dict):
    framework = InsertPatientFramework(output_stream=NEO4J)
    return framework.run(data)

@router.post(
    f"{GROUP}/patients",
    tags=tags,
    summary=summaries['insert_patients'],
    description=descriptions['insert_patients']
)
def insert_patients(data: dict):
    framework = InsertPatientsFramework(output_stream=NEO4J_PATIENT)
    return framework.run(data)
