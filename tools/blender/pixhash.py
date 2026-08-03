"""THE pixel-hash definition. One module, one definition, every caller.

    hash_file(path)   -> "sha256hex|WxH"
    hash_bytes(blob)  -> same, for a PNG already in memory (a staged git blob)

The hash covers decoded RGBA bytes, top-down row order as Pillow delivers them,
plus the dimensions. Never file bytes: Blender's PNG encoder is not
deterministic, so byte hashes of identical art differ; decoded pixels do not.

**Any change to this definition invalidates every hash in
`assets/rendered/manifest.json`, so the manifest must be regenerated
(`publish.py --init-manifest`) in the SAME commit as the change.** This has
already happened once: the first definition hashed Blender's bottom-up float
buffers because the system Python had no imaging library, and every pixel
operation paid a ~3 second Blender launch for it. Pillow ended that (installed
2026-08-02, both interpreters, user-approved); the hashes were regenerated in
the commit that switched, and `hash_pngs.py` -- the Blender-side hasher -- was
deleted rather than left as a second definition that would silently drift.

Runs under the system Python. Pillow is REQUIRED, deliberately: the pre-commit
guard imports this and must fail closed, not degrade to a weaker check, when
the library is missing (the accepted desktop-bootstrap speed bump).
"""

import hashlib
import io

try:
    from PIL import Image
except ImportError:
    raise ImportError(
        "Pillow is required by the art pipeline and its pre-commit guard.\n"
        "Install it into BOTH interpreters (the hook uses `python`, sessions"
        " use `py`):\n"
        "    py -m pip install pillow numpy\n"
        "    python -m pip install pillow numpy")


def _hash_image(img):
    rgba = img.convert("RGBA")
    d = hashlib.sha256()
    d.update(("%dx%d|" % rgba.size).encode())
    d.update(rgba.tobytes())
    return "%s|%dx%d" % (d.hexdigest(), rgba.size[0], rgba.size[1])


def hash_file(path):
    with Image.open(path) as img:
        return _hash_image(img)


def hash_bytes(blob):
    with Image.open(io.BytesIO(blob)) as img:
        return _hash_image(img)
