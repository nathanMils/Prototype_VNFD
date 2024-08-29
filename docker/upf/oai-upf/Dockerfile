# Use Alpine Linux as the base image
FROM oaisoftwarealliance/oai-upf:2024-june

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

CMD ["/openair-upf/bin/oai_upf", "-c", "/openair-upf/etc/config.yaml", "-o"]