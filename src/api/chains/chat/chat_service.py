from abc import ABC, abstractmethod

from src.config.config import config
from src.domain.ports.chat.interface_chat import InterfaceChat
from src.infrastructure.utils.agents.agent_factory import AgentFactory
from src.infrastructure.utils.chat.factory.chat_factory import chat_factory
from src.logger.logger_config import logger

MAX_RETRIES: int = config.chat.max_retries
VERBOSE: bool = config.chat.verbose
MAX_MESSAGES: int = config.chat.max_messages
CHAT_PROVIDER: str = config.chat.provider
CHAT_URL: str = config.chat.uri
CHAT_MODEL: str = config.chat.model


class ChatService(ABC):

    def __init__(
            self,
            max_messages: int = MAX_MESSAGES,
            chat_provider: str = CHAT_PROVIDER,
            chat_url: str = CHAT_URL,
            chat_model: str = CHAT_MODEL
    ):

        self.logger = logger.bind(category="agents")

        self.max_messages = max_messages

        self.agent_factory: AgentFactory = AgentFactory()
        self.chat: InterfaceChat = chat_factory.instance(chat_provider)

        self.chat_url: str = chat_url
        self.chat_model: str = chat_model

        self.logger.info(f"New chat service has been instantiated based on chat provider {chat_provider} and model {chat_model}.")

    @abstractmethod
    async def chatbot(self, inputs: dict):
        raise NotImplementedError("Method not implemented at the abstract level.")

