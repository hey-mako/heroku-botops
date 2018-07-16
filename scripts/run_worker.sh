#!/bin/bash
#
# run_worker.sh

set -e

application="$1"

panic() {
  echo "$1"
  exit 1
}

if [ -z "$application" ]; then
  panic 'main: a celery project is required'
fi

# Start a celery worker process.
/usr/local/bin/celery -A "$application" worker -D --pidfile "$HOME/%n.pid"

# Start the flask application.
/usr/local/bin/flask run

# Terminate all worker processes forked by celery.
trap $(ps aux | grep -v grep | grep 'celery worker' | awk '{print $2}' | xargs kill -9) SIGINT

exit "$?"
