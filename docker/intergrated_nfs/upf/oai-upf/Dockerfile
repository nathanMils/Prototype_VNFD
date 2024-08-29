# Use Alpine Linux as the base image
FROM oaisoftwarealliance/oai-upf:2024-june

# Update package list and install iproute2
RUN apt-get update && apt-get install -y iproute2 && apt-get clean

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

CMD ["/openair-upf/bin/oai_upf", "-c", "/openair-upf/etc/config.yaml", "-o"]