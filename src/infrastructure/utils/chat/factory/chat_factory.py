import os

from src.infrastructure.utils.chat.factory.interface_chat import InterfaceChat
from src.infrastructure.utils.chat.factory.interface_chat_ragas import InterfaceChatRAGAS
from src.infrastructure.utils.chat.factory.ollama_chat import OllamaChat
from src.infrastructure.utils.chat.factory.ollama_chat_EV import OllamaChatEV


# En el futuro se pueden importar otros chat providers, por ejemplo:
# from src.services.chat.other_chat import OtherChat

class FactoryChat:
    @staticmethod
    def get_chat_instance() -> InterfaceChat:
        # Lee la variable de entorno para determinar qué proveedor utilizar (por defecto, "ollama")
        chat_provider = os.getenv("DEFAULT_MODEL_PROVIDER", "ollama").lower()
        if chat_provider == "ollama":
            OllamaChat().load_model()
            return OllamaChat()
        # Se pueden agregar nuevos proveedores en el futuro
        # elif chat_provider == "other":
        #     return OtherChat()
        else:
            raise ValueError(f"Proveedor de chat desconocido: {chat_provider}")

    @staticmethod
    def get_chat_instanceEV() -> InterfaceChatRAGAS:
        OllamaChatEV.load_model()
        return OllamaChatEV()