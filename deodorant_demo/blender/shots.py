"""
Procedural 3D shots for the deodorant short (rendered with Blender/Cycles, CPU).
Every key word in the script gets its own 3D image.

Usage:  python shots.py -- OUT_DIR [shot1 shot2 ...]   (bpy python, Blender 5)
"""
import bpy, bmesh, math, sys, os, json, random, time
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "/tmp/shots"
ONLY = set(argv[1:])
os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.join(HERE, "..", "..", "tunguska_demo", "data", "countries.geojson")
RES = (1080, 1920)


# ----------------------------------------------------------------------------- basics
def reset():
    _mats.clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    w = sc.world = bpy.data.worlds.new("w")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.006, 0.006, 0.01, 1)
    return sc

_mats = {}
def mat(name, color, metal=0.0, rough=0.4, emit=None, strength=0.0, glass=False, alpha=1.0, sss=0.0):
    key = (name, color, metal, rough, emit, strength, glass)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if glass:
        b.inputs["Transmission Weight"].default_value = 1.0
        b.inputs["IOR"].default_value = 1.45
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    _mats[key] = m
    return m

def assign(obj, m, smooth=True):
    obj.data.materials.clear()
    obj.data.materials.append(m)
    if smooth and obj.type == "MESH":
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj

def cyl(r, depth, loc, m, verts=96, rot=(0, 0, 0), fill="NGON"):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot, end_fill_type=fill)
    return assign(bpy.context.object, m)

def sphere(r, loc, m, scale=(1, 1, 1), seg=48):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=r, location=loc)
    o = bpy.context.object
    o.scale = scale
    return assign(o, m)

def box(size, loc, m, rot=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    if bevel:
        bm = o.modifiers.new("b", "BEVEL"); bm.width = bevel; bm.segments = 4
    return assign(o, m, smooth=False)

def cyl_between(p1, p2, r, m):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=r, depth=d.length, location=(p1 + p2) / 2)
    o = bpy.context.object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return assign(o, m)

def text3d(body, loc, size, m, rot=(math.radians(90), 0, 0), extrude=0.05, align="CENTER"):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    t = bpy.context.object
    t.data.body = body
    t.data.align_x = align
    t.data.align_y = "CENTER"
    t.data.size = size
    t.data.extrude = extrude
    t.data.bevel_depth = extrude * 0.25
    t.data.materials.append(m)
    return t

def platform(r=2.4, rim=(1, 0.45, 0.12), top=(0.11, 0.10, 0.095)):
    cyl(r, 0.25, (0, 0, -0.125), mat("plat", top, rough=0.35), verts=160)
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.03, location=(0, 0, 0), major_segments=160)
    assign(bpy.context.object, mat("rim", (1, .5, .2), emit=rim, strength=14))
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, -0.26))
    assign(bpy.context.object, mat("floor", (0.02, 0.02, 0.025), rough=0.5))

def target(loc):
    bpy.ops.object.empty_add(location=loc)
    return bpy.context.object

def lights(tgt, key=900, rimc=(0.4, 0.6, 1.0), warm=250):
    def L(loc, e, c, s):
        bpy.ops.object.light_add(type="AREA", location=loc)
        o = bpy.context.object
        o.data.energy = e; o.data.color = c; o.data.size = s
        k = o.constraints.new("TRACK_TO"); k.target = tgt
    L((-3, -4, 5.5), key, (1, .95, .9), 3)
    L((4, 3, 4.5), key * 0.8, rimc, 2.5)
    L((3, -3, 0.8), warm, (1, .6, .3), 2)

def camera(loc, tgt, lens=45):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    k = c.constraints.new("TRACK_TO"); k.target = tgt
    c.data.lens = lens
    bpy.context.scene.camera = c

def render(name, samples=32):
    sc = bpy.context.scene
    sc.cycles.samples = samples
    sc.render.filepath = os.path.join(OUT, name + ".png")
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"SHOT {name} {time.time() - t0:.1f}s", flush=True)


