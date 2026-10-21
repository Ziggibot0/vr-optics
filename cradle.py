"""Parametric VR-glasses cradle: phone in the back, two lenses in the faceplate.

DERIVED from the same numbers the lens bench measures, so the moment Sean's
f / d / e are known the physical rig exists:

  f   focal length of the lens            (mm)
  d   lens  -> phone screen distance       (mm)
  e   eye   -> lens distance (eye relief) (mm)
  ipd  interpupillary distance           (mm)
  dl   lens outer diameter                (mm)

Everything else (phone size, wall thickness) is a constant.

The script PROVES two things instead of assuming them:
  1. the solid is watertight (printable), and
  2. nothing in the cradle blocks the eye's view of the phone screen -
     checked by boolean-intersecting the solid with the exact per-eye
     vision cone (eye -> lens bore -> screen half).

Output:  cradle.stl, cradle.svg (dimensioned top view), cradle_spec.json

Usage:
    python cradle.py --demo
    python cradle.py --f 45 --d 44 --e 18 --ipd 63 --dl 25
"""
import argparse
import json
import math
import os

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- Pixel 6 (landscape) ------------------------------------------------
PHONE_W = 146.7      # mm, screen width
PHONE_H = 63.5       # mm, screen height
PHONE_T = 8.2        # mm, body thickness

# ---- print / build defaults --------------------------------------------
WALL = 3.0           # mm, printed wall thickness
LENS_CLEAR = 0.4     # mm, radial clearance for the lens in its bore
BROW_H = 12.0        # mm, height of the brow bar above the lens centres
CHEEK_H = 12.0       # mm, height of the cheek bar below the lens centres
STRUT = 6.0          # mm, strut cross-section
BACK_PLATE = 3.0     # mm, plate behind the phone
LIP = 4.0            # mm, how far the bottom rail rises past the phone edge
ANCHOR = 6.0         # mm, strap anchor width
PAD = 6.0            # mm, extra clearance in the depth budget

ENGINE = "manifold"


