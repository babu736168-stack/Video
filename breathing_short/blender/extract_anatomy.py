"""One-off: pull the organs this video needs out of the Z-Anatomy atlas (CC BY-SA 4.0, built on
BodyParts3D, CC BY-SA 2.1 JP) into ../data/anatomy.blend, one joined mesh per group, plus
../data/anatomy_landmarks.json (atlas joint centres used to fit the organs to the runner's skeleton).

  python extract_anatomy.py -- /path/to/Z-Anatomy/Startup.blend

Atlas: metres, Z up, body facing -Y, feet at z ~= 0.
"""
import bpy, sys, os, re, json
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.join(HERE, "..", "data"); os.makedirs(OUTD, exist_ok=True)
SRC = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.open_mainfile(filepath=SRC, load_ui=False)
OBJ = bpy.data.objects
LABEL = re.compile(r"\.(j|g|i|t)$|\.o\d?[lr]?$|\.e[lr]$")   # atlas labels, insertion/origin patches


def top_coll(o):
    for c in bpy.context.scene.collection.children:
        if o.name in c.all_objects:
            return c.name
    return ""


def wverts(o):
    dg = bpy.context.evaluated_depsgraph_get()
    e = o.evaluated_get(dg); me = e.to_mesh()
    v = np.array([(o.matrix_world @ x.co)[:] for x in me.vertices]); e.to_mesh_clear()
    return v


def pick(pattern, coll=None, types=("MESH",)):
    rx = re.compile(pattern, re.I)
    return [o for o in OBJ if o.type in types and rx.search(o.name) and not LABEL.search(o.name)
            and (coll is None or top_coll(o).startswith(coll))]


def bbox_center(o):
    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return sum(cs, Vector()) / 8


GROUPS = {
    "lung_l": pick(r"lobe of left lung$", "8"),
    "lung_r": pick(r"lobe of right lung$", "8"),
    "heart": pick(r"^(Right|Left) (atrium|ventricle)$", "5") + pick(r"^Pulmonary trunk$", "5")
             + pick(r"aorta|^Pulmonary (artery|vein)", "5", ("CURVE",)),
    "airway": pick(r"^Trachea$", "8") + pick(r"bronch", "8", ("CURVE", "MESH")),
    "diaphragm": pick(r"^Diaphragm$", "4"),
    "ribcage": pick(r"\brib\.[lr]$|costal cartilage|sternum|xiphoid", "1"),
    "spine": pick(r"^Vertebra |^Sacrum$|^Coccyx|^Intervertebral disc|^Atlas|^Axis", "1"),
    "pelvis": pick(r"^Hip bone\.[lr]$", "1"),
    "skull": [o for o in pick(r".", "1") if bbox_center(o).z > 1.5],
    "vessels": pick(r"aorta|common iliac (artery|vein)|external iliac (artery|vein)|inferior vena cava|superior vena cava", "5", ("CURVE",)),
}
# brain: nervous-system meshes inside the skull, minus eye / ear / nose structures and nerves
skull_v = np.vstack([wverts(o) for o in GROUPS["skull"]])
lo, hi = skull_v.min(0), skull_v.max(0)
NOT_BRAIN = re.compile(r"eye|lens|vitreous|retina|cornea|iris|sclera|choroid|cochle|vestibul|semicircular|tympan|"
                       r"ossicle|malleus|incus|stapes|nasal|olfactory|nerve|ganglion|artery|vein|sinus|meninges|"
                       r"dura|arachnoid|pia|falx|tentorium|pituitary|hypophys|spinal|lacrimal|conjunctiv|eyelid|ciliary", re.I)
GROUPS["brain"] = [o for o in pick(r".", "7") if not NOT_BRAIN.search(o.name)
                   and all(lo[i] < bbox_center(o)[i] < hi[i] for i in range(3)) and bbox_center(o).z > lo[2] + 0.05]
