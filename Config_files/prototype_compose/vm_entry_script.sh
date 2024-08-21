# running docker compose
docker compose build --no-cache
docker compose up -d

# Forwarding traffic through gateway
sudo sysctl -w net.ipv4.ip_forward=1

# Forward all incoming traffic to the containerized gateway
sudo iptables -t nat -A PREROUTING -d $VM_IP -j DNAT --to-destination 172.18.0.2

# Ensure return traffic is masqueraded
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE