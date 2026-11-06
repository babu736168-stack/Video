"""Renders every shot of the sneeze short, frame by frame, driven by ../out/timeline.json.

  python shots.py -- --preview            # one still per shot -> ../out/preview/<shot>.png
  python shots.py -- [--only a,b] [--fps 15] [--spp 12] [--scale 0.5]   # -> ../out/frames/<shot>/0000.png

Each shot is a function of u (0..1 across the shot) that poses the character, moves the camera and
animates the x-ray props. Already-rendered frames are skipped, so the job can be resumed.
"""
import bpy, sys, os, json, math, time
import numpy as np
from mathutils import Vector

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
OUT = os.path.join(HERE, "..", "out")
TL = json.load(open(os.path.join(OUT, "timeline.json")))

# ----------------------------------------------------------------------------- scene
bpy.ops.wm.read_factory_settings(use_empty=True)
ch = C.build_character(); C.build_room(); C.build_lights()
J = C.J
body, rig, ik, hair = ch["body"], ch["rig"], ch["ik"], ch["hair"]
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"
sc.cycles.samples = SPP; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.05
sc.cycles.use_denoising = True; sc.cycles.max_bounces = 4; sc.cycles.transparent_max_bounces = 16
sc.render.resolution_x, sc.render.resolution_y = int(1080 * SCALE), int(1920 * SCALE)
sc.render.use_persistent_data = True
sc.view_settings.view_transform = "Filmic"; sc.view_settings.look = "Medium High Contrast"
sc.view_settings.exposure = -0.35

# ----------------------------------------------------------------------------- landmarks
V = np.array([v.co[:] for v in body.data.vertices])
eye = np.array(J["l-eye"][:]); EYE_Z = eye[2]
m = (np.abs(V[:, 0]) < 0.004) & (V[:, 2] > EYE_Z - 0.07) & (V[:, 2] < EYE_Z - 0.01)
NOSE = Vector(V[m][V[m][:, 1].argmin()])
m = (np.abs(V[:, 0]) < 0.004) & (V[:, 2] > NOSE.z - 0.065) & (V[:, 2] < NOSE.z - 0.025)
LIPS = Vector(V[m][V[m][:, 1].argmin()])
m = (V[:, 0] > 0.05) & (V[:, 2] > EYE_Z - 0.05) & (V[:, 2] < EYE_Z + 0.01) & (V[:, 1] > eye[1] + 0.04)
EAR = Vector(V[m][V[m][:, 0].argmax()])
SPINE = sorted([k for k in J if k.startswith("spine-")], key=lambda k: J[k].z)
CHEST = J[SPINE[-1]].copy()
HEADC = Vector((0, eye[1] + 0.085, EYE_Z + 0.01))
print("LANDMARKS nose", NOSE, "lips", LIPS, "ear", EAR, "chest", CHEST, "neck", J["neck"])

# cheek-puff shape key
body.shape_key_add(name="Basis")
puff = body.shape_key_add(name="puff")
for i, v in enumerate(body.data.vertices):
    c = v.co
    w = 0.0
    for sx in (1, -1):
        d = (c - Vector((sx * 0.036, LIPS.y + 0.03, LIPS.z + 0.012))).length
        w = max(w, math.exp(-d * d / (2 * 0.019 ** 2)))
    d = (c - Vector((0, LIPS.y, LIPS.z))).length
    w = max(w, 0.6 * math.exp(-d * d / (2 * 0.012 ** 2)))
    if c.z < J["neck"].z or c.y > eye[1] + 0.06:
        w = 0
    puff.data[i].co = c + v.normal * 0.011 * w

# ----------------------------------------------------------------------------- props
GREEN, RED, CYAN, PINK = (0.15, 1.0, 0.3), (1.0, 0.05, 0.03), (0.4, 0.85, 1.0), (1.0, 0.35, 0.45)
props = []


def prop(o, mat):
    o.data.materials.clear(); o.data.materials.append(mat)
    o.hide_render = True; props.append(o); return o