for s, side in (("l", "l"), ("r", "r")):
    GROUPS[f"thighbone_{s}"] = pick(rf"^(Femur|Patella)\.{side}$", "1")
    GROUPS[f"shinbone_{s}"] = pick(rf"^(Tibia|Fibula)\.{side}$", "1")
    GROUPS[f"thighmus_{s}"] = pick(rf"^(Rectus femoris|Vastus (lateralis|medialis|intermedius)|Sartorius|Gracilis|"
                                   rf"Semitendinosus|Semimembranosus|(Long|Short) head of biceps femoris|Adductor (longus|magnus|brevis)|"
                                   rf"Gluteus (maximus|medius)|Tensor fasciae latae)( muscle)?\.{side}$", "4")
    GROUPS[f"shinmus_{s}"] = pick(rf"^((Medial|Lateral) head of gastrocnemius|Soleus muscle|Tibialis anterior muscle|"
                                  rf"Fibularis longus muscle|Extensor digitorum longus muscle)\.{side}$", "4")

# landmarks (joint centres) in atlas space
def centroid(v):
    return v.mean(0)


L = {}
for s in ("l", "r"):
    fv = wverts(OBJ[f"Femur.{s}"]); tv = wverts(OBJ[f"Tibia.{s}"])
    L[f"hip_{s}"] = centroid(fv[fv[:, 2] > fv[:, 2].max() - 0.035]).tolist()          # femoral head
    L[f"knee_{s}"] = ((centroid(fv[fv[:, 2] < fv[:, 2].min() + 0.02]) + centroid(tv[tv[:, 2] > tv[:, 2].max() - 0.02])) / 2).tolist()
    L[f"ankle_{s}"] = centroid(tv[tv[:, 2] < tv[:, 2].min() + 0.02]).tolist()
c7 = OBJ.get("Vertebra C7")
L["c7"] = centroid(wverts(c7)).tolist()
eyes = [o for o in OBJ if o.type == "MESH" and re.match(r"Vitreous body\.[lr]$", o.name)]
L["eyes"] = centroid(np.vstack([centroid(wverts(o))[None] for o in eyes])).tolist()
L["l_eye"] = centroid(wverts(OBJ["Vitreous body.l"])).tolist()

# build joined meshes in a fresh scene
out_objs = []
for gname, objs in GROUPS.items():
    objs = [o for o in dict.fromkeys(objs)]
    meshes = []
    for o in objs:
        dg = bpy.context.evaluated_depsgraph_get()
        e = o.evaluated_get(dg)
        try:
            me = bpy.data.meshes.new_from_object(e, preserve_all_data_layers=False, depsgraph=dg)
        except RuntimeError:
            continue
        if len(me.vertices) == 0:
            continue
        me.transform(o.matrix_world)
        meshes.append(me)
    if not meshes:
        print("EMPTY", gname); continue
    import bmesh
    bm = bmesh.new()
    for me in meshes:
        bm.from_mesh(me)
    me = bpy.data.meshes.new(gname); bm.to_mesh(me); bm.free()
    me.materials.clear()
    ob = bpy.data.objects.new(gname, me)
    if len(me.polygons) > 120000:   # keep render memory sane
        dm = ob.modifiers.new("dec", "DECIMATE"); dm.ratio = 120000 / len(me.polygons)
        bpy.context.scene.collection.objects.link(ob)
        dg = bpy.context.evaluated_depsgraph_get()
        me2 = bpy.data.meshes.new_from_object(ob.evaluated_get(dg)); ob.modifiers.clear(); ob.data = me2
        bpy.context.scene.collection.objects.unlink(ob)
    for p in ob.data.polygons:
        p.use_smooth = True
    out_objs.append(ob)
    print("GROUP", gname, len(objs), "objects ->", len(ob.data.vertices), "verts")

bpy.data.libraries.write(os.path.join(OUTD, "anatomy.blend"), set(out_objs), compress=True)
json.dump(L, open(os.path.join(OUTD, "anatomy_landmarks.json"), "w"), indent=1)
print("LANDMARKS", json.dumps(L))
