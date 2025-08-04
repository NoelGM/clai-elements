import uvicorn

from src.api.app import app
from src.config.config import config
from src.config.logger_config import logger

logger = logger.bind(category="app")

host, port = config.service.host, config.service.port
logger.info(f"Service will be published on {host}:{str(port)}.")

if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)
