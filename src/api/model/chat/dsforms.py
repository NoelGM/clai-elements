from typing import Any, List

from pydantic import BaseModel


class OutputItem(BaseModel):
    type: str
    content: Any
    contentType: str
    originData: Any


class OutputPayload(BaseModel):
    status: str
    outputs: List[OutputItem]
    history: Any