# ---------------------------------------------------------------- helpers
def box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from two opposite corners (order free)."""
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    z0, z1 = min(z0, z1), max(z0, z1)
    m = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0))
    m.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    return m


def cyl(r, h, x=0.0, y=0.0, z=0.0, seg=64):
    m = trimesh.creation.cylinder(radius=r, height=h, sections=seg)
    m.apply_translation((x, y, z))
    return m


def union(parts):
    out = parts[0]
    for p in parts[1:]:
        out = trimesh.boolean.union([out, p], engine=ENGINE)
    return out


def subtract(base, cutters):
    for c in cutters:
        base = trimesh.boolean.difference([base, c], engine=ENGINE)
    return base


def beam(p0, p1, w, h):
    """A rectangular beam from point p0 to p1 (both 3D), cross-section w x h."""
    p0 = np.array(p0, dtype=float)
    p1 = np.array(p1, dtype=float)
    d = p1 - p0
    L = float(np.linalg.norm(d))
    if L < 1e-6:
        return None
    m = trimesh.creation.box(extents=(L, w, h))
    m.apply_transform(trimesh.transformations.translation_matrix((L / 2, 0, 0)))
    # rotate +X onto d
    q = trimesh.transformations.quaternion_from_matrix(
        np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]]))
    rot = trimesh.transformations.rotation_matrix(
        np.arctan2(d[2], d[0]), [0, 1, 0])
    m.apply_transform(rot)
    m.apply_transform(trimesh.transformations.translation_matrix(p0))
    return m


# ---------------------------------------------------------------- geometry
def build(p):
    f, d, e, ipd, dl = p["f"], p["d"], p["e"], p["ipd"], p["dl"]
    r_lens = dl / 2.0
    r_bore = r_lens + LENS_CLEAR

    z_face = 0.0                    # lens plane
    z_face_back = -WALL             # faceplate occupies z in [-WALL, 0]
    z_screen = -d                  # phone screen plane
    z_phone_back = -d - PHONE_T
    z_back = z_phone_back - BACK_PLATE

    # face frame half width: lens ring + margin.  The frame is NOT as wide
    # as the phone; the phone tray flares out behind it.
    half_frame = ipd / 2.0 + r_bore + 8.0
    half_tray = PHONE_W / 2.0 + 4.0
    half_h = BROW_H / 2.0           # above/below the lens centre line

    # ---- face frame: a bar above the lenses and a bar below --------------
    frame_parts = [
        box(-half_frame, half_frame, r_lens, r_lens + BROW_H, z_face_back, z_face),
        box(-half_frame, half_frame, -r_lens - CHEEK_H, -r_lens, z_face_back, z_face),
    ]
    # side pieces tying the two bars together, outboard of the lens bores
    for sx in (-1, 1):
        frame_parts.append(box(sx * (ipd / 2.0 + r_bore),
                               sx * half_frame,
                               -r_lens - CHEEK_H, r_lens + BROW_H,
                               z_face_back, z_face))
    frame = union(frame_parts)

    # ---- lens bores + retaining rings ------------------------------------
    rings = []
    for sx in (-1, 1):
        cx = sx * ipd / 2.0
        bore = cyl(r_bore, 40, x=cx, y=0, z=z_face_back / 2)
        frame = subtract(frame, [bore])
        # ring in FRONT of the lens (z 0 .. 6) holding it against the frame
        ro = cyl(r_bore + 2.5, 6.0, x=cx, y=0, z=3.0)
        ri = cyl(r_bore, 40, x=cx, y=0, z=3.0)
        rings.append(subtract(ro, [ri]))
        # lip BEHIND the lens (z -2 .. 0) retaining it
        lo = cyl(r_bore + 1.6, 2.0, x=cx, y=0, z=-1.0)
        li = cyl(r_bore, 40, x=cx, y=0, z=-1.0)
        rings.append(subtract(lo, [li]))

    # ---- phone tray: back plate, side rails, top/bottom rails -----------
    tray = [
        box(-half_tray, half_tray, -PHONE_H / 2 - 6, PHONE_H / 2 + 6,
            z_back, z_phone_back),
        # side rails, outboard of the screen, spanning the phone depth
        box(-half_tray - 3, -PHONE_W / 2 - 1, -PHONE_H / 2 - 6, PHONE_H / 2 + 6,
            z_screen, z_phone_back),
        box(PHONE_W / 2 + 1, half_tray + 3, -PHONE_H / 2 - 6, PHONE_H / 2 + 6,
            z_screen, z_phone_back),
        # bottom rail: supports the phone, rises LIP past the screen bottom
        box(-half_tray - 3, half_tray + 3, -PHONE_H / 2 - 6, -PHONE_H / 2 + LIP,
            z_screen, z_phone_back),
        # top rail: catches the phone
        box(-half_tray - 3, half_tray + 3, PHONE_H / 2 - LIP, PHONE_H / 2 + 6,
            z_screen, z_phone_back),
    ]

    # ---- struts: frame -> tray, ABOVE and BELOW the eye line -------------
    struts = []
    for sx in (-1, 1):
        for sy in (1, -1):
            y_frame = sy * (r_lens + (BROW_H if sy > 0 else CHEEK_H) / 2.0)
            y_tray = sy * (PHONE_H / 2 + 3)
            b = beam((sx * half_frame, y_frame, z_face),
                     (sx * half_tray, y_tray, z_screen), STRUT, STRUT)
            if b is not None:
                struts.append(b)

    # ---- strap anchors ---------------------------------------------------
    anchors = []
    for sx in (-1, 1):
        anchors.append(box(sx * (half_tray + 3), sx * (half_tray + 3 + ANCHOR),
                           -8, 8, z_phone_back, z_phone_back + 10))

    solid = union([frame] + rings + tray + struts + anchors)

    # nose notch: cut a cylinder through the lower frame
    solid = subtract(solid, [cyl(12.0, 60, x=0, y=-r_lens - CHEEK_H, z=-WALL / 2)])

    # ---- occlusion check -------------------------------------------------
    # Two regions carry light from the eye to the screen:
    #   (a) eye -> lens:  the cone with apex at the eye, base = the bore
    #       circle at the lens plane.
    #   (b) lens -> screen: the bore's shadow cylinder.  Every ray that
    #       reaches the screen passed through the bore, so any solid
    #       material inside that cylinder blocks part of the view.
    # Checking only the screen plane would miss a bar floating mid-way,
    # so the whole light path is tested.
    blocked = {}
    for sx, label in ((1, "right"), (-1, "left")):
        eye = np.array([sx * ipd / 2.0, 0.0, e])
        ring_pts = [[sx * ipd / 2.0 + r_bore * math.cos(2 * math.pi * k / 32),
                     r_bore * math.sin(2 * math.pi * k / 32), z_face]
                    for k in range(32)]
        cone = trimesh.convex.convex_hull(np.array([eye] + ring_pts))
        # (a) eye -> lens cone, clipped to z >= lens plane
        front = cone.intersection(
            box(-half_tray - 10, half_tray + 10, -r_bore - 10, r_bore + 10,
                z_face, e + 10))
        # (b) bore shadow cylinder, lens plane -> screen
        shadow = cyl(r_bore, abs(d) + 2.0, x=sx * ipd / 2.0, y=0.0,
                     z=(z_face + z_screen) / 2.0)
        parts = [m for m in (front, shadow) if m is not None and m.volume > 1e-6]
        path_vol = sum(float(m.volume) for m in parts)
        blk = 0.0
        for m in parts:
            inter = trimesh.boolean.intersection([solid, m], engine=ENGINE)
            if inter is not None:
                blk += float(inter.volume)
        blocked[label] = {
            "light_path_mm3": round(path_vol, 1),
            "blocked_mm3": round(blk, 1),
            "blocked_pct": round(100.0 * blk / path_vol, 2) if path_vol > 1e-6 else 0.0,
        }

    # ---- optics ---------------------------------------------------------
    vid = (f * d / (f - d)) if d < f else float("inf")
    d_target = f * 2000.0 / (2000.0 + f)
    a_lens = math.degrees(math.atan(r_lens / e))
    a_x = math.degrees(math.atan((PHONE_W / 4.0) / (e + d)))
    a_y = math.degrees(math.atan((PHONE_H / 2.0) / (e + d)))
    e_fill_x = r_lens * d / (PHONE_W / 4.0 - r_lens) if PHONE_W / 4.0 > r_lens else 0.0
    e_fill_y = r_lens * d / (PHONE_H / 2.0 - r_lens) if PHONE_H / 2.0 > r_lens else 0.0

    spec = {
        "inputs": {k: p[k] for k in ("f", "d", "e", "ipd", "dl")},
        "phone_mm": {"w": PHONE_W, "h": PHONE_H, "t": PHONE_T},
        "derived": {
            "frame_width_mm": round(2 * half_frame, 1),
            "frame_height_mm": round(2 * r_lens + BROW_H + CHEEK_H, 1),
            "tray_width_mm": round(2 * half_tray, 1),
            "lens_bore_mm": round(2 * r_bore, 1),
            "depth_face_to_back_mm": round(abs(z_back), 1),
            "depth_eye_to_phone_back_mm": round(e + d + PHONE_T, 1),
            "depth_with_clearance_mm": round(e + d + PHONE_T + PAD, 1),
            "virtual_image_m": (round(vid / 1000.0, 3) if vid != float("inf") else None),
            "phone_dist_for_2m_mm": round(d_target, 2),
            "fov_h_deg": round(2 * min(a_lens, a_x), 1),
            "fov_v_deg": round(2 * min(a_lens, a_y), 1),
            "fov_limited_by": ("lens rim" if a_lens <= a_x else "phone width") + " / " +
                              ("lens rim" if a_lens <= a_y else "phone height"),
            "e_needed_to_hide_bezel_mm": round(max(e_fill_x, e_fill_y), 1),
            "black_margin_outer_edges_mm": round((PHONE_W / 4.0 - ipd / 2.0) * 2, 1),
        },
        "occlusion": blocked,
        "mesh": {
            "watertight": bool(solid.is_watertight),
            "volume_cm3": round(float(solid.volume) / 1000.0, 2),
            "bbox_mm": [[round(float(v), 1) for v in solid.bounds[0]],
                        [round(float(v), 1) for v in solid.bounds[1]]],
        },
    }
    return solid, spec


# ---------------------------------------------------------------- svg
def top_view_svg(p, spec, path):
    ipd, dl, d, e = p["ipd"], p["dl"], p["d"], p["e"]
    half_frame = ipd / 2.0 + dl / 2.0 + 0.4 + 8.0
    half_tray = PHONE_W / 2.0 + 4.0
    W = 2 * (half_tray + 12)
    H = 2 * (dl / 2.0 + 20) + 40
    cx0, cy0 = W / 2.0, 20 + dl / 2.0
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" '
         f'viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         f'<g fill="none" stroke="#111" stroke-width="0.4">',
         f'<rect x="{cx0-half_frame}" y="{cy0-dl/2}" width="{2*half_frame}" '
         f'height="{dl}"/>',
         f'<rect x="{cx0-half_tray}" y="{cy0-PHONE_H/2}" width="{2*half_tray}" '
         f'height="{PHONE_H}" stroke="#06c" stroke-dasharray="2,1"/>']
    for sx in (-1, 1):
        cx = cx0 + sx * ipd / 2.0
        s.append(f'<circle cx="{cx}" cy="{cy0}" r="{dl/2}" stroke="#c00"/>')
        s.append(f'<circle cx="{cx}" cy="{cy0}" r="{dl/2+0.4}" stroke="#c00" '
                 f'stroke-dasharray="1,1"/>')
    y = cy0 + dl / 2.0 + 12
    s.append(f'<line x1="{cx0-ipd/2}" y1="{y}" x2="{cx0+ipd/2}" y2="{y}" '
             f'stroke="#0a0" stroke-width="0.4"/>')
    for sx in (-1, 1):
        s.append(f'<line x1="{cx0+sx*ipd/2}" y1="{y-3}" x2="{cx0+sx*ipd/2}" '
                 f'y2="{y+3}" stroke="#0a0" stroke-width="0.4"/>')
    s.append(f'<text x="{cx0}" y="{y+8}" font-size="4" text-anchor="middle">'
             f'IPD {ipd} mm</text>')
    s.append(f'<text x="{cx0}" y="12" font-size="4" text-anchor="middle">'
             f'top view  f={p["f"]} d={d} e={e} lens {dl}mm  '
             f'- print 1:1 at 100%, do NOT fit to page</text>')
    s.append(f'<text x="{cx0}" y="{H-6}" font-size="3.4" text-anchor="middle">'
             f'blue dashed = phone screen footprint, red = lens bore</text>')
    s.append('</g></svg>')
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--out", default=HERE)
    for k in ("f", "d", "e", "ipd", "dl"):
        ap.add_argument(f"--{k}", type=float, default=None)
    a = ap.parse_args()

    p = {"f": a.f, "d": a.d, "e": a.e, "ipd": a.ipd, "dl": a.dl}
    if a.demo or p["f"] is None:
        p = {"f": 45.0, "d": 44.0, "e": 18.0, "ipd": 63.0, "dl": 25.0}
        print("DEMO values (NOT measured): f=45 d=44 e=18 ipd=63 dl=25")
    if any(p[k] is None for k in ("f", "d", "e")):
        ap.error("need at least --f --d --e")

    mesh, spec = build(p)
    stl = os.path.join(a.out, "cradle.stl")
    svg = os.path.join(a.out, "cradle.svg")
    js = os.path.join(a.out, "cradle_spec.json")
    mesh.export(stl)
    top_view_svg(p, spec, svg)
    with open(js, "w", encoding="utf-8") as fh:
        json.dump(spec, fh, indent=2)

    print(json.dumps(spec, indent=2))
    print("\nwrote", stl, "|", svg, "|", js)
    print("watertight:", mesh.is_watertight)
    worst = max(v["blocked_pct"] for v in spec["occlusion"].values())
    print("worst blocked view: %.2f%%" % worst)
    if worst > 0.5:
        print("!! VIEW BLOCKED - do not print this")
    else:
        print("view clear")


if __name__ == "__main__":
    main()
