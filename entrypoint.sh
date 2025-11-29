#!/bin/sh

# Ensure necessary environment variables are set
if [ -z "$SERVER" ]; then
    echo "ERROR: SERVER variable is not set."
    exit 1
fi

if [ -z "$HTTP_PORT" ]; then
    echo "ERROR: HTTP_PORT variable is not set."
    exit 1
fi

# Add to /etc/hosts with sudo
echo "127.0.0.1 content.quakejs.com" | sudo tee -a /etc/hosts > /dev/null

cd /var/www/html

# Replace occurrences in index.html
# First replace the hostname
sed -i "s/quakejs/${SERVER}/g" index.html
# Set the content server port (HTTP_PORT for static assets)
sed -i "s/'fs_cdn', '${SERVER}:80'/'fs_cdn', '${SERVER}:${HTTP_PORT}'/g" index.html
# Set the game server port - use GAME_PORT if set, otherwise default to HTTP_PORT
GAME_PORT="${GAME_PORT:-${HTTP_PORT}}"
sed -i "s/'+connect', '${SERVER}:80'/'+connect', '${SERVER}:${GAME_PORT}'/g" index.html

echo "Configured client to connect to game server at ${SERVER}:${GAME_PORT}"

# start apache
sudo /etc/init.d/apache2 start

# move to quake dir
cd /usr/src/quakejs

# Check if SSL certificates are available for WSS proxy
if [ -f "/etc/ssl/kamal/certs/${SERVER}/privkey.pem" ] && [ -f "/etc/ssl/kamal/certs/${SERVER}/fullchain.pem" ]; then
    echo "SSL certificates found - starting WSS proxy on port 27961"

    # Update wssproxy.json with correct domain
    sed -i "s/kamal-quake.xyz/${SERVER}/g" wssproxy.json

    # Start wssproxy in background (use absolute path for config)
    node bin/wssproxy.js --config /usr/src/quakejs/wssproxy.json &
    WSSPROXY_PID=$!
    echo "WSS proxy started with PID: $WSSPROXY_PID"

    # Start game server on internal port 27960 (wssproxy will forward to this)
    echo "Starting game server on port 27960 (internal)"
    yes | head -n 90 | node build/ioq3ded.js +set fs_game baseq3 +set dedicated 1 +set net_port 27960 +exec server.cfg
else
    echo "WARNING: SSL certificates not found at /etc/ssl/kamal/certs/${SERVER}/"
    echo "Running game server without WSS proxy (multiplayer will be limited)"
    # Fall back to original behavior
    yes | head -n 90 | node build/ioq3ded.js +set fs_game baseq3 +set dedicated 1 +exec server.cfg
fi
