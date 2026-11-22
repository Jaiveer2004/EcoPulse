BEGIN;
-- 1. Create the application schema.
CREATE SCHEMA IF NOT EXISTS core;
-- 2. Track database migrations.
CREATE TABLE IF NOT EXISTS core.schema_migrations (
    version VARCHAR(20) PRIMARY KEY,
    description TEXT NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- 3. Environmental monitoring stations.
CREATE TABLE core.stations (
    station_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    station_code VARCHAR(64) NOT NULL UNIQUE,
    station_name VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    country_code CHAR(2),
    source_type VARCHAR(20) NOT NULL,
    source_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_station_latitude CHECK (
        latitude BETWEEN -90 AND 90
    ),
    CONSTRAINT chk_station_longitude CHECK (
        latitude BETWEEN -90 AND 90
    ),
    CONSTRAINT chk_station_source_type CHECK (source_type IN ('real', 'synthetic'))
);


-- 4. Environmental measurements.
CREATE TABLE core.measurements (
    measurement_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    station_id BIGINT NOT NULL,
    parameter_code VARCHAR(50) NOT NULL,
    measurement_value NUMERIC(18, 6) NOT NULL,
    unit VARCHAR(32) NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_type VARCHAR(20) NOT NULL,
    source_name VARCHAR(100) NOT NULL,
    source_record_id VARCHAR(255),
    raw_payload JSONB,
    CONSTRAINT fk_measurement_station FOREIGN KEY (station_id) REFERENCES core.stations(station_id) ON DELETE RESTRICT,
    CONSTRAINT chk_measurement_source_type CHECK (source_type IN ('real', 'synthetic')),
    -- Air-pollutant concentrations cannot be negative.
    -- Other environmental parameters, such as temperature,
    -- may legitimately be negative.
    CONSTRAINT chk_nonegative_pollutants CHECK (
        parameter_code NOT IN ('pm25', 'pm10', 'no2', 'so2', 'co', 'o3')
        OR measurement_value >= 0
    )
);

-- 5. Prevent duplicate ingestion of the same source record.
CREATE UNIQUE INDEX uq_measurement_source_record ON core.measurements (source_name, source_record_id)
WHERE source_record_id IS NOT NULL;

-- 6. Indexes for common analytical and lookup queries.
CREATE INDEX idx_measurements_station_observed ON core.measurements (station_id, observed_at DESC);

CREATE INDEX idx_measurements_parameter_observed ON core.measurements (parameter_code, observed_at DESC);

-- 7. Record this migration.
INSERT INTO core.schema_migrations (version, description)
VALUES (
        'V001',
        'Create core station and measurement tables'
    );

COMMIT;