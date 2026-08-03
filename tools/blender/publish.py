"""Promote finished renders out of the scratch directory into the repository.

    python tools/blender/publish.py                 # everything with a real change
    python tools/blender/publish.py hero_paladin    # only keys containing this
    python tools/blender/publish.py --dry-run       # report, touch nothing
    python tools/blender/publish.py --init-manifest # bootstrap manifest.json once

**This is the ONLY sanctioned path from `out/` to `assets/rendered/`.** Hand
copies are what caused every cross-machine drift: they bypass the bookkeeping
that lets the other machine (and the pre-commit guard) know what a file actually
is. If this tool's report is ever wrong, fix the tool -- do not route around it.

`tools/blender/out/` is SCRATCH: debug renders, probes, upscales, rewritten
wholesale, gitignored, machine-local. `assets/rendered/` is the durable
artifact: one copy of each finished image, named by roster key, committed,
reviewable on a machine that has never installed Blender.

**Changes are detected by PIXEL HASH, not bytes** (see `hash_pngs.py`).
Blender's PNG encoding varies between runs, so byte comparison reported all 83
sprites "changed" after any render; that useless report is why publishing
degenerated into hand-copying. The pixel hash makes "changed" mean changed, so
`--dry-run` is finally a truthful answer to "what did my edits actually affect".

After copying, the canonical contact sheets are recomposed FROM the published
files (never from scratch) and `assets/rendered/manifest.json` is updated with
every hash. The pre-commit guard cross-checks that manifest, so art published any
other way fails to commit.

Filters match keys as substrings, `=key` exactly -- same convention as
`render_attacks.py`. A filtered publish still recomposes every canonical sheet;
sheets are cheap and always current.

Layout, chosen so the game can map a roster key straight to a path:

    assets/rendered/sprites/<key>.png     the 83 static sprites
    assets/rendered/attack/<key>.png      the 63 attack sheets
    assets/rendered/sheets/<group>.png    contact sheets, for reviewing
    assets/rendered/manifest.json         pixel hash + provenance of all of it
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import roster           # noqa: E402
import attack_roster    # noqa: E402
import manifest as M    # noqa: E402
from render_all import find_blender  # noqa: E402

SRC = os.path.join(HERE, "out")


def jobs(filters=None):
    """(src abspath, dest abspath) for every sprite and attack the rosters name.

    Driven by the rosters, not by globbing the scratch directory, so probe images
    and abandoned experiments can never reach the repository by accident. Sheets
    are absent on purpose: the composers write those directly from published art.
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


def run_blender(script, args=()):
    blender = find_blender()
    cmd = [blender, "--background", "--factory-startup", "--python",
           os.path.join(HERE, script)]
    if args:
        cmd += ["--"] + list(args)
    proc = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True)
    if proc.returncode != 0 or "Traceback (most recent call last)" in proc.stdout:
        print(proc.stdout[-3000:])
        raise SystemExit("blender step failed: %s" % script)
    return proc.stdout


def hash_files(paths):
    """{abspath: pixel hash} via one Blender launch. Missing files are absent."""
    if not paths:
        return {}
    fd, job = tempfile.mkstemp(suffix=".json", prefix="pxjob_")
    result = job.replace(".json", "_result.json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(sorted(paths), fh)
    try:
        run_blender("hash_pngs.py", [job, result])
        with open(result, encoding="utf-8") as fh:
            return json.load(fh)
    finally:
        for p in (job, result):
            try:
                os.remove(p)
            except OSError:
                pass


def compose_canonical():
    """Recompose every canonical sheet from published art; both update the
    manifest themselves, sequentially, so there is no concurrent write."""
    out = run_blender("compose_contact.py")
    out += run_blender("compose_attack_contact.py")
    for line in out.splitlines():
        if line.startswith(("canonical", "  rewrote", "  unchanged")):
            print("  " + line.strip())


def init_manifest():
    """Bootstrap: hash everything already published and record it as the truth.

    Sheet `inputs` are seeded with the CURRENT hashes of the files each sheet is
    supposed to display, which asserts the published sheets are consistent today.
    For the hero content that was verified by pixel audit on 2026-08-02; for the
    enemy families it rests on their sheets having been composed in the same
    session that published their strips. The first real publish re-verifies
    everything through the composers.
    """
    files = []
    for sub in ("sprites", "attack", "sheets"):
        d = os.path.join(M.RENDERED, sub)
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".png"):
                files.append(os.path.join(d, fn))
    hashes = hash_files(files)
    man = {}
    for p, px in hashes.items():
        wh = [int(v) for v in px.rsplit("|", 1)[1].split("x")]
        man[M.rel(p)] = {"px": px, "wh": wh}
    for sheet, inputs in M.sheet_inputs().items():
        if sheet not in man:
            continue
        man[sheet]["inputs"] = {i: man[i]["px"] for i in inputs if i in man}
    M.save(man)
    print("manifest seeded: %d file(s), %d sheet(s) with provenance"
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

    pairs = jobs(args.filters)
    src_hashes = hash_files([s for s, _ in pairs if os.path.exists(s)])

    new, changed, current, unrendered = [], [], [], []
    for src, dst in pairs:
        px = src_hashes.get(src)
        if px is None:
            unrendered.append(dst)
            continue
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
    if args.dry_run or not (new or changed):
        return 0

    for src, dst, px in new + changed:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        wh = [int(v) for v in px.rsplit("|", 1)[1].split("x")]
        man[M.rel(dst)] = {"px": px, "wh": wh}
    M.save(man)

    # Sheets are recomposed from what is now published, and they update the
    # manifest themselves -- after our save, so nothing is lost between writers.
    compose_canonical()
    total = sum(os.path.getsize(d) for _, d, _ in new + changed)
    print("done: %.1f MB of art published" % (total / 1024.0 / 1024.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
