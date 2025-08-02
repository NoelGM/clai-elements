from fastapi import APIRouter, Depends

from src.api import RESP202
from src.api.model.examples.say_hello import say_hello_post_params
from src.domain.services.examples.say_hello_async import SayHelloAsync
from src.domain.services.examples.say_hello_sync import SayHelloSync
from src.domain.services.service import Service

router = APIRouter()

@router.get("/hellosync")
def say_hello_sync_get():
    service: Service = SayHelloSync()
    response = service.run('John Doe')
    return response

@router.post("/hellosync")
def say_hello_sync_post(params=Depends(say_hello_post_params)):
    service: Service = SayHelloSync()
    full_name: str = params['name'] + " " + params['family']
    response = service.run(full_name)
    return response

@router.get("/helloasync")
def say_hello_sync_get():
    service: Service = SayHelloAsync()
    service.run('John Doe')
    return RESP202

@router.post("/helloasync")
def say_hello_sync_post(params=Depends(say_hello_post_params)):
    service: Service = SayHelloAsync()
    full_name: str = params['name'] + " " + params['family']
    service.run(full_name)
    return RESP202
