from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 1020
img = Image.new('RGB', (W, H), '#FAFAFA')
draw = ImageDraw.Draw(img)

# ── Fonts ─────────────────────────────────────────────────────────────────────
def load_font(size):
    for path in [
        '/System/Library/Fonts/Helvetica.ttc',
        '/System/Library/Fonts/Arial.ttf',
        '/Library/Fonts/Arial.ttf',
    ]:
        try:
            return ImageFont.truetype(path, size)
        except:
            pass
    return ImageFont.load_default()

F_TITLE  = load_font(20)
F_COMP   = load_font(17)
F_PIN    = load_font(14)
F_SMALL  = load_font(12)
F_LEGEND = load_font(13)

# ── Colors ────────────────────────────────────────────────────────────────────
C_RED      = '#D32F2F'
C_BLACK    = '#212121'
C_YELLOW   = '#F9A825'
C_ORANGE   = '#E65100'
C_DKRED    = '#B71C1C'
C_GRAY     = '#757575'
C_DKGRAY   = '#424242'

# ── Helpers ───────────────────────────────────────────────────────────────────
def box(x1, y1, x2, y2, fill, outline, lw=2):
    draw.rectangle([x1, y1, x2, y2], fill=fill, outline=outline, width=lw)

def label(text, x, y, font, color=C_BLACK, anchor='lt'):
    draw.text((x, y), text, fill=color, font=font, anchor=anchor)

def dot(x, y, r=5, color=C_BLACK):
    draw.ellipse([x-r, y-r, x+r, y+r], fill=color)

def wire(pts, color, w=3):
    draw.line(pts, fill=color, width=w)

def dashed_wire(pts, color, w=2, dash=10, gap=6):
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i+1]
        length = ((x2-x1)**2 + (y2-y1)**2) ** 0.5
        if length == 0:
            continue
        dx, dy = (x2-x1)/length, (y2-y1)/length
        pos, on = 0.0, True
        while pos < length:
            end = min(pos + (dash if on else gap), length)
            if on:
                draw.line(
                    [(x1+dx*pos, y1+dy*pos), (x1+dx*end, y1+dy*end)],
                    fill=color, width=w
                )
            pos = end
            on = not on

# ══════════════════════════════════════════════════════════════════════════════
# Component positions
# ══════════════════════════════════════════════════════════════════════════════

# Arduino Uno  (center)
AX1, AY1, AX2, AY2 = 560, 360, 980, 680

# Capacitive Soil Sensor  (top-left)
SX1, SY1, SX2, SY2 = 50, 80, 280, 280

# Relay Module  (top-right)
RX1, RY1, RX2, RY2 = 1080, 80, 1380, 340

# Water Pump  (right-center)
PX1, PY1, PX2, PY2 = 1170, 460, 1430, 640

# 12V Adapter  (bottom-right)
DX1, DY1, DX2, DY2 = 1080, 730, 1380, 870

# ══════════════════════════════════════════════════════════════════════════════
# Pin anchor coordinates
# ══════════════════════════════════════════════════════════════════════════════

# Sensor right-edge pins
S_VCC  = (SX2, SY1 + 80)
S_AOUT = (SX2, SY1 + 120)
S_GND  = (SX2, SY1 + 160)

# Arduino left-edge pins
A_5V_L   = (AX1, AY1 + 80)
A_GND_L  = (AX1, AY1 + 130)
A_A0     = (AX1, AY1 + 180)

# Arduino right-edge pins
A_5V_R   = (AX2, AY1 + 80)
A_D7     = (AX2, AY1 + 130)
A_GND_R  = (AX2, AY1 + 180)
A_GND_SH = (AX1, AY2 - 40)   # shared ground pin (bottom-left area)

# Relay left-edge control pins
R_VCC = (RX1, RY1 + 80)
R_IN  = (RX1, RY1 + 130)
R_GND = (RX1, RY1 + 180)

# Relay bottom-edge load pins
R_NC  = (RX1 + 60,  RY2)
R_COM = (RX1 + 150, RY2)
R_NO  = (RX1 + 240, RY2)

# Pump left-edge pins
P_POS = (PX1, PY1 + 70)
P_NEG = (PX1, PY1 + 120)

# 12V adapter top-edge pins
D_POS = (DX1 + 80,  DY1)
D_NEG = (DX1 + 210, DY1)

# ══════════════════════════════════════════════════════════════════════════════
# Background circuit zones
# ══════════════════════════════════════════════════════════════════════════════
# 5V zone
box(30, 40, 1010, 710, '#E3F2FD', '#90CAF9', lw=2)
label('5V CONTROL CIRCUIT', 35, 43, F_SMALL, '#1565C0')

# 12V zone
box(1050, 40, 1560, 900, '#FFF3E0', '#FFCC80', lw=2)
label('12V PUMP CIRCUIT', 1055, 43, F_SMALL, '#E65100')

