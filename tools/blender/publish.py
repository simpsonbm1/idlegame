"""Promote finished renders out of the scratch directory into the repository.

    python tools/blender/publish.py                 # everything with a real change
    python tools/blender/publish.py hero_paladin    # only keys containing this
    python tools/blender/publish.py --dry-run       # report, touch nothing
    python tools/blender/publish.py --init-manifest # regenerate every hash

**This is the ONLY sanctioned path from `out/` to `assets/rendered/`.** Hand
copies are what caused every cross-machine drift: they bypass the bookkeeping
that lets the other machine (and the pre-commit guard) know what a file actually
is. If this tool's report is ever wrong, fix the tool -- do not route around it.

`tools/blender/out/` is SCRATCH: debug renders, probes, upscales, sheet
candidates, rewritten wholesale, gitignored, machine-local. `assets/rendered/`
is the durable artifact: one copy of each finished image, named by roster key,
committed, reviewable on a machine that has never installed Blender.

**Changes are detected by PIXEL HASH** (`pixhash.py` -- the one definition),
because Blender's PNG encoding varies between runs. Byte comparison reported
all 83 sprites "changed" after any render; that useless report is why
publishing degenerated into hand-copying. `--dry-run` is a truthful answer to
"what did my edits actually affect".

The division of labour with the composers: Blender turns pixels into pixels,
this tool does ALL bookkeeping. The composers read `assets/rendered/` and write
candidate sheets into `out/`; this tool hashes the candidates, copies the ones
that actually changed, and records provenance -- each sheet's entry in
`assets/rendered/manifest.json` carries the hash of every published file it
displays, which is what the pre-commit guard cross-checks.

Filters match keys as substrings, `=key` exactly -- same convention as
`render_attacks.py`. A filtered publish still refreshes every canonical sheet.

Layout, chosen so the game can map a roster key straight to a path:

    assets/rendered/sprites/<key>.png     the 83 static sprites
    assets/rendered/attack/<key>.png      the 63 attack sheets
    assets/rendered/sheets/<group>.png    contact sheets, for reviewing
    assets/rendered/manifest.json         pixel hash + provenance of all of it
"""

import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import roster           # noqa: E402
import attack_roster    # noqa: E402
import manifest as M    # noqa: E402
import pixhash          # noqa: E402
from render_all import find_blender  # noqa: E402

SRC = os.path.join(HERE, "out")


def jobs(filters=None):
    """(src abspath, dest abspath) for every sprite and attack the rosters name.

    Driven by the rosters, not by globbing the scratch directory, so probe images
    and abandoned experiments can never reach the repository by accident. Sheets
    are handled separately: their sources are candidates the composers write.
    """
    def wanted(key):
        if not filters:
            return True
        return any(f[1:] == key if f.startswith("=") else f in key
                   for f in filters)

    out = []
    for a in roster.ROSTER:
        if a.built and wanted(a.key):
            out.append((os.path.join(SRC, a.out),
                        os.path.join(M.RENDERED, "sprites", a.key + ".png")))
    atk = [a.key for a in attack_roster.ATTACKS] + ["knight", "goblin"]
    for key in atk:
        if wanted(key):
            out.append((os.path.join(SRC, "atk_%s.png" % key),
                        os.path.join(M.RENDERED, "attack", key + ".png")))
    return out


def run_blender(script):
    blender = find_blender()
    proc = subprocess.run([blender, "--background", "--factory-startup",
                           "--python", os.path.join(HERE, script)],
                          cwd=HERE, capture_output=True, text=True)
    if proc.returncode != 0 or "Traceback (most recent call last)" in proc.stdout:
        print(proc.stdout[-3000:])
        raise SystemExit("blender step failed: %s" % script)
    return proc.stdout


def entry(px):
    wh = [int(v) for v in px.rsplit("|", 1)[1].split("x")]
    return {"px": px, "wh": wh}


def publish_sheets(man, dry_run=False):
    """Compose candidates, then copy the ones whose pixels actually changed.

    Provenance comes from `manifest.sheet_inputs()` -- the same roster-derived
    mapping the composers walk -- with each input's hash read from the manifest
    entries this run just settled. Only inputs that exist are recorded, so a
    half-finished family degrades to a smaller sheet, not a lie.
    """
    if not dry_run:
        run_blender("compose_contact.py")
        run_blender("compose_attack_contact.py")
    rewrote, unchanged = [], []
    for dest_rel, inputs in sorted(M.sheet_inputs().items()):
        cand = os.path.join(SRC, "sheet_" + os.path.basename(dest_rel))
        if not os.path.exists(cand):
            continue
        px = pixhash.hash_file(cand)
        rec = entry(px)
        rec["inputs"] = {i: man[i]["px"] for i in inputs if i in man}
        changed = (man.get(dest_rel) or {}).get("px") != px
        if changed and not dry_run:
            dest = os.path.join(M.RENDERED, dest_rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(cand, dest)
        (rewrote if changed else unchanged).append(dest_rel)
        man[dest_rel] = rec
    print("  sheets rewrote: %s" % (", ".join(rewrote) or "none"))
    print("  sheets unchanged: %d" % len(unchanged))


def init_manifest():
    """Regenerate every hash from the published files themselves.

    Run this in the SAME commit as any change to the hash definition in
    `pixhash.py`, so no two definitions ever coexist in one manifest. Sheet
    `inputs` are seeded from current published hashes, which asserts the sheets
    are consistent as of this run; the next real publish re-verifies through
    the composers.
    """
    man = {}
    for sub in ("sprites", "attack", "sheets"):
        d = os.path.join(M.RENDERED, sub)
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".png"):
                p = os.path.join(d, fn)
                man[M.rel(p)] = entry(pixhash.hash_file(p))
    for sheet, inputs in M.sheet_inputs().items():
        if sheet in man:
            man[sheet]["inputs"] = {i: man[i]["px"] for i in inputs if i in man}
    M.save(man)
    print("manifest regenerated: %d file(s), %d sheet(s) with provenance"
          % (len(man), sum(1 for v in man.values() if "inputs" in v)))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("filters", nargs="*", help="only keys containing these strings")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--init-manifest", action="store_true")
    args = ap.parse_args()

    if args.init_manifest:
        return init_manifest()

    man = M.load()
    if not man:
        print("no manifest.json -- run publish.py --init-manifest once first")
        return 1

    new, changed, current, unrendered = [], [], [], []
    for src, dst in jobs(args.filters):
        if not os.path.exists(src):
            unrendered.append(dst)
            continue
        px = pixhash.hash_file(src)
        have = (man.get(M.rel(dst)) or {}).get("px")
        if have is None and not os.path.exists(dst):
            new.append((src, dst, px))
        elif have != px:
            changed.append((src, dst, px))
        else:
            current.append(dst)

    verb = "would publish" if args.dry_run else "publishing"
    print("%s %d new, %d changed; %d already current, %d not rendered here"
          % (verb, len(new), len(changed), len(current), len(unrendered)))
    for src, dst, _ in new + changed:
        print("  %s" % M.rel(dst))
    if args.dry_run:
        return 0

    for src, dst, px in new + changed:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        man[M.rel(dst)] = entry(px)
    if new or changed:
        M.save(man)

    publish_sheets(man)
    M.save(man)
    total = sum(os.path.getsize(d) for _, d, _ in new + changed)
    print("done: %.1f MB of art published" % (total / 1024.0 / 1024.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
