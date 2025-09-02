import httpx

from src.domain.ports.http.onesait_client import OnesaitClient


class EhrClient(OnesaitClient):
    """
    Cliente especializado para el endpoint FHIR /CodeSystem de DSForms.
    Hereda la funcionalidad genérica de OnesaitClient y añade métodos FHIR.
    """

    def __init__(
            self,
            token: str,
            protocol: str = 'https',    #   TODO NGM propagar desde capas superiores
            hostname: str = 'healthcare.cwbyminsait.com',
            verify: bool = False,
            timeout: float = 10.0
    ):
        self.token = token
        self.headers = {"Authorization": token}
        super().__init__(protocol, hostname, verify=verify, timeout=timeout)

    async def get(self, url: str, params: dict = None) -> dict:
        async with httpx.AsyncClient(headers=self.headers, verify=False) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def post(self, path: str, patient_id: str, data: dict = None, headers: dict = None) -> dict:
        payload = data if data is not None else {
            "resourceType": "Bundle",
            "type": "batch",
            "entry": [
                {"request": {"method": "GET", "url": f"Patient/{patient_id}"}},
                {"request": {"method": "GET",
                             "url": f"Encounter?patient=Patient/{patient_id}&_count=200&_sort=-_lastUpdated",
                             "_count": 200}},
                {"request": {"method": "GET",
                             "url": f"Observation?patient=Patient/{patient_id}&_count=200&_sort=-_lastUpdated",
                             "_count": 200}},
                {"request": {"method": "GET",
                             "url": f"Immunization?patient=Patient/{patient_id}&_count=200&_sort=-_lastUpdated",
                             "_count": 200}},
                {"request": {"method": "GET",
                             "url": f"Condition?patient=Patient/{patient_id}&_count=200&_sort=-_lastUpdated",
                             "_count": 200}},
                {"request": {"method": "GET",
                             "url": f"MedicationRequest?patient=Patient/{patient_id}&_count=200&_sort=-_lastUpdated",
                             "_count": 200}},
                {"request": {"method": "GET",
                             "url": f"DocumentReference?patient=Patient/{patient_id}&_count=200&_sort=-_lastUpdated",
                             "_count": 200}},
                {"request": {"method": "GET",
                             "url": f"DiagnosticReport?patient=Patient/{patient_id}&_count=200&_sort=-_lastUpdated",
                             "_count": 200}},
                {"request": {"method": "GET",
                             "url": f"Procedure?patient=Patient/{patient_id}&_count=200&_sort=-_lastUpdated",
                             "_count": 200}},
                {"request": {"method": "GET",
                             "url": f"ExplanationOfBenefit?patient=Patient/{patient_id}&_count=200&_sort=-_lastUpdated",
                             "_count": 200}},
                {"request": {"method": "GET",
                             "url": f"Claim?patient=Patient/{patient_id}&_count=200&_sort=-_lastUpdated",
                             "_count": 200}},
                {"request": {"method": "GET",
                             "url": f"AllergyIntolerance?patient=Patient/{patient_id}&_count=200&_sort=-_lastUpdated",
                             "_count": 200}}
            ]
        }
        # Usa la función post de la clase padre, que ya maneja base_url, verify, etc.
        response = await super().post(path, json=payload, headers=headers or self.headers)
        if hasattr(response, 'json'):
            return response.json()
        return response


