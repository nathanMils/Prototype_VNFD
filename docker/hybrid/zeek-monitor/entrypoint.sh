#!/bin/bash

# Enable IP forwarding
sysctl -w net.ipv4.ip_forward=1

# Set up IP tables to mirror traffic for monitoring
iptables -t nat -A PREROUTING -p tcp --destination 172.20.0.2 -j REDIRECT --to-ports 9999

# Run Zeek with the specified configuration
zeek -i eth0 local.zeek

# Move logs to the logs directory
mv /usr/local/zeek/logs/current/* /usr/local/zeek/logs/ && rmdir /usr/local/zeek/logs/current


####################################################################################
#!/bin/sh
#echo "Setting up routing rules..."
#iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
#iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT
#iptables -A FORWARD -i eth0 -o eth1 -j ACCEPT
#echo 1 > /proc/sys/net/ipv4/ip_forward

#mkdir -p /usr/local/zeek-monitor/logs
#chown -R zeek:zeek /usr/local/zeek-monitor/logs

#zeek -i eth0 /usr/local/zeek/share/zeek/local.zeek
#tail -f /usr/local/zeek-monitor/logs/current/conn.log


