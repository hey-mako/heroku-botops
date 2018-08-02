import json
import os
import subprocess

from celery import Celery
from flask import Flask, jsonify, request
from pymongo import MongoClient


application = Flask(__name__)
application.config.update(
    BROKER_URL=os.getenv('BROKER_URL'),
    CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND')
)

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
def resources():
    data = request.get_json(force=True)
    collection = database.resources
    document = collection.find_one(filter={'uuid': data['uuid']})
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
