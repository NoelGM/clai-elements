import os
from langchain_neo4j import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from neo4j import GraphDatabase
from neo4j_graphrag.retrievers import HybridCypherRetriever, HybridRetriever
from langchain.chains import RetrievalQA
from neo4j_graphrag.retrievers import Text2CypherRetriever
from neo4j_graphrag.generation import GraphRAG

from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_cohere import CohereRerank

from src.logger.logger_config import logger

import json
import re

from sentence_transformers import CrossEncoder
import torch

logger = logger.bind(category="agents")

#   TODO NGM parametriza y arregla
config_dict = {
    "EMBEDDER_MODEL": 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
}

class GraphUtility:
    device = None
    embedder = None
    cross_encoder = None

    def __new__(cls, *args, **kwargs):
        if cls.device is None:
            requested_device = 'cuda' if os.environ.get('CUDA_VISIBLE_DEVICES') else 'cpu'
            if requested_device.startswith('cuda') and torch.cuda.is_available():
                cls.device = requested_device
            else:
                cls.device = 'cpu'
            logger.info(f"✅ Dispositivo torch seleccionado: {cls.device} (cuda solicitado: {requested_device.startswith('cuda')})")


        return super().__new__(cls)

    def __init__(self):

        #   TODO NGM parametriza y arregla
        self.NEO4J_URI = 'bolt://10.86.11.43:7687'
        self.USERNAME = 'neo4j'
        self.PASSWORD = '12345678a'
        self.VECTOR_INDEX_NAME = "fhir_text_large"
        self.FULLTEXT_INDEX_NAME = "node_text_index"

        self.graph  = Neo4jGraph(
            self.NEO4J_URI,
            self.USERNAME,
            self.PASSWORD,
            refresh_schema=True
        )

        self.retrieval_query = """
            WITH node, score
            MATCH (patient:Patient)-[]->(node)
            WHERE patient.id = $patient_id
            //AND (
            //    (node.resource_type IN ['DocumentReference', 'MedicationRequest', 'Condition', 'Observation', 'Encounter']
            //    AND node.subject_reference = 'Patient/' + patient.id)
            //    OR (node.resource_type IN ['Immunization', 'AllergyIntolerance'] AND node.patient_reference = 'Patient/' + patient.id)
            //)
            OPTIONAL MATCH (node)-[]-(relatedNode)
            WHERE NOT relatedNode:Patient AND relatedNode.text IS NOT NULL
            OPTIONAL MATCH (relatedNode)-[]-(secondaryNode)
            WHERE NOT secondaryNode:Patient AND secondaryNode <> node AND secondaryNode.text IS NOT NULL

        WITH node, 
        relatedNode, 
        secondaryNode, 
        patient, 
        score 
        WHERE score >= 0.9

        RETURN 
            node.text AS texto, 
            COLLECT(DISTINCT relatedNode.text) AS contexto,
            COLLECT(DISTINCT secondaryNode.text) AS contextoAdicional
            // score
            // patient.name AS paciente
        """

    @classmethod
    def load_embeddings(cls) -> None:
        try:
            if cls.embedder is None:
                logger.info("🌀 Cargando embeddings por primera vez...")
                #   TODO NGM parametriza y arregla
                cls.embedder = HuggingFaceEmbeddings(model_name=config_dict.get("EMBEDDER_MODEL"), 
                                            model_kwargs={'device': cls.device})
        except Exception as e:
            #   TODO NGM parametriza y arregla
            logger.exception(f"Error cargando embeddings: {config_dict.get('EMBEDDER_MODEL')}")
            return {"error": str(e)}
        logger.info("✅ Embeddings cargados correctamente.")
        
    @classmethod
    def get_cross_encoder(cls):
        try:
            if cls.cross_encoder is None:
                logger.info("🌀 Cargando CrossEncoder por primera vez...")
                cls.cross_encoder = CrossEncoder('Alibaba-NLP/gte-multilingual-reranker-base', trust_remote_code=True, 
                             device=cls.device)
        except Exception as e:
            logger.exception("Error cargando CrossEncoder: Alibaba-NLP/gte-multilingual-reranker-base")
            return {"error": str(e)}
        logger.info("✅ CrossEncoder cargado correctamente.")
        
    def get_driver(self):
      driver = GraphDatabase.driver(
            self.NEO4J_URI,
            auth=(self.USERNAME, self.PASSWORD)
        )
      return driver


    def get_graph(self):
        return self.graph

    def get_hybrid_cypher_retriever(self):
        
        self.load_embeddings()
        retriever = HybridCypherRetriever(
            driver=self.get_driver(),
            vector_index_name= self.VECTOR_INDEX_NAME,
            fulltext_index_name= self.FULLTEXT_INDEX_NAME,
            embedder=self.embedder,
            retrieval_query=self.retrieval_query,
        )
        logger.debug("HybridCypherRetriever initialized with retrieval query: %s", retriever.embedder)
        return retriever
    
    def get_hybrid_retriever(self):

        self.load_embeddings()
        retriever = HybridRetriever(
            driver=self.get_driver(),
            vector_index_name=self.VECTOR_INDEX_NAME,
            fulltext_index_name=self.FULLTEXT_INDEX_NAME,
            embedder=self.embedder,
            return_properties=["text"],
        )

        return retriever

    def get_vector_store_retriever(self):
        vector_store = Neo4jVector.from_existing_index(
            self.embedder,
            url=self.NEO4J_URI,
            username=self.USERNAME,
            password=self.PASSWORD,
            index_name=self.VECTOR_INDEX_NAME
        )

        return vector_store

    def get_text2cypher_retriever(self):

        neo4j_schema = self.get_graph().schema
        driver = self.get_driver()

        with open(r'C:\Users\moteroa\Escritorio\Work\ia\sources\clai\serve\src\utils\examples.json', "r", encoding="utf-8") as file:
                examples_data = json.load(file)

        examples = [f"USER_INPUT: '{ex['USER_INPUT']}' QUERY: {ex['QUERY']}" for ex in examples_data]
        
        llm = ChatOllama(model='llama3')

        retriever = Text2CypherRetriever(
            driver=driver,
            llm=llm,
            neo4j_schema=neo4j_schema,
            examples = examples
        )

        llm = ChatOllama(model='llama3', temperature=0,  num_predict=-1)
        rag = GraphRAG(retriever=retriever, llm=llm)

        return rag
    
    def extract_fields_from_record(self, record_str):
        
        def extract_field(field_name):
            match = re.search(fr"{field_name}='(.*?)'", record_str)
            return match.group(1).strip() if match else ""

        return {
            'texto': extract_field('texto'),
            'contexto': extract_field('contexto'),
            'contextoAdicional': extract_field('contextoAdicional'),
            # 'paciente': extract_field('paciente')
        }

    def rerank_with_crossencoder(self, question, items):
        pairs = []
        valid_items = []

        for item in items:
            try:
                content_str = item.content  
                extracted_text = self.extract_fields_from_record(content_str)

                if extracted_text:
                    combined_text = " ".join([
                        extracted_text['texto'],
                        extracted_text['contexto'],
                        extracted_text['contextoAdicional']
                    ]).strip()

                    pairs.append((question, combined_text))
                    valid_items.append(item)

            except Exception as e:
                print(f"Skipping item due to error: {e}")
                continue

        if not pairs:
            print("No valid pairs to rerank.")
            return []
        
        
        self.get_cross_encoder()

        scores = self.cross_encoder.predict(pairs)
        reranked = sorted(zip(valid_items, scores), key=lambda x: x[1], reverse=True)
        return [item for item, _ in reranked]
    

    def busqueda_grafo(self, question, patient_id, type, k):
        if type == 0:
            retriever_result = self.get_vector_store_retriever().as_retriever(search_kwargs={"patient_id": patient_id}).search(question)

        if type == 1:
            retriever_result = self.get_hybrid_retriever().search(question, top_k=k)
        
        if type == 2:
            retriever_result = self.get_hybrid_cypher_retriever().search(question, top_k=k, query_params={'patient_id' : patient_id})
            return retriever_result

        if type == 3:
            retriever_result = self.get_text2cypher_retriever().search(question).answer
            print(retriever_result)

        return retriever_result
