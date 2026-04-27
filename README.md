# 🌱 WaterPlant

An Arduino-based automatic plant watering system managed by [Xiaoxia](https://github.com/xiaoxiaopenclaw) — my OpenClaw bot — so my plants stay alive while I'm away.

## Overview

WaterPlant is a smart irrigation system that combines:
- **Arduino Uno** — controls water pumps, reads soil moisture sensors
- **Xiaoxia (OpenClaw bot)** — monitors, manages, and waters remotely via Telegram
- **Serial bridge** — connects Arduino to Xiaoxia over the internet

## How It Works

```
Soil Sensors → Arduino → Serial → Mac → SSH Tunnel → VPS → Xiaoxia 🤖
                                              ↓
                                        Decision: Water?
                                              ↓
                                    Command back → Pump ON/OFF
```

## Features

- 🌡️ **Soil moisture monitoring** — real-time sensor readings
- 💧 **Automated watering** — triggered when soil gets too dry
- 📱 **Remote control** — manage everything from Telegram
- 📊 **Serial monitor bridge** — Xiaoxia reads Arduino output remotely
- 🏠 **Away mode** — plants stay watered while you travel

## 🔗 Quick Links

- 📋 **[Master plan](docs/plan.md)** — start here. Status snapshot, two-track overview, hardware track in full.
- 📊 [Dashboard plan](docs/dashboard_plan.md) — software track: data pipeline, dashboard, deployment, Xiaoxia integration.
- 📝 [Session log](docs/sessions/) — chronological "what did we do, why" notes.
- 🌐 [Live dashboard](https://winnieyangwannan.github.io/WaterPlant/) — public preview site.
- 🔌 [Wiring diagram](docs/images/wiring_diagram.png) — visual reference.
- 🛠️ [Serial bridge guide](docs/Openclaw_Arduino_Serial_Monitor.md) — connect Arduino to Xiaoxia.
- 📡 [Arduino serial bridge notes](docs/arduino-serial-bridge.md) — implementation details.

## 📊 Project Status

| Phase | Description | Status | Test Writeup |
|-------|-------------|--------|--------------|
| 1 | Calibrate moisture sensor | ✅ Done | [phase1_calibration.md](tests/phase1_calibration.md) |
| 2 | Basic wiring + no-pump test | ⏳ Next | — |
| 3 | Pump + relay integration | ⬜ TODO | — |
| 4 | Field test with real plant | ⬜ TODO | — |

## Project Structure

```
WaterPlant/
├── README.md                 # This file
├── CLAUDE.md                 # AI assistant instructions
│
├── WaterPlant/               # Main Arduino sketch
│   ├── WaterPlant.ino
│   ├── config.h              # Pins, thresholds, timing, calibration
│   ├── moisture.h            # Sensor read + averaging
│   └── pump.h                # Relay control + safety limits
├── calibrate/                # Calibration sketch (run first)
│   └── calibrate.ino
│
├── docs/                     # Project documentation
│   ├── plan.md               # Roadmap & implementation plan
│   ├── arduino-serial-bridge.md
│   └── images/
│       ├── wiring_diagram.png
│       └── reference_wiring.jpg
│
├── tests/                    # Phase test writeups
│   ├── phase1_calibration.md
│   └── images/
│       └── phase1_setup.jpg
│
├── tools/                    # Helper scripts
│   └── generate_diagram.py
│
└── lesson/                   # Guides & tutorials
    └── Openclaw_Arduino_Serial_Monitor.md
```

## Quick Start

### Hardware Needed
- Arduino Uno
- Capacitive soil moisture sensor
- Water pump + relay module
- 12V power supply
- Jumper wires + breadboard

See the [project plan](docs/plan.md) for exact models and wiring details.

### Software Setup
1. **Calibrate the sensor** — Open `calibrate/calibrate.ino` in Arduino IDE, upload, follow [`tests/phase1_calibration.md`](tests/phase1_calibration.md) to get your sensor's dry/wet ADC values
2. **Update calibration values** — Edit `WaterPlant/config.h` with your captured `SENSOR_DRY` and `SENSOR_WET`
3. **Upload main sketch** — Open `WaterPlant/` in Arduino IDE, upload to your Uno
4. **Set up serial bridge** — Follow [the bridge guide](docs/Openclaw_Arduino_Serial_Monitor.md) to connect Arduino to Xiaoxia
5. **Chat with Xiaoxia** — Ask "Check my plants" or "Water the plants"

## Xiaoxia Commands

| Command | What it does |
|---------|-------------|
| "Check soil moisture" | Reads current sensor values |
| "Water the plants" | Activates pump for set duration |
| "Plant status" | Full report: moisture, last watered, health |
| "Set threshold to 30%" | Adjusts when auto-watering triggers |

## Collaborators

- [@winnieyangwannan](https://github.com/winnieyangwannan) — Creator, plant parent
- [@xiaoxiaopenclaw](https://github.com/xiaoxiaopenclaw) — Digital familiar, watering assistant 🤖🦐

---

*Built with 💧 and 🤖 so no plant gets left behind.*
