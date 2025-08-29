import os
from typing import Any, Dict, List

import requests
import torch
from dotenv import load_dotenv
from fastapi import HTTPException
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableSequence
from langchain_ollama import ChatOllama

from src.infrastructure.utils.agents.agent_manager import AgentManager
from src.infrastructure.utils.chat.factory.interface_chat import InterfaceChat
from src.logger.logger_config import logger

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
logger = logger.bind(category="agents")
agent_manager = AgentManager(max_retries=2, verbose=True)

class OllamaChat(InterfaceChat):

    _model = None

    def __init__(self):
        '''
        self.model = os.getenv("DEFAULT_OLLAMA_MODEL")
        self.temperature = os.getenv("DEFAULT_OLLAMA_MODEL_TEMPERATURE")
        self.context_size = os.getenv("DEFAULT_OLLAMA_MODEL_CONTEXT_SIZE")
        self.top_k = os.getenv("DEFAULT_OLLAMA_MODEL_TOP_K")
        self.top_p = os.getenv("DEFAULT_OLLAMA_MODEL_TOP_P")
        self.keep_alive = int(os.getenv("DEFAULT_OLLAMA_MODEL_KEEP_ALIVE", 0))
        self.base_url = os.getenv("OLLAMA_BASE_URL")
        self.verbose = os.getenv("DEFAULT_OLLAMA_MODEL_VERBOSE")
        logger.info(
            f"Initialized OllamaChat with model={self.model}, "
            f"temperature={self.temperature}, context_size={self.context_size}, "
            f"top_k={self.top_k}, top_p={self.top_p}, keep_alive={self.keep_alive}, "
            f"base_url={self.base_url}, verbose={self.verbose}"
        )
        '''
    
    @classmethod
    def load_model(cls) -> None:
        try:
            #   TODO NGM cambiar datos procecendentes de env

            # DEFAULT_OLLAMA_MODEL_KEEP_ALIVE = 43200
            # DEFAULT_OLLAMA_MODEL_TEMPERATURE = 0.5
            # DEFAULT_OLLAMA_MODEL_TOP_P = 0.75
            # DEFAULT_OLLAMA_MODEL_TOP_K = 15
            # DEFAULT_OLLAMA_MODEL_CONTEXT_SIZE = 17000
            # DEFAULT_OLLAMA_MODEL_VERBOSE = True

            cls.model = "cogito:latest" # os.getenv("DEFAULT_OLLAMA_MODEL")
            cls.temperature = 0.5 # os.getenv("DEFAULT_OLLAMA_MODEL_TEMPERATURE")
            cls.context_size = 17000 # os.getenv("DEFAULT_OLLAMA_MODEL_CONTEXT_SIZE")
            cls.top_k = 15 # os.getenv("DEFAULT_OLLAMA_MODEL_TOP_K")
            cls.top_p = 0.75 # os.getenv("DEFAULT_OLLAMA_MODEL_TOP_P")
            cls.keep_alive = 43200 # int(os.getenv("DEFAULT_OLLAMA_MODEL_KEEP_ALIVE", 0))
            cls.base_url = 'http://localhost:11434' # 0.5 # os.getenv("OLLAMA_BASE_URL")
            cls.verbose = True # os.getenv("DEFAULT_OLLAMA_MODEL_VERBOSE")

            available_models = cls.get_models()
            if cls.model not in available_models:
                raise HTTPException(status_code=404, detail=f"El modelo base: '{cls.model}' no está en Ollama. Reconfigure el modelo base para poder ver los modelos disponibles.")
            
            cls.device = 'cuda' if  torch.cuda.is_available() else 'cpu'

            logger.info(f"✅ Dispositivo torch seleccionado: {cls.device}")            
            
            if cls._model is None:
                logger.info("🌀 Cargando modelo por primera vez...")
                cls._model = ChatOllama(
                    model=cls.model,
                    temperature=cls.temperature,
                    num_ctx=cls.context_size,
                    top_k=cls.top_k,
                    top_p=cls.top_p,
                    base_url=cls.base_url,
                    keep_alive=cls.keep_alive,
                    verbose=cls.verbose,
                    device=cls.device
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
            logger.exception("Error al ejecutar clai")
            return {"error": str(e)}
    
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
            return [f"Error obteniendo modelos: {str(e)}"]

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

            clai = agent_manager.get_agent("clai")
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
            clai = agent_manager.get_agent("clai_eval")
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
