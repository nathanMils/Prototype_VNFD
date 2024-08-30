FROM oaisoftwarealliance/oai-amf:v2.0.1

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh && \
    apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

# Set the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

CMD ["/openair-amf/bin/oai_amf", "-c", "/openair-amf/etc/config.yaml", "-o"]