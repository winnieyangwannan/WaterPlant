# Arduino Automatic Plant Watering System — Plan

## Context

Build a standalone automatic plant watering system using Arduino Uno. It monitors soil moisture in real-time and waters the plant only when needed. Logging is via Serial Monitor (CSV-formatted output) — no SD card or RTC module required.

---

## Hardware You Have

| Item | Model | Role |
|------|-------|------|
| [Arduino Uno REV3](https://www.amazon.com/dp/B008GRTSV6) | ATmega328P | Main controller |
| [Capacitive Soil Moisture Sensor](https://www.amazon.com/dp/B07H3P1NRM) | Gikfun EK1940 ×2 | Analog moisture reading (corrosion-resistant) |
| [5V Relay Module](https://www.amazon.com/dp/B00VRUAHLE) | Tolako 1-channel | Switches pump power circuit |
| [Mini Water Pump](https://www.amazon.com/dp/B07DW4WRV8) | Gikfun R385 | 6–12V DC, includes 1m tube |
| 12V DC Adapter | (you have one) | Powers the pump through relay |
| [Breadboards Kit](https://www.amazon.com/dp/B07DL13RZH) | 830pt + 400pt ×2 | Prototyping |
| [Jumper Wires](https://www.amazon.com/dp/B07GD3KDG9) | EDGELEC 120pcs 50cm | M-F, M-M, F-F |

## Additional Items Still Needed

| Item | Why | Note |
|------|-----|------|
| Water reservoir | Holds the water supply | Any bucket, bottle, or container |
| Extra silicone tubing | Route water from pump to plant | Pump includes 1m; extend if needed |
| USB cable (Type-B) | Program Arduino + Serial Monitor | Likely already have one |

---

## Wiring Diagram

### Reference Wiring (ArduinoGetStarted.com)
![Reference Wiring Diagram](images/reference_wiring.jpg)
*Source: [arduinogetstarted.com](https://arduinogetstarted.com/tutorials/arduino-soil-moisture-sensor-pump)*

### Full Diagram (all your exact components)
![Wiring Diagram](images/wiring_diagram.png)

> Reference diagrams from similar builds:
> - [Arduino + Soil Moisture + Relay + Pump (arduinogetstarted.com)](https://arduinogetstarted.com/tutorials/arduino-soil-moisture-sensor-pump)
> - [Capacitive Sensor Circuit Diagram (electroniclinic.com)](https://www.electroniclinic.com/capacitive-soil-moisture-sensor-arduino-circuit-diagram-and-programming/)



### Pin Summary Table

| Wire | From | To | Color suggestion |
|------|------|----|-----------------|
| Power | Arduino 5V | Sensor VCC | Red |
| Ground | Arduino GND | Sensor GND | Black |
| Signal | Sensor AOUT | Arduino A0 | Yellow |
| Power | Arduino 5V | Relay VCC | Red |
| Ground | Arduino GND | Relay GND | Black |
| Control | Arduino D7 | Relay IN | Orange |
| Pump power | 12V adapter (+) | Relay COM | Red (thick) |
| Pump positive | Relay NO | Pump (+) | Red (thick) |
| Pump negative | Pump (−) | 12V adapter (−) | Black (thick) |
| Shared ground | 12V adapter (−) | Arduino GND | Black |

### Relay Terminal Positions (Tolako module, left to right)

```
  ┌─────────────────────────────────────┐
  │  TOLAKO RELAY MODULE — TOP VIEW     │
  │                                     │
  │  Control side:    Load side:        │
  │  [VCC][GND][IN]   [NC][COM][NO]     │
  │    │    │    │      │    │    │     │
  │    │    │    │      X  USE  USE     │
  │    │    │    │    (not  ↑    ↑      │
  │    │    │    │    used) │    │      │
  └────┼────┼────┼──────────┼────┼─────┘
       │    │    │          │    │
      5V   GND  D7        12V(+) Pump(+)
  (Arduino)(Arduino)(Arduino)
```

> **NC = Normally Closed** (connected when relay is OFF — do NOT use this terminal)
> **NO = Normally Open** (connected when relay is ON / pump runs — use this one)
> **COM = Common** (always connected, this is your 12V input)

> **Safety rule**: The 12V and 5V circuits share only the GND rail. Never connect 12V to any Arduino pin.

---

## Code Architecture

```
WaterPlant/
├── WaterPlant.ino    # Main sketch: setup + loop
├── config.h          # All tunable constants (pins, thresholds, timing)
├── moisture.h        # Sensor read, averaging, map to %
└── pump.h            # Relay control with safety limits
```

### config.h
```cpp
// Pins
#define MOISTURE_PIN      A0
#define RELAY_PIN         7

// Sensor calibration (run calibration sketch first)
#define SENSOR_DRY        620   // ADC value in dry air
#define SENSOR_WET        310   // ADC value fully submerged

// Moisture thresholds
#define MOISTURE_LOW      30    // % — start watering below this
#define MOISTURE_HIGH     60    // % — stop watering above this

// Timing
#define READ_INTERVAL_MS  60000UL   // read & log every 60 seconds
#define PUMP_MAX_MS       3000UL    // max pump runtime per trigger
#define PUMP_COOLDOWN_MS  300000UL  // 5-min cooldown between waterings
```

### Main loop logic (WaterPlant.ino)
```
setup():
  Serial.begin(9600)
  print CSV header: "millis,moisture_pct,pump_state"
  relay pin → OUTPUT, LOW (pump OFF)

loop():
  every READ_INTERVAL_MS:
    pct = readMoisture()           // average 10 ADC samples → map to %
    Serial.println(millis + "," + pct + "," + pumpState)

    if pct < MOISTURE_LOW AND cooldownElapsed:
      pump ON  → Serial.println(... "PUMP_ON")
      wait PUMP_MAX_MS
      pump OFF → Serial.println(... "PUMP_OFF")
      record cooldown start
```

### moisture.h — reading logic
- Take 10 ADC samples, discard min/max, average the rest (noise reduction)
- `map(avg, SENSOR_DRY, SENSOR_WET, 0, 100)` → moisture percentage
- Clamp to 0–100%

### pump.h — safety logic
- `pumpOn()`: digitalWrite(RELAY_PIN, HIGH) + record start time
- `pumpOff()`: digitalWrite(RELAY_PIN, LOW)
- Hard safety: if pump has been ON > PUMP_MAX_MS, force off
- Cooldown enforced by timestamp comparison in main loop

### Serial Monitor output (CSV)
```
millis,moisture_pct,pump_state
0,--,INIT
60000,24,
60000,24,PUMP_ON
63000,24,PUMP_OFF
120000,38,
180000,55,
```
Copy-paste into Excel/Sheets for charting.

---

## Implementation Phases

### Phase 1 — Calibrate sensor
1. Upload `calibrate/calibrate.ino` (prints raw ADC value every second)
2. Hold sensor in dry air → note value → set `SENSOR_DRY` in config.h
3. Dip sensor in water → note value → set `SENSOR_WET` in config.h

### Phase 2 — Basic wiring + no-pump test
1. Wire moisture sensor to A0
2. Upload main sketch with relay pin wired but pump NOT connected
3. Verify Serial Monitor shows correct moisture % as you move sensor wet/dry

### Phase 3 — Add pump + relay
1. Wire relay to D7 and connect pump circuit with 12V adapter
2. Set `MOISTURE_LOW = 90` temporarily → pump should trigger immediately
3. Verify pump activates and stops after `PUMP_MAX_MS`
4. Reset thresholds to real values

### Phase 4 — Field test
1. Insert sensor in plant soil
2. Let run for several hours
3. Copy Serial Monitor log to spreadsheet and plot moisture over time

---

## Libraries Required
All built-in to Arduino IDE — no installs needed.

---

## Learning Resources & Tutorials

| Topic | Resource |
|-------|----------|
| Breadboard basics | [How to Use a Breadboard — YouTube](http://youtube.com/watch?v=zvCdkV52cis) |

---

## Reference Projects
- [Automatic Watering System - Arduino Project Hub](https://projecthub.arduino.cc/lc_lab/automatic-watering-system-for-my-plants-e4c4b9)
- [Soil Moisture Sensor with LCD, RTC, SD Logger - Instructables](https://www.instructables.com/Soil-Moisture-Sensor-LCD-RTC-SD-Logger-Temperature/)
- [SriTu Hobby — Step by step irrigation guide](https://srituhobby.com/how-to-make-an-automatic-irrigation-and-plant-watering-system-using-arduino-and-soil-moisture-sensor-step-by-step-instruction/)
