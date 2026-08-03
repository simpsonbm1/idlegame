# Blender pixel-art rig

Renders game sprites as 3D pixel art: low-poly models, orthographic camera,
hard-stepped toon shading, inverted-hull outlines, no anti-aliasing. Output is a
native small PNG with alpha, not a downscale of something larger. Attacks render
as horizontal sprite sheets.

**Status: this is the art pipeline going forward** (user decision 2026-07-31), and
**the roster is complete**: 83 assets, every character and building the game needs.
Nine heroes with 27 rarity variants, 30 enemies across five families, eight
townsfolk and nine buildings. `python tools/blender/render_all.py` rebuilds all of
it in about three minutes.

Nothing is wired into the game yet. Three things stand between this and adoption:
no human has judged the roster, `SCENE_WALL_FRAC` becomes 0.46 for this backdrop,
and unit contact shadows are drawn by `compose_vista.py` rather than by the game's
render loop. See `SESSION_HANDOFF.md`.

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

**A hero's rarity tiers are four DIFFERENT PEOPLE** (user ruling 2026-08-01), named
by `DESIGN.md` and built as branches inside the one builder so `attack_roster.py`
keeps generating their attack sheets. Three rules the rework paid for in rejected
renders. Height is not spendable, because `spritekit.finish()` scales the body to
the role height and a taller tier just shrinks itself. Overlapping cones fuse, so
a cloak stays narrow and behind the legs and only one mass sits at the shoulder
line. And a coloured garment over a leather body still reads leather, because the
torso's chest sphere is wider than the jerkin in front of it. Every base sprite is
verified pixel-identical after a tier rework; `H.stance()` must not be called on a
hero whose own art is the epic or legendary tier.

**EVERY CHARACTER AND EVERY VARIANT IS INDIVIDUALLY DESIGNED** (user ruling
2026-08-02). They are not reassembled from parts shared with other units. `hero_kit`
and `spritekit` exist for the things that must be IDENTICAL across the roster -- the
rig, the palette, the outline weight, role height, limb construction -- not for
identity. Anything that says who a character is belongs in that character's own
builder. `hero_kit.head(helm=...)` is the cautionary case: one generic helmet shared
by three heroes, and it read as a soft cap on all of them. It is deprecated; the
paladin now builds his own three, and the fighter and banneret should grow theirs.

**A part written in torso-local coordinates must go in `tors`, not `detail`.**
Everything in `tors` is parented to `tors_root`; `detail` is parented to the FIGURE
root instead. A paladin visor slit written at z 1.24 therefore rendered 1.4 units
lower, buried inside his chest, and no visor slit on that hero had ever appeared.
To skip the outline on a torso part, collect it in its own list, append that list to
`tors`, and pass the names through `skip_extra`.

**A HAND IS SIZED BY ITS RATIO TO THE WRIST, AND COMPARED ACROSS LINES IN WORLD
UNITS.** The user's verdict on the battlemages was "their hands are too big",
measured against the assassin. Two separate causes, and the second is the one that
matters. `spritekit.limb()` builds a hand at `fore_r * 1.7`, which is 2.02 times the
wrist it grows from once the forearm's own 0.84 taper is counted; the assassin's
hand-written arms give 1.40. **Half of a mitt is a wrist too thin, not a hand too
wide.** Fix both or the hand still reads wrong at a smaller radius.

Compare sizes in WORLD units, never in builder coordinates. `finish()` scales every
figure to the role height, and the factor it prints varies from 0.84 to 1.16 across
the roster, so identical builder numbers render at different sizes. Read the factor
off the render log line: `scaled 0.913 to 2.95 units`.

`limb()`'s default is still 1.7 and both judged robed lines now override it: the
battlemage and the mender pass `upper_r=0.145, fore_r=0.14, hand_r=0.17`, and any
third robed hero should pass the same three so they match on the `heroes` sheet. What
still takes the default is the frost adept, the eight townsfolk and `infernal_kit`,
all of them unjudged. **Do not "fix" the default to sweep them in.** Changing a shared
default silently re-renders every figure that ever accepted it, including ones already
signed off; each family takes the override when its own review comes round.

