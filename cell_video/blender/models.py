"""Inside the Cell: 3D model previews (Blender / Cycles, all geometry procedural).

  python models.py -- [--only cell,membrane,dna,mito,ribosome] [--spp 64] [--res 1600x900]
  -> ../models/<name>.png      then: python3 post.py  (bloom + vignette -> ../models/final/)

Look: medical-visualisation style: translucent glowing membranes (fresnel rim), organelles with
subsurface scattering and a soft inner glow, dark blue-violet space, shallow depth of field.
"""
import bpy, bmesh, sys, os, math, random
import numpy as np
from mathutils import Vector, Matrix, noise

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "models"); os.makedirs(OUT, exist_ok=True)
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(n, d):
    return type(d)(argv[argv.index(n) + 1]) if n in argv else d
ONLY = [s for s in arg("--only", "").split(",") if s]
SPP = arg("--spp", 64)
EMIT = float(os.environ.get("EMIT", "0.35"))   # global scale on self-glow
LIGHT = float(os.environ.get("LIGHT", "0.3"))  # global scale on lamps
EXPO = float(os.environ.get("EXPO", "-0.6"))
RX, RY = (int(v) for v in arg("--res", "1600x900").split("x"))


# ----------------------------------------------------------------------------- scene helpers
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"
    sc.cycles.samples = SPP; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.03
    sc.cycles.use_denoising = True; sc.cycles.max_bounces = 6; sc.cycles.transparent_max_bounces = 24
    sc.render.resolution_x, sc.render.resolution_y = RX, RY
    sc.view_settings.view_transform = "Filmic"; sc.view_settings.look = "Medium High Contrast"
    sc.view_settings.exposure = EXPO
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    nt = w.node_tree; bg = nt.nodes["Background"]
    # soft vertical gradient: deep violet above, navy below
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.004, 0.008, 0.025, 1); ramp.color_ramp.elements[1].color = (0.03, 0.012, 0.05, 1)
    nt.links.new(sep.outputs["Z"], ramp.inputs[0]); nt.links.new(ramp.outputs[0], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0
    return sc


def nodes(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    return m, nt, nt.nodes.new("ShaderNodeOutputMaterial")


def organic(name, col, emit=0.4, sss=0.4, rough=0.35, coat=0.3, bump=0.25, bscale=6.0):
    """Organelle surface: SSS + soft self-glow + fine bumpy detail."""
    m, nt, out = nodes(name)
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = (*col, 1); p.inputs["Roughness"].default_value = rough
    p.inputs["Subsurface Weight"].default_value = sss * 0.6; p.inputs["Subsurface Radius"].default_value = (1.0, 0.6, 0.4)
    p.inputs["Subsurface Scale"].default_value = 0.3
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Emission Color"].default_value = (*col, 1); p.inputs["Emission Strength"].default_value = emit * EMIT
    if bump:
        tx = nt.nodes.new("ShaderNodeTexNoise"); tx.inputs["Scale"].default_value = bscale; tx.inputs["Detail"].default_value = 8
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
        nt.links.new(tx.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    nt.links.new(p.outputs[0], out.inputs["Surface"])
    return m


def glass(name, col, rim=3.0, power=2.2, body=0.04):
    """Translucent membrane: almost clear face-on, glowing at grazing angles, faint gloss."""
    m, nt, out = nodes(name)
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.3
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = power
    nt.links.new(lw.outputs["Facing"], pw.inputs[0])
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = "MULTIPLY_ADD"; mu.inputs[1].default_value = rim; mu.inputs[2].default_value = body
    nt.links.new(pw.outputs[0], mu.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*col, 1)
    nt.links.new(mu.outputs[0], em.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    gl = nt.nodes.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = 0.15
    a1 = nt.nodes.new("ShaderNodeAddShader"); nt.links.new(tr.outputs[0], a1.inputs[0]); nt.links.new(em.outputs[0], a1.inputs[1])
    mx = nt.nodes.new("ShaderNodeMixShader"); mx.inputs["Fac"].default_value = 0.12
    nt.links.new(a1.outputs[0], mx.inputs[1]); nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return m


def glow(name, col, s=4.0):
    m, nt, out = nodes(name)
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (*col, 1); e.inputs["Strength"].default_value = s * EMIT * 1.5
    nt.links.new(e.outputs[0], out.inputs["Surface"]); return m


def link(obj):
    bpy.context.scene.collection.objects.link(obj); return obj


def mesh_obj(name, bm, mat=None, smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me))
    if smooth:
        for p in me.polygons: p.use_smooth = True
    if mat: me.materials.append(mat)
    return o


def sphere(name, r=1.0, loc=(0, 0, 0), scale=(1, 1, 1), mat=None, sub=4):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    o = mesh_obj(name, bm, mat); o.location = loc; o.scale = scale; return o


def cyl(name, r, depth, mat=None, seg=24):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=depth)
    return mesh_obj(name, bm, mat)


def displace(o, strength, size, kind="CLOUDS", seed=0):
    t = bpy.data.textures.new(o.name + "_tx", kind)
    if kind == "CLOUDS":
        t.noise_scale = size; t.noise_depth = 2
    elif kind == "VORONOI":
        t.noise_scale = size
    d = o.modifiers.new("disp", "DISPLACE"); d.texture = t; d.strength = strength; d.texture_coords = "GLOBAL" if not seed else "LOCAL"
    return d


def subsurf(o, lv=2):
    m = o.modifiers.new("sub", "SUBSURF"); m.levels = lv; m.render_levels = lv; return m


def solidify(o, t):
    m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = t; m.offset = 0; return m


def cut(o, cutter):
    b = o.modifiers.new("cut", "BOOLEAN"); b.operation = "DIFFERENCE"; b.object = cutter
    for s in ("EXACT", "FLOAT", "MANIFOLD", "FAST"):
        try:
            b.solver = s; break
        except TypeError:
            pass
    return b


def box_cutter(name, loc, size):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    o = mesh_obj(name, bm, smooth=False); o.location = loc; o.scale = size
    o.hide_render = True; o.display_type = "WIRE"; return o


def tube(name, pts, r, mat, res=6):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"
    cu.bevel_depth = r; cu.bevel_resolution = res; cu.use_fill_caps = True
    sp = cu.splines.new("POLY" if len(pts) > 40 else "NURBS"); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1)
    if sp.type == "NURBS":
        sp.order_u = 4; sp.use_endpoint_u = True; sp.resolution_u = 12
    o = link(bpy.data.objects.new(name, cu)); cu.materials.append(mat); return o


def instance_on(name, points, normals, child, align=True):
    """Instances `child` at each point (vertex instancing), oriented to the normal (child's +Z)."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(p) for p in points], [], [])
    if normals is not None:
        me.vertices.foreach_set("co", np.array(points, np.float32).ravel())
    par = link(bpy.data.objects.new(name, me))
    par.instance_type = "VERTS"; par.use_instance_vertices_rotation = align and normals is not None
    if normals is not None:
        # vertex normals of a point cloud are not stored: build tiny faces instead
        bm = bmesh.new()
        for p, n in zip(points, normals):
            n = Vector(n).normalized(); t = n.orthogonal().normalized() * 1e-4; b = n.cross(t)
            vs = [bm.verts.new(Vector(p) + d) for d in (t, b, -t - b)]
            f = bm.faces.new(vs)
            if f.normal.dot(n) < 0: f.normal_flip()
        bm.to_mesh(me); bm.free()
        par.instance_type = "FACES"; par.use_instance_faces_scale = False
    child.parent = par; child.track_axis = "POS_Z"; child.up_axis = "Y"
    child.location = (0, 0, 0)
    return par


def light(kind, loc, energy, col=(1, 1, 1), size=5.0, target=(0, 0, 0)):
    d = bpy.data.lights.new("L", kind); d.energy = energy * LIGHT; d.color = col
    if kind == "AREA": d.size = size
    o = link(bpy.data.objects.new("L", d)); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); return o


def camera(loc, target, lens=50, fstop=2.8, focus=None):
    c = bpy.data.cameras.new("cam"); c.lens = lens; c.sensor_width = 36
    c.dof.use_dof = True; c.dof.aperture_fstop = fstop
    c.dof.focus_distance = focus if focus else (Vector(target) - Vector(loc)).length
    o = link(bpy.data.objects.new("cam", c)); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = o; return o


def dust(n, center, radius, mat, rmin=0.02, rmax=0.08, seed=1, avoid=None):
    """Floating particles (out-of-focus bokeh)."""
    rng = np.random.default_rng(seed); bm = bmesh.new()
    c = Vector(center)
    for _ in range(n):
        p = c + Vector(rng.normal(0, 1, 3)).normalized() * radius * rng.uniform(0.2, 1) ** 0.5
        if avoid and avoid(p):
            continue
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=rng.uniform(rmin, rmax), matrix=Matrix.Translation(p))
    return mesh_obj("dust", bm, mat)


def render(name):
    p = os.path.join(OUT, name + ".png")
    bpy.context.scene.render.filepath = p
    bpy.ops.render.render(write_still=True)
    print("RENDERED", p, flush=True)


def rand_in_sphere(rng, R):
    while True:
        p = rng.uniform(-R, R, 3)
        if np.linalg.norm(p) < R:
            return Vector(p)


# ============================================================================ 1. whole cell cutaway
def m_cell():
    reset(); rng = np.random.default_rng(3)
    R = 10.0
    # cut away the front-right quarter so we can look inside
    cutter = box_cutter("cutter", (6, -6, 3), (12, 12, 26))
    mem = sphere("membrane", R, mat=glass("g_mem", (0.25, 0.55, 1.0), rim=4.0), sub=5)
    displace(mem, 0.35, 4.0); solidify(mem, 0.18); cut(mem, cutter)
    # the cut edge of the membrane: a thin glowing rim is produced by solidify faces (same glass)
    # cytoplasm haze: a faint inner shell
    cyto = sphere("cyto", R * 0.985, mat=glass("g_cyto", (0.35, 0.2, 0.7), rim=0.6, body=0.01), sub=4); cut(cyto, cutter)

    NUC = Vector((-0.8, 0.6, 0.3)); RN = 3.6
    nuc_cut = box_cutter("ncut", NUC + Vector((3.2, -3.2, 2.2)), (6.5, 6.5, 6.5))
    nuc = sphere("nucleus", RN, loc=NUC, mat=organic("m_nuc", (0.12, 0.25, 0.9), emit=0.5, sss=0.6), sub=5)
    displace(nuc, 0.18, 1.5); solidify(nuc, 0.2); cut(nuc, nuc_cut)
    # chromatin inside: tangled glowing threads
    chrom = organic("m_chrom", (0.35, 0.55, 1.0), emit=1.6, sss=0.2, bump=0)
    for k in range(14):
        p = NUC + rand_in_sphere(rng, RN * 0.6); pts = [p]
        for _ in range(40):
            p = p + Vector(rng.normal(0, 0.35, 3))
            if (p - NUC).length > RN * 0.85: p = NUC + (p - NUC) * 0.8
            pts.append(p)
        tube(f"chrom{k}", [tuple(q) for q in pts], 0.05, chrom)
    sphere("nucleolus", 1.0, loc=NUC + Vector((0.6, -0.5, 0.4)), mat=organic("m_ncl", (0.55, 0.2, 0.9), emit=1.2), sub=4)
    # nuclear pores: little rings over the uncut surface
    pore = bpy.data.objects.new("pore", None)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=12, radius1=0.16, radius2=0.12, depth=0.12)
    pore = mesh_obj("pore", bm, organic("m_pore", (0.6, 0.85, 1.0), emit=1.0))
    solidify(pore, 0.05)
    pts, nrm = [], []
    for _ in range(260):
        n = Vector(rng.normal(0, 1, 3)).normalized(); q = NUC + n * (RN + 0.12)
        if not (q.x > NUC.x and q.y < NUC.y and q.z < NUC.z + 5.5):
            pts.append(q); nrm.append(n)
    instance_on("pores", pts, nrm, pore)

    # rough ER: wavy sheets wrapped round the nucleus (back / left side), studded with ribosomes
    er = organic("m_er", (0.95, 0.25, 0.55), emit=0.35, sss=0.5)
    ribo = sphere("ribo", 0.07, mat=organic("m_ribo", (0.5, 0.9, 1.0), emit=2.0, bump=0), sub=1)
    rp, rn = [], []
    for k, rr in enumerate((RN + 0.9, RN + 1.6, RN + 2.3)):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=96, v_segments=48, radius=rr)
        kill = [v for v in bm.verts if (v.co.x > -0.3 * rr and v.co.y < 0.4 * rr) or abs(v.co.z) > 0.7 * rr]
        bmesh.ops.delete(bm, geom=kill, context="VERTS")
        for v in bm.verts:
            v.co += v.normal * 0.22 * math.sin(v.co.z * 2.2 + k) + v.normal * 0.15 * noise.noise(v.co * 0.7)
        o = mesh_obj(f"er{k}", bm, er); o.location = NUC; solidify(o, 0.14); subsurf(o, 1)
        for v in list(o.data.vertices)[::7]:
            rp.append(NUC + v.co + v.normal * 0.12); rn.append(v.normal)
    instance_on("ribos", rp, rn, ribo, align=False)

    # Golgi: stack of curved flattened sacs + budding vesicles
    G = Vector((4.2, 3.6, -1.8))
    gm = organic("m_golgi", (1.0, 0.65, 0.12), emit=0.6, sss=0.5)
    for i in range(6):
        s = sphere(f"golgi{i}", 1.0, mat=gm, sub=4)
        s.scale = (2.4 - 0.18 * abs(i - 2.5), 1.0, 0.14)
        bd = s.modifiers.new("bend", "SIMPLE_DEFORM"); bd.deform_method = "BEND"; bd.angle = math.radians(70); bd.deform_axis = "Y"
        s.location = G + Vector((0, 0, i * 0.38)); s.rotation_euler = (0.5, -0.3, 0.9)
    vm = organic("m_vesicle", (1.0, 0.8, 0.35), emit=0.9, sss=0.3, bump=0)
    for i in range(22):
        sphere(f"ves{i}", rng.uniform(0.12, 0.25), loc=G + Vector(rng.normal(0, 1.4, 3)), mat=vm, sub=2)

    # mitochondria: capsules with glowing cristae stripes
    mm, nt, out = nodes("m_mito")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled"); p.inputs["Base Color"].default_value = (1.0, 0.35, 0.08, 1)
    p.inputs["Subsurface Weight"].default_value = 0.5; p.inputs["Roughness"].default_value = 0.35; p.inputs["Coat Weight"].default_value = 0.4
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.bands_direction = "X"; wv.inputs["Scale"].default_value = 2.2; wv.inputs["Distortion"].default_value = 6
    tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; mu.inputs[1].default_value = 0.7
    nt.links.new(wv.outputs["Fac"], mu.inputs[0])
    p.inputs["Emission Color"].default_value = (1.0, 0.45, 0.1, 1); nt.links.new(mu.outputs[0], p.inputs["Emission Strength"])
    nt.links.new(p.outputs[0], out.inputs["Surface"])
    placed = []
    for i in range(9):
        for _ in range(200):
            q = rand_in_sphere(rng, R - 2.0)
            if (q - NUC).length > RN + 3.0 and (q - G).length > 3.0 and all((q - z).length > 2.6 for z in placed):
                break
        placed.append(q)
        s = sphere(f"mito{i}", 1.0, loc=q, mat=mm, sub=4)
        s.scale = (rng.uniform(1.3, 1.9), 0.55, 0.55); s.rotation_euler = tuple(rng.uniform(0, 3.14, 3))
        displace(s, 0.08, 0.6)
    # lysosomes + peroxisome-like bodies
    lm = organic("m_lyso", (0.35, 1.0, 0.45), emit=0.9, sss=0.4)
    for i in range(7):
        for _ in range(200):
            q = rand_in_sphere(rng, R - 1.5)
            if (q - NUC).length > RN + 2.6 and all((q - z).length > 1.8 for z in placed):
                break
        placed.append(q); sphere(f"lyso{i}", rng.uniform(0.35, 0.6), loc=q, mat=lm, sub=3)
    # centrioles: two perpendicular barrels near the nucleus
    cm = organic("m_centriole", (0.9, 0.9, 0.3), emit=1.2, bump=0)
    C = NUC + Vector((2.6, -1.2, -3.4))
    for k, rot in enumerate(((0, 0, 0), (math.pi / 2, 0, 0))):
        c = cyl(f"centriole{k}", 0.2, 0.7, cm); c.location = C + Vector((0.3 * k, 0, 0)); c.rotation_euler = rot
    # cytoskeleton: thin glowing filaments criss-crossing the cell
    fm = glow("m_fil", (0.4, 0.8, 1.0), 2.5)
    for k in range(40):
        a = rand_in_sphere(rng, R - 0.8); d = Vector(rng.normal(0, 1, 3)).normalized(); pts = []
        for j in range(12):
            q = a + d * j * 1.4 + Vector(rng.normal(0, 0.25, 3))
            if q.length > R - 0.5: break
            pts.append(tuple(q))
        if len(pts) > 3: tube(f"fil{k}", pts, 0.025, fm, res=2)
    # cytoplasm specks
    dust(500, (0, 0, 0), R - 0.6, glow("m_speck", (0.6, 0.5, 1.0), 2.0), 0.02, 0.05, seed=4,
         avoid=lambda p: (p - NUC).length < RN + 0.4)
    # background cells, far and out of focus
    for k, (pos, r) in enumerate((((-42, 70, 12), 10), ((40, 80, -14), 12), ((-6, 110, -30), 14))):
        b = sphere(f"bgcell{k}", r, loc=pos, mat=glass(f"g_bg{k}", (0.3, 0.4, 1.0), rim=2.0), sub=4); displace(b, 0.5, 4)
    dust(150, (0, 10, 0), 40, glow("m_bokeh", (0.5, 0.6, 1.0), 3.0), 0.05, 0.15, seed=9, avoid=lambda p: p.length < R + 1)
    light("AREA", (14, -18, 16), 9000, (0.85, 0.9, 1.0), 12)
    light("AREA", (-16, 18, 6), 5000, (0.6, 0.4, 1.0), 14)
    light("POINT", NUC + Vector((2, -2, 1)), 400, (0.6, 0.7, 1.0))
    camera((23, -26, 11.5), (0.5, 0.2, -0.4), lens=42, fstop=4.0)
    render("01_cell_cutaway")


# ============================================================================ 2. cell membrane
def m_membrane():
    reset(); rng = np.random.default_rng(7)
    head_m = organic("m_head", (0.25, 0.6, 1.0), emit=0.5, sss=0.4, bump=0.1, bscale=20)
    tail_m = organic("m_tail", (1.0, 0.75, 0.25), emit=0.25, sss=0.5, bump=0)
    # one phospholipid: head bead + two slightly kinked tails, pointing -Z (to the bilayer centre)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=0.34)
    lip_head = mesh_obj("lip_head", bm, head_m)
    for side in (-1, 1):
        pts = [(0.1 * side, 0, -0.25), (0.12 * side, 0, -0.8), (0.18 * side, 0.05 * side, -1.3), (0.14 * side, 0, -1.75)]
        t = tube(f"tail{side}", pts, 0.07, tail_m, res=3); t.parent = lip_head
    W, D = 28, 14
    for z0, flip in ((2.05, 1), (-2.05, -1)):
        pts = []
        for i in range(W):
            for j in range(D):
                x = (i - W / 2) * 0.74 + rng.normal(0, 0.05); y = (j - 2) * 0.74 + rng.normal(0, 0.05)
                if (x - 1.2) ** 2 + (y - 2.2) ** 2 < 2.4 ** 2 or (x + 5.5) ** 2 + (y - 4.5) ** 2 < 2.1 ** 2 or (x - 7) ** 2 + (y - 7.5) ** 2 < 2.2 ** 2:
                    continue   # room for proteins
                pts.append((x, y, z0 + rng.normal(0, 0.06)))
        lip = lip_head if flip > 0 else lip_head.copy()
        if flip < 0:
            link(lip)
            for ch in lip_head.children:
                c2 = ch.copy(); link(c2); c2.parent = lip
            lip.rotation_euler = (math.pi, 0, 0)
        me = bpy.data.meshes.new(f"leaf{flip}"); me.from_pydata(pts, [], [])
        par = link(bpy.data.objects.new(f"leaf{flip}", me)); par.instance_type = "VERTS"
        lip.parent = par; lip.location = (0, 0, 0)
    # transmembrane proteins: blobby, glossy, spanning the bilayer
    for k, (x, y, col, sc) in enumerate(((-5.5, 4.5, (0.65, 0.25, 0.95), (1.8, 1.7, 3.3)), (7, 7.5, (0.15, 0.85, 0.75), (1.9, 1.9, 3.0)))):
        p = sphere(f"prot{k}", 1.0, loc=(x, y, 0.2), mat=organic(f"m_prot{k}", col, emit=0.5, sss=0.6), sub=5)
        p.scale = sc; displace(p, 0.45, 0.45)
    # ion channel: ring of 5 subunits with an open pore + ions passing through
    C = Vector((1.2, 2.2, 0))
    chm = organic("m_chan", (0.95, 0.3, 0.45), emit=0.6, sss=0.6)
    for k in range(5):
        a = k / 5 * 2 * math.pi
        s = sphere(f"chan{k}", 1.0, loc=C + Vector((math.cos(a) * 1.25, math.sin(a) * 1.25, 0.1)), mat=chm, sub=4)
        s.scale = (0.75, 0.75, 3.1); s.rotation_euler = (0, 0, a); displace(s, 0.25, 0.4)
    ion = organic("m_ion", (1.0, 0.85, 0.2), emit=4.0, bump=0)
    for k, z in enumerate((4.2, 2.5, 0.6, -1.6, -3.6)):
        sphere(f"ion{k}", 0.28, loc=C + Vector((rng.normal(0, 0.1), rng.normal(0, 0.1), z)), mat=ion, sub=3)
    for k in range(14):
        sphere(f"ionf{k}", 0.25, loc=(rng.uniform(-10, 10), rng.uniform(-2, 10), rng.uniform(3.5, 7)), mat=ion, sub=2)
    # sugar chains (glycocalyx) on top of proteins
    sug = organic("m_sugar", (0.4, 1.0, 0.6), emit=1.2, bump=0)
    for base in ((-5.5, 4.5, 3.3), (7, 7.5, 3.0), (-2.5, 9, 2.6)):
        p = Vector(base)
        for j in range(7):
            p = p + Vector((rng.normal(0, 0.25), rng.normal(0, 0.25), 0.45))
            sphere("sugar", 0.17, loc=tuple(p), mat=sug, sub=2)
            if j == 3:
                q = p.copy()
                for _ in range(3):
                    q = q + Vector((0.4, rng.normal(0, 0.2), 0.3)); sphere("sugar", 0.15, loc=tuple(q), mat=sug, sub=2)
    dust(250, (0, 6, 2), 18, glow("m_water", (0.5, 0.7, 1.0), 1.5), 0.03, 0.08, seed=2)
    light("AREA", (-8, -14, 14), 4500, (0.85, 0.9, 1.0), 10, (0, 3, 0))
    light("AREA", (10, 16, 4), 3500, (0.5, 0.4, 1.0), 10, (0, 3, 0))
    light("AREA", (0, -6, -10), 1500, (1.0, 0.6, 0.3), 10, (0, 3, 0))
    camera((-2.5, -13.0, 9.0), (1.0, 3.5, 0.3), lens=32, fstop=2.8, focus=15.5)
    render("02_membrane")


# ============================================================================ 3. DNA
def m_dna():
    reset(); rng = np.random.default_rng(5)
    bb = organic("m_backbone", (0.3, 0.55, 1.0), emit=0.8, sss=0.5, bump=0)
    COL = dict(A=(1.0, 0.25, 0.2), T=(1.0, 0.8, 0.15), G=(0.2, 0.9, 0.35), C=(0.2, 0.6, 1.0))
    PAIR = dict(A="T", T="A", G="C", C="G")
    bmat = {k: organic(f"m_{k}", c, emit=1.0, sss=0.3, bump=0) for k, c in COL.items()}
    N, rise, twist, R = 46, 0.34, 2 * math.pi / 10.5, 1.0
    off = math.radians(150)   # minor/major groove
    s1, s2 = [], []
    for i in range(N):
        a = i * twist; z = (i - N / 2) * rise
        p1 = Vector((R * math.cos(a), R * math.sin(a), z)); p2 = Vector((R * math.cos(a + off), R * math.sin(a + off), z))
        s1.append(p1); s2.append(p2)
        sphere("p1", 0.2, loc=tuple(p1), mat=bb, sub=2); sphere("p2", 0.2, loc=tuple(p2), mat=bb, sub=2)
        b = "ATGC"[rng.integers(4)]
        for (pa, pb, base) in ((p1, (p1 + p2) / 2, b), ((p1 + p2) / 2, p2, PAIR[b])):
            c = cyl("rung", 0.1, (pb - pa).length * 0.94, bmat[base], seg=12)
            c.location = (pa + pb) / 2; c.rotation_euler = (pb - pa).to_track_quat("Z", "Y").to_euler()
    tube("strand1", [tuple(p) for p in s1], 0.11, bb); tube("strand2", [tuple(p) for p in s2], 0.11, bb)
    g = bpy.data.objects.new("dna", None); link(g)
    for o in list(bpy.context.scene.objects):
        if o is not g and o.parent is None: o.parent = g
    g.rotation_euler = (math.radians(12), math.radians(90), math.radians(18))
    # background: chromatin = DNA wrapped around histone spools (beads on a string)
    hm = organic("m_histone", (0.85, 0.3, 0.6), emit=0.5, sss=0.6)
    lk = organic("m_linker", (0.3, 0.55, 1.0), emit=1.0, bump=0)
    path = []
    for k in range(9):
        c = Vector((-20 + k * 4.6, 26 + 3 * math.sin(k * 0.9), -9 + 2.5 * math.cos(k * 0.7)))
        h = cyl("histone", 1.1, 1.2, hm, seg=32); h.location = c; h.rotation_euler = (1.2, 0.3 * k, 0.4)
        subsurf(h, 2); displace(h, 0.12, 0.3)
        M = h.rotation_euler.to_matrix()
        for t in np.linspace(0, 1.65 * 2 * math.pi, 40):
            path.append(c + M @ Vector((1.35 * math.cos(t), 1.35 * math.sin(t), -0.55 + 1.1 * t / (3.3 * math.pi))))
    tube("chromatin", [tuple(p) for p in path], 0.2, lk)
    dust(120, (0, 8, 0), 18, glow("m_bok", (0.45, 0.4, 1.0), 1.2), 0.03, 0.12, seed=3)
    light("AREA", (-6, -9, 8), 2500, (0.9, 0.9, 1.0), 6)
    light("AREA", (7, 6, -3), 2000, (0.6, 0.4, 1.0), 8)
    camera((3.0, -19.0, 2.0), (0, 0, 0), lens=50, fstop=2.4)
    render("03_dna")


# ============================================================================ 4. mitochondrion
def m_mito():
    reset(); rng = np.random.default_rng(8)
    L, Rr = 6.0, 2.6
    cutter = box_cutter("cutter", (0, 0, 5.15), (20, 20, 10))   # removes the top half (z > 0.15)
    def capsule(name, r, l, mat):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=32, radius=r)
        for v in bm.verts:
            v.co.x += math.copysign(l / 2, v.co.x) if abs(v.co.x) > 1e-4 else 0
        return mesh_obj(name, bm, mat)
    outer = capsule("outer", Rr, L, glass("g_outer", (1.0, 0.55, 0.25), rim=3.5, body=0.06))
    solidify(outer, 0.14); cut(outer, cutter); displace(outer, 0.08, 1.2)
    im = organic("m_inner", (0.75, 0.18, 0.05), emit=0.4, sss=0.6, bscale=10)
    cm_ = organic("m_crista", (1.0, 0.42, 0.08), emit=0.45, sss=0.6, bscale=10)
    inner = capsule("inner", Rr - 0.35, L - 0.2, im); solidify(inner, 0.1); cut(inner, cutter)
    # cristae: shelf-like folds from alternating sides
    syn_pts, syn_n = [], []
    for k in range(9):
        x = -L / 2 - 0.6 + k * (L + 1.2) / 8
        rr = Rr - 0.45 - (0.9 if abs(x) > L / 2 else 0)
        bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=28, y_segments=28, size=rr)
        side = 1 if k % 2 else -1
        # a shelf growing from one side wall, reaching ~3/4 of the way across
        kill = [v for v in bm.verts if v.co.length > rr + 0.05 or v.co.y * side < -0.45 * rr]
        bmesh.ops.delete(bm, geom=kill, context="VERTS")
        for v in bm.verts:
            v.co.z += 0.18 * math.sin(v.co.x * 3 + k) + 0.1 * noise.noise(v.co * 1.5)
        o = mesh_obj(f"crista{k}", bm, cm_); o.rotation_euler = (0, math.pi / 2, 0); o.location = (x, 0, 0)
        solidify(o, 0.4); subsurf(o, 1); cut(o, cutter)
        M = o.matrix_world
        bpy.context.view_layer.update()
        for v in list(o.data.vertices)[::11]:
            w = o.matrix_world @ v.co
            if w.z < 0.0:
                for s in (1, -1):
                    syn_pts.append(w + Vector((s * 0.14, 0, 0))); syn_n.append(Vector((s, 0, 0)))
    # ATP synthase "lollipops" on the cristae
    sm = organic("m_synth", (1.0, 0.85, 0.3), emit=1.0, bump=0)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.025, radius2=0.025, depth=0.16,
                                            matrix=Matrix.Translation((0, 0, 0.08)))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.07, matrix=Matrix.Translation((0, 0, 0.19)))
    synth = mesh_obj("synth", bm, sm)
    instance_on("synths", syn_pts, syn_n, synth)
    # matrix: granules, ribosomes and a ring of mitochondrial DNA
    dust(160, (0, 0, -0.8), Rr - 0.6, glow("m_matrix", (1.0, 0.8, 0.5), 2.0), 0.02, 0.05, seed=1, avoid=lambda p: p.z > -0.1 or abs(p.y) > Rr - 0.6)
    ring = [(-1.9 + 0.55 * math.cos(t), 0.55 * math.sin(t) + 0.06 * math.sin(5 * t), -0.9) for t in np.linspace(0, 2 * math.pi, 60)]
    tube("mtDNA", ring, 0.04, glow("m_mtdna", (0.4, 0.8, 1.0), 4.0))
    # ATP sparks leaving
    ap = glow("m_atp", (1.0, 0.85, 0.3), 6.0)
    for k in range(30):
        sphere("atp", rng.uniform(0.04, 0.09), loc=(rng.uniform(-6, 6), rng.uniform(-4, 4), rng.uniform(0.8, 3.5)), mat=ap, sub=2)
    dust(150, (0, 6, -4), 16, glow("m_bok", (0.7, 0.4, 1.0), 2.5), 0.04, 0.12, seed=6, avoid=lambda p: abs(p.y) < 4 and abs(p.x) < 6)
    light("AREA", (-6, -10, 9), 3000, (0.9, 0.9, 1.0), 8)
    light("AREA", (8, 4, -6), 2000, (0.5, 0.4, 1.0), 10)
    camera((1.5, -7.5, 11.0), (0.0, 0.2, -0.6), lens=36, fstop=3.5)
    render("04_mitochondrion")


# ============================================================================ 5. ribosome
def m_ribosome():
    reset(); rng = np.random.default_rng(12)
    rc = box_cutter("rcut", (0, -3.3, 0.6), (14, 6, 14))
    small = sphere("small", 1.0, loc=(0, 0, -1.3), mat=organic("m_small", (0.35, 0.7, 1.0), emit=0.45, sss=0.7, bump=0.45, bscale=14), sub=5)
    small.scale = (2.6, 1.7, 1.15); displace(small, 0.22, 1.1); subsurf(small, 1)
    large = sphere("large", 1.0, loc=(0, 0.2, 1.25), mat=organic("m_large", (0.45, 0.25, 0.95), emit=0.45, sss=0.7, bump=0.45, bscale=14), sub=5)
    large.scale = (3.0, 2.2, 1.9); displace(large, 0.3, 1.2); subsurf(large, 1)
    cut(small, rc); cut(large, rc)
    # mRNA threading between the subunits, nucleotides coloured by codon
    COLS = [(1.0, 0.3, 0.2), (1.0, 0.8, 0.15), (0.2, 0.9, 0.35), (0.25, 0.6, 1.0)]
    nm = [organic(f"m_nt{i}", c, emit=1.4, bump=0) for i, c in enumerate(COLS)]
    path = [(x, -0.2 + 0.25 * math.sin(x * 0.5), -0.15 + 0.15 * math.cos(x * 0.7)) for x in np.linspace(-10, 10, 80)]
    tube("mrna", path, 0.08, organic("m_mrna", (0.9, 0.9, 1.0), emit=0.8, bump=0))
    for k, p in enumerate(path[::2]):
        sphere("nt", 0.14, loc=(p[0], p[1] - 0.12, p[2] - 0.12), mat=nm[rng.integers(4)], sub=2)
    # two tRNAs (L-shaped) sitting in the ribosome, amino acids on top
    tm = organic("m_trna", (0.3, 1.0, 0.7), emit=1.0, sss=0.4, bump=0)
    aa = [organic(f"m_aa{i}", c, emit=1.5, bump=0) for i, c in enumerate(
        [(1.0, 0.4, 0.6), (0.6, 0.9, 1.0), (1.0, 0.75, 0.3), (0.6, 1.0, 0.4), (0.85, 0.5, 1.0)])]
    for k, x in enumerate((-0.7, 0.7)):
        pts = [(x, -0.3, 0.05), (x, -0.5, 0.8), (x + 0.1, -0.6, 1.5), (x + 0.6, -0.7, 1.9), (x + 1.2, -0.75, 2.0)]
        tube(f"trna{k}", pts, 0.18, tm)
        sphere("anticodon", 0.22, loc=(x, -0.3, 0.05), mat=tm, sub=2)
    # growing protein chain leaving the exit tunnel, folding into a helix
    p = Vector((0.6, -0.5, 2.3)); pts = []
    for j in range(46):
        if j < 12:
            p = p + Vector((0.05, -0.05, 0.38))
        else:
            t = (j - 12) * 0.6
            p = Vector((0.6 + 1.0 * math.cos(t), -1.2 + 1.0 * math.sin(t), 6.6 + (j - 12) * 0.12))
        pts.append(p.copy()); sphere("aa", 0.26, loc=tuple(p), mat=aa[j % 5], sub=2)
    tube("peptide", [tuple(q) for q in pts], 0.07, organic("m_pep", (0.9, 0.9, 1.0), emit=0.6, bump=0))
    # background: more ribosomes on the same mRNA (polysome), out of focus
    for k, x in enumerate((-8.5, 8.5)):
        s2 = sphere("bg_small", 1.0, loc=(x, 0.4, -1.3), mat=small.data.materials[0], sub=4); s2.scale = (2.4, 1.6, 1.1)
        l2 = sphere("bg_large", 1.0, loc=(x, 0.6, 1.2), mat=large.data.materials[0], sub=4); l2.scale = (2.8, 2.0, 1.8)
    dust(120, (0, 8, 1), 16, glow("m_bok", (0.45, 0.4, 1.0), 1.2), 0.03, 0.12, seed=4)
    light("AREA", (-6, -10, 9), 2500, (0.9, 0.9, 1.0), 8)
    light("AREA", (7, 6, -2), 2000, (0.7, 0.4, 1.0), 8)
    camera((3.5, -16.0, 4.5), (0.4, 0, 2.6), lens=40, fstop=3.2)
    render("05_ribosome")


MODELS = dict(cell=m_cell, membrane=m_membrane, dna=m_dna, mito=m_mito, ribosome=m_ribosome)
for k, f in MODELS.items():
    if not ONLY or k in ONLY:
        f()
