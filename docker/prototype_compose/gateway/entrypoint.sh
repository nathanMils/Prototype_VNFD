#!/bin/sh

# Add routing rules here
echo "Adding routing rules..."
# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward
# iptables -t nat -N POSTROUTING || true
# iptables -N FORWARD || true
# # Configure iptables
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT
iptables -A FORWARD -i eth0 -o eth1 -j ACCEPT

zeek -i eth0

# Keep the container running (optional)
tail -f /dev/null