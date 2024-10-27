FROM alpine:3.20.2

# Install necessary packages and set permissions
RUN apk add --no-cache iptables curl apache2 && \
    rm -rf /var/cache/apk/*

CMD ["httpd", "-D", "FOREGROUND"]
