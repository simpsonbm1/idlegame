"""A 5x7 bitmap font, drawn into a numpy RGBA buffer.

Contact sheets need every cell named, and there is no text renderer available in
a headless Blender that produces HARD pixels. Blender's `blf` draws antialiased
glyphs into a GPU offscreen buffer, which is the one thing this whole pipeline
exists to avoid: a soft label on a sheet whose purpose is judging hard-edged
sprites reads as a rendering fault rather than as writing.

So the font is data. Each glyph is seven rows of five characters, '#' for ink.
Drawn at scale 1 into the 1x sheet and then carried through the same
nearest-neighbour upscale as the sprites, label pixels end up exactly the size of
sprite pixels. That is why labels are drawn BEFORE the upscale, not after.

Uppercase, digits, space and hyphen only. Roster keys are lowercase with
underscores, and `text_lines()` handles the conversion.
"""

import numpy as np

GLYPH_W = 5
GLYPH_H = 7
ADVANCE = GLYPH_W + 1      # one blank column between glyphs
LINE_GAP = 2               # blank rows between stacked lines

_RAW = {
    "A": ".###.|#...#|#...#|#####|#...#|#...#|#...#",
    "B": "####.|#...#|#...#|####.|#...#|#...#|####.",
    "C": ".###.|#...#|#....|#....|#....|#...#|.###.",
    "D": "####.|#...#|#...#|#...#|#...#|#...#|####.",
    "E": "#####|#....|#....|####.|#....|#....|#####",
    "F": "#####|#....|#....|####.|#....|#....|#....",
    "G": ".###.|#...#|#....|#.###|#...#|#...#|.###.",
    "H": "#...#|#...#|#...#|#####|#...#|#...#|#...#",
    "I": "#####|..#..|..#..|..#..|..#..|..#..|#####",
    "J": "..###|...#.|...#.|...#.|...#.|#..#.|.##..",
    "K": "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#",
    "L": "#....|#....|#....|#....|#....|#....|#####",
    "M": "#...#|##.##|#.#.#|#...#|#...#|#...#|#...#",
    "N": "#...#|##..#|#.#.#|#..##|#...#|#...#|#...#",
    "O": ".###.|#...#|#...#|#...#|#...#|#...#|.###.",
    "P": "####.|#...#|#...#|####.|#....|#....|#....",
    "Q": ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#",
    "R": "####.|#...#|#...#|####.|#.#..|#..#.|#...#",
    "S": ".####|#....|#....|.###.|....#|....#|####.",
    "T": "#####|..#..|..#..|..#..|..#..|..#..|..#..",
    "U": "#...#|#...#|#...#|#...#|#...#|#...#|.###.",
    "V": "#...#|#...#|#...#|#...#|#...#|.#.#.|..#..",
    "W": "#...#|#...#|#...#|#...#|#.#.#|##.##|#...#",
    "X": "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#",
    "Y": "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..",
    "Z": "#####|....#|...#.|..#..|.#...|#....|#####",
    "0": ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.",
    "1": "..#..|.##..|..#..|..#..|..#..|..#..|.###.",
    "2": ".###.|#...#|....#|...#.|..#..|.#...|#####",
    "3": "#####|...#.|..#..|...#.|....#|#...#|.###.",
    "4": "...#.|..##.|.#.#.|#..#.|#####|...#.|...#.",
    "5": "#####|#....|####.|....#|....#|#...#|.###.",
    "6": "..##.|.#...|#....|####.|#...#|#...#|.###.",
    "7": "#####|....#|...#.|..#..|.#...|.#...|.#...",
    "8": ".###.|#...#|#...#|.###.|#...#|#...#|.###.",
    "9": ".###.|#...#|#...#|.####|....#|...#.|.##..",
    "-": ".....|.....|.....|#####|.....|.....|.....",
    " ": ".....|.....|.....|.....|.....|.....|.....",
}

# "#" -> True, as (7, 5) boolean masks, rows top-down.
GLYPHS = {ch: np.array([[c == "#" for c in row] for row in spec.split("|")],
                       dtype=bool)
          for ch, spec in _RAW.items()}

MISSING = GLYPHS[" "]


def text_width(s):
    """Pixel width of `s` at scale 1, without the trailing inter-glyph column."""
    return max(0, len(s) * ADVANCE - 1)


def text_lines(key, max_width):
    """Roster key -> uppercase display lines that each fit inside `max_width`.

    Wraps on the underscores, which are the only word boundary a key has. A
    single word longer than the cell is left overlong rather than split: a
    truncated key is worse than a label that runs wide, because the whole point
    is being able to name the sprite you want changed.
    """
    words = key.replace("_", " ").upper().split()
    if not words:
        return []
    lines, cur = [], words[0]
    for w in words[1:]:
        trial = cur + " " + w
        if text_width(trial) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def block_height(n_lines):
    """Pixel height of an `n_lines` label block at scale 1."""
    if n_lines <= 0:
        return 0
    return n_lines * GLYPH_H + (n_lines - 1) * LINE_GAP


def draw_text(canvas, text, x, y_bottom, rgba):
    """Stamp `text` into an RGBA float array, bottom-left corner at (x, y_bottom).

    `canvas` follows Blender's pixel convention where row 0 is the BOTTOM row, so
    glyph row 0 (the top of the letter) is written at the highest y. Pixels
    outside the canvas are dropped rather than wrapped.
    """
    h, w = canvas.shape[:2]
    ink = np.array(rgba, dtype=np.float32)
    y_top = y_bottom + GLYPH_H - 1
    for i, ch in enumerate(text):
        mask = GLYPHS.get(ch, MISSING)
        gx = x + i * ADVANCE
        for row in range(GLYPH_H):
            y = y_top - row
            if y < 0 or y >= h:
                continue
            for col in range(GLYPH_W):
                if not mask[row, col]:
                    continue
                px = gx + col
                if 0 <= px < w:
                    canvas[y, px] = ink


def draw_block(canvas, lines, cx, y_bottom, rgba):
    """Draw `lines` centred on `cx`, the lowest line sitting on `y_bottom`."""
    for i, line in enumerate(reversed(lines)):
        y = y_bottom + i * (GLYPH_H + LINE_GAP)
        draw_text(canvas, line, int(cx - text_width(line) // 2), y, rgba)
