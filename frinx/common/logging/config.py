import logging
import logging.config
from typing import Literal

from frinx.common.logging.root_logger import root_log_handler
from frinx.common.logging.settings import LoggerSettings
from frinx.common.type_aliases import DictAny


class LoggerConfig:
    """
    LoggerConfig class is responsible for setting up and configuring logging.
    """
    _setup_done: bool = False  # Class variable to ensure the logging setup happens only once

    def __init__(self,
                 log_file_path: str | None = None,
                 level: Literal['DEBUG', 'INFO', 'WARNING'] | None = None) -> None:
        """
        Initializes the LoggerConfig class with optional overrides for the log file path and log level.
        """
        self.logger_settings = LoggerSettings()
        self.logger_settings.LOG_FILE_PATH = log_file_path or self.logger_settings.LOG_FILE_PATH
        self.logger_settings.LOG_LEVEL = level or self.logger_settings.LOG_LEVEL

    def setup_logging(self) -> None:
        """
        Adds the root_log_handler for the root logger and marks the setup as complete to prevent reconfiguration.
        """
        if LoggerConfig._setup_done:
            return  # Prevent reconfiguration

        # Apply the logging configuration and add root_log_handler
        logging.config.dictConfig(self.generate_logging_config())
        logging.getLogger().addHandler(root_log_handler)
        LoggerConfig._setup_done = True

    def generate_logging_config(self) -> DictAny:
        """
        Generates the dictionary for configuring the logging.
        """
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose_formatter': {
                    'format': self.logger_settings.LOG_FORMAT_VERBOSE,
                    'datefmt': '%Y-%m-%d %H:%M:%S',
                },
                'default_formatter': {
                    'format': self.logger_settings.LOG_FORMAT_DEFAULT,
                    'datefmt': '%Y-%m-%d %H:%M:%S',
                },
            },
            'handlers': {
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': str(self.logger_settings.LOG_FILE_PATH),
                    'maxBytes': 10 * 1024 * 1024,  # 10 MB
                    'backupCount': 10,
                    'level': self.logger_settings.LOG_LEVEL,
                    'formatter': 'verbose_formatter',
                },
            },
            'root': {
                'handlers': ['file'],  # NOTE: The root_log_handler is attached automatically.
                'level': self.logger_settings.LOG_LEVEL,
                'propagate': False,
            },
        }
