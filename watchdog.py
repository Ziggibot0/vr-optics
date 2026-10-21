"""Watchdog: make sure the VR bench collector is alive. Prints nothing if healthy.

Used by a no-agent cron job so the collector survives a reboot or a crash
without anyone thinking about it.
"""
import socket
import subprocess
import sys
import time

PORT = 8788
HERE = r"C:\Users\skell\Desktop\vr-optics"


def alive():
    s = socket.socket()
    s.settimeout(1.5)
    try:
        s.connect(("127.0.0.1", PORT))
        return True
    except OSError:
        return False
    finally:
        s.close()


if alive():
    sys.exit(0)

subprocess.Popen(
    [sys.executable, HERE + r"\collect.py", "--port", str(PORT)],
    cwd=HERE,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=getattr(subprocess, "DETACHED_PROCESS", 0) | 0x00000008,
)
time.sleep(3)
if alive():
    print("VR bench collector was down; restarted it on port %d" % PORT)
else:
    print("VR bench collector FAILED to restart on port %d" % PORT)
