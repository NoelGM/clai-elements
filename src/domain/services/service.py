from abc import ABC, abstractmethod
from datetime import datetime

from src.config.logger_config import logger
from src.domain.ports.dao.data_stream import DataStream
from src.domain.services import STATUS_IDLE


def _job_id() -> int:
    return int(str(datetime.now().strftime('%Y%m%d%H%M%S')))


class Service(ABC):

    def __init__(
            self,
            name: str,
            logger_ = None
    ):

        self.name: str = name
        self._logger = logger.bind(category="services") if logger_ is None else logger_

        self.job: int = _job_id()
        self.status: int = STATUS_IDLE

        self._logger.info(f"Service {self.name} has been instantiated with job id {str(self.job)}.")

    @abstractmethod
    def run(self, *args) -> dict:
        raise NotImplementedError("Method not implemented at the abstract level.")

    def _check_port(self, port: DataStream, log_message: str = "Error during data transaction:") -> bool:
        if port.exception:
            self._logger.warning(f"{log_message} {str(port.exception)}.")
            return False
        return True