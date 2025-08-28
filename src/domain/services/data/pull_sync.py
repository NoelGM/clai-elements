from src.api import RESP500
from src.domain.ports.dao.data_stream import DataStream
from src.domain.services.sync_service import SyncService


class PullSync(SyncService):

    def __init__(
            self,
            input_stream: DataStream
    ):
        super().__init__("Pull sync")
        self._input_stream: DataStream = input_stream

    def run(self, input_params: dict) -> dict:
        self._logger.info('Getting data from sources...')
        input_data = self._input_stream.pull(input_params)
        if not self._check_port(self._input_stream):
            return RESP500
        self._logger.info('Data have been properly extracted.')
        return input_data.to_dict(orient='index')
