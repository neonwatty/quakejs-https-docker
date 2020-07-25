FROM ubuntu:18.04

# linux updates and installs
RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get update
RUN apt-get install -y vim
RUN apt-get install -y curl 
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y python3.8
RUN apt-get install -y python3-pip
RUN apt-get update
RUN apt-get install -y python-dev default-libmysqlclient-dev
RUN apt-get install -y python3-dev
RUN apt-get update 
RUN apt-get install -y graphviz
RUN mkdir /usr/src/app

COPY requirements.txt /usr/src/app/requirements.txt
RUN pip3 install -r /usr/src/app/requirements.txt