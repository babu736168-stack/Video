"""Renders every shot of "Why do you breathe faster when you run?", frame by frame, from ../out/timeline.json.

  python shots.py -- --preview [--us 0.3,0.7] [--only a,b]   # stills -> ../out/preview/<shot>_<u>.png
  python shots.py -- [--only a,b] [--fps 15] [--spp 12] [--scale 0.5]   # -> ../out/frames/<shot>/0000.png

The runner stays at the origin facing -Y while the track texture and trees scroll past. Legs are placed
by a two-bone IK solved here (so the stance foot moves exactly with the ground), arms swing opposite the
legs. X-ray organs are plain objects re-placed every frame from the bone they belong to, so they follow
the run. Two microscopic close-ups (mitochondria, alveoli) are built far away inside dark backdrops.
Already-rendered frames are skipped, so the job can be resumed.
"""
import bpy, sys, os, json, math, time
import numpy as np
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import character as C

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(name, default):
    return type(default)(argv[argv.index(name) + 1]) if name in argv else default
PREVIEW = "--preview" in argv
FPS = arg("--fps", 15)
SPP = arg("--spp", 12)
SCALE = arg("--scale", 0.5)
ONLY = [s for s in arg("--only", "").split(",") if s]
WIDE = arg("--aspect", "16:9") == "16:9"   # landscape by default; --aspect 9:16 for the vertical short
LENS_MUL = float(os.environ.get("LENS_MUL", "1.0"))
FSTOP_MUL = float(os.environ.get("FSTOP_MUL", "0.5"))
OUT = os.path.join(HERE, "..", "out")
TL = json.load(open(os.path.join(OUT, "timeline.json")))

# ----------------------------------------------------------------------------- scene
bpy.ops.wm.read_factory_settings(use_empty=True)
ch = C.build_character()
trk = C.build_track()
J = C.J
body, rig, hair = ch["body"], ch["rig"], ch["hair"]
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"
sc.cycles.samples = SPP; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.05
sc.cycles.use_denoising = True; sc.cycles.max_bounces = 4; sc.cycles.transparent_max_bounces = 16
sc.render.resolution_x, sc.render.resolution_y = (int(1920 * SCALE), int(1080 * SCALE)) if WIDE else (int(1080 * SCALE), int(1920 * SCALE))
sc.render.use_persistent_data = True
sc.view_settings.view_transform = "Filmic"; sc.view_settings.look = "Medium High Contrast"
sc.view_settings.exposure = float(os.environ.get("EXPOSURE", "-0.2"))

# ----------------------------------------------------------------------------- landmarks
V = np.array([v.co[:] for v in body.data.vertices])
eye = np.array(J["l-eye"][:]); EYE_Z = eye[2]
m = (np.abs(V[:, 0]) < 0.004) & (V[:, 2] > EYE_Z - 0.07) & (V[:, 2] < EYE_Z - 0.01)
NOSE = Vector(V[m][V[m][:, 1].argmin()])
m = (np.abs(V[:, 0]) < 0.004) & (V[:, 2] > NOSE.z - 0.065) & (V[:, 2] < NOSE.z - 0.025)
LIPS = Vector(V[m][V[m][:, 1].argmin()])
SP = sorted([k for k in J if k.startswith("spine-")], key=lambda k: J[k].z)
CHEST = J[SP[-1]].copy()
NECK = J["neck"].copy()
HEADC = Vector((0, eye[1] + 0.085, EYE_Z + 0.01))
G = J["ground"].z
LS = 1.0 if J["l-shoulder"].x > 0 else -1.0  # world x sign of the character's left side
LEG = {}
for s in ("l", "r"):
    H, K, A, T = (J[f"{s}-{k}"].copy() for k in ("upper-leg", "knee", "ankle", "foot-1"))
    LEG[s] = dict(H=H, A=A, Lt=(K - H).length, Ls=(A - K).length, FT=T - A, ah=A.z - G)
ARM = {}
for s in ("l", "r"):
    S_, E_, W_, F_ = (J[f"{s}-{k}"].copy() for k in ("shoulder", "elbow", "hand", "hand-3"))
    ARM[s] = dict(Lu=(E_ - S_).length, Lf=(W_ - E_).length, Lh=(F_ - W_).length)
print("LANDMARKS nose", NOSE, "chest", CHEST, "ground", G, "LS", LS,
      {s: (round(LEG[s]["Lt"], 3), round(LEG[s]["Ls"], 3), round(LEG[s]["H"].z - G, 3)) for s in LEG})

# ----------------------------------------------------------------------------- materials / helpers
BLUE, GREY, RED, PINK, GOLD = (0.2, 0.55, 1.0), (0.75, 0.7, 0.85), (1.0, 0.06, 0.04), (1.0, 0.35, 0.45), (1.0, 0.7, 0.1)
GREEN, CYAN, ORANGE = (0.15, 1.0, 0.3), (0.4, 0.85, 1.0), (1.0, 0.4, 0.05)
props = []


def prop(o, mat):
    o.data.materials.clear(); o.data.materials.append(mat)
    o.hide_render = True; props.append(o); return o


def catmull(pts, n=200, closed=False):
    pts = [Vector(p) for p in pts]
    P = ([pts[-1]] + pts + [pts[0], pts[1]]) if closed else ([pts[0]] + pts + [pts[-1]])
    out = []; segs = len(P) - 3; per = max(2, n // segs)
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(per):
            t = k / per
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2] if not closed else out[0])
    return out


def tube(name, pts, r, mat, n=120, closed=False):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = r; cu.bevel_resolution = 3
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY"); dense = catmull(pts, n, closed)
    sp.points.add(len(dense) - 1)
    for p, q in zip(sp.points, dense):
        p.co = (*q, 1)
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o)
    return prop(o, mat), dense


def path_at(dense, s):
    s = min(max(s, 0), 1) * (len(dense) - 1); i = int(s); f = s - i
    return dense[i].lerp(dense[min(i + 1, len(dense) - 1)], f)


def ball(name, r, mat, seg=16):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=seg // 2)
    o = bpy.context.object; o.name = name; bpy.ops.object.shade_smooth()
    return prop(o, mat)


GM = {}


def gm(name, color, strength, alpha, texture=None):
    GM[name] = (color, strength); return C.glow_material(name, color, strength, alpha, texture)


def set_val(mat_name, node, v):
    bpy.data.materials[mat_name].node_tree.nodes[node].outputs[0].default_value = v


def set_col(mat_name, col):
    bpy.data.materials[mat_name].node_tree.nodes["col"].outputs[0].default_value = (*col, 1)


g_air = gm("g_air", (1.0, 0.55, 0.4), 2.5, 0.7)
import anatomy as AN
HAS_ATLAS = os.path.exists(os.path.join(AN.DATA, "anatomy.blend")) and os.environ.get("ATLAS", "1") == "1"
TX = 13.0 if HAS_ATLAS else 1.0
g_lung = gm("g_lung", PINK, 1.5, 0.5, ("cells", 9.0 * TX))
g_bron = gm("g_bron", (1.0, 0.55, 0.4), 5.0, 0.9)
g_spine = gm("g_spine", (0.9, 0.95, 1.0), 1.4, 0.55)
g_heart = gm("g_heart", RED, 4.0, 0.9, ("stripes", 5.0 * TX))
g_dia = gm("g_dia", (1.0, 0.3, 0.12), 2.2, 0.7, ("stripes", 6.0 * TX))
g_rib = gm("g_rib", (0.85, 0.95, 1.0), 1.2, 0.35)
g_brain = gm("g_brain", PINK, 2.2, 0.8)
g_nerve = gm("g_nerve", (1.0, 0.9, 0.4), 3.0, 0.8)
g_sig = gm("g_sig", (1.0, 1.0, 0.6), 25.0, 1.0)
g_mus = gm("g_mus", RED, 2.5, 0.75, ("stripes", 7.0 * TX))
g_atp = gm("g_atp", (1.0, 0.85, 0.2), 6.0, 1.0)
g_o2 = gm("g_o2", BLUE, 3.0, 1.0)
g_co2 = gm("g_co2", GREY, 1.6, 0.95)
g_acid = gm("g_acid", RED, 5.0, 1.0)
g_bic = gm("g_bic", CYAN, 4.0, 1.0)
g_lac = gm("g_lac", GOLD, 5.0, 1.0)
g_art = gm("g_art", RED, 2.2, 0.6)
g_vein = gm("g_vein", (0.25, 0.35, 1.0), 2.2, 0.6)
g_blood = gm("g_blood", RED, 7.0, 1.0)
g_breath = gm("g_breath", (0.85, 0.95, 1.0), 0.5, 0.12)

# ----------------------------------------------------------------------------- organs that follow bones
ORG = {}


def organ(o, bone, loc=(0, 0, 0), scale=(1, 1, 1), rot=None):
    o.location = (0, 0, 0); o.scale = (1, 1, 1)
    ORG[o.name] = dict(o=o, bone=bone, loc=Vector(loc), scale=Vector(scale), k=Vector((1, 1, 1)), off=Vector(),
                       rot=rot.to_quaternion() if rot is not None else None)
    return o


def Wm(bone):
    pb = rig.pose.bones[bone]
    return rig.matrix_world @ pb.matrix @ rig.data.bones[bone].matrix_local.inverted()


