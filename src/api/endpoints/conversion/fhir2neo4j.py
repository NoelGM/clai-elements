from fastapi import APIRouter

from src.domain.services.data.conversion.bundle2neo4j import Bundle2Neo4j
from src.domain.services.sync_service import SyncService
from src.infrastructure.adapters.dao.patient_stream import PatientStream
from src.api.endpoints.conversion import GROUP
from src.config.config import config
from src.domain.ports.dao.data_stream import DataStream
from src.domain.services.data.push_sync import PushSync
from src.domain.services.service import Service
from src.infrastructure.adapters.conversion.fhir.FHIR_to_graph import resource_to_edges, resource_to_node
from src.infrastructure.adapters.dao.neo4j_stream import Neo4jStream

router = APIRouter()


@router.post(f"{GROUP}/patient")
def insert_resource(data: dict):

    resource_type, resource_data = resource_to_node(data)

    adapter: DataStream = Neo4jStream(
        uri=config.database.neo4j.uri,
        user=config.database.neo4j.user,
        password=config.database.neo4j.password
    )

    output_params = {
        "node": resource_type,
        "parameters": {}
    }

    service: Service = PushSync(adapter)

    return service.run(resource_data, output_params)

@router.post(f"{GROUP}/patients")
def insert_resources(data: dict):

    adapter: DataStream = PatientStream(
        uri=config.database.neo4j.uri,
        user=config.database.neo4j.user,
        password=config.database.neo4j.password
    )

    conversion_service: SyncService = Bundle2Neo4j()

    payload = conversion_service.run(data)
    
    output_params = {
        "node": payload.get("resource_type"),
        "parameters": {}
    }

    try:
        output_params["patientId"] = data["entry"][0]["resource"]["id"]
    except Exception:
        pass

    service: Service = PushSync(adapter)

    return service.run(payload, output_params)
