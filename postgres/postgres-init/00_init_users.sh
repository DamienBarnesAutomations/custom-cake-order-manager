#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE custom_order_user LOGIN PASSWORD '${DB_PASSWORD}';
    CREATE ROLE n8n_user LOGIN PASSWORD '${DB_PASSWORD}';
EOSQL

