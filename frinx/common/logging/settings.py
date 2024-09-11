import os
from pathlib import Path

from pydantic_settings import BaseSettings


class LoggerSettings(BaseSettings):
    LOG_FILE_PATH: Path = Path(os.environ.get('LOG_FILE_PATH', '/tmp/workers.log'))
    DEFAULT_LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO').upper()
    DEFAULT_HANDLERS: list[str] = ['file']  # The root handler is used by default for logging.
    LOG_FORMAT_DEFAULT: str = '%(asctime)s | %(threadName)s | %(levelname)s | %(source)s | %(message)s'
    LOG_FORMAT_VERBOSE: str = '%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s'
