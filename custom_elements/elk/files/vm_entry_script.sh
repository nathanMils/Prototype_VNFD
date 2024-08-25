#!/bin/bash

# Exporting ELK stack enviroment variables
export ELASTIC_VERSION=8.13.1

## Passwords for stack users
#

# User 'elastic' (built-in)
#
# Superuser role, full access to cluster management and data indices.
# https://www.elastic.co/guide/en/elasticsearch/reference/current/built-in-users.html
export ELASTIC_PASSWORD='elasticness'

# User 'logstash_internal' (custom)
#
# The user Logstash uses to connect and send data to Elasticsearch.
# https://www.elastic.co/guide/en/logstash/current/ls-security.html
export LOGSTASH_INTERNAL_PASSWORD='nopedope'

# User 'kibana_system' (built-in)
#
# The user Kibana uses to connect and communicate with Elasticsearch.
# https://www.elastic.co/guide/en/elasticsearch/reference/current/built-in-users.html
export KIBANA_SYSTEM_PASSWORD='kibanaNana'

# Users 'metricbeat_internal', 'filebeat_internal' and 'heartbeat_internal' (custom)
#
# The users Beats use to connect and send data to Elasticsearch.
# https://www.elastic.co/guide/en/beats/metricbeat/current/feature-roles.html
export FILEBEAT_INTERNAL_PASSWORD='filebeatNathan'

# User 'beats_system' (built-in)
#
# The user the Beats use when storing monitoring information in Elasticsearch.
# https://www.elastic.co/guide/en/elasticsearch/reference/current/built-in-users.html
export BEATS_SYSTEM_PASSWORD='beatsNathan'

# Starting containers and networks
TARGET_DIR=/opt/elk_v1
docker load -i $TARGET_DIR/images.tar
docker compose -f $TARGET_DIR/elk_compose/compose.yml up -d

