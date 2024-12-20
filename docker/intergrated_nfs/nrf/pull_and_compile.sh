#!/bin/bash

NF="nrf"

# Docker Compose file
compose_file="docker-compose-$NF.yml"

#Export elastic version
export ELASTIC_VERSION=8.15.0

# Build the Docker images
docker compose -f "$compose_file" build --no-cache

# Image names
images=(
    "$NF-zeek" 
    "$NF-filebeat" 
    "$NF-oai-$NF"
)
# tag names
tags=(
    "prototype-zeek:latest" 
    "prototype-filebeat:latest" 
    "prototype-$NF:latest"
)

# Tag the images
for i in "${!images[@]}"; do
    docker tag "${images[$i]}" "${tags[$i]}"
done

# Save the images to a tar file
docker save -o $NF-images.tar "${tags[@]}"