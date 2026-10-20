# VR lens bench — optical test chart

A single-page test chart for finding the eye → lens → phone distances of a DIY
phone-in-VR headset. Made for a homemade lens of unknown focal length, so it
measures rather than assumes.

**Live:** https://ziggibot0.github.io/vr-optics/

## What it does

- Two identical halves, one per eye, so both lenses can be checked at once.
- **Siemens star** (centre) — the focus target. Spokes merge into grey when out of focus.
- **1 / 2 / 4 device-pixel line gratings** — the sharpness limit. If the 1px grating
  still shows distinct lines, the phone screen is resolving at full pixel density.
- **Concentric rings** — barrel distortion shows as bows, pincushion as pinched edges.
  If rings look egg-shaped, the phone is too close to the lens.
- **Checkerboard** — contrast plus astigmatism.
- **Text ladder** — four sizes, grades how far out of focus you are.
- **Frame + corner brackets** — the bezel test. If you can see past the white frame
  into black, the phone image is not filling your lens; you need more eye relief or
  a bigger lens.
- **mm calibration** — match the striped bar to a real ruler once; it is remembered.
  Then the chart knows your real screen size, so field-of-view readings are in degrees.

## Use

1. Phone brightness to max, auto-brightness off.
2. Open the URL, match the bar to a ruler, tap **Start test** (it goes fullscreen landscape).
3. Rest your eye at the marked distance, look through the lens, slide the phone until
   the star snaps crisp. Measure that gap — that is your lens → phone distance.

Sibling files in the parent folder build the physical rig: `template.svg` (print at
100% for the card parts and mm gauges) and `solve.py` (turns the measured numbers into
field of view, stack depth, and a helmet fit verdict).
