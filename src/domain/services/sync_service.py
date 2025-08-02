import logging
from abc import ABC
from logging import Logger

from src.domain.services.service import Service


class SyncService(Service, ABC):

    def __init__(
            self,
            name: str,
            logger: Logger = logging.getLogger('Synchronous service')
    ):
        super().__init__(name, logger)
