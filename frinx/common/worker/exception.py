import os
from typing import Any
from typing import TypeAlias

from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.worker.task_result import TaskResult

RawTaskIO: TypeAlias = dict[str, Any]


class RetryOnExceptionError(Exception):
    """
    Exception class representing a task that needs to be retried.

    This class encapsulates the logic to determine if a task should be retried based on
    the number of poll attempts and manages the logging of the retry events.

    Attributes:
        retry_delay_seconds (int): Delay in seconds before retrying the task.
        max_retries (int): Maximum number of retries allowed.
        caught_exception (Exception): The exception that caused the task to stop and retry.
    """

    def __init__(self, exception: Exception, retry_delay_seconds: int, max_retries: int):
        """Initializes a RetryOnExceptionError exception."""
        self.retry_delay_seconds: int = retry_delay_seconds or int(os.getenv('WORKFLOW_TASK_RETRY_DELAY', '10'))
        self.max_retries = max_retries or int(os.getenv('WORKFLOW_TASK_MAX_RETRIES', '3'))
        self.caught_exception: Exception = exception

    def update_task_result(self, task: RawTaskIO, task_result: TaskResult[Any]) -> TaskResult[Any]:
        """
        Updates the task result based on the current poll count and retry logic.

        Args:
            task (RawTaskIO): The raw task input/output object.
            task_result (TaskResult): The result object to be updated.

        Returns:
            TaskResult: The updated task result object.
        """
        current_poll_count: int = task.get('pollCount', 0)

        if self._should_retry(current_poll_count):
            task_result.status = TaskResultStatus.IN_PROGRESS
            task_result.callback_after_seconds = self.retry_delay_seconds
        else:
            task_result.status = TaskResultStatus.FAILED

        self._log_task_status(task_result, current_poll_count)
        return task_result

    def _should_retry(self, current_poll_count: int) -> bool:
        """Determines if the task should be retried based on the current poll count."""
        return current_poll_count < self.max_retries

    def _log_task_status(self, task_result: TaskResult[Any], current_poll_count: int) -> None:
        """Logs the task status with the current poll count and exception details."""
        error_name: str = type(self.caught_exception).__name__
        error_info: str = str(self.caught_exception)
        log_message = (f'{RetryOnExceptionError.__name__}({current_poll_count}/{self.max_retries}): '
                       f'{error_name} - {error_info}')

        if isinstance(task_result.logs, str):
            task_result.logs = [task_result.logs]

        task_result.logs.append(log_message)

    @property
    def get_caught_exception_name(self) -> str:
        """Returns the name of the exception that caused the task to stop and retry."""
        return f'{type(self.caught_exception).__name__} (via {self.__class__.__name__})'
