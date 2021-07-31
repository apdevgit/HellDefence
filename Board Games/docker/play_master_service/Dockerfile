FROM ubuntu:18.04

#Install python, pip
RUN apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && apt-get install -y python3.6 python3.6-dev python3-pip
RUN ln -sfn /usr/bin/python3.6 /usr/bin/python3 && ln -sfn /usr/bin/python3 /usr/bin/python && ln -sfn /usr/bin/pip3 /usr/bin/pip

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN mkdir /webapp
COPY ./files/. /webapp/
WORKDIR /webapp

#Install python modules
RUN python3 -m pip install -r ./requirements


EXPOSE 5000

CMD ["flask", "run", "-h", "0.0.0.0"]

