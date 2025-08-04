from fastapi import Depends
from pydantic import BaseModel


def _say_hello_params(name: str, family: str):
    return {
        "name": name,
        "family": family
    }

class _SayHelloModel(BaseModel):
    name: str
    family: str

say_hello_model: _SayHelloModel = Depends(_say_hello_params)
