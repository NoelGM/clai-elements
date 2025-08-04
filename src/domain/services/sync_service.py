from abc import ABC

from src.domain.services.service import Service


class SyncService(Service, ABC):

    def __init__(
            self,
            name: str,
            logger_=None
    ):
        super().__init__(name, logger_)
