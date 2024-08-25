#!/bin/bash
# running docker compose
TARGET_DIR=/opt/prototype_v1
docker load -i $TARGET_DIR/images.tar
docker compose -f $TARGET_DIR/prototype_compose/compose.yml up -d

# NF Variables
VM_EXTERNAL_IP=$1                   # VM's external IP
GATEWAY_IP="172.18.0.2"             # IP of the gateway container in its network
INTERNAL_CONTAINER_IP="172.20.0.3"  # IP of the internal container
EXTERNAL_INTERFACE="ens3"           # Interface assigned to the external network

# Filebeat Variables
VM_ELK_IP=$2
FILEBEAT_IP=""
ELK_INTERFACE=""

# ELK DNS Name resolution
ELASTICSEARCH_IP=$3
LOGSTASH_IP=$4

# Update hosts for DNS Name resolution for logstash and elasticsearch
echo "$ELASTICSEARCH_IP elasticsearch" >> /etc/hosts
echo "$LOGSTASH_IP logstash" >> /etc/hosts

# Enable IP forwarding on the gateway container (to be run inside the gateway container)
echo "Enabling IP forwarding on the gateway container"
echo 1 > /proc/sys/net/ipv4/ip_forward

# HOST/EXTERNAL <--> GATEWAY/ZEEK <--> NF
###################################################################################################################
# On the VM (external host) - DNAT to forward all traffic to the internal container via the gateway container
echo "Setting up DNAT to forward traffic to the internal container"
sudo iptables -t nat -A PREROUTING -d $VM_EXTERNAL_IP -j DNAT --to-destination $INTERNAL_CONTAINER_IP

# This bugger took me  forever to fix
sudo iptables -A FORWARD -d $INTERNAL_CONTAINER_IP -j ACCEPT

# On the VM (external host) - Add a route to forward traffic for the internal container via the gateway container
echo "Adding route to forward traffic to the internal container via the gateway container"
sudo ip route add $INTERNAL_CONTAINER_IP via $GATEWAY_IP

# On the gateway container - Set up NAT (optional, if you want to masquerade outgoing traffic)
echo "Setting up NAT on the gateway container (if required)"
sudo iptables -t nat -A POSTROUTING -o $EXTERNAL_INTERFACE -j MASQUERADE
####################################################################################################################

# HOST/ELK <--> FILEBEAT
####################################################################################################################
# On the VM (external host) - DNAT to forward all traffic to the internal container via the gateway container
echo "Setting up DNAT to forward traffic to the internal container"
sudo iptables -t nat -A PREROUTING -d $VM_ELK_IP -j DNAT --to-destination $FILEBEAT_IP

# This bugger took me  forever to fix
sudo iptables -A FORWARD -d $FILEBEAT_IP -j ACCEPT

# On the gateway container - Set up NAT (optional, if you want to masquerade outgoing traffic)
echo "Setting up NAT on the gateway container (if required)"
sudo iptables -t nat -A POSTROUTING -o $ELK_INTERFACE -j MASQUERADE
####################################################################################################################

# (Optional) - Save iptables rules to ensure they persist
echo "Saving iptables rules to persist after reboot"
sudo iptables-save > /etc/iptables/rules.v4