#!/bin/bash

TEMPLATE_CONFIG=/opt/prototype_master/socks_server/sockd.template.conf
CONFIG_DIR=/opt/prototype_master/socks_server/configs

matching_interfaces=$(ip -o link show | awk -F': ' '{print $2}' | grep -E '^uesimtun[0-9]+$')

for interface in $matching_interfaces; do
    NUMERIC_PART=$(echo "$interface" | grep -o '[0-9]\+')
    PORT=$((1080 + NUMERIC_PART))
    
    cp "$TEMPLATE_CONFIG" "$CONFIG_DIR/sockd.$interface.conf"
    
    sed -i "s|<PORT>|$PORT|g; s|<EXTERNAL_INTERFACE>|$interface|g" "$CONFIG_DIR/sockd.$interface.conf"
done

echo "Configuration files created successfully."

echo "Pulling Dante SOCKS server image..."
docker pull vimagick/dante

echo "Starting SOCKS proxies..."
for interface in $matching_interfaces; do
    CONTAINER_NAME="socks_proxy_$interface"
    cp $CONFIG_DIR/sockd.$interface.conf $CONFIG_DIR/sockd.conf
    docker run -d --network host -v $CONFIG_DIR/sockd.conf:/etc/dante/sockd.conf --name "$CONTAINER_NAME" vimagick/dante
done

for interface in $matching_interfaces; do
    ip_address=$(ip -o -4 addr show "$interface" | awk '{print $4}')
    CONTAINER_NAME="socks_proxy_$interface"
    NUMERIC_PART=$(echo "$interface" | grep -o '[0-9]\+')
    PORT=$((1080 + NUMERIC_PART))
    echo "UE TUN Interface: $interface, IP Address: $ip_address, Port: $PORT, SOCKS Proxy Container: $CONTAINER_NAME"
done