def follow():
    bpy.context.view_layer.update()
    for b, l in zip(btrees, lungs):
        b.hide_render = l.hide_render
    for v in spine_parts:
        v.hide_render = not XR[0]
    for d in ORG.values():
        if d["o"].hide_render:
            continue
        s = Vector([a * b for a, b in zip(d["scale"], d["k"])])
        d["o"].matrix_world = Wm(d["bone"]) @ Matrix.LocRotScale(d["loc"] + d["off"], d["rot"], s)


TORSO = SP[0]  # torso organs ride on the lowest spine bone (the lean pivot)
NOSTRIL = NOSE + Vector((0, 0.012, -0.014))
NASO = Vector((0, NOSE.y + 0.085, NOSE.z - 0.008))
TRACH = Vector((0, CHEST.y - 0.04, NECK.z - 0.1))
airway_pts = [NOSTRIL, NOSTRIL + Vector((0, 0.03, 0.012)), Vector((0, NOSE.y + 0.06, NOSE.z + 0.004)), NASO,
              Vector((0, NASO.y + 0.004, LIPS.z - 0.01)), Vector((0, NECK.y - 0.035, NECK.z + 0.01)),
              Vector((0, NECK.y - 0.04, NECK.z - 0.06)), TRACH]
airway, AIR = tube("airway", airway_pts, 0.0075, g_air); organ(airway, "neck")
mouth_pts = [Vector((0, LIPS.y + 0.012, LIPS.z)), Vector((0, LIPS.y + 0.045, LIPS.z + 0.004)),
             Vector((0, NASO.y, LIPS.z - 0.004)), Vector((0, NASO.y + 0.004, LIPS.z - 0.012))]
mouthway, MOUTH = tube("mouthway", mouth_pts, 0.008, g_air); organ(mouthway, "neck")
bronchi = []
for sx in (1, -1):
    o, _ = tube(f"bronch{sx}", [TRACH, Vector((sx * 0.03, CHEST.y - 0.035, NECK.z - 0.125)),
                                Vector((sx * 0.055, CHEST.y - 0.03, NECK.z - 0.16))], 0.005, g_air)
    bronchi.append(organ(o, TORSO))
LUNG_C = [Vector((sx * 0.07, CHEST.y - 0.03, NECK.z - 0.15)) for sx in (1, -1)]
from mathutils import Euler


def shaped(name, mat, fn, seg=48):
    """UV sphere whose unit-sphere vertices are reshaped by fn(Vector) -> Vector."""
    o = ball(name, 1.0, mat, seg)
    for v in o.data.vertices:
        v.co = fn(v.co.copy())
    o.data.update(); return o


def lung_shape(side):
    """Anatomical-ish lung: narrow apex, broad base hollowed by the diaphragm, flat medial face,
    cardiac notch on the heart side. side=+1/-1 is the lung's x side."""
    def f(c):
        x, y, z = c
        r = 0.62 + 0.38 * math.sqrt(max(0.0, (1 - z) / 2)) ** 0.8          # apex taper
        x, y = x * r, y * r
        if x * side < 0:
            x *= 0.6                                                          # flat medial face
        if z < -0.35:
            z += 0.55 * max(0.0, 1 - (x * x + y * y) * 1.6) * (-0.35 - z) / 0.65   # diaphragm hollow
        if side == LS and x * side < 0.1 and y < 0.2 and z < 0.1:
            x += side * 0.35 * math.exp(-((z + 0.45) / 0.35) ** 2)          # cardiac notch
        return Vector((x, y, z))
    return f


def heart_shape(c):
    x, y, z = c
    t = 1 - 0.55 * max(0.0, -z) ** 1.1                                        # taper to the apex
    x, y = x * t, y * t * 0.9
    x += 0.08 * math.sin(3 * math.atan2(y, x)) * (1 - abs(z))                # lumpy chambers
    return Vector((x, y, z))


lungs = [organ(shaped(f"lung{i}", g_lung, lung_shape(1 if i == 0 else -1)), TORSO, c, (0.072, 0.058, 0.11))
         for i, c in enumerate(LUNG_C)]
HEART = Vector((LS * 0.022, CHEST.y - 0.05, NECK.z - 0.19))
heart = organ(shaped("heart", g_heart, heart_shape), TORSO, HEART, (0.034, 0.03, 0.045),
              Euler((math.radians(-25), math.radians(-30 * LS), 0)))
# bronchial trees: recursive branches inside each lung (one curve object per lung)
BR = np.random.default_rng(8)


def bronchial_tree(name, root, d, lc, ls):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 1.0; cu.bevel_resolution = 2

    def inside(p):
        q = p - lc
        return (q.x / ls[0]) ** 2 + (q.y / ls[1]) ** 2 + (q.z / ls[2]) ** 2 < 0.8

    def grow(p, d, length, r, depth):
        e = p + d * length
        if not inside(e):
            e = p + d * length * 0.5
            if not inside(e):
                return
        sp = cu.splines.new("POLY"); sp.points.add(1)
        sp.points[0].co = (*p, 1); sp.points[1].co = (*e, 1)
        sp.points[0].radius = r; sp.points[1].radius = r * 0.75
        if depth == 0:
            return
        for sgn in (1, -1):
            ax = d.cross(Vector(BR.normal(0, 1, 3))).normalized()
            nd = (Matrix.Rotation(math.radians(sgn * BR.uniform(25, 45)), 3, ax) @ d).normalized()
            grow(e, nd, length * BR.uniform(0.62, 0.8), r * 0.72, depth - 1)
    grow(root, d, 0.035, 0.0045, 5)
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o)
    return prop(o, g_bron)


btrees = []
for i, sx in enumerate((1, -1)):
    root = Vector((sx * 0.055, CHEST.y - 0.03, NECK.z - 0.16))
    btrees.append(organ(bronchial_tree(f"btree{i}", root, Vector((sx * 0.5, 0.0, -0.85)).normalized(), LUNG_C[i],
                                       (0.072, 0.058, 0.11)), TORSO))
# x-ray spine: a column of vertebrae from the pelvis to the skull
SPN = [J["pelvis"] + Vector((0, 0.045, -0.02))] + [J[k] + Vector((0, 0.03, 0)) for k in SP] + [NECK + Vector((0, 0.02, 0.04))]
SPN = catmull(SPN, 60)
vert_mesh = None
spine_parts = []
for i in range(22):
    p = path_at(SPN, i / 21)
    o = ball(f"vert{i}", 1.0, g_spine, 12)
    w = 0.016 - 0.005 * i / 21
    spine_parts.append(organ(o, TORSO, p, (w, w * 0.8, 0.0075)))
# diaphragm: a dome under the lungs
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=40, ring_count=20)
dome = bpy.context.object; dome.name = "dome"
import bmesh
bm = bmesh.new(); bm.from_mesh(dome.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.05], context="VERTS"); bm.to_mesh(dome.data); bm.free()
bpy.ops.object.shade_smooth()
DOME = Vector((0, CHEST.y - 0.02, NECK.z - 0.255))
organ(prop(dome, g_dia), TORSO, DOME, (0.14, 0.09, 0.1))
ribs = []
for i in range(7):
    bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.04, major_segments=48, minor_segments=6)
    r = prop(bpy.context.object, g_rib); r.name = f"rib{i}"
    z = NECK.z - 0.07 - i * 0.03
    w = 0.12 + 0.025 * math.sin(math.pi * min(1, i / 4))
    ribs.append(organ(r, TORSO, (0, CHEST.y - 0.01, z), (w, 0.095, 0.11)))
    ORG[r.name]["base_z"] = z
# brain, brainstem, phrenic nerves
brain = ball("brain", 1.0, g_brain, 48)
tex = bpy.data.textures.new("gyri", "VORONOI"); tex.noise_scale = 0.09; tex.distance_metric = "DISTANCE"
brain.modifiers.new("s0", "SUBSURF").levels = 2
dm = brain.modifiers.new("d", "DISPLACE"); dm.texture = tex; dm.strength = -0.12; dm.texture_coords = "LOCAL"
BRAIN = HEADC + Vector((0, 0.01, 0.025))
organ(brain, "head", BRAIN, (0.06, 0.075, 0.05))
STEM = HEADC + Vector((0, 0.025, -0.06))
stem, STEMP = tube("stem", [BRAIN + Vector((0, 0.01, -0.02)), STEM, NECK + Vector((0, 0.035, 0.03))], 0.007, g_nerve)
organ(stem, "neck")
phrenic = []
for sx in (1, -1):
    o, d = tube(f"phren{sx}", [NECK + Vector((0, 0.035, 0.03)), NECK + Vector((sx * 0.02, 0.0, -0.03)),
                               Vector((sx * 0.04, CHEST.y - 0.06, NECK.z - 0.12)),
                               DOME + Vector((sx * 0.06, -0.03, 0.03))], 0.0025, g_nerve)
    phrenic.append((organ(o, TORSO), d))
signals = [ball(f"sig{i}", 0.006, g_sig) for i in range(12)]
# blood vessels: aorta from the heart down to the hips, vein back up in front
AORTA = [HEART + Vector((0, 0.01, 0.03)), HEART + Vector((-LS * 0.01, 0.03, 0.06)), Vector((0, CHEST.y + 0.01, NECK.z - 0.16)),
         Vector((0, CHEST.y + 0.0, J["pelvis"].z + 0.12)), Vector((0, J["pelvis"].y - 0.0, J["pelvis"].z + 0.04))]
