// Calibration sketch — upload this first before using WaterPlant.ino.
//
// Steps:
//   1. Hold sensor in dry air for 10 seconds → note the "Raw" value → SENSOR_DRY
//   2. Submerge sensor tip in water for 10 seconds → note the "Raw" value → SENSOR_WET
//   3. Copy both values into WaterPlant/config.h

#define MOISTURE_PIN A0

void setup() {
    Serial.begin(9600);
    Serial.println(F("Calibration mode — open Serial Monitor at 9600 baud"));
    Serial.println(F("Raw ADC value printed every second."));
    Serial.println(F("Dry air value → SENSOR_DRY | In water value → SENSOR_WET"));
}

void loop() {
    int raw = analogRead(MOISTURE_PIN);
    Serial.print(F("Raw: "));
    Serial.println(raw);
    delay(1000);
}
