"""
ASCII art generator for GitHub profile README.
Converts an image into ASCII text art, then renders animated frames
(glitch/reveal effect) as a GIF for embedding in README.md.

Usage:
    python3 ascii_render.py input.jpg output.gif
"""

import sys
import random
from PIL import Image, ImageDraw, ImageFont

CHARS = "@%#*+=-:. "[::-1]  # dark -> light density ramp
FONT_SIZE = 7
COLS = 140  # ascii columns


def image_to_ascii_grid(img: Image.Image, cols: int = COLS):
    img = img.convert("L")
    w, h = img.size
    cell_w = w / cols
    # character cells are taller than wide, compensate aspect ratio
    cell_h = cell_w * 2
    rows = int(h / cell_h)
    img = img.resize((cols, rows))
    pixels = list(img.getdata())

    grid = []
    for y in range(rows):
        row = []
        for x in range(cols):
            brightness = pixels[y * cols + x] / 255.0
            idx = int(brightness * (len(CHARS) - 1))
            row.append(CHARS[idx])
        grid.append(row)
    return grid


def render_frame(grid, font, glitch_amount=0.0, revealed_fraction=1.0):
    rows = len(grid)
    cols = len(grid[0])
    cell_w = FONT_SIZE * 0.6
    cell_h = FONT_SIZE

    out_w = int(cols * cell_w)
    out_h = int(rows * cell_h)
    frame = Image.new("RGB", (out_w, out_h), (0, 0, 0))
    draw = ImageDraw.Draw(frame)

    total_cells = rows * cols
    revealed_cells = int(total_cells * revealed_fraction)

    idx = 0
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if idx > revealed_cells:
                idx += 1
                continue
            idx += 1

            c = ch
            if random.random() < glitch_amount:
                c = random.choice(CHARS)

            # subtle color variance: cold white/blue-grey, like the reference image
            base = random.randint(180, 255)
            color = (base - 20, base - 10, base)

            draw.text((x * cell_w, y * cell_h), c, fill=color, font=font)

    return frame


def main():
    if len(sys.argv) < 3:
        print("usage: python3 ascii_render.py input.jpg output.gif")
        sys.exit(1)

    src, dst = sys.argv[1], sys.argv[2]
    img = Image.open(src)
    grid = image_to_ascii_grid(img)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", FONT_SIZE
        )
    except Exception:
        font = ImageFont.load_default()

    frames = []

    # reveal-in effect: image assembles from noise, 15 frames
    reveal_steps = 15
    for i in range(reveal_steps):
        frac = (i + 1) / reveal_steps
        glitch = max(0.0, 0.6 - frac * 0.6)
        frames.append(render_frame(grid, font, glitch_amount=glitch, revealed_fraction=frac))

    # hold + subtle glitch loop, 10 frames
    for _ in range(10):
        frames.append(render_frame(grid, font, glitch_amount=0.03, revealed_fraction=1.0))

    durations = [80] * reveal_steps + [120] * 10

    frames[0].save(
        dst,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=False,
    )
    print(f"saved {dst}, {len(frames)} frames, grid {len(grid)}x{len(grid[0])}")


if __name__ == "__main__":
    main()
