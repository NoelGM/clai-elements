from src.domain.services.async_service import AsyncService


class SayHelloAsync(AsyncService):

    def __init__(self):
        super().__init__('Say Hello async service')

    def _thread(self, name: str) -> dict:

        try:

            self._logger.info(f'Hello {name}')

            return {
                "status_code": 202,
                "msg": "Accepted"
            }

        except Exception as e:

            self._logger.error(f'Error while replaying: {str(e)}.')

            return {
                "status_code": 500,
                "msg": "Internal server error"
            }
