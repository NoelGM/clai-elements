from typing import Any, Dict, Optional

from src.domain.ports.http.http_client import HttpClient


class OnesaitClient(HttpClient):

    def __init__(
            self,
            protocol: str,
            hostname: str,
            verify: bool = False,
            timeout: float = 10.0
    ):
        self.protocol = protocol
        self.hostname = hostname
        if not self.protocol or not self.hostname:
            # raise ValueError("Las variables de entorno 'general.protocol' y/o 'general.hostname' no están definidas.")
            raise ValueError("Protocol and/or hostname have not been defined.")
        self.verify = verify # os.getenv("AUTH_CERTIFICATE_VALIDATE") == "1"
        self.timeout = timeout # float(os.getenv("HTTP_CLIENT_TIMEOUT", 10.0))
        # Construimos la URL base (permitimos override)
        self.base_url=f"{self.protocol}://{self.hostname}/"
        super().__init__(base_url=self.base_url, timeout=self.timeout, verify=self.verify)

    def _get_headers(self):
        headers = super()._get_headers() if hasattr(super(), '_get_headers') else {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers

    async def get(
            self,
            path: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None
        ) :
            return await super().get(path, params=params, headers=headers)

    async def post(
        self,
        path: str,
        data: Any = None,
        json: Any = None,
        headers: Optional[Dict[str, str]] = None
    ) :
        return await super().post(path, data=data, json=json, headers=headers)