aorta, AOR = tube("aorta", AORTA, 0.007, g_art); organ(aorta, TORSO)
VENA = [Vector((-LS * 0.02, J["pelvis"].y - 0.02, J["pelvis"].z + 0.04)), Vector((-LS * 0.015, CHEST.y - 0.02, J["pelvis"].z + 0.12)),
        HEART + Vector((-LS * 0.02, 0.01, -0.03)), HEART]
vena, VEN = tube("vena", VENA, 0.007, g_vein); organ(vena, TORSO)
# leg muscles (+ a thigh artery) riding on the thigh / shin bones
legmus = []; legart = {}
for s in ("l", "r"):
    H, A = LEG[s]["H"], LEG[s]["A"]; K = J[f"{s}-knee"]
    for nm, bone, c, sc_ in (("quad", f"{s}_th", H.lerp(K, 0.5) + Vector((0, -0.035, 0)), (0.036, 0.03, 0.18)),
                             ("ham", f"{s}_th", H.lerp(K, 0.55) + Vector((0, 0.035, 0)), (0.032, 0.028, 0.15)),
                             ("calf", f"{s}_sh", K.lerp(A, 0.3) + Vector((0, 0.03, 0)), (0.028, 0.03, 0.11)),
                             ("shin", f"{s}_sh", K.lerp(A, 0.45) + Vector((0, -0.01, 0)), (0.015, 0.015, 0.13))):
        legmus.append(organ(ball(f"{nm}_{s}", 1.0, g_mus, 24), bone, c, sc_))
    o, d = tube(f"fem_{s}", [Vector((H.x * 0.6, H.y - 0.02, H.z + 0.04)), H + Vector((0, -0.02, -0.05)), H.lerp(K, 0.85) + Vector((0, 0.0, 0))],
                0.0045, g_art)
    legart[s] = (organ(o, f"{s}_th"), d)
MUS_PTS = {s: [J[f"{s}-upper-leg"].lerp(J[f"{s}-knee"], f) + Vector((0, -0.035 if f < 0.5 else 0.035, 0)) for f in (0.3, 0.45, 0.6, 0.7)]
           for s in ("l", "r")}
# ---- real anatomy (Z-Anatomy atlas) replaces the procedural stand-ins when available
skull = None
if HAS_ATLAS:
    ANAT = AN.load(J)
    g_skull = gm("g_skull", (0.85, 0.93, 1.0), 0.5, 0.18)
    g_rib = gm("g_ribs", (0.85, 0.93, 1.0), 0.55, 0.22)
    old = lungs + [heart, dome, brain] + ribs + spine_parts + legmus + bronchi + btrees + [aorta, vena]
    for o in old:
        ORG.pop(o.name, None)
        if o in props:
            props.remove(o)
        o.hide_render = True

    def reg(name, mat, bone):
        o, c = ANAT[name]
        o.data.materials.clear(); o.data.materials.append(mat); props.append(o)
        return organ(o, bone, c)
    lungs = [reg("lung_l", g_lung, TORSO), reg("lung_r", g_lung, TORSO)]
    heart = reg("heart", g_heart, TORSO)
    dome = reg("diaphragm", g_dia, TORSO)
    ribs = [reg("ribcage", g_rib, TORSO)]
    brain = reg("brain", g_brain, "head")
    skull = reg("skull", g_skull, "head")
    bronchi = [reg("airway", g_bron, TORSO)]
    btrees = []
    aorta = vena = reg("vessels", g_art, TORSO)
    legmus = []
    spine_parts = [reg("spine", g_spine, TORSO), reg("pelvis", g_spine, TORSO)]
    for s_ in ("l", "r"):
        legmus += [reg(f"thighmus_{s_}", g_mus, f"{s_}_th"), reg(f"shinmus_{s_}", g_mus, f"{s_}_sh")]
        spine_parts += [reg(f"thighbone_{s_}", g_spine, f"{s_}_th"), reg(f"shinbone_{s_}", g_spine, f"{s_}_sh")]
    spine_parts += ribs + [skull]

# loose particles (positioned in world space every frame)
sparks = [ball(f"atp{i}", 0.006, g_atp, 8) for i in range(40)]
acid = [ball(f"acid{i}", 0.006, g_acid, 8) for i in range(40)]
bic = [ball(f"bic{i}", 0.006, g_bic, 8) for i in range(20)]
bub = [ball(f"co2b{i}", 0.008, g_co2, 10) for i in range(24)]
lac = [ball(f"lac{i}", 0.007, g_lac, 8) for i in range(30)]
cells = [ball(f"cell{i}", 0.006, g_blood, 8) for i in range(30)]
puffs = [ball(f"puff{i}", 0.006, g_o2, 10) for i in range(20)]
breath = [ball(f"breath{i}", 0.03, g_breath, 16) for i in range(10)]
RNG = np.random.default_rng(3)
JIT = [Vector(RNG.normal(0, 1, 3)) for _ in range(60)]

# ----------------------------------------------------------------------------- microscopic sets
def backdrop(name, center, r, c_in, c_out):
    o = ball(name, r, C.glow_material(name + "_m", c_in, 1.0, 1.0), 48)
    nt = o.data.materials[0].node_tree
    # gradient: brighter behind the subject
    o.location = center; o.hide_render = True
    lw = next(n for n in nt.nodes if n.type == "LAYER_WEIGHT")
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*c_out, 1); mix.inputs["B"].default_value = (*c_in, 1)
    nt.links.new(lw.outputs["Facing"], mix.inputs["Factor"])
    em = next(n for n in nt.nodes if n.type == "EMISSION"); nt.links.new(mix.outputs["Result"], em.inputs["Color"])
    return o


def banded(name, c1, c2, scale, strength, alpha):
    """Emissive material with wavy bands (mitochondrial cristae / muscle striations)."""
    m = C.glow_material(name, c1, strength, alpha); nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    w = nt.nodes.new("ShaderNodeTexWave"); w.inputs["Scale"].default_value = scale; w.inputs["Distortion"].default_value = 6
    w.inputs["Detail"].default_value = 2
    nt.links.new(tc.outputs["Object"], w.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*c1, 1); mix.inputs["B"].default_value = (*c2, 1)
    nt.links.new(w.outputs["Fac"], mix.inputs["Factor"])
    em = next(n for n in nt.nodes if n.type == "EMISSION"); nt.links.new(mix.outputs["Result"], em.inputs["Color"])
    return m


UPL = os.environ.get("UPLOADS", "/root/.claude/uploads/32770705-7d9b-5f9f-9b3a-9f911fd69f71/")
PLATES = os.path.join(HERE, "..", "plates")


