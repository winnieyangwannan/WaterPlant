
[[2026-04-21]]
## 1. Open Arduino IDE

Launch the Arduino IDE app on your Mac.

## 2. Create a New Sketch

- File → New (or Cmd+N)
- You'll see a blank window with `setup()` and `loop()` functions

## 3. Replace the Code

Delete everything in the editor and paste this:

```cpp
void setup() {
  Serial.begin(115200);
}

void loop() {
  Serial.println("Hello from Arduino!");
  delay(1000);
}
```

## 4. Select Your Board

- Tools → Board → Arduino AVR Boards → Arduino Uno

## 5. Select Your Port

- Tools → Port → `/dev/cu.usbmodem1301 (Arduino Uno)`

## 6. Upload

- Click the **→ (Upload)** button (top left, arrow pointing right)
- Or Sketch → Upload (Cmd+U)

You'll see "Compiling sketch..." then "Uploading..." at the bottom. Wait for "Done uploading."

## 7. Check Serial Monitor (Locally First)

- Tools → Serial Monitor (or Cmd+Shift+M)
- Set baud rate to **115200** (dropdown at bottom right)
- You should see "Hello from Arduino!" printing every second

## 8. Close Serial Monitor

**Important:** Only one program can use the serial port at a time. Close the Arduino Serial Monitor so `socat` can access it.

---

Once you've uploaded and closed the Serial Monitor, I'll be able to read it from here. Let me know when you're done!