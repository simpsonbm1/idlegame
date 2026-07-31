# Blender pixel-art rig

Renders game sprites as 3D pixel art: low-poly models, orthographic camera,
hard-stepped toon shading, inverted-hull outlines, no anti-aliasing. Output is a
native small PNG with alpha, not a downscale of something larger. Attacks render
as horizontal sprite sheets.

**Status: pilot.** Nothing here is wired into the game yet. The developer's verdict
(2026-07-31) is that these do NOT sit well beside the existing Gemini sprites, so
the open question is now whether an all-Blender art pass is worth committing to,
not whether the two styles can be mixed. See `SESSION_HANDOFF.md`.

## Running it

Blender must be open with the MCP add-on connected. Everything is driven from
Python, so there is no manual modelling step.

```python
import sys, importlib
sys.path.insert(0, r"<repo>/tools/blender")
import build_knight        # builds and renders on import
importlib.reload(build_knight)   # re-run after an edit
```

Renders land in `tools/blender/out/`, which is gitignored. Paths resolve from
`__file__`, so nothing is tied to one machine.

| Script | Produces |
|---|---|
| `pixelrig.py` | the shared rig: materials, geometry helpers, outline, render, upscale |
| `build_knight.py` | guardian knight sprite |
| `build_goblin.py` | goblin brute sprite |
| `build_undead_caster.py` | undead necromancer, built from the written spec with no reference |
| `build_cottage.py` | cottage sprite, near-isometric |
| `build_scene.py` | town-to-battlefield vista, one continuous image |
| `compose_battle.py` | battle band with sprites composited at matched scale (run after `build_scene`) |
| `compose_lineup.py` | all character sprites on one strip, to make style drift visible |
| `build_attack.py` | attack animations as horizontal sprite sheets (`knight()`, `goblin()`) |

## How the style is produced

**Three tones, never more.** Each material is a Diffuse BSDF into Shader-to-RGB
into a ColorRamp set to `CONSTANT` whose three stops *are* the palette colours.
The ramp cannot emit an intermediate value, so a surface is one of three colours
or it is outline.

**Deterministic sampling.** `taa_render_samples = 1`, shadows off, raytracing
off, `filter_size = 0.01`. The tone ramp is a hard step, so any sample jitter
becomes speckle rather than a clean band. One exact sample per pixel avoids it.
This is why `use_shadows` is off and must stay off.

**Outlines measured in pixels.** `outline()` takes a width in *rendered pixels*
and multiplies by `pixel_size(scn)`. Outline weight therefore matches across a
96px sprite and a 288px vista without retuning.

**Standard view transform.** `view_transform = 'Standard'`, and `hexcol()`
converts sRGB to linear on the way in, so a palette hex renders as that exact hex.
AgX or Filmic would desaturate everything.

## Two rules that cost real debugging time

1. **A part belongs to exactly one root.** Sub-assemblies (a sword, a shield, a
   staff) parent to their own root, and only that root parents to the figure.
   Adding a sub-assembly's parts to the figure list as well silently re-parents
   them and discards their angle.
2. **Overlapping parts must be separated in depth.** The outline is an inverted
   hull, so it only draws where a part stands clear of what is behind it. An arm
   flush against the torso produces no internal outline and the figure reads as
   mush. Push limbs toward the camera.

Two more things worth knowing. A flat box shows exactly one tone, which is what
makes blocky armour look dead; `add_ridged()` splays a form into two planes so it
catches two. And an outline only reads against a light tone, so a palette's
shadow stop has to stay well above black.

## Scale matching

One constant governs every character: `SPRITE_PX = 0.0390625` world units per
rendered pixel. Call `sprite_cam(scn, res, target_z)` and it derives the ortho
scale as `SPRITE_PX * res`.

**Pick the cell RESOLUTION to fit a figure. Never pick the ortho scale.** They
look interchangeable and they are not. A larger cell gives a bigger canvas at the
same rendered size; a larger ortho shrinks the figure. The knight uses a 96px
cell, the goblin and the necromancer 112px because they are taller and wider, and
the attack sheets 128px because a raised weapon needs headroom. All four render at
identical scale.

This was gotten wrong once. The goblin was originally built at `4.15 / 96`, which
rendered him about ten percent small against the knight, and the error was
invisible until the two stood side by side on the battle band.

The battle band is `SPRITE_PX * 288` over a 288x112 frame, sharing the 112px
cells' ground row, so a sprite pasted onto it lands at the right size and on the
right line without fitting.

## Animation

`build_attack.py` renders attacks as horizontal sprite sheets. No remodelling is
involved: it puts one pivot at the shoulder, hands it the arm parts and the
weapon root, and turns that pivot once per frame.

**A frame needs two angles, not one.**

`swing` turns the pivot about **Y**. That is the arc the camera sees, because the
camera looks down world +Y and XZ is the only plane a swing shows in. It is
measured from straight up: 0 overhead, 90 level and forward, 180 straight down.
Account for the weapon's own rest angle, since the knight's blade already sits at
132 degrees.

`lift` turns the pivot about **X**, carrying the arm forward in depth, toward the
direction the figure faces. Negative is forward.

Swing alone looks correct in a wireframe and is wrong on screen. A figure's weapon
hand is on the opposite side from the direction it attacks, so a flat arc drags
the arm through the torso, and on a two-handed swing it drives the shoulders up
through the head. Both happened, and both were visible only once the frames played
in sequence rather than sitting in a row. Lift moves the whole arc in front of the
body. Any frame with a real swing needs a real lift, roughly a third of it.

**A pivot must sit on the joint the limb actually turns about.** Anywhere else and
the limb translates as well as rotates, which reads unmistakably as the arm coming
away from the shoulder. A two-handed weapon therefore takes three pivots, not one:
one on each shoulder ball, plus one at their midpoint carrying the weapon. The
hands stay the right distance apart because each arm turns by the same amount
about its own joint, and the weapon tracks the midpoint of the two hands exactly.

Two more things that only showed up in playback. A weapon overlapping the body has
to separate by **value**, since at this size an outline alone will not carry it;
the knight's blade sat inside the armour's own tone range and looked embedded in
his leg until it was brightened to near-white. And an attack whose end pose
resembles its rest pose reads as nothing happening, which is what the goblin did
until frame 1 gained a backward dip as anticipation.

Every frame passes through the same rig, so palette, outline weight and pixel grid
hold across a sheet by construction. Hand-drawn frames are where sprite animation
usually gets expensive; here a new attack is a list of angles.

## Cost, measured on the pilot

| Asset | Primitives | Render passes to acceptable |
|---|---|---|
| Cottage | 20 | 2 |
| Knight | 37 | 4 |
| Goblin brute | 36 | 2 |
| Undead necromancer | 24 | 2 |
| Town-to-field vista | 217 | 3 |

Robed figures are cheaper than armoured ones. One cone replaces two legs, two
boots, two knees and two thighs, which is why the necromancer is two thirds of
the knight. Casters and shamans across the five enemy families are the fast ones.
