"""Batch-render the whole roster with no Blender window and nobody watching.

    python tools/blender/render_all.py                 # everything with a builder
    python tools/blender/render_all.py undead goblin   # only those groups
    python tools/blender/render_all.py --list          # what is built, what is not

Runs under the SYSTEM Python, not Blender's. It launches Blender itself, once per
asset.

**One process per asset, deliberately.** Sharing a session lets state leak between
builds, and that is not hypothetical: the necromancer on disk was rendered at a
KeySun energy of 3.0 while the knight and goblin beside it were rendered at 2.6,
because the value drifted during a long interactive session and nothing reset it.
The figures are therefore lit 15% apart in a set whose whole premise is a shared
rig. A fresh process per asset makes that class of drift impossible, and costs
about two seconds of startup per sprite.

Exit code is the number of assets that failed, so a scheduled run can be checked
without reading the log.
"""

import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import roster  # noqa: E402

BLENDER_CANDIDATES = [
    os.environ.get("BLENDER_EXE"),
    r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
    "/usr/bin/blender",
    "/Applications/Blender.app/Contents/MacOS/Blender",
]


def find_blender():
    for c in BLENDER_CANDIDATES:
        if c and os.path.exists(c):
            return c
    # last resort: whatever is on PATH
    from shutil import which
    exe = which("blender")
    if exe:
        return exe
    raise SystemExit(
        "Blender not found. Set BLENDER_EXE to the executable, e.g.\n"
        r'  $env:BLENDER_EXE = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"')


def render_one(blender, asset, log_dir):
    """Run one builder in its own headless Blender. Returns (ok, seconds, log_path)."""
    script = os.path.join(HERE, asset.module + ".py")
    log_path = os.path.join(log_dir, asset.key + ".log")
    t0 = time.time()
    env = dict(os.environ)
    env.update(asset.env)
    with open(log_path, "w", encoding="utf-8", errors="replace") as log:
        proc = subprocess.run(
            [blender, "--background", "--factory-startup", "--python", script],
            stdout=log, stderr=subprocess.STDOUT, cwd=HERE, env=env)
    dt = time.time() - t0
    produced = os.path.join(HERE, "out", asset.out)
    # Blender exits 0 even when the script raised, so the render itself is the test.
    ok = proc.returncode == 0 and os.path.exists(produced)
    if ok:
        # a builder that failed after an earlier successful run would leave a stale
        # file behind and look like a pass, so require the traceback to be absent too
        with open(log_path, encoding="utf-8", errors="replace") as f:
            if "Traceback (most recent call last)" in f.read():
                ok = False
    return ok, dt, log_path


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("groups", nargs="*", help="only these groups (default: all)")
    ap.add_argument("--list", action="store_true", help="show roster status and exit")
    args = ap.parse_args()

    if args.list:
        for g in roster.GROUPS:
            assets = roster.by_group(g)
            done = [a for a in assets if a.built]
            print("%-10s %2d/%2d  %s" % (
                g, len(done), len(assets),
                " ".join(a.key if a.built else "(%s)" % a.key for a in assets)))
        print("\ntotal: %d built, %d to go" % (len(roster.built()), len(roster.todo())))
        return 0

    blender = find_blender()
    wanted = args.groups or roster.GROUPS
    unknown = [g for g in wanted if g not in roster.GROUPS]
    if unknown:
        raise SystemExit("unknown group(s): %s\nknown: %s"
                         % (", ".join(unknown), ", ".join(roster.GROUPS)))

    assets = [a for a in roster.ROSTER if a.group in wanted and a.built]
    if not assets:
        print("nothing to render for: %s" % ", ".join(wanted))
        return 0

    log_dir = os.path.join(HERE, "out", "logs")
    os.makedirs(log_dir, exist_ok=True)

    print("blender: %s" % blender)
    print("rendering %d asset(s)\n" % len(assets))
    failed = []
    t0 = time.time()
    for i, a in enumerate(assets, 1):
        sys.stdout.write("[%2d/%d] %-22s " % (i, len(assets), a.key))
        sys.stdout.flush()
        ok, dt, log_path = render_one(blender, a, log_dir)
        print("%s  %5.1fs" % ("ok  " if ok else "FAIL", dt))
        if not ok:
            failed.append((a, log_path))

    print("\n%d ok, %d failed, %.1fs total" % (len(assets) - len(failed),
                                               len(failed), time.time() - t0))
    for a, log_path in failed:
        print("  FAILED %s -- %s" % (a.key, log_path))

    # Contact sheets last, so an unattended run ends with the one image a human
    # actually has to look at. A failure here must not mask a successful batch.
    contact = os.path.join(HERE, "compose_contact.py")
    sheets = subprocess.run([blender, "--background", "--factory-startup",
                             "--python", contact],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            cwd=HERE, text=True, errors="replace")
    if sheets.returncode == 0 and "contact sheets written" in sheets.stdout:
        print("\ncontact sheets: %s" % os.path.join(HERE, "out", "sheet_*_big.png"))
    else:
        print("\ncontact sheets FAILED (renders above are unaffected)")
        print(sheets.stdout[-1500:])

    return len(failed)


if __name__ == "__main__":
    sys.exit(main())
