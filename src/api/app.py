from fastapi import FastAPI
from langserve import add_routes

from src.api.chains.echo_chain import echo_chain
from src.api.endpoints.conversion.fhir2neo4j import router as fhir2neo4j_router
from src.api.endpoints.data.fhir import router as fhir_router
from src.api.endpoints.data.neo4j import router as neo4j_router
from src.api.endpoints.examples.say_hello import router as say_hello_router

#   Instance main application
app = FastAPI()

#   Record LangChain path
add_routes(app, echo_chain, path="/echo")

#   Record project endpoints
app.include_router(say_hello_router)
app.include_router(fhir_router)
app.include_router(neo4j_router)
app.include_router(fhir2neo4j_router)

