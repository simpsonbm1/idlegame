# Blender pixel-art rig

Renders game sprites as 3D pixel art: low-poly models, orthographic camera,
hard-stepped toon shading, inverted-hull outlines, no anti-aliasing. Output is a
native small PNG with alpha, not a downscale of something larger. Attacks render
as horizontal sprite sheets.

**Status: this is the art pipeline going forward** (user decision 2026-07-31). The
AI-generated sprites and the rendered ones do not sit together, so the roster gets
REBUILT here rather than added to. Proven on a knight, a goblin brute, an undead
necromancer built from spec prose with no reference, a cottage, attack sheets for
two characters, and the whole backdrop.

Nothing is wired into the game yet. Three things stand between this and adoption:
the roster is 3 characters against about 47 planned, `SCENE_WALL_FRAC` becomes 0.46
for this backdrop, and unit contact shadows are drawn by `compose_vista.py` rather
than by the game's render loop. See `SESSION_HANDOFF.md`.

## Running it

**The batch way, which needs no Blender window and nobody watching:**

```bash
python tools/blender/render_all.py            # every asset that has a builder
python tools/blender/render_all.py undead     # one group
python tools/blender/render_all.py --list     # what is built, what is not
```

It launches Blender headless once per asset, logs each to `out/logs/`, and ends
by writing the contact sheets. About 2.5 seconds per sprite. Exit code is the
number of failures. Set `BLENDER_EXE` if Blender is not at the default path.

**The interactive way**, for building something new with the viewport in front of
you. Blender open, MCP add-on connected:

```python
import sys, importlib
sys.path.insert(0, r"<repo>/tools/blender")
import build_knight        # builds and renders on import
importlib.reload(build_knight)   # re-run after an edit
```

Both paths build the same scene, because `ensure_rig()` creates the camera, the
key light and the world from scratch when they are missing and leaves them alone
when they are not.

Renders land in `tools/blender/out/`, which is gitignored. Paths resolve from
`__file__`, so nothing is tied to one machine.

**One Blender process per asset, deliberately.** A shared session lets state leak
between builds, and that already happened: the necromancer on disk was rendered
at a KeySun energy of 3.0 while the knight and goblin beside it were rendered at
2.6, because the value drifted during a long interactive session and nothing
reset it. Three "identically rigged" pilot figures were lit 15% apart. A fresh
process per asset makes that impossible for two seconds of startup.

