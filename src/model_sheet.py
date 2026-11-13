"""Character model sheet for "The Great Laddoo Heist": each character with poses and expressions.

Usage:  python3 model_sheet.py [output.png]
"""
import os
import sys

from PIL import Image, ImageDraw

import kitchen_art as K
from railway_art import OL, SD, font

SS = 2
CELL_W, CELL_H, LABEL_H = 300, 330, 34

ROWS = [
    ("TUBBY BILLA", "the cat", (235, 130, 30), "cat", [
        ("Neutral", dict(pose="idle", face="smirk")),
        ("Evil grin", dict(pose="rub", face="grin")),
        ("Shocked", dict(pose="reach", face="shock")),
        ("YEOW!", dict(pose="flail", face="yeow", trap=True)),
        ("Dizzy", dict(pose="idle", face="dizzy", lump=True)),
        ("Nervous", dict(pose="hide_pan", face="nervous")),
    ]),
    ("CHHOTU", "the mouse", (130, 110, 105), "mouse", [
        ("Neutral", dict(pose="idle", face="smile")),
        ("Carrying a laddoo", dict(pose="carry", face="smile")),
        ("Laughing", dict(pose="laugh", face="laugh")),
        ("Cheeky", dict(pose="cheese", face="tongue")),
        ("Wink", dict(pose="wave", face="wink")),
        ("Shocked", dict(pose="idle", face="shock")),
    ]),
    ("SHERU", "the dog", (150, 90, 45), "dog", [
        ("Asleep", dict(pose="sleep", face="sleep")),
        ("Calm", dict(pose="sit", face="calm")),
        ("Angry", dict(pose="sit", face="angry", lump=True)),
        ("Laughing", dict(pose="sit", face="laugh")),
        ("Happy", dict(pose="sit", face="happy", laddoo=True)),
        ("Running", dict(pose="run", face="angry")),
    ]),
    ("DADI", "the grandmother", (40, 150, 95), "dadi", [
        ("Neutral", dict(pose="hips", face="smile")),
        ("Serving laddoos", dict(pose="carry", face="smile")),
        ("Warning", dict(pose="wag", face="angry")),
        ("Broom ready", dict(pose="broom_up", face="angry")),
        ("THWACK!", dict(pose="broom_swat", face="angry")),
        ("Shocked", dict(pose="shock", face="shock")),
    ]),
]

FIT = {  # (draw fn, anchor x, anchor y, canvas height, scale)
    "cat": (K.draw_cat, K.CAX, K.CAY, 300, 0.78),
    "mouse": (K.draw_mouse, K.MAX, K.MAY, 160, 1.7),
    "dog": (K.draw_dog, K.DAX, K.DAY, 300, 0.78),
    "dadi": (K.draw_dadi, K.GAX, K.GAY, 430, 0.66),
}


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                                              "output", "laddoo_heist_model_sheet.png")
    head_w = 250
    cols = 6
    W, H = head_w + cols * CELL_W, 90 + len(ROWS) * (CELL_H + LABEL_H + 10)
    big = Image.new("RGB", (W * SS, H * SS), (250, 246, 238))
    d = ImageDraw.Draw(big)
    sd = SD(d, SS)
    sd.text((W / 2, 45), "THE GREAT LADDOO HEIST  -  CHARACTER MODEL SHEET", 34, OL)
    for r, (name, role, color, who, cells) in enumerate(ROWS):
        y0 = 90 + r * (CELL_H + LABEL_H + 10)
        sd.rrect((12, y0, head_w - 12, y0 + CELL_H + LABEL_H), 16, fill=color)
        sd.text((head_w / 2, y0 + CELL_H / 2 - 10), name, 28 if len(name) < 10 else 24, (255, 255, 255), stroke=3)
        sd.text((head_w / 2, y0 + CELL_H / 2 + 26), role, 20, (255, 255, 255), name="Inter-SemiBold.otf")
        fn, ax, ay, ch, k = FIT[who]
        for c, (label, st) in enumerate(cells):
            x0 = head_w + c * CELL_W
            sd.rrect((x0 + 6, y0, x0 + CELL_W - 6, y0 + CELL_H + LABEL_H), 14, fill=(255, 255, 255),
                     outline=(220, 214, 204), width=2)
            sd.ellipse((x0 + CELL_W / 2 - 80, y0 + CELL_H - 26, x0 + CELL_W / 2 + 80, y0 + CELL_H - 6),
                       fill=(232, 226, 216))
            gx, gy = x0 + CELL_W / 2, y0 + CELL_H - 16
            fn(SD(d, k * SS, (gx - ax * k) * SS, (gy - ay * k) * SS), 0.4, dict(st))
            sd.text((gx, y0 + CELL_H + LABEL_H / 2 - 2), label, 18, (60, 60, 70), name="Inter-Bold.otf")
    big.resize((W, H), Image.LANCZOS).save(out)
    print("Saved", out)


if __name__ == "__main__":
    main()
