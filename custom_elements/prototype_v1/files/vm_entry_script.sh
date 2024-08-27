#!/bin/bash

# Starting containers and networks
TARGET_DIR=/opt/prototype_v1
docker load -i $TARGET_DIR/images.tar
docker compose -f $TARGET_DIR/prototype_compose/compose.yml up -d

# NF Variables
VM_EXTERNAL_IP=$1                   # VM's external IP
GATEWAY_IP="172.18.0.2"             # IP of the gateway container in its network
INTERNAL_CONTAINER_IP="172.20.0.3"  # IP of the internal container
EXTERNAL_INTERFACE="ens3"           # Interface assigned to the external network

# ELK DNS Name resolution
LOGSTASH_IP=$2
ELASTIC_IP=$3

# Update hosts for DNS Name resolution for logstash and elasticsearch
echo "$LOGSTASH_IP elasticsearch" >> /etc/hosts
echo "$ELASTIC_IP logstash" >> /etc/hosts

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