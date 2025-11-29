FROM node:16-slim
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=US/Eastern

# Update package list and upgrade installed packages
RUN apt-get update && apt-get upgrade -y

# Install essential packages
RUN apt-get install -y apt-utils wget apache2 vim curl git sudo jq npm

# pull quake and install
RUN git clone --recurse-submodules https://github.com/neonwatty/quakejs.git /usr/src/quakejs
RUN cd /usr/src/quakejs
WORKDIR /usr/src/quakejs
RUN npm install

# copy over assets
COPY server.cfg /usr/src/quakejs/base/baseq3/server.cfg
COPY server.cfg /usr/src/quakejs/base/cpma/server.cfg

# copy wssproxy configuration
COPY wssproxy.json /usr/src/quakejs/wssproxy.json

# expose ports: 80 (web), 27960 (game internal), 27961 (wss proxy)
EXPOSE 80 27960 27961

# replace index / assets
RUN rm /var/www/html/index.html 
RUN cp /usr/src/quakejs/html/* /var/www/html/
COPY ./include/assets/ /var/www/html/assets

# run entrypoint
ADD entrypoint.sh /entrypoint.sh
RUN chmod 777 /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]