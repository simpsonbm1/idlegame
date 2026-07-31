# Blender pixel-art rig

Renders game sprites as 3D pixel art: low-poly models, orthographic camera,
hard-stepped toon shading, inverted-hull outlines, no anti-aliasing. Output is a
native small PNG with alpha (96x96 for characters), not a downscale of something
larger.

**Status: pilot, awaiting the developer's style verdict.** Nothing here is wired
into the game yet. The knight, goblin, cottage and vista were built to answer one
question, which is whether rendered pixel art can sit beside the existing Gemini
sprites. See `SESSION_HANDOFF.md`.

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
| `build_scene.py` | town-to-battlefield vista, one continuous 288x96 image |
| `compose_battle.py` | battle band with sprites composited at matched scale (run after `build_scene`) |
| `compose_lineup.py` | all character sprites on one strip, to make style drift visible |

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

Sprite and backdrop share a pixel size, computed as `ortho_scale / resolution_x`.
The character sprites use `3.75 / 96` and the battle band uses `11.25 / 288`, both
equal to `0.0390625` world units per pixel. A sprite dropped onto the band is
therefore the correct size with no fitting.

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
