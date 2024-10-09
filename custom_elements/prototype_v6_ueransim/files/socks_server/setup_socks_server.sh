#!/bin/bash


PDU_SESSION_ID=$1
HOST_PORT=$2
CONTAINER_NAME=$3

/UERANSIM/build/nr-binder $PDU_SESSION_ID /opt/prototype_master/socks_server/run_server.sh $HOST_PORT $CONTAINER_NAME