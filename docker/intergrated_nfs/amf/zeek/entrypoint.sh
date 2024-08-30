#!/bin/sh

zeek -i eth0

# Keep the container running (optional)
tail -f /dev/null