import logging.config

from frinx.common.logging.root_logger import root_log_handler
from frinx.common.logging.settings import LoggerSettings
from frinx.common.type_aliases import DictAny


class LoggerConfig:
    """
    Configuration class for setting up logging.
    """
    _setup_done = False
    _logger_settings = LoggerSettings()

    def __init__(self, level: str | None = None, handlers: list[str] | None = None):
        self.level = level or self._logger_settings.DEFAULT_LOG_LEVEL
        self.handlers = handlers or self._logger_settings.DEFAULT_HANDLERS

    def setup_logging(self) -> None:
        """Set up logging configuration using dictConfig."""
        if LoggerConfig._setup_done:
            return  # Prevent reconfiguration

        logging.config.dictConfig(self.generate_logging_config())
        logging.getLogger().addHandler(root_log_handler)
        LoggerConfig._setup_done = True

    def generate_logging_config(self) -> DictAny:
        """Generate the logging configuration dictionary."""
        return {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'verbose_formatter': {
                    'format': self._logger_settings.LOG_FORMAT_VERBOSE,
                    'datefmt': '%Y-%m-%d %H:%M:%S',
                },
                'default_formatter': {
                    'format': self._logger_settings.LOG_FORMAT_DEFAULT,
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
            },
            'root': {
                'handlers': ['file'],  # NOTE: The root_log_handler is attached automatically.
                'level': self.level,
                'propagate': False,
            },
        }
