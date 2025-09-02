from fastapi import FastAPI
from langserve import add_routes

from src.api.chains.chat.ds_forms_service import runnable as dsforms_runnable
from src.api.chains.echo_chain import echo_chain
from src.api.endpoints.data.clinical_history import router as clinical_history_router
from src.api.endpoints.data.dsforms import router as dsforms_router

#   Instantiate main application.

app = FastAPI()

#   Record LangChain paths.

add_routes(app, echo_chain, path="/echo")
add_routes(app, dsforms_runnable, path="/chat/dsforms")

#   Remove app routes from schema to fix problems with swagger.

for route in app.routes:
    route.include_in_schema = False

#   Record project endpoints to be published.

app.include_router(clinical_history_router)
app.include_router(dsforms_router)
