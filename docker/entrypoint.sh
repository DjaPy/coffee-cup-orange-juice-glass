#! /usr/bin/env bash
set -e

/wait-for-it.sh $DB_SERVER:5432 -t 5
retVal=$?
if [ $retVal -ne 0 ]; then
    exit $retVal
fi

# If there's a prestart.sh script in the /app directory or other path specified, run it before starting
PRE_START_PATH=${PRE_START_PATH:-/prestart.sh}
echo "Checking for script in $PRE_START_PATH"
if [ -f $PRE_START_PATH ] ; then
    echo "Running script $PRE_START_PATH"
    . "$PRE_START_PATH"
else 
    echo "There is no script $PRE_START_PATH"
fi

exec python -m app.main