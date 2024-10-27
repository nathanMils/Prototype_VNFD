ARG ELASTIC_VERSION

FROM docker.elastic.co/beats/filebeat:${ELASTIC_VERSION}

USER root
RUN mkdir -p /etc/pki/filebeat
USER filebeat