def catmull(pts, n=200):
    P = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n // (len(P) - 3)):
            t = k / (n // (len(P) - 3))
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-1])
    return out


def tube(name, pts, r, mat):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = r; cu.bevel_resolution = 4
    sp = cu.splines.new("POLY"); dense = catmull(pts, 120)
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


g_air = C.glow_material("g_air", GREEN, 3.0, 0.75)
g_red = C.glow_material("g_red", RED, 4.0, 0.85)
g_brain = C.glow_material("g_brain", PINK, 2.5, 0.8)
g_lung = C.glow_material("g_lung", PINK, 2.0, 0.6)
g_puff = C.glow_material("g_puff", CYAN, 6.0, 0.9)
g_dust = C.glow_material("g_dust", (1.0, 0.85, 0.5), 3.0, 1.0)
g_ring = C.glow_material("g_ring", RED, 5.0, 0.8)
g_spray = C.glow_material("g_spray", (0.75, 0.9, 1.0), 2.0, 0.55)
g_sig = C.glow_material("g_sig", (1.0, 1.0, 0.6), 25.0, 1.0)

NOSTRIL = NOSE + Vector((0, 0.012, -0.014))
NASO = Vector((0, NOSE.y + 0.085, NOSE.z - 0.008))
airway_pts = [NOSTRIL, NOSTRIL + Vector((0, 0.03, 0.012)), Vector((0, NOSE.y + 0.06, NOSE.z + 0.004)), NASO,
              Vector((0, NASO.y + 0.004, LIPS.z - 0.01)), Vector((0, J["neck"].y - 0.035, J["neck"].z + 0.01)),
              Vector((0, J["neck"].y - 0.04, J["neck"].z - 0.06)), Vector((0, CHEST.y - 0.04, J["neck"].z - 0.1))]
airway, AIR = tube("airway", airway_pts, 0.0075, g_air)
bronchi = [tube(f"bronch{sx}", [airway_pts[-1], Vector((sx * 0.03, CHEST.y - 0.035, J["neck"].z - 0.125)),
                               Vector((sx * 0.055, CHEST.y - 0.03, J["neck"].z - 0.15))], 0.005, g_air)[0] for sx in (1, -1)]
air_up = list(reversed(AIR))  # chest -> nostril
mouth_pts = [Vector((0, LIPS.y + 0.012, LIPS.z)), Vector((0, LIPS.y + 0.045, LIPS.z + 0.004)),
             Vector((0, NASO.y, LIPS.z - 0.004)), Vector((0, NASO.y + 0.004, LIPS.z - 0.012))]
mouthway, _ = tube("mouthway", mouth_pts, 0.008, g_air)
EARIN = EAR + Vector((-0.02, -0.004, -0.012))
euwhere = []
for sx in (1, -1):
    pts = [NASO + Vector((sx * 0.01, 0.0, 0)), Vector((sx * 0.03, NASO.y + 0.02, NASO.z + 0.002)),
           Vector((sx * (EARIN.x - 0.012), EARIN.y - 0.004, EARIN.z - 0.004)), Vector((sx * EARIN.x, EARIN.y, EARIN.z))]
    o, d = tube(f"eustach{sx}", pts, 0.0035, g_air); euwhere.append((o, d))
    canal = [Vector((sx * EARIN.x, EARIN.y, EARIN.z)), Vector((sx * (EAR.x - 0.004), EARIN.y, EARIN.z + 0.002))]
    tube(f"canal{sx}", canal, 0.0045, g_air)
bpy.ops.mesh.primitive_cylinder_add(radius=0.0065, depth=0.0015, location=(EARIN.x + 0.003, EARIN.y, EARIN.z),
                                    rotation=(0, math.pi / 2, 0))