After any edit to a shared kit, prove the approved sprites did not move by rendering
them and counting differing pixels against `assets/rendered/sprites/`. Blender can do
it in one `--python-expr` with numpy over `bpy.data.images`, and the count separates
the two cases outright: the mender read 0 across all four tiers when only the
parameter was added, and 98-126 once it actually opted in.

**A CONE IS PLACED BY ITS CENTRE AND AIMED BY ITS LOCAL +Z.** Both bite when you
grow spikes out of a figure, and the frost adept's ice shards hit all four faces of
it. `add_cone` centres on the location given, so a shard placed at the shoulder
buries half its length inside the body and the visible half reads as a fringe on the
collar; compute the centre as `base + direction * length / 2` instead. Its axis is
local +Z, which `rot=(0, ry, 0)` maps to `(sin ry, 0, cos ry)`, so aiming a left-side
spike outward and up needs ry NEGATIVE -- the sign that looks right is the one that
points every shard back into the chest. Make them SHORT AND FAT: at 0.13 across a
1.20 length they taper away within two pixels and read as antennae. And they must
CONTRAST with what they grow from, which `ice` shards on an `ice` robe did not, so
they had never once existed.

**A SHOULDER WRAP IS WIDE AND SHORT, NEVER A CONE.** A cone whose base is at the
chest and whose top is at the neck flares DOWNWARD, and at 112 pixels that reads as a
bib rather than as fur over the shoulders -- the user could not identify it on two
separate figures. Use two overlapping spheres across the shoulder line sharing one
material: the inverted-hull outline draws no seam where they meet, so they read as a
single wrap that follows the shoulders.

**ONLY ONE MASS AT THE SHOULDER LINE, AND MAKE IT CURVED.** The warmage carried a
wide shallow mantle cone, pauldrons and a cuirass at the same height, and the three
fused into one flat plate jutting across his chest. A 0.32-deep cone is a disc: it
has one normal, so the ramp gives it one tone, and it is the widest thing on the
figure. Spheres survive where it cannot, because they turn through all three tones
and read as two bumps rather than one slab. Pick the pauldrons and delete the rest.

**A HELD SHAFT MUST NOT TILT ITS HEAD ACROSS THE FACE.** The battlemage's war-staff
leaned top-toward-the-body at 24 degrees and put its spearhead over his own cheek.
Measure the blade tip's x against the HEAD's span, not against the figure: the head
is about 0.27 either side of centre, so the tip needs to land past that with a few
pixels to spare. Twelve degrees over a 2.3 shaft still leans ten pixels, which is
plenty to read as angled.

**HEADGEAR GOES ON ITS OWN ROOT, LIKE A WEAPON.** `finish()` measures `figure` and
scales the body to the role height, so a hat or a crest listed in `figure` makes the
man under it shorter to pay for itself. Parent it to its own root and pass that root
in `roots`: it is still outlined, because `outline_all` walks the whole scene, and it
is no longer measured. `crown_root` in `build_hero_battlemage.py` is the worked case.

**A CREST IS AN ARC GROWN OUT OF THE HELM, NOT A BOX STOOD ON IT.** A tall rectangle
seated on the warmage's helm read as a gold signboard floating over his head. Two
things fix it, and it needs both: give it a tapering outline with `add_prism` so its
shape says crest, and bury a third of it inside the shell, because a part that merely
touches another part reads as a separate object.

**A POSE HAS TO BE A GRIP A PERSON WOULD USE.** Four assassin arm poses picked purely
for outline shape did separate the silhouettes and were rejected anyway: "the way he's
holding the knives now doesn't really make sense" (user, 2026-08-02). Start from how
that kind of fighter actually holds the weapon -- a duellist's extended line, a knife
fighter's guard -- and the outline change falls out of the stance for free.

**ANYTHING THAT RIDES A LIMB MUST BE DERIVED FROM THAT LIMB'S POSED POSITION.** Wrist
bracers written at fixed coordinates stayed where the old pose's wrists had been once
the assassin's arms moved, and rendered as boxes floating at his waist. Interpolate
from the fist toward the elbow instead.

