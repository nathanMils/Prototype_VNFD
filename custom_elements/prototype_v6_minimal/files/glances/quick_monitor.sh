#!/bin/bash

TIME=$1

echo "Montioring the system for 5 minutes..."
glances --docker --processes filebeat,zeek --time $TIME --export json
