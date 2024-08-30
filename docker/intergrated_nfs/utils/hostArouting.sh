#!/bin/bash
# Routing config for host A

# HOST A info
5G_NET_A_CIDR="10.5.0.0/26"
ELK_NET_A_CIDR="10.6.0.0/26"
VIR_ROUTER_A_EXT_IP="fill in"
HOST_A_IP="fill in"

ip route add $5G_NET_A_CIDR via $VIR_ROUTER_A_EXT_IP
ip route add $ELK_NET_A_CIDR via $VIR_ROUTER_A_EXT_IP

# HOST B info
5G_NET_B_CIDR="10.7.0.0/26"
ELK_NET_B_CIDR="10.8.0.0/26"
HOST_B_IP="fill in"

ip route add $5G_NET_B_CIDR via $HOST_B_IP
ip route add $ELK_NET_B_CIDR via $HOST_B_IP