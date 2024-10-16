import os

from pydantic_settings import BaseSettings


class LoggerSettings(BaseSettings):
    """
    A class that defines logger settings, which can be overridden by environment variables.
    Defaults are provided if no environment variables are set.
    """
    LOG_FILE_PATH: str = os.environ.get('LOG_FILE_PATH', '/tmp/workers.log')
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FORMAT_DEFAULT: str = '%(asctime)s | %(threadName)s | %(levelname)s | %(source)s | %(message)s'
    LOG_FORMAT_VERBOSE: str = '%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s'
