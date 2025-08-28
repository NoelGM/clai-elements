from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langgraph.graph import END, StateGraph

from src.domain.model.agents.graph_status import EstadoGrafo
from src.infrastructure.adapters.agents.llama_agent import LlamaAgent
from src.infrastructure.utils.http.clients.dsforms_client import DsformsClient
from src.infrastructure.utils.promts.RouterPrompts import router_obtener_prompt

#   TODO NGM extraer estos valores de la configuración. Organizar tambien la propagación de verify y timeout para los clientes
protocol = ''
hostname = ''


class DsformsAgent(LlamaAgent):

    def __init__(self):

        super().__init__('DS From Agent')

        self.historial = []
        self.contexto = ""
        self.pregunta = ""
        self.patient_name = ""
        self.patient_id = ""
        # Construcción de los nodos del grafo de estado
        graph = StateGraph(EstadoGrafo)
        graph.set_entry_point("consulta_forms")
        graph.add_node("consulta_forms", self.consulta_forms)
        graph.add_node("procesar", self.extraer_preguntas_y_opciones)
        graph.add_edge("consulta_forms", "procesar")
        graph.add_node("generar", self.generar)
        graph.add_edge("procesar", "generar")
        graph.add_edge("generar", END)
        self.logger.info(f"__init__ graph.compile() ")
        self.graph = graph.compile()

    def build_history_from_frontend(self, messages: list[BaseMessage]) -> ChatMessageHistory:
        history = ChatMessageHistory()
        for msg in messages:
            history.add_message(msg)
        return history

    def get_session_history(self) -> ChatMessageHistory:
        return self.build_history_from_frontend(self.messages)

    #   TODO NGM 1) De donde procede la variable state?; 2) Esta función tambien se crea anidada más abajo; 3) No tiene valor de retorno
    # def get_session_history_adapter(self) -> ChatMessageHistory:
    #     state = state.get("history", [])

    async def consulta_forms(self, state: EstadoGrafo):
        # Instancia de DsformsClient
        dsforms_client = DsformsClient(protocol, hostname, self.token)
        try:
            path = f"/dsforms/fhir/rest/Questionnaire/{self.resourceId}?_format=json"
            response = await dsforms_client.get(path=path)
        except Exception as e:
            # Cualquier otro fallo
            self.logger.error(f"Error inesperado: {e}")
            response = None

        state["questionnaire"] = response

        return state

    ############################################################################################
    def transformar_pregunta_hc(self, question):
        """
        Reformula la pregunta para consultar la historia clínica.
        """
        # Usamos un prompt específico para transformar la pregunta
        transformar_template = router_obtener_prompt(self.modelo_usado.model, "transformar_hc")
        router_pregunta = transformar_template | self.modelo_usado_json | JsonOutputParser()
        pregunta_transformada = router_pregunta.invoke({"question": question})["hc"]
        return pregunta_transformada

    ############################################################################################
    def extraer_preguntas_y_opciones(self, state: EstadoGrafo):
        preguntas = {}
        items = state["questionnaire"]
        # Control de None o estructura inesperada
        if not items or not isinstance(items, dict) or "item" not in items or not isinstance(items["item"], list):
            self.generacion = preguntas
            self.originData = "dsforms"
            return state
        for item in items["item"]:
            texto = item.get("text")
            opciones = []

            # Extraer opciones si las hay
            for option in item.get("option", []):
                value_coding = option.get("valueCoding", {})
                display = value_coding.get("display")
                if display:
                    opciones.append(display)
            # Verificar si hay texto en la extensión para "valorPorDefecto"
            valor_por_defecto = None
            for extension in item.get("extension", []):
                if extension.get("url") == "http://hn.indra.es/dsforms/fhir/QuestionnaireItem/properties":
                    coding = extension.get("valueCodeableConcept", {}).get("coding", [])
                    for code in coding:
                        if code.get("code") == "valorPorDefecto":
                            valor_por_defecto = code.get("display")
                            break
            if texto:
                if texto not in preguntas:
                    preguntas[texto] = opciones if opciones else [
                        valor_por_defecto or "Texto informativo sin opciones"]

            subitems = item.get("item", [])
            i = 0
            while i < len(subitems):
                subitem = subitems[i]
                tipo = subitem.get("type")
                pregunta = subitem.get("text")

                # Caso 1: subitem tipo display (texto informativo)
                if tipo == "display" and pregunta:
                    # Ver si el siguiente subitem tiene opciones
                    if i + 1 < len(subitems):
                        siguiente = subitems[i + 1]
                        opciones_siguientes = []
                        for option in siguiente.get("option", []):
                            value_coding = option.get("valueCoding", {})
                            display = value_coding.get("display")
                            if display:
                                opciones_siguientes.append(display)
                        if pregunta not in preguntas:
                            preguntas[pregunta] = opciones_siguientes if opciones_siguientes else [
                                "Texto informativo sin opciones"]
                        i += 2
                        continue

                # Caso 2: subitem con texto y opciones propias
                opciones_directas = []
                for option in subitem.get("option", []):
                    value_coding = option.get("valueCoding", {})
                    display = value_coding.get("display")
                    if display:
                        opciones_directas.append(display)

                if pregunta:
                    if pregunta not in preguntas:
                        preguntas[pregunta] = opciones_directas if opciones_directas else [
                            "Texto informativo sin opciones"]
                elif opciones_directas:
                    # Opciones sin pregunta (caso raro)
                    preguntas["Pregunta sin texto"] = opciones_directas

                # Recursión si hay subitems anidados
                if subitem.get("item"):
                    sub_preguntas = self.extraer_preguntas_y_opciones([subitem])
                    for key, value in sub_preguntas.items():
                        if key not in preguntas:
                            preguntas[key] = value

                i += 1
        titulo = items.get("title", "Sin título")
        print("Título del formulario:", titulo)
        self.generacion = preguntas
        print("Preguntas y opciones extraídas:", preguntas)
        self.originData = "dsforms"
        self.contexto = preguntas
        state["context"] = str(preguntas)  # Usamos string como contexto

        return state

    # necesario??
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

        historial_p_str = ""
        historial_r_str = ""

        historial = state["history"] if "history" in state else []

        for turn in historial:
            if turn["role"] == "user":
                historial_p_str += f"Humano: {turn['content']}\n"
            elif turn["role"] == "assistant":
                historial_r_str += f"Asistente: {turn['content']}\n"
        # <<-- FIN DE CAMBIOS PARA USAR EL HISTORIAL DEL PAYLOAD -->>

        self.logger.info(f"Paso: Generando respuesta final {'con' if 'context' in state else 'sin'} contexto")

        # Determinar contexto y prompt a utilizar
        contexto = state.get("context", "chat")
        contexto_hc = state.get("contexto_hc", "")  #### añadido para contexto historia clínica
        prompt_name = "forms" if "context" in state else "forms"

        '''
        generar_template = obtener_prompt(self.modelo_usado.model, prompt_name)
        cadena_generacion = generar_template | self.modelo_usado | StrOutputParser()
        '''

        generar_template = router_obtener_prompt(self.modelo_usado.model, "forms")
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
            {
                "input": pregunta,
                "question": pregunta,
                "context": contexto,
                "historial_p": historial_p_str,
                "historial_r": historial_r_str,
                "contexto_hc": contexto_hc  #### añadido para contexto historia clínica
            },
            config={"configurable": {"session_id": self.patient_id}})

        self.logger.info(f"Respuesta recibida generar: {self.generacion}")

        # Añadir respuesta al estado y devolverlo
        state["generation"] = self.generacion
        return state

    def configureLLmChat(self, chat, patientId, token, resourceId, resourceType):
        self.modelo_usado = chat
        self.logger.info(f"chat model: {self.modelo_usado}")
        self.modelo_usado_json = chat
        self.logger.info(f"chat model json: {self.modelo_usado_json}")
        # self.historial = []
        self.contexto = ""
        self.pregunta = ""
        # self.history=history
        # self.patient_name=patient["patient_name"]
        self.patientId = patientId
        self.resourceId = resourceId
        self.resourceType = resourceType
        self.token = token

    def execute(self, chat, question, patient, token, resourceId, resourceType, history=None):
        final_state = self.graph.invoke({
            "question": question,
            "token": token,
            "form_id": resourceId,
            "history": history or []
        })
        context_used = final_state.get("context", None)
        return self.generacion, self.originData, context_used

    '''
    async def async_execute(self, chat, question, patientId, token, resourceId, resourceType, history=None):
        self.configureLLmChat(chat, patientId, token, resourceId, resourceType)
        final_state = await self.graph.ainvoke({
            "question": question,
            "token": token,
            "form_id": resourceId,
            "history": history or []
        })
        context_used = final_state.get("context", None)
        return {
            "generacion": self.generacion,
            "originData": self.originData,
            "contextUsed": context_used
        }
        '''

    async def async_execute(self, chat, question, patientId, token, resourceId, resourceType, history=None,
                            contexto_hc=""):
        self.configureLLmChat(chat, patientId, token, resourceId, resourceType)
        final_state = await self.graph.ainvoke({
            "question": question,
            "token": token,
            "form_id": resourceId,
            "history": history or [],
            "contexto_hc": contexto_hc or ""
        })
        context_used = final_state.get("context", None)
        return {
            "generacion": self.generacion,
            "originData": self.originData,
            "contextUsed": context_used
            }