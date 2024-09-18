#!/bin/bash

# Define the ports to check
CHROME_DRIVER_PORT=9515
# Add any additional ports you want to check

# Function to check if a port is in use
is_port_in_use() {
    local port=$1
    netstat -tuln | grep ":$port " > /dev/null
    return $?
}

# Kill all Chrome processes
for pid in $(pgrep chrome); do
    echo "Killing Chrome process with PID: $pid"
    kill -9 $pid
done

# Kill all ChromeDriver processes
for pid in $(pgrep chromedriver); do
    echo "Killing ChromeDriver process with PID: $pid"
    kill -9 $pid
done

# Check if the ports are still in use and report
if is_port_in_use $CHROME_DRIVER_PORT; then
    echo "Port $CHROME_DRIVER_PORT is still in use."
else
    echo "Port $CHROME_DRIVER_PORT is free."
fi

# Add additional port checks as needed

echo "All Chrome and ChromeDriver processes have been terminated and ports checked."
