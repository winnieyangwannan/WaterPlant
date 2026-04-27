#!/usr/bin/env python3
"""
waterplant-logger — reads Arduino CSV from the serial bridge (TCP),
writes readings + watering events into SQLite.

Expected CSV format from Arduino:
    millis,sensor_idx,moisture_pct,event

Events: INIT, PUMP_ON, PUMP_OFF, or empty (regular reading).
"""

import socket
import sqlite3
import sys
import time
import os
import yaml
from datetime import datetime, timezone

# --- Config ---
BRIDGE_HOST = "localhost"
BRIDGE_PORT = 12345
DB_PATH = "/var/lib/waterplant/waterplant.db"
SENSOR_MAP_PATH = "/home/clawd/WaterPlant/plants/_sensor_map.yaml"
RECONNECT_DELAY = 5  # seconds between reconnect attempts
RENDER_SCRIPT = "/home/clawd/WaterPlant/server/render.py"
VENV_PYTHON = "/home/clawd/WaterPlant/server/.venv/bin/python3"


def load_sensor_map(path):
    """Load sensor_idx -> plant_id mapping from YAML."""
    try:
        with open(path, "r") as f:
            raw = yaml.safe_load(f)
        if raw is None:
            return {}
        # YAML parses "0: 1" as {0: 1}
        return {int(k): int(v) for k, v in raw.items()}
    except Exception as e:
        print(f"[logger] WARNING: could not load sensor map: {e}", file=sys.stderr)
        return {}


def get_db(db_path):
    """Open SQLite connection with WAL mode for concurrent reads."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def insert_reading(conn, plant_id, recorded_at, arduino_millis, moisture_pct):
    conn.execute(
        "INSERT INTO readings (plant_id, recorded_at, arduino_millis, moisture_pct) "
        "VALUES (?, ?, ?, ?)",
        (plant_id, recorded_at, arduino_millis, moisture_pct),
    )
    conn.commit()


def handle_pump_on(conn, plant_id, recorded_at, moisture_pct):
    """Record the start of a watering event."""
    conn.execute(
        "INSERT INTO watering_events (plant_id, started_at, moisture_before, trigger_source) "
        "VALUES (?, ?, ?, 'auto')",
        (plant_id, recorded_at, moisture_pct),
    )
    conn.commit()


def handle_pump_off(conn, plant_id, recorded_at, duration_ms):
    """Fill in ended_at and duration for the most recent open watering event."""
    conn.execute(
        "UPDATE watering_events SET ended_at = ?, duration_ms = ? "
        "WHERE plant_id = ? AND ended_at IS NULL "
        "ORDER BY id DESC LIMIT 1",
        (recorded_at, duration_ms, plant_id),
    )
    conn.commit()


def fill_moisture_after(conn, plant_id, moisture_pct):
    """Fill moisture_after on the most recent watering event that's missing it."""
    conn.execute(
        "UPDATE watering_events SET moisture_after = ? "
        "WHERE plant_id = ? AND moisture_after IS NULL AND ended_at IS NOT NULL "
        "ORDER BY id DESC LIMIT 1",
        (moisture_pct, plant_id),
    )
    conn.commit()


def trigger_render(plant_id):
    """Trigger a page re-render for the given plant (fire-and-forget)."""
    try:
        os.system(f"{VENV_PYTHON} {RENDER_SCRIPT} {plant_id} &")
    except Exception:
        pass  # non-critical


def process_line(line, conn, sensor_map):
    """Parse one CSV line and write to DB."""
    line = line.strip()
    if not line or line.startswith("millis"):  # skip header or empty
        return

    parts = line.split(",")

    # Support both old format (millis,moisture_pct,event) and new (millis,sensor_idx,moisture_pct,event)
    if len(parts) == 3:
        # Old format — assume sensor_idx=0
        millis_str, moisture_str, event = parts
        sensor_idx = 0
    elif len(parts) == 4:
        millis_str, sensor_idx_str, moisture_str, event = parts
        try:
            sensor_idx = int(sensor_idx_str.strip())
        except ValueError:
            print(f"[logger] SKIP bad sensor_idx: {line}", file=sys.stderr)
            return
    else:
        print(f"[logger] SKIP malformed line: {line}", file=sys.stderr)
        return

    try:
        arduino_millis = int(millis_str.strip())
    except ValueError:
        print(f"[logger] SKIP bad millis: {line}", file=sys.stderr)
        return

    moisture_str = moisture_str.strip()
    if moisture_str == "--":
        # INIT line, no moisture data
        print(f"[logger] Arduino INIT detected")
        return

    try:
        moisture_pct = int(moisture_str)
    except ValueError:
        print(f"[logger] SKIP bad moisture: {line}", file=sys.stderr)
        return

    event = event.strip().upper()

    # Resolve plant_id
    plant_id = sensor_map.get(sensor_idx)
    if plant_id is None:
        print(f"[logger] SKIP unknown sensor_idx={sensor_idx} (not in sensor map)", file=sys.stderr)
        return

    now = datetime.now(timezone.utc).isoformat()

    # Always insert a reading
    insert_reading(conn, plant_id, now, arduino_millis, moisture_pct)

    if event == "PUMP_ON":
        handle_pump_on(conn, plant_id, now, moisture_pct)
        print(f"[logger] PUMP_ON plant={plant_id} moisture={moisture_pct}%")
    elif event == "PUMP_OFF":
        handle_pump_off(conn, plant_id, now, duration_ms=None)
        print(f"[logger] PUMP_OFF plant={plant_id}")
    else:
        # Regular reading — try to fill moisture_after for recent waterings
        fill_moisture_after(conn, plant_id, moisture_pct)

    # Trigger re-render
    trigger_render(plant_id)


def main():
    print(f"[logger] Starting waterplant-logger")
    print(f"[logger] DB: {DB_PATH}")
    print(f"[logger] Bridge: {BRIDGE_HOST}:{BRIDGE_PORT}")
    print(f"[logger] Sensor map: {SENSOR_MAP_PATH}")

    sensor_map = load_sensor_map(SENSOR_MAP_PATH)
    if not sensor_map:
        print("[logger] WARNING: sensor map is empty — no readings will be recorded", file=sys.stderr)
    else:
        print(f"[logger] Sensor map: {sensor_map}")

    conn = get_db(DB_PATH)

    while True:
        try:
            print(f"[logger] Connecting to {BRIDGE_HOST}:{BRIDGE_PORT}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            sock.connect((BRIDGE_HOST, BRIDGE_PORT))
            print(f"[logger] Connected!")

            buf = ""
            while True:
                try:
                    data = sock.recv(4096)
                except socket.timeout:
                    continue  # no data in 30s, keep waiting
                if not data:
                    print("[logger] Connection closed by bridge", file=sys.stderr)
                    break
                buf += data.decode("utf-8", errors="replace")
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    process_line(line, conn, sensor_map)

        except ConnectionRefusedError:
            print(f"[logger] Bridge not available, retrying in {RECONNECT_DELAY}s...", file=sys.stderr)
        except Exception as e:
            print(f"[logger] Error: {e}, retrying in {RECONNECT_DELAY}s...", file=sys.stderr)
        finally:
            try:
                sock.close()
            except Exception:
                pass

        time.sleep(RECONNECT_DELAY)
        # Reload sensor map on reconnect in case plants were added
        sensor_map = load_sensor_map(SENSOR_MAP_PATH)


if __name__ == "__main__":
    main()
