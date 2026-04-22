from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def render(size: int) -> Image.Image:
    scale = size / 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    grad = Image.new("RGB", (size, size))
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size)
            r = int(0x3B + (0x4F - 0x3B) * t)
            g = int(0x82 + (0x46 - 0x82) * t)
            b = int(0xF6 + (0xE5 - 0xF6) * t)
            grad.putpixel((x, y), (r, g, b))
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    r = int(16 * scale)
    md.rounded_rectangle([(0, 0), (size - 1, size - 1)], radius=r, fill=255)
    img.paste(grad, (0, 0), mask)

    draw = ImageDraw.Draw(img)
    font_path = None
    for c in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    ]:
        if Path(c).exists():
            font_path = c
            break
    font_size = int(40 * scale)
    try:
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), "S", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - tw) / 2 - bbox[0]
    y = (size - th) / 2 - bbox[1]
    draw.text((x, y), "S", font=font, fill=(255, 255, 255, 255))
    return img


OUT = Path("/app/_favicon_out")
OUT.mkdir(exist_ok=True)

sizes = [16, 24, 32, 48, 64]
imgs = [render(s) for s in sizes]
imgs[0].save(
    OUT / "favicon.ico",
    format="ICO",
    sizes=[(s, s) for s in sizes],
    append_images=imgs[1:],
)
render(180).save(OUT / "apple-touch-icon.png", format="PNG")
print("OK")
