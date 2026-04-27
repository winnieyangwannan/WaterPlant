#!/usr/bin/env python3
"""
render.py — generates static HTML plant profile pages from SQLite + YAML.

Usage:
    python render.py              # render all plants
    python render.py 1            # render plant_id=1 only
    python render.py --rebuild-sensor-map   # regenerate _sensor_map.yaml
"""

import sqlite3
import yaml
import os
import sys
import json
from datetime import datetime, timezone, timedelta
from jinja2 import Environment, FileSystemLoader

# --- Config ---
DB_PATH = "/var/lib/waterplant/waterplant.db"
PLANTS_DIR = "/home/clawd/WaterPlant/plants"
TEMPLATES_DIR = "/home/clawd/WaterPlant/server/templates"
OUTPUT_DIR = "/var/www/waterplant"
PHOTOS_DIR = "/var/lib/waterplant/photos"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def load_plant_yaml(plant_id):
    path = os.path.join(PLANTS_DIR, f"{plant_id}.yaml")
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return None


def get_all_plant_ids():
    """Get plant IDs from YAML files in plants/ dir."""
    ids = []
    for fname in os.listdir(PLANTS_DIR):
        if fname.endswith(".yaml") and not fname.startswith("_"):
            try:
                ids.append(int(fname.replace(".yaml", "")))
            except ValueError:
                pass
    return sorted(ids)


def get_latest_reading(conn, plant_id):
    row = conn.execute(
        "SELECT moisture_pct, recorded_at FROM readings "
        "WHERE plant_id = ? ORDER BY recorded_at DESC LIMIT 1",
        (plant_id,),
    ).fetchone()
    if row:
        return {"moisture_pct": row["moisture_pct"], "recorded_at": row["recorded_at"]}
    return None


def get_readings_history(conn, plant_id, days=30):
    """Get readings for the moisture chart (last N days)."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT moisture_pct, recorded_at FROM readings "
        "WHERE plant_id = ? AND recorded_at > ? ORDER BY recorded_at ASC",
        (plant_id, cutoff),
    ).fetchall()
    return [{"moisture_pct": r["moisture_pct"], "recorded_at": r["recorded_at"]} for r in rows]


def get_watering_events(conn, plant_id, limit=20):
    """Get recent watering events."""
    rows = conn.execute(
        "SELECT started_at, ended_at, moisture_before, moisture_after, "
        "duration_ms, trigger_source FROM watering_events "
        "WHERE plant_id = ? ORDER BY started_at DESC LIMIT ?",
        (plant_id, limit),
    ).fetchall()
    return [dict(r) for r in rows]


def time_ago(iso_str):
    """Convert ISO timestamp to human-readable 'N min ago'."""
    if not iso_str:
        return "never"
    try:
        # Ensure it's treated as timezone-aware UTC, even if 'Z' is missing
        if iso_str.endswith('Z'):
            dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(iso_str).astimezone(timezone.utc) # Assume local if no tz, then convert to UTC

        now = datetime.now(timezone.utc)
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 0: # Handle future dates gracefully, though unlikely
            return "in the future"
        elif seconds < 60:
            return f"{seconds}s ago"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        elif seconds < 86400:
            return f"{seconds // 3600}h ago"
        else:
            return f"{seconds // 86400}d ago"
    except Exception as e:
        print(f"[time_ago] Error formatting {iso_str}: {e}", file=sys.stderr)
        return iso_str


def render_plant(conn, plant_id, env):
    """Render a single plant's dashboard page."""
    meta = load_plant_yaml(plant_id)
    if not meta:
        print(f"[render] No YAML found for plant {plant_id}, skipping")
        return

    # Ensure dates are handled correctly
    if 'added_at' in meta and isinstance(meta['added_at'], datetime):
        pass # Already a datetime object, likely from YAML parsing
    elif 'added_at' in meta:
        try:
            meta['added_at'] = datetime.fromisoformat(meta['added_at']).astimezone(timezone.utc)
        except (ValueError, TypeError):
            meta['added_at'] = datetime.now(timezone.utc) # Fallback

    latest = get_latest_reading(conn, plant_id)
    readings = get_readings_history(conn, plant_id, days=30)
    waterings = get_watering_events(conn, plant_id, limit=20)

    # Determine sensor health
    sensor_status = "unknown"
    if latest:
        sensor_status = time_ago(latest["recorded_at"])

    # Build chart data as JSON for embedded <script>
    chart_data = json.dumps(
        [{"t": r["recorded_at"], "v": r["moisture_pct"]} for r in readings]
    )

    template = env.get_template("plant.html.j2")
    html = template.render(
        plant=meta,
        latest=latest,
        sensor_status=sensor_status,
        chart_data=chart_data,
        waterings=waterings,
        time_ago=time_ago, # Make time_ago available in template
        now=datetime.now(timezone.utc).isoformat(),
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{plant_id}.html")
    with open(out_path, "w") as f:
        f.write(html)
    print(f"[render] Wrote {out_path}")


def render_index(conn, env):
    """Render an index page listing all plants."""
    plant_ids = get_all_plant_ids()
    plants = []
    for pid in plant_ids:
        meta = load_plant_yaml(pid)
        if meta:
            latest = get_latest_reading(conn, pid)
            plants.append({
                "id": pid,
                "name": meta.get("name", f"Plant {pid}"),
                "species": meta.get("species", "Unknown"),
                "latest": latest,
                "sensor_status": time_ago(latest["recorded_at"]) if latest else "no data",
            })

    template = env.get_template("index.html.j2")
    html = template.render(plants=plants, time_ago=time_ago, now=datetime.now(timezone.utc).isoformat()) # Make time_ago available
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(out_path, "w") as f:
        f.write(html)
    print(f"[render] Wrote {out_path}")


def rebuild_sensor_map():
    """Regenerate plants/_sensor_map.yaml from individual plant YAMLs."""
    mapping = {}
    for pid in get_all_plant_ids():
        meta = load_plant_yaml(pid)
        if meta and "sensor_idx" in meta:
            mapping[meta["sensor_idx"]] = pid

    out_path = os.path.join(PLANTS_DIR, "_sensor_map.yaml")
    lines = [
        "# Auto-generated from plants/*.yaml — do not hand-edit.",
        "# Used by server/logger.py to resolve sensor_idx -> plant_id at startup.",
        "# Regenerate with: python server/render.py --rebuild-sensor-map",
    ]
    for sidx in sorted(mapping):
        meta = load_plant_yaml(mapping[sidx])
        name = meta.get("name", "?") if meta else "?"
        lines.append(f"{sidx}: {mapping[sidx]}   # sensor_idx {sidx} -> {name}")

    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[render] Wrote {out_path}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--rebuild-sensor-map":
        rebuild_sensor_map()
        return

    conn = get_db()
    # Add time_ago to the global environment for all templates
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)
    env.globals['time_ago'] = time_ago

    if len(sys.argv) > 1:
        # Render specific plant
        try:
            plant_id = int(sys.argv[1])
            render_plant(conn, plant_id, env)
        except ValueError:
            print(f"[render] Invalid plant_id: {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)
    else:
        # Render all plants + index
        for pid in get_all_plant_ids():
            render_plant(conn, pid, env)
        render_index(conn, env)

    conn.close()
    print("[render] Done")


if __name__ == "__main__":
    main()
