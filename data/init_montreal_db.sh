#!/usr/bin/env bash
set -e

echo "Creating montreal_data DB"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE DATABASE montreal_data;
  CREATE USER flight_user WITH PASSWORD 'test';
  GRANT ALL PRIVILEGES ON DATABASE montreal_data TO flight_user;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "montreal_data" <<-EOSQL
  CREATE SCHEMA IF NOT EXISTS flight_schema AUTHORIZATION flight_user;

  CREATE TABLE flight_schema.flight_table (
      primary_id SERIAL PRIMARY KEY,
      schedule_time TIMESTAMP,
      schedule_date DATE,
      revised_time TIMESTAMP,
      aircraft_number VARCHAR(10),
      aircraft_comp VARCHAR(40),
      aircraft_status VARCHAR(20),
      aircraft_gate VARCHAR(10),
      destination VARCHAR(40),
      destination_initial VARCHAR(20),
      id_scrap INTEGER,
      creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA flight_schema TO flight_user;
  GRANT USAGE ON SCHEMA flight_schema TO flight_user;
EOSQL

echo "Database 'montreal_data' with 'flight_schema' created."