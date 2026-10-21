"""VR lens bench solver.

Feed it the numbers you measured; it turns them into field of view, the eye/lens/
phone stack depth, and whether that stack fits an Iron-Man style faceplate.

Usage (any order, k=v):
    python solve.py f=45 d=44 e=20 ipd=63 dl=25
Optional: ws=146.7 hs=63.5 (phone screen, mm, landscape)  pt=8.2 (phone thickness)
          tp=2000 (target virtual-image distance in mm)  helm= (measured front-of-eye depth)
Bare `python solve.py` prints the worked example + the reference table.
"""
import sys, math

DEF = dict(f=None, d=None, e=None, ipd=63.0, dl=25.0, ws=146.7, hs=63.5, pt=8.2,
           tp=2000.0, helm=None)
PAD = 6.0  # lens holder + eye-card clearance, mm


def solve(f, d, e, ipd, dl, ws, hs, pt, tp, helm=None):
    r = dl / 2.0
    out = {}
    out["stack"] = e + d + pt + PAD
    out["d_target"] = f * tp / (tp + f)      # phone distance that puts the image at tp
    out["e_fill_x"] = None
    # virtual image distance for the measured d
    if d < f - 0.01:
        out["vid"] = f * d / (f - d)
    else:
        out["vid"] = float("inf")
    # half-angles, degrees
    a_lens = math.degrees(math.atan(r / e))
    a_x = math.degrees(math.atan((ws / 4.0) / (e + d)))   # per-eye half-width = ws/4
    a_y = math.degrees(math.atan((hs / 2.0) / (e + d)))   # per-eye half-height = hs/2
    out["a_lens"], out["a_x_phone"], out["a_y_phone"] = a_lens, a_x, a_y
    hx, hy = min(a_lens, a_x), min(a_lens, a_y)
    out["fov_h"], out["fov_v"] = 2 * hx, 2 * hy
    out["fov_diag"] = 2 * math.degrees(math.atan(math.hypot(math.tan(math.radians(hx)),
                                                            math.tan(math.radians(hy)))))
    lim_h = "lens rim" if a_lens <= a_x else "phone width"
    lim_v = "lens rim" if a_lens <= a_y else "phone height"
    out["limited_h"], out["limited_v"] = lim_h, lim_v
    out["limited_by"] = f"width capped by {lim_h}, height by {lim_v}"
    # eye relief needed for the phone to fill the lens on each axis
    out["e_fill_x"] = r * d / (ws / 4.0 - r) if ws / 4.0 > r else 0.0
    out["e_fill_y"] = r * d / (hs / 2.0 - r) if hs / 2.0 > r else 0.0
    # lens diameter needed to reach a target half-angle with the phone as the limit
    out["dl_for_phone"] = None
    # lateral split: where each eye's image centre must sit
    out["split_margin"] = (ws / 4.0 - ipd / 2.0) * 2  # total black added to both outer edges
    if helm is not None:
        out["helm_fit"] = helm - out["stack"]
    return out


def report(o, f, d, e, ipd, dl, ws, hs, tp, helm=None, pt=8.2):
    L = []
    L.append(f"lens f={f:.1f}mm  d(lens->phone)={d:.1f}  e(eye->lens)={e:.1f}  lens dia={dl:.1f}  ipd={ipd:.1f}")
    L.append(f"1. FOCUS: image sits at {o['vid']/1000:.2f} m" if o["vid"] != float("inf")
             else "1. FOCUS: image at infinity (relaxed eye, but vergence strain at close range)")
    L.append(f"   the 'sit back and relax' phone distance for your lens is {o['d_target']:.1f}mm"
             f" (you measured {d:.1f})")
    L.append(f"2. FIELD OF VIEW (one eye): {o['fov_h']:.0f} deg wide x {o['fov_v']:.0f} deg tall,"
             f" {o['fov_diag']:.0f} deg diagonal  [limited by {o['limited_by']}]")
    L.append(f"   raw angles: lens rim {o['a_lens']:.0f} deg | phone width {o['a_x_phone']:.0f}"
             f" | phone height {o['a_y_phone']:.0f}")
    if o["a_lens"] > min(o["a_x_phone"], o["a_y_phone"]):
        L.append(f"   !! you are seeing the phone edge, not the lens rim -> bezel in view."
                 f" need e >= {max(o['e_fill_x'], o['e_fill_y']):.0f}mm or a bigger phone image")
    else:
        L.append("   phone fills the lens on both axes: no bezel visible. Good.")
    L.append(f"3. STACK DEPTH eye-to-outside-of-phone: {o['stack']:.0f}mm"
             f"  (e {e:.0f} + d {d:.0f} + phone {pt:.1f} + clearance {PAD:.0f})")
    if helm is not None:
        fit = o["helm_fit"]
        L.append(f"4. HELMET: {helm:.0f}mm available - {o['stack']:.0f}mm needed = "
                 f"{fit:+.0f}mm -> " + ("FITS" if fit >= 0 else "DOES NOT FIT"))
    else:
        L.append("4. HELMET: measure brow-to-faceplate depth on the shell, rerun with helm=<mm>")
    L.append(f"5. SPLIT: at ipd {ipd:.0f} each half image must centre {ipd/2:.1f}mm off-centre,"
             f" leaving {o['split_margin']:.1f}mm of black across the two outer edges")
    return "\n".join(L)


def parse(argv):
    v = dict(DEF)
    for a in argv:
        if "=" in a:
            k, val = a.split("=", 1)
            if k in v:
                v[k] = float(val)
    return v


if __name__ == "__main__":
    v = parse(sys.argv[1:])
    if v["f"] is None:
        print("WORKED EXAMPLE (a 45mm-focal 25mm-diameter lens, eye 18mm back, phone 44mm out):")
        o = solve(45, 44, 18, 63, 25, 146.7, 63.5, 8.2, 2000, helm=70)
        print(report(o, 45, 44, 18, 63, 25, 146.7, 63.5, 2000, helm=70))
        print("\nREFERENCE — per-eye horizontal FOV vs eye relief, 45mm lens, Pixel 6 landscape")
        print(f"{'lens dia':>8} {'e=12':>7} {'e=15':>7} {'e=18':>7} {'e=22':>7} {'e=26':>7}"
              f" {'stack@e18':>10}")
        for dl in (20, 25, 30, 35, 40, 45, 50):
            row = []
            for e in (12, 15, 18, 22, 26):
                oo = solve(45, 44, e, 63, dl, 146.7, 63.5, 8.2, 2000)
                row.append(f"{oo['fov_h']:6.0f}")
            st = solve(45, 44, 18, 63, dl, 146.7, 63.5, 8.2, 2000)["stack"]
            print(f"{dl:8.0f} " + " ".join(row) + f" {st:9.0f}mm")
        print("\n(stack column = eye-to-outside-of-phone depth at e=18, d=44)")
        sys.exit(0)
    if v["d"] is None or v["e"] is None:
        print("need at least f= d= e=  (see header)")
        sys.exit(1)
    print(report(solve(**v), **v))
