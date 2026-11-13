"""Build the detailed anatomy sheets.  Usage: python3 build_v2.py [cat|mouse|dog|dadi ...]"""
import os
import sys

import sheet_v2

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output"))


def cat():
    import cat_v2 as C
    return dict(
        name="TUBBY BILLA", role="The Proud House Cat", color=(235, 130, 30),
        blurb="Orange tabby with green eyes, cream chest, striped limbs and white-gloved paws.",
        spec=C.SPEC, assembly=C.ASSEMBLY, char_box=(520, 560, 0, 30),
        annotated=("arm", "leg", "foot", "tail"),
        marks=[(1, 30, -108, "R"), (2, -66, -150, "L"), (3, -42, -88, "L"), (4, 22, -34, "R"), (6, 52, 30, "R"),
               (7, -70, 20, "L"), (9, 30, 170, "L"), (10, 34, 214, "R"), (11, -72, 80, "L")],
        parts=[("Head", "Wide tabby face with fluffy cheek tufts, forehead stripes and a cream chin.", "head"),
               ("Ear", "Pointed ear with a pink inner ear and cream fur tufts. He has two.", "ear"),
               ("Eyes & brows", "Glossy green eyes with fibre-textured irises, catchlights, lids and lashes.", "eyes"),
               ("Muzzle, nose & whiskers", "Cream muzzle puffs with whisker dots, a shiny pink nose and long whiskers.", "muzzle"),
               ("Mouth & tongue", "Open mouth with fangs and a pink tongue, used when he yells or laughs.", "mouth"),
               ("Torso", "Round body with a cream belly, chest fluff and tiger stripes along the sides.", "torso"),
               ("Arm", "Striped two-bone arm: shoulder, elbow and wrist bend as he moves.", "arm"),
               ("Glove", "White glove with separate fingers, a thumb and a blue cuff.", "glove"),
               ("Leg", "Striped two-bone leg: hip, knee and ankle bend when he walks or runs.", "leg"),
               ("Shoe", "White sneaker with laces, a toe-cap seam and a grey rubber sole.", "foot"),
               ("Tail", "Long striped tail that curls up, with a dark tip.", "tail")])


def mouse():
    import mouse_v2 as C
    return dict(
        name="CHHOTU", role="The Tiny Genius Mouse", color=(130, 110, 105),
        blurb="Small grey mouse in a red cap with big ears, glossy eyes, buck teeth and a pink tail.",
        spec=C.SPEC, assembly=C.ASSEMBLY, char_box=(420, 440, 0, 0),
        annotated=("arm", "leg", "foot"),
        marks=[(1, 30, -48, "R"), (2, -56, -104, "L"), (3, 0, -128, "R"), (4, -32, -72, "L"), (5, 22, -46, "R"),
               (7, 0, 20, "L"), (8, 46, 20, "R"), (10, 16, 100, "L"), (11, 20, 132, "R"), (12, 60, 60, "R")],
        parts=[("Head", "Pear-shaped head with a cream muzzle area and soft pink cheeks.", "head"),
               ("Ear", "Big round ear with a pink inner ear and a fold line. He has two.", "ear"),
               ("Red cap", "His trademark red cap with panel seams, a button and a curved brim.", "cap"),
               ("Eyes & brows", "Large glossy eyes with brown irises, catchlights, lids and lashes.", "eyes"),
               ("Snout, nose & teeth", "Cream muzzle, shiny pink nose, whiskers, a smile and two buck teeth.", "snout"),
               ("Mouth & tongue", "Open mouth with a pink tongue and teeth, used when he laughs.", "mouth"),
               ("Body", "Chubby pear-shaped body with a cream belly.", "body"),
               ("Arm", "Tiny two-part arm: shoulder, elbow and wrist.", "arm"),
               ("Paw", "Small pink paw with three fingers and a thumb.", "paw"),
               ("Leg", "Short two-part leg: hip, knee and ankle.", "leg"),
               ("Foot", "Furry foot with three pink toes.", "foot"),
               ("Tail", "Long thin pink tail with faint rings.", "tail")])


def dog():
    import dog_v2 as C
    return dict(
        name="SHERU", role="The Sleepy Guard Dog", color=(150, 90, 45),
        blurb="Big brown dog with floppy ears, an eye patch, a cream chest and a red collar.",
        spec=C.SPEC, assembly=C.ASSEMBLY, char_box=(380, 420, 0, 20),
        annotated=("front_leg", "hind_leg"),
        marks=[(1, 30, -128, "R"), (2, -84, -80, "L"), (3, 44, -84, "R"), (4, 20, -34, "R"), (6, -80, 0, "L"),
               (7, 0, 30, "R"), (9, 84, 60, "R"), (10, 92, 140, "R")],
        parts=[("Head", "Broad round head with a cream blaze down the forehead and cream cheeks.", "head"),
               ("Floppy ear", "Long dark-brown ear that flops down beside his face.", "ear"),
               ("Eyes & eye patch", "Glossy brown eyes with expressive brows and a dark patch around one eye.", "eyes"),
               ("Snout & nose", "Cream muzzle, big shiny black nose and a soft smile line.", "snout"),
               ("Mouth & tongue", "Open happy mouth with a lolling pink tongue.", "mouth"),
               ("Collar & tag", "Red collar with stitching, rivets and a gold bone-shaped tag.", "collar"),
               ("Body", "Big round sitting body with a cream chest and soft fur.", "body"),
               ("Front leg", "Straight two-bone front leg with a cream sock.", "front_leg"),
               ("Paw (pads)", "Paw seen from below: one big pad and four toe pads.", "paw"),
               ("Hind leg", "Round haunch with a cream foot, used when he sits.", "hind_leg"),
               ("Tail", "Thick fluffy tail with a cream tip that wags when he is happy.", "tail")])


def dadi():
    import dadi_v2 as C
    return dict(
        name="DADI", role="Queen of the Kitchen", color=(40, 150, 95),
        blurb="Grandmother in a green saree with silver hair, round glasses and gold jewellery.",
        spec=C.SPEC, assembly=C.ASSEMBLY, char_box=(420, 660, 0, 40),
        annotated=("arm",),
        marks=[(1, 20, -226, "R"), (2, -34, -152, "L"), (3, 30, -130, "R"), (4, -60, 150, "L"), (5, 14, 40, "R"),
               (6, -68, -10, "L"), (7, -70, 56, "L"), (8, 24, 250, "R")],
        parts=[("Head, hair & bun", "Silver hair with a centre parting, a top bun with a gold pin and gold earrings.", "head"),
               ("Glasses & eyes", "Round gold-framed glasses with glossy lenses over warm brown eyes.", "eyes"),
               ("Face details", "Red bindi, gold nose pin, rosy cheeks, smile lines and a gentle smile.", "face"),
               ("Saree", "Green saree with folded pleats and a golden border at the hem.", "saree"),
               ("Pallu", "Maroon shoulder cloth with a gold border pattern and paisley dots.", "pallu"),
               ("Arm & sleeve", "Maroon sleeve and a two-bone arm with stacked gold bangles.", "arm"),
               ("Hand", "Hand with separate fingers, a gold ring and gold bangles.", "hand"),
               ("Feet", "Bare feet with toes and gold anklets peeking under the saree.", "feet"),
               ("Broom (prop)", "Her favourite weapon: a wooden broom with a bound straw head.", "broom")])


def main():
    names = sys.argv[1:] or ["cat", "mouse", "dog", "dadi"]
    for n in names:
        sheet_v2.make_sheet(globals()[n](), OUT)


if __name__ == "__main__":
    main()
