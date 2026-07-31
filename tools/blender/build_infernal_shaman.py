"""Infernal Siege shaman -- M15_ASSET_SPECS.md entry 43.

  "a blood acolyte in deep crimson hooded vestments, pale horns curling from the
   hood, holding up a chalice glowing with sinister red light"

The horns coming THROUGH the hood are the entry. A hood is a shape the roster
already uses three times, so this one has to be broken by something, and pale
horns pushing out of dark crimson cloth do it in a way no palette change could.

His chalice glows RED where every other infernal light is ember-orange. One
figure in the family carrying a different heat is what stops the six of them
reading as a single orange wash in a formation, which is the same reason the
undead grave digger's lantern is green among five teals.
"""

import bpy, math, os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import infernal_kit as I
import spritekit as S
import pixelrig as P
importlib.reload(P)
importlib.reload(S)
importlib.reload(I)

scn = P.get_scene()
px = I.start(scn, res=112)
M = I.palette()

figure, detail, noline = [], [], []

# ---- deep crimson vestments to the ground ----
figure.append(P.add_cone(scn, "ivest", (0, 0, 0.84), 0.82, 0.40, 1.68, M["crim"], verts=12))
figure.append(P.add_cyl(scn, "ihem", (0, 0, 0.06), 0.85, 0.10, M["brass"], verts=12))
detail += S.tatters(scn, (0, -0.42, 0.12), 1.22, M["robe"], count=6, drop=0.26, seed=7)
figure.append(P.add_cone(scn, "ichest", (0, 0, 2.02), 0.43, 0.36, 0.88, M["crim"], verts=12))
detail.append(P.add_box(scn, "iplacket", (0, -0.40, 2.00), (0.11, 0.07, 0.66), M["brass"]))
figure.append(P.add_box(scn, "isash", (0, -0.40, 1.62), (0.58, 0.09, 0.13), M["iron"]))

# ---- shoulder mantle and the hood ----
figure.append(P.add_cone(scn, "imantle", (0, -0.02, 2.48), 0.68, 0.28, 0.44, M["robe"], verts=12))
for s in (-1, 1):
    figure.append(P.add_sphere(scn, "ishoulder", (s * 0.48, -0.04, 2.38), 0.23, M["crim"],
                               scale=(1, .95, .8)))
figure.append(P.add_cone(scn, "ihood", (0, 0.02, 2.88), 0.44, 0.14, 0.58, M["robe"], verts=10))
# the face inside is shadow with two lights in it, not a modelled head
detail.append(P.add_box(scn, "ifacedark", (0, -0.24, 2.80), (0.30, 0.10, 0.26), M["dark"]))
noline += [P.add_box(scn, "ieye", (s * 0.09, -0.29, 2.84), (0.08, 0.05, 0.07), M["ember_h"])
           for s in (-1, 1)]

# ---- pale horns pushing OUT THROUGH the hood, which is the entry's whole read ----
figure += I.horns(scn, M, (0, 0.0, 2.96), r=0.30, curl=3, sweep=40, length=0.28, mat=M["bone"])

# ---- one hand raising the chalice, one down holding the vestment closed ----
figure += I.clawed_limb(scn, M, (-0.48, -0.12, 2.30), (-0.66, -0.56, 1.78),
                        upper_r=0.12, fore_r=0.105)
figure += I.clawed_limb(scn, M, (0.48, -0.12, 2.32), (0.66, -0.60, 2.34),
                        upper_r=0.12, fore_r=0.105)

# ---- the chalice, glowing red rather than ember-orange ----
ch_root = P.make_root(scn, "chalice_root", rot=(0, 8, 0), loc=(0.70, -0.66, 2.52))
chalice = [P.add_cone(scn, "ibowl", (0, 0, 0.14), 0.09, 0.20, 0.26, M["brass"], verts=10),
           P.add_cyl(scn, "istem", (0, 0, -0.06), 0.045, 0.16, M["brass"], verts=6),
           P.add_cyl(scn, "ifoot", (0, 0, -0.16), 0.12, 0.06, M["brass"], verts=10)]
glow = [P.add_cyl(scn, "iblood", (0, 0, 0.25), 0.175, 0.05, M["blood"], verts=10),
        P.add_sphere(scn, "ibloodhalo", (0, -0.02, 0.38), 0.10, M["blood"], segs=8, rings=5),
        P.add_sphere(scn, "ibloodwisp", (0.03, -0.02, 0.54), 0.06, M["ember_d"], segs=8, rings=5)]
P.parent_all(ch_root, chalice + glow)

I.finish(scn, px, "infernal_shaman", figure, detail, noline, roots=[ch_root],
         skip_extra=tuple(o.name for o in glow), role="shaman")
