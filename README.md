# VR lens bench — the distance test

Answers three numbers, in this order: **f** (your lens's focal length), then **d** (lens → phone screen), then **e** (eye → lens). Those three plus your IPD decide whether the Iron Man helmet fits at all.

Build time ~15 min, no printer needed for the rig (a paper printer is all).

## Files
| file | what it is |
|---|---|
| `template.svg` | print on paper at **100% / Actual size** (not "fit to page"). Cut out: lens frame, eye card, 2 stalks, d-gauge, log table. |
| `pattern.png` | display fullscreen on the phone, landscape, brightness max. Any sharp image works for step 3; this one also lets you read bezel and FOV exactly. |
| `solve.py` | feed it your numbers → FOV, stack depth, helmet verdict. You don't run this; give me the numbers and I run it. |

---

## Step 1 — measure the lens (2 min)

**Focal length:** hold the lens over a sheet of white paper, aim it at a bright window across the room, and move it up and down until the window's image on the paper is *smallest and sharpest*. That lens→paper gap is **f**. Write it down in mm.
**Diameter:** measure across the lens with a ruler.

Why this comes first: your phone distance will land within ~2 mm of f. Guess wrongly here and every later number is wrong.

## Step 2 — build the eyepiece (5 min)

1. Tape the lens into the frame's round hole (recut the hole if your lens isn't ~25 mm).
2. Cut the two stalks at the **same** number — start at **20**. The thick line is height 0.
3. Tape the stalks' 0-ends to the frame, upright, one left one right. Tape the eye card on top of them.
4. Tape the d-gauge to the frame's side so it hangs down past the lens.

Now the eye card's hole is your eye position, the stalk length **is** `e`, and `d` reads directly off the gauge.

## Step 3 — find focus (this is the test)

Phone flat on the table, screen up, pattern fullscreen, brightness max, screen timeout off. Sit down, put your brow against the eye card, look down through the lens at the phone with **one eye**.

Now change **one** thing at a time:

- **Distance `d`:** raise/lower the whole assembly over the phone (books, a box, card shims) until the middle of the pattern is sharpest. The Siemens star should snap crisp and the 1 pixel lines should stop shimmering. Read `d` off the gauge.
- **Eye relief `e`:** with `d` locked in, swap the stalks for 15 / 20 / 25 and note which is comfortable. Take the **smallest** one that doesn't touch your lashes — smaller `e` = shallower headset = helmet has a chance.
- **Both eyes:** second lens at the same `d`, spaced at your IPD. Both images should fuse without strain. Adjust spacing until it does — that's your real IPD, and it may not match what you thought.

## Step 4 — read the failures, they're the design info

| what you see | what it means |
|---|---|
| rings egg-shaped / bowed outward at the edges | phone too close — push `d` out a few mm |
| you can see the phone's black edge past the pattern's frame | lens is bigger than the phone's image at that `e` — increase `e` or use a smaller lens |
| image sharp but eyes ache after 2 min | virtual image is too close — `d` needs to come in ~1–2 mm under `f` |
| can't get sharp at any distance | f is wrong; redo step 1, and check the lens isn't a fresnel with a curved field |

## Step 5 — the helmet verdict

**Stack depth = e + d + phone thickness + 6 mm clearance.** That is how far your eye sits in front of the *back* of the phone.

Helmet works if the faceplate has that much room from your eye to the phone's rear face. Measure that on your face now: ruler from your closed eyelid straight forward until it would hit helmet shell. Slim ski-goggle mask ≈ 85–95 mm of room; a form-fitting Iron Man faceplate is usually **less**, which is exactly why the phone-in-helmet builds put the phone in the forehead and angle it down through prisms instead of pointing it straight ahead.

Typical phone-VR lenses are 42–45 mm, so expect `d ≈ 44`, `e ≈ 18`, Pixel 6 is 8.2 mm thick → **~76 mm stack**. If your lenses come out much longer than that, the helmet is dead and the glasses form is still fine.

## Log it

Fill the table on the printed sheet — one column per attempt: f, lens dia, e, d, sharp?, bezel?, strain. Give me the numbers and I'll run the solver, print the cradle to those exact numbers, and tell you what FOV you're actually getting before you cut any plastic.

---
Caden · `C:\Users\skell\Desktop\vr-optics\`
