#!/usr/bin/env python3
from pathlib import Path
import sys

from PIL import Image, ImageDraw


SIZE = 1024


def mix(a: int, b: int, t: float) -> int:
    return round(a + (b - a) * t)


def lerp_color(start: tuple[int, int, int], end: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(mix(start[i], end[i], t) for i in range(3))


def rounded_gradient(size: int, radius: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    gradient = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pixels = gradient.load()
    for y in range(size):
        t = y / (size - 1)
        color = lerp_color(top, bottom, t)
        for x in range(size):
            pixels[x, y] = (*color, 255)

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
    gradient.putalpha(mask)
    return gradient


def draw_vertical_gradient_rect(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int) -> None:
    x1, y1, x2, y2 = box
    width = x2 - x1
    height = y2 - y1
    shape = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shape_pixels = shape.load()
    for y in range(height):
        t = y / max(1, height - 1)
        if t < 0.55:
            color = lerp_color((124, 255, 178), (69, 245, 155), t / 0.55)
        else:
            color = lerp_color((69, 245, 155), (37, 199, 116), (t - 0.55) / 0.45)
        for x in range(width):
            shape_pixels[x, y] = (*color, 255)

    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=255)
    shape.putalpha(mask)
    draw._image.alpha_composite(shape, (x1, y1))


def spark_points(cx: int, cy: int, outer_x: int, outer_y: int, inner_x: int, inner_y: int) -> list[tuple[int, int]]:
    return [
        (cx, cy - outer_y),
        (cx + inner_x, cy - inner_y),
        (cx + outer_x, cy),
        (cx + inner_x, cy + inner_y),
        (cx, cy + outer_y),
        (cx - inner_x, cy + inner_y),
        (cx - outer_x, cy),
        (cx - inner_x, cy - inner_y),
    ]


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist/Typemore-icon.png")
    output.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    app_bg = rounded_gradient(832, 206, (16, 26, 20), (5, 8, 6))
    image.alpha_composite(app_bg, (96, 96))

    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((112, 112, 912, 912), radius=190, outline=(124, 255, 178, 31), width=16)

    for box, radius in [((256, 316, 612, 398), 41), ((393, 316, 475, 708), 41)]:
        draw_vertical_gradient_rect(draw, box, radius)

    draw.polygon(spark_points(734, 458, 102, 102, 30, 30), fill=(124, 255, 178, 255))
    draw.ellipse((785, 377, 803, 395), fill=(167, 255, 208, 132))

    image.save(output)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
