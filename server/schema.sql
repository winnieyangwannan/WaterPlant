# Dummy schema for SQLite database
# This file is for reference and won't be executed directly.

# Table for moisture readings
CREATE TABLE readings (
  id              INTEGER PRIMARY KEY,
  plant_id        INTEGER NOT NULL,
  recorded_at     TEXT NOT NULL,
  arduino_millis  INTEGER NOT NULL,
  moisture_pct    INTEGER NOT NULL
);
CREATE INDEX idx_readings_plant_time ON readings(plant_id, recorded_at);

# Table for watering events
CREATE TABLE watering_events (
  id                INTEGER PRIMARY KEY,
  plant_id          INTEGER NOT NULL,
  started_at        TEXT NOT NULL,
  ended_at          TEXT,
  moisture_before   INTEGER,
  moisture_after    INTEGER,
  duration_ms       INTEGER,
  trigger_source    TEXT NOT NULL DEFAULT 'auto'
);
