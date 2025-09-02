from src.infrastructure.adapters.chat.ollama_chat import OllamaChat
from src.infrastructure.adapters.chat.ollama_chat_EV import OllamaChatEV
from src.infrastructure.utils.chat.factory import OLLAMA, OLLAMA_EV
from src.infrastructure.utils.factories.factory import Factory


class ChatFactory(Factory):

    def __init__(self):
        instances: dict = {
            OLLAMA: OllamaChat(),
            OLLAMA_EV: OllamaChatEV()
        }
        super().__init__(instances)

chat_factory: ChatFactory = ChatFactory()