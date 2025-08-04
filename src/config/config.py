import os

from dynaconf import Dynaconf

config = Dynaconf(
    settings_files=[os.environ.get('CONFIG_FILE')],
    environments=True,
    env='local'
)
