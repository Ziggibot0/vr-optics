"""Emit a 1:1 (millimetre-true) printable card kit for the VR lens bench.

template.svg  ->  Letter, 216x279mm. Print at 100% / 'Actual size', no scaling.
Everything is sized in real millimetres so cut parts are already correct.
"""
import os

S = []
A = S.append


def text(x, y, s, size=3.4, anchor="start", bold=False):
    w = ' font-weight="bold"' if bold else ""
    A(f'<text x="{x}" y="{y}" font-family="Arial,Helvetica" font-size="{size}"'
      f' text-anchor="{anchor}" fill="#000"{w}>{s}</text>')


def ticks(x, y, length, step, label_every, vertical=True, flip=False, big=7, small=4):
    """Ruler ticks. vertical=True ticks run down from y."""
    t = []
    for i in range(0, int(length) + 1, step):
        p = y + i if vertical else x + i
        major = (i % label_every == 0)
        ln = big if major else small
        if vertical:
            t.append(f'<line x1="{x}" y1="{p}" x2="{x + ln}" y2="{p}" stroke="#000" stroke-width="0.3"/>')
            if major:
                t.append(f'<text x="{x + ln + 1.5}" y="{p + 1.2}" font-family="Arial" '
                         f'font-size="3" fill="#000">{i}</text>')
        else:
            t.append(f'<line x1="{p}" y1="{y}" x2="{p}" y2="{y + ln}" stroke="#000" stroke-width="0.3"/>')
            if major:
                t.append(f'<text x="{p}" y="{y + ln + 3.4}" font-family="Arial" font-size="3" '
                         f'fill="#000" text-anchor="middle">{i}</text>')
    return "".join(t)


A('<svg xmlns="http://www.w3.org/2000/svg" width="216mm" height="279mm" '
  'viewBox="0 0 216 279">')
A('<rect width="216" height="279" fill="#fff"/>')

# ---- header + calibration bar -------------------------------------------
text(8, 10, "VR LENS BENCH - CARD KIT", 5, bold=True)
text(8, 15, "Print at 100% / Actual size. NO 'fit to page'. Then check the bar below:", 3.2)

A('<rect x="8" y="18" width="100" height="6" fill="none" stroke="#000" stroke-width="0.4"/>')
A('<rect x="8" y="18" width="50" height="6" fill="#000"/>')
A(ticks(8, 26, 100, 10, 50, vertical=False, big=0, small=0))
for i in range(0, 101, 10):
    A(f'<line x1="{8+i}" y1="24" x2="{8+i}" y2="18" stroke="#000" stroke-width="0.3"/>')
text(110, 22.5, "this bar MUST measure 100mm", 3.2, bold=True)
text(110, 27, "if it doesn't, your printer scaled it", 3.0)

# ---- lens frame ----------------------------------------------------------
FX, FY = 8, 34
text(FX, FY, "A. LENS FRAME  (cut out, tape lens in the hole)", 3.4, bold=True)
A(f'<rect x="{FX}" y="{FY+3}" width="62" height="62" fill="none" stroke="#000" stroke-width="0.4"/>')
A(f'<circle cx="{FX+31}" cy="{FY+34}" r="12.5" fill="none" stroke="#000" stroke-width="0.4"/>')
A(f'<line x1="{FX+31-20}" y1="{FY+34}" x2="{FX+31+20}" y2="{FY+34}" stroke="#000" stroke-width="0.2"/>')
A(f'<line x1="{FX+31}" y1="{FY+34-20}" x2="{FX+31}" y2="{FY+34+20}" stroke="#000" stroke-width="0.2"/>')
for i, (cx, cy) in enumerate([(FX, FY + 3), (FX + 62, FY + 3), (FX, FY + 65), (FX + 62, FY + 65)]):
    A(f'<circle cx="{cx}" cy="{cy}" r="1.2" fill="#000"/>')
text(FX + 31, FY + 34 + 26, "tape lens here", 2.6, anchor="middle")
text(FX + 31, FY + 34 + 30, "25mm hole shown", 2.6, anchor="middle")
text(FX + 31, FY + 34 + 34, "recut to your lens", 2.6, anchor="middle")

# ---- eye card ------------------------------------------------------------
EX, EY = 80, 34
text(EX, EY, "B. EYE CARD  (cut hole, rest on brow)", 3.4, bold=True)
A(f'<path d="M {EX} {EY+8} L {EX+60} {EY+8} L {EX+60} {EY+52} L {EX+40} {EY+52} '
  f'L {EX+38} {EY+44} L {EX+22} {EY+44} L {EX+20} {EY+52} L {EX} {EY+52} Z" '
  f'fill="none" stroke="#000" stroke-width="0.4"/>')
