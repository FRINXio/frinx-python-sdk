from pydantic.errors import JsonError


class InvalidJSONError(JsonError):
    def __init__(self, error_args):
        super().__init__()
        error_args = '\n'.join(error_args)
        self.msg_template = f'{self.msg_template}: {error_args}'