def image_plane(name, img, center, width, aspect, strength=0.8):
    """Out-of-focus background plate made from one of the user's images (emissive, faces -Y)."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=center, rotation=(math.pi / 2, 0, 0))
    o = bpy.context.object; o.name = name; o.scale = (width, width / aspect, 1)
    m, nt, out = C._nodes(name + "_m")
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(img); tx.extension = "EXTEND"
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = strength
    nt.links.new(tx.outputs["Color"], em.inputs["Color"]); nt.links.new(em.outputs[0], out.inputs["Surface"])
    o.data.materials.append(m); o.hide_render = True; props.append(o)
    return o


MC = Vector((80, 0, 6))  # mitochondria set
micro_m = [backdrop("bd_m", MC, 6, (0.25, 0.02, 0.04), (0.02, 0.0, 0.01))]
if os.path.exists(os.path.join(PLATES, "cell.png")):
    micro_m.append(image_plane("plate_m", os.path.join(PLATES, "cell.png"), MC + Vector((0, 2.6, 0)), 10, 16 / 9, 0.55))
fib_mat = banded("fiber", (0.6, 0.06, 0.08), (0.25, 0.01, 0.03), 4.0, 0.5, 0.8)
for i in range(6):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=12, location=MC + Vector((0, 1.2 + (i % 2) * 0.5, -1.4 + i * 0.55)),
                                        rotation=(0, math.pi / 2, 0), vertices=32)
    o = bpy.context.object; bpy.ops.object.shade_smooth(); micro_m.append(prop(o, fib_mat))
mito_mat = banded("mito", (1.0, 0.45, 0.08), (0.5, 0.08, 0.02), 9.0, 3.0, 0.95)
MITO = []
for i, (p, rot) in enumerate([((-0.3, 0.2, 0.15), 0.3), ((0.55, 0.35, -0.3), -0.5), ((-0.9, 0.6, -0.45), 0.9),
                              ((0.9, 0.7, 0.5), 0.2), ((0.15, 0.9, 0.75), -0.8), ((-1.2, 1.0, 0.6), -0.2)]):
    o = ball(f"mito{i}", 1.0, mito_mat, 32); o.location = MC + Vector(p); o.scale = (0.42, 0.2, 0.2)
    o.rotation_euler = (0, rot, rot * 0.5); micro_m.append(o); MITO.append(MC + Vector(p))
o2m = [ball(f"o2m{i}", 0.04, g_o2, 10) for i in range(30)]
co2m = [ball(f"co2m{i}", 0.045, g_co2, 10) for i in range(24)]
atpm = [ball(f"atpm{i}", 0.025, g_atp, 8) for i in range(50)]

AC = Vector((80, 30, 6))  # alveoli set
micro_a = [backdrop("bd_a", AC, 6, (0.18, 0.05, 0.12), (0.01, 0.0, 0.02))]
if os.path.exists(os.path.join(PLATES, "alveoli.png")):
    micro_a.append(image_plane("plate_a", os.path.join(PLATES, "alveoli.png"), AC + Vector((0, 2.6, 0)), 9, 16 / 9, 0.5))
alv_mat = C.glow_material("alv", (1.0, 0.45, 0.55), 1.3, 0.45)
ALV = []
for i in range(9):
    a = i / 9 * 2 * math.pi; ring = 0.55 if i < 6 else 0.0
    p = AC + Vector((math.cos(a) * ring * (1 if i < 6 else 0) + (i - 7) * 0.35 * (i >= 6), 0.15 * math.sin(a * 2),
                     math.sin(a) * ring * 0.8 + (0.15 if i >= 6 else 0)))
    if i >= 6:
        p = AC + Vector(((i - 7) * 0.45, 0.35, 0.05))
    o = ball(f"alv{i}", 0.36 + 0.06 * math.sin(i * 1.7), alv_mat, 32); o.location = p; micro_a.append(o); ALV.append((p, 0.36 + 0.06 * math.sin(i * 1.7)))
bron, BRON = tube("bronchiole", [AC + Vector((0, 0.3, 2.5)), AC + Vector((0.1, 0.25, 1.4)), AC + Vector((0, 0.15, 0.6))], 0.16, alv_mat)
micro_a.append(bron)
cap_art = C.glow_material("cap_art", (1.0, 0.1, 0.08), 2.5, 0.85)
cap_vein = C.glow_material("cap_vein", (0.35, 0.3, 1.0), 2.5, 0.85)
CAPS = []
for i, (p, r) in enumerate(ALV[:6]):
    pts = []
    for k in range(7):
        a = k / 6 * math.pi * 1.4 - 0.7 * math.pi + i
        pts.append(p + Vector((math.cos(a) * (r + 0.03), -r * 0.55, math.sin(a) * (r + 0.03))))
    o, d = tube(f"cap{i}", pts, 0.03, cap_art if i % 2 else cap_vein, 80)
    micro_a.append(o); CAPS.append(d)
rbc = [ball(f"rbc{i}", 0.05, cap_art, 12) for i in range(36)]
for o in rbc:
    o.scale = (1, 0.45, 1)
o2a = [ball(f"o2a{i}", 0.04, g_o2, 10) for i in range(24)]
co2a = [ball(f"co2a{i}", 0.045, g_co2, 10) for i in range(24)]

# ----------------------------------------------------------------------------- camera
bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam
cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 24.0
cam.data.dof.use_dof = True; cam.data.clip_end = 400


SHOT_LENS = {} if os.environ.get("CAMS", "v3") == "v3" else (dict(intro=0.85, muscles=0.8, mito=1.25, brain=0.85, alveoli=1.8, buffer=0.85, trained=1.15) if WIDE else {})
CUR = None


def look(loc, tgt, lens, fstop=4.0, roll=0.0, shake=0.0, t=0.0):
    loc, tgt = Vector(loc), Vector(tgt)
    if shake:
        loc = loc + Vector((math.sin(t * 13.1) * 0.6 + math.sin(t * 29.3) * 0.4, 0,
                            math.sin(t * 17.7) * 0.6 + math.sin(t * 23.9) * 0.4)) * shake
    cam.location = loc
    cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
    cam.rotation_euler.rotate_axis("Z", math.radians(roll))
    cam.data.lens = lens * LENS_MUL * SHOT_LENS.get(CUR, 1.0); cam.data.dof.focus_distance = (tgt - loc).length; cam.data.dof.aperture_fstop = fstop * FSTOP_MUL


def L(a, b, u):
    return Vector(a).lerp(Vector(b), u) if not isinstance(a, (int, float)) else a + (b - a) * u


def ez(u):
    u = min(max(u, 0), 1); return u * u * (3 - 2 * u)


def win(u, a, b):
    return ez((u - a) / (b - a)) if b > a else float(u >= a)


def pulse(x, w):
    return math.exp(-(x / w) ** 2)


# ----------------------------------------------------------------------------- posing
MATS = [m for m in bpy.data.materials]
REST_X = {b.name: (b.matrix_local.to_3x3() @ Vector((1, 0, 0))) for b in rig.data.bones}


XR = [False]


_WBG = bpy.context.scene.world.node_tree.nodes["Background"].inputs["Strength"]
_W0 = _WBG.default_value; _SUN = bpy.data.objects["sun"].data; _S0 = _SUN.energy
XR_DIM = float(os.environ.get("XR_DIM", "0.9"))


def xray(v):
    """v: 0 normal .. 1 full x-ray. The world dims as the body turns to glass, so the glowing anatomy
    becomes the light source of the frame (medical-visualisation look)."""
    _WBG.default_value = _W0 * (1 - XR_DIM * v); _SUN.energy = _S0 * (1 - XR_DIM * v)
    XR[0] = v > 0.3
    for mt in MATS:
        n = mt.node_tree.nodes.get("xray") if mt.node_tree else None
        if n:
            n.outputs[0].default_value = v
    for k in ("hair",):
        ch["objs"][k].hide_render = v > 0.3
    for k in ("helper-upper-teeth", "helper-lower-teeth", "helper-tongue", "brow1", "brow-1"):
        ch["objs"][k].hide_render = v > 0.3


FIST = float(os.environ.get("FIST", "-60"))
THUMB = float(os.environ.get("THUMB", "1.0"))   # finger curl per joint (deg); thumb curls less


def fist(deg):
    for s in ("l", "r"):
        for f in range(1, 6):
            for k in range(1, 4):
                pb = rig.pose.bones.get(f"{s}_f{f}{k}")
                if pb:
                    a = deg * (THUMB if f == 1 else 1.0) * (0.8 if k == 1 else 1.0)
                    pb.rotation_euler = (math.radians(a), 0, 0)


def pose(rot):
    for pb in rig.pose.bones:
        pb.rotation_mode = "XYZ"; pb.rotation_euler = (0, 0, 0); pb.location = (0, 0, 0)
    fist(FIST)
    for k, (x, y, z) in rot.items():
        rig.pose.bones[k].rotation_euler = (math.radians(x), math.radians(y), math.radians(z))


def aim(pb, target, ref=None):
    """Points pose bone pb (its Y axis) at target (armature space), keeping its posed head and roll."""
    bpy.context.view_layer.update()
    head = pb.head.copy()
    y = (Vector(target) - head).normalized()
    r = Vector(ref) if ref is not None else REST_X[pb.name]
    x = (r - y * r.dot(y)).normalized(); z = x.cross(y)
    M = Matrix((x, y, z)).transposed().to_4x4(); M.translation = head
    pb.matrix = M


FOOT_KEYS = [(0.0, -0.24, 0.0), (0.2, 0.0, 0.0), (0.4, 0.26, 0.02), (0.55, 0.30, 0.24),
             (0.72, 0.02, 0.32), (0.87, -0.28, 0.13)]


def foot_curve(ph):
    ph %= 1.0; n = len(FOOT_KEYS)
    i = max(k for k in range(n) if FOOT_KEYS[k][0] <= ph)
    t0 = FOOT_KEYS[i][0]; t1 = FOOT_KEYS[(i + 1) % n][0] + (1.0 if i + 1 == n else 0)
    t = (ph - t0) / (t1 - t0)
    P = [Vector(FOOT_KEYS[(i + d) % n][1:]) for d in (-1, 0, 1, 2)]
    p0, p1, p2, p3 = P
    q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
    if i < 2:  # stance: exactly linear so the foot stays planted on the moving ground
        q = Vector((L(FOOT_KEYS[i][1], FOOT_KEYS[i + 1][1], t), L(FOOT_KEYS[i][2], FOOT_KEYS[i + 1][2], t)))
    return q.x, max(0.0, q.y)


def foot_pitch(ph):
    ph %= 1.0
    if ph < 0.25:
        return 0.0
    if ph < 0.5:
        return 55 * ez((ph - 0.25) / 0.25)
    if ph < 0.8:
        return L(55, -5, ez((ph - 0.5) / 0.3))
    return L(-5, 0, ez((ph - 0.8) / 0.2))


GAITS = dict(jog=dict(P=0.72, stride=1.0, lift=1.0, lean=7, arm=28, bob=0.025),
             sprint=dict(P=0.56, stride=1.3, lift=1.45, lean=12, arm=34, bob=0.035),
             easy=dict(P=0.76, stride=0.9, lift=0.85, lean=5, arm=26, bob=0.02))


def gait_speed(g):
    return 0.5 * g["stride"] / (0.4 * g["P"])


def leg(s, ph, g, k):
    d = LEG[s]; pt, ps, pf = (rig.pose.bones[f"{s}_{b}"] for b in ("th", "sh", "ft"))
    bpy.context.view_layer.update()
    H = pt.head.copy()
    y, z = foot_curve(ph)
    y *= g["stride"]; z *= g["lift"]
    bob = rig.location.z
    A = Vector((d["A"].x, d["A"].y + y * k, G + d["ah"] + z * k - bob))
    v = A - H; dist = min(v.length, 0.998 * (d["Lt"] + d["Ls"])); dn = v.normalized()
    A = H + dn * dist
    ca = (d["Lt"] ** 2 + dist ** 2 - d["Ls"] ** 2) / (2 * d["Lt"] * dist)
    a = math.acos(max(-1, min(1, ca)))
    f = Vector((0, -1, 0)); n = (f - dn * dn.dot(f)).normalized()
    K = H + d["Lt"] * (math.cos(a) * dn + math.sin(a) * n)
    aim(pt, K, (1, 0, 0)); aim(ps, A, (1, 0, 0))
    p = math.radians(foot_pitch(ph) * k)
    FT = d["FT"]
    toe = A + Vector((FT.x, FT.y * math.cos(p) - FT.z * math.sin(p), FT.y * math.sin(p) + FT.z * math.cos(p)))
    aim(pf, toe, (1, 0, 0))


_AR = os.environ.get("ARMREF", "x,y,y").split(",")
ARMREF = [None if a == "rest" else ((1, 0, 0) if a == "x" else (0, 0, 1) if a == "z" else (0, -1, 0)) for a in _AR]


def arm(s, swing, flex, out=0.12, inward=0.25, k=1.0):
    """swing: upper-arm angle forward (deg); flex: elbow bend (deg)."""
    d = ARM[s]; side = LS if s == "l" else -LS
    pu, pf_, ph = (rig.pose.bones[f"{s}_{b}"] for b in ("up", "fa", "hand"))
    bpy.context.view_layer.update()
    S = pu.head.copy()
    a = math.radians(swing); b = math.radians(swing + flex)
    ud = Vector((side * out, -math.sin(a), -math.cos(a))).normalized()
    E = S + ud * d["Lu"]
    fd = Vector((-side * inward, -math.sin(b), -math.cos(b))).normalized()
    W = E + fd * d["Lf"]
    F = W + (fd + Vector((0, 0, -0.35))).normalized() * d["Lh"]
    E0, W0, F0 = pu.tail.copy(), pf_.tail.copy(), ph.tail.copy()
    aim(pu, E0.lerp(E, k), ARMREF[0]); aim(pf_, W0.lerp(W, k), ARMREF[1]); aim(ph, F0.lerp(F, k), ARMREF[2])


def arm_pts(s, E, W, F):
    pu, pf_, ph = (rig.pose.bones[f"{s}_{b}"] for b in ("up", "fa", "hand"))
    aim(pu, E, (1, 0, 0)); aim(pf_, W, (1, 0, 0)); aim(ph, F, (1, 0, 0))


def breathe_jaw(t, rate, amt):
    return amt * (0.55 + 0.45 * math.sin(2 * math.pi * rate * t))


def run(T, gait="jog", k=1.0, jaw=6.0, head=0.0, breath_rate=1.4):
    """Poses the runner at global time T (s); k blends from standing (0) to full stride (1)."""
    g = GAITS[gait]; ph = (T / g["P"]) % 1.0
    tw = 4 * math.sin(2 * math.pi * ph) * k
    rig.location = (0, 0, -g["bob"] * k * (0.5 + 0.5 * math.cos(4 * math.pi * (ph - 0.2))))
    pose({SP[0]: (g["lean"] * k, 0, 0), SP[-1]: (0, tw, 0), "neck": (0, -tw * 0.5, 0),
          "head": (-g["lean"] * 0.7 * k + head, 0, 0), "jaw": (breathe_jaw(T, breath_rate, jaw), 0, 0)})
    leg("l", ph, g, k); leg("r", ph + 0.5, g, k)
    sw = g["arm"] * k
    arm("l", -sw * math.cos(2 * math.pi * ph) + 8, 75 + 10 * k, k=1.0)
    arm("r", -sw * math.cos(2 * math.pi * (ph + 0.5)) + 8, 75 + 10 * k, k=1.0)
    return ph


# ----------------------------------------------------------------------------- motion capture run
# Real running from the CMU motion-capture database, retargeted by bone DIRECTIONS (so the runner keeps
# his own proportions), hips from the capture, feet put back on the ground every frame.
MOCAP = os.environ.get("MOCAP", "1") == "1"
if MOCAP:
    import mocap as MC_
    _MD = os.path.join(HERE, "..", "data", "mocap")
    CLIPS = dict(jog="16_35", sprint="16_45", easy="16_36")
    CYC = {}
    _our_leg = LEG["l"]["Lt"] + LEG["l"]["Ls"]
    for gname, f in CLIPS.items():
        cyc = MC_.cycle(MC_.load(os.path.join(_MD, f + ".bvh")))
        _q = cyc["Q"]; _i = cyc["idx"]
        cyc["ah"] = float(np.percentile(np.minimum(_q[:, _i["LeftFoot"], 2], _q[:, _i["RightFoot"], 2]), 3))
        cyc["th"] = float(np.percentile(np.minimum(_q[:, _i["LeftToeBase"], 2], _q[:, _i["RightToeBase"], 2]), 3))
        CYC[gname] = cyc
        GAITS[gname]["speed"] = cyc["speed"] * _our_leg / 0.86
        GAITS[gname]["P"] = cyc["period"]
    _sgn = 1.0 if LS > 0 else -1.0    # mocap "Left" is at +X after facing -Y
    BMAP = {}
    for s, side in (("l", "Left"), ("r", "Right")):
        BMAP[f"{s}_up"] = (f"{side}Arm", f"{side}ForeArm")
        BMAP[f"{s}_fa"] = (f"{side}ForeArm", f"{side}Hand")
        BMAP[f"{s}_hand"] = (f"{side}Hand", f"{side}HandIndex1")
        BMAP[f"{s}_th"] = (f"{side}UpLeg", f"{side}Leg")
        BMAP[f"{s}_sh"] = (f"{side}Leg", f"{side}Foot")
        BMAP[f"{s}_ft"] = (f"{side}Foot", f"{side}ToeBase")
    _spine = ["pelvis"] + SP
    REST_DIR = {b.name: (b.tail_local - b.head_local).normalized() for b in rig.data.bones}
    REST_LEN = {b.name: b.length for b in rig.data.bones}


def gait_speed(g):
    return g["speed"] if "speed" in g else 0.5 * g["stride"] / (0.4 * g["P"])


def _mc(Q, ix, name):
    v = Q[ix[name]]
    return Vector((v[0] * _sgn, v[1], v[2]))


def run_mocap(T, gait="jog", k=1.0, jaw=6.0, head=0.0, breath_rate=1.4):
    cyc = CYC[gait]; ix = cyc["idx"]
    sc_ = _our_leg / 0.86
    Q = MC_.sample(cyc, T) * sc_
    P = lambda n: _mc(Q, ix, n)
    pose({})
    rest_hips = (J["l-upper-leg"] + J["r-upper-leg"]) / 2
    mh = (P("LeftUpLeg") + P("RightUpLeg")) / 2
    mh.z += G
    rig.location = (rest_hips.lerp(mh, k) - rest_hips)

    def aim_dir(bn, d, ref):
        pb = rig.pose.bones[bn]
        d = REST_DIR[bn].lerp(d.normalized(), k).normalized()
        bpy.context.view_layer.update()
        aim(pb, pb.head + d * REST_LEN[bn], ref)

    # torso: lower half of the spine chain follows Hips->Spine, upper half Spine->Neck; twist from hips/shoulders
    hipline = (P("LeftUpLeg") - P("RightUpLeg")) * LS
    shline = (P("LeftArm") - P("RightArm")) * LS
    low = P("Spine") - P("Hips"); up = P("Neck") - P("Spine")
    for i, bn in enumerate(_spine):
        f = i / max(1, len(_spine) - 1)
        aim_dir(bn, low.lerp(up, f), hipline.lerp(shline, f).normalized() * LS)
    aim_dir("neck", P("Head") - P("Neck"), shline.normalized() * LS)
    hd = P("Head_end") - P("Head") if "Head_end" in ix else up
    aim_dir("head", hd, shline.normalized() * LS)
    rig.pose.bones["head"].rotation_euler.x += math.radians(head)
    for bn, (a, b) in BMAP.items():
        if bn.endswith("_hand"):     # firm wrist: mostly in line with the forearm, slight drop
            fa = P(BMAP[bn.replace("_hand", "_fa")][1]) - P(BMAP[bn.replace("_hand", "_fa")][0])
            aim_dir(bn, fa.normalized() * 0.85 + (P(b) - P(a)).normalized() * 0.15 + Vector((0, 0, -0.12)),
                    ARMREF[2])
            continue
        if bn.endswith(("_th", "_sh", "_ft")):
            ref = (1, 0, 0)
        elif bn.endswith("_clav"):
            ref = None
        else:
            ref = ARMREF[{"up": 0, "fa": 1, "hand": 2}[bn.split("_")[1]]]
        aim_dir(bn, P(b) - P(a), ref)
    fist(FIST)
    rig.pose.bones["jaw"].rotation_mode = "XYZ"
    rig.pose.bones["jaw"].rotation_euler = (math.radians(breathe_jaw(T, breath_rate, jaw)), 0, 0)
    # feet on the ground: our heel/toe "contact height" matches the capture's at every frame
    bpy.context.view_layer.update()
    def ours(s_):
        pf = rig.pose.bones[f"{s_}_ft"]
        return min((rig.matrix_world @ pf.head).z - J[f"{s_}-ankle"].z, (rig.matrix_world @ pf.tail).z - J[f"{s_}-foot-1"].z)
    def theirs(side):
        return min(P(f"{side}Foot").z - cyc["ah"] * sc_, P(f"{side}ToeBase").z - cyc["th"] * sc_)
    c_o = min(ours("l"), ours("r")); c_t = min(theirs("Left"), theirs("Right"))
    rig.location.z += (max(c_t, 0.0) - c_o) * k + (1 - k) * 0
    return (T / cyc["period"]) % 1.0


if MOCAP:
    run = run_mocap


def scroll(dist):
    trk["scroll"].outputs[0].default_value = -dist
    for o, y0 in trk["movers"]:
        o.location.y = ((y0 + dist + 70) % 140) - 70


def reset():
    for p in props:
        p.hide_render = True
    xray(0.0)
    for k, (c, s) in GM.items():
        set_val(k, "strength", s); set_col(k, c)
    set_val("skin", "flush", 0.0)
    bpy.data.materials["g_lung"].node_tree.nodes["alpha"].inputs["Fac"].default_value = 0.5
    for d in ORG.values():
        d["k"] = Vector((1, 1, 1)); d["off"] = Vector()
    rig.location = (0, 0, 0)
    pose({})


def show(*objs):
    for o in objs:
        o.hide_render = False


def wpos(bone, p):
    return Wm(bone) @ Vector(p)


def breath_cycle(T, rate):
    """0..1 lung fill for a breathing rate in breaths/s."""
    return 0.5 - 0.5 * math.cos(2 * math.pi * rate * T)


def lungs_fill(f, depth=1.0):
    for l in lungs:
        ORG[l.name]["k"] = Vector((1 + 0.12 * f * depth, 1 + 0.12 * f * depth, 1 + 0.22 * f * depth))
        ORG[l.name]["off"] = Vector((0, 0, -0.012 * f * depth))
    ORG[dome.name]["off"] = Vector((0, 0, -0.03 * f * depth)); ORG[dome.name]["k"] = Vector((1 + 0.05 * f * depth, 1, 1 - 0.45 * f * depth))
    for r in ribs:
        ORG[r.name]["k"] = Vector((1 + 0.06 * f * depth, 1 + 0.08 * f * depth, 1))


def heartbeat(T, bpm):
    ph = (T * bpm / 60) % 1.0
    return pulse(ph - 0.08, 0.06) + 0.6 * pulse(ph - 0.3, 0.06)


# ----------------------------------------------------------------------------- shots
FACE = Vector((0, LIPS.y + 0.02, (EYE_Z + LIPS.z) / 2))
HIPZ = J["pelvis"].z


def s_intro(u, t, T):
    g = GAITS["jog"]; run(T, "jog", jaw=10 * win(u, 0.3, 0.8) + 3, breath_rate=1.6); scroll(T * gait_speed(g))
    c = Vector((0, 0, HIPZ + 0.35))
    look(L(c + Vector((0.9, -3.0, 0.1)), c + Vector((0.55, -1.9, 0.25)), ez(u)), c + Vector((0, 0, 0.15 * u)),
         L(40, 48, u), 2.8, roll=L(-3, 2, u), shake=0.006, t=t)


def s_muscles(u, t, T):
    g = GAITS["jog"]; ph = run(T, "jog", jaw=8); scroll(T * gait_speed(g))
    xray(0.75 * win(u, 0.0, 0.2)); show(*legmus)
    set_val("g_mus", "strength", 2.0 + 2.5 * win(u, 0.15, 0.5))
    follow()
    # ATP sparks burst off the working muscles each stride and burn out
    for i, sp in enumerate(sparks):
        s = "l" if i % 2 else "r"
        life = ((T * 2.6 + i * 0.137) % 1.0)
        if u < 0.25:
            continue
        base = wpos(f"{s}_th", MUS_PTS[s][i % 4])
        sp.hide_render = False
        sp.location = base + JIT[i] * (0.015 + 0.06 * life)
        sp.scale = (1.4 * (1 - life),) * 3
    c = Vector((0, 0, HIPZ - 0.15))
    look(L(c + Vector((2.3, -0.9, -0.1)), c + Vector((1.8, -0.65, -0.05)), ez(u)), c, 38, 3.5, roll=-2, shake=0.004, t=t)


def s_mito(u, t, T):
    show(*micro_m)
    for i, o in enumerate(o2m):  # oxygen streams in from the left to the mitochondria
        s = (u * 1.6 + i * 0.071) % 1.0
        tgt = MITO[i % len(MITO)]
        start = MC + Vector((-3.2, 0.2 + (i % 5) * 0.15, -1.2 + (i % 7) * 0.4))
        o.hide_render = False; o.location = start.lerp(tgt, ez(s)) + JIT[i] * 0.05 * (1 - s)
        o.scale = (1 - 0.6 * s * s,) * 3
    for i, o in enumerate(co2m):  # carbon dioxide drifts out to the upper right
        if u < 0.35:
            continue
        s = ((u - 0.35) * 1.7 + i * 0.083) % 1.0
        src = MITO[(i * 3) % len(MITO)]
        o.hide_render = False; o.location = src.lerp(MC + Vector((3.0, 0.3, 1.8)) + JIT[i] * 0.6, ez(s))
    for i, o in enumerate(atpm):  # ATP sparks
        life = (t * 1.8 + i * 0.061) % 1.0
        o.hide_render = False; o.location = MITO[i % len(MITO)] + JIT[i].normalized() * (0.25 + 0.7 * life)
        o.scale = (1.3 * (1 - life),) * 3
    set_val("mito", "strength", 2.5 + 1.5 * (0.5 + 0.5 * math.sin(t * 6)))
    c = MC + Vector((0, 0.4, 0.1))
    look(L(c + Vector((0.4, -4.4, 0.5)), c + Vector((-0.1, -3.0, 0.2)), ez(u)), c, 32, 2.8, roll=L(4, -2, u), shake=0.01, t=t)


def signal_run(u0, u, speed=1.2):
    """Bright pulses: brain -> brainstem -> phrenic nerves -> diaphragm. Returns arrival flash 0..1."""
    stemw = [wpos("neck", p) for p in STEMP]
    phw = [[wpos(TORSO, p) for p in d] for _, d in phrenic]
    s = (u - u0) * speed
    for i, o in enumerate(signals):
        si = s - (i % 6) * 0.03
        if si < 0 or si > 1:
            continue
        o.hide_render = False
        o.location = path_at(stemw, si / 0.35) if si < 0.35 else path_at(phw[i // 6], (si - 0.35) / 0.65)
    return pulse(s - 1.0, 0.08)


def s_brain(u, t, T):
    k = win(u, 0.35, 0.75)
    g = GAITS["jog"]; run(T, "jog", k=k, jaw=6); scroll(T * gait_speed(g) * k)
    xray(0.7); show(brain, stem, *[o for o, _ in phrenic], airway, *lungs, dome, *bronchi)
    set_val("g_brain", "strength", 2.2 + 12 * pulse(u - 0.3, 0.08))
    fl = signal_run(0.32, u, 1.3)
    set_val("g_dia", "strength", 2.5 + 15 * fl)
    lungs_fill(breath_cycle(T, 0.5 + 0.6 * k), 0.5 + 0.7 * k)
    follow()
    c = Vector((0, NECK.y - 0.02, NECK.z - 0.02))
    look(L(c + Vector((-0.45, -1.2, 0.3)), c + Vector((-0.3, -0.85, 0.1)), ez(u)), L(HEADC, c + Vector((0, 0, -0.1)), ez(u)),
         38, 4.0, roll=4, shake=0.003, t=t)


def s_diaphragm(u, t, T):
    g = GAITS["jog"]; run(T, "jog", jaw=10, breath_rate=0.8); scroll(T * gait_speed(g))
    xray(0.8); show(*lungs, dome, *ribs, airway, *bronchi, *[o for o, _ in phrenic])
    f = breath_cycle(T, 0.8)
    lungs_fill(f, 1.3)
    set_val("g_dia", "strength", 2.5 + 4 * f); set_val("g_lung", "strength", 1.4 + 1.2 * f)
    follow()
    # air puffs rush down the airway on the inhale, up on the exhale
    air = [wpos("neck", p) for p in AIR]
    infl = math.sin(2 * math.pi * 0.8 * T)
    for i, p in enumerate(puffs[:12]):
        s = ((T * 1.6 + i / 12) % 1.0)
        p.hide_render = False; p.location = path_at(air, s if infl > 0 else 1 - s); p.scale = (0.8,) * 3
    c = Vector((0, CHEST.y - 0.05, NECK.z - 0.17))
    look(L(c + Vector((0.3, -1.0, 0.05)), c + Vector((0.18, -0.75, 0.0)), ez(u)), c, 36, 5.6, roll=-3, shake=0.003, t=t)


def s_alveoli(u, t, T):
    show(*micro_a)
    caps = CAPS
    for i, o in enumerate(rbc):  # red blood cells flow through the capillaries
        d = caps[i % len(caps)]; s = (t * 0.35 + i * 0.173) % 1.0
        o.hide_render = False; o.location = path_at(d, s)
    for i, o in enumerate(o2a):  # oxygen: from inside each alveolus out into its capillary
        p, r = ALV[i % 6]; s = (u * 2.0 + i * 0.09) % 1.0
        tgt = path_at(caps[i % 6], 0.3 + 0.4 * ((i * 7) % 10) / 10)
        o.hide_render = False; o.location = (p + JIT[i] * 0.12).lerp(tgt, ez(s)); o.scale = (1.0 - 0.5 * s,) * 3
    for i, o in enumerate(co2a):  # carbon dioxide: out of the capillaries, up the airway
        if u < 0.4:
            continue
        s = ((u - 0.4) * 1.8 + i * 0.08) % 1.0
        src = path_at(caps[(i + 3) % 6], 0.5)
        tgt = BRON[min(len(BRON) - 1, int(len(BRON) * (0.2 + 0.3 * s)))] if False else AC + Vector((0.05, 0.2, 2.6))
        o.hide_render = False
        o.location = src.lerp(AC + Vector((0, 0.15, 0.6)), ez(min(1, s * 2))).lerp(tgt, ez(max(0, s * 2 - 1)))
    for i, (p, r) in enumerate(ALV):  # gentle inflate / deflate
        f = 1 + 0.06 * math.sin(2 * math.pi * 0.8 * t + i * 0.3)
        bpy.data.objects[f"alv{i}"].scale = (f,) * 3
    c = AC + Vector((0, 0, 0.25))
    look(L(c + Vector((1.4, -5.6, 1.4)), c + Vector((0.5, -4.2, 0.6)), ez(u)), c, 30, 3.2, roll=L(-4, 2, u), shake=0.01, t=t)


def s_heart(u, t, T):
    g = GAITS["jog"]; run(T, "jog", jaw=10); scroll(T * gait_speed(g))
    xray(0.8); show(heart, aorta, vena, *lungs, *[o for o, _ in legart.values()])
    set_val("g_lung", "strength", 0.6); bpy.data.materials["g_lung"].node_tree.nodes["alpha"].inputs["Fac"].default_value = 0.15
    hb = heartbeat(T, 160)
    ORG[heart.name]["k"] = Vector((1 + 0.18 * hb,) * 3)
    set_val("g_heart", "strength", 3 + 10 * hb)
    follow()
    aor = [wpos(TORSO, p) for p in AOR]; ven = [wpos(TORSO, p) for p in VEN]
    for i, o in enumerate(cells):
        s = (T * 0.9 + i / 15) % 1.0
        o.hide_render = False
        o.location = path_at(aor, s) if i < 15 else path_at(ven, s)
        if i >= 15:
            o.hide_render = True
    for i, o in enumerate(puffs[:12]):  # blue oxygen-poor blood back up the vein
        s = (T * 0.9 + i / 12) % 1.0
        o.hide_render = False; o.location = path_at(ven, s)
    c = HEART + Vector((0, 0, 0.02))
    look(L(c + Vector((-0.45, -0.95, 0.08)), c + Vector((-0.28, -0.62, 0.04)), ez(u)), c, 40, 4.0, roll=4,
         shake=0.003 + 0.004 * hb, t=t)


def s_sprint(u, t, T):
    g = GAITS["sprint"]; run(T, "sprint", jaw=14, breath_rate=2.2); scroll(T * gait_speed(g))
    set_val("skin", "flush", 0.35 * u)
    x = 0.75 * win(u, 0.5, 0.7)
    xray(x)
    if x > 0:
        show(*legmus)
        set_col("g_mus", (1.0, 0.03, 0.02)); set_val("g_mus", "strength", 3 + 3 * win(u, 0.6, 1))
        follow()
        n = int(len(acid) * win(u, 0.6, 1.0))
        for i, o in enumerate(acid[:n]):
            s = "l" if i % 2 else "r"
            o.hide_render = False
            o.location = wpos(f"{s}_th", MUS_PTS[s][i % 4] + JIT[i] * 0.022 + Vector((0, 0, 0.004 * math.sin(T * 9 + i))))
    c = Vector((0, 0, HIPZ + 0.1))
    look(L(c + Vector((-0.7, -2.6, -0.55)), c + Vector((-0.45, -1.7, -0.45)), ez(u)), c + Vector((0, 0, 0.1)), 30, 2.8,
         roll=L(5, -5, u), shake=0.012, t=t)


def s_buffer(u, t, T):
    g = GAITS["sprint"]; run(T, "sprint", jaw=18, breath_rate=2.4); scroll(T * gait_speed(g))
    set_val("skin", "flush", 0.35)
    xray(0.75); show(*legmus, aorta, *lungs, airway, *[o for o, _ in legart.values()])
    set_col("g_mus", (1.0, 0.03, 0.02)); set_val("g_mus", "strength", 4)
    lungs_fill(breath_cycle(T, 1.1), 1.4)
    follow()
    aor = list(reversed([wpos(TORSO, p) for p in AOR]))  # hips -> chest
    air = list(reversed([wpos("neck", p) for p in AIR]))   # chest -> nose
    for i, o in enumerate(acid[:24]):
        s = "l" if i % 2 else "r"
        meet = win(u, 0.15 + 0.02 * (i % 10), 0.35 + 0.02 * (i % 10))
        if meet >= 1:
            continue
        o.hide_render = False
        o.location = wpos(f"{s}_th", MUS_PTS[s][i % 4] + JIT[i] * 0.022)
    for i, o in enumerate(bic[:20]):  # bicarbonate arrives through the thigh artery
        s = "l" if i % 2 else "r"
        a = win(u, 0.0 + 0.015 * i, 0.25 + 0.015 * i)
        if a >= 1:
            continue
        o.hide_render = False
        d = [wpos(f"{s}_th", p) for p in legart[s][1]]
        o.location = path_at(d, a).lerp(wpos(f"{s}_th", MUS_PTS[s][i % 4]), ez(max(0, a * 2 - 1)))
    # each neutralised acid becomes a CO2 bubble that rides up to the lungs and out of the mouth
    for i, o in enumerate(bub):
        s0 = 0.3 + 0.018 * i
        if u < s0:
            continue
        s = (u - s0) * 1.4
        if s > 1:
            continue
        o.hide_render = False
        side = "l" if i % 2 else "r"
        p0 = wpos(f"{side}_th", MUS_PTS[side][i % 4])
        o.location = p0.lerp(aor[0], ez(min(1, s * 4))) if s < 0.25 else (path_at(aor, (s - 0.25) / 0.45) if s < 0.7 else path_at(air, (s - 0.7) / 0.3))
    c = Vector((0, 0, HIPZ + 0.05))
    look(L(c + Vector((1.9, -1.3, 0.2)), c + Vector((1.5, -1.0, 0.25)), ez(u)), c + Vector((0, 0, 0.1)), 30, 4.0, roll=-3, shake=0.01, t=t)


def s_lactate(u, t, T):
    g = GAITS["jog"]; run(T, "jog", jaw=12); scroll(T * gait_speed(g))
    xr_ = 0.75 * win(u, 0.15, 0.35); xray(xr_)
    if xr_ > 0.25:
        show(heart, aorta, vena, *legmus, *[o for o, _ in legart.values()])
    set_val("g_mus", "strength", 2.0)
    hb = heartbeat(T, 150); ORG[heart.name]["k"] = Vector((1 + 0.15 * hb,) * 3)
    gl = win(u, 0.5, 0.9)
    set_col("g_heart", (1.0, 0.06 + 0.5 * gl, 0.04)); set_val("g_heart", "strength", 3 + 8 * hb + 4 * gl)
    follow()
    ven = [wpos(TORSO, p) for p in VEN]
    for i, o in enumerate(lac):  # lactate leaves the muscles and is carried up to the heart as fuel
        if u < 0.35:
            continue
        s = ((u - 0.3) * 1.5 - i * 0.025)
        if s < 0 or s > 1:
            continue
        side = "l" if i % 2 else "r"
        p0 = wpos(f"{side}_th", MUS_PTS[side][i % 4] + JIT[i] * 0.02)
        o.hide_render = False
        o.location = p0.lerp(ven[0], ez(min(1, s * 3))) if s < 0.33 else path_at(ven, (s - 0.33) / 0.67)
    c = Vector((0, CHEST.y - 0.05, HIPZ + 0.05))
    look(L(c + Vector((-0.8, -1.9, 0.0)), c + Vector((-0.6, -1.45, 0.1)), ez(u)), c + Vector((0, 0, 0.1)), 32, 4.0, roll=3, shake=0.004, t=t)


def s_after(u, t, T):
    stop = win(u, 0.0, 0.18)
    g = GAITS["jog"]
    if stop < 1:
        run(T, "jog", k=1 - stop, jaw=12)
    else:
        rate = 0.75
        f = breath_cycle(T, rate)
        rig.location = (0, 0, 0)
        pose({SP[0]: (6, 0, 0), SP[-1]: (-4 * f, 0, 0), "head": (-6 - 6 * f, 0, 0), "jaw": (6 + 10 * f, 0, 0),
              "l_clav": (0, 0, 3 * f * LS), "r_clav": (0, 0, -3 * f * LS)})
        bpy.context.view_layer.update()
        for s in ("l", "r"):  # hands on hips
            side = LS if s == "l" else -LS
            S = rig.pose.bones[f"{s}_up"].head
            E = S + Vector((side * 0.2, 0.08, -0.2))
            W = Vector((side * 0.16, J["pelvis"].y - 0.01, HIPZ + 0.09))
            arm_pts(s, E, W, W + Vector((-side * 0.04, -0.06, -0.05)))
        for s in ("l", "r"):
            leg(s, 0.2, g, 0.0)
        # breath clouds on each exhale
        ph = (T * rate) % 1.0
        mouth = rig.matrix_world @ (rig.pose.bones["head"].matrix @ rig.data.bones["head"].matrix_local.inverted()) @ LIPS
        for i, o in enumerate(breath):
            s = (ph - 0.5) * 2 - i * 0.05
            if 0 < s < 1:
                o.hide_render = False
                o.location = mouth + Vector((JIT[i].x * 0.03 * s, -0.04 - 0.2 * s, -0.02 * s + JIT[i].z * 0.02 * s))
                o.scale = (0.3 + 1.0 * s,) * 3
    dur = TL_SHOT["after"]["end"] - TL_SHOT["after"]["start"]
    scroll((T - t + min(t, 0.09 * dur)) * gait_speed(g))
    set_val("skin", "flush", 0.3)
    c = FACE + Vector((0, 0, -0.12))
    look(L(c + Vector((0.5, -1.4, -0.05)), c + Vector((0.3, -0.85, 0.0)), ez(u)), c, 40, 2.8, roll=-2, shake=0.002, t=t)


def s_trained(u, t, T):
    g = GAITS["easy"]; run(T, "easy", jaw=2, breath_rate=0.6); scroll(T * gait_speed(g))
    x = 0.75 * win(u, 0.2, 0.35) * (1 - win(u, 0.8, 0.95))
    xray(x)
    if x > 0:
        show(heart, *legmus, *lungs)
        set_col("g_mus", GREEN); set_col("g_heart", GREEN); set_val("g_lung", "strength", 0.8)
        hb = heartbeat(T, 110); ORG[heart.name]["k"] = Vector((1 + 0.12 * hb,) * 3)
        set_val("g_heart", "strength", 3 + 6 * hb)
        follow()
    c = Vector((0, 0, HIPZ + 0.3))
    look(L(c + Vector((0.4, -1.6, 0.1)), c + Vector((1.2, -4.0, 0.6)), ez(u)), c, 38, 4.0, roll=L(2, 0, u), shake=0.003, t=t)


def s_runtest(u, t, T):
    gname = os.environ.get("GAIT", "jog"); g = GAITS[gname]
    T = u * g["P"]; run(T, gname, jaw=6); scroll(T * gait_speed(g))
    c = Vector((0, 0, HIPZ - 0.05))
    look(orbit(c, 3.6, float(os.environ.get("AZ", "0")), 3), c, 35, 8.0)


def s_handtest(u, t, T):
    run(T, "jog")
    bpy.context.view_layer.update()
    h = rig.matrix_world @ rig.pose.bones[os.environ.get("TESTBONE", "l_hand")].tail
    look(h + Vector((0.25, -0.45, 0.1)), h, 50, 4.0)


# ============================================================================ v3: multi-angle shots
def orbit(c, dist, az, el):
    """Camera position around c: az in degrees (0 = runner's left side +X, -90 = in front), el above the horizon."""
    a, e = math.radians(az), math.radians(el)
    return Vector(c) + Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e))) * dist


