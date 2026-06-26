#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    CREATE DATABASE airflow;
    CREATE DATABASE enterprise_etl;
    CREATE USER airflow WITH PASSWORD 'airflow';
    GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
    GRANT ALL PRIVILEGES ON DATABASE enterprise_etl TO airflow;
EOSQL
