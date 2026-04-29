-- Initial database setup for local development.
-- Loaded automatically by docker-compose on first run.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Ensure the test database also exists
SELECT 'CREATE DATABASE transactbank_test'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'transactbank_test'
)\gexec
