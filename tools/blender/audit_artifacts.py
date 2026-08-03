"""Pre-commit guard: published art must be bookkept, and its sheets current.

Reads staged repo paths on stdin (one per line) and exits non-zero on a
violation. Called by `.githooks/pre-commit`; run it by hand the same way:

    git diff --cached --name-only | python tools/blender/audit_artifacts.py

**Why this is mechanised.** The standing invariant is that every change must
survive the trip between machines, and the art pipeline kept breaking it in one
specific way: what a contact sheet SHOWED and what the repository CARRIED came
apart, so the other machine reviewed art that did not exist. Prose told sessions
to keep them together; prose does not execute. It happened with unpublished
sheets twice in one day, and then a third way on 2026-08-02: sheets composed
from a stale scratch directory were committed showing four banneret sprites and
twenty hero attack sheets the repository did not have.

Three layers of defence:

1. **Staged-set completeness** (the original guard): publishing a sprite obliges
   the sheets that display it, in the same commit.
2. **Manifest consistency**: `assets/rendered/manifest.json` records the pixel
   hash of every published file and, for each sheet, the hashes of the files it
   was composed FROM (written by `publish.py`, the only sanctioned path). The
   guard requires the manifest to travel with any art change and requires every
   sheet's recorded inputs to match the manifest's own current entries. A sheet
   whose inputs disagree is stale BY THE PIPELINE'S OWN RECORDS.
3. **Staged pixels match the manifest.** Every staged PNG under
   `assets/rendered/` is decoded FROM ITS STAGED BLOB (`git show :path`) and
   its pixel hash must equal its manifest entry. This is what catches the
   hand copy that layer 2 cannot: a PNG smuggled in around `publish.py` hashes
   differently from what the manifest records, whatever its bytes look like.
   Pixels, not bytes, because Blender's PNG encoding varies between runs.

Layer 3 needs Pillow under the hook's interpreter and FAILS CLOSED without it,
printing the install command -- the accepted desktop-bootstrap speed bump
(user-approved install, 2026-08-02). It never degrades to the text-only check.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import roster            # noqa: E402
import attack_roster     # noqa: E402

SPRITES = "assets/rendered/sprites/"
ATTACK = "assets/rendered/attack/"
SHEETS = "assets/rendered/sheets/"
MANIFEST = "assets/rendered/manifest.json"


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


def staged_manifest():
    """The manifest as STAGED, which is what the commit will actually carry.

    `AUDIT_MANIFEST_FILE` overrides the source for tests, so the guard's failure
    paths can be exercised against synthesized manifests without touching git.
    """
    override = os.environ.get("AUDIT_MANIFEST_FILE")
    if override:
        with open(override, encoding="utf-8") as fh:
            return json.load(fh)
    proc = subprocess.run(["git", "show", ":" + MANIFEST],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return json.loads(proc.stdout)


def staged_blob(path):
    proc = subprocess.run(["git", "show", ":" + path], capture_output=True)
    return proc.stdout if proc.returncode == 0 else None


def check_manifest(staged_set, fail):
    art = [p for p in staged_set
           if p.startswith("assets/rendered/") and p.endswith(".png")]
    if not art:
        return

    if MANIFEST not in staged_set:
        fail("art is staged but %s is not." % MANIFEST)
        fail("  Publish through the pipeline, which maintains it:")
        fail("    python tools/blender/publish.py")
        return

    man = staged_manifest()
    if man is None:
        fail("cannot read the staged %s." % MANIFEST)
        return

    # Fail CLOSED if the pixel check cannot run: a guard that silently skips its
    # strongest layer is how a bootstrap gap becomes a drift. `pixhash` raises
    # with the install command when Pillow is absent; that message IS the
    # refusal text.
    try:
        import pixhash
    except ImportError as e:
        fail(str(e))
        return

    for p in sorted(art):
        rel = p[len("assets/rendered/"):]
        if rel not in man:
            fail("%s is staged with no manifest entry." % p)
            fail("  Only publish.py writes art here; hand copies are the drift.")
            continue
        blob = staged_blob(p)
        if blob is None:
            fail("cannot read the staged blob of %s." % p)
            continue
        px = pixhash.hash_bytes(blob)
        if px != man[rel].get("px"):
            fail("%s: staged pixels do not match the manifest." % p)
            fail("  This file did not come through publish.py. Re-run:"
                 " python tools/blender/publish.py")

    # Every sheet's recorded inputs must match the manifest's current entries.
    # Checked globally, not only for staged sheets: a staged sprite with an
    # unstaged-but-stale sheet is exactly the ordering hazard this exists for.
    for sheet, entry in sorted(man.items()):
        for src, px in sorted((entry.get("inputs") or {}).items()):
            cur = (man.get(src) or {}).get("px")
            if cur != px:
                fail("%s%s was composed from a different %s than the manifest"
                     " now records." % ("assets/rendered/", sheet, src))
                fail("  The sheet is stale by the pipeline's own bookkeeping."
                     " Re-run: python tools/blender/publish.py")


def main():
    staged = [l.strip().replace("\\", "/") for l in sys.stdin if l.strip()]
    staged_set = set(staged)

    failures = []

    def fail(msg):
        failures.append(msg)

    need = sheets_for(staged)
    missing = {s: v for s, v in need.items() if s not in staged_set}
    for sheet in sorted(missing):
        why = sorted(missing[sheet])
        fail("published art without its contact sheet: %s (needed by %s%s)"
             % (sheet, os.path.basename(why[0]),
                " and %d more" % (len(why) - 1) if len(why) > 1 else ""))
        fail("  A sheet that still shows the old art is what the other machine"
             " reviews. Re-run: python tools/blender/publish.py")

    check_manifest(staged_set, fail)

    if not failures:
        return 0
    print("pre-commit: art-consistency guard failed.", file=sys.stderr)
    for msg in failures:
        print("    " + msg, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
