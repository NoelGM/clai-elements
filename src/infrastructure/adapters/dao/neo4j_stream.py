from typing import Any
from neo4j import GraphDatabase
from pandas import DataFrame

from src.domain.ports.dao.data_stream import DataStream


class Neo4jStream(DataStream):

    def __init__(self, uri: str, user: str, password: str):
        super().__init__()
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def pull(
            self,
            args: dict
    ) -> DataFrame:
        parameters = args.get("parameters", {})
        node = args.get("node")
        topic = args.get("topic")
        field = args.get("field")
        identifier = args.get("identifier")
        result = args.get("result", "text")
        query = f"MATCH (n:{node})-[]-(a:{topic}) where n.{field}='{identifier}' RETURN a.{result} as result"
        with self.driver.session() as session:
            result = session.run(query, **parameters)
            records = [record.data() for record in result]
        return DataFrame(records)

    def push(
            self,
            data: Any,
            args: dict
    ) -> bool:
        parameters = args.get("parameters", {})
        node = args.get("node")
        query = f"CREATE (n:{node} {data}) RETURN n;"
        if not isinstance(data, dict):
            self.exception = "Error: Input data must be typed as dict."
            return False
        try:
            with self.driver.session() as session:
                session.run(query, **parameters)
            return True
        except Exception as e:
            self.exception = str(e)
            return False

    def update(
            self,
            field: str,
            old,
            new,
            args: dict,
            comparator: str = '=='
    ) -> bool:

        label = args.get("label")
        match_params = args.get("match_params", {})
        comp_map = {"==": "=", ">": ">", "<": "<="}  # ajustar según necesidades
        operator = comp_map.get(comparator, "=")

        cypher = (
            f"MATCH (n:{label} {{{field}: $old}}) "
            f"SET n.{field} = $new "
        )
        params = {**match_params, "old": old, "new": new}

        try:
            with self.driver.session() as session:
                session.run(cypher, **params)
            return True
        except Exception as e:
            self.exception = str(e)
            return False