# ----------------------------------------------------------------------------- objects
def can(loc=(0, 0, 0), scale=1.0, paint=(0.05, 0.16, 0.6), label="DEO", cut=False):
    x, y, z = loc
    s = scale
    alu = mat("alu", (0.8, 0.8, 0.82), metal=1.0, rough=0.18)
    if not cut:
        o = cyl(0.42 * s, 2.2 * s, (x, y, z + 1.1 * s), mat("paint", paint, metal=0.6, rough=0.22))
        bv = o.modifiers.new("b", "BEVEL"); bv.width = 0.05 * s; bv.segments = 5
        cyl(0.425 * s, 0.7 * s, (x, y, z + 1.15 * s), mat("label", (0.92, 0.92, 0.9), rough=0.45))
        if label:
            text3d(label, (x, y - 0.44 * s, z + 1.12 * s), 0.3 * s, mat("txt" + str(paint), paint, rough=0.3), extrude=0.01 * s)
    else:
        # hollow shell, front quarter cut away to show the inside
        o = cyl(0.42 * s, 2.2 * s, (x, y, z + 1.1 * s), mat("paint", paint, metal=0.6, rough=0.22), fill="NOTHING")
        so = o.modifiers.new("s", "SOLIDIFY"); so.thickness = 0.03 * s
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x - 0.5 * s, y - 0.5 * s, z + 1.1 * s))
        cutter = bpy.context.object
        cutter.scale = (1.0 * s, 1.0 * s, 2.6 * s)
        bo = o.modifiers.new("cut", "BOOLEAN"); bo.object = cutter; bo.operation = "DIFFERENCE"
        cutter.hide_render = True; cutter.hide_viewport = True
        cyl(0.42 * s, 0.04 * s, (x, y, z + 0.02 * s), alu)
        cyl(0.39 * s, 0.85 * s, (x, y, z + 0.46 * s), mat("liquid", (0.1, 0.45, 0.8), rough=0.05, glass=True, emit=(0.05, 0.3, 0.7), strength=1.5))
        cyl(0.03 * s, 2.0 * s, (x, y, z + 1.15 * s), mat("tube", (0.9, 0.9, 0.95), rough=0.3))
        r = random.Random(4)
        gas = mat("gas", (1, .7, .2), emit=(1, .6, .15), strength=4)
        for i in range(40):
            a = r.uniform(0, 2 * math.pi); rr = r.uniform(0.05, 0.33) * s
            sphere(r.uniform(0.025, 0.06) * s, (x + rr * math.cos(a), y + rr * math.sin(a), z + r.uniform(1.0, 2.05) * s), gas, seg=16)
    d = sphere(0.42 * s, (x, y, z + 2.2 * s), alu)
    d.scale.z = 0.35
    cyl(0.2 * s, 0.25 * s, (x, y, z + 2.42 * s), mat("cap", (0.9, 0.9, 0.92), rough=0.3))
    box((0.12 * s, 0.12 * s, 0.12 * s), (x + 0.16 * s, y, z + 2.5 * s), mat("noz", (0.1, 0.1, 0.1), rough=0.5))
    return o

def mist(origin, n=70, spread=2.2, seed=3):
    r = random.Random(seed)
    m = mat("mist", (0.8, 0.9, 1), emit=(0.7, 0.85, 1), strength=2.5)
    ox, oy, oz = origin
    for i in range(n):
        d = r.uniform(0.15, spread)
        sphere(0.015 + 0.03 * d, (ox + d, oy + r.uniform(-0.2, 0.2) * d, oz + r.uniform(-0.12, 0.25) * d), m, seg=12)