# ══════════════════════════════════════════════════════════════════════════════
# Wires (drawn before components so boxes sit on top)
# ══════════════════════════════════════════════════════════════════════════════

MID_L = 420   # x routing channel between sensor and Arduino

# Sensor VCC  → Arduino 5V (left)
wire([S_VCC,  (SX2+20, S_VCC[1]),  (MID_L, S_VCC[1]),  (MID_L, A_5V_L[1]),  A_5V_L],  C_RED)
# Sensor AOUT → Arduino A0
wire([S_AOUT, (SX2+40, S_AOUT[1]), (MID_L-20, S_AOUT[1]), (MID_L-20, A_A0[1]),  A_A0],   C_YELLOW, w=3)
# Sensor GND  → Arduino GND (left)
wire([S_GND,  (SX2+60, S_GND[1]),  (MID_L-40, S_GND[1]), (MID_L-40, A_GND_L[1]), A_GND_L], C_DKGRAY)

MID_R = 1050  # x routing channel between relay and Arduino

# Relay VCC → Arduino 5V (right)
wire([R_VCC, (RX1-20, R_VCC[1]), (MID_R, R_VCC[1]), (MID_R, A_5V_R[1]),  A_5V_R],  C_RED)
# Relay IN  → Arduino D7
wire([R_IN,  (RX1-40, R_IN[1]),  (MID_R-20, R_IN[1]),  (MID_R-20, A_D7[1]),   A_D7],    C_ORANGE)
# Relay GND → Arduino GND (right)
wire([R_GND, (RX1-60, R_GND[1]), (MID_R-40, R_GND[1]), (MID_R-40, A_GND_R[1]), A_GND_R], C_DKGRAY)

# 12V(+) → Relay COM  (thick dark red)
wire([D_POS, (D_POS[0], RY2+60), (R_COM[0], RY2+60), R_COM], C_DKRED, w=5)
# Relay NO → Pump(+)
wire([R_NO,  (R_NO[0], RY2+30), (PX1-30, RY2+30), (PX1-30, P_POS[1]), P_POS], C_DKRED, w=5)
# Pump(−)  → 12V(−)
wire([P_NEG, (PX1-60, P_NEG[1]), (PX1-60, DY1-30), (D_NEG[0], DY1-30), D_NEG], C_DKGRAY, w=5)

# Shared GND: 12V(−) to Arduino GND (dashed)
dashed_wire([D_NEG, (D_NEG[0], DY2+30), (AX1-60, DY2+30), (AX1-60, A_GND_SH[1]), A_GND_SH], C_DKGRAY, w=2)

# ══════════════════════════════════════════════════════════════════════════════
# Component boxes (drawn on top of wires)
# ══════════════════════════════════════════════════════════════════════════════

