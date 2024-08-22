#!/bin/bash

GATEWAY=nathanmills/gateway:latest
NF=nathanmills/nf:latest
TARGET=../../custom_elements/prototype_v1

# Login
docker login

# Build and push nf image
docker compose build --no-cache

# Tag and push images to docker hub
docker tag prototype_compose-nf:latest $NF
docker push $NF

docker tag prototype_compose-gateway:latest $GATEWAY
docker push $GATEWAY

# Pull the images
docker pull $NF
docker pull $GATEWAY

# Pull alpine just in case
docker pull alpine:3.20.2

# Compress to tar file
docker save -o $TARGET/images.tar alpine:3.20.2 $GATEWAY $NF
