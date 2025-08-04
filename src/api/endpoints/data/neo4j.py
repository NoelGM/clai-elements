from fastapi import APIRouter

from src.api.endpoints.data import GROUP
from src.config.config import config
from src.domain.services.data.get_sync import GetSync
from src.api.model.data.neo4j import get_patient_model
from src.domain.ports.dao.data_stream import DataStream
from src.domain.services.service import Service
from src.infrastructure.adapters.dao.neo4j_stream import Neo4jStream

router = APIRouter()

@router.post(f"{GROUP}/patient")
def get_patient(params=get_patient_model):

    adapter: DataStream = Neo4jStream(
        uri=config.database.neo4j.uri,
        user=config.database.neo4j.user,
        password=config.database.neo4j.password
    )

    params = {
        "node": "Patient",
        "identifier": params['identifier'],
        "topic": params['topic'],
        "field": "id",
        "parameters": {}
    }

    service: Service = GetSync(adapter)

    return service.run(params)
