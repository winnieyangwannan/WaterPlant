# Arduino Serial Monitor Bridge Setup

**Date:** 2026-04-22
**Setup:** Xiaoxia (VPS) ←→ Winnie's Mac ←→ Arduino Uno

---

## Overview

Xiaoxia runs on a VPS. The Arduino Uno is physically connected to Winnie's Mac via USB. This setup creates a remote serial monitor bridge so Xiaoxia can read Arduino serial output from the VPS.

**Architecture:**
```
Arduino Uno → USB → Mac (/dev/cu.usbmodem1301) → socat (TCP:12345) → SSH reverse tunnel → VPS (localhost:12345) → nc
```

---

## Prerequisites

- macOS with Homebrew installed
- Arduino IDE (for uploading sketches)
- SSH access from Mac to VPS (`clawd@2.24.221.71`)
- Existing SSH tunnel for OpenClaw dashboard: `ssh -N -L 18789:127.0.0.1:18789 clawd@2.24.221.71`

---

## Step 1: Find Arduino Serial Port

**Via Arduino IDE:**
- Tools → Port → note the port (e.g., `/dev/cu.usbmodem1301`)

**Via Terminal:**
```bash
ls /dev/cu.usbmodem* /dev/cu.usbserial*
```

**Our port:** `/dev/cu.usbmodem1301`

---

## Step 2: Install socat (One-Time)

```bash
brew install socat
```

---

## Step 3: Configure Serial Port

Set baud rate and raw mode (run once before starting socat):

```bash
socat TCP-LISTEN:12345,reuseaddr,fork FILE:/dev/cu.usbmodem11301,rawer,echo=0 &
```

**Parameters:**
- `115200` — baud rate (match `Serial.begin(115200)` in Arduino sketch)
- `cs8` — 8 data bits
- `-cstopb` — 1 stop bit
- `-parenb` — no parity
- `raw` — raw mode (no processing)
- `-echo` — disable local echo

---

## Step 4: Start socat (Terminal 1)

Expose the serial port over TCP on localhost:12345:

```bash
socat TCP-LISTEN:12345,reuseaddr,fork FILE:/dev/cu.usbmodem1301,rawer,echo=0 &
```

**What this does:**
- `TCP-LISTEN:12345` — listen on TCP port 12345
- `reuseaddr` — allow port reuse
- `fork` — handle multiple connections
- `FILE:/dev/cu.usbmodem1301` — connect to Arduino serial port
- `rawer` — raw data passthrough
- `echo=0` — disable echo
- `&` — run in background

**Verify it's running:**
```bash
jobs
```

**To stop:**
```bash
kill <PID>
```

---

## Step 5: Create SSH Reverse Tunnel (Terminal 2)

Forward VPS port 12345 back to Mac's port 12345:

```bash
ssh -N -R 12345:localhost:12345 clawd@2.24.221.71
```

**What this does:**
- `-N` — no remote command (port forwarding only)
- `-R 12345:localhost:12345` — reverse tunnel: VPS:12345 → Mac:12345
- Keep this running

**Enter password when prompted.**

---

## Step 6: Xiaoxia Connects from VPS

Xiaoxia reads the serial data using:

```bash
nc localhost 12345
```

Or for a timed read:
```bash
timeout 10 nc localhost 12345
```

---

## Example Arduino Sketch

Upload this to test the connection:

```cpp
void setup() {
  Serial.begin(115200);
}

void loop() {
  Serial.println("Hello from Arduino!");
  delay(1000);
}
```

**Important:** Close Arduino IDE's Serial Monitor before starting socat — only one program can use the serial port at a time.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `command not found: socat` | Run `brew install socat` |
| `unknown option "b115200"` | Use `stty` to set baud rate first, then run socat without `b115200` |
| Connection refused on VPS | Ensure SSH tunnel is running and socat is listening |
| No data received | Check Arduino is powered, sketch is uploaded, baud rates match |
| Garbled characters | Ensure baud rate matches between Arduino and stty config |
| Arduino resets on connect | This is normal (DTR signal). Add delay in setup() if needed |

---

## Security Notes

- socat binds to `localhost` only — not reachable from other machines on your network
- SSH tunnel encrypts all traffic between Mac and VPS
- Only serial data is exposed, not filesystem or shell access
- Port 12345 on VPS is accessible to anyone on the VPS — but only carries Arduino serial output

---

## Quick Reference (Copy-Paste)

**Terminal 1 (Mac):**
```bash
stty -f /dev/cu.usbmodem1301 115200 cs8 -cstopb -parenb raw -echo
socat TCP-LISTEN:12345,reuseaddr,fork FILE:/dev/cu.usbmodem1301,rawer,echo=0 &
```

**Terminal 2 (Mac):**
```bash
ssh -N -R 12345:localhost:12345 clawd@2.24.221.71
```

**VPS (Xiaoxia):**
```bash
nc localhost 12345
```

---

*Setup completed successfully on 2026-04-22. Serial data flowing: "Hello from Arduino!"*
