#!/bin/bash

# NF Variables
VM_EXTERNAL_IP=$1                   # VM's external IP
GATEWAY_IP="172.18.0.2"             # IP of the gateway container in its network
INTERNAL_CONTAINER_IP="172.20.0.3"  # IP of the internal container
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
TARGET_DIR=/opt/ausf
docker load -i $TARGET_DIR/ausf-images.tar
docker compose -f $TARGET_DIR/docker-compose-ausf-built.yml up -d

# Enable IP forwarding
echo "Enabling IP forwarding"
echo 1 > /proc/sys/net/ipv4/ip_forward

# HOST/EXTERNAL <--> GATEWAY/ZEEK <--> NF
###################################################################################################################
# DNAT to forward all traffic to the internal container via the gateway container
echo "Setting up DNAT to forward traffic to the internal container"
sudo iptables -t nat -A PREROUTING -d $VM_EXTERNAL_IP -j DNAT --to-destination $INTERNAL_CONTAINER_IP

# Allow forwarding to the internal container
echo "Allowing forwarding to internal container"
sudo iptables -A FORWARD -d $INTERNAL_CONTAINER_IP -j ACCEPT

# Add a route to forward traffic for the internal container via the gateway container
echo "Adding route to forward traffic to the internal container via the gateway container"
sudo ip route add $INTERNAL_CONTAINER_IP via $GATEWAY_IP

# Set up NAT
echo "Setting up NAT"
sudo iptables -t nat -A POSTROUTING -o $EXTERNAL_INTERFACE -j MASQUERADE
####################################################################################################################

# Save iptables rules to ensure they persist
echo "Saving iptables rules to persist after reboot"
sudo iptables-save > /etc/iptables/rules.v4