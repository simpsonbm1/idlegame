"""Render one attack sheet per combatant, headless and unattended.

    python tools/blender/render_attacks.py            # every entry
    python tools/blender/render_attacks.py orc goblin # keys containing these
    python tools/blender/render_attacks.py --list
    python tools/blender/render_attacks.py --check    # framing, renders nothing

Same shape as `render_all.py` and for the same reason: one Blender process per
sheet, so no state can leak between them. Reads `attack_roster.py`.

Exit code is the number of failures, or of clipped sheets under `--check`.

**`--check` is how framing gets verified, because eyes cannot do it.** A swing
that leaves its cell is cut off at the boundary, and on a strip of eight small
cells a clipped blade tip looks like a short blade. It reports each sheet's
smallest margin to any edge; anything at or below zero is losing pixels, and a
margin in low single digits means the next tweak will. Raising an entry's `cell`
is the fix, never shrinking the attack.
"""

import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from render_all import find_blender  # noqa: E402

RUNNER = os.path.join(HERE, "_run_attack.py")

RUNNER_SRC = '''"""Written by render_attacks.py. Renders ONE attack sheet, named by ATTACK_KEY."""
import os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import pixelrig as P
import animkit as A
import attack_roster as R
importlib.reload(P)
importlib.reload(A)
importlib.reload(R)

key = os.environ["ATTACK_KEY"]
spec = [a for a in R.ATTACKS if a.key == key][0]
mod = importlib.import_module(spec.module)
importlib.reload(mod)

scn = P.get_scene()
# The attack key IS the figure key, tier suffix and all. A rarity variant names
# its root "hero_fighter_rare_root", so deriving the root from the MODULE name
# instead finds nothing -- which is what it did.
root = A.figure_root(scn, key)

# An entry carrying an `ik` spec drives the WEAPON and solves the arms to reach
# it, which is the only technique that can raise a grip or extend an arm. Pivots
# are ignored entirely for those; the two cannot be mixed on one figure.
if spec.ik:
    A.twohand_sheet(scn, key, root, spec.ik.weapon, spec.ik.arms, spec.frames,
                    res=spec.cell, mid=spec.ik.mid, stretch=spec.ik.stretch,
                    out_name="atk_" + key)
else:
    # Each pivot gets a UNIQUE name: `P.find` matches on the name before Blender's
    # `.001` suffix, so two empties called "atk_pivot" read as one name to it.
    made = [A.pivot_arm(scn, root, g.joint, g.parts, g.weapon, name="atk_pivot_%d" % i)
            for i, g in enumerate(spec.groups)]
    # Chaining runs AFTER every pivot has taken its parts, so a parent cannot
    # collect a child's weapon on the way past.
    for g, p in zip(spec.groups, made):
        if g.parent is not None:
            A.chain_pivot(p, made[g.parent])
    tracks = [(p, g.frames) for g, p in zip(spec.groups, made)]
    A.swing_sheet(scn, key, root, tracks, spec.frames, res=spec.cell,
                  out_name="atk_" + key)
'''


CHECK_SRC = '''"""Written by render_attacks.py --check. Reports each sheet's edge margin."""
import os, sys
import numpy as np
import bpy
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.append(HERE)
import attack_roster as R

keys = set(os.environ["CHECK_KEYS"].split(","))
worst = 10 ** 9
for a in R.ATTACKS:
    if a.key not in keys:
        continue
    p = os.path.join(HERE, "out", "atk_%s.png" % a.key)
    if not os.path.exists(p):
        print("%-30s NOT RENDERED" % a.key)
        continue
    img = bpy.data.images.load(p, check_existing=False)
    w, h = img.size
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    alpha = buf.reshape(h, w, 4)[:, :, 3]
    bpy.data.images.remove(img)
    margin, clipped = 10 ** 9, []
    for i in range(w // a.cell):
        sub = alpha[:, i * a.cell:(i + 1) * a.cell]
        cols = np.where(sub.max(axis=0) > 0)[0]
        rows = np.where(sub.max(axis=1) > 0)[0]
        if not len(cols):
            continue
        # Blender buffers are bottom-up, so the LAST row is the top of the cell.
        m = min(cols.min(), a.cell - 1 - cols.max(), h - 1 - rows.max())
        margin = min(margin, m)
        if m <= 0:
            clipped.append(i)
    worst = min(worst, margin)
    print("%-30s cell %3d  margin %3d px%s"
          % (a.key, a.cell, margin,
             "  CLIPPED frames " + str(clipped) if clipped else ""))
print("WORST %d" % worst)
'''


