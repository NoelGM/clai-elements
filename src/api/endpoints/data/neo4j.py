from fastapi import APIRouter, Depends

from src.domain.services.data.get_patien_sync import GetPatientSync
from src.api.model.data.neo4j import get_patient_params
from src.domain.ports.dao.data_stream import DataStream
from src.domain.services.service import Service
from src.infrastructure.adapters.dao.neo4j_stream import Neo4jStream

router = APIRouter()

@router.post("/patient")
def get_patient(params=Depends(get_patient_params)):

    adapter: DataStream = Neo4jStream(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="12345678a"
    )

    params = {
        "node": "Patient",
        "identifier": "AC1743089727161",
        "topic": "AllergyIntolerance",
        "field": "id",
        "parameters": {}
    }

    service: Service = GetPatientSync(adapter)

    return service.run(params)
