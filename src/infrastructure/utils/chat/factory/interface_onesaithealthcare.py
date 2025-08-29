from abc import ABC, abstractmethod
from typing import List, Dict, Any

class InterfaceOnesaitHealthcare(ABC):

    @abstractmethod
    def ask_dsforms(self, question: str, patient: Dict[str, Any], history: List[Dict[str, Any]], token:str) -> Dict[str, Any]:
        """Realiza una consulta especifica para clai, utilizando además datos del paciente."""
        pass        

    @abstractmethod
    def ask_ohbpm(self, question: str, patient: Dict[str, Any], history: List[Dict[str, Any]], token:str) -> Dict[str, Any]:
        """Realiza una consulta especifica para clai, utilizando además datos del paciente."""
        pass    