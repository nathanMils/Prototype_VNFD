#!/bin/sh

cd /opt/zeek/log
zeek -i $INTERFACE local.zeek

# Keep the container running (optional)
tail -f /dev/null