drum = prop(bpy.context.object, C.glow_material("g_drum", GREEN, 5.0, 0.95)); drum.name = "drum"
# brain
brain = ball("brain", 1.0, g_brain, 48)
brain.location = HEADC + Vector((0, 0.01, 0.025)); brain.scale = (0.06, 0.075, 0.05)
tex = bpy.data.textures.new("gyri", "VORONOI"); tex.noise_scale = 0.09; tex.distance_metric = "DISTANCE"
brain.modifiers.new("s0", "SUBSURF").levels = 2
dm = brain.modifiers.new("d", "DISPLACE"); dm.texture = tex; dm.strength = -0.12; dm.texture_coords = "LOCAL"
sig_path = catmull([brain.location.copy(), Vector((0, HEADC.y + 0.02, LIPS.z)), J["neck"] + Vector((0, 0.03, 0)),
                    CHEST + Vector((0, 0.04, 0.0)), CHEST + Vector((0, 0.02, -0.08))], 120)
signal = ball("signal", 0.008, g_sig)
sigtrail = [ball(f"trail{i}", 0.006 - i * 0.0005, g_sig) for i in range(6)]
# lungs
lungs = []
for sx in (1, -1):
    l = ball(f"lung{sx}", 1.0, g_lung, 32)
    l.location = Vector((sx * 0.07, CHEST.y - 0.03, J["neck"].z - 0.15)); l.scale = (0.055, 0.05, 0.1)
    lungs.append(l)
puffs = [ball(f"puff{i}", 0.006, g_puff, 12) for i in range(26)]
dust = [ball(f"dust{i}", 0.0025, g_dust, 8) for i in range(16)]
rings = []
for i in range(3):
    bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.012, major_segments=64, minor_segments=8,
                                     location=HEADC, rotation=(math.pi / 2, 0, 0))
    rings.append(prop(bpy.context.object, g_ring))
TEAR = J["neck"] + Vector((0, -0.04, -0.03))
tear = ball("tear", 0.009, g_red, 16); tear.location = TEAR
cracks = []
for i in range(7):
    a = i / 7 * 2 * math.pi
    bpy.ops.mesh.primitive_cone_add(radius1=0.0016, radius2=0.0, depth=0.03, vertices=6)
    c = bpy.context.object; c.rotation_euler = (0, a, 0); cracks.append(prop(c, g_red))
spray = [ball(f"spray{i}", 0.0025, g_spray, 8) for i in range(70)]
RNG = np.random.default_rng(3)
SPRAY_DIR = [Vector((RNG.normal(0, 0.35), -1.0, RNG.normal(0.05, 0.3))).normalized() for _ in spray]
SPRAY_SPD = RNG.uniform(0.25, 0.6, len(spray))
DUST0 = [Vector((RNG.uniform(-0.05, 0.05), RNG.uniform(-0.14, -0.06), RNG.uniform(-0.05, 0.02))) for _ in dust]

# ----------------------------------------------------------------------------- camera
bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam
cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 24.0
cam.data.dof.use_dof = True


def look(loc, tgt, lens, fstop=4.0, roll=0.0, shake=0.0, t=0.0):
    loc, tgt = Vector(loc), Vector(tgt)
    if shake:
        loc = loc + Vector((math.sin(t * 13.1) * 0.6 + math.sin(t * 29.3) * 0.4, 0,
                            math.sin(t * 17.7) * 0.6 + math.sin(t * 23.9) * 0.4)) * shake
    cam.location = loc
    q = (tgt - loc).to_track_quat("-Z", "Y")
    cam.rotation_euler = q.to_euler()
    cam.rotation_euler.rotate_axis("Z", math.radians(roll))
    cam.data.lens = lens; cam.data.dof.focus_distance = (tgt - loc).length; cam.data.dof.aperture_fstop = fstop


def L(a, b, u):
    return Vector(a).lerp(Vector(b), u) if not isinstance(a, (int, float)) else a + (b - a) * u


def ez(u):
    u = min(max(u, 0), 1); return u * u * (3 - 2 * u)


def win(u, a, b):
    return ez((u - a) / (b - a)) if b > a else float(u >= a)


# ----------------------------------------------------------------------------- state
MATS = [m for m in bpy.data.materials]


def set_val(mat_name, node, v):
    bpy.data.materials[mat_name].node_tree.nodes[node].outputs[0].default_value = v


