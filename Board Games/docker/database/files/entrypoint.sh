#!/usr/bin/env bash

(sleep 10 && cd /webapp/ && flask db init && flask db migrate && flask db upgrade && python3 create_admin.py)&
docker-entrypoint.sh postgres
