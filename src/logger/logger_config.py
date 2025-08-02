import yaml
from loguru import logger
import os
import logging

# Ruta del archivo YAML
base_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(base_dir, "..", ".."))
logging_config = os.path.join(root_dir, "config", "logging_config.yaml")

# Cargar configuración desde YAML
with open(logging_config, "r") as config_file:
    config = yaml.safe_load(config_file)

# Limpiar handlers previos de loguru
logger.remove()

# Función para crear filtros dinámicos
def build_filter(config_section):
    if "log_filter_by_name" in config_section:
        name = config_section["log_filter_by_name"]
        return lambda record: record["name"].startswith(name)
    elif "log_level_filter" in config_section:
        level = config_section["log_level_filter"]
        return lambda record: record["level"].name == level
    elif "category" in config_section:
        return lambda record: record["extra"].get("category") == config_section["category"]
    return None

# Crear los sinks de loguru desde el YAML
for logger_name, log_config in config["loggers"].items():
    logger.add(
        log_config["log_file"],
        format=log_config["log_format"],
        level=log_config["log_level"],
        rotation=log_config["log_rotation"],
        retention=log_config["log_retention"],
        compression=log_config["log_compression"],
        filter=build_filter(log_config)
    )

# Handler para interceptar logs estándar (logging)
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

# Redirigir logging estándar hacia loguru
logging.basicConfig(handlers=[InterceptHandler()], level=logging.DEBUG, force=True)

# Activar nivel de logging para librerías externas
for name in ["neo4j_graphrag","neo4j"]:
    logging.getLogger(name).setLevel(logging.DEBUG)

logger.info("Configuración de logs cargada correctamente.")