def xray(v):
    for mt in MATS:
        n = mt.node_tree.nodes.get("xray") if mt.node_tree else None
        if n:
            n.outputs[0].default_value = v
    hair.hide_render = v > 0.3
    for k in ("helper-upper-teeth", "helper-lower-teeth", "helper-tongue"):
        ch["objs"][k].hide_render = v > 0.3
    for k in ("brow1", "brow-1"):
        ch["objs"][k].hide_render = v > 0.3


def pose(rot):
    for pb in rig.pose.bones:
        pb.rotation_mode = "XYZ"; pb.rotation_euler = (0, 0, 0)
    for k, (x, y, z) in rot.items():
        rig.pose.bones[k].rotation_euler = (math.radians(x), math.radians(y), math.radians(z))


def arms_down():
    """Relaxed arms instead of the A-pose."""
    return {"l_up": (0, 0, 0), "r_up": (0, 0, 0), "l_clav": (0, 0, 0)}


from mathutils import Matrix


def aim(pb, target, up):
    """Points pose bone pb (its Y axis) at target (armature space), keeping its posed head."""
    bpy.context.view_layer.update()
    head = pb.head.copy()
    y = (Vector(target) - head).normalized()
    x = Vector(up).cross(y).normalized(); z = x.cross(y)
    M = Matrix((x, y, z)).transposed().to_4x4(); M.translation = head
    pb.matrix = M
    bpy.context.view_layer.update()


def arm_to(side, E, W, F, up_arm=(0, 0, 1), up_hand=(0, 0, 1), k=1.0, arc=(0, -0.12, 0)):
    """Moves the arm so the elbow aims at E, wrist at W and the hand at F; k blends from the rest pose."""
    pu, pf, ph = (rig.pose.bones[f"{side}_{b}"] for b in ("up", "fa", "hand"))
    bpy.context.view_layer.update()
    E0, W0 = pu.tail.copy(), pf.tail.copy(); F0 = ph.tail.copy()
    bump = Vector(arc) * math.sin(math.pi * k)
    E_, W_, F_ = E0.lerp(Vector(E), k) + bump, W0.lerp(Vector(W), k) + bump, F0.lerp(Vector(F), k) + bump
    aim(pu, E_, up_arm); aim(pf, W_, up_arm); aim(ph, F_, up_hand)


REST_ARMS = {"l_up": (0, 0, 52), "r_up": (0, 0, -52), "l_fa": (-15, 0, 0), "r_fa": (-15, 0, 0)}


def reset():
    for p in props:
        p.hide_render = True
    xray(0.0)
    for k, v in (("g_air", 3.0), ("g_red", 4.0), ("g_ring", 5.0), ("g_drum", 5.0), ("g_brain", 2.5),
                 ("g_lung", 2.0), ("g_puff", 6.0), ("g_spray", 2.0)):
        set_val(k, "strength", v)
    bpy.data.materials["g_air"].node_tree.nodes["col"].outputs[0].default_value = (*GREEN, 1)
    bpy.data.materials["g_drum"].node_tree.nodes["col"].outputs[0].default_value = (*GREEN, 1)
    set_val("skin", "flush", 0.0); set_val("eye_veins", "veins", 0.0)
    puff.value = 0.0
    for s in ("l", "r"):
        ik[s]["con"].influence = 0.0
    pose(dict(REST_ARMS))
    for k in ("helper-l-eye", "helper-r-eye"):
        ch["objs"][k].scale = (1, 1, 1)


def show(*objs):
    for o in objs:
        o.hide_render = False


def puffs_along(path, u0, spacing, speed, u, n=len(puffs), scale=1.0):
    for i, p in enumerate(puffs[:n]):
        s = (u - u0) * speed - i * spacing
        if 0 <= s <= 1:
            p.hide_render = False; p.location = path_at(path, s); p.scale = (scale,) * 3


# ----------------------------------------------------------------------------- shots
FACE = Vector((0, LIPS.y + 0.02, (EYE_Z + LIPS.z) / 2))


