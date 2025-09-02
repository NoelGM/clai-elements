# utils/utilNeo4j.py

import re

from src.infrastructure.adapters.http.ehr_client import EhrClient
from src.infrastructure.utils.fhir.FHIR_to_graph import resource_to_node, resource_to_edges
from src.logger.logger_config import logger
# from src.config import Config

from langchain_community.vectorstores import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_neo4j import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_community.embeddings import HuggingFaceEmbeddings

from neo4j import GraphDatabase

logger = logger.bind(category="agents")
# config_dict = Config.as_dict()


class utilNeo4j:

    def __init__(self):

        #   TODO paramterizar valroes de conexión a Neo4j
        self.NEO4J_URI = 'bolt://10.86.11.43:7687'
        self.USERNAME = 'neo4j'
        self.PASSWORD = '12345678a'
        self.VECTOR_INDEX_NAME = 'fhir_text_large'

        self.driver = GraphDatabase.driver(self.NEO4J_URI, auth=(self.USERNAME, self.PASSWORD))
        self.graph = Neo4jGraph(
            self.NEO4J_URI,
            self.USERNAME,
            self.PASSWORD,
            refresh_schema=True
        )

    def initialize_neo4j(self, tx):
        queries = [
            "CREATE CONSTRAINT pid IF NOT EXISTS FOR (p:Patient) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT prid IF NOT EXISTS FOR (p:Practitioner) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT orgid IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE",
            "CREATE CONSTRAINT encid IF NOT EXISTS FOR (e:Encounter) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT cond IF NOT EXISTS FOR (c:Condition) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT obs IF NOT EXISTS FOR (o:Observation) REQUIRE o.id IS UNIQUE",
            "CREATE CONSTRAINT mr IF NOT EXISTS FOR (m:MedicationRequest) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT pr IF NOT EXISTS FOR (pr:Procedure) REQUIRE pr.id IS UNIQUE",
            "CREATE FULLTEXT INDEX node_text_index IF NOT EXISTS FOR (n:resource) ON EACH [n.text]"
        ]
        for q in queries:
            tx.run(q)

    def delete(self, patientId):

        query = """
        MATCH (p:Patient)
        WHERE p.id = $patientId
        CALL apoc.path.subgraphAll(p, {}) YIELD nodes
        UNWIND nodes AS node
        DETACH DELETE node;
        """

        with self.driver.session() as session:
            session.run(query, {"patientId": patientId})

        self.driver.close()

        logger.info(f"Paciente {patientId} eliminado con éxito")

        return f"Paciente {patientId} eliminado con éxito"

    async def execute(self, patientId, token=None):

        if not patientId:
            logger.warning("No se proporcionó patientId")
            return {"error": "No se proporcionó patientId"}

        self.delete(patientId)

        #   TODO NGM propagar protocol y hostname
        ehr_client = EhrClient(token)

        try:
            path = "/ehrserver/fhir"
            response = await ehr_client.post(path=path, patient_id=patientId)
        except Exception as e:
            # Cualquier otro fallo
            logger.error(f"Error inesperado: {e}")
            response = None

        with self.driver.session() as session:
            session.execute_write(self.initialize_neo4j)

        nodes = []
        edges = []
        dates = set()  # set is used here to make sure dates are unique
        graph = self.graph

        def convert_sets(obj):  # Helper to convert sets (if any) to lists so langserve.orjson.dumps() can handle them
            """Recursively convert sets to lists in a nested JSON structure"""
            if isinstance(obj, dict):
                return {k: convert_sets(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_sets(v) for v in obj]
            elif isinstance(obj, set):  # Convert sets to lists
                return list(obj)
            else:
                return obj

        json = convert_sets(response)

        for entry in json['entry']:
            resource_type = entry['resource']['resourceType']
            if resource_type != 'Provenance' and resource_type != 'Bundle':
                # generated the cypher for creating the resource node
                nodes.append(resource_to_node(entry['resource']))
                # generated the cypher for creating the reference & date edges and capture dates
                node_edges, node_dates = resource_to_edges(entry['resource'])
                edges += node_edges
                dates.update(node_dates)

        for i in range(1, len(json["entry"])):
            for bundle_entry in json["entry"][i].get("resource", {}).get("entry", []):
                # print('Bundle_Entry:', bundle_entry['resource']['resourceType'])
                # generated the cypher for creating the resource node
                nodes.append(resource_to_node(bundle_entry['resource']))
                # generated the cypher for creating the reference & date edges and capture dates
                node_edges, node_dates = resource_to_edges(bundle_entry['resource'])
                edges += node_edges
                dates.update(node_dates)

        # create the nodes for resources
        for node in nodes:
            graph.query(node)

        date_pattern = re.compile(r'([0-9]+)/([0-9]+)/([0-9]+)')

        # create the nodes for dates
        for date in dates:
            date_parts = date_pattern.findall(date)[0]
            cypher_date = f'{date_parts[2]}-{date_parts[0]}-{date_parts[1]}'
            cypher = 'CREATE (:Date {name:"' + date + '", id: "' + date + '", date: date("' + cypher_date + '")})'
            graph.query(cypher)

        # create the edges
        for edge in edges:
            try:
                graph.query(edge)
            except:
                print(f'Failed to create edge: {edge}')

        #   TODO NGM parametrizar
        Neo4jVector.from_existing_graph(
            HuggingFaceEmbeddings(model_name='intfloat/multilingual-e5-large-instruct'), # HuggingFaceEmbeddings(model_name=config_dict.get("EMBEDDER_MODEL")),
            url=self.NEO4J_URI,
            username=self.USERNAME,
            password=self.PASSWORD,
            index_name=self.VECTOR_INDEX_NAME,
            node_label="resource",
            text_node_properties=['text'],
            embedding_node_property='embedding_text',
        )

        # TODO: Modificar el metodo de procesar la hc para que se añadan los nuevos campos
        # util_hc = utilHCtexto()
        # await util_hc.execute(json=response)

        return response
