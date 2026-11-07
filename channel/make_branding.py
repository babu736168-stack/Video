"""Generate every image a YouTube channel needs, in one consistent brand style.

    python3 make_branding.py            # -> out/*.png

Edit the BRAND block below (name, handle, tagline, colours) and re-run.
Sizes follow YouTube's current upload specs:
  profile picture 800x800 (shown as a circle), banner 2560x1440 (safe area 1546x423),
  video watermark 150x150, thumbnail 1280x720, Shorts cover 1080x1920.
"""
import math
import os
import random
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------- brand
BRAND = {
    "name": "RAHASYA LAB",
    "name_hi": "रहस्य लैब",
    "handle": "@RahasyaLab",
    "tagline": "Science ke peeche ka sach",
    "tagline2": "Mysteries  •  Science  •  Myth-busting",
    "schedule": "NEW SHORTS EVERY TUE • THU • SAT",
}
BG_TOP = (8, 10, 22)        # near-black navy
BG_BOTTOM = (22, 14, 48)    # deep violet
ACCENT = (255, 200, 40)     # caption yellow, same as the videos
ACCENT2 = (0, 210, 255)     # cyan glow
WHITE = (245, 246, 250)
GREY = (160, 165, 185)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def font(style, size):
    path = subprocess.check_output(["fc-match", "-f", "%{file}", f"Inter:style={style}"]).decode()
    return ImageFont.truetype(path, int(size))


def font_hi(size):
    path = subprocess.check_output(["fc-match", "-f", "%{file}", "FreeSans:style=Bold:lang=hi"]).decode()
    return ImageFont.truetype(path, int(size), layout_engine=ImageFont.Layout.RAQM)


# ---------------------------------------------------------------- pieces
def background(w, h, seed=7):
    """Vertical gradient + star field + soft glow blobs."""
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM)))
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    g = ImageDraw.Draw(glow)
    rnd = random.Random(seed)
    for cx, cy, r, col in [(0.15, 0.3, 0.35, (60, 20, 120)), (0.85, 0.75, 0.4, (0, 70, 110)),
                           (0.5, 0.5, 0.25, (40, 30, 90))]:
        R = r * max(w, h)
        g.ellipse([cx * w - R, cy * h - R, cx * w + R, cy * h + R], fill=col)
    glow = glow.filter(ImageFilter.GaussianBlur(max(w, h) * 0.12))
    img = Image.blend(img, Image.composite(glow, img, Image.new("L", (w, h), 255)), 0.55)
    d = ImageDraw.Draw(img)
    for _ in range(int(w * h / 6000)):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        s = rnd.choice([1, 1, 1, 2, 2, 3]) * max(1, w // 1280)
        v = rnd.randint(90, 230)
        d.ellipse([x, y, x + s, y + s], fill=(v, v, min(255, v + 20)))
    return img


def logo_mark(size):
    """Magnifying glass whose lens holds an atom: 'investigating science'."""
    S = size * 4  # supersample
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy, r = S * 0.43, S * 0.43, S * 0.30
    lw = int(S * 0.055)
    # handle
    a = math.radians(45)
    x0, y0 = cx + r * math.cos(a), cy + r * math.sin(a)
    x1, y1 = cx + S * 0.52 * math.cos(a), cy + S * 0.52 * math.sin(a)
    d.line([(x0, y0), (x1, y1)], fill=ACCENT, width=int(S * 0.10))
    d.ellipse([x1 - S * 0.05, y1 - S * 0.05, x1 + S * 0.05, y1 + S * 0.05], fill=ACCENT)
    # lens
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(14, 18, 40, 255), outline=ACCENT, width=lw)
    # atom orbits
    orb = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    for ang in (0, 60, 120):
        o = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(o).ellipse([cx - r * 0.72, cy - r * 0.27, cx + r * 0.72, cy + r * 0.27],
                                  outline=ACCENT2, width=int(S * 0.018))
        orb = Image.alpha_composite(orb, o.rotate(ang, center=(cx, cy), resample=Image.BICUBIC))
    im = Image.alpha_composite(im, orb)
    d = ImageDraw.Draw(im)
    n = r * 0.13
    d.ellipse([cx - n, cy - n, cx + n, cy + n], fill=WHITE)
    # glint
    d.arc([cx - r * 0.78, cy - r * 0.78, cx + r * 0.78, cy + r * 0.78], 200, 250,
          fill=(255, 255, 255, 150), width=int(S * 0.02))
    return im.resize((size, size), Image.LANCZOS)


