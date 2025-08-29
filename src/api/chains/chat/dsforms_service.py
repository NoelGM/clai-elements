import os
from typing import List, Any

from fastapi import HTTPException
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel

from src.infrastructure.utils.agents.agent_manager import AgentManager
from src.infrastructure.utils.chat.factory.chat_factory import FactoryChat
from src.logger.logger_config import logger


# from src.config import Config

#config_dict = Config.as_dict()


class OutputItem(BaseModel):
    type: str
    content: Any
    contentType: str
    originData: Any


class OutputPayload(BaseModel):
    status: str
    outputs: List[OutputItem]
    history: Any

#   TODO NGM: max_messages se estaba extrayendo de esta forma: int(os.getenv("MAX_HISTORY_MESSAGES", 10))
class DsformsService:
    """Servicio para invocar el agente clai con manejo de errores y logs."""

    def __init__(self, max_retries: int = 2, verbose: bool = True, max_messages: int = 10):
        self.logger = logger.bind(category="services")
        self.agent_manager = AgentManager(max_retries=max_retries, verbose=verbose)
        self.max_messages = max_messages
        self.chat = FactoryChat.get_chat_instance()

    """
    Servicio para interactuar con el agente clai, proporcionando manejo de errores y logs.
    Métodos
    -------
    onesait_healthcare_dsforms(inputs: dict, config: Dict[str, Any]) -> Dict[str, Any]
        Invoca el agente clai para procesar una pregunta relacionada con un paciente, utilizando el historial y un token de autenticación.
        Parámetros:
            inputs (dict): Diccionario que contiene la pregunta ('question'), información del paciente ('patient_name', 'patient_id') y el historial ('history').
            config (Dict[str, Any]): Diccionario de configuración que debe incluir los metadatos, especialmente el 'token' de autenticación.
        Retorna:
            Dict[str, Any]: Respuesta generada por el agente clai a través del método 'ask_dsforms'.
        Comentarios:
            - El método extrae la información relevante de los parámetros de entrada.
            - Utiliza un patrón de factoría para obtener una instancia de chat.
            - Llama al método 'ask_dsforms' del chat, pasando la pregunta, los datos del paciente, el historial y el token.
            - Es importante que el 'token' esté presente en los metadatos de la configuración.
    """

    # async def chatbot(self, inputs: dict, config: Dict[str, Any]):

        # token = config.get("metadata", {}).get("token", "")

    async def chatbot(self, inputs: dict, config):

        token = config.get("metadata", {}).get("token", "")

        question = inputs.get("question", "")
        # patient = {
        #     "patient_name": inputs.get("patient_name", ""),
        #     "patient_id": inputs.get("patient_id", "")
        # }
        patientId = inputs.get("patientId", "")
        resourceId = inputs.get("resourceId", "")
        resourceType = inputs.get("resourceType", "Questionnaire")
        history = inputs.get("history", [])
        # Ultimos X mensajes del historial
        # max_messages = int(os.getenv("MAX_HISTORY_MESSAGES", 10))   #   TODO NGM

        if history and len(history) > self.max_messages:
            history = history[-self.max_messages:]
        try:
            # Chatbot
            self.logger.info(f"Realizando pregunta para la question de longitud {len(question)} caracteres")
            chat_model = self.chat.load_model()
            self.logger.info(
                f"Instanciated OllamaChat with model={self.chat.model}, "
                f"temperature={self.chat.temperature}, context_size={self.chat.context_size}, "
                f"top_k={self.chat.top_k}, top_p={self.chat.top_p}, keep_alive={self.chat.keep_alive}, "
                f"base_url={self.chat.base_url}, verbose={self.chat.verbose}, device={self.chat.device}"
            )
            # Invocamos al agente historia clínica
            # se recupera la corutina del agente historia clínica
            async_dsfroms = self.agent_manager.get_agent("forms")  # NGM la pregunta va hasta aqui en primera instancia
            async_dsfroms.configureLLmChat(chat_model, patientId, token, resourceId, resourceType)
            ## transformar la pregunta para historia clínica
            pregunta_hc = async_dsfroms.transformar_pregunta_hc(question)

            ############################################################################################################

            ##agente combinador
            #  agente_combinador = self.agent_manager.get_agent("combinador")

            ##invocar agente historia_clinica con la pregunta transformada
            # historia_clinica_agent = self.agent_manager.get_agent("historia_clinica")
            # result_historia = await historia_clinica_agent.async_execute(chat_model, pregunta_hc, patientId, token,
            #                                                              history)
            # contexto_hc = result_historia.get("generacion", "")

            # Ejecutar el agente dsforms normalmente
            '''
            result_dsforms = await async_dsfroms.async_execute(
                chat_model, question, patientId, token, resourceId, resourceType, history
            )
            '''
            result_dsforms = await async_dsfroms.async_execute(
                chat_model, question, patientId, token, resourceId, resourceType, history, '' #contexto_hc
            )  # NGM aqui es la llamada al llm, se omite el context determina por la historia, por el momento

            # respuesta = result_dsforms["generacion"]
            respuesta_forms = result_dsforms["generacion"]
            # respuesta_hc = contexto_hc

            ### Llamamos al agente combinador para combinar las respuestas de dsforms y historia clínica
            # respuesta_final = await agente_combinador.combinar(
            #     chat_model, question, respuesta_forms, respuesta_hc, history)
            respuesta_final = respuesta_forms # NGM

            originData = result_dsforms["originData"]

            '''
            # Añade el contexto de historia clínica si existe
            if contexto_hc:
                respuesta_final = f"{respuesta}\n\n[Información relevante de historia clínica]:\n{contexto_hc}"
            else:
                respuesta_final = respuesta 

            # Ejecutamos la corutina y esperamos la respuesta
            respuesta_async_ds = []            
            result_dsforms = await async_dsfroms
            respuesta_async_ds.append(result_dsforms)            
            respuesta= respuesta_async_ds[0]["generacion"]
            originData= respuesta_async_ds[0]["originData"]

             # 4. Si el contexto de historia clínica es relevante, combinarlo en la respuesta final
            if contexto_hc and self.es_contexto_relevante(respuesta, contexto_hc):
                respuesta_final = f"{respuesta}\n\n[Información relevante de historia clínica]:\n{contexto_hc}"
            else:
                respuesta_final = respuesta
            '''

            # TODO - Ampliar condiciones para el tipo de respuesta img/html
            if isinstance(respuesta_final, str):
                typeData = "text"
                contentType = "text/plain"
            else:
                typeData = "json"
                contentType = "application/json"

            '''
            output_payload = {
                "status": "success",
                "outputs": [
                    {
                        "type": typeData,
                        "content": respuesta,
                        "contentType": contentType,
                        "originData": originData
                    }
                ],
                "history": history
            }
            return output_payload 
            '''
            output_payload = OutputPayload(
                status="success",
                outputs=[
                    OutputItem(
                        type=typeData,
                        content=respuesta_final,
                        contentType=contentType,
                        originData=originData
                    )
                ],
                history=history
            )
            return {
                "root": output_payload
            }

        except Exception as e:
            # self.logger.error("dsforms service fallido", e)
            self.logger.error(f"dsforms service fallido{e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error interno en DsformsService")


# instancia única y runnable asociado
clai_service_dsforms = DsformsService()
clai_service_dsforms_runnable_lambda = RunnableLambda(clai_service_dsforms.chatbot)