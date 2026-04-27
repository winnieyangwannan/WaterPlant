-- WaterPlant SQLite schema
-- Owned by server/logger.py; never write to these tables from anywhere else.
-- See docs/dashboard_plan.md for the full data layout (time-series in SQLite,
-- plant metadata in plants/<id>.yaml).

-- Every moisture reading the logger ingests from the Arduino serial bridge.
CREATE TABLE readings (
  id              INTEGER PRIMARY KEY,
  plant_id        INTEGER NOT NULL,    -- resolved from sensor_idx via plants/_sensor_map.yaml
  recorded_at     TEXT NOT NULL,       -- host wall-clock at receive time (ISO 8601)
  arduino_millis  INTEGER NOT NULL,    -- Arduino uptime in ms; debug aid only, not a timestamp
  moisture_pct    INTEGER NOT NULL     -- 0..100, computed Arduino-side from raw ADC
);
CREATE INDEX idx_readings_plant_time ON readings(plant_id, recorded_at);

-- One row per watering event. moisture_after is filled in async by the logger
-- on the next regular reading from the same plant (the lazy-pairing approach).
CREATE TABLE watering_events (
  id                INTEGER PRIMARY KEY,
  plant_id          INTEGER NOT NULL,
  started_at        TEXT NOT NULL,                       -- ISO 8601, host wall-clock
  ended_at          TEXT,                                -- filled when PUMP_OFF arrives
  moisture_before   INTEGER,                             -- last reading before PUMP_ON
  moisture_after    INTEGER,                             -- next reading after PUMP_OFF
  duration_ms       INTEGER,                             -- ended_at - started_at
  trigger_source    TEXT NOT NULL DEFAULT 'auto'         -- 'auto' | 'manual'
);