def text_c(d, xy, txt, f, fill, **kw):
    d.text(xy, txt, font=f, fill=fill, anchor="mm", **kw)


def fit(txt, style, max_w, start):
    s = start
    while s > 10 and font(style, s).getlength(txt) > max_w:
        s -= 2
    return font(style, s)


# ---------------------------------------------------------------- assets
def profile_picture():
    W = 800
    img = background(W, W, seed=3)
    m = logo_mark(int(W * 0.78))
    img.paste(m, ((W - m.width) // 2 + 10, (W - m.height) // 2 + 10), m)
    # preview with circular crop (how YouTube shows it)
    mask = Image.new("L", (W, W), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, W, W], fill=255)
    prev = Image.new("RGBA", (W, W), (255, 255, 255, 0))
    prev.paste(img, (0, 0), mask)
    return img, prev


def banner():
    W, H = 2560, 1440
    img = background(W, H, seed=11)
    d = ImageDraw.Draw(img)
    # decorative grid lines on outer (TV-only) area
    for i in range(0, W, 80):
        d.line([(i, 0), (i, H)], fill=(30, 30, 60))
    for j in range(0, H, 80):
        d.line([(0, j), (W, j)], fill=(30, 30, 60))
    img = Image.blend(background(W, H, seed=11), img, 0.35)
    d = ImageDraw.Draw(img)
    # safe area 1546x423 centred: everything important lives here
    sx0, sy0 = (W - 1546) // 2, (H - 423) // 2
    m = logo_mark(330)
    img.paste(m, (sx0 + 20, sy0 + 45), m)
    tx = sx0 + 400
    d.text((tx, sy0 + 70), BRAND["name"], font=font("Black", 150), fill=WHITE, anchor="lt")
    d.text((tx + 4, sy0 + 245), BRAND["name_hi"], font=font_hi(62), fill=ACCENT, anchor="lt")
    w_hi = font_hi(62).getlength(BRAND["name_hi"])
    d.text((tx + w_hi + 34, sy0 + 250), "•  " + BRAND["tagline"], font=font("SemiBold", 54), fill=ACCENT, anchor="lt")
    d.text((tx + 4, sy0 + 330), BRAND["tagline2"], font=font("Medium", 40), fill=GREY, anchor="lt")
    # schedule ribbon below safe area (visible on desktop/TV)
    rf = font("Bold", 34)
    rw = rf.getlength(BRAND["schedule"]) + 80
    rx, ry = (W - rw) / 2, sy0 + 423 + 40
    d.rounded_rectangle([rx, ry, rx + rw, ry + 64], radius=32, fill=ACCENT)
    text_c(d, (W / 2, ry + 33), BRAND["schedule"], rf, BG_TOP)
    return img


def banner_safe_preview(b):
    """Same banner with YouTube's display zones drawn on, for checking only."""
    W, H = b.size
    p = b.copy().convert("RGBA")
    o = Image.new("RGBA", p.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(o)
    zones = [((W - 2560) // 2, (H - 423) // 2, 2560, 423, (0, 200, 255), "Desktop (all)"),
             ((W - 1855) // 2, (H - 423) // 2, 1855, 423, (0, 255, 120), "Tablet"),
             ((W - 1546) // 2, (H - 423) // 2, 1546, 423, (255, 60, 60), "SAFE AREA — phone, everywhere")]
    for x, y, w, h, c, label in zones:
        d.rectangle([x, y, x + w, y + h], outline=c + (255,), width=6)
        d.text((x + 14, y + 10), label, font=font("Bold", 30), fill=c + (255,))
    d.text((20, 20), "TV: full 2560x1440", font=font("Bold", 36), fill=(255, 255, 255, 255))
    return Image.alpha_composite(p, o)


def watermark():
    W = 150
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([4, 4, W - 4, W - 4], fill=(10, 12, 28, 235), outline=ACCENT, width=5)
    m = logo_mark(112)
    img.paste(m, (22, 22), m)
    return img


def thumbnail(title="TUNGUSKA", sub="1908 ka RAHASYA", tag="SCIENCE MYSTERY", seed=5):
    """1280x720 template: big 2-3 word title, yellow keyword, brand corner badge."""
    W, H = 1280, 720
    img = background(W, H, seed=seed)
    d = ImageDraw.Draw(img)
    # right-side placeholder "hero" circle (replace with a frame from the video)
    d.ellipse([760, 120, 1240, 600], fill=(255, 120, 30))
    hero = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(hero).ellipse([700, 60, 1300, 660], fill=(255, 140, 40, 90))
    img = Image.alpha_composite(img.convert("RGBA"), hero.filter(ImageFilter.GaussianBlur(40)))
    d = ImageDraw.Draw(img)
    d.ellipse([800, 160, 1200, 560], fill=(255, 210, 90))
    text_c(d, (1000, 360), "?", font("Black", 300), (40, 20, 10))
    # tag pill
    tf = font("Bold", 34)
    tw = tf.getlength(tag) + 50
    d.rounded_rectangle([60, 70, 60 + tw, 130], radius=30, fill=ACCENT2)
    d.text((85, 100), tag, font=tf, fill=BG_TOP, anchor="lm")
    # title
    f1 = fit(title, "Black", 680, 170)
    d.text((60, 300), title, font=f1, fill=WHITE, anchor="lm", stroke_width=10, stroke_fill=(0, 0, 0))
    f2 = fit(sub, "Black", 680, 100)
    d.text((60, 460), sub, font=f2, fill=ACCENT, anchor="lm", stroke_width=8, stroke_fill=(0, 0, 0))
    # brand badge
    wm = watermark().resize((90, 90), Image.LANCZOS)
    img.paste(wm, (60, 590), wm)
    d.text((165, 635), BRAND["name"], font=font("Bold", 34), fill=WHITE, anchor="lm")
    return img.convert("RGB")


def shorts_cover(title="SKELETON LAKE", sub="Roopkund ka sach"):
    W, H = 1080, 1920
    img = background(W, H, seed=9)
    d = ImageDraw.Draw(img)
    m = logo_mark(520)
    img.paste(m, ((W - 520) // 2, 520), m)
    f1 = fit(title, "Black", W - 120, 150)
    text_c(d, (W / 2, 1250), title, f1, WHITE, stroke_width=10, stroke_fill=(0, 0, 0))
    f2 = fit(sub, "Black", W - 160, 96)
    text_c(d, (W / 2, 1390), sub, f2, ACCENT, stroke_width=8, stroke_fill=(0, 0, 0))
    text_c(d, (W / 2, 1700), BRAND["handle"], font("Bold", 52), GREY)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    pp, pp_prev = profile_picture()
    pp.save(f"{OUT}/profile_800.png")
    pp_prev.save(f"{OUT}/profile_preview_circle.png")
    b = banner()
    b.save(f"{OUT}/banner_2560x1440.png", optimize=True)
    banner_safe_preview(b).convert("RGB").resize((1280, 720), Image.LANCZOS).save(f"{OUT}/banner_safe_zones_preview.png")
    watermark().save(f"{OUT}/watermark_150.png")
    thumbnail().save(f"{OUT}/thumbnail_template_tunguska.png")
    thumbnail("DEODORANT", "Kitna KHATRA?", "HEALTH FACTS", seed=21).save(f"{OUT}/thumbnail_template_deodorant.png")
    shorts_cover().save(f"{OUT}/shorts_cover_roopkund.png")
    for f in sorted(os.listdir(OUT)):
        print(f"{OUT}/{f}  {os.path.getsize(f'{OUT}/{f}') // 1024} KB")


if __name__ == "__main__":
    main()
