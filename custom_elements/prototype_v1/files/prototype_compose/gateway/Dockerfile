ARG ALPINE_VERSION
ARG EXTERNAL_IF
ARG INTERNAL_IF
# Use Alpine Linux as the base image
FROM alpine:${ALPINE_VERSION}

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