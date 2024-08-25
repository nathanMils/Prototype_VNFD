#!/bin/bash

# ELK stack enviroment variables
ELASTIC_VERSION=8.13.1

TARGET=../../custom_elements/elk/files
ELASTICSEARCH=docker.elastic.co/elasticsearch/elasticsearch:${ELASTIC_VERSION}
KIBANA=docker.elastic.co/kibana/kibana:${ELASTIC_VERSION}
LOGSTASH=docker.elastic.co/logstash/logstash:${ELASTIC_VERSION}

# Login
docker login

# Build and push nf image
docker pull $ELASTICSEARCH
docker pull $KIBANA
docker pull $LOGSTASH

docker save -o $TARGET/images.tar $ELASTICSEARCH $KIBANA $LOGSTASH
