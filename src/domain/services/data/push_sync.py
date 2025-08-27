from src.api import RESP500, RESP200
from src.domain.ports.dao.data_stream import DataStream
from src.domain.services.sync_service import SyncService


class PushSync(SyncService):

    def __init__(
            self,
            output_stream: DataStream
    ):
        super().__init__("Push sync")
        self._output_stream: DataStream = output_stream

    def run(self, data, output_params: dict) -> dict:
        self._logger.info('Pushing data...')
        success: bool = self._output_stream.push(data, output_params)
        if not self._check_port(self._output_stream) or not success:
            return RESP500
        self._logger.info('Data have been properly inserted.')
        return RESP200
