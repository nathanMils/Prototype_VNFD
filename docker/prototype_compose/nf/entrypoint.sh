#!/bin/sh
ip route show
sudo ip route add default via 172.20.0.2

# Keep the container running (optional)
tail -f /dev/null