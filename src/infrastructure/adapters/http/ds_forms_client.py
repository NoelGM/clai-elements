import httpx

from src.domain.ports.http.onesait_client import OnesaitClient


class DsFormsClient(OnesaitClient):
    """
    Cliente especializado para el endpoint FHIR /CodeSystem de DSForms.
    Hereda la funcionalidad genérica de OnesaitClient y añade métodos FHIR.
    """

    def __init__(
        self,
        protocol,
        hostname,
        token: str,
        verify: bool = False,
        timeout: float = 10.0
    ):
        self.token = token
        self.headers = {"Authorization": token}
        super().__init__(protocol, hostname, verify=verify, timeout=timeout)

    async def get(
            self,
            path: str,
            params: dict = None,
            headers: dict = None
    ) -> dict:
        response = await super().get(path, params=params, headers=self.headers)
        # Si la respuesta es un objeto httpx.Response, obtener el json
        if hasattr(response, 'json'):
            return response.json()
        return response

    #   FIXME NGM actualiza los parámetros y compara con el código original
    async def post(self, url: str, data: dict = None) -> dict:
        async with httpx.AsyncClient(headers=self.headers, verify=False) as client:
            payload = data if data is not None else {
                "resourceType": "Questionnaire",
                "title": "prueba-clai",
                "version": "1",
                "language": "es",
                "extension": [
                    {
                        "url": "http://hn.indra.es/dsforms/fhir/Questionnaire/type",
                        "valueCoding": {"code": "1"}
                    },
                    {
                        "url": "http://hn.indra.es/dsforms/fhir/Questionnaire/owner",
                        "valueCoding": {"code": "DESARROLLO", "display": "Desarrollo"}
                    },
                    {   
                        "url": "http://hn.indra.es/dsforms/fhir/Questionnaire/properties",
                        "valueCodeableConcept": {
                            "coding": [
                                {"code": "restriccionEdadUnidad", "display": "YEAR"}
                            ]
                        }
                    }
                ]
            }
            headers = {
                "Authorization": f"Bearer {self.token}",
                "accept": "application/json, text/plain, */*",
                "accept-language": "es,en-US;q=0.9,en;q=0.8",
                "cache-control": "no-cache",
                "content-type": "application/json",
                "origin": f"{self.base_url}",
                "pragma": "no-cache",
                "priority": "u=1, i"
            }
            response = await super().post(url, json=payload, headers=headers, verify=False)
            return response.json()
