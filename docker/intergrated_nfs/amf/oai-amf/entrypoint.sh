#!/bin/bash

# Perform substitution and write to a temporary file
envsubst < /openair-amf/etc/config.yaml > /openair-amf/etc/config.tmp.yaml
# Replace the original file with the temporary file
mv /openair-amf/etc/config.tmp.yaml /openair-amf/etc/config.yaml

# Start the main application
exec "$@"