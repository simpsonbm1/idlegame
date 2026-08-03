"""The pixel-hash manifest of `assets/rendered/`: what each artifact actually IS.

`assets/rendered/manifest.json` maps each published file (path relative to
`assets/rendered/`, forward slashes) to the hash of its PIXELS:

    "sprites/hero_fighter.png": {"px": "<sha256 hex>", "wh": [112, 112]}
    "sheets/heroes.png":        {"px": "...", "wh": [...], "inputs":
                                    {"sprites/hero_fighter.png": "<px it was
                                     composed from>", ...}}

**Why pixels and not bytes.** Blender's PNG encoding varies between runs, so two
renders of identical art are never byte-identical and byte comparison calls all
83 sprites "changed" after any render -- which is why `publish.py`'s old report
was useless and publishing became hand-copying, and hand-copying is where every
cross-machine drift entered. The pixel hash is stable across encodings, so
"changed" finally means changed.

**Why `inputs` on sheets.** A contact sheet is a claim about other files: "these
are the sprites in the repository". On 2026-08-02 that claim was false in a
commit -- sheets composed from a stale scratch directory showed four banneret
sprites and twenty hero attack sheets the repository did not have. The composer
now records the pixel hash of every file it consumed, and the pre-commit guard
verifies `inputs` against the manifest's own entries as a pure text comparison.
A sheet whose inputs no longer match is stale by definition, with no image
decoding at commit time.

Kept free of `bpy` so the system Python (publish.py, audit_artifacts.py) can use
it. Hashing itself needs pixel access and lives in `hash_pngs.py`, which runs
inside Blender.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
RENDERED = os.path.join(REPO, "assets", "rendered")
PATH = os.path.join(RENDERED, "manifest.json")


def load(path=PATH):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save(data, path=PATH):
    """Sorted keys and a trailing newline, so diffs are stable and reviewable."""
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=1, sort_keys=True)
        fh.write("\n")


def rel(abspath):
    """Manifest key for an absolute path under assets/rendered/."""
    r = os.path.relpath(abspath, RENDERED)
    return r.replace("\\", "/")


def sheet_inputs():
    """Which published files each canonical contact sheet is composed from.

    Derived from the rosters, exactly as the composers derive their own work
    lists, so the guard and the composers cannot disagree about what a sheet
    shows. Returns {sheet rel: [input rel, ...]}.
    """
    import roster
    import attack_roster

    out = {}

    def sprite_rel(a):
        return "sprites/%s.png" % a.key

    for g in roster.GROUPS:
        if g == "variants":
            assets = roster.variant_rows()
        else:
            assets = roster.by_group(g)
        ins = []
        for item in assets:
            a = item[0] if isinstance(item, tuple) else item
            if a.built:
                ins.append(sprite_rel(a))
        out["sheets/%s.png" % g] = ins

    out["sheets/all_characters.png"] = [
        sprite_rel(a) for a in roster.ROSTER
        if a.group != "buildings" and a.built]

    for g, filters in attack_roster.SHEET_GROUPS:
        ins = []
        for a in attack_roster.ATTACKS:
            hit = any(f[1:] == a.key if f.startswith("=") else f in a.key
                      for f in filters)
            if hit:
                ins.append("attack/%s.png" % a.key)
        out["sheets/attacks_%s.png" % g] = ins

    return out
