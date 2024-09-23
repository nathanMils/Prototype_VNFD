#!/bin/bash


# Docker Compose file
compose_file="docker-compose-base.yml"

#Export elastic version
export ELASTIC_VERSION=8.15.0

# Build the Docker images
docker compose -f "$compose_file" build --no-cache

# Image names
images=(
    "prototype-zeek" 
    "prototype-filebeat" 
)
# tag names
tags=(
    "prototype-zeek:latest" 
    "prototype-filebeat:latest"
)

# Tag the images
for i in "${!images[@]}"; do
    docker tag "${images[$i]}" "${tags[$i]}"
done

# Save the images to a tar file
docker save -o base-images.tar "${tags[@]}"