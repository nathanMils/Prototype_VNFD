#!/bin/sh
ip route del default via 172.21.0.1
ip route add default via 172.21.0.2
ip route show
# Keep the container running (optional)
tail -f /dev/null