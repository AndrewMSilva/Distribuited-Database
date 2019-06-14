#!/bin/bash
TITLE='DRDB'
SCRIPT_TO_EXECUTE='Service'
SCRIPT_TO_EXECUTE_PLUS_ARGS="$SCRIPT_TO_EXECUTE.py -m -r"
PYTHON_TO_USE="python3"

echo "Starting $TITLE..."

pgrep -x $SCRIPT_TO_EXECUTE
if [ $? -eq 0 ]; then
    $PYTHON_TO_USE $SCRIPT_TO_EXECUTE_PLUS_ARGS
else
    echo "$TITLE is already running!"
fi

exit 0