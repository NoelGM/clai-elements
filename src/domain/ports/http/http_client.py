import httpx
from typing import Any, Dict, Optional

class HttpClient:

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 10.0,
        verify: bool = True
    ):
        self.base_url = base_url.rstrip("/")
        self.default_headers = headers or {}
        self.timeout = timeout
        self.verify = verify

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        async with httpx.AsyncClient(
            timeout=self.timeout,
            headers={**self.default_headers, **(headers or {})},
            verify=self.verify
        ) as client:
            resp = await client.get(f"{self.base_url}{path}", params=params)
            resp.raise_for_status()
            return resp

    async def post(
        self,
        path: str,
        data: Any = None,
        json: Any = None,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        async with httpx.AsyncClient(
            timeout=self.timeout,
            headers={**self.default_headers, **(headers or {})},
            verify=self.verify
        ) as client:
            resp = await client.post(f"{self.base_url}{path}", data=data, json=json)
            resp.raise_for_status()
            return resp