def v_intro(u, t, T):
    g = GAITS["jog"]; run(T, "jog", jaw=10 * win(u, 0.3, 0.8) + 3, breath_rate=1.6); scroll(T * gait_speed(g))
    c = Vector((0, 0, HIPZ + 0.4)); e = ez(u)
    look(orbit(c, L(3.4, 1.9, e), L(-100, -45, e), L(-2, 8, e)), c + Vector((0, 0, 0.2 * e)), L(30, 42, e), 2.8,
         roll=L(-4, 2, e), shake=0.006, t=t)


def v_muscles(u, t, T):
    s_muscles(u, t, T)   # pose, x-ray legs, ATP sparks
    c = Vector((0, 0, HIPZ - 0.3)); e = ez(u)
    look(orbit(c, L(2.0, 1.45, e), L(-25, 40, e), L(-6, 10, e)), c, 30, 3.2, roll=L(-3, 3, e), shake=0.004, t=t)


def v_mito(u, t, T):
    s_mito(u, t, T)
    c = MC + Vector((0, 0.4, 0.1)); e = ez(u)
    look(orbit(c, L(4.6, 2.8, e), L(-110, -70, e), L(18, 4, e)), c, 34, 2.8, roll=L(5, -3, e), shake=0.01, t=t)


def v_brain(u, t, T):
    s_brain(u, t, T)
    e = ez(u)
    tgt = HEADC.lerp(Vector((0, CHEST.y - 0.03, NECK.z - 0.18)), ez((u - 0.25) / 0.75))
    look(orbit(tgt, L(0.95, 1.5, e), L(-95, -55, e), L(4, 38, e)), tgt, 36, 4.0, roll=L(0, 6, e), shake=0.003, t=t)


