FROM ubuntu:latest

# install basics, node, pull quakejs and install
ENV DEBIAN_FRONTEND=noninteractive
COPY install_scripts /usr/src/install_scripts
WORKDIR /usr/src/install_scripts
RUN bash /usr/src/install_scripts/start.sh

# copy over assets
COPY server.cfg /usr/src/quakejs/base/baseq3/server.cfg
COPY server.cfg /usr/src/quakejs/base/cpma/server.cfg
COPY ./include/ioq3ded/ioq3ded.fixed.js /usr/src/quakejs/build/ioq3ded.js

# replace index / assets
WORKDIR /
RUN rm /var/www/html/index.html 
RUN cp /usr/src/quakejs/html/* /var/www/html/
COPY ./include/assets/ /var/www/html/assets
RUN ls /var/www/html

# set host
RUN echo "127.0.0.1 content.quakejs.com" >> /etc/hosts

# run entrypoint
ADD entrypoint.sh /entrypoint.sh
RUN chmod 777 ./entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]