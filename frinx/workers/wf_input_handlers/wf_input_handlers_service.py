import json
from typing import Any

from frinx.common.type_aliases import ListStr
from frinx.common.type_aliases import ListAny
from frinx.common.type_aliases import DictAny
from frinx.common.worker.service import ServiceWorkersImpl
from frinx.common.worker.task_result import TaskResult
from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.worker.worker import WorkerImpl
from frinx.common.worker.task_def import TaskExecutionProperties
from frinx.common.worker.task_def import TaskDefinition
from frinx.common.worker.task_def import TaskInput
from frinx.common.worker.task_def import TaskOutput


# TODO: rename
class WFInputHandlersService(ServiceWorkersImpl):

    class JSONTransformTask(WorkerImpl):

        class WorkerDefinition(TaskDefinition):
            name: str = 'JSON_transform_task'
            description: str = 'Returns an object from JSON string.'
            labels: ListStr = ['UTILS']

        class WorkerInput(TaskInput):
            input: str

        class WorkerOutput(TaskOutput):
            result: DictAny | ListAny | None
            errors: ListStr | None

        def execute(self, worker_input: WorkerInput) -> TaskResult[Any]:
            result, errors = None, None
            if worker_input.input:
                try:
                    result = json.loads(worker_input.input)
                except json.JSONDecodeError:
                    errors = ['Property < input > is JSON invalid format.']
            else:
                errors = ['Cannot parse empty string.']

            return TaskResult(
                status=TaskResultStatus.COMPLETED,
                output=self.WorkerOutput(result=result, errors=errors)
            )
        
    class ForkJoinWFInputHandler(WorkerImpl):

        class WorkerDefinition(TaskDefinition):
            name: str = 'fork_join_wf_input_handler'
            description: str = 'Input handler and validator for Dynamic_Fork_Join workflow.'
            labels: ListStr = ['UTILS']

        class WorkerInput(TaskInput):
            dynamic_tasks: str
            expected_type: str
            expected_name: str
            dynamic_tasks_input: str
        
        class WorkerOutput(TaskOutput):
            result: DictAny | ListAny | None
            errors: ListStr | None

        # TODO: REFACTOR !!!
        def execute(self, worker_input: WorkerInput) -> TaskResult[Any]:
            # def _unixp_err(name: str, type: str) -> str:
            #     return f'Dynamic tasks contain unexpected name "{name}" or expected type "{type}"'
            
            _unixp_err = lambda n, t: \
                f'Dynamic tasks contain unexpected name < {n} > or expected type < {t} >'

            errors = []

            if worker_input.dynamic_tasks:
                try:
                    dynamic_tasks = json.loads(worker_input.dynamic_tasks)
                except json.JSONDecodeError:
                    errors.append('Property < dynamic_tasks > is JSON invalid format.')
            else:
                errors.append('Cannot parse empty string, property < dynamic_tasks > is empty.')
            if worker_input.dynamic_tasks_input:
                try:
                    dynamic_tasks_input = json.loads(worker_input.dynamic_tasks_input)
                except json.JSONDecodeError:
                    errors.append('Property < dynamic_tasks_input > is JSON invalid format.')
            else:
                errors.append('Cannot parse empty string, property < dynamic_tasks_input > is empty.')
            try:
                for task in dynamic_tasks:
                    match task['name'], task['type']:
                        case worker_input.expected_name, worker_input.expected_type:
                            continue
                        case _:
                            errors.append(
                                _unixp_err(
                                    worker_input.expected_name, 
                                    worker_input.expected_type
                                )
                            )
                            break
            except KeyError as err:
                errors.append(f'Missing property < {err.args[0]} > in < dynamic_tasks >.')        

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
