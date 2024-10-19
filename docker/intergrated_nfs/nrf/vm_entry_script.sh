#!/bin/bash

# DNS Name resolution
ELK_IP=$1
NRF_IP=$2
MYSQL_IP=$3

# Update hosts for DNS Name resolution
echo "$ELK_IP elasticsearch" >> /etc/hosts
echo "$ELK_IP logstash" >> /etc/hosts
echo "$NRF_IP oai-nrf" >> /etc/hosts
echo "$MYSQL_IP mysql" >> /etc/hosts

ELK_GATEWAY=$4

# Add routing via elk network to not disturb NF
sudo ip route add $ELK_IP via $ELK_GATEWAY

# Exporting required vars
export FILEBEAT_INTERNAL_PASSWORD=$5
export BEATS_SYSTEM_PASSWORD=$6
export INTERFACE="ens3"

# Starting containers and networks
TARGET_DIR=/opt/smf
docker load -i $TARGET_DIR/smf-images.tar
docker compose -f $TARGET_DIR/docker-compose-smf-built.yml up -d