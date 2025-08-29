from fastapi import FastAPI
from langserve import add_routes

from src.api.chains.chat.dsforms_service import clai_service_dsforms_runnable_lambda
from src.api.chains.echo_chain import echo_chain
from src.api.endpoints.conversion.fhir2neo4j import router as fhir2neo4j_router
from src.api.endpoints.data.clinical_history import router as clinical_history_router
from src.api.endpoints.data.dsforms import router as dsforms_router
from src.api.endpoints.data.fhir import router as fhir_router

#   Instance main application
app = FastAPI()

#   Record LangChain paths
add_routes(app, echo_chain, path="/echo")
add_routes(app, clai_service_dsforms_runnable_lambda, path="/chat/dsforms")

#   Remove app routes from schema to fix problems with swagger
for route in app.routes:
    route.include_in_schema = False

#   Record project endpoints to be published
app.include_router(fhir_router)
app.include_router(clinical_history_router)
app.include_router(fhir2neo4j_router)
app.include_router(dsforms_router)
