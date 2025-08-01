import logging
import threading
from abc import ABC, abstractmethod
from datetime import datetime
from logging import Logger

from src.api import RESPONSE_202, RESPONSE_500
from src.domain.ports.dao.data_stream import DataStream
from src.domain.services import STATUS_IDLE, STATUS_RUNNING, STATUS_ERROR


def _job_id() -> int:
    return int(str(datetime.now().strftime('%Y%m%d%H%M%S')))


class Service(ABC):

    def __init__(
            self,
            name: str = '',
            logger: Logger = logging.getLogger('service')
    ):

        self.name: str = name
        self._logger: Logger = logger

        self.job: int = _job_id()
        self.status: int = STATUS_IDLE

        self.ident: int = 0
        self.native_id: int = 0

    def run(self, *args) -> dict:

        self.status = STATUS_RUNNING

        self._logger.info('Running service %s.', self.name)
        self._logger.info('JobId: %d.', self.job)

        try:

            self._logger.info('Launching thread for execution of service %s.', self.name)

            thread = threading.Thread(target=self._thread, args=args)
            thread.start()

            self.ident = thread.ident
            self.native_id = thread.native_id
            self._logger.info('Request to service %s has been successfully sent through execution thread.', self.name)
            self._logger.debug('Thread indent is %d.', self.ident)
            self._logger.debug('Thread native id is %d.', self.native_id)

            return RESPONSE_202

        except Exception as e:

            self._logger.error('Error while launching thread for service %s.', self.name)
            self._logger.error(str(e))

            self.status = STATUS_ERROR

            return RESPONSE_500

    @abstractmethod
    def _thread(self, *args) -> dict:
        raise NotImplementedError("Method not implemented at the abstract level.")

    def _check_port(self, port: DataStream, log_message: str = "Error during data transaction:") -> bool:
        if port.exception:
            self._logger.warning(f"{log_message} {str(port.exception)}.")
            return False
        return True