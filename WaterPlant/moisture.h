#pragma once
#include <Arduino.h>
#include "config.h"

// Returns soil moisture as a percentage (0 = bone dry, 100 = saturated).
// Takes SAMPLE_COUNT ADC readings, discards the highest and lowest, and
// averages the rest to reduce electrical noise.
inline int readMoisturePct() {
    int samples[SAMPLE_COUNT];
    for (int i = 0; i < SAMPLE_COUNT; i++) {
        samples[i] = analogRead(MOISTURE_PIN);
        delay(10);
    }

    // Selection-sort just to find min/max without a full sort
    int minVal = samples[0], maxVal = samples[0];
    long sum = 0;
    for (int i = 0; i < SAMPLE_COUNT; i++) {
        if (samples[i] < minVal) minVal = samples[i];
        if (samples[i] > maxVal) maxVal = samples[i];
        sum += samples[i];
    }
    sum -= minVal + maxVal;
    int avg = sum / (SAMPLE_COUNT - 2);

    // Capacitive sensor: higher raw value = drier soil
    int pct = map(avg, SENSOR_DRY, SENSOR_WET, 0, 100);
    return constrain(pct, 0, 100);
}
