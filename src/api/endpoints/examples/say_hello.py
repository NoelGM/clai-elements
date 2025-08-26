from fastapi import APIRouter

from src.api import RESP202
from src.api.endpoints.examples import GROUP
from src.api.model.examples.say_hello import say_hello_model
from src.domain.services.examples.say_hello_async import SayHelloAsync
from src.domain.services.examples.say_hello_sync import SayHelloSync
from src.domain.services.service import Service

router = APIRouter()

tags: list[str] = ["Examples"]


@router.get(
    f"{GROUP}/hellosync",
    tags=tags
)
def say_hello_sync_get():
    service: Service = SayHelloSync()
    response = service.run('John Doe')
    return response

@router.post(
    f"{GROUP}/hellosync",
    tags=tags
)
def say_hello_sync_post(params=say_hello_model):
    service: Service = SayHelloSync()
    full_name: str = params['name'] + " " + params['family']
    response = service.run(full_name)
    return response

@router.get(
    f"{GROUP}/helloasync",
    tags=tags
)
def say_hello_sync_get():
    service: Service = SayHelloAsync()
    service.run('John Doe')
    return RESP202

@router.post(
    f"{GROUP}/helloasync",
    tags=tags
)
def say_hello_sync_post(params=say_hello_model):
    service: Service = SayHelloAsync()
    full_name: str = params['name'] + " " + params['family']
    service.run(full_name)
    return RESP202