def country(name, lon0, lat0, k, height, m, z=0.0, keep=1.0):
    gj = json.load(open(GEO))
    for f in gj["features"]:
        if f["properties"].get("ADMIN") != name:
            continue
        g = f["geometry"]
        for poly in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]):
            ring = poly[0]
            lons = [p[0] for p in ring]; lats = [p[1] for p in ring]
            if (max(lons) - min(lons)) * (max(lats) - min(lats)) < keep:
                continue
            if len(ring) > 900:
                ring = ring[:: len(ring) // 900 + 1]
            me = bpy.data.meshes.new(name)
            bm = bmesh.new()
            vs = [bm.verts.new(((lo - lon0) * math.cos(math.radians(lat0)) * k, (la - lat0) * k, z)) for lo, la in ring[:-1]]
            try:
                face = bm.faces.new(vs)
            except ValueError:
                bm.free(); continue
            ext = bmesh.ops.extrude_face_region(bm, geom=[face])
            for v in [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]:
                v.co.z += height
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(me); bm.free()
            o = bpy.data.objects.new(name, me)
            bpy.context.collection.objects.link(o)
            o.data.materials.append(m)
            bv = o.modifiers.new("b", "BEVEL"); bv.width = 0.03; bv.segments = 2; bv.limit_method = "ANGLE"

def ll(lon, lat, lon0, lat0, k):
    return ((lon - lon0) * math.cos(math.radians(lat0)) * k, (lat - lat0) * k)

def school(loc, s=1.0):
    x, y, z = loc
    wall = mat("wall", (0.85, 0.82, 0.75), rough=0.6)
    roof = mat("roof", (0.55, 0.12, 0.1), rough=0.5)
    box((1.4 * s, 0.7 * s, 0.6 * s), (x, y, z + 0.3 * s), wall)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.05 * s, depth=0.45 * s, location=(x, y, z + 0.82 * s), rotation=(0, 0, math.radians(45)))
    o = bpy.context.object; o.scale = (1.0, 0.55, 1.0); assign(o, roof, smooth=False)
    win = mat("win", (0.3, 0.6, 0.9), emit=(1, .8, .4), strength=2)
    for i in range(4):
        box((0.16 * s, 0.02 * s, 0.18 * s), (x - 0.5 * s + i * 0.33 * s, y - 0.36 * s, z + 0.35 * s), win)
    cyl(0.015 * s, 0.9 * s, (x + 0.85 * s, y, z + 0.45 * s), mat("pole", (.8, .8, .8), metal=1, rough=.2))

def pin(loc, s=1.0):
    x, y, z = loc
    m = mat("pin", (1, 0.8, 0.05), rough=0.25, emit=(1, .7, 0), strength=0.6)
    sphere(0.22 * s, (x, y, z + 0.75 * s), m)
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.17 * s, depth=0.55 * s, location=(x, y, z + 0.42 * s), rotation=(math.pi, 0, 0))
    assign(bpy.context.object, m)

def figurine(loc, m, s=1.0):
    x, y, z = loc
    cyl(0.11 * s, 0.32 * s, (x, y, z + 0.16 * s), m, verts=24)
    sphere(0.09 * s, (x, y, z + 0.42 * s), m, seg=16)


# ----------------------------------------------------------------------------- shots
SHOTS = {}
def shot(f):
    SHOTS[f.__name__] = f
    return f

@shot
def spray_can():
    reset(); platform()
    can(paint=(0.05, 0.16, 0.6)); mist((0.3, 0, 2.5))
    t = target((0.3, 0, 1.3)); lights(t); camera((0, -7.5, 2.3), t)
    render("spray_can", 32)

@shot
def australia_school():
    reset(); platform(r=3.0)
    k = 0.072
    country("Australia", 134, -27, k, 0.22, mat("land", (0.75, 0.05, 0.06), rough=0.3), z=0.0)
    sx, sy = ll(151.2, -33.9, 134, -27, k)
    school((sx - 0.35, sy + 0.2, 0.22), 0.7)
    pin((sx + 0.25, sy - 0.25, 0.22), 0.8)
    t = target((0, -0.1, 0.3)); lights(t); camera((0, -8.4, 6.0), t, 38)
    render("australia_school", 32)

