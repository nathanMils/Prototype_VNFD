FROM oaisoftwarealliance/oai-amf:v2.0.1

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable, update package list, and install iproute2
RUN chmod +x /entrypoint.sh

# Set the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

CMD ["/openair-amf/bin/oai_amf", "-c", "/openair-amf/etc/config.yaml", "-o"]