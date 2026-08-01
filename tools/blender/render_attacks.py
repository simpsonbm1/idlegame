"""Render one attack sheet per combatant, headless and unattended.

    python tools/blender/render_attacks.py            # every entry
    python tools/blender/render_attacks.py orc goblin # keys containing these
    python tools/blender/render_attacks.py --list

Same shape as `render_all.py` and for the same reason: one Blender process per
sheet, so no state can leak between them. Reads `attack_roster.py`.

Exit code is the number of failures.
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
pivots = [A.pivot_arm(scn, root, sh, parts, weapon) for sh, parts, weapon in spec.groups]
A.swing_sheet(scn, key, root, pivots, spec.frames, res=spec.cell,
              out_name="atk_" + key)
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("filters", nargs="*", help="only keys containing these strings")
    ap.add_argument("--list", action="store_true")
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
