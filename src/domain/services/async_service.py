import threading
from abc import ABC, abstractmethod

from src.api import RESP202, RESP500
from src.domain.services import STATUS_RUNNING, STATUS_ERROR
from src.domain.services.service import Service


class AsyncService(Service, ABC):

    def __init__(
            self,
            name: str,
            logger_=None
    ):
        super().__init__(name, logger_)

        self.ident: int = 0
        self.native_id: int = 0

    def run(self, *args) -> dict:

        self.status = STATUS_RUNNING

        self._logger.info(f'Running service {self.name}.')
        self._logger.info(f'JobId: {self.job}.')

        try:

            self._logger.info(f'Launching thread for execution of service {self.name}.')

            thread = threading.Thread(target=self._thread, args=args)
            thread.start()

            self.ident = thread.ident
            self.native_id = thread.native_id
            self._logger.info(f'Request to service {self.name} has been successfully sent through execution thread.')
            self._logger.debug(f'Thread indent is {self.ident}.')
            self._logger.debug(f'Thread native id is {self.native_id}.')

            return RESP202

        except Exception as e:

            self._logger.error(f'Error while launching thread for service {self.name}: {str(e)}.')

            self.status = STATUS_ERROR

            return RESP500

    @abstractmethod
    def _thread(self, *args) -> dict:
        raise NotImplementedError("Method not implemented at the abstract level.")