#!/bin/bash
# Routing config for host Util

# HOST A IPv4 info
5G_NET_A_CIDR_V4="10.5.0.0/26"
ELK_NET_A_CIDR_V4="10.6.0.0/26"
HOST_A_IP_V4="fill in"                     # IPv4 address of Host A

# HOST A IPv6 info
# 5G_NET_A_CIDR_V6="2001:db8:abcd:001::/64"
# ELK_NET_A_CIDR_V6="2001:db8:abcd:002::/64"
# HOST_A_IP_V6="fill in"                     # IPv6 address of Host A

# Routing for Host A
ip route add $5G_NET_A_CIDR_V4 via $HOST_A_IP_V4
ip route add $ELK_NET_A_CIDR_V4 via $HOST_A_IP_V4
# ip -6 route add $5G_NET_A_CIDR_V6 via $HOST_A_IP_V6
# ip -6 route add $ELK_NET_A_CIDR_V6 via $HOST_A_IP_V6

# HOST B IPv4 info
# 5G_NET_B_CIDR_V4="10.7.0.0/26"
# ELK_NET_B_CIDR_V4="10.8.0.0/26"
# HOST_B_IP_V4="fill in"                     # IPv4 address of Host B

# HOST B IPv6 info
# 5G_NET_B_CIDR_V6="2001:db8:abcd:003::/64"
# ELK_NET_B_CIDR_V6="2001:db8:abcd:004::/64"
# HOST_B_IP_V6="fill in"                     # IPv6 address of Host B

# Routing for Host B
# ip route add $5G_NET_B_CIDR_V4 via $HOST_B_IP_V4
# ip route add $ELK_NET_B_CIDR_V4 via $HOST_B_IP_V4
# ip -6 route add $5G_NET_B_CIDR_V6 via $HOST_B_IP_V6
# ip -6 route add $ELK_NET_B_CIDR_V6 via $HOST_B_IP_V6