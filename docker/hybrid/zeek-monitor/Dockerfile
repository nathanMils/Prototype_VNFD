# zeek-monitor/Dockerfile
FROM zeek/zeek:latest

# Install additional packages if necessary (optional)
RUN apt-get update && apt-get install -y iproute2 iptables 

# Copy the Zeek configuration files
COPY zeek /usr/local/zeek/etc/

# Copy the entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# Make the script executable
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]



##################################################
# Make the entrypoint script executable
#RUN chmod +x /entrypoint.sh

# Expose ports for Zeek communication (optional, if needed)
#EXPOSE 47760

# Set the entrypoint script
#ENTRYPOINT ["/entrypoint.sh"]

# Default command to start Zeek (can be overridden if needed)
#CMD ["zeek", "-i", "eth0", "/usr/local/zeek/share/zeek/local.zeek"]
