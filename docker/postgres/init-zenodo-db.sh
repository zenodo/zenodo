#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER zenodo WITH CREATEDB PASSWORD 'zenodo';
    CREATE DATABASE zenodo OWNER zenodo;
    GRANT ALL PRIVILEGES ON DATABASE zenodo TO zenodo;
EOSQL
