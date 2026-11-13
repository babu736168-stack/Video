"""Builds an anatomy sheet from detailed part functions: each part enlarged and labelled, plus the assembled character."""
import math
import os
import re

from PIL import Image, ImageDraw, ImageFont, ImageOps

from charart import Cv, tone

FD = "/usr/share/fonts/opentype/inter/"
CARD_BG, CARD_LINE = (255, 252, 246), (226, 216, 200)


def font(n, size):
    return ImageFont.truetype(FD + n, size)


def render(spec_entry, S, **kw):
    fn, w, h, cx, cy = spec_entry
    cv = Cv(w, h, S, cx, cy)
    ann = fn(cv) or []
    return cv, ann


def fit_part(spec_entry, cw, ch, sidepad, vpad, kmax=7.0, ss=2):
    """Render a part sharp at the biggest scale that fits the cell. Returns (image, annotations in image px)."""
    cv, _ = render(spec_entry, 2)
    bb = cv.im.getbbox() or (0, 0, 10, 10)
    ew, eh = (bb[2] - bb[0]) / 2, (bb[3] - bb[1]) / 2
    k = min((cw - sidepad) / max(ew, 1), (ch - vpad) / max(eh, 1), kmax)
    S = k * ss
    cv, ann = render(spec_entry, S)
    bb = cv.im.getbbox() or (0, 0, 10, 10)
    im = cv.im.crop(bb).resize((max(1, round((bb[2] - bb[0]) / ss)), max(1, round((bb[3] - bb[1]) / ss))), Image.LANCZOS)
    out = []
    for x, y, t, dx, dy in ann:
        px, py = cv.P(x, y)
        out.append(((px - bb[0]) / ss, (py - bb[1]) / ss, t, dx, dy))
    return im, out


def place(char, part_cv, pos, mirror, rot, S):
    im = part_cv.im
    ox, oy = part_cv.P(0, 0)
    if mirror:
        im = ImageOps.mirror(im)
        ox = im.width - ox
    if rot:
        im = im.rotate(rot, center=(ox, oy), resample=Image.BICUBIC)
    px, py = char.P(*pos)
    char.im.alpha_composite(im, (int(round(px - ox)), int(round(py - oy))))


def assemble(spec, assembly, S, w, h, cx, cy):
    char = Cv(w, h, S, cx, cy)
    for name, x, y, z, mir, rot in sorted(assembly, key=lambda a: a[3]):
        fn, pw, ph, pcx, pcy = spec[name]
        pc = Cv(pw, ph, S, pcx, pcy)
        fn(pc)
        place(char, pc, (x, y), mir, rot, S)
    return char


def annotate(d, ann, ox, oy):
    f = font("Inter-Bold.otf", 15)
    for x, y, text, dx, dy in ann:
        px, py = ox + x, oy + y
        tx, ty = px + dx, py + dy
        d.line((px, py, tx, ty), fill=(90, 90, 100), width=2)
        d.ellipse((px - 6, py - 6, px + 6, py + 6), fill=(255, 90, 60), outline=(255, 255, 255), width=2)
        tw = f.getlength(text) + 14
        d.rounded_rectangle((tx - tw / 2, ty - 12, tx + tw / 2, ty + 12), 8, fill=(255, 255, 255), outline=(90, 90, 100), width=2)
        d.text((tx, ty), text, font=f, fill=(50, 50, 60), anchor="mm")


