import os
from typing import List, Any

from fastapi import HTTPException
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel

from src.infrastructure.utils.agents.agent_manager import AgentManager
from src.infrastructure.utils.chat.factory.chat_factory import FactoryChat
from src.logger.logger_config import logger


# from src.config import Config

#config_dict = Config.as_dict()


class OutputItem(BaseModel):
    type: str
    content: Any
    contentType: str
    originData: Any


class OutputPayload(BaseModel):
    status: str
    outputs: List[OutputItem]
    history: Any

#   TODO NGM: max_messages se estaba extrayendo de esta forma: int(os.getenv("MAX_HISTORY_MESSAGES", 10))
class DsformsService:
    """Servicio para invocar el agente clai con manejo de errores y logs."""

    def __init__(self, max_retries: int = 2, verbose: bool = True, max_messages: int = 10):
        self.logger = logger.bind(category="services")
        self.agent_manager = AgentManager(max_retries=max_retries, verbose=verbose)
        self.max_messages = max_messages
        self.chat = FactoryChat.get_chat_instance()

    """
    Servicio para interactuar con el agente clai, proporcionando manejo de errores y logs.
    Métodos
    -------
    onesait_healthcare_dsforms(inputs: dict, config: Dict[str, Any]) -> Dict[str, Any]
        Invoca el agente clai para procesar una pregunta relacionada con un paciente, utilizando el historial y un token de autenticación.
        Parámetros:
            inputs (dict): Diccionario que contiene la pregunta ('question'), información del paciente ('patient_name', 'patient_id') y el historial ('history').
            config (Dict[str, Any]): Diccionario de configuración que debe incluir los metadatos, especialmente el 'token' de autenticación.
        Retorna:
            Dict[str, Any]: Respuesta generada por el agente clai a través del método 'ask_dsforms'.
        Comentarios:
            - El método extrae la información relevante de los parámetros de entrada.
            - Utiliza un patrón de factoría para obtener una instancia de chat.
            - Llama al método 'ask_dsforms' del chat, pasando la pregunta, los datos del paciente, el historial y el token.
            - Es importante que el 'token' esté presente en los metadatos de la configuración.
    """

    # async def chatbot(self, inputs: dict, config: Dict[str, Any]):

        # token = config.get("metadata", {}).get("token", "")

    async def chatbot(self, inputs: dict, config):

        # token = config.get("metadata", {}).get("token", "")
        # token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJoazdIZHN5bmJyZGFHNk1QMEZwSkJXN2hISjJLUkZLaU82QnFiS2cxb213In0.eyJleHAiOjE3Nzg1ODg4OTIsImlhdCI6MTc0NzA1Mjg5MiwianRpIjoiNTkyYzI5ZjEtMzU2MS00Nzc3LWFjNzYtNWJlMTQyMjNmOTY4IiwiaXNzIjoiaHR0cHM6Ly9oZWFsdGhjYXJlLmN3YnltaW5zYWl0LmNvbS9hdXRoL3JlYWxtcy9vaC1iYXNlIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6IjUxODVlODc0LTAyZTItNDE5ZS04NGZhLTA2YzY0MDY0NzI1ZSIsInR5cCI6IkJlYXJlciIsImF6cCI6Imhucm9sZSIsInNlc3Npb25fc3RhdGUiOiIzNGY2ODM4NC1hZWY0LTQxZjEtOGRjZS01NTk4Zjc2MWRmNTgiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbIioiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIkhOUE9SX0NMSU5JQ0FMX0ZPUk1TX1dJREdFVCIsIkhOQ0lUX0NJVF9QQVRJX0FQUE8iLCJITkdFUF9QQUNTX0FDQ0VTUyIsIkhOR0VQX0VYVF9TQU0iLCJITkFVVF9DT05GX1JPTEVfUFJGX1JFQUQiLCJITkRPQ19BVFRBQ0hfUkVBRCIsIkhOR0VQX1dSSVRFX1JFUV9MQUIiLCJITkFVVF9GVU5fTEFCRUwiLCJITlBPUl9SRVFfV0lER0VUIiwiSE5BVVRfT0ZFUl9ERU1BX1BSRVNUIiwiSE5BVVRfRlVOX0FDVElWRV9QQVNTSVZFIiwiSE5BVVRfVVNSX1JFQURfU1lTIiwiSE5BVVRfRlVOX1NUUlVDVF9SRUFEX1NZUyIsIkhOQ09OX1dPUktMSVNUX0lNUEVYUCIsInVtYV9hdXRob3JpemF0aW9uIiwiSE5BVVRfQURNX1JFQUQiLCJITkdFUF9SRVNVTFRTX1JFUV9JTUEiLCJPSEFMRV9XUiIsIkhOR0VQX1dSSVRFX1JFUV9JTUFfQURWQU5DRUQiLCJITkFVVF9QSFlTX1NUUlVDVF9XUklURV9TWVMiLCJITkNJVF9DSVRfRURJVElPTl9BUFBPIiwiSE5DT05fR0VTVF9QQVJBTSIsIkhOR0VQX0VYRV9JTUEiLCJIRFJfQkFTRV9SIiwiSE5DSVRfQVBQT0lOVF9DQUxMIiwiSERSX0ZPVU5EQVRJT05fUiIsIkhEUl9CQVNFX1ciLCJITkNJVF9BQ1RJT05fQURNSVNTSU9OIiwiSE5DT05fV09SS0xJU1RfV1JJVEUiLCJIRFJfRk9VTkRBVElPTl9XIiwiSE5DT05fRE9NQUlOX1JFQUQiLCJITkNPTl9QQVJBTV9XUklURSIsIkhOQVVUX1VTUl9XUklURV9PUkciLCJITkFVVF9QSFlTX1NUUlVDVF9SRUFEX1NZUyIsIkhOQVVUX0NBTEVOREFSX01OR19XUklURSIsIkhOQ09OX0NMSSIsIkhOR0VQX1dSSVRFX1JFUV9JTUEiLCJITkFVVF9QUkZfV1JJVEUiLCJITkNPTl9ET01BSU5fV1JJVEUiLCJITkdFUF9XUklURV9PV05fUkVRX0lNQSIsIkhOQVVUX0ZVTl9TVFJVQ1RfV1JJVEVfU1lTIiwiT0hBTEVfUkQiLCJITkFVVF9DT05GX1JPTEVfUFJGX1dSSVRFIiwiSE5BVVRfV09SS1BMQUNFX1dSSVRFIiwiSE5QT1JfQVBQT19ORVdfUFJPRiIsIkhOUE9CX1BPQl9XUklURSIsIkhOQ0FUX0NBVF9XUklURSIsIkhOQVVUX1VTUl9XUklURV9TWVMiLCJITlBPUl9BUFBPX05FV19TQ0hFIiwib2ZmbGluZV9hY2Nlc3MiLCJITkdFUF9DSVRfTkVXIiwiSE5BVVRfSElTVF9DT05ORUNUSU9OX1NZUyIsIkhOQ0lUX0NJVF9SRVNDSEVEVUxFIiwiSE5HRVBfUkVBRF9SRVEiLCJITkNJVF9BQ1RJT05fRU5EX0FQUE8iLCJkZWZhdWx0LXJvbGVzLW9wZW5zaGlmdC1kZXYiLCJITkNBVF9URVJNSU5PTE9HWV9XUklURSIsIkhOQVVUX1dPUktQTEFDRV9SRUFEIiwiSE5HRVBfQ0lUX0NBTkNFTCIsIkhOQ0lUX0NJVF9DQU5DRUwiLCJITlBPQl9QT0JfUkVBRF9DT05GSURFTlRJQUwiLCJITkdFUF9BVVRPUklaX1JFUSIsIkhOUE9SX0FQUE9fV0lER0VUIiwiSE5BVVRfRlVOX1JFQUQiLCJITkFVVF9QUkZfUkVBRCIsIkhOR0VQX1JFU1VMVFNfUkVRX0xBQiIsIkhOQ0lUX0NJVF9ORVciLCJITkdFUF9GSU5fUkVRIiwiSE5BVVRfVVNSX1dSSVRFX0NFTlRFUiIsIkhOUE9CX1BPQl9SRUFEIiwiSE5BVVRfQURNX1dSSVRFIiwiSE5HRVBfU0VFX01JTl9ERVRBSUwiLCJITkdFUF9XUklURV9PV05fUkVRX0xBQiIsIkhOQ0xJX0ZPTExPV19GT1JNU19SRUFEIiwiSU1QUklNSVJfSU5GIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJwcm9maWxlIGVtYWlsIiwic2lkIjoiMzRmNjgzODQtYWVmNC00MWYxLThkY2UtNTU5OGY3NjFkZjU4IiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwcmFjdGl0aW9uZXJfaWQiOiJ1c19pbnN0YWxsIiwicHJlZmVycmVkX3VzZXJuYW1lIjoidXNfaW5zdGFsbCJ9.G8RUGbLseQx1UvIpzLe8UQNsRx-z5yORwq179LYtK0WuwZ6x5-0tRj9gDFngU_eop_esUSLFxuujXw_GoDJ2goZrfO2p4O7Pz4MOPV6466Kzun3OiLwMn8GlhmwlU_vovJD6boPNtAFaVtvdLPwBvFPjc9Fk5W4lRK3ISxwcA2_wmPuboeaAjgQcN2EUwjx6c-dQ0H9TLWPJ2hep907h54XLFNGv4UGLN12VYJQn46VhTC6_4wUQ7cy3t6mI0sLSiQb506DAIFRmjg1v2IpjveLqPQeNWEuzOIulK7y7waQ-wYxd4Wn8-dx_NKKpTnsOmgryFjZ273UDMhA7XQ24QQ"
        token = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJoazdIZHN5bmJyZGFHNk1QMEZwSkJXN2hISjJLUkZLaU82QnFiS2cxb213In0.eyJleHAiOjE3ODI4MDY3OTksImlhdCI6MTc1MTI3NDQ1OCwiYXV0aF90aW1lIjoxNzUxMjcwNzk5LCJqdGkiOiI5NWQwNmVmYS1jMDk3LTRiZDktYmFjZi1jMzhkOTg4MTljNDQiLCJpc3MiOiJodHRwczovL2hlYWx0aGNhcmUuY3dieW1pbnNhaXQuY29tL2F1dGgvcmVhbG1zL29oLWJhc2UiLCJzdWIiOiJmOjE0NTBhYWE3LWJhNjgtNDRlZC04MTEyLTBiNTljZDhlMDVjNTp1c19hZG1pbiIsInR5cCI6IkJlYXJlciIsImF6cCI6Imhucm9sZSIsIm5vbmNlIjoiNGQwYWU3MWUtYWQ1ZS00NWE3LWFiZTEtNDdlYzVlNDRjMjQ3Iiwic2Vzc2lvbl9zdGF0ZSI6IjIyZDJkNjBkLTY5ZDAtNGM3Zi05OTkzLWM3ZGFlZTk2NzE1YyIsImFjciI6IjAiLCJhbGxvd2VkLW9yaWdpbnMiOlsiKiJdLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwic2lkIjoiMjJkMmQ2MGQtNjlkMC00YzdmLTk5OTMtYzdkYWVlOTY3MTVjIiwibGFzdC1sb2dpbiI6IjIwMjUvMDYvMzAgMDg6MDYiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJITkNBVF9BRE1fUkVBRCIsIkhOQ0FUX0FETV9XUklURSIsIkhOQ0FUX0NBVF9SRUFEIiwiSE5DQVRfQ0FUX1dSSVRFIiwiSE5DQVRfQ0FUX1ZBTFVFIiwiSE5DQVRfU1BBX1JFQUQiLCJITkNBVF9TUEFfV1JJVEUiLCJITkNBVF9DQVRfRVhQT1JUIiwiSE5DQVRfQ09ORl9QUkVTVCIsIkhOQ0FUX1RFUk1JTk9MT0dZX0RSQUZUIiwiSE5DQVRfVEVSTUlOT0xPR1lfV1JJVEUiLCJITkNBVF9URVJNSU5PTE9HWV9SRUFEIiwiSE5DQVRfVEVSTUlOT0xPR1lfTE9DSyIsIkhOQ0FUX0NPTkZfRVFVSSIsIkhOQVVUX0FETV9SRUFEIiwiSE5BVVRfQURNX1dSSVRFIiwiSE5BVVRfQ09ORl9ST0xFX1BSRl9SRUFEIiwiSE5BVVRfQ09ORl9ST0xFX1BSRl9XUklURSIsIkhOQVVUX1VTUl9SRUFEX1NZUyIsIkhOQVVUX1VTUl9XUklURV9TWVMiLCJITkFVVF9QUkZfV1JJVEUiLCJITkFVVF9GVU5fTEFCRUwiLCJITkFVVF9GVU5fQUNUSVZFX1BBU1NJVkUiLCJITkFVVF9ISVNUX0NPTk5FQ1RJT05fU1lTIiwiSE5BVVRfUEhZU19TVFJVQ1RfUkVBRF9TWVMiLCJITkFVVF9QSFlTX1NUUlVDVF9XUklURV9TWVMiLCJITkFVVF9GVU5fU1RSVUNUX1JFQURfU1lTIiwiSE5BVVRfRlVOX1NUUlVDVF9XUklURV9TWVMiLCJITkFVVF9QUkVTVF9XUklURV9TWVMiLCJITkFVVF9QUkVTVF9SRUFEX1NZUyIsIkhOQVVUX0NBTEVOREFSX01OR19XUklURSIsIkhOQVVUX1dPUktQTEFDRV9SRUFEIiwiSE5BVVRfV09SS1BMQUNFX1dSSVRFIiwiSE5BVVRfREVTS1RPUCIsIkhOQVVUX09SR19MQUJFTF9SRUFEIiwiSE5BVVRfT1JHX0xBQkVMX1dSSVRFIiwiSE5QT0JfQURNX1JFQUQiLCJITlBPQl9BRE1fV1JJVEUiLCJITlBPQl9QT0JfUkVBRCIsIkhOUE9CX1BPQl9SRUFEX0NPTkZJREVOVElBTCIsIkhOUE9CX1BPQl9FWFRFUk5BTF9TWVNURU0iLCJITlBPQl9QT0JfQUNUSVZFX1BBU1NJVkUiLCJITlBPQl9QT0JfQ09ORklERU5USUFMIiwiSE5QT0JfUE9CX0RVUExJQ0FURV9QUk9QT1NBTCIsIkhOUE9CX1BPQl9EVVBMSUNBVEVfTUFOQUdFTUVOVCIsIkhOUE9CX1BPQl9DT05DSUxJQVRJT05fU0VBUkNIIiwiSE5QT0JfUE9CX0NPTkNJTElBVElPTl9NQU5BR0VNRU5UIiwiSE5QT0JfUE9CX1VOS05PV05fTUFOQUdFTUVOVCIsIkhOUE9CX1BPQl9ET0NVTUVOVF9NQU5BR0VNRU5UIiwiSE5QT0JfUE9CX0FEVkFOQ0VEX0NBUkVURUFNIiwiSE5QT0JfUE9CX1JFUE9SVCIsIkhOUE9CX1BPQl9JTVBPUlRfUkVBRCIsIkhOUE9CX1BPQl9DQVJFVEVBTV9QUk9DRVNTX1JFQUQiLCJITlBPQl9QT0JfQ0FSRVRFQU1fUFJPQ0VTU19XUklURSIsIkhOUE9CX0dBVVNTX1VOS05PV05fTUFOQUdFTUVOVCIsIkhOUE9CX1BPQl9BRFZBTkNFRF9DQVJFVEVBTV9DTE9TRV9PQ0NVUEFUSU9OIiwiSE5IQ0VfSERfQUNDRVNPIiwiSE5IRFdfQVBQT0lOVE1FTlQiLCJITkhEV19BUFBPSU5UTUVOVF9OT0NMSU5JQ0FMIiwiSE5IRFdfRVBJU09ERSIsIkhOSERXX0VQSVNPREVfTk9DTElOSUNBTCIsIkhOSERXX1BST0NFRFVSRSIsIkhOSERXX0NBUkVQTEFOIiwiSE5IRFdfUkVRVUVTVFMiLCJITkhEV19SRVFVRVNUU19OT0NMSU5JQ0FMIiwiSE5DT05fR0VTVF9QQVJBTSIsIkhOQ09OX0NMSSIsIkhOQ09OX0RPTUFJTl9XUklURSIsIkhOQ09OX0RPTUFJTl9SRUFEIiwiSE5DT05fV09SS0xJU1RfV1JJVEUiLCJITkNPTl9XT1JLTElTVF9JTVBFWFAiLCJITkNPTl9QQVJBTV9XUklURSIsIktGQ19fTUVOVV9fVklTSUJJTElEQUQiLCJDSVRfX0NJVEFDSU9OX19WRVJDSVRBU1RPRE9TQ0VOVFJPUyIsIkNJVF9fU0lNUExFX19TVVBNQVhGT1JaIiwiS0ZDX19NRU5VX19DSVRfUkVQUk9CTE9RIiwiQ0lUX19SRVBST0JMT1FfX1JFUFJPRyIsIkNJVF9fUkVQUk9CTE9RX19BTlVMQVIiLCJDSVRfX1JFUFJPQkxPUV9fQlVaT04iLCJDSVRfX1JFUFJPQkxPUV9fTk9BR0VOREEiLCJDSVRfX1JFUFJPQkxPUV9fRk9SWkFSIiwiQ0lUX19SRVBST0JMT1FfX1NVUE1BWEZPUloiLCJDSVRfX1JFUFJPQkxPUV9fTk9ERU1PUkEiLCJLRkNfX01FTlVfX0NJVF9DQUpBUkVQUiIsIkhOQ0lUX0FETV9BRERJQ0lPTkFMX0lORk9STUFUSU9OIiwiSE5DSVRfX1ZJU1VBTElaRV9BRERJVElPTkFMX0lORk9STUFUSU9OIiwiSU1QUklNSVJfSU5GIiwiSE5GT1JNX01BTkFHX1JFQUQiLCJITkZPUk1fTUFOQUdfV1JJVEUiLCJITkZPUk1fTUFOQUdfUFVCTElTSCIsIkhORk9STV9NQU5BR19ERUFDVElWQVRFIiwiSE5GT1JNX01BTkFHX1RSQU5TTEFURSIsIkhORk9STV9SRVBPUlRfUkVBRCIsIkhORk9STV9SRVBPUlRfV1JJVEUiLCJITkFVVF9QUkZfUkVBRCIsIkhOQVVUX0ZVTl9SRUFEIiwiSE5BVVRfRlVOX1dSSVRFIiwiSE5QT0JfUE9CX1dSSVRFIiwiSE5QT0JfUE9CX1dSSVRFX0NPTkZJREVOVElBTCIsIlJPTEVfVVNFUiIsIlJPTEVfQURNSU5JU1RSQVRPUiIsIkhOQVROX1JFQUQiLCJITkFUTl9DUkVBVEUiLCJITkRPQ19BVFRBQ0hfUkVBRCIsIkhORE9DX0FUVEFDSF9XUklURSIsIkhORE9DX0FUVEFDSF9TVVBFUldSSVRFIiwiSE5QUkVGQUNfTUFOQUdfTUFJTlRFTkFOQ0UiLCJPSFBMQVNNQV9NQU5BR19QTEFTTUEiLCJPSFBMQVNNQV9JTVBPUlRfUExBU01BIiwiT0hQTEFTTUFfRVhQT1JUX1BMQVNNQSIsIkhEUl9CQVNFX1IgIiwiSERSX0JBU0VfVyAiLCJIRFJfQkFTRV9EICIsIkhEUl9DTElOSUNBTF9SICIsIkhEUl9DTElOSUNBTF9XICIsIkhEUl9DTElOSUNBTF9EICIsIkhEUl9GT1VOREFUSU9OX1IgIiwiSERSX0ZPVU5EQVRJT05fVyAiLCJIRFJfRk9VTkRBVElPTl9EICIsIkhEUl9GSU5BTkNJQUxfUiAiLCJIRFJfRklOQU5DSUFMX1cgIiwiSERSX0ZJTkFOQ0lBTF9EICIsIkhEUl9TUEVDSUFMSVpFRF9SICIsIkhEUl9TUEVDSUFMSVpFRF9XICIsIkhEUl9TUEVDSUFMSVpFRF9EICIsIk9IQlBNX1BBVElFTlRfQUNDRVNTIiwiT0hCUE1fUFJPQ0VTU19MSVNUIiwiT0hCUE1fUFJPQ0VTU19ERVNJR05FUiIsIk9IQlBNX0RFRklOSVRJT05fVyIsIk9IQlBNX0RFRklOSVRJT05fUiIsIk9IQlBNX0NBUkVQTEFOX1ciLCJPSEJQTV9DQVJFUExBTl9SIiwiT0hCUE1fVEFTS19XIiwiT0hCUE1fVEFTS19SIiwiT0hJRU5fQVBJR1dfUkVBRCIsIk9ISUVOX0NIQU5ORUxTX1ZJRVciLCJPSElFTl9DSEFOTkVMU19XUklURSIsIk9ISUVOX0tBRktBX0NPTk5FQ1QiLCJPSEhPTV9QQVRJRU5UX0FERCIsIk9ISE9NX1BST0dSQU1fQUNDRVNTIiwiT0hIT01fUEFUSUVOVF9DQVRFR09SWV9XUklURSIsIk9ISE9NX1BST0dSQU1fRklOSVNIIiwiT0hIT01fQ0FSRV9QTEFOX1JFQUQiLCJPSEhPTV9DQVJFX1BMQU5fV1JJVEUiLCJPSEhPTV9JTklUSUFMX0FTU0VTU01FTlRfUkVBRCIsIk9ISE9NX0lOSVRJQUxfQVNTRVNTTUVOVF9XUklURSIsIk9ISE9NX01FQVNVUkVNRU5UX1JFQUQiLCJPSEhPTV9NRUFTVVJFTUVOVF9TRVRUSU5HIiwiT0hIT01fUVVFU1RJT05OQUlSRV9SRUFEIiwiT0hIT01fUVVFU1RJT05OQUlSRV9TRVRUSU5HIiwiT0hIT01fUFJPR1JBTV9SRUFDVElWQVRFIiwiT0hIT01fUEFUSUVOVF9MSVNUX0FDQ0VTUyIsIk9ISE9NX01FQVNVUkVNRU5UX1dSSVRFIiwiT0hIT01fUVVFU1RJT05OQUlSRV9XUklURSIsIk9IQ1NNX0RFU0tUT1AiLCJPSENTTV9DT05TRU5UX1dSSVRFIiwiT0hDU01fQ09OU0VOVF9SRUFEIiwiT0hQUk1fUFJPR1JBTV9BQ0NFU1MiLCJQUk1fQVBQT19XSURHRVQiLCJQUk1fVklUQUxTSUdOU19XSURHRVQiLCJQUk1fRVBJU19XSURHRVQiLCJQUk1fSU5EX1dJREdFVCIsIlBSTV9UUkVBVE1FTlRTX1dJREdFVCIsIlBSTV9FU0NfV0lER0VUIiwiUFJNX1ZBTF9XSURHRVQiLCJQUk1fRVZPX1dJREdFVCIsIlBSTV9ESUFHX1dJREdFVCIsIkhOQVVUX01BTkFHRVJfVVNFUlMiLCJPSEJQTV9QUk9DRVNTX0RFU0lHTkVSX1BVQkxJU0giLCJPSEJQTV9BRE1JTiIsIk9IQlBNX1BST0NFU1NfREVTSUdORVJfUiIsIk9IQ0hBVF9BSSIsIk9IQlBNX1BST0NFU1NfREVTSUdORVJfQURNSU4iLCJPSEJQTV9BQ0NFU1NfT1BFUkFUSU9OX0lOQ0lERU5UUyIsIk9IQlBNX0FDQ0VTU19PUEVSQVRJT05fQUNUSVZJVElFUyIsIk9IQlBNX0FDQ0VTU19PUEVSQVRJT05fVElNRVJTIiwiT0hEU0tfQUNDRVNTX0FMRVJUIiwiT0hEU0tfUEFUSUVOVEFMRVJUUyIsIk9IRFNLX1BBVElFTlRBTEVSVFNfTk9DTElOSUNBTCIsIk9ISERSX1BBVElFTlRBTEVSVFNfTk9DTElOSUNBTCIsIk9ISERBX0FMTEVSR1lfQUNDRVNTIiwiT0hEU0tfU0VBUkNIX1BBVElFTlRTIl19LCJyZXNvdXJjZSI6W10sInByYWN0aXRpb25lcl9pZCI6InVzX2FkbWluIiwicHJvZmlsZSI6InVzX2FkbWluIiwiaG5yb2xlIjp7ImNvZGUiOiJVU19BRE1JTl9ST0xfU1lTVEVNIiwiZGlzcGxheSI6IlNJU1RFTUEiLCJzY29wZSI6IjEiLCJoY1Byb2Zlc3Npb25Db2RlIjpudWxsLCJoY1Byb2Zlc3Npb25OYW1lIjpudWxsLCJoY1NwZWNpYWx0eUNvZGUiOm51bGwsImhjU3BlY2lhbHR5TmFtZSI6bnVsbH0sIm5hbWUiOiJVc3VhcmlvIGFkbWluaXN0cmFkb3IiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ1c19hZG1pbiIsImdpdmVuX25hbWUiOiJVc3VhcmlvIiwiZmFtaWx5X25hbWUiOiJhZG1pbmlzdHJhZG9yIiwiZW1haWwiOiIifQ.duJpUOXHeHC6mNvvBceV4kBOoFcFnBA_sxKiMN3YSAk4aosKYUt3C_FzMDvebpzFCuFqEvX_4uJmOi7n_BDlxHf8ZaC3esVuRrWI0LSN05t5YaxK6AeYP0Up7-8kbcTWePc7H023xDwJ2NAJQkKt4pRZXdfyx8DN4ig31_Yfu1RpT-Ojwm29Nm01F92wStxFltCpM1-aVZ9BuXyxfDZhkKb-77-S47huo3S-p_les4hI7d_edbqye5nxwEwXD_4FzB8vi1o_7WAD8Ff8kKVjjeoDkPmj0-4QTKlsFxy0Jsa8bQ4GXS5PDt6TLif3SisTpeF3MbGzD-vez5f3H4xY6A"

        question = inputs.get("question", "")
        # patient = {
        #     "patient_name": inputs.get("patient_name", ""),
        #     "patient_id": inputs.get("patient_id", "")
        # }
        patientId = inputs.get("patientId", "")
        resourceId = inputs.get("resourceId", "")
        resourceType = inputs.get("resourceType", "Questionnaire")
        history = inputs.get("history", [])
        # Ultimos X mensajes del historial
        # max_messages = int(os.getenv("MAX_HISTORY_MESSAGES", 10))   #   TODO NGM

        if history and len(history) > self.max_messages:
            history = history[-self.max_messages:]
        try:
            # Chatbot
            self.logger.info(f"Realizando pregunta para la question de longitud {len(question)} caracteres")
            chat_model = self.chat.load_model()
            self.logger.info(
                f"Instanciated OllamaChat with model={self.chat.model}, "
                f"temperature={self.chat.temperature}, context_size={self.chat.context_size}, "
                f"top_k={self.chat.top_k}, top_p={self.chat.top_p}, keep_alive={self.chat.keep_alive}, "
                f"base_url={self.chat.base_url}, verbose={self.chat.verbose}, device={self.chat.device}"
            )
            # Invocamos al agente historia clínica
            # se recupera la corutina del agente historia clínica
            async_dsfroms = self.agent_manager.get_agent("forms")  # NGM la pregunta va hasta aqui en primera instancia
            async_dsfroms.configureLLmChat(chat_model, patientId, token, resourceId, resourceType)
            ## transformar la pregunta para historia clínica
            # pregunta_hc = async_dsfroms.transformar_pregunta_hc(question)

            ############################################################################################################

            ##agente combinador
            #  agente_combinador = self.agent_manager.get_agent("combinador")

            ##invocar agente historia_clinica con la pregunta transformada
            # historia_clinica_agent = self.agent_manager.get_agent("historia_clinica")
            # result_historia = await historia_clinica_agent.async_execute(chat_model, pregunta_hc, patientId, token,
            #                                                              history)
            # contexto_hc = result_historia.get("generacion", "")

            # Ejecutar el agente dsforms normalmente
            '''
            result_dsforms = await async_dsfroms.async_execute(
                chat_model, question, patientId, token, resourceId, resourceType, history
            )
            '''
            result_dsforms = await async_dsfroms.async_execute( #   FIXME NGM aqui falla
                chat_model, question, patientId, token, resourceId, resourceType, history, '' #contexto_hc
            )  # NGM aqui es la llamada al llm, se omite el context determina por la historia, por el momento

            # respuesta = result_dsforms["generacion"]
            respuesta_forms = result_dsforms["generacion"]
            # respuesta_hc = contexto_hc

            ### Llamamos al agente combinador para combinar las respuestas de dsforms y historia clínica
            # respuesta_final = await agente_combinador.combinar(
            #     chat_model, question, respuesta_forms, respuesta_hc, history)
            respuesta_final = respuesta_forms # NGM

            originData = result_dsforms["originData"]

            '''
            # Añade el contexto de historia clínica si existe
            if contexto_hc:
                respuesta_final = f"{respuesta}\n\n[Información relevante de historia clínica]:\n{contexto_hc}"
            else:
                respuesta_final = respuesta 

            # Ejecutamos la corutina y esperamos la respuesta
            respuesta_async_ds = []            
            result_dsforms = await async_dsfroms
            respuesta_async_ds.append(result_dsforms)            
            respuesta= respuesta_async_ds[0]["generacion"]
            originData= respuesta_async_ds[0]["originData"]

             # 4. Si el contexto de historia clínica es relevante, combinarlo en la respuesta final
            if contexto_hc and self.es_contexto_relevante(respuesta, contexto_hc):
                respuesta_final = f"{respuesta}\n\n[Información relevante de historia clínica]:\n{contexto_hc}"
            else:
                respuesta_final = respuesta
            '''

            # TODO - Ampliar condiciones para el tipo de respuesta img/html
            if isinstance(respuesta_final, str):
                typeData = "text"
                contentType = "text/plain"
            else:
                typeData = "json"
                contentType = "application/json"

            '''
            output_payload = {
                "status": "success",
                "outputs": [
                    {
                        "type": typeData,
                        "content": respuesta,
                        "contentType": contentType,
                        "originData": originData
                    }
                ],
                "history": history
            }
            return output_payload 
            '''
            output_payload = OutputPayload(
                status="success",
                outputs=[
                    OutputItem(
                        type=typeData,
                        content=respuesta_final,
                        contentType=contentType,
                        originData=originData
                    )
                ],
                history=history
            )
            return {
                "root": output_payload
            }

        except Exception as e:
            # self.logger.error("dsforms service fallido", e)
            self.logger.error(f"dsforms service fallido: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error interno en DsformsService")


# instancia única y runnable asociado
clai_service_dsforms = DsformsService()
clai_service_dsforms_runnable_lambda = RunnableLambda(clai_service_dsforms.chatbot)