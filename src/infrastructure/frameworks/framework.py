from abc import ABC, abstractmethod

from src.config.config import config
from src.config.logger_config import logger
from src.domain.ports.dao.data_stream import DataStream
from src.domain.services.service import Service
from src.infrastructure.adapters.dao.neo4j_stream import Neo4jStream
from src.infrastructure.adapters.dao.patient_stream import Neo4jPatientStream

NEO4J: str = 'neo4j'
NEO4J_PATIENT: str = 'neo4j_patient'

def stream(label: str) -> DataStream:
    adapter: DataStream = None
    if label == NEO4J:
        adapter: DataStream = Neo4jStream(
            uri=config.database.neo4j.uri,
            user=config.database.neo4j.user,
            password=config.database.neo4j.password
        )
    elif label == NEO4J_PATIENT:
        adapter: DataStream = Neo4jPatientStream(
            uri=config.database.neo4j.uri,
            user=config.database.neo4j.user,
            password=config.database.neo4j.password
        )
    return adapter


class Framework(ABC):

    def __init__(
            self,
            service: Service,
            logger_ = None
    ):
        self._service: Service = service
        self._logger = logger.bind(category="services") if logger_ is None else logger_

    def service(self) -> Service:
        return self._service

    @abstractmethod
    def run(self, *args) -> dict:
        raise NotImplementedError("Method not implemented at the abstract level.")

