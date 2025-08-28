from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

#   TODO refactorizar cuando se hayan incluído los módulos de código que emplean esta dependencia
class EstadoGrafo(TypedDict):
    """
    Representa el estado de nuestro grafo.

    Atributos:
        question: Pregunta
        generation: Generación de LLM
        search_query: Consulta transformada para búsqueda web
        context: Resultado de búsqueda web
    """
    question: str
    generation: str
    context: str
    originData: str
    history: list[dict]
    messages: list[BaseMessage]
    questionnaire: str