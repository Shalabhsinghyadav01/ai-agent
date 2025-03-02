#!/bin/bash

# Directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Create necessary directories
mkdir -p logs
mkdir -p .pid

# Function to start the agent
start_agent() {
    echo "Starting LinkedIn Agent..."
    # Run the scheduler in the background with nohup
    PYTHONPATH=src nohup python3 src/scheduler.py > logs/stdout.log 2> logs/stderr.log &
    
    # Store the PID
    echo $! > .pid/agent.pid
    echo "LinkedIn Agent started with PID: $!"
}

# Function to stop the agent
stop_agent() {
    echo "Stopping LinkedIn Agent..."
    if [ -f .pid/agent.pid ]; then
        PID=$(cat .pid/agent.pid)
        if ps -p $PID > /dev/null; then
            kill $PID
            echo "LinkedIn Agent stopped (PID: $PID)"
        else
            echo "Process not running"
        fi
        rm .pid/agent.pid
    else
        echo "PID file not found"
    fi
}

# Function to check agent status
status_agent() {
    if [ -f .pid/agent.pid ]; then
        PID=$(cat .pid/agent.pid)
        if ps -p $PID > /dev/null; then
            echo "LinkedIn Agent is running (PID: $PID)"
            echo "Recent logs:"
            tail -n 5 logs/linkedin_agent.log
        else
            echo "LinkedIn Agent is not running (stale PID file)"
            rm .pid/agent.pid
        fi
    else
        echo "LinkedIn Agent is not running"
    fi
}

# Parse command line arguments
case "$1" in
    start)
        start_agent
        ;;
    stop)
        stop_agent
        ;;
    restart)
        stop_agent
        sleep 2
        start_agent
        ;;
    status)
        status_agent
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0 