def s_intro(u, t):
    pose({**REST_ARMS, "head": (-10 * win(u, 0.2, 1), 0, 0), "jaw": (8 * win(u, 0.55, 1), 0, 0)})
    look(L(FACE + Vector((0.12, -0.75, 0.06)), FACE + Vector((0.05, -0.42, 0.02)), ez(u)), FACE + Vector((0, 0, 0.01)),
         55, 2.8, roll=L(-4, 2, u), shake=0.0015, t=t)


def s_tickle(u, t):
    xray(0.6); show(airway, mouthway)
    set_val("g_air", "strength", 2.0 + 2.5 * win(u, 0.4, 0.9))
    for i, d in enumerate(dust):
        s = ez(min(1, max(0, u * 1.3 - i * 0.03)))
        d.hide_render = s >= 0.99
        d.location = (NOSTRIL + DUST0[i]).lerp(NOSTRIL + Vector((0, 0.02, 0.01)) + DUST0[i] * 0.1, s)
    a = math.radians(L(-60, -30, ez(u)))
    c = FACE + Vector((0, 0.02, 0.0))
    look(c + Vector((math.cos(a) * 0.5, math.sin(a) * 0.5, 0.05)), c, 50, 4.0, shake=0.001, t=t)


def s_brain(u, t):
    xray(0.65); show(brain, airway, signal, *sigtrail)
    flash = math.exp(-((u - 0.25) / 0.12) ** 2)
    set_val("g_brain", "strength", 2.0 + 10 * flash)
    for k, o in enumerate([signal] + sigtrail):
        o.location = path_at(sig_path, ez(min(1, max(0, (u - 0.2) / 0.75))) - k * 0.02)
    c = HEADC + Vector((0, 0, -0.05))
    look(L(c + Vector((-0.35, -0.55, 0.22)), c + Vector((-0.25, -0.45, 0.08)), ez(u)), L(c + Vector((0, 0, 0.05)), c + Vector((0, 0, -0.08)), ez(u)),
         38, 5.6, roll=6, shake=0.002, t=t)


def s_lungs(u, t):
    xray(0.8); show(airway, *lungs, *bronchi)
    sq = win(u, 0.1, 0.45)
    for sx, l in zip((1, -1), lungs):
        l.scale = (0.055 * (1 - 0.25 * sq), 0.05 * (1 - 0.25 * sq), 0.095 * (1 - 0.18 * sq))
    set_val("g_lung", "strength", 2.0 + 3.0 * sq)
    puffs_along(air_up, 0.15, 0.035, 1.6, u)
    c = (CHEST + NOSE) / 2
    look(L(c + Vector((0.25, -0.95, -0.1)), c + Vector((0.12, -0.7, 0.0)), ez(u)), c, 32, 5.6, roll=-5, shake=0.002, t=t)


def pinch_pose(k):
    """Right hand clamps over nose and mouth."""
    arm_to("r", Vector((-0.2, NOSE.y + 0.02, LIPS.z - 0.22)), Vector((-0.06, NOSE.y - 0.035, LIPS.z - 0.035)),
           Vector((0.07, NOSE.y - 0.02, NOSE.z - 0.005)), up_arm=(0, -1, 0), up_hand=HAND_UP, k=k)


HAND_UP = tuple(float(x) for x in os.environ.get("HAND_UP", "0,-1,0").split(","))


def s_pinch(u, t):
    k = win(u, 0.05, 0.6)
    pose({**REST_ARMS, "head": (-4, 0, 0)})
    pinch_pose(k)
    c = FACE + Vector((0, 0, -0.08))
    look(L(c + Vector((-0.3, -0.8, -0.12)), c + Vector((-0.2, -0.62, -0.08)), ez(u)), c, 40, 3.2, roll=4, shake=0.0015, t=t)


