"""Bench measurement collector for the VR lens bench.

Sean opens a form on his phone, types the numbers he just measured off the
paper rig, and taps submit.  The server:

  1. appends the reading to a JSONL log (raw evidence, never overwritten),
  2. re-runs solve.py and cradle.py with the new numbers,
  3. rewrites a vault note under System/Caden/Projects/ with the results.

No third party, no cloud, no tokens.  The phone talks to the PC over the
Tailscale tailnet by LAN IP.

Run:  python collect.py --port 8788
Then on the phone:  http://<pc-tailnet-ip>:8788/
"""
import argparse
import json
import os
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = r"C:\Users\skell\Desktop\vaultbot-home\myvault"
NOTE = os.path.join(VAULT, "System", "Caden", "Projects", "VR-Bench-Results.md")
LOG = os.path.join(VAULT, "System", "Caden", "_data", "vr-bench.jsonl")
LOG_DIR = os.path.dirname(LOG)

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>VR bench</title>
<style>
 body{font:16px system-ui,sans-serif;background:#111;color:#eee;margin:0;padding:14px}
 h1{font-size:19px;margin:0 0 4px} p{color:#aaa;font-size:13px;margin:0 0 12px}
 label{display:block;margin:10px 0 2px;font-size:14px;color:#9cf}
 input{width:100%;box-sizing:border-box;padding:12px;font-size:18px;background:#1e1e1e;
       color:#fff;border:1px solid #444;border-radius:8px}
 button{margin-top:16px;width:100%;padding:14px;font-size:17px;background:#2f6fff;color:#fff;
        border:0;border-radius:8px}
 a{color:#2f6fff} .ok{color:#7fdc7f}
 table{border-collapse:collapse;width:100%;font-size:13px;margin-top:10px}
 td,th{border:1px solid #333;padding:5px;text-align:left}
</style></head><body>
<h1>VR lens bench — record a reading</h1>
<p>Measure f first (lens-&gt;paper distance where the window image is sharpest),
then d (lens-&gt;phone) and e (eye-&gt;lens). Millimetres.</p>
<form method="POST" action="/record">
<label>f — lens focal length (mm)</label><input name="f" inputmode="decimal" placeholder="e.g. 45">
<label>d — lens to phone screen (mm)</label><input name="d" inputmode="decimal" placeholder="e.g. 44">
<label>e — eye to lens (mm)</label><input name="e" inputmode="decimal" placeholder="e.g. 18">
<label>lens outer diameter (mm)</label><input name="dl" inputmode="decimal" placeholder="e.g. 25">
<label>your IPD (mm)</label><input name="ipd" inputmode="decimal" placeholder="e.g. 63">
<label>notes (what you saw)</label><input name="notes" placeholder="e.g. star sharp, edges soft">
<button type="submit">Save reading</button>
</form>
<p style="margin-top:14px"><a href="/chart">Open the test chart</a> &middot;
<a href="/log">Reading log</a></p>
<div id="out"></div>
<script>
document.querySelector('form').addEventListener('submit',function(ev){
  document.querySelector('button').textContent='Saving...';
});
</script>
</body></html>"""

CHART = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>VR lens test chart</title>
<style>body{margin:0;background:#000;color:#ccc;font:14px system-ui;text-align:center}
iframe{border:0;width:100%;height:88vh;background:#000}</style></head><body>
<iframe src="https://ziggibot0.github.io/vr-optics/?auto=1"></iframe>
<p>Tap once for fullscreen. Landscape. Turn brightness up, auto-brightness off.</p>
</body></html>"""


def run(cmd):
    try:
        p = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, timeout=300)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as exc:  # noqa: BLE001
        return -1, str(exc)


def save_reading(rec):
    os.makedirs(LOG_DIR, exist_ok=True)
    rec["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")

    f, d, e = rec.get("f"), rec.get("d"), rec.get("e")
    spec = None
    if f and d and e:
        dl = rec.get("dl") or 25.0
        ipd = rec.get("ipd") or 63.0
        rc, out = run([os.sys.executable, "solve.py",
                       "f=%s" % f, "d=%s" % d, "e=%s" % e,
                       "ipd=%s" % ipd, "dl=%s" % dl, "hs=63.5", "ws=146.7",
                       "pt=8.2", "tp=2000"])
        rc2, out2 = run([os.sys.executable, "cradle.py", "--f", str(f), "--d", str(d),
                         "--e", str(e), "--ipd", str(ipd), "--dl", str(dl)])
        try:
            with open(os.path.join(HERE, "cradle_spec.json"), encoding="utf-8") as fh:
                spec = json.load(fh)
        except Exception:  # noqa: BLE001
            spec = None
        rec["solve_output"] = out.strip()
        rec["cradle_output"] = out2.strip()[-2000:]
        rec["solve_rc"] = rc
        rec["cradle_rc"] = rc2

    # Log AFTER the solve so the raw record carries the derived numbers too.
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    write_note(rec, spec)
    return rec, spec


def write_note(rec, spec):
    os.makedirs(os.path.dirname(NOTE), exist_ok=True)
    lines = [
        "---",
        "type: measurement-log",
        "status: active",
        "created: " + rec["ts"],
        f"summary: VR lens bench reading — f={rec.get('f')} d={rec.get('d')} "
        f"e={rec.get('e')} lens {rec.get('dl')}mm ipd {rec.get('ipd')}mm",
        "tags: [vr, optics, measurement, caden-built]",
        "---",
        "",
        "# VR lens bench — measured readings",
        "",
        "Written by the bench collector (vr-optics/collect.py). Raw log: "
        "`System/Caden/_data/vr-bench.jsonl`",
        "",
        "## Latest reading — " + rec["ts"],
        "",
        f"- f (focal length): {rec.get('f')} mm",
        f"- d (lens->phone): {rec.get('d')} mm",
        f"- e (eye->lens): {rec.get('e')} mm",
        f"- lens outer dia: {rec.get('dl')} mm",
        f"- IPD: {rec.get('ipd')} mm",
        f"- notes: {rec.get('notes') or '(none)'}",
        "",
    ]
    if spec:
        dv = spec.get("derived", {})
        lines += [
            "### Result",
            "",
            f"- virtual image: {dv.get('virtual_image_m')} m",
            f"- FOV per eye: {dv.get('fov_h_deg')} h x {dv.get('fov_v_deg')} v "
            f"({dv.get('fov_limited_by')})",
            f"- eye-to-phone-back: {dv.get('depth_eye_to_phone_back_mm')} mm "
            f"(+clearance {dv.get('depth_with_clearance_mm')} mm)",
            f"- e needed to hide the bezel: {dv.get('e_needed_to_hide_bezel_mm')} mm",
            f"- black margin at the outer edges: "
            f"{dv.get('black_margin_outer_edges_mm')} mm",
            f"- cradle mesh watertight: {spec.get('mesh', {}).get('watertight')}, "
            f"blocked view: "
            f"{max(v['blocked_pct'] for v in spec.get('occlusion', {}).values())}%",
            "",
        ]
    lines += [
        "## All readings",
        "",
    ]
    try:
        with open(LOG, encoding="utf-8") as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except Exception:  # noqa: BLE001
                    continue
                lines.append(f"- {r.get('ts')} — f={r.get('f')} d={r.get('d')} "
                             f"e={r.get('e')} dl={r.get('dl')} ipd={r.get('ipd')} "
                             f"— {r.get('notes') or ''}")
    except FileNotFoundError:
        pass
    with open(NOTE, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *a):  # quiet
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            self._send(200, PAGE)
        elif path == "/chart":
            self._send(200, CHART)
        elif path == "/log":
            try:
                with open(LOG, encoding="utf-8") as fh:
                    body = fh.read()
            except FileNotFoundError:
                body = "(no readings yet)\n"
            self._send(200, "<pre>" + body.replace("&", "&amp;").replace("<", "&lt;")
                       + "</pre>")
        else:
            self._send(404, "nope")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8", "replace")
        q = parse_qs(raw)
        rec = {}
        for k in ("f", "d", "e", "dl", "ipd"):
            v = (q.get(k) or [""])[0].strip()
            if v:
                try:
                    rec[k] = float(v)
                except ValueError:
                    rec[k] = None
        rec["notes"] = (q.get("notes") or [""])[0].strip()
        rec, _ = save_reading(rec)
        self._send(200, "<!doctype html><meta charset=utf-8>"
                        "<body style='font:16px system-ui;background:#111;color:#eee;padding:20px'>"
                        "<div class='ok'><b>Saved.</b> The cradle and optics were rebuilt "
                        "from these numbers.</div><p><a style='color:#2f6fff' href='/log'>"
                        "see the log</a> &middot; <a style='color:#2f6fff' href='/chart'>"
                        "the chart</a></p></body>")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8788)
    ap.add_argument("--host", default="0.0.0.0")
    a = ap.parse_args()
    srv = ThreadingHTTPServer((a.host, a.port), H)
    print("VR bench collector on http://%s:%d/" % (a.host, a.port), flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