# Arduino Uno
box(AX1, AY1, AX2, AY2, '#E8F5E9', '#2E7D32', lw=3)
label('ARDUINO UNO REV3', (AX1+AX2)//2, AY1+14, F_COMP, '#1B5E20', anchor='mt')
label('ATmega328P', (AX1+AX2)//2, AY1+38, F_SMALL, '#388E3C', anchor='mt')
# Left pins
for (px, py), txt, col in [
    (A_5V_L,  '5V  ●', C_RED),
    (A_GND_L, 'GND ●', C_DKGRAY),
    (A_A0,    'A0  ●', C_YELLOW),
]:
    label(txt, AX1+8, py-10, F_PIN, col)
# Right pins
for (px, py), txt, col in [
    (A_5V_R,  '● 5V',  C_RED),
    (A_D7,    '● D7',  C_ORANGE),
    (A_GND_R, '● GND', C_DKGRAY),
]:
    label(txt, AX2-60, py-10, F_PIN, col)
# Shared GND marker
dot(*A_GND_SH, color=C_DKGRAY)
label('● GND (shared)', AX1+8, A_GND_SH[1]-10, F_PIN, C_DKGRAY)

# Capacitive Soil Sensor
box(SX1, SY1, SX2, SY2, '#FFFDE7', '#F57F17', lw=3)
label('CAPACITIVE SOIL', (SX1+SX2)//2, SY1+14, F_COMP, '#E65100', anchor='mt')
label('MOISTURE SENSOR', (SX1+SX2)//2, SY1+35, F_COMP, '#E65100', anchor='mt')
label('Gikfun EK1940', (SX1+SX2)//2, SY1+56, F_SMALL, '#BF360C', anchor='mt')
label('Insert prongs', (SX1+SX2)//2, SY2-40, F_SMALL, '#795548', anchor='mt')
label('into plant soil', (SX1+SX2)//2, SY2-22, F_SMALL, '#795548', anchor='mt')
for (px, py), txt, col in [
    (S_VCC,  'VCC ●',  C_RED),
    (S_AOUT, 'AOUT ●', C_YELLOW),
    (S_GND,  'GND ●',  C_DKGRAY),
]:
    label(txt, SX2-70, py-10, F_PIN, col)

# Relay Module
box(RX1, RY1, RX2, RY2, '#E3F2FD', '#1565C0', lw=3)
label('5V RELAY MODULE', (RX1+RX2)//2, RY1+14, F_COMP, '#0D47A1', anchor='mt')
label('Tolako 1-channel', (RX1+RX2)//2, RY1+36, F_SMALL, '#1565C0', anchor='mt')
# Control pins (left)
for (px, py), txt, col in [
    (R_VCC, '● VCC', C_RED),
    (R_IN,  '● IN',  C_ORANGE),
    (R_GND, '● GND', C_DKGRAY),
]:
    label(txt, RX1+10, py-10, F_PIN, col)
# Load pins (bottom)
for (px, py), txt, col in [
    (R_NC,  'NC',  C_GRAY),
    (R_COM, 'COM', C_DKRED),
    (R_NO,  'NO',  C_DKRED),
]:
    dot(px, RY2-4, color=col)
    label(txt, px, RY2+6, F_PIN, col, anchor='mt')
label('(unused)', R_NC[0],  RY2+24, F_SMALL, C_GRAY,  anchor='mt')
label('← 12V(+)', R_COM[0], RY2+24, F_SMALL, C_DKRED, anchor='mt')
label('→ Pump(+)',R_NO[0],  RY2+24, F_SMALL, C_DKRED, anchor='mt')

# Water Pump
box(PX1, PY1, PX2, PY2, '#FCE4EC', '#880E4F', lw=3)
label('WATER PUMP',     (PX1+PX2)//2, PY1+14, F_COMP, '#880E4F', anchor='mt')
label('Gikfun R385',   (PX1+PX2)//2, PY1+36, F_SMALL, '#AD1457', anchor='mt')
label('6–12V DC',      (PX1+PX2)//2, PY1+54, F_SMALL, '#AD1457', anchor='mt')
label('● (+)', PX1+14, P_POS[1]-10, F_PIN, C_DKRED)
label('● (−)', PX1+14, P_NEG[1]-10, F_PIN, C_DKGRAY)

# 12V Adapter
box(DX1, DY1, DX2, DY2, '#F3E5F5', '#4A148C', lw=3)
label('12V DC ADAPTER',   (DX1+DX2)//2, DY1+14, F_COMP, '#4A148C', anchor='mt')
label('(+) → Relay COM',  DX1+20,       DY1+44, F_SMALL, C_DKRED)
label('(−) → Pump (−)',   DX1+20,       DY1+64, F_SMALL, C_DKGRAY)
label('(−) also → Arduino GND', DX1+20, DY1+84, F_SMALL, C_DKGRAY)
dot(*D_POS, color=C_DKRED)
dot(*D_NEG, color=C_DKGRAY)

# ══════════════════════════════════════════════════════════════════════════════
# Legend
# ══════════════════════════════════════════════════════════════════════════════
LX, LY = 50, 740
box(LX, LY, LX+370, LY+230, '#FFFFFF', '#BDBDBD', lw=1)
label('WIRE LEGEND', LX+14, LY+12, F_LEGEND, C_BLACK)
legend_items = [
    (C_RED,    3, 'Red   — 5V power'),
    (C_DKGRAY, 3, 'Black — Ground (GND)'),
    (C_YELLOW, 3, 'Yellow — Analog signal (A0)'),
    (C_ORANGE, 3, 'Orange — Digital signal (D7)'),
    (C_DKRED,  5, 'Dark red — 12V pump circuit (thick)'),
    (C_DKGRAY, 2, 'Black dashed — Shared ground bridge'),
]
for i, (col, w, txt) in enumerate(legend_items):
    ly = LY + 44 + i * 30
    draw.line([(LX+14, ly+7), (LX+60, ly+7)], fill=col, width=w)
    label(txt, LX+70, ly, F_LEGEND, C_BLACK)

# Draw the dashed legend line
dashed_wire([(LX+14, LY+44+5*30+7), (LX+60, LY+44+5*30+7)], C_DKGRAY, w=2)

# ══════════════════════════════════════════════════════════════════════════════
# Title bar
# ══════════════════════════════════════════════════════════════════════════════
box(0, 980, W, H, '#37474F', '#37474F')
label(
    'Arduino Automatic Plant Watering System — Wiring Diagram',
    W//2, 993, F_TITLE, '#ECEFF1', anchor='mt'
)

out = '/Users/winnieyang/Documents/Projects/WaterPlant/wiring_diagram.png'
img.save(out, dpi=(150, 150))
print(f'Saved: {out}')