def s_trapped(u, t):
    pose({**REST_ARMS, "head": (-4, 0, 0)}); pinch_pose(1.0)
    xray(0.62); show(airway, mouthway)
    bpy.data.materials["g_air"].node_tree.nodes["col"].outputs[0].default_value = (*RED, 1)
    set_val("g_air", "strength", 3 + 3 * win(u, 0, 0.6))
    # puffs rush up and bounce back and forth inside the sealed airway
    for i, p in enumerate(puffs[:18]):
        ph = (u * 2.2 + i * 0.137) % 1.0
        s = 0.55 + 0.42 * abs(math.sin(math.pi * ph))   # oscillates between throat and nose
        p.hide_render = False; p.location = path_at(air_up, s) + Vector((math.sin(i * 7.1) * 0.006, 0, math.cos(i * 3.3) * 0.006))
    a = math.radians(L(-35, -15, ez(u)))
    c = FACE + Vector((0, 0.03, -0.02))
    look(c + Vector((math.cos(a) * 0.45, math.sin(a) * 0.45, 0.02)), c, 50, 4.0, shake=0.002, t=t)


def s_pressure(u, t):
    pose({**REST_ARMS, "head": (-4, 0, 0)}); pinch_pose(1.0)
    k = win(u, 0.05, 0.7)
    puff.value = k * (1 + 0.08 * math.sin(t * 40) * k)
    set_val("skin", "flush", 0.65 * k)
    show(*rings)
    for i, r in enumerate(rings):
        ph = (u * 2.5 + i / 3) % 1.0
        r.location = HEADC + Vector((0, 0.0, -0.02)); r.scale = (0.1 + 0.2 * ph,) * 3
        r.hide_render = u < 0.2
    set_val("g_ring", "strength", 4.0)
    look(L(FACE + Vector((0.4, -0.5, 0.05)), FACE + Vector((0.27, -0.33, 0.03)), ez(u)), FACE + Vector((0.02, 0, 0)), 50, 2.8,
         roll=L(0, -6, u), shake=0.001 + 0.006 * k, t=t)


def s_ear(u, t):
    pose({**REST_ARMS, "head": (-4, 0, 0)}); pinch_pose(1.0)
    puff.value = 0.8; set_val("skin", "flush", 0.5)
    xray(0.55 * win(u, 0.0, 0.25)); show(airway, *[o for o, _ in euwhere], drum)
    for o in bpy.data.objects:
        if o.name.startswith("canal"):
            o.hide_render = False
    bpy.data.materials["g_air"].node_tree.nodes["col"].outputs[0].default_value = (*RED, 1)
    pop = win(u, 0.72, 0.78)
    bpy.data.materials["g_drum"].node_tree.nodes["col"].outputs[0].default_value = (*(GREEN if pop < 0.5 else RED), 1)
    set_val("g_drum", "strength", 5 + 30 * math.exp(-((u - 0.76) / 0.05) ** 2))
    d = euwhere[0][1]
    for i, p in enumerate(puffs[:10]):
        s = (u * 1.6 - i * 0.07)
        if 0 <= s <= 1:
            p.hide_render = False; p.location = path_at(d, s); p.scale = (0.6,) * 3
    c = EARIN + Vector((0.0, 0.01, 0.0))
    look(L(c + Vector((0.42, -0.18, 0.06)), c + Vector((0.24, -0.1, 0.03)), ez(u)), c, 50, 3.2, roll=-5,
         shake=0.0015 + 0.01 * math.exp(-((u - 0.76) / 0.06) ** 2), t=t)


def s_eye(u, t):
    pose({**REST_ARMS, "head": (-4, 0, 0)}); pinch_pose(1.0)
    puff.value = 0.85; set_val("skin", "flush", 0.55)
    set_val("eye_veins", "veins", 1.6 * win(u, 0.2, 0.8))
    for k in ("helper-l-eye", "helper-r-eye"):
        ch["objs"][k].scale = (1 + 0.05 * win(u, 0.2, 0.8),) * 3
    e = J["l-eye"] + Vector((0, -0.01, 0))
    look(L(e + Vector((0.04, -0.2, 0.01)), e + Vector((0.025, -0.13, 0.005)), ez(u)), e, 60, 2.2, roll=3, shake=0.001, t=t)


