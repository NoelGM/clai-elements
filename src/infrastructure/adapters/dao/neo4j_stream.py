import re
from typing import Any, cast
from neo4j import GraphDatabase
from pandas import DataFrame
from typing_extensions import LiteralString
from langchain_community.vectorstores import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings

from src.domain.ports.dao.data_stream import DataStream
from src.config.config import config


class Neo4jStream(DataStream):

    def __init__(
            self,
            uri: str,
            user: str,
            password: str,
            symbols: list = None,
            unique_node: str = None,
            resource: str = None
    ):
        super().__init__()
        self._symbols: list = symbols
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._unique_node: str = unique_node
        self._resource: str = resource

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
        
        # Delete existing nodes and relationships of the specified patient.
        #TODO: Ver como se pasa el patientId desde el endpoint
        if self._unique_node is not None:
            if self._unique_node in args:
                if not self._delete(args[self._unique_node]):
                    return False

        # Initialize constraints in Neo4j.
        if not self._initialize_neo4j_vector(self._driver.session()):
            return False

        #   Extract method parameters.

        parameters = args.get("parameters", {})
        node = args.get("node")

        #   Create query for nodes.

        for resource_type, content in zip(node, data["resource_data"]):

            query = f"CREATE (:{resource_type}:resource {content})"

            try:
                with self._driver.session() as session:
                    session.run(query, **parameters)
            except Exception as e:
                self.exception = str(e)
                return False
            
        #   Create query for dates.
       
        if 'node_dates' in data:

            date_pattern = re.compile(r'([0-9]+)/([0-9]+)/([0-9]+)')

            for date in data['node_dates']:

                date_parts = date_pattern.findall(date)[0]
                cypher_date = f'{date_parts[2]}-{date_parts[0]}-{date_parts[1]}'
                query = 'CREATE (:Date {name:"' + date + '", id: "' + date + '", date: date("' + cypher_date + '")})'
                
                try:
                    with self._driver.session() as session:
                        session.run(query, **parameters)
                except Exception as e:
                    self.exception = str(e)
                    return False
                
        #   Create query for edges.
                
        if 'node_edges' in data:

            for edge in data['node_edges']:

                query = edge

                try:
                    with self._driver.session() as session:
                        session.run(query, **parameters)
                except Exception as e:
                    self.exception = str(e)
                    return False
                
        #   Create vector index.
        if not self._create_vector_index():
            return False

        # If everything okay return True
        return True

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
    

    #TODO: ESTAS FUNCIONES SON NUEVAS Y NO SÉ SI AQUÍ ESTÁN BIEN DEFINIDAS
    def _create_vector_index(self) -> bool:

        try:
            Neo4jVector.from_existing_graph(
            HuggingFaceEmbeddings(model_name=config.database.neo4j.embedder_model),
            url=config.database.neo4j.uri,
            username=config.database.neo4j.user,
            password=config.database.neo4j.password,
            index_name=config.database.neo4j.index_name,
            node_label="resource",
            text_node_properties=['text'],
            embedding_node_property='embedding_text',
            )
            return True
        except Exception as e:
            self.exception = f"Error creando el índice vectorial: {str(e)}"
            return False
        
    def _initialize_neo4j_vector(self, tx) -> bool:
        try:
            queries = [
                "CREATE CONSTRAINT pid IF NOT EXISTS FOR (p:Patient) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT prid IF NOT EXISTS FOR (p:Practitioner) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT orgid IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE",
                "CREATE CONSTRAINT encid IF NOT EXISTS FOR (e:Encounter) REQUIRE e.id IS UNIQUE",
                "CREATE CONSTRAINT cond IF NOT EXISTS FOR (c:Condition) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT obs IF NOT EXISTS FOR (o:Observation) REQUIRE o.id IS UNIQUE",
                "CREATE CONSTRAINT mr IF NOT EXISTS FOR (m:MedicationRequest) REQUIRE m.id IS UNIQUE",
                "CREATE CONSTRAINT pr IF NOT EXISTS FOR (pr:Procedure) REQUIRE pr.id IS UNIQUE",
                "CREATE CONSTRAINT ai IF NOT EXISTS FOR (a:AllergyIntolerance) REQUIRE a.id IS UNIQUE",
                "CREATE FULLTEXT INDEX node_text_index IF NOT EXISTS FOR (n:resource) ON EACH [n.text]"
            ]
            for q in queries:
                tx.run(q)
            return True
        except Exception as e:
            self.exception = f"Error initializing Neo4j constraints: {str(e)}"
            return False
        
    def _delete(self, unique_node_id: str) -> bool:

        query = f"MATCH (r:{self._resource}) WHERE r.id = $unique_node_id CALL apoc.path.subgraphAll(r, {{}}) YIELD nodes UNWIND nodes AS node DETACH DELETE node"

        try:
            with self._driver.session() as session:
                session.run(query, {"unique_node_id": unique_node_id})

        except Exception as e:
            self.exception = f"Error deleting {self._resource} {unique_node_id}: {str(e)}"
            return False

        self._driver.close()

        return True
