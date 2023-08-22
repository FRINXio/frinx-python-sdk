from typing import Any

from pydantic import BaseModel
from pydantic import Extra
from pydantic.types import StrictStr
from pydantic.types import StrictInt

from frinx.common.type_aliases import ListStr
from frinx.common.type_aliases import ListAny
from frinx.common.type_aliases import DictAny
from frinx.common.worker.service import ServiceWorkersImpl
from frinx.common.worker.task_result import TaskResult
from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.worker.worker import WorkerImpl
from frinx.common.worker.task_def import TaskDefinition
from frinx.common.worker.task_def import TaskInput
from frinx.common.worker.task_def import TaskOutput
from frinx.common.util import json_parse
from frinx.common.util import validate_structure
from frinx.common.util import snake_to_camel_case


# TODO: move to other file, e.g. local/util.py
class DynamicTask(BaseModel):
    class _SubWorkflowParam(BaseModel):
        name: StrictStr
        version: StrictInt

    class Config:
        alias_generator = snake_to_camel_case
        extra = Extra.forbid

    name: StrictStr
    task_reference_name: StrictStr
    type: StrictStr
    sub_workflow_param: _SubWorkflowParam


class UtilsService(ServiceWorkersImpl):

    class JSONParse(WorkerImpl):

        class WorkerDefinition(TaskDefinition):
            name: str = 'JSON_parse'
            description: str = 'Returns object from JSON or errors if occures.'
            labels: ListStr = ['UTILS']

        class WorkerInput(TaskInput):
            input: str

        class WorkerOutput(TaskOutput):
            result: DictAny | ListAny | None
            errors: ListStr | None

        def execute(self, worker_input: WorkerInput) -> TaskResult[Any]:
            result, errors = json_parse(input=worker_input.input)

            return TaskResult(
                status=TaskResultStatus.COMPLETED,
                output=self.WorkerOutput(
                    result=result, 
                    errors=errors or None
                )
            )

    class ForkJoinInputValidator(WorkerImpl):

        class WorkerDefinition(TaskDefinition):
            name: str = 'fork_join_input_validator'
            description: str = 'Input validator for Dynamic_Fork / 1.'
            labels: ListStr = ['UTILS']

        class WorkerInput(TaskInput):
            dynamic_tasks: str
            expected_type: str
            expected_name: str
            dynamic_tasks_input: str
        
        class WorkerOutput(TaskOutput):
            result: DictAny | ListAny | None
            errors: ListStr | None

        def execute(self, worker_input: WorkerInput) -> TaskResult[Any]:
            # TODO: validate also dynamic_tasks_input
            dynamic_tasks, errors = json_parse(dynamic_tasks=worker_input.dynamic_tasks)
            dynamic_tasks_input, errors = json_parse(
                errors, dynamic_tasks_input=worker_input.dynamic_tasks_input)

            if dynamic_tasks:
                for idx, dyn_task in enumerate(dynamic_tasks):
                    errors = validate_structure(
                        dyn_task, DynamicTask, 
                        properties={
                            'type': worker_input.expected_type,
                            'name': worker_input.expected_name
                        },
                        errors=errors,
                        idx=idx
                    )

            return TaskResult(
                status=TaskResultStatus.COMPLETED,
                output=self.WorkerOutput(
                    result={
                        'dynamic_tasks': dynamic_tasks,
                        'dynamic_tasks_input': dynamic_tasks_input
                    } if not errors else None, 
                    errors=errors or None
                )
            )
