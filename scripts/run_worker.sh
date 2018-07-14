#!/bin/bash
#
# run_worker.sh

set -e

application="$1"

# Start a celery worker process.
/usr/local/bin/celery -A "$application" worker > /dev/null 2>&1 &

exit 0
