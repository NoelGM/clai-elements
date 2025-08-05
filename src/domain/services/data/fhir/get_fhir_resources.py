from abc import ABC

import requests

from src.api import RESP500
from src.domain.services.sync_service import SyncService


class GetFHIRResources(SyncService, ABC):

    def __init__(
            self,
            name: str,
            base_url: str,
            resource: str,
    ):
        super().__init__(name)
        self._base_url: str = base_url
        self._resource: str = resource
        self._uri: str = base_url + resource if resource.startswith('/') else base_url + '/' + resource

    def run(self, token: str) -> dict:

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        try:

            response = requests.get(self._uri, headers=headers)
            response.raise_for_status()
            return response.json()

        except Exception as e:

            self._logger.error(f"Error while recovering resource {self._resource}: {str(e)}.")

            return RESP500