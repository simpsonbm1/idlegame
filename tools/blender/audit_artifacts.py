"""Pre-commit guard: a published sprite must bring its contact sheet with it.

Reads staged repo paths on stdin (one per line) and exits non-zero if a commit
publishes art without the review sheets that show it. Called by
`.githooks/pre-commit`; run it by hand the same way:

    git diff --cached --name-only | python tools/blender/audit_artifacts.py

**Why this is mechanised.** The standing invariant is that every change must
survive the trip between machines, and the art pipeline kept breaking it in one
specific way: a sprite got published while the contact sheet showing that sprite
did not, so the other machine reviewed art that no longer existed. It happened
twice in one day. The paladin's and banneret's grips were rebuilt and published
while `sheets/heroes.png`, `sheets/variants.png` and `sheets/all_characters.png`
still showed the old ones; separately, 61 attack sheets were published with no
`attacks_*` sheet in the repository at all, so reviewing an animation on a second
machine began with installing Blender and rendering the whole roster (user ruling
2026-08-02: "if it requires re-rendering then it isn't a durable artifact and I do
not consider it an asset").

**It tests the STAGED SET, not file contents.** Blender's PNG encoding varies
between runs, so neither bytes nor timestamps distinguish a genuinely stale sheet
from re-render noise -- every sprite reads as "changed" after any render pass, and
a content check would fire on all 83 every time. Whether a path is in this commit
is exact and has no noise in it.

The rule has close to no false positives, because there is no reason to publish a
sprite and deliberately leave the sheet that displays it out of date.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import roster            # noqa: E402
import attack_roster     # noqa: E402

SPRITES = "assets/rendered/sprites/"
ATTACK = "assets/rendered/attack/"
SHEETS = "assets/rendered/sheets/"


def sheets_for(staged):
    """Contact sheets this commit's published art obliges it to refresh."""
    need = {}

    sprite_group = {a.key: a.group for a in roster.ROSTER}
    for path in staged:
        if not path.startswith(SPRITES):
            continue
        key = os.path.basename(path)[:-4]
        group = sprite_group.get(key)
        if not group:
            continue
        # A hero appears on his own group sheet, on the rarity-variants sheet and
        # on the everything sheet, so publishing one obliges all three.
        for g in (group, "all_characters"):
            need.setdefault(SHEETS + g + ".png", set()).add(path)
        if group == "heroes":
            need.setdefault(SHEETS + "variants.png", set()).add(path)

    attack_group = {}
    for g, filters in attack_roster.SHEET_GROUPS:
        for a in attack_roster.ATTACKS:
            hit = any(f[1:] == a.key if f.startswith("=") else f in a.key
                      for f in filters)
            if hit:
                attack_group.setdefault(a.key, []).append(g)
    for path in staged:
        if not path.startswith(ATTACK):
            continue
        key = os.path.basename(path)[:-4]
        for g in attack_group.get(key, []):
            need.setdefault(SHEETS + "attacks_" + g + ".png", set()).add(path)
    return need


def main():
    staged = [l.strip().replace("\\", "/") for l in sys.stdin if l.strip()]
    staged_set = set(staged)
    need = sheets_for(staged)

    missing = {s: v for s, v in need.items() if s not in staged_set}
    if not missing:
        return 0

    print("pre-commit: published art without its contact sheet.", file=sys.stderr)
    print("  A sheet that still shows the old art is what the other machine"
          " reviews.", file=sys.stderr)
    for sheet in sorted(missing):
        why = sorted(missing[sheet])
        print("    %s  (needed by %s%s)"
              % (sheet, os.path.basename(why[0]),
                 " and %d more" % (len(why) - 1) if len(why) > 1 else ""),
              file=sys.stderr)
    print("  Rebuild and copy them in, then stage them in THIS commit:",
          file=sys.stderr)
    print("    python tools/blender/render_all.py     # writes the sprite sheets",
          file=sys.stderr)
    print("    python tools/blender/render_attacks.py # writes the attack sheets",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
