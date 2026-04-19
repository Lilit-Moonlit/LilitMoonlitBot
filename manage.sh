#!/bin/bash

# Configuration
# Get the absolute path to the directory where the script is located
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv_linux"
PYTHON="$VENV_DIR/bin/python"
PID_FILE="$PROJECT_DIR/bot.pid"
LOG_FILE="$PROJECT_DIR/bot.log"
ENTRY_POINT="app.main"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

usage() {
    echo "Usage: $0 {start|stop|restart|status|logs}"
    exit 1
}

# Check if venv exists
if [ ! -f "$PYTHON" ]; then
    echo -e "${RED}Error: Virtual environment not found at $VENV_DIR${NC}"
    echo -e "Please create it first or check the PROJECT_DIR: $PROJECT_DIR"
    exit 1
fi

start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null; then
            echo -e "${YELLOW}Bot is already running (PID: $PID)${NC}"
            return
        else
            echo -e "${YELLOW}Warning: Found stale PID file. Removing it.${NC}"
            rm "$PID_FILE"
        fi
    fi

    echo -e "${GREEN}Starting Bot...${NC}"
    cd "$PROJECT_DIR"
    
    # Export PYTHONPATH to ensure app module is found
    export PYTHONPATH=$PROJECT_DIR
    
    nohup "$PYTHON" -m "$ENTRY_POINT" >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    sleep 1
    if ps -p $(cat "$PID_FILE") > /dev/null; then
        echo -e "${GREEN}Bot started with PID: $(cat $PID_FILE)${NC}"
        echo -e "Logs are being written to: $LOG_FILE"
    else
        echo -e "${RED}Error: Bot failed to start. Check $LOG_FILE for details.${NC}"
        rm "$PID_FILE"
    fi
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${YELLOW}Bot is not running (no PID file)${NC}"
        # Fallback check for any app.main process
        PID=$(pgrep -f "python.*-m $ENTRY_POINT")
        if [ ! -z "$PID" ]; then
            echo -e "${YELLOW}Found running bot process (PID: $PID) without PID file. Stopping...${NC}"
        else
            return
        fi
    else
        PID=$(cat "$PID_FILE")
    fi

    echo -e "${YELLOW}Stopping Bot (PID: $PID)...${NC}"
    kill $PID
    sleep 2
    if ps -p $PID > /dev/null; then
        echo -e "${RED}Bot still running. Force killing...${NC}"
        kill -9 $PID
    fi
    
    if [ -f "$PID_FILE" ]; then
        rm "$PID_FILE"
    fi
    echo -e "${GREEN}Bot stopped.${NC}"
}

status() {
    PID=$(pgrep -f "python.*-m $ENTRY_POINT")
    if [ ! -z "$PID" ]; then
        echo -e "${GREEN}Bot is running (PID: $PID)${NC}"
        if [ ! -f "$PID_FILE" ]; then
            echo -e "${YELLOW}Note: PID file is missing, but process is running.${NC}"
        fi
        echo -e "Last 5 lines of logs:"
        if [ -f "$LOG_FILE" ]; then
            tail -n 5 "$LOG_FILE"
        else
            echo "Log file not found."
        fi
    else
        echo -e "${RED}Bot is not running${NC}"
        if [ -f "$PID_FILE" ]; then
            echo -e "${YELLOW}Note: Stale PID file found. Cleaning up...${NC}"
            rm "$PID_FILE"
        fi
    fi
}

logs() {
    if [ ! -f "$LOG_FILE" ]; then
        echo -e "${RED}Log file not found: $LOG_FILE${NC}"
        return
    fi
    echo -e "${GREEN}Showing logs (Ctrl+C to stop)...${NC}"
    tail -f "$LOG_FILE"
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        start
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    *)
        usage
        ;;
esac
