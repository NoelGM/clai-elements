from abc import ABC, abstractmethod
from typing import Any


class Factory(ABC):

    def __init__(self, instances: dict):
        self.instances: dict = instances

    def instance(self, label: str) -> Any:
        instance = self.instances.get(label)
        if label not in self.instances.keys():
            return None
        return instance
