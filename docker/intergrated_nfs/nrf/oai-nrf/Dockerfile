# Use Alpine Linux as the base image
FROM oaisoftwarealliance/oai-nrf:v2.0.1

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable, update package list, and install iproute2
RUN chmod +x /entrypoint.sh && \
	apt-get update && \
	apt-get install -y iproute2 && \
	apt-get clean

# Set the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

CMD ["/openair-nrf/bin/oai_nrf", "-c", "/openair-nrf/etc/config.yaml", "-o"]