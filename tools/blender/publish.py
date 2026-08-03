"""Promote finished renders out of the scratch directory into the repository.

    python tools/blender/publish.py            # copy everything the roster names
    python tools/blender/publish.py --dry-run  # say what would change, copy nothing

`tools/blender/out/` is a SCRATCH directory. It holds debug renders, probe
images, eight-times upscales and every intermediate a render pass leaves behind,
it is rewritten wholesale on every run, and it is gitignored. Nothing in it is
durable.

`assets/rendered/` is the durable artifact. It holds one copy of each finished
image, named by its roster key rather than by the pipeline's `out_` convention,
and it is committed. A machine that has never installed Blender can review the
whole roster from it, and the game loads its sprites from it.

**Publishing is a DELIBERATE step, not part of rendering.** That separation is
the only thing keeping the repository small. A full render pass rewrites all 350
files in the scratch directory, and PNGs do not delta-compress, so git would
store every version whole -- four full passes in one evening would have added
about 76 MB of permanent history. Publishing happens when art is approved, so the
committed history gets one version per decision instead of one per render.

Layout, chosen so the game can map a roster key straight to a path:

    assets/rendered/sprites/<key>.png     the 83 static sprites
    assets/rendered/attack/<key>.png      the 61 attack sheets
    assets/rendered/sheets/<group>.png    contact sheets, for reviewing

Three directories means three glob lines in `assets/CREDITS.md`, which is what
the pre-commit credits guard wants.
"""

import argparse
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import roster  # noqa: E402
import attack_roster  # noqa: E402

SRC = os.path.join(HERE, "out")
DEST = os.path.join(REPO, "assets", "rendered")


def jobs():
    """(source path, destination path) for everything the rosters name.

    Driven by the rosters, not by globbing the scratch directory, so probe images
    and abandoned experiments can never reach the repository by accident.
    """
    out = []
    for a in roster.ROSTER:
        if a.built:
            out.append((os.path.join(SRC, a.out),
                        os.path.join(DEST, "sprites", a.key + ".png")))
    for a in attack_roster.ATTACKS:
        out.append((os.path.join(SRC, "atk_%s.png" % a.key),
                    os.path.join(DEST, "attack", a.key + ".png")))
    # the two worked examples live in build_attack.py rather than the roster
    for key in ("knight", "goblin"):
        out.append((os.path.join(SRC, "atk_%s.png" % key),
                    os.path.join(DEST, "attack", key + ".png")))
    # contact sheets: the upscaled ones, since those are what a human looks at
    for g in roster.GROUPS + ["all_characters"]:
        out.append((os.path.join(SRC, "sheet_%s_big.png" % g),
                    os.path.join(DEST, "sheets", g + ".png")))
    # **Attack contact sheets are ARTIFACTS, not scratch** (user ruling
    # 2026-08-02: "if it requires re-rendering then it isn't a durable artifact
    # and I do not consider it an asset"). They lived only in `out/` for a while,
    # which meant reviewing an animation on a second machine began with a render.
    for g, _ in attack_roster.SHEET_GROUPS:
        out.append((os.path.join(SRC, "sheet_attacks_%s.png" % g),
                    os.path.join(DEST, "sheets", "attacks_" + g + ".png")))
    return out


def same(a, b):
    if not os.path.exists(b):
        return False
    if os.path.getsize(a) != os.path.getsize(b):
        return False
    with open(a, "rb") as fa, open(b, "rb") as fb:
        return fa.read() == fb.read()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    new, changed, unchanged, missing = [], [], [], []
    for src, dst in jobs():
        if not os.path.exists(src):
            missing.append(src)
            continue
        if not os.path.exists(dst):
            new.append((src, dst))
        elif not same(src, dst):
            changed.append((src, dst))
        else:
            unchanged.append(dst)

    for src, dst in new + changed:
        if not args.dry_run:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    verb = "would copy" if args.dry_run else "copied"
    print("%s %d new, %s %d changed, %d already current"
          % (verb, len(new), verb, len(changed), len(unchanged)))
    for src in missing:
        print("  MISSING %s -- render it first" % os.path.basename(src))
    if not args.dry_run and (new or changed):
        total = sum(os.path.getsize(d) for _, d in new + changed)
        print("  %.1f MB written to assets/rendered/" % (total / 1024.0 / 1024.0))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
