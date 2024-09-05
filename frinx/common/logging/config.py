import logging.config
from pathlib import Path

from pydantic_settings import BaseSettings


class LoggerSettings(BaseSettings):
    LOG_FILE_PATH: Path = Path.cwd() / 'workers.log'  # TODO
    DEFAULT_LOG_LEVEL: str = 'INFO'
    DEFAULT_HANDLERS: list[str] = ['file', 'console']
    TASK_LOG_HANDLER_CONFIG: dict = {
        'max_capacity': 100,
        'max_message_length': 15000
    }  # TODO


class LoggerConfig:
    """
    Configuration class for setting up logging.
    """
    _setup_done = False
    _logger_settings = LoggerSettings()

    def __init__(self, level: str | None = None, handlers: list[str] | None = None):
        self.level = level or self._logger_settings.DEFAULT_LOG_LEVEL
        self.handlers = handlers or self._logger_settings.DEFAULT_HANDLERS

    def setup_logging(self):
        """Set up logging configuration using dictConfig."""
        if LoggerConfig._setup_done:
            return  # Prevent reconfiguration

        logging.config.dictConfig(self.generate_logging_config())
        LoggerConfig._setup_done = True

    def generate_logging_config(self) -> dict:
        """Generate the logging configuration dictionary."""
        return {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'verbose_formatter': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d]: %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S',
                },
                'default_formatter': {
                    'format': '%(asctime)s | %(threadName)s | %(levelname)s | %(name)s | %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S',
                },
            },
            'handlers': {
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': str(self._logger_settings.LOG_FILE_PATH),
                    'maxBytes': 10 * 1024 * 1024,  # 10 MB
                    'backupCount': 10,
                    'level': self.level,
                    'formatter': 'verbose_formatter',
                },
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': self.level,
                    'formatter': 'default_formatter',
                },
                # Prefer to configure TaskLogHandler in the root rather than adding it manually with .addHandler()
                # 'task_logger': {
                #     'class': 'frinx.common.logging.handlers.TaskLogHandler',
                #     'level': 'DEBUG',
                #     'max_capacity': self._logger_settings.TASK_LOG_HANDLER_CONFIG['max_capacity'],
                #     'max_message_length': self._logger_settings.TASK_LOG_HANDLER_CONFIG['max_message_length'],
                # },
            },
            'root': {
                'handlers': ['file'],  # TODO, see the comment above
                'level': self.level,
                'propagate': False,
            },
            'loggers': {
                'logger_placeholder': {
                    'handlers': self.handlers,
                    'level': self.level,
                    'propagate': False,
                },
            },
        }
