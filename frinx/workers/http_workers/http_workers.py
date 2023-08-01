from typing import Any
from typing import Optional

from pydantic import AnyHttpUrl
from pydantic import Field
from pydantic import NonNegativeFloat

from frinx.common.conductor_enums import ContentType
from frinx.common.conductor_enums import HttpMethod
from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.type_aliases import DictAny
from frinx.common.type_aliases import DictStr
from frinx.common.type_aliases import ListAny
from frinx.common.type_aliases import ListStr
from frinx.common.util import cookie_jar_to_dict
from frinx.common.util import snake_to_camel_case
from frinx.common.worker.service import ServiceWorkersImpl
from frinx.common.worker.task_def import TaskDefinition
from frinx.common.worker.task_def import TaskExecutionProperties
from frinx.common.worker.task_def import TaskInput
from frinx.common.worker.task_def import TaskOutput
from frinx.common.worker.task_result import TaskResult
from frinx.common.worker.worker import WorkerImpl
from frinx.services.http_service import http_service


class HTTPWorkersService(ServiceWorkersImpl):

    class GenericHTTPWorker(WorkerImpl):

        class WorkerDefinition(TaskDefinition):
            name: str = 'generic_HTTP_worker'
            description: str = 'Generic HTTP worker.'
            labels: ListAny = ['SIMPLE']
            timeout_seconds: int = 360
            response_timeout_seconds: int = 360

        class ExecutionProperties(TaskExecutionProperties):
            exclude_empty_inputs: bool = True
        
        class WorkerInput(TaskInput):
            uri: AnyHttpUrl
            method: HttpMethod
            # OPTIONAL WITH DEFAULTS
            content_type: ContentType | None = ContentType.APPLICATION_JSON
            connect_timeout: NonNegativeFloat | None = 360
            headers: DictStr | None = {}
            accept: ContentType | None = None
            read_timeout: NonNegativeFloat | None
            body: DictAny | ListAny | str | None = None
            cookies: DictStr | None = None

            class Config(TaskInput.Config):
                alias_generator = snake_to_camel_case
                use_enum_values = True

        class WorkerOutput(TaskOutput):
            status_code: int = Field(..., alias='statusCode')
            response: DictAny | ListAny | str
            cookies: DictAny
            logs: Optional[ListStr] | Optional[str]

            class Config(TaskOutput.Config):
                allow_population_by_field_name = True
                min_anystr_length = 1

        def execute(self, worker_input: WorkerInput) -> TaskResult[Any]:
            response = http_service.http_task(worker_input)
            logs = f'{worker_input.method} {worker_input.uri} | status: {response.status_code} {response.reason}'
            logs = f'{worker_input}'

            return TaskResult(
                status=TaskResultStatus.COMPLETED if response.ok else TaskResultStatus.FAILED,
                output=self.WorkerOutput(
                    status_code=response.status_code,
                    response=response.text,
                    cookies=cookie_jar_to_dict(response.cookies),
                    logs=logs
                ),
                logs=logs
            )
