#!/bin/bash
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <host_port> <container_name>"
    exit 1
fi

HOST_PORT=$1
CONTAINER_NAME=$2
docker run -d -p "$HOST_PORT":1080 -v /opt/prototype_master/socks_server/sockd.conf:/etc/dante/sockd.conf --name "$CONTAINER_NAME" vimagick/dante