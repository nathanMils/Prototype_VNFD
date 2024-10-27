FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive


ENV PATH="$PATH:/opt/zeek/bin"

RUN apt-get update && apt-get install -y \
    apache2 \
    ca-certificates \
    curl \
    git \
    gnupg2 \
    lsb-release \
    sudo \
    vim \
    wget \
    nano \
    iproute2 \
    libjemalloc2 \
    libjemalloc-dev \
    build-essential \
    libnghttp2-dev \
    libbrotli-dev \
    cmake \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Zeek
RUN echo "Starting Zeek installation script..." && \
    echo 'Adding Zeek repository...' && \
    echo 'deb http://download.opensuse.org/repositories/security:/zeek/xUbuntu_22.04/ /' | tee /etc/apt/sources.list.d/security:zeek.list && \
    echo 'Adding Zeek repository key...' && \
    curl -fsSL https://download.opensuse.org/repositories/security:/zeek/xUbuntu_22.04/Release.key | gpg --dearmor | tee /etc/apt/trusted.gpg.d/security_zeek.gpg > /dev/null && \
    echo 'Updating package list...' && \
    apt update && \
    echo 'Installing Zeek...' && \
    apt install -y zeek && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# COPY config/networks.cfg "$SOURCE_DIR"/networks.cfg
# COPY config/node.cfg "$SOURCE_DIR"/node.cfg
# COPY config/zeekctl.cfg "$SOURCE_DIR"/zeekctl.cfg
# COPY config/zkg/config "$SOURCE_DIR"/zkg/config
# COPY config/local.zeek "$SOURCE_DIR"/local.zeek

RUN zkg refresh && \
    echo "y" | zkg install zeek/mitrecnd/bro-http2

RUN mkdir -p /opt/nathan/images

CMD ["apache2ctl", "-D", "FOREGROUND"]
