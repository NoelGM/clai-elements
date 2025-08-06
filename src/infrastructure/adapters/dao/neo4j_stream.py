from typing import Any, cast
from neo4j import GraphDatabase
from pandas import DataFrame
from typing_extensions import LiteralString

from src.domain.ports.dao.data_stream import DataStream


class Neo4jStream(DataStream):

    def __init__(
            self,
            uri: str,
            user: str,
            password: str,
            symbols: list = None
    ):
        super().__init__()
        self._symbols: list = symbols
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def pull(
            self,
            args: dict
    ) -> DataFrame:

        #   Extract method parameters.

        params = args.get("parameters", {})
        main_node = args.get("main_node")
        secondary_node = args.get("secondary_node", "")
        filter_field = args.get("filter_field", "")
        filter_value = args.get("filter_value", "")
        result_field = args.get("result", "text")

        #   Check whether all properties are enabled at the data model.

        if not self._check_symbols([main_node, secondary_node, filter_field, result_field]):
            return DataFrame()

        #   Create the query from parameters.

        query_text: str = f"MATCH (n:{main_node})-[]-(a:{secondary_node}) " if secondary_node else f"MATCH (n:{main_node}) "
        query_close: str = f"RETURN a.{result_field} AS {result_field}" if secondary_node else f"n.{result_field} AS {result_field}"

        if filter_field and filter_value:
            query_text += f"WHERE n.{filter_field} = $filter_value "

        query_text += query_close

        query: LiteralString = cast(LiteralString, query_text)

        #   Instance results data frame.

        results: DataFrame = DataFrame()

        #   Launch query and capture result.

        try:
            with self._driver.session() as session:
                res = session.run(query, filter_value=filter_value, **params) if filter_value else session.run(query, **params)
                records = [rec.data() for rec in res]
            results = DataFrame(records)
        except Exception as e:
            self.exception = f"Error while extracting data Neo4j: {e}"

        #   Return the results

        return results

    def push(
            self,
            data: Any,
            args: dict
    ) -> bool:

        #   Extract method parameters.

        parameters = args.get("parameters", {})
        node = args.get("node")

        #   Create query.

        if isinstance(data, dict):

            query = f"CREATE (:{node}:resource {{"

            for key in data.keys():
                query += f"{key}: '{str(data.get(key))}',"

            query = query[:-1]

            query += f"}})"

        else:

            query = f"CREATE (:{node}:resource {data})"

        #   Launch query.

        try:
            with self._driver.session() as session:
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
        comp_map = {"==": "=", ">": ">", "<": "<="}
        operator = comp_map.get(comparator, "=")
        cypher = (
            f"MATCH (n:{label} {{{field}: $old}}) "
            f"SET n.{field} = $new "
        )
        params = {**match_params, "old": old, "new": new}
        try:
            with self._driver.session() as session:
                session.run(cypher, **params)
            return True
        except Exception as e:
            self.exception = str(e)
            return False

    def _check_symbol(self, symbol) -> bool:
        if symbol not in self._symbols:
            self.exception = f"Property {str(symbol)} is not enabled in current data model."
            return False
        return True

    def _check_symbols(self, symbols: list) -> bool:
        if self._symbols is None:
            return True
        for symbol in symbols:
            if not self._check_symbol(symbol):
                return False
        return True