def make_sheet(c, outdir):
    """c: dict(name, role, blurb, color, spec, assembly, marks, parts[(label, desc, key)], char_box=(w,h,cx,cy))."""
    parts = c["parts"]
    cols, cell_w, cell_h, draw_h, gap = 4, 400, 414, 300, 20
    rows = math.ceil(len(parts) / cols)
    left_w, margin, band = 560, 30, 124
    W = margin * 2 + left_w + gap + cols * cell_w + (cols - 1) * gap
    H = band + rows * (cell_h + gap) + margin - 6
    img = Image.new("RGB", (W, H), (248, 243, 234))
    d = ImageDraw.Draw(img)
    color = c["color"]
    d.rectangle((0, 0, W, band - 14), fill=color)
    d.text((margin + 6, 40), c["name"], font=font("Inter-Black.otf", 58), fill=(255, 255, 255), anchor="lm")
    d.text((margin + 8, 88), c["role"], font=font("Inter-Bold.otf", 28), fill=tone(color, 1.6), anchor="lm")
    d.text((W - margin, 62), "ANATOMY SHEET  -  THE GREAT LADDOO HEIST", font=font("Inter-Bold.otf", 22), fill=(255, 255, 255), anchor="rm")
    d.text((W - margin, 92), c["blurb"], font=font("Inter-Regular.otf", 19), fill=(255, 255, 255), anchor="rm")
    # assembled character
    lx, ly, lh = margin, band, rows * (cell_h + gap) - gap
    d.rounded_rectangle((lx, ly, lx + left_w, ly + lh), 22, fill=CARD_BG, outline=CARD_LINE, width=3)
    d.text((lx + left_w / 2, ly + 30), "ASSEMBLED", font=font("Inter-Black.otf", 20), fill=(150, 140, 125), anchor="mm")
    cw_, ch_, ccx, ccy = c["char_box"]
    probe = assemble(c["spec"], c["assembly"], 1, cw_, ch_, ccx, ccy)
    bb = probe.im.getbbox()
    ew, eh = bb[2] - bb[0], bb[3] - bb[1]
    k = min((left_w - 190) / ew, (lh - 120) / eh)
    ss = 2
    big = assemble(c["spec"], c["assembly"], k * ss, cw_, ch_, ccx, ccy)
    bb2 = big.im.getbbox()
    fig = big.im.crop(bb2).resize((round((bb2[2] - bb2[0]) / ss), round((bb2[3] - bb2[1]) / ss)), Image.LANCZOS)
    fx = lx + (left_w - fig.width) / 2
    fy = ly + 56 + (lh - 80 - fig.height) / 2
    img.paste(fig, (int(fx), int(fy)), fig)
    d = ImageDraw.Draw(img)
    pts = []
    for n, x, y, side in c["marks"]:
        px, py = big.P(x, y)
        pts.append([n, fx + (px - bb2[0]) / ss, fy + (py - bb2[1]) / ss, side])
    for side in ("L", "R"):
        grp = sorted((p for p in pts if p[3] == side), key=lambda p: p[2])
        ys = []
        for i, p in enumerate(grp):
            ys.append(p[2] if i == 0 else max(p[2], ys[-1] + 48))
        for p, yy in zip(grp, ys):
            bx = lx + 40 if side == "L" else lx + left_w - 40
            d.line((p[1], p[2], bx, yy), fill=(120, 110, 100), width=2)
            d.ellipse((p[1] - 6, p[2] - 6, p[1] + 6, p[2] + 6), fill=(255, 90, 60), outline=(255, 255, 255), width=2)
            d.ellipse((bx - 19, yy - 19, bx + 19, yy + 19), fill=color, outline=(255, 255, 255), width=3)
            d.text((bx, yy), str(p[0]), font=font("Inter-Black.otf", 22), fill=(255, 255, 255), anchor="mm")
    # part cells
    gx0 = margin + left_w + gap
    safe = re.sub(r"[^a-z0-9]+", "_", c["name"].lower()).strip("_")
    os.makedirs(os.path.join(outdir, "parts", safe), exist_ok=True)
    for i, (label, desc, key) in enumerate(parts):
        cc, r = i % cols, i // cols
        x0, y0 = gx0 + cc * (cell_w + gap), band + r * (cell_h + gap)
        d.rounded_rectangle((x0, y0, x0 + cell_w, y0 + cell_h), 22, fill=CARD_BG, outline=CARD_LINE, width=3)
        pim, ann = fit_part(c["spec"][key], cell_w, draw_h, 90 if key in c.get("annotated", ()) else 50, 56)
        ox, oy = x0 + (cell_w - pim.width) / 2, y0 + 8 + (draw_h - pim.height) / 2
        img.paste(pim, (int(ox), int(oy)), pim)
        d = ImageDraw.Draw(img)
        annotate(d, ann, ox, oy)
        d.line((x0 + 22, y0 + draw_h + 16, x0 + cell_w - 22, y0 + draw_h + 16), fill=CARD_LINE, width=2)
        d.ellipse((x0 + 14, y0 + 14, x0 + 50, y0 + 50), fill=color, outline=(255, 255, 255), width=3)
        d.text((x0 + 32, y0 + 32), str(i + 1), font=font("Inter-Black.otf", 21), fill=(255, 255, 255), anchor="mm")
        d.text((x0 + 22, y0 + draw_h + 40), label, font=font("Inter-Black.otf", 25), fill=(45, 40, 40), anchor="lm")
        yy = y0 + draw_h + 64
        dfont = font("Inter-Regular.otf", 17)
        line = ""
        for wd in desc.split():
            if dfont.getlength((line + " " + wd).strip()) > cell_w - 44 and line:
                d.text((x0 + 22, yy), line, font=dfont, fill=(90, 85, 80), anchor="lm")
                yy += 22
                line = wd
            else:
                line = (line + " " + wd).strip()
        d.text((x0 + 22, yy), line, font=dfont, fill=(90, 85, 80), anchor="lm")
        ex, _ = fit_part(c["spec"][key], 1400, 1400, 40, 40, kmax=12, ss=1)
        ex.save(os.path.join(outdir, "parts", safe, f"{i + 1:02d}_{re.sub(r'[^a-z0-9]+', '_', label.lower()).strip('_')}.png"))
    path = os.path.join(outdir, f"anatomy_{safe}.png")
    img.save(path)
    print("Saved", path)
    return path
