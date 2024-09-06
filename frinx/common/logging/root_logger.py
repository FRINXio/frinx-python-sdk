import logging

from frinx.common.logging.config import LoggerConfig
from frinx.common.logging.handlers import RootLogHandler

# I would like to remove all the code below and add handler to root via config.py
root_log_handler = RootLogHandler()

logger_config_instance = LoggerConfig()
logger_config_instance.setup_logging()

root_logger = logging.getLogger('root')
root_logger.addHandler(root_log_handler)  # Add the custom RootLogHandler to the root logger

logger = root_logger  # Assign the root logger to 'logger' for compatibility with existing code
