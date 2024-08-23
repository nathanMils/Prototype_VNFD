#!/bin/bash

# Exit on error
set -e

SERVICE="openvswitch-switch"

# Check if the service is running
if systemctl is-active --quiet $SERVICE; then
  echo "$SERVICE is already running."
else
  echo "$SERVICE is not running. Starting $SERVICE..."
  sudo systemctl start $SERVICE

  # Verify if the service started successfully
  if systemctl is-active --quiet $SERVICE; then
    echo "$SERVICE started successfully."
  else
    echo "Failed to start $SERVICE."
  fi
fi
