"""Re-render one hero's four rarity tiers and build that line's contact sheet.

    python tools/blender/render_line.py hero_fighter

The developer reviews the rarity rework a line at a time (user, 2026-08-01), so
this is the loop: change one builder, run this, send him
`out/sheet_line_<hero>_big.png`. A full `render_all.py` is about five minutes and
rebuilds 83 assets to look at four of them.

Takes a key from `roster.BASE_TIER` -- the hero's OWN sprite key, not a variant
key, because the base sprite is one of the four tiers and gets re-rendered too.
"""

import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import roster  # noqa: E402
import render_all  # noqa: E402


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in roster.BASE_TIER:
        print("usage: render_line.py <hero>\nheroes: %s"
              % " ".join(roster.BASE_TIER))
        return 2

    hero = sys.argv[1]
    blender = render_all.find_blender()
    if not blender:
        return 1

    assets = [a for a, _ in roster.variant_rows(hero)]
    log_dir = os.path.join(HERE, "out", "logs")
    os.makedirs(log_dir, exist_ok=True)

    t0 = time.time()
    failed = []
    for a in assets:
        ok, dt, log_path = render_all.render_one(blender, a, log_dir)
        print("  %-32s %s  %4.1fs" % (a.key, "ok  " if ok else "FAIL", dt))
        if not ok:
            failed.append((a.key, log_path))

    if failed:
        print("\n%d FAILED -- the sheet below is stale for those cells" % len(failed))
        for key, log_path in failed:
            print("  %s: %s" % (key, log_path))

    sheets = subprocess.run(
        [blender, "--background", "--factory-startup", "--python",
         os.path.join(HERE, "compose_contact.py"), "--", "--line", hero],
        capture_output=True, text=True, cwd=HERE)
    if "contact sheets written" not in sheets.stdout:
        print("\nsheet FAILED (the renders above are unaffected)")
        print(sheets.stdout[-1500:])
        return 1

    print("\n%s in %.0fs -> %s" % (
        hero, time.time() - t0,
        os.path.join(HERE, "out", "sheet_line_%s_big.png" % hero)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