**`KEY_SUN_ENERGY = 2.6` is measured, not chosen.** It was recovered by sweeping
the value until a headless re-render matched the knight and goblin on disk pixel
for pixel, and it does: zero differing pixels at 2.6, drift at 2.4 and at 2.8.
Do not tune it. Anything that needs different light (the backdrop's fill) sets its
own and says why.

## The manifest

`roster.py` lists every asset the game needs, its entry number in
`M15_ASSET_SPECS.md`, its builder module and its cell resolution. `render_all.py`
and `compose_contact.py` both read it, so adding an asset means one line there
plus the builder. `M15_ASSET_SPECS.md` stays the authority on what each asset
DEPICTS; the roster only records how it gets built.

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
| `build_backdrop.py` | the game backdrop at the locked watchtower camera, wall on 46% |
| `compose_vista.py` | characters seated on the backdrop by world coordinate (run after both) |

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

**`target_z` is derived from the cell, never chosen.** World z=0 sits exactly 10%
up from the bottom of every cell -- the knight at 96/1.50, the goblin and
necromancer at 112/1.76 -- and that shared ground row is what lets a sprite drop
onto the backdrop or a contact sheet without being fitted. `spritekit.start()`
computes it, so a builder picks the RESOLUTION and nothing else. Six undead
figures whose builders each picked a plausible-looking target_z came out standing
on six different lines, which is invisible in a single render and unmissable the
moment they line up.

## Building a family

Five of the six enemy families share a body type across their six entries, so a
family is one real build plus five variants. That is expressed as a **family
kit**: `undead_kit.py` holds the palette and the parts that faction repeats (its
skull, its ribcage, its bone limb), and each builder holds only what makes its
figure distinct. `spritekit.py` sits underneath and holds what every character
sprite needs regardless of faction -- ground line, facing, outline weight, sun
angle, tatters, flames, aimed limb segments, and the open/close pair each builder
is bracketed by.

Three rules the Undead Legion cost, each of which had to be rendered to be seen:

1. **One material over a whole figure reads as carved wood.** The death knight
   was built entirely from the family's rust brown and came back a mannequin: the
   tone ramp has nothing to work with when every surface shares a palette, and a
   warm brown at armour scale stops reading as metal. Rust is TRIM on aged steel.
   Rusted armour still has to be armour first.
2. **"Mid-bright" is a constraint, not a suggestion.** The shadow reaver's
   "tattered black cloak" taken literally produced one unreadable mass, because an
   outline only reads against a light tone and his internal edges all vanished at
   once. His palette needed lifting about 60%.
3. **Gaunt, hulking, towering and small are RATIOS, not details.** The reaver read
   as an ape while lit correctly and modelled correctly, because he was as tall as
   a dwarf and as broad as the brute. Height against width, and how much
   background shows between the limbs, is the whole of it at forty pixels. A
   visible neck was worth more than any amount of skull detail.

   Those ratios are measured against the FAMILY THE PLAYER ALREADY KNOWS, not
   against the cell. A goblin common stands 2.5 world units, an orc common 3.6, a
   boss more again. Fitting each figure to a fixed fraction of its own cell -- as
   the generator brief asks, because each generated image was independently
   scaled -- would have made every faction the same size.

And three more the Goblin Raid and Orc Warband added:

4. **A hood must be bigger than the head and set BACK.** The goblin skulker's was
   sized to just clear his skull, so his face filled it exactly, the hood rendered
   entirely behind him, and he came out bare-headed. A hood is only ever visible
   as the margin around a face.
5. **A part's coordinates decide its root.** Anything written in torso-local
   space belongs to the torso root, and anything held by a hand belongs to
   whatever root moves that hand. This was got wrong three times in one evening
   and looked different each time: daggers hanging where the fists would be if
   the goblin stood straight, an orc's chest paint landing at his groin, a mask's
   trim sliding off the mask when the torso leaned.
6. **Armour must be WIDER than the body under it.** The orc brute's cuirass was
   narrower than his chest sphere, so olive hide showed all round the plate and he
   read as an unarmoured orc with a grey patch. Its material also has to separate
   from the skin by VALUE -- a dark armour whose mid tone matches the hide's is
   invisible however black it is in the palette.

One about symbols rather than shapes, which is a different kind of mistake: **a
broad horizontal band across the eyes reads as a tied bandana, not as war paint.**
It did so on all six orcs at once. A vertical stripe down the centre of the face
plus one asymmetric cheek bar cannot be misread, because no garment has that
shape. When a marking looks like an object, change its geometry, not its colour.

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
away from the shoulder.

**One hand on the weapon is a pivot problem. Two hands is an IK problem.** Turning
each arm about its own shoulder keeps both shoulders attached, but it does not keep
the hands a fixed distance apart: the gap between the shoulders is fixed while each
hand's offset from its shoulder rotates, so the separation drifts and the weapon
floats between the fists. A two-handed grip is a closed loop. Drive the weapon,
then solve each arm to reach its grip point with `two_bone_ik()`, which is what
`goblin()` does. Grip points are captured from the rest pose, so frame 0 still
reproduces the static sprite.

Swing a two-handed weapon about a point BELOW the shoulder line. Pivoting on the
shoulders themselves lifts the grip to head height at full raise, and both
forearms fold across the face.

**Give the solver stretch.** The goblin's rest pose already holds his arms at 94
percent of full extension, so almost any motion puts a hand past arm's length.
Clamped, the hand drops off the club; stretched up to about 20 percent it stays
on, and at this resolution the lengthening is invisible. A fully extended arm also
has no elbow left to steer, so the pole vector stops working entirely, which is
worth knowing before spending time tuning one.

**Check clearance with arithmetic, not with your eyes.** Sample each arm segment
and measure its distance to the head volume, then read the per-frame number. Two
rounds were spent adjusting poses that looked plausible in the strip, and the
measurement located the real culprit immediately: the left elbow sitting 0.10
units inside the jaw box, on one frame.

Two more things that only showed up in playback. A weapon overlapping the body has
to separate by **value**, since at this size an outline alone will not carry it;
the knight's blade sat inside the armour's own tone range and looked embedded in
his leg until it was brightened to near-white. And an attack whose end pose
resembles its rest pose reads as nothing happening, which is what the goblin did
until frame 1 gained a backward dip as anticipation.

Every frame passes through the same rig, so palette, outline weight and pixel grid
hold across a sheet by construction. Hand-drawn frames are where sprite animation
usually gets expensive; here a new attack is a list of angles.

## The backdrop

`build_backdrop.py` targets what game.js already expects of the painted backdrop:
the locked "strategy-map-from-a-watchtower" camera, the wall seated so
`SCENE_WALL_FRAC` puts its centre on 46% across, the 2400/1270 kept-region aspect,
and clear ground across the `BUILDING_PLOTS` band because game.js draws the
buildings itself.

It renders at exactly **2x SPRITE_PX**, the density `M15_ASSET_SPECS.md` recorded
as the sweet spot. Holding that density while covering a whole town and
battlefield is what sets the resolution: 60 world units at 2x needs 768 pixels
across. `compose_vista.py` then displays it at 2x, which makes one screen pixel
equal one character pixel, so sprites drop on at 1:1 seated by world coordinate.

**Depth comes from shadows and relief, not from more props.** A flat ground plane
has one normal, so the tone ramp can only ever give it one colour, and it reads
dead beside a character built from curved parts. Two changes fix that, and the
backdrop needs both:

- `enable_hard_shadows(scn)` turns cast shadows back on. `setup_render()` disables
  them because the defaults are stochastic and a hard ramp turns jitter into
  speckle. The setting that actually matters is `shadow_filter_radius`, which at
  its default of 1.0 covers every lit surface in acne. Set it to zero, with no sun
  angular size, one ray and one step, and shadows are exact.
- `add_terrain()` replaces the ground plane with a grid displaced by a height
  function, so the normal varies and the ramp lays down all its greens as terrain
  texture. Several octaves work better than one.

**Smooth-shade that terrain, and then keep it nearly flat.** Flat shading gives
every quad one normal, so each renders as a solid block of one tone the size of the
CELL rather than the pixel. At a 0.85-unit cell that is a 22-pixel square of flat
green behind characters detailed to the pixel, and it reads as a coarser resolution
than the rest of the art. Raising the render resolution does not help; the blocks
only get sharper edges. With smooth normals the shading varies across each quad, so
the ramp's steps set the band edges and those follow the terrain's contours instead
of its topology.

Displace with **fractal noise, never a stack of sines**. Separable `sin(x)*cos(y)`
terms are a regular lattice by construction, and no number of octaves fixes that:
they keep lining their peaks up in rows, which renders as diagonal ribbons across
the ground. `mathutils.noise.fractal` has no preferred direction and no repeat.

**Flatten hardest where the action is.** The battle line already carries two
formations, their contact shadows and the road. Textured ground underneath competes
with the thing the player is meant to be watching, and the busiest patch of terrain
should not sit under the busiest patch of gameplay. `BATTLE` is an ellipse over the
combat zone where the relief drops to about 5%, tapering back to full toward the
frame edges.

Then scatter a few CALM patches where the relief eases toward flat. The plaza
produced one of these as a side effect of being flattened for its paving, and that
break was the part of the ground that read best, so the effect is worth placing
deliberately rather than leaving to accident.

Once shading is smooth, drop the amplitude hard. Crossing one ramp stop in the lit
cluster takes about 2.3 degrees of tilt, so very little slope produces plenty of
tone. High relief is only needed while the ground is flat-shaded and every tone has
to come from a visible facet; left high afterwards it reads as rolling hills. Weight
the height function toward its FINE octaves, since the broad rolls are the part that
reads as terrain rather than as surface.

**Measure the shading range before choosing ramp stops.** Swap a material's ramp
for a linear black-to-white one, render, and histogram the pixels, converting sRGB
back to linear first because the ramp reads linear while the saved image does not.
With hard shadows the distribution is BIMODAL: in this backdrop the ground clusters
over 0.13-0.33 and 0.63-0.83 with nothing at all between 0.375 and 0.625. Evenly
spaced stops strand half of themselves in that gap, which is why raising the step
count from three to six changed almost nothing on screen. Pass `positions` with a
group of stops inside each cluster instead. Re-measure whenever the lights change.

**A cast shadow receives zero direct light**, so it lands on the darkest stop no
matter how many stops exist, and every shadowed area comes out one flat colour. Add
a fill light with `use_shadow = False`. It lifts shadowed surfaces off the bottom
stop and, because it still varies with surface normal, gives the shading inside a
shadow somewhere to go.

**Distance dressing must not cast.** Anything that exists only to hide a seam or
stand in for distance needs `visible_shadow = False`: the masking treeline at the
ground's far edge, the mountains, the haze strip, and above all THE SKY PANEL. The
sky is a 200-unit box standing 44 tall, and left casting it drops a shadow across
most of the battlefield with nothing visible in the frame to explain it.

When hunting a shadow whose source is unclear, unlink candidate objects one at a
time and compare the mean brightness of the region, rather than toggling their
shadow flag. A group can change the average simply by removing its own dark
pixels, so removal alone does not prove it was casting; confirm with the flag once
you have a suspect.

**Step count is a per-asset decision.** `toon_mat(..., steps=N)` sets how many
shades the ramp holds. Three is right for a character sprite, where curved parts
turn through all three across a few pixels and the flatness reads as punch. Three
is wrong for a backdrop, where surfaces are large, each holds a single tone, and
the whole scene reads as cut paper with no gradient anywhere. The backdrop uses
six. Widen the three palette anchors when raising the count, or the extra shades
interpolate into near-identical colours and buy nothing.

**Light azimuth is per-camera, because screen-up is.** For character sprites the
camera is near level, so screen-up is world +Z and "lit from the upper left" means
a sun azimuth around -40. For the top-down backdrop screen-up is world **+Y**, and
that same -40 puts the light at the BOTTOM left, throwing every shadow up-screen.
Do not swing it fully to the top either: we look along -Y, so the slopes we can see
are the ones facing -Y, and lighting straight down-screen back-lights all of them
and darkens the whole ground. About -105 keeps the sun left and slightly above,
which throws shadows right and a little down while the ground stays lit.

**Snap repeating detail to the pixel grid.** Pass `snap_u` and `snap_v` to
`tile_top()`. They are the world size of one rendered pixel along each axis;
`snap_v` is the pixel size divided by cos(camera elevation), since depth
foreshortens. Without them the mortar gap is a fraction of a pixel wide and its
phase drifts across the surface, so the lines fade in and out in broad patches.
That looks like a texturing bug and is really moire.

**A squashed sphere reads as a disc from a steep camera.** Tree canopies built as
spheres scaled to 0.82 in Z looked drawn from straight overhead, because a steep
camera foreshortens height by sin(elevation) while width comes through at full
size. Canopies need to be taller than wide before any of their side shows.

**Masonry has to be built, not coloured.** A wall made of one box reads as poured
concrete, because one box is one normal and therefore one tone, and no palette
change fixes that. `tile_top()` and `tile_face_y()` lay staggered blocks over a
surface, each a touch taller or more proud than its neighbour, so the hard shadows
cut the mortar lines for free. Put a DARKER material on the slab underneath and the
gaps read as mortar. Cycle two or three stone tones so the courses do not look
printed. Size the blocks against the surface they sit on: 0.52-wide flagstones on a
1.15-wide wall walk gave two across and read as ladder rungs, where 0.37 gives three
and reads as stone.

Scatter props as solids rather than flat decals so they catch light and cast their
own small shadows, and taper the relief to nothing where the wall and plaza stand
so nothing has to be sunk into a slope.

Watch the arithmetic when scattering by index. `(i * 7) % 21` yields only three
distinct values because 7 divides 21, which put every grass tuft on one of three
rows across the frame. Use a multiplier coprime with the modulus.

Two things an orthographic camera forces, both of which cost a debugging round:

1. **There is no horizon.** Distance never thins anything out, so the ground plane
   would run off the top of the frame. End the ground at a chosen depth and stand
   the range and a sky panel just beyond it. Hide the cut with a haze strip and a
   continuous distant treeline.
2. **Distant scenery must be a standing flat, not a solid.** A cone wide enough to
   read as a mountain is equally wide in DEPTH, so its near edge reaches forward
   past everything in front of it. One mountain was poking through the town wall
   and out onto the grass. Squash distant cones to about 0.16 in Y.

## Grounding the units

Sprites are composited, so they get no shadow from the backdrop's sun. Without one
they float. `compose_vista.py` draws a contact ellipse under each unit, offset the
way the sun throws it, which on this backdrop is right and slightly down.

It is a CONTACT shadow, not a projection. A geometrically correct one would run
about 94 screen pixels from a figure 40 pixels wide, and a formation would turn
into a thicket.

The ellipse darkens the ground it covers and then snaps the result back onto the
backdrop's own palette, so a shadow never introduces a colour the scene does not
already contain. A plain translucent overlay would, and it reads immediately as a
layer sitting on top rather than as part of the art.

**Keep the battle line out of the wall's cast shadow, and measure where that
actually ends.** Everything on the wall throws its shadow right, onto the field
where the fighting happens, and the GATEHOUSE governs the reach, not the curtain
wall. The towers stand about 6 world units against the wall's 3.2, so they shade
nearly twice as far and a line placed clear of the wall was still inside them.
Sample the rendered ground along the line instead of estimating: here it read 0.23
out to x = 5 and 0.45 from x = 6, so the line forms up past 6.

A fully lit sprite standing in a shaded band looks pasted on. Moving the line clear
is free; darkening sprites that stand in shadow means the game has to know the
shadow's shape at runtime, which is a much bigger commitment.

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
