from abc import ABC, abstractmethod
from typing import Any

from src.config.logger_config import logger


class Agent(ABC):

    def __init__(
            self,
            name,
            max_retries: int=2,
            verbose: bool=True,
            logger_ = None
    ):
        self.name = name
        self.max_retries = max_retries
        self.verbose = verbose
        self.logger = logger.bind(category="agents") if logger_ is None else logger_

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        raise NotImplementedError("Method not implemented at the abstract level.")

    @abstractmethod
    def call_llm(self, *args, **kwargs) -> dict:
        raise NotImplementedError("Method not implemented at the abstract level.")