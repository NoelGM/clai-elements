from typing import Any

from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langgraph.graph import END, StateGraph

from src.domain.model.agents.graph_status import EstadoGrafo
from src.domain.ports.agents.agent import Agent
from src.infrastructure.utils.promts.Prompts import obtener_prompt
from src.infrastructure.utils.utilClai import GraphUtility
from src.infrastructure.utils.utilneo4j import utilNeo4j

graph_util = GraphUtility()


class HistoryAgent(Agent):

    def __init__(
            self,
            protocol: str = 'https',  # NGM en la versión de la POC lo extrae de configuracion en la clase onesaitclient: self.protocol = Config.get_property('general.protocol')
            hostname: str = 'healthcare.cwbyminsait.com',  # NGM idem como protocol
    ):

        super().__init__('History Agent')

        self.protocol: str = protocol
        self.hostname: str = hostname

        ## ruta para acceder a la capeta data con las historias clinica en txt

        # base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))  # Sube 4 niveles
        self.carpeta_hc = '' # os.path.join(base_dir, "serve", "data", "fhir_txt_files")

        self.contexto = ""
        self.pregunta = ""
        self.patient_name = ""
        self.patient_id = ""
        self.historial_p_str = ""
        self.historial_r_str = ""

        # Construcción de los nodos del grafo de estado
        graph = StateGraph(EstadoGrafo)
        graph.add_node("decidir_descargar_ehr", self.decidir_descargar_ehr)
        graph.add_node("descargar_ehr", self.descargar_ehr)
        graph.add_node("consulta_grafo", self.consulta_grafo)
        graph.add_node("generar", self.generar)
        graph.add_node("consultar_HC_texto", self.consultar_HC_texto)
        graph.add_node("combinar_grafo_HC", self.combinar_grafo_HC)

        graph.set_conditional_entry_point(
            self.decidir_descargar_ehr,
            {
                "descargar_ehr": "descargar_ehr",
                "no_descargar_ehr": "combinar_grafo_HC"
            }
        )

        # graph.add_edge(START, "combinar_grafo_HC")
        graph.add_edge("descargar_ehr", "combinar_grafo_HC")
        graph.add_edge("combinar_grafo_HC", END)
        # graph.add_edge("consulta_grafo", "generar")
        # graph.add_edge("consultar_HC_texto", "generar")
        # graph.add_edge("generar", END)
        self.logger.info(f"__init__ graph.compile() ")
        self.graph = graph.compile()

    def execute(self, *args, **kwargs) -> Any:
        pass

    async def async_execute(self, *args, **kwargs) -> Any:
        pass

    def configure_chat(self, *args, **kwargs):
        pass

    def decidir_descargar_ehr(self, state: EstadoGrafo):
        """ Decidir si se debe descargar el EHR del paciente."""
        state["descargar_ehr"] = False # TODO NGM parametrizar: config_dict.get("DESCARGAR_EHR", False)  # Asignar True para indicar que se debe descargar el EHR
        if state["descargar_ehr"] == 'True':  # Si DESCARGAR_EHR es True
            self.logger.info("Decisión: Descargar EHR del paciente")
            return "descargar_ehr"
        else:
            self.logger.info("Decisión: No descargar EHR del paciente")
            return "no_descargar_ehr"

    async def descargar_ehr(self, state: EstadoGrafo) -> EstadoGrafo:
        """
        Descargar el EHR del paciente y guardarlo en un archivo de texto.

        Args:
            state (EstadoGrafo): Estado actual del grafo LangGraph

        Returns:
            state (EstadoGrafo): Estado actualizado con el contenido del EHR
        """

        state["patient_ehr"] = await utilNeo4j().execute(self.patient_id)

        return state

    def consulta_grafo(self, state: EstadoGrafo):
        """
        Realizar consulta basandose en Neo4JGraph.

        Args:
            state (dict): Estado actual del grafo LangGraph

        Returns:
            state (dict): Resultados de consulta añadidos al contexto
        """

        # NUEVO: Obtener la última pregunta del usuario del historial provisto por el frontend
        history_from_frontend = state.get("history", [])
        last_user_question_from_history = ""
        for turn in reversed(history_from_frontend):
            if turn["role"] == "user":
                last_user_question_from_history = turn["content"]
                break

        # consulta_grafo = last_user_question_from_history + state['question']
        consulta_grafo = state[
            'question']  # TODO VER COMO HACER PARA QUE NO SE DUPLIQUE LA PREGUNTA CON LA ANTERIOR DEL HISTORIAL
        self.logger.info(f'Paso: Realizando búsqueda grafo: "{consulta_grafo}"')

        use_rag_fusion = False # TODO NGM parametrizar: config_dict.get("USE_RAG_FUSION", False)  # Flag para aplicar rag_fusion o no
        use_reranking = False # TODO NGM parametrizar: config_dict.get("USE_RERANKING", False)  # Flag para aplicar reranking o no

        if use_rag_fusion == True:
            contexto = self.rag_fusion(consulta_grafo, self.patient_id, n_queries=2, k=5)
        else:
            contexto = graph_util.busqueda_grafo(consulta_grafo, self.patient_id, 2, k=15)
            if use_reranking == True:
                contexto = graph_util.rerank_with_crossencoder(consulta_grafo, contexto.items)
        '''
        logger.info(f"Respuesta recibida grafo: {contexto}")
        return {"context": contexto}
        '''
        # Extraer los contenidos relevantes del contexto del grafo
        context_items = self._extraer_contextos_grafo(contexto)

        self.logger.info(f"Respuesta recibida grafo: {context_items}")
        return {"context": context_items}

    def generar(self, state: EstadoGrafo) -> EstadoGrafo:
        """
        Generar respuesta

        Args:
            state (EstadoGrafo): Estado actual del grafo

        Returns:
            state (EstadoGrafo): Nueva clave añadida al estado, "generation", con la respuesta generada por el LLM
        """
        pregunta = state["question"]

        # <<-- INICIO DE CAMBIOS PARA USAR EL HISTORIAL DEL PAYLOAD -->>
        # history_from_frontend = state.get("history", [])

        # historial_p_str = ""
        # historial_r_str = ""

        historial = state["history"] if "history" in state else []

        for turn in historial:
            if turn["role"] == "user":
                self.historial_p_str += f"Humano: {turn['content']}\n"
            elif turn["role"] == "assistant":
                self.historial_r_str += f"Asistente: {turn['content']}\n"
        # <<-- FIN DE CAMBIOS PARA USAR EL HISTORIAL DEL PAYLOAD -->>

        self.logger.info(f"Paso: Generando respuesta final {'con' if 'context' in state else 'sin'} contexto")

        # Determinar contexto y prompt a utilizar
        contexto = state.get("context", "chat")
        prompt_name = "FHIR" if "context" in state else "general"
        generar_template = obtener_prompt(self.modelo_usado.model, prompt_name)
        cadena_generacion = generar_template | self.modelo_usado | StrOutputParser()
        self.logger.info(f"Historial recibido: {historial}")
        self.messages = historial

        # Esta función adapta el session_id a un estado y llama al método get_session_history
        def get_session_history_adapter(session_id: str) -> ChatMessageHistory:
            return self.get_session_history()

        runnable_with_history = RunnableWithMessageHistory(
            runnable=cadena_generacion,
            get_session_history=get_session_history_adapter,
            input_messages_key="input",
            history_messages_key="messages"
        )

        self.generacion = runnable_with_history.invoke(
            {"question": [HumanMessage(content=pregunta)],
             "context": contexto},
            config={"configurable": {"session_id": self.patient_id}})

        self.logger.info(f"Respuesta recibida generar: {self.generacion}")

        # Añadir respuesta al estado y devolverlo
        state["generation"] = self.generacion
        return state

