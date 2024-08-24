# Use Alpine Linux as the base image
FROM zeek/zeek:6.0.5

# Install iptables
RUN apk add --no-cache iptables

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Default command (can be overridden if needed)
CMD ["sh"]