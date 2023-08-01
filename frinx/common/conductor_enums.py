from enum import Enum


class TaskResultStatus(str, Enum):
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    FAILED_WITH_TERMINAL_ERROR = 'FAILED_WITH_TERMINAL_ERROR'
    IN_PROGRESS = 'IN_PROGRESS'


class WorkflowStatus(str, Enum):
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    PAUSED = 'PAUSED'
    RUNNING = 'RUNNING'
    TERMINATED = 'TERMINATED'
    TIMED_OUT = 'TIMED_OUT'


class TimeoutPolicy(str, Enum):
    TIME_OUT_WORKFLOW = 'TIME_OUT_WF'
    ALERT_ONLY = 'ALERT_ONLY'


class SwitchEvaluatorType(str, Enum):
    JAVASCRIPT = 'javascript'
    VALUE_PARAM = 'value-param'


class DoWhileEvaluatorType(str, Enum):
    JAVASCRIPT = 'javascript'
    VALUE_PARAM = 'value-param'


class RetryLogic(str, Enum):
    FIXED = 'FIXED'
    EXPONENTIAL_BACKOFF = 'EXPONENTIAL_BACKOFF'
    LINEAR_BACKOFF = 'LINEAR_BACKOFF'


class HttpMethod(str, Enum):
    # CONNECT = 'CONNECT'
    # OPTIONS = 'OPTIONS'
    # TRACE = 'TRACE'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    HEAD = 'HEAD'
    POST = 'POST'
    PUT = 'PUT'
    GET = 'GET'


class ContentType(str, Enum):
    APPLICATION_JSON = 'application/json'
    APPLICATION_XML = 'application/xml'
    APPLICATION_X_WWW_FORM_URLENCODED = 'application/x-www-form-urlencoded'
    MULTIPART_FROM_DATA = 'multipart/form-data'
    TEXT_CSV = 'text/csv'
    TEXT_PLAIN = 'text/plain'
    TEXT_XML = 'text/xml'
