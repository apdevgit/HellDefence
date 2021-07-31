FROM postgres:12.3

ENV POSTGRES_USER flaskuser
ENV POSTGRES_PASSWORD zero
ENV POSTGRES_DB board_games_db

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

#Install python, pip
RUN apt-get update && apt-get install -y software-properties-common

RUN apt install -y python3-pip
RUN python3 -m pip install --upgrade pip

RUN pip uninstall psycopg2
RUN pip3 uninstall psycopg2
RUN pip3 list --outdated
RUN pip3 install --upgrade wheel
RUN pip3 install --upgrade setuptools

RUN apt-get install -y --reinstall libpq-dev


RUN mkdir /webapp
COPY ./files/. /webapp/
WORKDIR /webapp


#Install python modules
RUN python3 -m pip install -r ./requirements

EXPOSE 5432

RUN chmod u+x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

