from abc import ABC, abstractmethod
from typing import Any

from src.config.logger_config import logger
from src.domain.ports.http.http_client import HttpClient


class Agent(ABC):

    def __init__(
            self,
            name,
            client: HttpClient = None,
            max_retries: int=2,
            verbose: bool=True,
            logger_ = None
    ):
        self.name = name
        self.client: HttpClient = client
        self.max_retries = max_retries
        self.verbose = verbose
        self.logger = logger.bind(category="agents") if logger_ is None else logger_

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        raise NotImplementedError("Method not implemented at the abstract level.")

    @abstractmethod
    async def async_execute(self, *args, **kwargs) -> Any:
        raise NotImplementedError("Method not implemented at the abstract level.")

    @abstractmethod
    def configure_chat(self, *args, **kwargs):
        raise NotImplementedError("Method not implemented at the abstract level.")
