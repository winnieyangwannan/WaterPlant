#!/usr/bin/env python3
"""
daily_reading.py — connects to the Arduino serial bridge, grabs moisture
readings for ~2 minutes, averages them, updates plants/*.yaml with the
latest reading, then commits and pushes to GitHub.

Designed to be run once daily via cron.
"""

import socket
import sys
import os
import yaml
import subprocess
from datetime import datetime, timezone

# --- Config ---
BRIDGE_HOST = "localhost"
BRIDGE_PORT = 12345
REPO_DIR = "/home/clawd/WaterPlant"
PLANTS_DIR = os.path.join(REPO_DIR, "plants")
SENSOR_MAP_PATH = os.path.join(PLANTS_DIR, "_sensor_map.yaml")
READ_DURATION_SECS = 120  # collect readings for 2 minutes, then average


def load_sensor_map(path):
    """Load sensor_idx -> plant_id mapping from YAML."""
    try:
        with open(path, "r") as f:
            raw = yaml.safe_load(f)
        if raw is None:
            return {}
        return {int(k): int(v) for k, v in raw.items()}
    except Exception as e:
        print(f"[daily] WARNING: could not load sensor map: {e}", file=sys.stderr)
        return {}


def collect_readings(duration_secs, sensor_map):
    """Connect to serial bridge, collect readings for `duration_secs`, return {plant_id: [pct, ...]}."""
    import time

    readings = {}  # plant_id -> [moisture_pct, ...]
    print(f"[daily] Connecting to {BRIDGE_HOST}:{BRIDGE_PORT}...")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((BRIDGE_HOST, BRIDGE_PORT))
        print(f"[daily] Connected! Collecting readings for {duration_secs}s...")
    except Exception as e:
        print(f"[daily] ERROR: Could not connect to serial bridge: {e}", file=sys.stderr)
        return readings

    start = time.time()
    buf = ""

    try:
        while time.time() - start < duration_secs:
            try:
                data = sock.recv(4096)
            except socket.timeout:
                continue
            if not data:
                print("[daily] Bridge closed connection", file=sys.stderr)
                break

            buf += data.decode("utf-8", errors="replace")
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if not line or line.startswith("millis"):
                    continue

                parts = line.split(",")
                if len(parts) == 3:
                    _, moisture_str, _ = parts
                    sensor_idx = 0
                elif len(parts) == 4:
                    _, sensor_idx_str, moisture_str, _ = parts
                    try:
                        sensor_idx = int(sensor_idx_str.strip())
                    except ValueError:
                        continue
                else:
                    continue

                moisture_str = moisture_str.strip()
                if moisture_str == "--":
                    continue

                try:
                    moisture_pct = int(moisture_str)
                except ValueError:
                    continue

                plant_id = sensor_map.get(sensor_idx)
                if plant_id is not None:
                    readings.setdefault(plant_id, []).append(moisture_pct)
                    print(f"[daily]   sensor {sensor_idx} -> plant {plant_id}: {moisture_pct}%")
    finally:
        sock.close()

    return readings


def update_plant_yaml(plant_id, avg_moisture):
    """Update a plant's YAML file with the latest moisture reading."""
    path = os.path.join(PLANTS_DIR, f"{plant_id}.yaml")
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"[daily] WARNING: {path} not found, skipping", file=sys.stderr)
        return False

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Add/update the latest_reading block
    if "readings_history" not in data:
        data["readings_history"] = []

    data["latest_reading"] = {
        "moisture_pct": avg_moisture,
        "recorded_at": now,
    }

    # Append to readings_history (keep last 90 entries = ~3 months daily)
    data["readings_history"].append({
        "moisture_pct": avg_moisture,
        "recorded_at": now,
    })
    data["readings_history"] = data["readings_history"][-90:]

    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"[daily] Updated {path}: moisture={avg_moisture}% at {now}")
    return True


def git_commit_and_push():
    """Commit updated YAML files and push to GitHub."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    os.chdir(REPO_DIR)

    try:
        subprocess.run(["git", "add", "plants/"], check=True)

        # Check if there are changes to commit
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if result.returncode == 0:
            print("[daily] No changes to commit")
            return

        subprocess.run(
            ["git", "commit", "-m", f"daily reading: {now}"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)
        print(f"[daily] Committed and pushed to GitHub")
    except subprocess.CalledProcessError as e:
        print(f"[daily] ERROR: git operation failed: {e}", file=sys.stderr)


def main():
    print(f"[daily] === Daily moisture reading — {datetime.now(timezone.utc).isoformat()} ===")

    sensor_map = load_sensor_map(SENSOR_MAP_PATH)
    if not sensor_map:
        print("[daily] ERROR: sensor map is empty, nothing to do", file=sys.stderr)
        sys.exit(1)

    print(f"[daily] Sensor map: {sensor_map}")

    # Collect readings
    readings = collect_readings(READ_DURATION_SECS, sensor_map)

    if not readings:
        print("[daily] WARNING: no readings collected — is the Arduino connected?", file=sys.stderr)
        sys.exit(1)

    # Average and update each plant
    updated = False
    for plant_id, values in readings.items():
        avg = round(sum(values) / len(values))
        print(f"[daily] Plant {plant_id}: {len(values)} readings, avg={avg}%")
        if update_plant_yaml(plant_id, avg):
            updated = True

    # Commit and push if anything changed
    if updated:
        git_commit_and_push()
    else:
        print("[daily] No plants updated")

    print("[daily] Done!")


if __name__ == "__main__":
    main()
