#!/bin/bash

TIME=$1

echo "Montioring the system for 5 minutes..."
timeout 300 glances --process-filter filebeat --process-filter zeek --export jsonfile --export-json-file output.json --docker -t 1