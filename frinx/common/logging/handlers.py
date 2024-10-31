import logging
import logging.config
import threading
from collections import deque

from frinx.common.logging.settings import LoggerSettings


class RootLogHandler(logging.Handler):
    """
    A logging handler that manages log messages for both task-specific and general logging,
    utilizing thread-specific queues for logs from tasks.

    Attributes:
        max_capacity (int): Maximum number of log messages to retain in the queue (for tasks).
        max_message_length (int): Maximum length of each log message (for tasks).
        thread_data (threading.local): Thread-local storage for log data (for tasks).
        formatter (logging.Formatter): Formatter for internal log storage.
        console_formatter (logging.Formatter): Formatter for console output.
        console_handler (logging.StreamHandler): Handler for console output.
    """

    _logger_settings = LoggerSettings()

    def __init__(self, max_capacity: int = 100, max_message_length: int = 15000, level: int = logging.INFO) -> None:
        super().__init__(level)
        self._is_task: bool = False
        self.max_capacity: int = max_capacity
        self.max_message_length: int = max_message_length
        self.thread_data = threading.local()
        self.thread_data.log_queue = deque(maxlen=self.max_capacity)
        self.console_formatter = logging.Formatter(self._logger_settings.LOG_FORMAT_DEFAULT, datefmt='%F %T')
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(self.console_formatter)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Process and emit a log record. Store the log in a thread-specific queue if the context is task-related.
        """
        record.threadName = self._shorten_thread_name(record.threadName)
        truncated_record: str = self._truncate_message(record.message)

        if self._is_task:
            if not hasattr(self.thread_data, 'log_queue'):
                self._setup_thread_logging()
            self.thread_data.log_queue.append(truncated_record)
            record.source = getattr(self.thread_data, 'source', record.name)
        else:
            record.source = record.name

        self.console_handler.emit(record)

    def _truncate_message(self, message: str) -> str:
        """Truncate a message if it exceeds the maximum message length."""
        if len(message) > self.max_message_length:
            return message[:self.max_message_length] + '... [truncated]'
        return message

    def _setup_thread_logging(self) -> None:
        """Setup thread-specific logging."""
        self.thread_data.log_queue = deque(maxlen=self.max_capacity)

    def set_task_info_for_thread(self, *args: str) -> None:
        """Set task-specific information for the current thread. """
        self._is_task = True
        delimiter: str = ' '
        self.thread_data.source = delimiter.join(str(arg) for arg in args)

    def get_logs(self, clear: bool = True) -> list[str]:
        """Retrieve and optionally clear the logs stored in the current thread's queue."""
        if not hasattr(self.thread_data, 'log_queue'):
            return []

        logs: list[str] = list(self.thread_data.log_queue)

        if clear:
            self.thread_data.log_queue.clear()
            self._clear_taskname_for_thread()

        return logs

    def _clear_taskname_for_thread(self) -> None:
        """Clear the task-specific information for the current thread."""
        if hasattr(self.thread_data, 'task_name'):
            del self.thread_data.task_name

    def _shorten_thread_name(self, thread_name: str | None) -> str:
        """Shorten the thread name by replacing 'Thread-' with 'T'."""
        return thread_name.replace('Thread-', 'T') if thread_name is not None else 'UnknownThread'
