from src.infrastructure.adapters.dao.neo4j_stream import Neo4jStream


class PatientStream(Neo4jStream):

    def __init__(
            self,
            uri: str,
            user: str,
            password: str,
            symbols: list = None
    ):
        super().__init__(uri, user, password, symbols=symbols, unique_node="patientId", resource="Patient")

    