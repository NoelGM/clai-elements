from abc import ABC, abstractmethod
from typing import List, Dict, Any

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class InterfaceChatRAGAS(ABC):

    @classmethod
    @abstractmethod
    def load_model(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def get_models(cls) -> List[str]:
        pass

    @abstractmethod
    def info_model(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def ask_model(self, question: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def ask_clai(self, question: str, patient: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def ask_clai_eval(self, question: str, patient: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def set_run_config(self, config):
        """Método requerido por RAGAS para configurar la ejecución."""
        pass
        

    @abstractmethod
    def generate(self, messages, **kwargs):
        """Método requerido por LangChain/RAGAS para generación de respuestas."""
        pass