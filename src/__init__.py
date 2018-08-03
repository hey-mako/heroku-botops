import json
import os
import subprocess

from base64 import b64decode
from functools import wraps
from celery import Celery
from flask import Flask, jsonify, request
from pymongo import MongoClient


application = Flask(__name__)
application.config.update(
    BROKER_URL=os.getenv('BROKER_URL'),
    CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND')
)

filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'addon-manifest.json')

with open(filename) as f:
    manifest = json.load(f)


def login_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        header = request.headers.get('Authorization')
        if header is None:
            return '', 401
        header = header.split()[-1]
        user, password = b64decode(header.encode()).decode().split(':')
        if not (user == manifest['id'] and password == manifest['api']['password']):
            return '', 401
        return f(*args, **kwargs)
    return inner


# TODO: Use an environment variable for the connection URI.
client = MongoClient('mongo', 27017)
database = client.heroku


def make_celery(application):
    celery = Celery(
        application.import_name,
        backend=application.config['CELERY_RESULT_BACKEND'],
        broker=application.config['BROKER_URL']
    )
    celery.conf.update(application.config)

    class ContextTask(celery.Task):

        def __call__(self, *args, **kwargs):
            with application.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(application)


@celery.task
def provision():
    command = '/usr/local/bin/ansible-playbook -i localhost, scripts/main.yml'.split()
    result = subprocess.run(
        command,
        check=True,
        env={'ANSIBLE_STDOUT_CALLBACK': 'json'},
        stdout=subprocess.PIPE
    )
    return json.loads(result.stdout.decode('UTF-8'))


@application.route('/heroku/resources', methods=['POST'])
@login_required
def resources():
    data = request.get_json(force=True)
    collection = database.resources
    document = collection.find_one({'uuid': data['uuid']})
    # See https://goo.gl/3Y83zz
    if document is not None:
        task = provision.AsyncResult(document['task_id'])
        return jsonify({
            'result': task.result,
            'state': task.state
        }), 200
    result = provision.delay()
    # Add the `task_id` key to the `data` object.
    data['task_id'] = result.id
    collection.insert_one(data)
    return jsonify({'id': result.id}), 202


@application.route('/heroku/resources/<heroku_uuid>', methods=['PUT'])
@login_required
def plan(heroku_uuid):
    data = request.get_json(force=True)
    collection = database.resources
    # Returns the original document before it was updated, or None if no
    # document matches.
    document = collection.find_one_and_update(
        {'task_id': heroku_uuid},
        {'$set': {'plan': data['plan']}}
    )
    if document is None:
        return '', 404
    return '', 200

@application.route('/heroku/resources/<heroku_uuid>', methods=['DELETE'])
@login_required
def delete(heroku_uuid):
    collection = database.resources
    filter = {'task_id': heroku_uuid}
    collection.find_one_and_delete(filter)
    count = collection.count(filter)
    if count != 0:
        return '', 400
    return '', 204

