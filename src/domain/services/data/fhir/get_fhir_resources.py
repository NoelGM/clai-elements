import requests

from src.api import RESP500
from src.domain.services.sync_service import SyncService


class GetFHIRResources(SyncService):

    def __init__(
            self,
            name: str,
            base_url: str,
            resource: str
    ):
        super().__init__(name)
        self._base_url: str = base_url
        self._resource: str = resource
        self._uri: str = base_url + resource if resource.startswith('/') else base_url + '/' + resource

    def run(self, token: str, resource_id: str = '', query: str = '') -> dict:

        if token is None:

            self._logger.error('No authorization token provided.')

            return RESP500

        auth_header = token if token.lower().startswith('bearer') else f"Bearer {token}"

        headers = {
            "Authorization": auth_header,
            "Accept": "application/json"
        }

        url: str = self._uri if not resource_id else self._uri + '/' + resource_id
        url = url if not query else url + '?' + query

        try:

            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            return response.json()

        except Exception as e:

            self._logger.error(f"Error while recovering resource {self._resource}: {str(e)}.")

            return RESP500