def v_diaphragm(u, t, T):
    s_diaphragm(u, t, T)
    c = Vector((0, CHEST.y - 0.04, NECK.z - 0.19)); e = ez(u)
    look(orbit(c, L(1.15, 0.95, e), L(-140, -40, e), L(10, 4, e)), c, 32, 5.6, shake=0.003, t=t)


def v_heart(u, t, T):
    s_heart(u, t, T)
    c = HEART + Vector((0, 0, 0.01)); e = ez(u)
    look(orbit(c, L(1.0, 0.42, e), L(-125, -105, e), L(12, 6, e)), c, 36, 4.0, roll=L(4, -2, e), shake=0.003, t=t)


def v_buffer(u, t, T):
    if u < 0.32:   # the sprint, seen from a low front angle
        k = u / 0.32
        g = GAITS["sprint"]; run(T, "sprint", jaw=14, breath_rate=2.2); scroll(T * gait_speed(g))
        set_val("skin", "flush", 0.3 * k)
        c = Vector((0, 0, HIPZ + 0.25))
        look(orbit(c, L(3.2, 2.4, ez(k)), L(-75, -60, ez(k)), L(-14, -10, ez(k))), c + Vector((0, 0, 0.1)), 24, 2.8,
             roll=L(6, -4, k), shake=0.012, t=t)
        return
    v = (u - 0.32) / 0.68
    s_buffer(v, t, T)   # acid -> bicarbonate -> CO2 bubbles -> lungs -> mouth
    c = Vector((0, 0, HIPZ + 0.05)); e = ez(v)
    look(orbit(c, L(2.1, 1.7, e), L(-30, 15, e), L(4, 10, e)), c + Vector((0, 0, 0.1 + 0.25 * e)), 30, 4.0,
         roll=-3, shake=0.009, t=t)


