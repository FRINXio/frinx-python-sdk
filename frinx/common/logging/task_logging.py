import logging
import threading
from collections import deque


class TaskLogHandler(logging.Handler):
    """
    A custom logging handler that stores log messages in a thread-specific queue,
    creates a log list, and prints formatted log messages to the console.

    Attributes:
        max_capacity (int): Maximum number of log messages to retain in the queue.
        max_message_length (int): Maximum length of each log message.
        thread_data (threading.local): Thread-local storage for log data.
        formatter (logging.Formatter): Formatter for internal log storage.
        console_formatter (logging.Formatter): Formatter for console output.
        console_handler (logging.StreamHandler): Handler for console output.
    """

    def __init__(self, max_capacity: int = 100, max_message_length: int = 15000, level: int = logging.INFO) -> None:
        super().__init__(level)
        self.max_capacity: int = max_capacity
        self.max_message_length: int = max_message_length
        self.thread_data = threading.local()
        self.thread_data.log_queue = deque(maxlen=self.max_capacity)
        self.thread_data.task_name = 'Unknown'
        self.formatter = logging.Formatter('%(levelname)s: %(message)s')
        self.console_formatter = logging.Formatter(
            '%(asctime)s | %(threadName)s | %(levelname)s | task: %(taskname)s | %(message)s', datefmt='%F %T')
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(self.console_formatter)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record.
        Store the log record in the thread-specific queue and print it to the console.
        """
        if not hasattr(self.thread_data, 'log_queue'):
            self._setup_thread_logging()

        if not hasattr(self.thread_data, 'task_name'):
            self.thread_data.task_name = 'Unknown'

        record.taskname = self.thread_data.task_name

        formatted_record: str = self.format(record)
        truncated_record: str = self._truncate_message(formatted_record)
        self.thread_data.log_queue.append(truncated_record)

        self.console_handler.emit(record)

    def _truncate_message(self, message: str) -> str:
        """
        Truncate a message if it exceeds the maximum message length.
        """
        if len(message) > self.max_message_length:
            return message[:self.max_message_length] + '... [truncated]'
        return message

    def _setup_thread_logging(self) -> None:
        """
        Setup thread-specific logging.
        """
        self.thread_data.log_queue = deque(maxlen=self.max_capacity)

    def set_taskname_for_thread(self, task_name: str) -> None:
        """
        Set the task name for the current thread.
        """
        self.thread_data.task_name = task_name

    def get_logs(self, clear: bool = True) -> list[str]:
        """
        Get the logs for the current thread.
        """
        if not hasattr(self.thread_data, 'log_queue'):
            return []

        logs: list[str] = list(self.thread_data.log_queue)

        if clear:
            self.thread_data.log_queue.clear()
            self._clear_taskname_for_thread()

        return logs

    def _clear_taskname_for_thread(self) -> None:
        """
        Clear the task name for the current thread.
        """
        if hasattr(self.thread_data, 'task_name'):
            del self.thread_data.task_name