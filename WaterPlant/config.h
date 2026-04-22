#pragma once

// ── Pins ──────────────────────────────────────────────────────────────────────
#define MOISTURE_PIN      A0
#define RELAY_PIN         7

// ── Sensor calibration ────────────────────────────────────────────────────────
// Run calibrate/calibrate.ino first to find your sensor's actual range.
#define SENSOR_DRY        620   // raw ADC in dry air (higher = drier)
#define SENSOR_WET        310   // raw ADC fully submerged (lower = wetter)

// ── Moisture thresholds ───────────────────────────────────────────────────────
#define MOISTURE_LOW      30    // % — trigger watering below this
#define MOISTURE_HIGH     60    // % — stop watering above this

// ── Timing ────────────────────────────────────────────────────────────────────
#define READ_INTERVAL_MS  60000UL   // how often to read + log (ms)
#define PUMP_MAX_MS       3000UL    // max pump run per watering event (ms)
#define PUMP_COOLDOWN_MS  300000UL  // minimum gap between waterings (ms)

// ── Averaging ─────────────────────────────────────────────────────────────────
#define SAMPLE_COUNT      10    // ADC samples per reading (min/max discarded)
