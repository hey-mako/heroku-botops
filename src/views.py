from flask import (
    g,
    redirect,
    request,
    url_for,
)
from functools import wraps
from . import application


def authenticate(route):
    """authenticate is a view decorator for authenticating requests."""
    @wraps(route)
    def inner(*args, **kwargs):
        header = request.headers.get('Authorization')
        if header is None:
            return '', 401
        return route(*args, **kwargs)
    return inner


@application.route('/heroku/resources', methods=['POST'])
@authenticate
def index():
    return '', 200
