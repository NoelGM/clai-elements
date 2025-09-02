import os
from typing import Any, Dict, List

import requests
import torch
from fastapi import HTTPException
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableSequence
from langchain_ollama import ChatOllama

from src.domain.ports.chat.interface_chat import InterfaceChat
from src.infrastructure.utils.agents.agent_factory import AgentFactory
from src.logger.logger_config import logger

logger = logger.bind(category="agents")
agent_manager = AgentFactory()

class OllamaChat(InterfaceChat):

    _model = None
    
    @classmethod
    def load_model(cls, url: str, model: str) -> str:

        try:

            cls.model = model
            cls.temperature = 0.5
            cls.context_size = 17000
            cls.top_k = 15
            cls.top_p = 0.75
            cls.keep_alive = 43200
            cls.base_url = url
            cls.verbose = True

            available_models = cls.get_models()

            if cls.model not in available_models:
                raise HTTPException(status_code=404, detail=f"Base model '{cls.model}' is not available in ollama.")

            #   FIXME NGM comprobar y ver si se puede eliminar
            cls.device = 'cuda' if torch.cuda.is_available() else 'cpu'

            logger.info(f"✅ Selected torch device: {cls.device}.")
            
            if cls._model is None:
                logger.info("🌀 Loading model for the first time...")
                cls._model = ChatOllama(
                    model=cls.model,
                    temperature=cls.temperature,
                    num_ctx=cls.context_size,
                    top_k=cls.top_k,
                    top_p=cls.top_p,
                    base_url=cls.base_url,
                    keep_alive=cls.keep_alive,
                    verbose=cls.verbose,
                    # device=cls.device # NGM argumento inesperado en el recurso
                )
                logger.info(
                    f"Loaded OllamaChat with model={cls.model}, "
                    f"temperature={cls.temperature}, context_size={cls.context_size}, "
                    f"top_k={cls.top_k}, top_p={cls.top_p}, keep_alive={cls.keep_alive}, "
                    f"base_url={cls.base_url}, verbose={cls.verbose}, device={cls.device}"
                )            
            return cls._model
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.exception(f"Error while executing CLAI: {str(e)}.")
            return f"Error: {str(e)}"
    
    @classmethod
    def get_models(cls) -> List[str]:
        """
        Obtiene una lista de modelos disponibles en Ollama.
        Esta función ejecuta el comando `ollama list` usando `subprocess.run` para obtener una lista de modelos
        disponibles en Ollama. La salida del comando se procesa para extraer los nombres de los modelos.
        Returns:
            list: Una lista de nombres de modelos disponibles en Ollama. Si ocurre un error, se devuelve una lista
            con un mensaje de error.
        """        
        try:
            response = requests.get(f"{cls.base_url}/api/tags")
            response.raise_for_status()  # Lanza una excepción si la respuesta es un error HTTP
            models = [model["name"] for model in response.json().get("models", [])]        
            return models
        except Exception as e:
            return [f"Error while getting models: {str(e)}."]

    def info_model(self) -> Dict[str, Any]:
        """
        Muestra información detallada del modelo seleccionado.
        Verifica si el modelo está disponible en la lista de modelos
        disponibles en Ollama. Si no está disponible, lanza una excepción HTTP 404.    
        """
        available_models = self.get_models()
        if self.model not in available_models:
            raise HTTPException(status_code=404, detail=f"Modelo '{self.model}' no encontrado en Ollama.")
        
        try:
            # Obtener información del modelo usando ollama.show
            url = f"{self.base_url}/api/show"
            response = requests.post(url, json={"model": self.model})
            response.raise_for_status()  # Lanza error si el servidor responde con un error HTTP
            return response.json()  # Devuelve la información del modelo en JSON        
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error obteniendo información del modelo: {str(e)}")

    def ask_model(self, question) -> Dict[str, Any]:
        """
        Realiza una pregunta al modelo de lenguaje de Ollama y devuelve la respuesta.
        se utiliza el modelo, temperatura, tamaño de contexto, top_k y top_p
        especificados en la configuración. Si el modelo no está disponible, lanza una excepción HTTP 404.
        Args:
            question (str): La pregunta que se desea hacer al modelo.
            Returns:"""

        try:
            available_models = self.get_models()
            if self.model not in available_models:
                raise HTTPException(status_code=404, detail=f"Modelo '{self.model}' no encontrado en Ollama.")

            chat_model = self.load_model()

            logger.info(
                f"Using OllamaChat with model={self.model}, "
                f"temperature={self.temperature}, context_size={self.context_size}, "
                f"top_k={self.top_k}, top_p={self.top_p}, keep_alive={self.keep_alive}, "
                f"base_url={self.base_url}, verbose={self.verbose}"
            )            

            chain = RunnableSequence(
                ChatPromptTemplate.from_template("{question}") | chat_model | StrOutputParser()
            )

            result = chain.invoke({"question": question})
            return {
                "question": question,
                "answer": result,
                "model": self.model,
                "temperature": self.temperature,
                "context_size": self.context_size,
                "top_k": self.top_k,
                "top_p": self.top_p
            }
        except Exception as e:
            logger.exception("Error al ejecutar clai")
            return {"error": str(e)}        

    def ask_clai(self, question, patient, history) -> Dict[str, Any]:
        try:
            if not question:
                raise HTTPException(status_code=400, detail=f"No se proporcionó question")

            available_models = self.get_models()
            if self.model not in available_models:
                raise HTTPException(status_code=404, detail=f"Modelo '{self.model}' no encontrado en Ollama.")
            
            logger.info(f"Realizando pregunta para la question de longitud {len(question)} caracteres")
            chat_model = self.load_model()
            logger.info(
                f"Instanciated OllamaChat with model={self.model}, "
                f"temperature={self.temperature}, context_size={self.context_size}, "
                f"top_k={self.top_k}, top_p={self.top_p}, keep_alive={self.keep_alive}, "
                f"base_url={self.base_url}, verbose={self.verbose}, device={self.device}"
            )            


            # Ultimos X mensajes del historial
            # MAX_HISTORY_MESSAGES se puede configurar en el archivo .env
            max_messages = os.getenv("MAX_HISTORY_MESSAGES", 10)
            if history and len(history) > max_messages:
                history = history[-max_messages:]

            clai = agent_manager.instance("clai")
            respuesta, originData = clai.execute(chat_model, question, patient, history)

            logger.info("Pregunta generada correctamente")

            # TODO - Ampliar condiciones para el tipo de respuesta img/html 
            if isinstance(respuesta, str):
                typeData = "text"
                contentType = "text/plain"
            else:
                typeData = "json"
                contentType = "application/json"

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
        except Exception as e:
            logger.exception("Error al ejecutar clai")
            return {"error": str(e)}
    
    ###### Función igual pero que devuelve los contextos para la evaluación en ragas
    def ask_clai_eval(self, question, patient) -> Dict[str, Any]:
        try:
            if not question:
                raise HTTPException(status_code=400, detail=f"No se proporcionó question")

            available_models = self.get_models()
            if self.model not in available_models:
                raise HTTPException(status_code=404, detail=f"Modelo '{self.model}' no encontrado en Ollama.")
            
            logger.info(f"Realizando pregunta para la question de longitud {len(question)} caracteres")
            chat_model = self.load_model()
            logger.info(
                f"Instanciated OllamaChat with model={self.model}, "
                f"temperature={self.temperature}, context_size={self.context_size}, "
                f"top_k={self.top_k}, top_p={self.top_p}, keep_alive={self.keep_alive}, "
                f"base_url={self.base_url}, verbose={self.verbose}, device=cuda"
            )            

            #clai = agent_manager.get_agent("clai")
            #respuesta, originData = clai.execute(chat_model, question, patient)
            clai = agent_manager.instance("clai_eval")
            respuesta, originData, context_used = clai.execute_eval(chat_model, question, patient)


            logger.info("Pregunta generada correctamente")

            return {
                "question": question,
                "respuesta": respuesta,
                "model": self.model,
                "temperature": self.temperature,
                "context_size": self.context_size,
                "top_k": self.top_k,
                "top_p": self.top_p,
                "originData": originData,
                "context_used": context_used
            }
        except Exception as e:
            logger.exception("Error al ejecutar clai")
            return {"error": str(e)}