@shot
def lungs():
    reset(); platform()
    pink = mat("lung", (0.85, 0.35, 0.4), rough=0.45, sss=0.3)
    for sx in (-0.62, 0.62):
        o = sphere(0.62, (sx, 0, 1.45), pink, scale=(0.85, 0.6, 1.35))
    cyl(0.12, 1.0, (0, 0, 2.55), mat("trach", (0.9, 0.75, 0.75), rough=0.4), verts=32)
    br = mat("br", (0.9, 0.75, 0.75), rough=0.4)
    cyl_between((0, 0, 2.08), (-0.45, 0, 1.75), 0.09, br)
    cyl_between((0, 0, 2.08), (0.45, 0, 1.75), 0.09, br)
    r = random.Random(2)
    irr = mat("irr", (1, .1, .05), emit=(1, .08, .02), strength=6)
    for i in range(36):  # irritation hot-spots
        sx = r.choice((-0.62, 0.62))
        sphere(r.uniform(0.03, 0.07), (sx + r.uniform(-0.4, 0.4), -0.36, 1.45 + r.uniform(-0.6, 0.7)), irr, seg=12)
    mist((-2.6, -0.6, 2.4), n=50, spread=1.6, seed=7)
    t = target((0, 0, 1.5)); lights(t, rimc=(1, .4, .4)); camera((0, -7.2, 2.1), t)
    render("lungs", 32)

@shot
def recall_shelf():
    reset(); platform(r=3.0)
    cols = [(0.05, 0.16, 0.6), (0.55, 0.05, 0.1), (0.05, 0.35, 0.2), (0.6, 0.6, 0.62)]
    for row in range(3):
        for c in range(4):
            x = -1.65 + c * 1.1
            y = -0.9 + row * 1.0
            can((x, y, 0), 0.55, paint=cols[(c + row) % 4], label="")
    t = target((0, 0.1, 0.6)); lights(t); camera((0, -10.5, 4.6), t, 40)
    render("recall_shelf", 32)

@shot
def benzene():
    reset()
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, -3))
    assign(bpy.context.object, mat("floor", (0.02, 0.02, 0.025), rough=0.5))
    C = mat("C", (0.12, 0.12, 0.14), rough=0.25, metal=0.3)
    Hm = mat("H", (0.95, 0.95, 0.97), rough=0.2)
    bond = mat("bond", (0.75, 0.75, 0.8), rough=0.3, metal=0.5)
    rc, rh = 1.35, 2.35
    pc = [(rc * math.cos(i * math.pi / 3), 0, rc * math.sin(i * math.pi / 3) + 1.6) for i in range(6)]
    ph = [(rh * math.cos(i * math.pi / 3), 0, rh * math.sin(i * math.pi / 3) + 1.6) for i in range(6)]
    for i in range(6):
        sphere(0.36, pc[i], C); sphere(0.24, ph[i], Hm)
        cyl_between(pc[i], ph[i], 0.07, bond)
        a, b = Vector(pc[i]), Vector(pc[(i + 1) % 6])
        cyl_between(a, b, 0.08, bond)
        if i % 2 == 0:
            ctr = Vector((0, 0, 1.6))
            off = lambda p: p + (ctr - p) * 0.2
            cyl_between(off(a) + (b - a) * 0.15, off(b) + (a - b) * 0.15, 0.06, bond)
    for o in bpy.data.objects:  # tilt the molecule for depth
        if o.type == "MESH" and o.location.z > -2:
            o.location.rotate(__import__("mathutils").Euler((0.35, 0.0, 0.5)))
    bpy.ops.object.light_add(type="POINT", location=(0, 3, 1.6))
    o = bpy.context.object; o.data.energy = 3000; o.data.color = (1, 0.1, 0.05); o.data.shadow_soft_size = 2
    t = target((0, 0, 1.6)); lights(t, rimc=(1, .3, .2)); camera((0, -13.5, 1.9), t, 45)
    render("benzene", 32)

@shot
def test_tubes():
    reset(); platform()
    box((3.2, 0.7, 0.12), (0, 0, 0.55), mat("rack", (0.85, 0.85, 0.88), rough=0.3))
    for xx in (-1.45, 1.45):
        box((0.12, 0.7, 0.55), (xx, 0, 0.28), mat("rack", (0.85, 0.85, 0.88), rough=0.3))
    glass = mat("glass", (1, 1, 1), rough=0.02, glass=True)
    liq = [(0.2, 0.6, 0.9), (0.2, 0.8, 0.4), (1.0, 0.15, 0.1), (0.9, 0.8, 0.2), (0.6, 0.3, 0.9)]
    for i in range(5):
        x = -1.1 + i * 0.55
        cyl(0.17, 1.5, (x, 0, 1.05), glass, verts=48, fill="NOTHING")
        sphere(0.17, (x, 0, 0.3), glass, seg=32)
        strong = 8 if i == 2 else 0.6
        cyl(0.15, 0.7, (x, 0, 0.62), mat(f"liq{i}", liq[i], rough=0.1, emit=liq[i], strength=strong), verts=48)
    t = target((0, 0, 0.9)); lights(t); camera((0.4, -5.6, 2.2), t, 50)
    render("test_tubes", 64)

