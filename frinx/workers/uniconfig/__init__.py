from typing import Optional

from requests import Response

from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.worker.task_result import TO
from frinx.common.worker.task_result import TaskResult


def handle_response(response: Response, worker_output: Optional[TO] = None) -> TaskResult[TO]:
    if not response.ok:
        return TaskResult(
            status=TaskResultStatus.FAILED,
            logs=response.content.decode('utf8')
        )
    return TaskResult(
        status=TaskResultStatus.COMPLETED,
        output=worker_output
    )
