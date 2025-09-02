from fastapi import HTTPException
from langchain_core.runnables import RunnableLambda

from src.api.chains.chat.chat_service import ChatService
from src.api.model.chat.dsforms import OutputPayload, OutputItem
from src.infrastructure.adapters.agents.ds_forms_agent import DsFormsAgent
from src.infrastructure.utils.agents import FORMS


class _DsFormsService(ChatService):

    def __init__(self):
        super().__init__()

    async def chatbot(self, inputs: dict):

        token = 'Bearer ' + inputs.get("token", "")

        question = inputs.get("question", "")
        patient_id = inputs.get("patientId", "")
        resource_id = inputs.get("resourceId", "")
        resource_type = inputs.get("resourceType", "Questionnaire")
        history = inputs.get("history", [])

        if history and len(history) > self.max_messages:

            history = history[-self.max_messages:]

        try:

            #   Extract chatbot instance.

            self.logger.info(f"Making question with length {len(question)} characters.")

            chat_model = self.chat.load_model(self.chat_url, self.chat_model)

            #   Instantiate the corresponding agent and configure chat.

            dsforms_agent: DsFormsAgent = self.agent_factory.instance(FORMS)
            dsforms_agent.configure_chat(chat_model, patient_id, token, resource_id, resource_type)

            #   Call to the LLM for DS Forms, execute the question and capture its response.

            dsform_result = await dsforms_agent.async_execute(
                chat_model, question, patient_id, token, resource_id, resource_type, history, '' #contexto_hc
            )  # TODO NGM aqui es la llamada al llm, se omite el context determinado por la historia, por el momento

            dsforms_response = dsform_result["generacion"]

            origin_data = dsform_result["originData"]

            #   Create payload from the agent response.

            # TODO - Ampliar condiciones para el tipo de respuesta img/html
            if isinstance(dsforms_response, str):
                data_type = "text"
                content_type = "text/plain"
            else:
                data_type = "json"
                content_type = "application/json"

            output_payload = OutputPayload(
                status="success",
                outputs=[
                    OutputItem(
                        type=data_type,
                        content=dsforms_response,
                        contentType=content_type,
                        originData=origin_data
                    )
                ],
                history=history
            )

            #   Return the output.

            return {
                "root": output_payload
            }

        except Exception as e:

            self.logger.error(f"Fail in DSForms service: {e}.", exc_info=True)

            raise HTTPException(status_code=500, detail="Internal error in DsForms service")


#   Create the runnable lambda function.

_service = _DsFormsService()
runnable = RunnableLambda(_service.chatbot)