A(f'<circle cx="{EX+30}" cy="{EY+28}" r="7" fill="none" stroke="#000" stroke-width="0.4"/>')
A(f'<circle cx="{EX+30}" cy="{EY+28}" r="1" fill="#000"/>')
text(EX + 30, EY + 62, "14mm sighting hole", 2.6, anchor="middle")
text(EX + 30, EY + 66, "nose notch at bottom", 2.6, anchor="middle")

# ---- stalks (eye relief) -------------------------------------------------
SX, SY = 8, 110
text(SX, SY, "C. EYE-RELIEF STALKS", 3.4, bold=True)
text(SX, SY + 4.5, "cut 2 at the SAME number = your eye relief e", 3.0)
for k in range(2):
    x = SX + k * 22
    A(f'<rect x="{x}" y="{SY + 10}" width="16" height="84" fill="none" stroke="#000" stroke-width="0.4"/>')
    A(ticks(x + 1, SY + 10, 82, 5, 10, big=8, small=4))
    A(f'<line x1="{x}" y1="{SY + 10}" x2="{x+16}" y2="{SY + 10}" stroke="#000" stroke-width="0.9"/>')
text(SX + 50, SY + 14, "thick line = height 0, sits flush", 3.0)
text(SX + 50, SY + 18, "on the lens frame. Cut across at", 3.0)
text(SX + 50, SY + 22, "the number you want, tape the top", 3.0)
text(SX + 50, SY + 26, "end to the eye card.", 3.0)
text(SX + 50, SY + 34, "start at e = 20mm", 3.6, bold=True)

# ---- d gauge -------------------------------------------------------------
DX, DY = 130, 110
text(DX, DY, "D. PHONE-DISTANCE GAUGE", 3.4, bold=True)
text(DX, DY + 4.5, "cut at the thick line, tape that end", 3.0)
text(DX, DY + 8, "flush to the lens frame, let it hang.", 3.0)
text(DX, DY + 11.5, "read the number level with the phone", 3.0)
text(DX, DY + 15, "screen - that is your d.", 3.0)
A(f'<rect x="{DX}" y="{DY + 19}" width="16" height="84" fill="none" stroke="#000" stroke-width="0.4"/>')
A(f'<line x1="{DX}" y1="{DY + 19}" x2="{DX+16}" y2="{DY + 19}" stroke="#000" stroke-width="0.9"/>')
A(ticks(DX + 1, DY + 19, 82, 5, 10, big=8, small=4))

# ---- log sheet -----------------------------------------------------------
LX, LY = 8, 212
text(LX, LY, "E. LOG IT  (one row per attempt - the numbers are the whole point)", 3.4, bold=True)
rows = ["lens dia / focal f", "eye relief e (stalk)", "phone gap d (gauge)",
        "image sharp? rings round?", "see phone edge/bezel?", "eye-strain notes"]
A(f'<rect x="{LX}" y="{LY+4}" width="200" height="{len(rows)*7}" fill="none" stroke="#000" stroke-width="0.4"/>')
for i, r in enumerate(rows):
    y = LY + 4 + i * 7
    A(f'<line x1="{LX}" y1="{y}" x2="{LX+200}" y2="{y}" stroke="#000" stroke-width="0.2"/>')
    A(f'<line x1="{LX+55}" y1="{y}" x2="{LX+55}" y2="{y+7}" stroke="#000" stroke-width="0.2"/>')
    text(LX + 2, y + 5, r, 3.0)
text(LX + 57, LY + 4 + 5, "trial 1", 2.8)
text(LX + 110, LY + 4 + 5, "trial 2", 2.8)
text(LX + 155, LY + 4 + 5, "trial 3", 2.8)
for x in (110, 155):
    A(f'<line x1="{LX+x}" y1="{LY+4}" x2="{LX+x}" y2="{LY+4+len(rows)*7}" stroke="#000" stroke-width="0.2"/>')

text(8, 275, "CADEN - vr-optics - pattern.png goes fullscreen on the phone, landscape", 2.6)
A("</svg>")

svg = "\n".join(S)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.svg")
open(out, "w", encoding="utf-8").write(svg)
print("wrote", out, len(svg), "bytes")
