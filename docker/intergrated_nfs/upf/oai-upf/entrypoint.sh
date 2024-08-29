#!/bin/bash
ip route del default via 172.20.0.1
ip route add default via 172.20.0.2
ip route show
# Execute original entrypoint
exec "$@"