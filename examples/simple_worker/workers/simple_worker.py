from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.type_aliases import ListAny
from frinx.common.worker.task_def import TaskDefinition
from frinx.common.worker.task_def import TaskInput
from frinx.common.worker.task_def import TaskOutput
from frinx.common.worker.task_result import TaskResult
from frinx.common.worker.worker import WorkerImpl


class Echo(WorkerImpl):
    class WorkerDefinition(TaskDefinition):
        name: str = 'Echo'
        description: str = 'Returns input as output'
        labels: ListAny = ['TEST']
        timeout_seconds: int = 60
        response_timeout_seconds: int = 60

    class WorkerInput(TaskInput):
        input: str

    class WorkerOutput(TaskOutput):
        output: str

    def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
        return TaskResult(
            status=TaskResultStatus.COMPLETED,
            logs=['Echo worker invoked successfully'],
            output=self.WorkerOutput(output=worker_input.input)
        )
