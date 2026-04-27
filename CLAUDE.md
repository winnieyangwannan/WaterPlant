# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Arduino-based automatic plant watering system. Written in C/C++ for Arduino Uno (ATmega328P). No package manager or external build system — compilation and uploading is handled by the Arduino IDE.

## Development Workflow

**Upload to Arduino**: Open `.ino` files in Arduino IDE, select board (Arduino Uno) and port, then use Verify/Upload.

**Calibration**: Before deploying, run `calibrate/calibrate.ino` to find the sensor's real dry/wet ADC values, then update `SENSOR_DRY` and `SENSOR_WET` in `WaterPlant/config.h`.

**Serial monitoring**: Connect at 9600 baud to view CSV-formatted moisture readings and pump events.

## Architecture

All tunable constants live in `WaterPlant/config.h` — this is the single place to change pins, thresholds, timing, and calibration values. Everything else reads from there.

**Main control loop** (`WaterPlant/WaterPlant.ino`):
1. Every iteration: run `pumpSafetyCheck()` to enforce hard pump time limit
2. Every `READ_INTERVAL_MS` (60s): read moisture, log CSV to Serial
3. If moisture < `MOISTURE_LOW` AND pump idle AND cooldown elapsed → run pump for `PUMP_MAX_MS`

**Module responsibilities**:
- `config.h` — all constants (pins, thresholds, timing, calibration)
- `moisture.h` — ADC reads (10 samples, discard min/max), maps raw → percentage
- `pump.h` — relay control with safety limits and cooldown enforcement

**Pin assignments** (from `config.h`):
- `A0` — capacitive moisture sensor
- `D7` — relay module (HIGH = pump on)

**Safety invariants**: The pump has a hard `PUMP_MAX_MS` (3s) cutoff enforced every loop iteration, plus a `PUMP_COOLDOWN_MS` (5min) minimum gap between waterings. Do not remove these checks.

## Serial Output Format

CSV with header `millis,moisture_pct,event`. Events: `INIT`, `PUMP_ON`, `PUMP_OFF`. Empty event field = routine reading.
