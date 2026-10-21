@echo off
REM VR lens bench collector. Double-click to run, or let the Scheduled Task start it.
start "" /min python "%~dp0collect.py" --port 8788
