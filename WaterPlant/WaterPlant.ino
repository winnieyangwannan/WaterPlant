#include "config.h"
#include "moisture.h"
#include "pump.h"

static unsigned long lastReadMs = 0;

void logRow(unsigned long ts, int pct, const char* event) {
    Serial.print(ts);
    Serial.print(',');
    Serial.print(pct);
    Serial.print(',');
    Serial.println(event);
}

void setup() {
    Serial.begin(9600);
    while (!Serial) {}  // wait for Serial on Leonardo/Micro; instant on Uno

    pumpSetup();
    pinMode(MOISTURE_PIN, INPUT);

    Serial.println(F("millis,moisture_pct,event"));
    logRow(millis(), 0, "INIT");

    // Force a first reading immediately
    lastReadMs = millis() - READ_INTERVAL_MS;
}

void loop() {
    pumpSafetyCheck();  // enforce hard pump time limit every iteration

    unsigned long now = millis();

    if (now - lastReadMs >= READ_INTERVAL_MS) {
        lastReadMs = now;

        int pct = readMoisturePct();
        logRow(now, pct, "");  // regular reading row

        if (pct < MOISTURE_LOW && !pumpIsRunning() && pumpCooldownElapsed()) {
            logRow(now, pct, "PUMP_ON");
            pumpOn();
            delay(PUMP_MAX_MS);
            pumpOff();
            logRow(millis(), pct, "PUMP_OFF");
        }
    }
}
