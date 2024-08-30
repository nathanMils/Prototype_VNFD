#!/bin/bash

# NF Variables
EXTERNAL_INTERFACE="ens3"           # Interface assigned to the external network

# DNS Name resolution
ELK_IP=$2
NRF_IP=$3
MYSQL_IP=$4

# Update hosts for DNS Name resolution
echo "$ELK_IP elasticsearch" >> /etc/hosts
echo "$ELK_IP logstash" >> /etc/hosts
echo "$NRF_IP oai-nrf" >> /etc/hosts
echo "$MYSQL_IP mysql" >> /etc/hosts

ELK_GATEWAY=$5

# Add routing via elk network to not disturb NF
sudo ip route add $ELK_IP via $ELK_GATEWAY

# Exporting required vars
export FILEBEAT_INTERNAL_PASSWORD=$6
export BEATS_SYSTEM_PASSWORD=$7

# Starting containers and networks
TARGET_DIR=/opt/amf
docker load -i $TARGET_DIR/amf-images.tar
docker compose -f $TARGET_DIR/docker-compose-amf-built.yml up -d