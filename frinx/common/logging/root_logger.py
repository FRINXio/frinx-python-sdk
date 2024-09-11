import logging

from frinx.common.logging.handlers import RootLogHandler

root_log_handler = RootLogHandler()

root_logger = logging.getLogger('root')
logger = root_logger  # Assign the root logger to 'logger' for compatibility
