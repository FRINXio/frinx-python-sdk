from enum import Enum


class HTTPMethod(str, Enum):
    # CONNECT = 'CONNECT'
    # OPTIONS = 'OPTIONS'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    # TRACE = 'TRACE'
    HEAD = 'HEAD'
    POST = 'POST'
    PUT = 'PUT'
    GET = 'GET'
