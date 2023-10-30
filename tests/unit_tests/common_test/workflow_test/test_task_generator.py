from typing import Any

from frinx.common.conductor_enums import SwitchEvaluatorType
from frinx.common.conductor_enums import WorkflowStatus
from frinx.common.workflow import task
from frinx.common.workflow.task import TaskType
from frinx.common.workflow.task import WorkflowTaskImpl
from tests.unit_tests.conftest import MockWorker
from tests.unit_tests.conftest import MockWorkflow


class TestTaskGenerator:
    def test_decision_task(self) -> None:
        test_task = task.DecisionTask(
            type=TaskType.DECISION,
            name='decision',
            task_reference_name='decision',
            decision_cases={
                'true': [task.HumanTask(type=TaskType.HUMAN, name='human', task_reference_name='human')]
            },
            default_case=[
                task.TerminateTask(
                    type=TaskType.TERMINATE,
                    name='terminate',
                    task_reference_name='terminate',
                    input_parameters=task.TerminateTaskInputParameters(
                        termination_status=WorkflowStatus.FAILED,
                        termination_reason=None,
                        workflow_output=None
                    ),
                )
            ],
            input_parameters=task.DecisionTaskInputParameters(
                root=dict(
                    status='${workflow.input.status}'
                )
            ),
            case_expression="$.status === 'true' ? 'true' : 'False'",
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'decision',
            'task_reference_name': 'decision',
            'type': 'DECISION',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [
                {
                    'name': 'terminate',
                    'task_reference_name': 'terminate',
                    'type': 'TERMINATE',
                    'start_delay': 0,
                    'optional': False,
                    'async_complete': False,
                    'default_case': [],
                    'input_parameters': {'termination_status': 'FAILED'},
                }
            ],
            'input_parameters': {'status': '${workflow.input.status}'},
            'case_expression': "$.status === 'true' ? 'true' : 'False'",
            'decision_cases': {
                'true': [
                    {
                        'name': 'human',
                        'task_reference_name': 'human',
                        'type': 'HUMAN',
                        'start_delay': 0,
                        'optional': False,
                        'async_complete': False,
                        'default_case': [],
                        'input_parameters': {},
                    }
                ]
            },
        }

        assert test_mock == test_task

    def test_decision_case_value_task(self) -> None:
        test_task = task.DecisionCaseValueTask(
            type=TaskType.DECISION,
            name='decision',
            task_reference_name='decision',
            decision_cases={
                'true': [task.HumanTask(type=TaskType.HUMAN, name='human', task_reference_name='human')]
            },
            default_case=[
                task.TerminateTask(
                    type=TaskType.TERMINATE,
                    name='terminate',
                    task_reference_name='terminate',
                    input_parameters=task.TerminateTaskInputParameters(
                        termination_status=WorkflowStatus.FAILED,
                        termination_reason=None,
                        workflow_output=None
                    ),
                )
            ],
            input_parameters=task.DecisionCaseValueTaskInputParameters(
                case_value_param='${workflow.input.status}'
            ),
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'decision',
            'task_reference_name': 'decision',
            'type': 'DECISION',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [
                {
                    'name': 'terminate',
                    'task_reference_name': 'terminate',
                    'type': 'TERMINATE',
                    'start_delay': 0,
                    'optional': False,
                    'async_complete': False,
                    'default_case': [],
                    'input_parameters': {'termination_status': 'FAILED'},
                }
            ],
            'input_parameters': {'case_value_param': '${workflow.input.status}'},
            'case_value_param': 'case_value_param',
            'decision_cases': {
                'true': [
                    {
                        'name': 'human',
                        'task_reference_name': 'human',
                        'type': 'HUMAN',
                        'start_delay': 0,
                        'optional': False,
                        'async_complete': False,
                        'default_case': [],
                        'input_parameters': {},
                    }
                ]
            },
        }

        assert test_mock == test_task

    def test_do_while_task(self) -> None:
        loop_tasks = task.WaitDurationTask(
            type=TaskType.WAIT,
            name='wait',
            task_reference_name='wait',
            input_parameters=task.WaitDurationTaskInputParameters(duration='1 seconds'),
        )

        test_task = task.DoWhileTask(
            type=TaskType.DO_WHILE,
            name='do_while',
            task_reference_name='LoopTask',
            loop_condition="if ( $.LoopTask['iteration'] < $.value ) { true; } else { false; }",
            loop_over=[loop_tasks],
            input_parameters={'value': 'value'},
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'do_while',
            'task_reference_name': 'LoopTask',
            'type': 'DO_WHILE',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {'value': 'value'},
            'loop_condition': "if ( $.LoopTask['iteration'] < $.value ) { true; } else { false; }",
            'loop_over': [
                {
                    'name': 'wait',
                    'task_reference_name': 'wait',
                    'type': 'WAIT',
                    'start_delay': 0,
                    'optional': False,
                    'async_complete': False,
                    'default_case': [],
                    'input_parameters': {'duration': '1 seconds'},
                }
            ],
            'evaluator_type': 'javascript',
        }

        assert test_mock == test_task

    def test_dyn_fork_arrays_def_task(self) -> None:
        workflow_input = MockWorkflow.WorkflowInput()

        fork_inputs: list[dict[object, str]] = [
            {workflow_input.device_name.name: 'IOS01'},
            {workflow_input.device_name.name: 'IOS02'},
            {workflow_input.device_name.name: 'IOS02'},
        ]

        test_task = task.DynamicForkTask(
            type=TaskType.FORK_JOIN_DYNAMIC,
            name='dyn_fork',
            task_reference_name='dyn_fork',
            input_parameters=task.DynamicForkArraysTaskFromDefInputParameters(
                fork_task_name=MockWorkflow,
                fork_task_inputs=fork_inputs,
            ),
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'dyn_fork',
            'task_reference_name': 'dyn_fork',
            'type': 'FORK_JOIN_DYNAMIC',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {
                'fork_task_name': 'MockWorkflow',
                'fork_task_inputs': [
                    {'device_name': 'IOS01'},
                    {'device_name': 'IOS02'},
                    {'device_name': 'IOS02'},
                ],
            },
            'dynamic_fork_tasks_param': 'dynamicTasks',
            'dynamic_fork_tasks_input_param_name': 'dynamicTasksInput',
        }

        assert test_mock == test_task

    def test_dyn_fork_arrays_task(self) -> None:
        workflow_input = MockWorkflow.WorkflowInput()

        fork_inputs = [
            {workflow_input.device_name.name: 'IOS01'},
            {workflow_input.device_name.name: 'IOS02'},
            {workflow_input.device_name.name: 'IOS02'},
        ]

        input_parameters = task.DynamicForkArraysTaskInputParameters(
            fork_task_name='MockWorkflow', fork_task_inputs=fork_inputs
        )

        test_task = task.DynamicForkTask(
            type=TaskType.FORK_JOIN_DYNAMIC,
            name='dyn_fork',
            task_reference_name='dyn_fork',
            input_parameters=input_parameters,
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'dyn_fork',
            'task_reference_name': 'dyn_fork',
            'type': 'FORK_JOIN_DYNAMIC',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {
                'fork_task_name': 'MockWorkflow',
                'fork_task_inputs': [
                    {'device_name': 'IOS01'},
                    {'device_name': 'IOS02'},
                    {'device_name': 'IOS02'},
                ],
            },
            'dynamic_fork_tasks_param': 'dynamicTasks',
            'dynamic_fork_tasks_input_param_name': 'dynamicTasksInput',
        }

        assert test_mock == test_task

    def test_dyn_fork_def_task(self) -> None:
        input_parameters = task.DynamicForkTaskFromDefInputParameters(
            dynamic_tasks=MockWorkflow,
            dynamic_tasks_input='${workflow.input.device_name}',
        )

        test_task = task.DynamicForkTask(
            type=TaskType.FORK_JOIN_DYNAMIC,
            name='dyn_fork',
            task_reference_name='dyn_fork',
            input_parameters=input_parameters,
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'dyn_fork',
            'task_reference_name': 'dyn_fork',
            'type': 'FORK_JOIN_DYNAMIC',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {
                'dynamic_tasks': 'MockWorkflow',
                'dynamic_tasks_input': '${workflow.input.device_name}',
            },
            'dynamic_fork_tasks_param': 'dynamicTasks',
            'dynamic_fork_tasks_input_param_name': 'dynamicTasksInput',
        }

        assert test_mock == test_task

    def test_dyn_fork_task(self) -> None:
        input_parameters = task.DynamicForkTaskInputParameters(
            dynamic_tasks='Install_device_by_name',
            dynamic_tasks_input='${workflow.input.device_name}',
        )

        test_task = task.DynamicForkTask(
            type=TaskType.FORK_JOIN_DYNAMIC,
            name='dyn_fork',
            task_reference_name='dyn_fork',
            input_parameters=input_parameters,
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'dyn_fork',
            'task_reference_name': 'dyn_fork',
            'type': 'FORK_JOIN_DYNAMIC',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {
                'dynamic_tasks': 'Install_device_by_name',
                'dynamic_tasks_input': '${workflow.input.device_name}',
            },
            'dynamic_fork_tasks_param': 'dynamicTasks',
            'dynamic_fork_tasks_input_param_name': 'dynamicTasksInput',
        }

        assert test_mock == test_task

    def test_event_task(self) -> None:
        test_task = task.EventTask(
            type=TaskType.EVENT,
            name='Event',
            task_reference_name='event_a',
            sink='conductor:Wait_task',
            async_complete=False,
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'Event',
            'task_reference_name': 'event_a',
            'type': 'EVENT',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {},
            'sink': 'conductor:Wait_task',
        }

        assert test_mock == test_task

    def test_exclusive_join_task(self) -> None:
        test_task = task.ExclusiveJoinTask(
            type=TaskType.EXCLUSIVE_JOIN,
            name='exclusive_join',
            task_reference_name='exclusive_join',
            join_on=['wf1', 'wf2'],
            optional=True,
            start_delay=30,
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'exclusive_join',
            'task_reference_name': 'exclusive_join',
            'type': 'EXCLUSIVE_JOIN',
            'start_delay': 30,
            'optional': True,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {},
            'join_on': ['wf1', 'wf2'],
        }

        assert test_mock == test_task

    def test_fork_task(self) -> None:
        fork_tasks_a: list[WorkflowTaskImpl] = []
        fork_tasks_b: list[WorkflowTaskImpl] = []

        fork_tasks_a.append(
            task.SimpleTask(
                type=TaskType.SIMPLE,
                name=MockWorker,
                task_reference_name='add_device_cli',
                input_parameters=task.SimpleTaskInputParameters(
                    root=dict(
                        device_name='IOS01',
                        zone='uniconfig',
                        service_state='IN_SERVICE',
                        mount_body='body'
                    )
                )
            )
        )

        fork_tasks_a.append(
            task.SimpleTask(
                type=TaskType.SIMPLE,
                name=MockWorker,
                task_reference_name='install_device_cli',
                input_parameters=task.SimpleTaskInputParameters(
                    root=dict(
                        device_name='IOS01'
                    )
                )
            )
        )

        fork_tasks_b.append(
            task.SimpleTask(
                type=TaskType.SIMPLE,
                name=MockWorker,
                task_reference_name='add_device',
                input_parameters=task.SimpleTaskInputParameters(
                    root=dict(
                        device_name='NTF01',
                        zone='uniconfig',
                        service_state='IN_SERVICE',
                        mount_body='body'
                    )
                )
            )
        )

        fork_tasks_b.append(
            task.SimpleTask(
                type=TaskType.SIMPLE,
                name=MockWorker,
                task_reference_name='install_device_netconf',
                input_parameters=task.SimpleTaskInputParameters(
                    root=dict(
                        device_name='NTF01'
                    )
                )
            )
        )

        test_task = task.ForkTask(
            type=TaskType.FORK_JOIN,
            name='fork',
            task_reference_name='fork',
            fork_tasks=[fork_tasks_a, fork_tasks_b],
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'fork',
            'task_reference_name': 'fork',
            'type': 'FORK_JOIN',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {},
            'fork_tasks': [
                [
                    {
                        'name': 'MockWorker',
                        'task_reference_name': 'add_device_cli',
                        'type': 'SIMPLE',
                        'start_delay': 0,
                        'optional': False,
                        'async_complete': False,
                        'default_case': [],
                        'input_parameters': {
                            'zone': 'uniconfig',
                            'device_name': 'IOS01',
                            'mount_body': 'body',
                            'service_state': 'IN_SERVICE',
                        },
                    },
                    {
                        'name': 'MockWorker',
                        'task_reference_name': 'install_device_cli',
                        'type': 'SIMPLE',
                        'start_delay': 0,
                        'optional': False,
                        'async_complete': False,
                        'default_case': [],
                        'input_parameters': {'device_name': 'IOS01'},
                    },
                ],
                [
                    {
                        'name': 'MockWorker',
                        'task_reference_name': 'add_device',
                        'type': 'SIMPLE',
                        'start_delay': 0,
                        'optional': False,
                        'async_complete': False,
                        'default_case': [],
                        'input_parameters': {
                            'zone': 'uniconfig',
                            'device_name': 'NTF01',
                            'mount_body': 'body',
                            'service_state': 'IN_SERVICE',
                        },
                    },
                    {
                        'name': 'MockWorker',
                        'task_reference_name': 'install_device_netconf',
                        'type': 'SIMPLE',
                        'start_delay': 0,
                        'optional': False,
                        'async_complete': False,
                        'default_case': [],
                        'input_parameters': {'device_name': 'NTF01'},
                    },
                ],
            ],
        }

        assert test_mock == test_task

    def test_human_task(self) -> None:
        test_task = task.HumanTask(type=TaskType.HUMAN, name='human', task_reference_name='human').model_dump(
            exclude_none=True
        )

        test_mock = {
            'name': 'human',
            'task_reference_name': 'human',
            'type': 'HUMAN',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {},
        }

        assert test_mock == test_task

    def test_inline_task(self) -> None:
        test_task = task.InlineTask(
            type=TaskType.INLINE,
            name='inline',
            task_reference_name='inline',
            input_parameters=task.InlineTaskInputParameters(
                expression='if ($.value){return {"result": true}} else { return {"result": false}}',
                value='${workflow.variables.test}',
            ),
        ).model_dump(exclude_none=True)

        input_parameters_exp = (
            'function e() { if ($.value){return {"result": true}} else { return {"result": false}} } e();'
        )

        test_mock = {
            'name': 'inline',
            'task_reference_name': 'inline',
            'type': 'INLINE',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {
                'evaluator_type': 'javascript',
                'expression': input_parameters_exp,
                'value': '${workflow.variables.test}',
            },
        }

        assert test_mock == test_task

    def test_inline_func_task(self) -> None:
        input_parameters_exp = (
            'function e() { if ($.value){return {"result": true}} else { return {"result": false}} } e();'
        )

        test_task = task.InlineTask(
            type=TaskType.INLINE,
            name='inline',
            task_reference_name='inline',
            input_parameters=task.InlineTaskInputParameters(
                expression=input_parameters_exp,
                value='${workflow.variables.test}',
            ),
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'inline',
            'task_reference_name': 'inline',
            'type': 'INLINE',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {
                'evaluator_type': 'javascript',
                'expression': input_parameters_exp,
                'value': '${workflow.variables.test}',
            },
        }

        assert test_mock == test_task

    def test_join_task(self) -> None:
        test_task = task.JoinTask(type=TaskType.JOIN, name='join', task_reference_name='join').model_dump(
            exclude_none=True
        )

        test_mock = {
            'name': 'join',
            'task_reference_name': 'join',
            'type': 'JOIN',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {},
            'join_on': [],
        }

        assert test_mock == test_task

    def test_json_jq_task(self) -> None:
        test_task = task.JsonJqTask(
            type=TaskType.JSON_JQ_TRANSFORM,
            name='json_jq',
            task_reference_name='json_jq',
            input_parameters=task.JsonJqTaskInputParameters(
                query_expression='{ key3: (.key1.value1) }',
                key_1={'value1': ['a', 'b']},
            ),
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'json_jq',
            'task_reference_name': 'json_jq',
            'type': 'JSON_JQ_TRANSFORM',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {
                'query_expression': '{ key3: (.key1.value1) }',
                'key_1': {'value1': ['a', 'b']},
            },
        }

        assert test_mock == test_task

    def test_set_variable_task(self) -> None:
        test_task = task.SetVariableTask(
            type=TaskType.SET_VARIABLE,
            name='var',
            task_reference_name='var',
            input_parameters=task.SetVariableTaskInputParameters(root=dict(env='frinx')),
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'var',
            'task_reference_name': 'var',
            'type': 'SET_VARIABLE',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {'env': 'frinx'},
        }

        assert test_mock == test_task

    def test_simple_task(self) -> None:
        test_task = task.SimpleTask(
            type=TaskType.SIMPLE,
            name=MockWorker,
            task_reference_name='test',
            input_parameters=task.SimpleTaskInputParameters(
                root=dict(
                    device_name='IOS01',
                    zone='uniconfig',
                    service_state='IN_SERVICE',
                    mount_body='body',
                )
            ),
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'MockWorker',
            'task_reference_name': 'test',
            'type': 'SIMPLE',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {
                'device_name': 'IOS01',
                'zone': 'uniconfig',
                'mount_body': 'body',
                'service_state': 'IN_SERVICE',
            },
        }

        assert test_mock == test_task

    def test_start_workflow_from_def_task(self) -> None:
        workflow_input_parameters: dict[str, object] = {
            MockWorkflow.WorkflowInput().device_name.name: 'IOS01'
        }

        task_inputs = task.StartWorkflowTaskInputParameters(
            start_workflow=task.StartWorkflowTaskFromDefInputParameters(
                workflow=MockWorkflow,
                input=workflow_input_parameters,
                correlationId=None
            )
        )

        test_task = task.StartWorkflowTask(
            type=TaskType.START_WORKFLOW,
            name='MockWorkflow',
            task_reference_name='start',
            input_parameters=task_inputs,
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'MockWorkflow',
            'task_reference_name': 'start',
            'type': 'START_WORKFLOW',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {
                'start_workflow': {
                    'name': 'MockWorkflow',
                    'version': 1,
                    'input': {'device_name': 'IOS01'},
                }
            },
        }

        assert test_mock == test_task

    def test_start_workflow_plain_task(self) -> None:
        workflow_input_parameters: dict[str, object] = {
            MockWorkflow.WorkflowInput().device_name.name: 'IOS01'
        }

        task_inputs = task.StartWorkflowTaskInputParameters(
            start_workflow=task.StartWorkflowTaskPlainInputParameters(
                name='MockWorkflow',
                version=1,
                input=workflow_input_parameters,
                correlationId=None
            )
        )

        test_task = task.StartWorkflowTask(
            type=TaskType.START_WORKFLOW,
            name='MockWorkflow',
            task_reference_name='start',
            input_parameters=task_inputs,
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'MockWorkflow',
            'task_reference_name': 'start',
            'type': 'START_WORKFLOW',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {
                'start_workflow': {
                    'name': 'MockWorkflow',
                    'version': 1,
                    'input': {'device_name': 'IOS01'},
                }
            },
        }

        assert test_mock == test_task

    def test_sub_workflow_task(self) -> None:
        sub_workflow_param = task.SubWorkflowParam(
            name=MockWorkflow.__name__, version=1
        )

        workflow_input = MockWorkflow.WorkflowInput()

        sub_workflow_input: dict[str, Any] = {}
        sub_workflow_input.setdefault(workflow_input.device_name.name, 'IOS01')
        sub_workflow_input.setdefault(workflow_input.zone.name, 'uniconfig')

        test_task = task.SubWorkflowTask(
            type=TaskType.SUB_WORKFLOW,
            name='subworkflow',
            task_reference_name='subworkflow',
            sub_workflow_param=sub_workflow_param,
            input_parameters=task.SubWorkflowInputParameters(root=sub_workflow_input),
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'subworkflow',
            'task_reference_name': 'subworkflow',
            'type': 'SUB_WORKFLOW',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {'device_name': 'IOS01', 'zone': 'uniconfig'},
            'sub_workflow_param': {'name': 'MockWorkflow', 'version': 1},
        }

        assert test_mock == test_task

    def test_switch_value_param_task(self) -> None:
        test_task = task.SwitchTask(
            type=TaskType.SWITCH,
            name='switch',
            task_reference_name='switch',
            decision_cases={
                'true': [
                    task.WaitDurationTask(
                        type=TaskType.WAIT,
                        name='wait',
                        task_reference_name='wait1',
                        input_parameters=task.WaitDurationTaskInputParameters(
                            duration='10 seconds'
                        ),
                    )
                ]
            },
            default_case=[
                task.WaitDurationTask(
                    type=TaskType.WAIT,
                    name='wait',
                    task_reference_name='wait2',
                    input_parameters=task.WaitDurationTaskInputParameters(
                        duration='10 seconds'
                    ),
                )
            ],
            expression='switch_case_value',
            evaluator_type=SwitchEvaluatorType.VALUE_PARAM,
            input_parameters=task.SwitchTaskValueParamInputParameters(
                switch_case_value='${workflow.input.value}'
            ),
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'switch',
            'task_reference_name': 'switch',
            'type': 'SWITCH',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [
                {
                    'name': 'wait',
                    'task_reference_name': 'wait2',
                    'type': 'WAIT',
                    'start_delay': 0,
                    'optional': False,
                    'async_complete': False,
                    'default_case': [],
                    'input_parameters': {'duration': '10 seconds'},
                }
            ],
            'input_parameters': {'switch_case_value': '${workflow.input.value}'},
            'decision_cases': {
                'true': [
                    {
                        'name': 'wait',
                        'task_reference_name': 'wait1',
                        'type': 'WAIT',
                        'start_delay': 0,
                        'optional': False,
                        'async_complete': False,
                        'default_case': [],
                        'input_parameters': {'duration': '10 seconds'},
                    }
                ]
            },
            'evaluator_type': 'value-param',
            'expression': 'switch_case_value',
        }

        assert test_mock == test_task

    def test_switch_javascript_task(self) -> None:
        test_task = task.SwitchTask(
            type=TaskType.SWITCH,
            name='switch',
            task_reference_name='switch',
            decision_cases={
                'true': [
                    task.WaitDurationTask(
                        type=TaskType.WAIT,
                        name='wait',
                        task_reference_name='wait1',
                        input_parameters=task.WaitDurationTaskInputParameters(
                            duration='10 seconds'
                        ),
                    )
                ]
            },
            default_case=[
                task.WaitDurationTask(
                    type=TaskType.WAIT,
                    name='wait',
                    task_reference_name='wait2',
                    input_parameters=task.WaitDurationTaskInputParameters(
                        duration='10 seconds'
                    ),
                )
            ],
            expression="$.inputValue == 'true' ? 'true' : 'false'",
            evaluator_type=SwitchEvaluatorType.JAVASCRIPT,
            input_parameters=task.SwitchTaskInputParameters(
                input_value='${workflow.input.value}'
            ),
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'switch',
            'task_reference_name': 'switch',
            'type': 'SWITCH',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [
                {
                    'name': 'wait',
                    'task_reference_name': 'wait2',
                    'type': 'WAIT',
                    'start_delay': 0,
                    'optional': False,
                    'async_complete': False,
                    'default_case': [],
                    'input_parameters': {'duration': '10 seconds'},
                }
            ],
            'input_parameters': {'input_value': '${workflow.input.value}'},
            'decision_cases': {
                'true': [
                    {
                        'name': 'wait',
                        'task_reference_name': 'wait1',
                        'type': 'WAIT',
                        'start_delay': 0,
                        'optional': False,
                        'async_complete': False,
                        'default_case': [],
                        'input_parameters': {'duration': '10 seconds'},
                    }
                ]
            },
            'evaluator_type': 'javascript',
            'expression': "$.inputValue == 'true' ? 'true' : 'false'",
        }

        assert test_mock == test_task

    def test_terminate_task(self) -> None:
        test_task = task.TerminateTask(
            type=TaskType.TERMINATE,
            name='terminate',
            task_reference_name='terminate',
            input_parameters=task.TerminateTaskInputParameters(
                termination_status=WorkflowStatus.COMPLETED,
                termination_reason=None,
                workflow_output={'output': 'COMPLETED'},
            ),
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'terminate',
            'task_reference_name': 'terminate',
            'type': 'TERMINATE',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {
                'termination_status': 'COMPLETED',
                'workflow_output': {'output': 'COMPLETED'},
            },
        }

        assert test_mock == test_task

    def test_wait_duration_task(self) -> None:
        test_task = task.WaitDurationTask(
            type=TaskType.WAIT,
            name='WAIT',
            task_reference_name='WAIT',
            input_parameters=task.WaitDurationTaskInputParameters(
                duration='10 seconds'
            ),
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'WAIT',
            'task_reference_name': 'WAIT',
            'type': 'WAIT',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {'duration': '10 seconds'},
        }

        assert test_mock == test_task

    def test_wait_until_task(self) -> None:
        test_task = task.WaitUntilTask(
            type=TaskType.WAIT,
            name='WAIT_UNTIL',
            task_reference_name='WAIT_UNTIL',
            input_parameters=task.WaitUntilTaskInputParameters(
                until='2022-12-25 09:00 PST'
            ),
        ).model_dump(exclude_none=True)

        test_mock = {
            'name': 'WAIT_UNTIL',
            'task_reference_name': 'WAIT_UNTIL',
            'type': 'WAIT',
            'start_delay': 0,
            'optional': False,
            'async_complete': False,
            'default_case': [],
            'input_parameters': {'until': '2022-12-25 09:00 PST'},
        }

        assert test_mock == test_task
