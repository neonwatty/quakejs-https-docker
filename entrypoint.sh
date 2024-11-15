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
sed -i "s/quakejs/${SERVER}/g" index.html
sed -i "s/${SERVER}:80/${SERVER}:${HTTP_PORT}/g" index.html

# start apache
sudo /etc/init.d/apache2 start

# move to quake dir
cd /usr/src/quakejs

# Start Node.js server
yes | head -n 90 | node build/ioq3ded.js +set fs_game baseq3 set dedicated 1 +exec server.cfg -s 
