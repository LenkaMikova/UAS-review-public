"""Cut platform-free sensor icons out of the existing UAS icons.

The drone icons are platform+payload combinations, so using them for a sensor
*category* (which also covers satellite and ground instruments) says the wrong
thing. The payload itself is already drawn in the right style and colour, so the
generic icons are cropped from it rather than redrawn.

Writes 80_figures/81_icons/sensor_*.png. Safe to re-run.
"""
from pathlib import Path

from PIL import Image

FIG = Path(__file__).resolve().parent.parent / "80_figures" / "81_icons"

# source, output, and the part of the drawing that carries the meaning
CROPS = [
    ("drone_ms", "sensor_ms", "payload"),
    ("drone_rgb", "sensor_rgb", "payload"),
    ("drone_thermal", "sensor_thermal", "payload"),
    ("drone_hs", "sensor_hs", "payload"),
    ("drone_gnssr", "sensor_microwave", "signal"),
    ("drone_lidar", "sensor_lidar", "signal"),
]

PAD = 12


def saturated_box(im: Image.Image, lower_half_only: bool) -> tuple[int, int, int, int]:
    """Bounding box of strongly coloured (non-grey, non-white) pixels."""
    rgb = im.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    alpha = im.convert("RGBA").split()[3].load()
    y_from = h // 2 if lower_half_only else 0
    xs, ys = [], []
    for y in range(y_from, h):
        for x in range(w):
            if alpha[x, y] < 128:
                continue
            r, g, b = px[x, y]
            hi, lo = max(r, g, b), min(r, g, b)
            if hi - lo > 60 and hi > 60:          # clearly coloured, not grey
                xs.append(x)
                ys.append(y)
    if not xs:
        raise SystemExit("no coloured pixels found")
    return min(xs), min(ys), max(xs), max(ys)


for src, dst, part in CROPS:
    im = Image.open(FIG / f"{src}.png").convert("RGBA")
    w, h = im.size
    x0, y0, x1, y1 = saturated_box(im, lower_half_only=True)

    # "signal" icons are the beams / waves alone: including the grey payload box
    # above them drags the drone body into the crop.
    box = (max(0, x0 - PAD), max(0, y0 - PAD), min(w, x1 + PAD + 1), min(h, y1 + PAD + 1))
    out = im.crop(box)

    # square canvas so every icon keeps the same optical weight in a table cell
    side = max(out.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(out, ((side - out.width) // 2, (side - out.height) // 2), out)
    canvas = canvas.resize((256, 256), Image.LANCZOS)
    canvas.save(FIG / f"{dst}.png", optimize=True)

    print(f"{src:15} -> {dst:18} crop={box} size={(FIG / f'{dst}.png').stat().st_size // 1024} kB")
