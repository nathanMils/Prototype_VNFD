#!/bin/sh

zeek -i $INTERFACE

# Keep the container running (optional)
tail -f /dev/null