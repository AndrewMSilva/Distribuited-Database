#!/bin/bash

SCRIPT_TO_EXECUTE='DRBD'
SCRIPT_TO_EXECUTE_PLUS_ARGS="DRBD.py -m -r"
OUTPUT_PID_FILE=running.pid
OUTPUT_PID_PATH=.
PYTHON_TO_USE="$python3"

echo "Starting $SCRIPT_TO_EXECUTE..."

# If the .pid file doesn't exist (let's assume no processes are running)...
if [ ! -e "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE" ]; then
	echo "$SCRIPT_TO_EXECUTE is not running!"
else
	# If the running.pid exists, read it & try to kill the process if it exists, then delete it.
    the_pid=$(<$OUTPUT_PID_PATH/$OUTPUT_PID_FILE)

	rm "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"

	kill "$the_pid"
	COUNTER=1
	while [ -e /proc/$the_pid ]
	do
	    echo "$SCRIPT_TO_EXECUTE still running"
	    sleep .7
	    COUNTER=$[$COUNTER +1]
	    if [ $COUNTER -eq 20 ]; then
	    	kill -9 "$the_pid"

	    fi
	    if [ $COUNTER -eq 40 ]; then
	    	exit 1
	    fi
	done
	echo "$SCRIPT_TO_EXECUTE has finished"
fi

exit 0