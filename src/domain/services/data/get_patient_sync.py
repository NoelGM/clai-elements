from src.api import RESP500
from src.domain.ports.dao.data_stream import DataStream
from src.domain.services.sync_service import SyncService


class GetPatientSync(SyncService):

    def __init__(
            self,
            input_port: DataStream
    ):
        super().__init__("Get patient sync")
        self._input_port: DataStream = input_port

    def run(self, input_params: dict) -> dict:

        input_data = self._input_port.pull(input_params)

        if not self._check_port(self._input_port):
            return RESP500

        return input_data.to_dict(orient='index')
