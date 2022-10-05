from functools import wraps

from jsonschema.validators import validate
from werkzeug.exceptions import abort
from jsonschema.exceptions import ValidationError


def print_result(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        print(result)
        return result

    return wrapper


def body_validate(schema):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                validate(kwargs.get('body'), schema)
            except ValidationError:
                abort(400, "Parameters not valid")
            return function(*args, **kwargs)

        return wrapper

    return decorator
