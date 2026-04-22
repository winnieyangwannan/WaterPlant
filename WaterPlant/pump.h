#pragma once
#include <Arduino.h>
#include "config.h"

static bool      _pumpRunning      = false;
static unsigned long _pumpStartMs  = 0;
static unsigned long _lastWaterMs  = 0;  // millis() at last pump-off

inline void pumpSetup() {
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, LOW);  // relay off = pump off
}

inline void pumpOn() {
    if (_pumpRunning) return;
    digitalWrite(RELAY_PIN, HIGH);
    _pumpRunning = true;
    _pumpStartMs = millis();
}

inline void pumpOff() {
    digitalWrite(RELAY_PIN, LOW);
    if (_pumpRunning) {
        _lastWaterMs = millis();
    }
    _pumpRunning = false;
}

inline bool pumpCooldownElapsed() {
    return (millis() - _lastWaterMs) >= PUMP_COOLDOWN_MS;
}

// Call every loop iteration to enforce the hard time limit.
inline void pumpSafetyCheck() {
    if (_pumpRunning && (millis() - _pumpStartMs) >= PUMP_MAX_MS) {
        pumpOff();
    }
}

inline bool pumpIsRunning() {
    return _pumpRunning;
}