@shot
def can_cutaway():
    reset(); platform()
    can(paint=(0.05, 0.16, 0.6), cut=True, scale=1.15)
    t = target((0, 0, 1.3)); lights(t, key=1100); camera((-1.6, -6.6, 2.6), t, 45)
    render("can_cutaway", 48)

@shot
def uk_map():
    reset(); platform(r=3.0)
    k = 0.42
    country("United Kingdom", -3.2, 54.5, k, 0.22, mat("land", (0.75, 0.05, 0.06), rough=0.3), keep=0.3)
    country("Ireland", -3.2, 54.5, k, 0.12, mat("land2", (0.2, 0.2, 0.24), rough=0.4), keep=0.3)
    x, y = ll(-1.5, 52.5, -3.2, 54.5, k)
    pin((x, y, 0.22), 0.8)
    t = target((0, -0.2, 0.3)); lights(t); camera((0, -6.2, 5.6), t, 40)
    render("uk_map", 32)

@shot
def perfume():
    reset(); platform()
    glass = mat("glass", (1, 1, 1), rough=0.02, glass=True)
    box((1.3, 0.8, 1.5), (0, 0, 0.8), glass, bevel=0.15)
    box((1.05, 0.58, 0.95), (0, 0, 0.6), mat("amber", (1, 0.55, 0.1), rough=0.05, glass=True, emit=(1, .4, .05), strength=1.2), bevel=0.1)
    cyl(0.18, 0.3, (0, 0, 1.7), mat("gold", (1, .75, .3), metal=1, rough=.15), verts=48)
    box((0.5, 0.5, 0.45), (0, 0, 2.05), mat("gold", (1, .75, .3), metal=1, rough=.15), bevel=0.06)
    q = mat("q", (1, .85, .2), emit=(1, .75, .1), strength=5)
    r = random.Random(5)
    for i in range(9):
        a = i / 9 * 2 * math.pi
        x, z = 2.0 * math.cos(a), 1.4 + 1.1 * math.sin(a)
        text3d("?", (x, r.uniform(-0.3, 0.3), z), r.uniform(0.35, 0.6), q, extrude=0.06)
    t = target((0, 0, 1.2)); lights(t); camera((0, -7.6, 2.0), t, 45)
    render("perfume", 64)

@shot
def figurines():
    reset(); platform(r=3.2)
    red = mat("red", (0.9, 0.07, 0.05), rough=0.35, emit=(1, .05, .02), strength=0.6)
    grey = mat("grey", (0.45, 0.46, 0.5), rough=0.45)
    idx = 0
    for row in range(10):
        for c in range(10):
            x = -2.0 + c * 0.44
            y = -2.0 + row * 0.44
            figurine((x, y, 0), red if (row * 10 + c) < 42 else grey, 1.25)
    t = target((0, 0.1, 0.2)); lights(t); camera((0, -9.0, 6.6), t, 38)
    render("figurines", 32)

@shot
def question():
    reset(); platform()
    can(paint=(0.05, 0.16, 0.6), loc=(-0.9, 0, 0), scale=0.85)
    text3d("?", (0.9, 0, 1.5), 2.6, mat("qq", (1, .7, .15), emit=(1, .6, .1), strength=6), extrude=0.25)
    t = target((0, 0, 1.3)); lights(t); camera((0, -7.6, 2.0), t, 45)
    render("question", 32)


if __name__ == "__main__":
    for name, f in SHOTS.items():
        if ONLY and name not in ONLY:
            continue
        f()
