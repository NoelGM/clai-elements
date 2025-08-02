from src.domain.services.sync_service import SyncService


class SayHelloSync(SyncService):

    def __init__(self):
        super().__init__('Say Hello sync service')

    def run(self, name: str) -> dict:

        return {
            "msg": f"hello {name}"
        }
