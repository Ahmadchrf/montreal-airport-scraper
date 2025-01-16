CREATE SCHEMA IF NOT EXISTS flight_schema;

CREATE USER flight_user WITH PASSWORD 'test';
GRANT ALL PRIVILEGES ON SCHEMA flight_schema TO flight_user;
ALTER SCHEMA flight_schema OWNER TO flight_user;

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