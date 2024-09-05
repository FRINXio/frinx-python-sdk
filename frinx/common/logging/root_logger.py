import logging

from frinx.common.logging.config import LoggerConfig
from frinx.common.logging.config import LoggerSettings
from frinx.common.logging.handlers import TaskLogHandler

# I would like to remove all the code below and add handler to root via config.py
logger_settings = LoggerSettings()
task_log_handler = TaskLogHandler(**logger_settings.TASK_LOG_HANDLER_CONFIG)

logger_config_instance = LoggerConfig()
logger_config_instance.setup_logging()

root_logger = logging.getLogger('root')
root_logger.addHandler(task_log_handler)  # Add the custom TaskLogHandler to the root logger

logger = root_logger  # Assign the root logger to 'logger' for compatibility with existing code
