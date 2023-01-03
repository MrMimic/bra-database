#!/usr/bin/env bash

set -e
source .env

docker build \
    --build-arg "MYSQL_USER=${MYSQL_USER}" \
    --build-arg "MYSQL_PWD=${MYSQL_PWD}" \
    --build-arg "MYSQL_HOST=${MYSQL_HOST}" \
    --build-arg "MYSQL_PORT=${MYSQL_PORT}" \
    --build-arg "MYSQL_DB=${MYSQL_DB}" \
    --build-arg "MYSQL_TABLE=${MYSQL_TABLE}" \
    -t bra/backend:latest .
