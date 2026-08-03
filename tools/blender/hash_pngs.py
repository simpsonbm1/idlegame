"""Pixel-hash PNGs, inside Blender, where pixel access exists.

    blender -b --factory-startup --python hash_pngs.py -- <job.json> <result.json>

`job.json` is a list of absolute paths. `result.json` maps each path that exists
to "sha256|WxH". Non-existent paths are silently absent from the result, which
is how a caller distinguishes "not rendered" from "rendered and hashed".

**The hash covers decoded RGBA bytes plus dimensions, never file bytes.**
Blender's PNG encoder is not deterministic, so byte hashes of identical art
differ; decoded pixels do not. Everything that compares art in this pipeline
must go through `hash_image` so there is exactly one definition of "same".

Importable from other Blender-side scripts (the composers) for the same reason.
No system-Python caller may import this: it needs `bpy`.
"""

import hashlib
import json
import sys

import bpy
import numpy as np


def hash_pixels(arr, w, h):
    """sha256 of an RGBA float buffer quantized to 8 bits, plus dimensions.

    `np.rint` before uint8: the floats are n/255 values off a byte image, and
    truncation would flip a pixel that reads 0.9999999 back to the wrong byte.
    """
    q = np.rint(np.asarray(arr, dtype=np.float32) * 255.0).astype(np.uint8)
    d = hashlib.sha256()
    d.update(("%dx%d|" % (w, h)).encode())
    d.update(q.tobytes())
    return "%s|%dx%d" % (d.hexdigest(), w, h)


def hash_image(path):
    """Hash one PNG on disk. Returns "sha256|WxH"."""
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    bpy.data.images.remove(img)
    return hash_pixels(buf, w, h)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(argv) != 2:
        print(__doc__)
        return 2
    job_path, result_path = argv
    with open(job_path, encoding="utf-8") as fh:
        paths = json.load(fh)
    result = {}
    for p in paths:
        try:
            result[p] = hash_image(p)
        except RuntimeError:
            pass  # unloadable or missing: absent from the result, caller decides
    with open(result_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("hashed %d of %d file(s)" % (len(result), len(paths)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
