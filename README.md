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

## Project Structure

```
WaterPlant/
├── WaterPlant/          # Main Arduino sketch
├── calibrate/           # Sensor calibration tools
├── lesson/              # Guides & tutorials
│   └── Openclaw_Arduino_Serial_Monitor.md
├── generate_diagram.py  # Wiring diagram generator
├── wiring_diagram.png   # Visual wiring reference
├── plan.md              # Project roadmap
└── README.md            # This file
```

## Quick Start

### Hardware Needed
- Arduino Uno
- Soil moisture sensor(s)
- Water pump + relay module
- Power supply
- Jumper wires

### Software Setup
1. **Upload Arduino sketch** — Open `WaterPlant/` in Arduino IDE, select your board/port, upload
2. **Set up serial bridge** — Follow [this guide](lesson/Openclaw_Arduino_Serial_Monitor.md) to connect Arduino to Xiaoxia
3. **Chat with Xiaoxia** — Ask "Check my plants" or "Water the plants"

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
