import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from fastapi import HTTPException
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableSequence
from langchain_ollama import ChatOllama

from src.infrastructure.utils.agents.agent_manager import AgentManager
from src.infrastructure.utils.chat.factory.interface_chat import InterfaceChat
from src.infrastructure.utils.chat.factory.interface_chat_ragas import InterfaceChatRAGAS
from src.logger.logger_config import logger

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
logger = logger.bind(category="agents")
agent_manager = AgentManager(max_retries=2, verbose=True)

class OllamaChatEV(InterfaceChat, InterfaceChatRAGAS):

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
            cls.model = os.getenv("DEFAULT_OLLAMA_MODEL")
            cls.temperature = os.getenv("DEFAULT_OLLAMA_MODEL_TEMPERATURE")
            cls.context_size = os.getenv("DEFAULT_OLLAMA_MODEL_CONTEXT_SIZE")
            cls.top_k = os.getenv("DEFAULT_OLLAMA_MODEL_TOP_K")
            cls.top_p = os.getenv("DEFAULT_OLLAMA_MODEL_TOP_P")
            cls.keep_alive = int(os.getenv("DEFAULT_OLLAMA_MODEL_KEEP_ALIVE", 0))
            cls.base_url = os.getenv("OLLAMA_BASE_URL")
            cls.verbose = os.getenv("DEFAULT_OLLAMA_MODEL_VERBOSE")

            available_models = cls.get_models()
            if cls.model not in available_models:
                raise HTTPException(status_code=404, detail=f"El modelo base: '{cls.model}' no está en Ollama. Reconfigure el modelo base para poder ver los modelos disponibles.")
            
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
                    verbose=cls.verbose
                )
                logger.info(
                    f"Loaded OllamaChat with model={cls.model}, "
                    f"temperature={cls.temperature}, context_size={cls.context_size}, "
                    f"top_k={cls.top_k}, top_p={cls.top_p}, keep_alive={cls.keep_alive}, "
                    f"base_url={cls.base_url}, verbose={cls.verbose}"
                )            
            return cls._model
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.exception("Error al ejecutar clai")
            return {"error": str(e)}
    def set_run_config(self, config):
        # Implementación vacía para compatibilidad con RAGAS
        pass
    
    def __call__(self, prompt, **kwargs):
        # Devuelve solo el texto de la respuesta, como espera RAGAS
        return self.ask_model(prompt)["answer"]
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

            '''
            chat_model = ChatOllama(
                model=self.model,
                temperature=self.temperature,
                context_size=self.context_size,
                top_k=self.top_k,
                top_p=self.top_p,
                base_url=self.base_url,
                keep_alive=self.keep_alive,
                verbose=self.verbose
            )
            '''
            chat_model = self.load_model()

            logger.info(
                f"Using OllamaChatRAGAS with model={self.model}, "
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

    def ask_clai(self, question, patient) -> Dict[str, Any]:
        try:
            if not question:
                raise HTTPException(status_code=400, detail=f"No se proporcionó question")

            available_models = self.get_models()
            if self.model not in available_models:
                raise HTTPException(status_code=404, detail=f"Modelo '{self.model}' no encontrado en Ollama.")
            
            logger.info(f"Realizando pregunta para la question de longitud {len(question)} caracteres")
            '''
            chat_model = ChatOllama(
                model=self.model,
                temperature=self.temperature,
                context_size=self.context_size,
                top_k=self.top_k,
                top_p=self.top_p,
                base_url=self.base_url,
                keep_alive=self.keep_alive,
                verbose=self.verbose,
                device="cuda"
            )
            '''
            chat_model = self.load_model()
            logger.info(
                f"Instanciated OllamaChat with model={self.model}, "
                f"temperature={self.temperature}, context_size={self.context_size}, "
                f"top_k={self.top_k}, top_p={self.top_p}, keep_alive={self.keep_alive}, "
                f"base_url={self.base_url}, verbose={self.verbose}, device=cuda"
            )            



            clai = agent_manager.get_agent("clai")
            respuesta, originData = clai.execute(chat_model, question, patient)

            logger.info("Pregunta generada correctamente")


            return {
                "question": question,
                "respuesta": respuesta,
                "model": self.model,
                "temperature": self.temperature,
                "context_size": self.context_size,
                "top_k": self.top_k,
                "top_p": self.top_p,
                "originData": originData
            }
        except Exception as e:
            logger.exception("Error al ejecutar clai")
            return {"error": str(e)}
    ##añadida para ragas
    def generate(self, messages, **kwargs):
        """
        Método requerido por LangChain/RAGAS.
        """
        if self._model is None:
            self.load_model()
        # Si messages es string, úsalo directamente
        if isinstance(messages, str):
            prompt = messages
        elif isinstance(messages, list):
            prompt = "\n".join([m.content if hasattr(m, "content") else str(m) for m in messages])
        else:
            prompt = str(messages)
        # Llama al modelo y obtiene el texto
        result = self._model(prompt)
        # Devuelve en el formato esperado por LangChain/RAGAS
        return {"generations": [[{"text": result}]]}
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