**A DETAIL HAS TO BREAK THE SILHOUETTE OR IT DOES NOT EXIST.** The pig-faced
bascinet's snout projected 0.08 past its helm shell, which is about two pixels, and
was invisible. At 112 pixels a figure is read from its outline first, so a feature
that stays inside another part's hull is wasted geometry. Measure the projection
against the shell it grows from, not against the figure.

**A LIMB'S SEGMENTS MUST TAPER INTO EACH OTHER, AND A JOINT SPHERE IS NOT THE FIX.**
The outline is a per-object inverted hull (`pixelrig.outline`), so every part's end
CAP carries its own dark shell and a cap sitting in open air draws a line straight
across the limb. A shoulder, an upper arm, a forearm and a fist therefore read as
four separate segments, which is what the developer saw on the fighter: "upper arm,
joint 1, another arm segment, joint 2, another arm segment, joint 3, another arm
segment, hand" (user, 2026-08-01). Adding an elbow sphere makes it worse, because
one more part is one more line.

Build each segment so it **ends narrower than the piece that swallows it**. On the
fighter that is a shoulder sphere burying the upper arm's top, an upper arm tapered
from 0.155 down to 0.10 so the forearm's wide elbow mouth sleeves over it, and a
fist burying the wrist. Use `add_cone`, not `add_cyl`. Check the burial in numbers
rather than by eye: the swallowed cap's RIM has to be inside the swallowing solid,
and it was the shoulder sphere's y offset, not its radius, that left the fighter's
last line in place.

Two things this constrains. `spritekit.limb()` builds the same five-part chain and
has the same exposure wherever a limb is fully visible; it survives on the archer
only because the bow hides his arms. And `animkit.twohand_sheet` solves an arm with
IK, posing only `upper`, `fore` and `hand`, so any extra joint object would stay
behind while the arm swings.

**Every contact-sheet cell is captioned with its roster key** (user, 2026-08-01:
three mender rarity variants were indistinguishable on the sheet, so there was no
way to SAY which one needed the edit). Labels are stamped into the 1x sheet before
the upscale, which is what makes label pixels the same size as sprite pixels;
`pixelfont.py` explains why the font is data rather than a call to Blender's `blf`.

**The interactive way**, for building something new with the viewport in front of
you. Blender open, MCP add-on connected. On a machine that has never had it,
set the connection up first:

```powershell
pwsh -File tools/blender/setup-blender-mcp.ps1 -WhatIfOnly   # say what it would do
pwsh -File tools/blender/setup-blender-mcp.ps1
```

That installs `uv`, clones the upstream `blender_mcp` repository, copies the
add-on into Blender's extensions folder, builds the server's virtualenv and
registers the MCP server with Claude Code. Two steps stay manual: ENABLE the
add-on in Blender's preferences, and restart Claude Code. The headless pipeline
needs none of this.

Three traps it now handles, all found setting up LAPTOP-7EN0K6TP on 2026-08-01.
Upstream asks for `mcp[cli]>=1.2.0` with no upper bound but imports
`mcp.server.fastmcp`, which mcp 2.0.0 deleted, so a fresh clone resolves to a
version that cannot start; the script pins the checkout below 2.0 and builds the
virtualenv immediately, so a bad resolve fails loudly at setup instead of
silently at first use. The `claude` CLI is absent under the desktop app, so
registration falls back to writing the top-level `mcpServers` key of
`~/.claude.json` itself, as a text splice rather than a re-serialise, keeping a
`.bak-preblender` backup. And `-BlenderVersion` names the extensions folder, so
a wrong value used to install into a folder no Blender reads while reporting
success; it now warns when the machine has config for other versions.

Drop the pin step when upstream supports the mcp 2.x API. It is a local edit to
the checkout's own `pyproject.toml`, so it can conflict on a `git pull` there.

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

**`out/` is SCRATCH; `assets/rendered/` is the artifact.** The scratch directory
holds debug renders, probe images and eight-times upscales, and a render pass
rewrites all 350 files in it.

