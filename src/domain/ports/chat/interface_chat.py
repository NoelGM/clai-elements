from abc import ABC, abstractmethod
from typing import List, Dict, Any

class InterfaceChat(ABC):

    @classmethod
    @abstractmethod
    def load_model(cls, url: str, model: str) -> str:
        """Devuelve el modelo de chat actual."""
        pass

    @classmethod
    @abstractmethod
    def get_models(self) -> List[str]:
        """Retorna una lista de modelos disponibles."""
        pass

    @abstractmethod
    def info_model(self) -> Dict[str, Any]:
        """Devuelve información detallada del modelo seleccionado."""
        pass

    @abstractmethod
    def ask_model(self, question: str) -> Dict[str, Any]:
        """Realiza una consulta al modelo de Ollama y retorna la respuesta."""
        pass

    @abstractmethod
    def ask_clai(self, question: str, patient: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Realiza una consulta especifica para clai, utilizando además datos del paciente."""
        pass

    @abstractmethod
    def ask_clai_eval(self, question: str, patient: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza una consulta especifica para clai, utilizando además datos del paciente.
        Debe devolver también el contexto utilizado bajo la clave 'context_used'.
        """
        pass