def run_check(wanted):
    blender = find_blender()
    path = os.path.join(HERE, "_check_attack.py")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(CHECK_SRC)
    env = dict(os.environ)
    env["CHECK_KEYS"] = ",".join(a.key for a in wanted)
    proc = subprocess.run([blender, "--background", "--factory-startup",
                           "--python", path],
                          cwd=HERE, env=env, capture_output=True, text=True)
    lines = [l for l in proc.stdout.splitlines()
             if " margin " in l or "NOT RENDERED" in l or l.startswith("WORST")]
    print("\n".join(lines) or proc.stdout[-2000:])
    try:
        os.remove(path)
    except OSError:
        pass
    return sum(1 for l in lines if "CLIPPED" in l)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("filters", nargs="*", help="only keys containing these strings")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="report each rendered sheet's margin to the cell edge")
    args = ap.parse_args()

    import attack_roster as R
    wanted = [a for a in R.ATTACKS
              if not args.filters or any(f in a.key for f in args.filters)]

    if args.list:
        for a in wanted:
            print("%-34s %-28s %d frames, %d cell"
                  % (a.key, a.module, len(a.frames), a.cell))
        print("\n%d attack sheet(s)" % len(wanted))
        return 0

    if args.check:
        return run_check(wanted)

    blender = find_blender()
    with open(RUNNER, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(RUNNER_SRC)

    log_dir = os.path.join(HERE, "out", "logs")
    os.makedirs(log_dir, exist_ok=True)
    print("rendering %d attack sheet(s)\n" % len(wanted))

    failed, t0 = [], time.time()
    for i, a in enumerate(wanted, 1):
        sys.stdout.write("[%2d/%d] %-34s " % (i, len(wanted), a.key))
        sys.stdout.flush()
        env = dict(os.environ)
        env.update(a.env)
        env["ATTACK_KEY"] = a.key
        log_path = os.path.join(log_dir, "atk_" + a.key + ".log")
        t1 = time.time()
        with open(log_path, "w", encoding="utf-8", errors="replace") as log:
            proc = subprocess.run([blender, "--background", "--factory-startup",
                                   "--python", RUNNER],
                                  stdout=log, stderr=subprocess.STDOUT, cwd=HERE, env=env)
        produced = os.path.join(HERE, "out", "atk_%s.png" % a.key)
        ok = proc.returncode == 0 and os.path.exists(produced)
        if ok:
            with open(log_path, encoding="utf-8", errors="replace") as f:
                if "Traceback (most recent call last)" in f.read():
                    ok = False
        print("%s  %5.1fs" % ("ok  " if ok else "FAIL", time.time() - t1))
        if not ok:
            failed.append((a, log_path))

    # Contact sheets at the end of every run, exactly as `render_all.py` does.
    # They are ARTIFACTS, not scratch (user ruling 2026-08-02), so leaving them to
    # a separate manual step is what let them go stale and out of the repository.
    if not failed:
        sheet_script = os.path.join(HERE, "compose_attack_contact.py")
        subprocess.run([blender, "--background", "--factory-startup",
                        "--python", sheet_script],
                       cwd=HERE, capture_output=True, text=True)
        print("contact sheets: %s" % os.path.join(HERE, "out", "sheet_attacks_*.png"))

    print("\n%d ok, %d failed, %.1fs total"
          % (len(wanted) - len(failed), len(failed), time.time() - t0))
    for a, log_path in failed:
        print("  FAILED %s -- %s" % (a.key, log_path))
    try:
        os.remove(RUNNER)
    except OSError:
        pass
    return len(failed)


if __name__ == "__main__":
    sys.exit(main())
