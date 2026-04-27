# Static Site Generator - renders YAML to HTML
# Designed for GitHub Pages deployment.

import os
import yaml
import sys
from datetime import datetime, timezone, timedelta
from jinja2 import Environment, FileSystemLoader


# --- Config ---
REPO_DIR = "/home/clawd/WaterPlant"
PLANTS_DIR = os.path.join(REPO_DIR, "plants")
TEMPLATES_DIR = os.path.join(REPO_DIR, "server", "templates") # Assuming templates are still there
OUTPUT_DIR = REPO_DIR # GitHub Pages looks in the root of the repo
PHOTOS_BASE_URL = "/WaterPlant/photos/" # Adjust if your repo is a sub-path

# Helper function to format datetime to ISO string without microseconds
def format_iso(dt):
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return dt

# Helper function to format date for display
def format_date_display(dt):
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d")
    return str(dt)

# Global time_ago function for templates
def time_ago(iso_str):
    if not iso_str: return "never"
    try:
        if iso_str.endswith("Z"):
            dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(iso_str).astimezone(timezone.utc)
        now = datetime.now(timezone.utc)
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 0: return "in the future"
        elif seconds < 60: return f"{seconds}s ago"
        elif seconds < 3600: return f"{seconds // 60}m ago"
        elif seconds < 86400: return f"{seconds // 3600}h ago"
        else: return f"{seconds // 86400}d ago"
    except Exception as e:
        print(f"[time_ago] Error formatting {iso_str}: {e}", file=sys.stderr)
        return iso_str

def load_plant_yaml(plant_id):
    path = os.path.join(PLANTS_DIR, f"{plant_id}.yaml")
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            # Ensure dates and times are loaded as datetime objects if possible
            if data and 'added_at' in data:
                try:
                    data['added_at'] = datetime.fromisoformat(data['added_at']).astimezone(timezone.utc)
                except (ValueError, TypeError):
                    pass # Keep as string if parsing fails
            if data and 'latest_reading' in data and data['latest_reading'] and 'recorded_at' in data['latest_reading']:
                 try:
                    data['latest_reading']['recorded_at'] = datetime.fromisoformat(data['latest_reading']['recorded_at']).astimezone(timezone.utc)
                 except (ValueError, TypeError):
                    pass
            if data and 'readings_history' in data:
                for reading in data['readings_history']:
                    try:
                        reading['recorded_at'] = datetime.fromisoformat(reading['recorded_at']).astimezone(timezone.utc)
                    except (ValueError, TypeError):
                        pass
            return data
    except FileNotFoundError:
        return None

def get_all_plant_ids():
    ids = []
    for fname in os.listdir(PLANTS_DIR):
        if fname.endswith(".yaml") and not fname.startswith("_"):
            try:
                ids.append(int(fname.replace(".yaml", "")))
            except ValueError:
                pass
    return sorted(ids)

def render_plant_page(plant_data, env):
    """Render a single plant's page."""
    template = env.get_template("plant.html.j2")
    html = template.render(
        plant=plant_data,
        latest=plant_data.get("latest_reading"),
        sensor_status=time_ago(plant_data.get('latest_reading', {}).get('recorded_at')) if plant_data.get('latest_reading') else "no data",
        chart_data=json.dumps([
            {"t": r["recorded_at"].isoformat() if isinstance(r.get("recorded_at"), datetime) else r.get("recorded_at"), "v": r["moisture_pct"]}
            for r in plant_data.get("readings_history", [])
        ]),
        waterings=plant_data.get("watering_events", []), # Assuming this might be added later
        time_ago=time_ago,
        now=datetime.now(timezone.utc).isoformat(),
    )
    return html

def render_index_page(all_plants_data, env):
    """Render the main index page listing all plants."""
    template = env.get_template("index.html.j2")
    
    # Prepare simplified plant data for the index page
    simplified_plants = []
    for plant_id, plant_data in all_plants_data.items():
        latest = plant_data.get("latest_reading")
        simplified_plants.append({
            "id": plant_id,
            "name": plant_data.get("name", f"Plant {plant_id}"),
            "species": plant_data.get("species", "Unknown"),
            "latest": latest,
            "sensor_status": time_ago(latest["recorded_at"]) if latest else "no data",
        })
        
    html = template.render(plants=simplified_plants, time_ago=time_ago, now=datetime.now(timezone.utc).isoformat())
    return html

def main():
    print("[Static Site Gen] Starting site generation...")
    
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)
    env.globals['time_ago'] = time_ago
    env.globals['format_date_display'] = format_date_display # Make available for {{ plant.added_at | format_date_display }} in jinja
    env.filters['strftime'] = lambda dt, fmt: dt.strftime(fmt) if isinstance(dt, datetime) else str(dt) # For {{ date_obj | strftime('%Y-%m-%d') }}

    all_plants_data = {}
    plant_ids = get_all_plant_ids()
    
    if not plant_ids:
        print("[Static Site Gen] No plant YAML files found. Exiting.")
        sys.exit(0)

    for pid in plant_ids:
        data = load_plant_yaml(pid)
        if data:
            all_plants_data[pid] = data
            html = render_plant_page(data, env)
            
            # Save individual plant pages
            out_path = os.path.join(OUTPUT_DIR, f"{pid}.html")
            with open(out_path, "w") as f:
                f.write(html)
            print(f"[Static Site Gen] Wrote {out_path}")

    # Generate index page
    index_html = render_index_page(all_plants_data, env)
    out_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(out_path, "w") as f:
        f.write(index_html)
    print(f"[Static Site Gen] Wrote {out_path}")

    print("[Static Site Gen] Site generation complete.")

if __name__ == "__main__":
    main()