def v_lactate(u, t, T):
    s_lactate(u, t, T)
    c = Vector((0, CHEST.y - 0.03, HIPZ + 0.05)); e = ez(u)
    look(orbit(c, L(2.5, 1.8, e), L(70, 25, e), L(38, 22, e)), c + Vector((0, 0, 0.1)), 32, 4.0, roll=L(-4, 2, e), shake=0.004, t=t)


def v_trained(u, t, T):
    s_trained(u, t, T)
    c = Vector((0, 0, HIPZ + 0.35)); e = ez(u)
    look(orbit(c, L(2.0, 7.0, e), L(-60, -100, e), L(6, 32, e)), c, L(34, 30, e), 4.0, roll=L(3, 0, e), shake=0.003, t=t)


V3 = dict(intro=v_intro, muscles=v_muscles, mito=v_mito, brain=v_brain, diaphragm=v_diaphragm, heart=v_heart,
          buffer=v_buffer, lactate=v_lactate, trained=v_trained)


SHOTS = dict(runtest=s_runtest, handtest=s_handtest, intro=s_intro, muscles=s_muscles, mito=s_mito, brain=s_brain, diaphragm=s_diaphragm, alveoli=s_alveoli,
             heart=s_heart, sprint=s_sprint, buffer=s_buffer, lactate=s_lactate, after=s_after, trained=s_trained)
TL_SHOT = {s["id"]: s for s in TL["shots"]}
if os.environ.get("CAMS", "v3") == "v3":
    SHOTS.update(V3)

# ----------------------------------------------------------------------------- render
for shot in TL["shots"] + [dict(id=k, start=3.0, end=4.0) for k in ("handtest", "runtest") if k in ONLY]:
    sid = shot["id"]
    if ONLY and sid not in ONLY:
        continue
    dur = shot["end"] - shot["start"]
    if PREVIEW:
        us = [float(x) for x in arg("--us", "0.6").split(",")]
        frames = [(f"{OUT}/preview/{sid}_{int(uu*100):02d}.png", uu) for uu in us]
    else:
        n = max(1, round(dur * FPS))
        frames = [(f"{OUT}/frames/{sid}/{i:04d}.png", (i + 0.5) / n) for i in range(n)]
    for path, u in frames:
        if os.path.exists(path) and not PREVIEW:
            continue
        CUR = sid
        reset(); SHOTS[sid](u, u * dur, shot["start"] + u * dur)
        follow()
        sc.render.filepath = path; t0 = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"FRAME {path} {time.time() - t0:.1f}s", flush=True)
