import os
import random
import time
from typing import Optional

from pydantic import field_validator

from frinx.common.conductor_enums import TaskResultStatus
from frinx.common.type_aliases import DictAny
from frinx.common.type_aliases import ListAny
from frinx.common.worker.exception import RetryOnExceptionError
from frinx.common.worker.service import ServiceWorkersImpl
from frinx.common.worker.task_def import TaskDefinition
from frinx.common.worker.task_def import TaskInput
from frinx.common.worker.task_def import TaskOutput
from frinx.common.worker.task_result import TaskResult
from frinx.common.worker.worker import WorkerImpl


class TestWorkers(ServiceWorkersImpl):
    class Echo(WorkerImpl):
        class WorkerDefinition(TaskDefinition):
            name: str = 'TEST_echo'
            description: str = 'testing purposes: returns input unchanged'
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

    class Sleep(WorkerImpl):
        sleep = 10
        MAX_SLEEP_TIME = 600

        class WorkerDefinition(TaskDefinition):
            name: str = 'TEST_sleep'
            description: str = 'testing purposes: sleep'
            labels: ListAny = ['TEST']
            timeout_seconds: int = 600
            response_timeout_seconds: int = 600

        class WorkerInput(TaskInput):
            time: Optional[int]

            @field_validator('time')
            def time_validator(cls, value: int) -> int:
                if not 0 <= value <= TestWorkers.Sleep.MAX_SLEEP_TIME:
                    raise ValueError(f'Invalid sleep time, must be > 0 and < {TestWorkers.Sleep.MAX_SLEEP_TIME}')
                return value

        class WorkerOutput(TaskOutput):
            time: int

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            if worker_input.time is not None:
                self.sleep = worker_input.time

            time.sleep(self.sleep)
            return TaskResult(
                status=TaskResultStatus.COMPLETED,
                logs=['Sleep worker invoked. Sleeping'],
                output=self.WorkerOutput(time=self.sleep)
            )

    class DynamicForkGenerator(WorkerImpl):
        class WorkerDefinition(TaskDefinition):
            name: str = 'TEST_dynamic_fork_generate'
            description: str = 'testing purposes: generate dynamic fork tasks'
            labels: ListAny = ['TEST']
            timeout_seconds: int = 60
            response_timeout_seconds: int = 60

        class WorkerInput(TaskInput):
            wf_count: int = 10
            wf_name: str = 'Test_workflow'
            wf_inputs: Optional[DictAny] = {}

        class WorkerOutput(TaskOutput):
            dynamic_tasks_i: DictAny
            dynamic_tasks: ListAny

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            wf_count = worker_input.wf_count
            wf_name = worker_input.wf_name
            wf_inputs = worker_input.wf_inputs
            dynamic_tasks = []
            dynamic_tasks_i = {}

            for task_ref in range(0, wf_count):
                dynamic_tasks.append(
                    {
                        'name': 'sub_task',
                        'taskReferenceName': str(task_ref),
                        'type': 'SUB_WORKFLOW',
                        'subWorkflowParam': {'name': wf_name, 'version': 1},
                    }
                )
                dynamic_tasks_i[str(task_ref)] = wf_inputs

            return TaskResult(
                status=TaskResultStatus.COMPLETED,
                logs=['Dynamic fork generator worker invoked successfully'],
                output=self.WorkerOutput(
                    dynamic_tasks_i=dynamic_tasks_i,
                    dynamic_tasks=dynamic_tasks
                )
            )

    class LoremIpsum(WorkerImpl):

        WORDS = ['lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing', 'elit']

        class WorkerDefinition(TaskDefinition):
            name: str = 'TEST_lorem_ipsum'
            description: str = 'testing purposes: text generator'
            labels: ListAny = ['TEST']
            timeout_seconds: int = 60
            response_timeout_seconds: int = 60

        class WorkerInput(TaskInput):
            num_paragraphs: int = 3
            num_sentences: int = 3
            num_words: int = 3

        class WorkerOutput(TaskOutput):
            text: str
            bytes: int

        @classmethod
        def generate_sentence(cls, num_words: int) -> str:
            sentence = []
            for i in range(num_words):
                sentence.append(random.choice(cls.WORDS))
            return ' '.join(sentence).capitalize() + '.'

        @classmethod
        def generate_paragraph(cls, num_sentences: int, num_words: int) -> str:
            paragraph = []
            for i in range(num_sentences):
                paragraph.append(cls.generate_sentence(num_words))
            return ' '.join(paragraph)

        @classmethod
        def generate_text(cls, num_paragraphs: int, num_sentences: int, num_words: int) -> str:
            text = []
            for i in range(num_paragraphs):
                text.append(cls.generate_paragraph(num_sentences, num_words))
            return '\n\n'.join(text)

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            text = self.generate_text(
                num_paragraphs=worker_input.num_paragraphs,
                num_sentences=worker_input.num_sentences,
                num_words=worker_input.num_words,
            )

            return TaskResult(
                status=TaskResultStatus.COMPLETED,
                logs=['Lorem ipsum worker invoked successfully'],
                output=self.WorkerOutput(
                    text=text,
                    bytes=len(text.encode('utf-8'))
                )
            )

    class Logs(WorkerImpl):
        class WorkerDefinition(TaskDefinition):
            name: str = 'TEST_logs'
            description: str = 'testing purposes: logging'
            labels: ListAny = ['TEST']
            timeout_seconds: int = 60
            response_timeout_seconds: int = 60

        class WorkerInput(TaskInput):
            ...

        class WorkerOutput(TaskOutput):
            ...

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:
            import logging

            from frinx.common.logging.root_logger import root_logger

            module_logger = logging.getLogger(__name__)

            module_logger.info('This is an INFO message from module_logger')
            module_logger.debug('This is a DEBUG message from module_logger')
            module_logger.warning('This is a WARNING message from module_logger')
            module_logger.error('This is an ERROR message from module_logger')

            root_logger.info('This is an INFO message from the root_logger')
            root_logger.debug('This is a DEBUG message from the root_logger')
            root_logger.warning('This is a WARNING message from the root_logger')
            root_logger.error('This is an ERROR message from the root_logger')

            return TaskResult(
                status=TaskResultStatus.COMPLETED,
                logs=['This is a log message from TaskResult.']
            )

    # TODO: Not currently used in any workflow or test
    # A new standalone workflow and test scenario should be created
    class SimulateRetryableErrorWorker(WorkerImpl):
        class WorkerDefinition(TaskDefinition):
            name: str = 'TEST_simulate_retryable_error'
            description: str = 'testing purposes: simulates a retryable error'
            labels: ListAny = ['TEST']
            timeout_seconds: int = 60
            response_timeout_seconds: int = 60

        class WorkerInput(TaskInput):
            ...

        class WorkerOutput(TaskOutput):
            output: str

        def execute(self, worker_input: WorkerInput) -> TaskResult[WorkerOutput]:

            def fail_three_times() -> None:
                """
                Simulates three consecutive failures by using an environment variable to track attempts.
                Raises an exception on the first three executions and succeeds on the fourth.
                """
                env_var_name: str = f'{self.__class__.__name__}_attempt_count'
                attempt_count: int = int(os.getenv(env_var_name, '0'))

                try:
                    if attempt_count < 3:  # noqa: PLR2004
                        os.environ[env_var_name] = str(attempt_count + 1)
                        raise RuntimeError('Simulated failure')
                    else:
                        os.environ.pop(env_var_name, None)
                except RuntimeError as e:
                    raise RetryOnExceptionError(e, max_retries=5, retry_delay_seconds=5)

            fail_three_times()

            return TaskResult(
                status=TaskResultStatus.COMPLETED,
                output=self.WorkerOutput(output='passed')
            )