**IF LOOKING AT IT REQUIRES A RE-RENDER, IT IS NOT AN ASSET** (user ruling
2026-08-02: "if it requires re-rendering then it isn't a durable artifact and I do
not consider it an asset"). That covers contact sheets, not just sprites. Anything
a human is asked to judge belongs in `assets/rendered/`.

**`publish.py` is the ONLY path from `out/` to `assets/rendered/`, and the
pre-commit guard enforces it.** The full cycle for changing any art:

```bash
python tools/blender/render_all.py <group>       # or render_attacks.py <key>
python tools/blender/publish.py --dry-run        # truthful: what actually changed
python tools/blender/publish.py <key filters>    # copy + sheets + manifest
git add -A && git commit                         # guard cross-checks the manifest
```

Publishing copies each pixel-changed image to `assets/rendered/` named by roster
key, recomposes every canonical contact sheet FROM the published files, and
records every pixel hash in `assets/rendered/manifest.json`. Three properties
carry the whole cross-machine story:

- **Change detection is by PIXEL HASH** (`pixhash.py` -- THE one definition,
  Pillow under the system Python), because Blender's PNG bytes vary per run.
  `--dry-run` reporting "0 changed" after a re-render of untouched builders is
  the expected result, and 115 files were verified to report exactly that, in
  0.3 seconds. The old byte-compare called all 83 sprites changed every time,
  which is why publishing degenerated into the hand copies that caused every
  drift. **Changing the hash definition means regenerating the manifest
  (`publish.py --init-manifest`) in the SAME commit** -- no two definitions may
  coexist.
- **Canonical sheets are composed from `assets/rendered/`, never from `out/`.**
  `out/` is gitignored and never travels, so on 2026-08-02 sheets composed from
  it were committed showing four banneret sprites and twenty hero attack sheets
  the repository did not have. A sheet is a claim about the repository, so it is
  built from the repository; a stale `out/` can no longer poison one. The
  composers write CANDIDATES into `out/` and `publish.py` does all bookkeeping:
  Blender turns pixels into pixels, one system-Python tool owns every hash. The
  renderers no longer auto-compose canonical sheets at all. For judging
  UNPUBLISHED renders, the scratch modes remain: `compose_contact.py -- --line
  <hero>` and `compose_attack_contact.py -- <filter>`, both reading and writing
  `out/` only.
- **The guard verifies the STAGED PIXELS themselves.** Three layers: art
  obliges its sheets in the same commit; every sheet's recorded inputs must
  match the manifest's current entries; and every staged PNG is decoded from
  its staged git blob and its pixel hash must equal its manifest entry. That
  third layer is what catches a hand copy smuggled around `publish.py` -- it
  was fire-verified refusing a real commit of a hand-copied sprite. The guard
  FAILS CLOSED if Pillow is missing under the hook's interpreter, printing the
  install command; it never degrades to the text-only check.

Judging happens from `assets/rendered/` (the attack preview and the committed
sheets both read it), so publish BEFORE asking for a verdict and `git checkout`
to reject. Publishing stays deliberate to keep history small: PNGs do not
delta-compress, and four full render passes in one evening would have added
about 76 MB if `out/` were committed.

Machine bootstrap: both interpreters need the imaging libraries, because the
hook invokes `python` while sessions use `py`, and on Windows those are two
different installs:

```bash
py -m pip install pillow numpy
python -m pip install pillow numpy
```

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

| Layer | What it is |
|---|---|
| `pixelrig.py` | the renderer: materials, primitives, outline, cameras, render, upscale |
| `spritekit.py` | what every CHARACTER sprite needs: ground line, facing, role heights, limbs |
| `building_kit.py` | what every BUILDING needs: isometric camera, walls, roofs, doors |
| `<family>_kit.py` | one per faction: its palette and the parts it repeats |
| `build_*.py` | one per asset. A builder is the figure and nothing else. |
| `roster.py` | the manifest: 83 assets, their builders, cells and tiers |
| `render_all.py` | headless batch driver, one Blender process per asset |
| `compose_contact.py` | per-group contact sheets, written at the end of every run |
| `compose_attack_contact.py` | attack contact sheets: one captioned row per character |
| `probe_rig.py` | where a part is and where it goes, per frame, in world units |
| `pixelfont.py` | 5x7 bitmap font, so sheet labels are hard pixels like the art |

Still here from the pilot: `build_scene.py`, `compose_battle.py`,
`compose_lineup.py`, `build_attack.py` (attack sheets for two characters),
`build_backdrop.py` (the game backdrop, wall on 46%) and `compose_vista.py`.

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

## How big anything is

**USER RULING 2026-07-31:** "The normal enemies and the heroes should be roughly
the same size, maybe slightly bigger or smaller depending on type, and the bosses
should be noticeably much bigger."

So height is set by ROLE, not by faction. `spritekit.ROLE_SCALE` multiplies a
`NORMAL_HEIGHT` of 2.95 world units, which is the guardian knight's own height
because he is the style anchor and was already built to it:

| role | height | |
|---|---|---|
| brute | 3.16 | the family's heavy |
| hero, caster | 2.95 | the baseline |
| shaman | 2.89 | |
| skirmisher | 2.83 | |
| sapper | 2.74 | the family's smallest |
| boss | 4.43 | 1.5x, not slightly |

**A builder passes `role=` and never sizes its own figure.** `finish()` measures
the assembled body and scales the figure root to hit the target exactly, so a
builder's coordinates only ever have to be in PROPORTION. Sizing by hand is what
put the goblins at 2.5 units against the orcs' 3.6.

Faction identity therefore lives entirely in width, build and palette. A goblin
is a goblin because he is wiry, an orc because he is broad, and they are the same
height. That reads better anyway: two figures of different widths at one height
are easier to tell apart than two of the same width at different heights.

Three things this machinery gets right that are easy to get wrong by hand:

1. **Pass `body_roots` for any figure whose torso hangs off a root.** Otherwise
   only the legs are measured, and scaling a pair of legs to a whole body's
   target made every goblin and orc render about two and a half times too big.
2. **Weapons are excluded from the measurement.** A raised staff must not shrink
   the character holding it.
3. **Outline width is divided by the scale factor.** Scaling the root scales the
   inverted hull with it, and outline weight is the one thing that has to be
   identical on every sprite whatever its size.

Do not use `ob.matrix_world` to measure. It is evaluated by the ACTIVE scene's
depsgraph, and in background Blender the active scene is the startup file's
"Scene" rather than "PixelPilot", so the matrices read stale.
`spritekit._world_matrix` composes the parent chain by hand instead.

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
weapon root, and turns that pivot once per frame. `render_attacks.py` drives the
whole roster from `attack_roster.py`, and `compose_attack_contact.py` writes the
review sheets, one captioned row per character.

**A REPARENT MUST PRESERVE THE CHILD'S EXISTING PARENT CHAIN.** This is what made
every attack sheet in the repository show detached limbs, for months, on every
character at once. `reparent_keep` set ONE shared parent inverse -- the pivot's
own inverse -- on every part it took, which is correct only when a part's basis
matrix already is its world matrix, meaning it has no parent. No part of a
finished figure qualifies: `spritekit.finish()` parents everything to a figure
root and scales that root to the role height. The fighter's arms were therefore
handed the figure's 30-degree facing and 1.08 scale BACKWARDS, and his fist
jumped 1.64 units on reparenting alone, landing below the ground line. The
correct inverse is per-object: `new_parent_world⁻¹ @ child_world @ child_basis⁻¹`.

Two things made it survive so long. Nothing errors -- the sheet renders, the
process exits zero, and only a human looking at the image would catch it. And
`pixelrig.world_matrix` composed only the basis matrices, dropping the
`matrix_parent_inverse` term from Blender's own
`world = parent.world @ parent_inverse @ basis`, which was harmless while
`parent_all` set every inverse to the identity and wrong the moment animation set
a real one. Measure a reparent rather than looking at it: render the rest frame,
read one part's world position before and after, and the answer is a number.

**SWING IS SIGNED AGAINST THE FIGURE, NOT THE WORLD.** A pivot turns about world
Y, which points one fixed way, while heroes face +30 degrees and every enemy
family faces -30. One table of angles therefore drives a hero forward and an
enemy backward. `animkit.facing_sign` reads the figure's own root and flips the
rotation, so `attack_shapes` can state one meaning: **positive swing carries the
weapon forward and down, the way the figure faces.** `OVERHAND` was authored on
the knight, who faces right, and `SMASH` on the goblin brute, who faces left, so
the shared tables disagreed from the start and half the roster played its attack
in reverse -- the fighter's overhead smash came out as an underhand scoop. `lift`
does not flip: it turns about X toward the camera, and both facings are only 30
degrees off camera-on.

**A DUAL-WIELDER NEEDS ONE PIVOT PER ARM, ON ITS OWN SHOULDER.** Both shoulder
balls are usually built in one loop and so share a single name, and a name is all
`top_joint` has to choose by, so `("shoulder",)` on both arms put BOTH pivots on
whichever ball sat highest. The far arm then swung about a joint a foot away and
the assassin's knives went over his head. Derive each pivot from that arm's own
upper segment instead, written `^upperL`: the caret means the part's TOP rather
than its centre, and an upper arm's top IS its shoulder.

**KEEP THE SHOULDER MASSES OUT OF A LARGE TWO-HANDED SWING.** A two-handed grip
pivots about the midpoint between the shoulders, and rotating the shoulder
spheres with it by 92 degrees sweeps one of them from beside the head to above
it, straight across the face. Rotate the arm chain and the weapon; leave the
shoulder balls on the torso. They bury the upper arms' tops well enough that no
gap opens at the joint.

**AN ARM TURNS ABOUT THE TOP OF ITS OWN UPPER ARM.** That point is the shoulder
joint, and a rotation leaves its own centre exactly where it was, so the shoulder
ball on the torso keeps covering the arm's top. Any other centre translates the
arm as well as turning it and the joint comes apart in view: the ball's own
middle, the midpoint between two shoulders, a point on the chest. The fighter's
shoulder was rejected as separating twice before this was understood (user,
2026-08-02). Write the joint as `^upperL`, which means that part's TOP.

**A WEAPON NEEDS A SECOND PIVOT AT THE FIST.** Reach is radius, and an arm
rotation alone moves a weapon only as far as the hand goes. Give the weapon its
own pivot at the hand, chained under the arm's, and the two rotations compound so
the far end sweeps further than the arm is long. **They ADD, so budget the
total** rather than each one: the paladin's hammer at 182 degrees combined passed
straight down and came back up behind him, and the measured path doubled back
between two frames.

**A RIGID PIVOT CANNOT RAISE A GRIP OR EXTEND AN ARM, AND MOST ATTACKS ARE MADE OF
THOSE TWO MOTIONS.** A pivot welds an arm and its weapon into one piece turning
about one point, so it can spin a weapon and drag a hand along a short arc, and
that is the whole of what it can do. Four heroes were rejected in one pass for
exactly this (user, 2026-08-02): the fighter "holding the sword at crotch-level
and flicking it", the paladin "reverse-flicking" his hammer, the assassin "still
not extending his arms", the archer "just punching himself in the stomach". No
table of angles fixes any of them, because the geometry cannot express the motion.

Use `animkit.ik_poses` instead, declared in the roster as `Attack(..., ik=IK(...))`.
It drives the WEAPON along a path and solves each arm to reach its own grip, so
elbows bend and nothing rotates about a shoulder to be torn off one. **A frame
then carries five columns, `(lift, swing, lunge, dx, dz)`**, and the last two move
the weapon in world x and z. The travel is where the attack lives; the rotation
only angles the blade. The fighter's chop moves his left fist from world z 1.28 to
1.86 on the raise and out to x 1.01 on the strike, where the pivot version held
that same fist within 0.01 of its rest height across all eight frames.

**FRAME 0 MUST REPRODUCE THE IDLE SPRITE, AND IT IS THE FIRST THING TO CHECK ON AN
IK ENTRY.** A part's `location` is NOT where it is: it is an offset inside its
parent, and these figures' parents carry the 30-degree facing and the role-height
scale. The solve used to aim an arm from a WORLD shoulder at a target built from
LOCAL fist positions, two spaces about 0.8 units apart on the fighter. Nothing
errors and the sheet renders; the arm simply reaches for the wrong point. Probe
the rest pose against frame 0 and the mismatch is one column of numbers.

**A HAND HAS TO BE ON THE HANDLE IN THE MODEL, AND STANDING STILL HIDES IT.** The
fighter's lower fist sat at sword-local z +0.129, inside a crossguard spanning
+0.066 to +0.174, with the grip entirely below both hands at -0.240 to +0.040. It
was invisible in the idle sprite because a vertical sword puts the guard behind
the hands from this camera, and obvious the moment the sword swung away from the
body (user, 2026-08-02). Fix it by moving the HILT to the hands rather than the
hands to the hilt: re-posing an arm disturbs segment angles tuned so no end cap
shows in open air. Measure it in the WEAPON's own space, where a grip is a z range
and a fist is one number.

Known and accepted on the fighter: his fists are built 0.65 apart and straddle the
hilt, sitting about 0.30 off its centre line sideways, so the far hand reads as
floating. Closing it means re-posing both arms inward. The developer called it
close enough (user, 2026-08-02).

**A WEAPON'S REST POSE DECIDES WHETHER IT CAN BE ANIMATED AT ALL.** Check where its
mass sits relative to the hand BEFORE writing any angles, because the answer may be
that the sprite has to change. Two heroes needed it (user approved both,
2026-08-02). The paladin carried his warhammer head-up, which put the head at world
z 2.14 with his shoulder joint at 2.15: the head sat on the pivot, so rotating his
arm spun the hammer about its own head and no table could help. Carried head-down
with the grip at the top of the haft, the head hangs 1.75 from the shoulder and
travels 2.5 units from wind-up to impact. The banneret had one hand on a five-unit
polearm, so his attack could only ever be one-handed; his pole came in from x -0.94
to -0.72 for the right arm to reach, and -0.72 is the limit, because past about
-0.70 the shaft lies across his face.

**A BUSINESS END BELOW ITS PIVOT INVERTS THE SIGN.** Rotating about Y sends a point
ABOVE the pivot forward and a point BELOW it backward, so a head-down hammer and a
blade-down dagger both need their swing column negated against the table
convention. Measure the tip rather than reasoning about it. The assassin's blade
read +0.41 forward on his WIND-UP frame and -0.92 back on his strike, which is the
whole attack playing in reverse, and it looked plausible enough in a strip that it
survived a review.

**A STAFF'S WRIST ROTATION STAYS SMALL.** The hand grips a staff near its middle,
so turning it about the hand spins it end over end and reads as baton twirling. At
38 degrees the battlemage's crystal came down to hand height and the butt swung up
behind him. The arm carries a staff; the wrist only angles it.

**DO NOT ROTATE `torso_root`.** It sits on the hip, so it looks like the waist
joint a big swing wants, and it is not one: the torso is a cylinder and a sphere
meeting the legs flat, and turning them 20 degrees tears the belt off the hips and
sinks the head between the shoulders. The fighter and the paladin were both tried
that way and both came out broken.

**A LUNGE IS A STEP IN WORLD X, TOWARD THE ENEMY.** Translating a figure in world
Y buys nothing, because that is the axis the camera looks down: at its 3-degree
tilt a 0.3 move is under half a pixel on screen. The step is multiplied by the
facing sign, so heroes go right and enemies left off one shared table.

This matters more than any angle. **A rotation alone never sends a weapon at
anybody**, which is why the assassin read as waving his knives about (user,
2026-08-02): his blades moved, he did not. About 0.4 world units is ten pixels at
a 128 cell, which reads clearly without walking a figure out of its frame. The
step is also what pays for keeping swings small, and swings have to be small --
see the next rule.

**A GROUP ROTATED ABOUT A SHARED POINT MUST STAY UNDER ABOUT 20 DEGREES.** That is
the one case where the joint rule above cannot apply: a two-handed grip has to turn
the arms, both shoulder balls and the weapon as ONE piece about the midpoint between
the shoulders, or a hand leaves the hilt. The balls then travel, at twice their
distance from that midpoint times the half-angle. On the fighter they sit 0.60 out,
so 18 degrees moves them under five pixels and reads as a shoulder rolling, and 58
took them off his body outright. The blade's reach comes from its own fist pivot
instead.

**A WEAPON WHOSE MASS SITS AT THE SHOULDER CANNOT BE SWUNG FROM THE SHOULDER.**
Turn it about the FIST instead, on its own pivot chained under the arm's, which is
what `attack_roster.Swing(parent=...)` and `animkit.chain_pivot` are for. The
paladin's warhammer is carried head-up at world z 2.14 and his shoulder is at the
same height, so an arm-only swing moves the head 0.58 units across a whole chop
and reads as a caster's gesture. Rotating the hammer about the fist gives it the
haft as a lever: the head then travels from x -0.77 behind him to x +0.41 in front
and drops 0.36. The banneret's five-unit polearm is the same case. **List the
weapon's pivot BEFORE the arm's**, or the arm pivot collects the weapon first.

**PER-PIVOT TABLES ARE WHAT A BOW NEEDS.** A draw is the string hand traveling
back while the bow hand holds still, and one shared table can only rock the whole
assembly, which swings a two-unit bow across the archer's face. Give each pivot its
own frames, and hand the arrow and the bowstring to the string hand so the nock
visibly loads and then empties. The body's step follows the entry's default table,
so an override moves a limb without teleporting the man.

**THREE FIGURES HOLDING THE SAME PROP MUST NOT RUN THE SAME TABLE.** The mender,
the battlemage and the frost adept all carry a staff in the left hand and all ran
`CAST`, so all three played the identical animation and the developer read them as
one character (user, 2026-08-02). What separates them is the PATH the staff takes,
because that is all a silhouette carries: one holds at the top of a raise, one
drives straight out off the longest step, one travels the widest arc and never
steps at all.

**A RAISE EXPRESSED AS A ROTATION LAYS A STAFF FLAT.** A vertical staff rotated
about the shoulder tips over long before it lifts, so the mender's blessing at 50
degrees put his own staff across his face. Under 30 keeps it upright. Actually
raising it needs the pivot to TRANSLATE, which the (lift, swing, lunge) table
cannot say.

**MEASURE THE WEAPON WITH `probe_rig.py`, NOT WITH EYES.** It prints a part's world
position on every frame beside the angle driving it:

```bash
blender -b --factory-startup --python tools/blender/probe_rig.py -- hero_paladin hammerhead fistL
```

Three animation rounds were rejected in one day and every diagnosis came from that
column of numbers, never from the renders. Each failure was invisible in a strip:
a fist that jumped 1.64 units on reparenting and landed below the ground line, a
hammer head sharing a coordinate with the shoulder turning it, a blade reading
+0.41 forward on the WIND-UP frame and -0.92 back on the strike. The last one is
a whole attack playing in reverse, and it survived a review by looking plausible.

**FRAMING IS CHECKED WITH `render_attacks.py --check`, NOT WITH EYES.** It reports
each sheet's smallest margin to a cell edge. A clipped blade tip on a strip of
small cells just looks like a short blade, which is how the goblin boss kept all
eight of his frames cut off at a 144 cell. Raise the entry's `cell`; never shrink
the attack to fit. A margin in low single digits means the next tweak will clip.

**ACCOUNT FOR WHERE THE WEAPON ALREADY IS.** A wind-up assumes the weapon starts
low. The paladin carries his warhammer head-UP, so `OVERHAND` spent its whole
raise laying the haft flat across his eyes and never got the head overhead;
`CHOP` gives that case a short wind back and one long drive forward. Measure it
rather than guessing: track the weapon's head per frame and read the numbers. His
hammer head sits at z 2.14 at rest and his shoulder pivot is at the same height,
which is why the head travels only 0.58 units across the whole chop -- a pendulum
pivoted at its own mass moves that mass very little, and no table of angles fixes
that. It is a rest-pose question, not an animation one.

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