def s_throat(u, t):
    pose({**REST_ARMS, "head": (-4, 0, 0)}); pinch_pose(1.0)
    puff.value = 0.6
    xray(0.65); show(airway, mouthway)
    bpy.data.materials["g_air"].node_tree.nodes["col"].outputs[0].default_value = (*RED, 1)
    set_val("g_air", "strength", 4)
    g = win(u, 0.45, 0.75)
    if g > 0:
        show(tear, *cracks)
        tear.location = TEAR; tear.scale = (0.3 + 0.9 * g,) * 3
        for i, c in enumerate(cracks):
            a = i / len(cracks) * 2 * math.pi + 0.3
            L_ = 0.3 + 0.9 * g * (0.7 + 0.3 * math.sin(i * 2.7))
            d = Vector((math.cos(a), 0, math.sin(a)))
            c.location = TEAR + d * 0.012 * L_ + Vector((0, -0.003, 0))
            c.rotation_euler = d.to_track_quat("Z", "Y").to_euler(); c.scale = (1, 1, L_)
        set_val("g_red", "strength", 4 + 20 * math.exp(-((u - 0.5) / 0.06) ** 2))
    c = TEAR + Vector((0, 0.01, 0.03))
    a = math.radians(L(-55, -40, ez(u)))
    look(c + Vector((math.cos(a), math.sin(a), 0.12)) * L(0.55, 0.38, ez(u)), c, 50, 4.0, shake=0.002 + 0.008 * math.exp(-((u - 0.5) / 0.06) ** 2), t=t)


def s_elbow(u, t):
    k = win(u, 0.05, 0.4)
    snz = win(u, 0.52, 0.6)
    pose({**REST_ARMS, "head": (-8 * (1 - k) + 22 * snz - 10 * k * (1 - snz), 0, 0), "neck": (8 * snz, 0, 0),
          "jaw": (10 * k * (1 - snz), 0, 0)})
    arm_to("r", Vector((-0.03, NOSE.y - 0.14, LIPS.z - 0.03)), Vector((0.15, NOSE.y - 0.04, NOSE.z + 0.03)),
           Vector((0.22, NOSE.y + 0.02, NOSE.z + 0.05)), up_arm=(0, 0, 1), up_hand=(0, 0, 1), k=k)
    show(*spray)
    mouth = rig.matrix_world @ rig.pose.bones["head"].matrix @ rig.data.bones["head"].matrix_local.inverted() @ LIPS
    for i, p in enumerate(spray):
        tt = (u - 0.55) * 10 - i * 0.004
        if tt <= 0:
            p.hide_render = True; continue
        d = min(tt * SPRAY_SPD[i], 0.06 + 0.02 * (i % 5) / 5)
        p.location = mouth + SPRAY_DIR[i] * d + Vector((0, 0, -0.01))
        p.scale = (1 + 0.5 * (i % 3),) * 3
    set_val("g_spray", "strength", 2.0 * (1 - win(u, 0.8, 1.0)) + 0.01)
    c = FACE + Vector((0, -0.02, -0.08))
    look(L(c + Vector((0.55, -0.85, 0.0)), c + Vector((0.4, -0.65, 0.02)), ez(u)), c, 38, 4.0, roll=-3,
         shake=0.0015 + 0.01 * math.exp(-((u - 0.57) / 0.04) ** 2), t=t)


SHOTS = dict(intro=s_intro, tickle=s_tickle, brain=s_brain, lungs=s_lungs, pinch=s_pinch, trapped=s_trapped,
             pressure=s_pressure, ear=s_ear, eye=s_eye, throat=s_throat, elbow=s_elbow)

# ----------------------------------------------------------------------------- render
for shot in TL["shots"]:
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
        reset(); SHOTS[sid](u, u * dur)
        bpy.context.view_layer.update()
        sc.render.filepath = path; t0 = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"FRAME {path} {time.time() - t0:.1f}s", flush=True)
