#!/bin/bash
# running docker compose
docker compose -f /opt/prototype/Conf_files/prototype_compose/compose.yml build --no-cache
docker compose -f /opt/prototype/Conf_files/prototype_compose/compose.yaml up -d

sleep 30
# Variables
VM_IP="your_vm_ip"             # Replace with your VM's external IP
GATEWAY_IP="172.18.0.2"        # IP of the gateway container in its network
INTERNAL_CONTAINER_IP="172.20.0.3"  # IP of the internal container

# Enable IP forwarding on the gateway container (to be run inside the gateway container)
echo "Enabling IP forwarding on the gateway container"
echo 1 > /proc/sys/net/ipv4/ip_forward

# On the VM (external host) - DNAT to forward all traffic to the internal container via the gateway container
echo "Setting up DNAT to forward traffic to the internal container"
sudo iptables -t nat -A PREROUTING -d $VM_IP -j DNAT --to-destination $INTERNAL_CONTAINER_IP

# On the VM (external host) - Add a route to forward traffic for the internal container via the gateway container
echo "Adding route to forward traffic to the internal container via the gateway container"
sudo ip route add $INTERNAL_CONTAINER_IP via $GATEWAY_IP

# On the gateway container - Set up NAT (optional, if you want to masquerade outgoing traffic)
echo "Setting up NAT on the gateway container (if required)"
sudo iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE

# (Optional) - Save iptables rules to ensure they persist
echo "Saving iptables rules to persist after reboot"
sudo iptables-save > /etc/iptables/rules.v4