"""Loads the organs extracted from the Z-Anatomy atlas (../data/anatomy.blend, CC BY-SA 4.0) and fits
them to the MakeHuman character's rest pose with similarity transforms:
  torso groups: atlas hip-centre -> C7 segment mapped onto our hips -> neck joint,
  head groups:  same scale, atlas eye centre moved onto our eye centre,
  leg groups:   atlas hip -> knee (thigh) and knee -> ankle (shin) mapped onto our leg joints.
Every object gets its origin at its own centre so it can be scaled (breathing, heartbeat) in place.
"""
import bpy, os, json
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
TORSO_G = ("lung_l", "lung_r", "heart", "airway", "diaphragm", "ribcage", "spine", "pelvis", "vessels")
HEAD_G = ("skull", "brain")


def _sim(a0, a1, b0, b1):
    """Matrix mapping segment a0->a1 onto b0->b1 (rotation + uniform scale + translation)."""
    va, vb = a1 - a0, b1 - b0
    s = vb.length / va.length
    R = va.rotation_difference(vb).to_matrix().to_4x4()
    return Matrix.Translation(b0) @ R @ Matrix.Scale(s, 4) @ Matrix.Translation(-a0), s


def load(J):
    path = os.path.join(DATA, "anatomy.blend")
    if not os.path.exists(path):
        return {}
    with bpy.data.libraries.load(path) as (src, dst):
        dst.objects = list(src.objects)
    L = {k: Vector(v) for k, v in json.load(open(os.path.join(DATA, "anatomy_landmarks.json"))).items()}
    hips_a = (L["hip_l"] + L["hip_r"]) / 2
    hips_b = (J["l-upper-leg"] + J["r-upper-leg"]) / 2
    Mt, s = _sim(hips_a, L["c7"], hips_b, J["neck"])
    eyes_b = (J["l-eye"] + J["r-eye"]) / 2
    Mh = Matrix.Translation(eyes_b) @ Matrix.Scale(s, 4) @ Matrix.Translation(-L["eyes"])
    out = {}
    for o in dst.objects:
        if o is None:
            continue
        n = o.name.split(".")[0]
        if n in TORSO_G:
            M = Mt
        elif n in HEAD_G:
            M = Mh
        elif n.startswith(("thigh", "shin")):
            side = n[-1]
            if n.startswith("thigh"):
                M, _ = _sim(L[f"hip_{side}"], L[f"knee_{side}"], J[f"{side}-upper-leg"], J[f"{side}-knee"])
            else:
                M, _ = _sim(L[f"knee_{side}"], L[f"ankle_{side}"], J[f"{side}-knee"], J[f"{side}-ankle"])
        else:
            continue
        o.data.transform(M)
        vs = [v.co for v in o.data.vertices]
        c = sum(vs, Vector()) / len(vs)
        o.data.transform(Matrix.Translation(-c))
        bpy.context.collection.objects.link(o)
        o.name = "A_" + n
        o.hide_render = True
        out[n] = (o, c)
    print("ANATOMY loaded", sorted(out), "torso scale", round(s, 3))
    return out
