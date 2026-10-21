"""Generate the phone-screen optical test target for the VR lens bench.

Output: pattern.png 2400x1080 (Pixel 6 native, landscape, two identical eye halves).
Purpose: judge (a) focus, (b) field-of-view cut-off, (c) distortion, (d) chromatic
aberration, (e) resolution at a given lens distance.
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

W, H = 2400, 1080
HALF = W // 2  # 1200

img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)


def font(sz):
    for p in (
        r"C:\Windows\Fonts\consolab.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


def half(off, label):
    cx, cy = off + HALF // 2, H // 2

    # --- distortion grid, light gray, 60px cells ---
    for x in range(off, off + HALF + 1, 60):
        d.line([(x, 0), (x, H)], fill=(205, 205, 205), width=1)
    for y in range(0, H + 1, 60):
        d.line([(off, y), (off + HALF, y)], fill=(205, 205, 205), width=1)

    # --- hard frame at the half's edge: if the lens clips the image, this vanishes ---
    d.rectangle([off + 6, 6, off + HALF - 6, H - 6], outline="black", width=6)

    # --- decile ticks with numbers down both sides ---
    f24 = font(26)
    for i in range(11):
        y = int(6 + (H - 12) * i / 10)
        for x0 in (off + 6, off + HALF - 6):
            d.line([(x0, y), (x0 + (44 if x0 < cx else -44), y)], fill="black", width=4)
    for i in range(1, 10):
        y = int(6 + (H - 12) * i / 10)
        t = str(i)
        d.text((off + 58, y - 14), t, fill="black", font=f24)
        d.text((off + HALF - 78, y - 14), t, fill="black", font=f24)

    # --- concentric field rings, every 60px of radius, labelled ---
    for r in range(60, 561, 60):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline="black", width=3)
        d.text((cx + r - 30, cy - 16), str(r // 60), fill="black", font=f24)

    # --- Siemens star (focus + astigmatism) ---
    R = 110
    for k in range(36):
        a0 = math.radians(k * 10)
        a1 = math.radians(k * 10 + 5)
        d.polygon(
            [
                (cx, cy),
                (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                (cx + R * math.cos(a1), cy + R * math.sin(a1)),
            ],
            fill="black",
        )
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill="white", outline="black", width=3)

    # --- crosshair ---
    d.line([(cx - 300, cy), (cx + 300, cy)], fill="black", width=2)
    d.line([(cx, cy - 300), (cx, cy + 300)], fill="black", width=2)

    # --- line-grating patches: period 2/4/6/8/10 px, tells you when the optics run out ---
    gy = cy + 150
    gx = cx - 260
    for period in (2, 4, 6, 8, 10):
        for xx in range(0, 88, period * 2):
            d.rectangle([gx + xx, gy, gx + xx + period - 1, gy + 60], fill="black")
        d.text((gx, gy + 64), f"{period}px", fill="black", font=font(20))
        gx += 110

    # --- text ladder: 6 sizes, resolution sanity ---
    ty = cy - 240
    for i, sz in enumerate((40, 30, 22, 16, 12, 9)):
        d.text((cx - 250, ty + i * 34), f"{sz}px ABCDEFGHIJ klmnop 0123456789", fill="black", font=font(sz))

    # --- chromatic aberration target: fine black/white checker in two sizes ---
    ax, ay = off + 80, H - 200
    for i in range(8):
        for j in range(8):
            if (i + j) % 2 == 0:
                d.rectangle([ax + i * 20, ay + j * 20, ax + i * 20 + 19, ay + j * 20 + 19], fill="black")

    # --- eye label ---
    d.text((off + HALF // 2 - 30, H - 70), label, fill="black", font=font(54))


half(0, "L")
half(HALF, "R")

# center split line + bezel warning markers at the outer corners
d.line([(HALF, 0), (HALF, H)], fill=(230, 0, 0), width=3)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pattern.png")
img.save(out, "PNG")
print("wrote", out, img.size)
