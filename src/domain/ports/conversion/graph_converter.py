from abc import ABC, abstractmethod
from typing import Any


class GraphConverter(ABC):

    @abstractmethod
    def node(self, data: Any) -> (Any, Any):
        raise NotImplementedError("Method not implemented at the abstract level.")

    @abstractmethod
    def edges(self, data: Any) -> (Any, Any):
        raise NotImplementedError("Method not implemented at the abstract level.")