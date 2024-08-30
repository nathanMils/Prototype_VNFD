#!/bin/bash

NF="udm"

# Docker Compose file
compose_file="docker-compose-$NF.yml"

# Build the Docker images
docker compose -f "$compose_file" build --no-cache

# Image names
images=(
    "$NF-gateway" 
    "$NF-filebeat" 
    "$NF-oai-$NF"
)
# tag names
tags=(
    "prototype-gateway:latest" 
    "prototype-filebeat:latest" 
    "prototype-$NF:latest"
)

# Tag the images
for i in "${!images[@]}"; do
    docker tag "${images[$i]}" "${tags[$i]}"
done

# Save the images to a tar file
docker save -o $NF-images.tar "${tags[@]}"