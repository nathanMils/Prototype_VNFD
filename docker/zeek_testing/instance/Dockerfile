FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install necessary packages
RUN apt-get update && apt-get install -y \
    apache2 \
    hping3 \
    iptables \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

CMD ["apache2ctl", "-D", "FOREGROUND"]
