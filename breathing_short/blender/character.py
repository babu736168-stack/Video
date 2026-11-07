"""Procedural set + rigged, clothed character built from the CC0 MakeHuman base mesh.

Everything here is code: clothing is painted onto the body by nearest-bone regions, hair is a displaced
scalp shell, eyebrows are shrink-wrapped strips, the rig is generated from the mesh's joint helpers and
skinned with Blender's automatic weights.
"""
import bpy, math, os, bmesh
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("CHAR_DATA", os.path.join(HERE, "..", "..", "sneeze_short", "data"))
DATA_OWN = os.path.join(HERE, "..", "data")
BASE_OBJ = os.path.join(DATA, "base.obj")
TARGETS = [("caucasian-male-young.target", 1.0), ("universal-male-young-maxmuscle-averageweight.target", float(os.environ.get("MUSCLE", "0.15")))]


def morphed_obj():
    """Applies MakeHuman (CC0) morph targets to base.obj and caches the result."""
    tag = "_".join(f"{w:g}" for _, w in TARGETS)
    out = os.path.join(DATA_OWN, f"base_morphed_{tag}.obj")
    if os.path.exists(out):
        return out
    lines = open(BASE_OBJ).read().split("\n")
    vidx = [i for i, l in enumerate(lines) if l.startswith("v ")]
    V = np.array([[float(x) for x in lines[i].split()[1:4]] for i in vidx])
    for name, w in TARGETS:
        for l in open(os.path.join(DATA, name)):
            if l.strip() and not l.startswith("#"):
                i, dx, dy, dz = l.split()[:4]
                V[int(i)] += w * np.array([float(dx), float(dy), float(dz)])
    for k, i in enumerate(vidx):
        lines[i] = "v %.5f %.5f %.5f" % tuple(V[k])
    open(out, "w").write("\n".join(lines))
    return out
J = {}  # joint name -> world position (metres)
OUTFIT = os.environ.get("OUTFIT", "tee")   # "tee": fitted running tee; "vest" (experimental)
SHORTS = os.environ.get("SHORTS", "1") == "1"
SHIRT = (0.03, 0.08, 0.2)
PANTS = (0.015, 0.015, 0.02)
SHOES = (0.75, 0.75, 0.78)
SHOE_UP = (0.9, 0.22, 0.04)
# x-ray shell: a crisp cyan rim (fresnel power) and an almost clear centre
XR_POW = float(os.environ.get("XR_POW", "2.6"))
XR_COL = (0.25, 0.65, 1.0, 1)   # orange knit upper


# ----------------------------------------------------------------------------- materials
def _nodes(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    return m, nt, out


def _bump(nt, bsdf, scale, strength, detail=6.0, kind="noise", wave_scale=None):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    if kind == "noise":
        tex = nt.nodes.new("ShaderNodeTexNoise"); tex.inputs["Scale"].default_value = scale
        tex.inputs["Detail"].default_value = detail
        nt.links.new(tc.outputs["Object"], tex.inputs["Vector"])
        src = tex.outputs["Fac"]
    else:
        tex = nt.nodes.new("ShaderNodeTexWave"); tex.inputs["Scale"].default_value = scale
        tex.inputs["Distortion"].default_value = 4.0; tex.inputs["Detail"].default_value = detail
        nt.links.new(tc.outputs["Object"], tex.inputs["Vector"])
        src = tex.outputs["Fac"]
    b = nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value = strength
    b.inputs["Distance"].default_value = 0.002
    nt.links.new(src, b.inputs["Height"]); nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])
    return src


def principled(name, color, rough=0.5, sss=0.0, bump=None, spec=0.5, metal=0.0):
    m, nt, out = _nodes(name)
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if "Specular IOR Level" in p.inputs:
        p.inputs["Specular IOR Level"].default_value = spec
    if sss:
        p.inputs["Subsurface Weight"].default_value = sss
        p.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
        p.inputs["Subsurface Scale"].default_value = 0.01
    if bump:
        _bump(nt, p, *bump)
    nt.links.new(p.outputs["BSDF"], out.inputs["Surface"])
    return m


def skin_material(name="skin"):
    """Skin with an X-ray control: the node group input 'xray' (0..1) fades the skin to a glassy
    blue shell so the glowing organs inside become visible."""
    m, nt, out = _nodes(name)
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = (0.6, 0.32, 0.2, 1)
    p.inputs["Roughness"].default_value = 0.48
    p.inputs["Subsurface Weight"].default_value = 0.25
    p.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
    p.inputs["Subsurface Scale"].default_value = 0.01
    if "Specular IOR Level" in p.inputs:
        p.inputs["Specular IOR Level"].default_value = 0.45
    _bump(nt, p, 900.0, 0.08, 2.0)
    # shirt fabric, blended in by the per-vertex 'cloth' attribute (smooth neckline / sleeve hems)
    ps = nt.nodes.new("ShaderNodeBsdfPrincipled")
    ps.inputs["Base Color"].default_value = (*SHIRT, 1); ps.inputs["Roughness"].default_value = 0.95
    _bump(nt, ps, 180.0, 0.25, 8.0)
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_name = "cloth"
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.42; mr.inputs["From Max"].default_value = 0.58
    nt.links.new(at.outputs["Fac"], mr.inputs["Value"])
    mixs = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mr.outputs["Result"], mixs.inputs["Fac"])
    nt.links.new(p.outputs["BSDF"], mixs.inputs[1]); nt.links.new(ps.outputs["BSDF"], mixs.inputs[2])
    # cheek blush / redness, driven by material value "flush"
    flush = nt.nodes.new("ShaderNodeValue"); flush.name = "flush"; flush.outputs[0].default_value = 0.0
    mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = "RGBA"
    mixc.inputs["A"].default_value = (0.6, 0.32, 0.2, 1); mixc.inputs["B"].default_value = (0.85, 0.22, 0.18, 1)
    nt.links.new(flush.outputs[0], mixc.inputs["Factor"]); nt.links.new(mixc.outputs["Result"], p.inputs["Base Color"])
    skin_png = os.path.join(DATA_OWN, "skin_diffuse.png")
    if os.path.exists(skin_png):   # photographic MakeHuman skin (CC0), blended to a medium tone
        tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(skin_png)
        hs = nt.nodes.new("ShaderNodeHueSaturation")
        hs.inputs["Saturation"].default_value = 0.78; hs.inputs["Value"].default_value = 0.92
        nt.links.new(tx.outputs["Color"], hs.inputs["Color"])
        a_col = next(i for i in mixc.inputs if i.name == "A" and i.type == "RGBA")
        nt.links.new(hs.outputs["Color"], a_col)
    # x-ray shell
    xr = nt.nodes.new("ShaderNodeValue"); xr.name = "xray"; xr.outputs[0].default_value = 0.0
    fres = nt.nodes.new("ShaderNodeLayerWeight"); fres.inputs["Blend"].default_value = 0.35
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = XR_COL
    ramp = nt.nodes.new("ShaderNodeMath"); ramp.operation = "POWER"; ramp.inputs[1].default_value = XR_POW
    nt.links.new(fres.outputs["Facing"], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], em.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(tr.outputs[0], add.inputs[0]); nt.links.new(em.outputs[0], add.inputs[1])
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(xr.outputs[0], mix.inputs["Fac"])
    nt.links.new(mixs.outputs[0], mix.inputs[1]); nt.links.new(add.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def xray_wrap(m):
    """Inserts an x-ray mix (value node 'xray') between the material's shader and its output."""
    nt = m.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    src = out.inputs["Surface"].links[0].from_socket
    xr = nt.nodes.new("ShaderNodeValue"); xr.name = "xray"; xr.outputs[0].default_value = 0.0
    fres = nt.nodes.new("ShaderNodeLayerWeight"); fres.inputs["Blend"].default_value = 0.35
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = XR_POW
    nt.links.new(fres.outputs["Facing"], pw.inputs[0])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = XR_COL
    nt.links.new(pw.outputs[0], em.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(tr.outputs[0], add.inputs[0]); nt.links.new(em.outputs[0], add.inputs[1])
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(xr.outputs[0], mix.inputs["Fac"])
    nt.links.new(src, mix.inputs[1]); nt.links.new(add.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def glow_material(name, color, strength=6.0, alpha=1.0, texture=None):
    """Hologram-style emissive material; node 'strength' (value) scales it, 'col' sets the colour.
    texture=("stripes", scale) adds muscle-fibre streaks, ("cells", scale) a mottled tissue look."""
    m, nt, out = _nodes(name)
    col = nt.nodes.new("ShaderNodeRGB"); col.name = "col"; col.outputs[0].default_value = (*color, 1)
    st = nt.nodes.new("ShaderNodeValue"); st.name = "strength"; st.outputs[0].default_value = strength
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
    ma = nt.nodes.new("ShaderNodeMath"); ma.operation = "MULTIPLY_ADD"
    ma.inputs[1].default_value = 1.2; ma.inputs[2].default_value = 0.35
    nt.links.new(lw.outputs["Facing"], ma.inputs[0])
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = "MULTIPLY"
    nt.links.new(ma.outputs[0], mu.inputs[0]); nt.links.new(st.outputs[0], mu.inputs[1])
    em = nt.nodes.new("ShaderNodeEmission")
    src = mu.outputs[0]
    if texture:
        kind, scale = texture
        tc = nt.nodes.new("ShaderNodeTexCoord")
        if kind == "stripes":
            tx = nt.nodes.new("ShaderNodeTexWave"); tx.wave_type = "BANDS"; tx.bands_direction = "X"
            tx.inputs["Scale"].default_value = scale; tx.inputs["Distortion"].default_value = 3.0
            tx.inputs["Detail"].default_value = 3.0
        else:
            tx = nt.nodes.new("ShaderNodeTexVoronoi"); tx.feature = "DISTANCE_TO_EDGE"
            tx.inputs["Scale"].default_value = scale
        nt.links.new(tc.outputs["Object"], tx.inputs["Vector"])
        fac = tx.outputs["Fac"] if kind == "stripes" else tx.outputs["Distance"]
        k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY_ADD"
        k.inputs[1].default_value = 0.6 if kind == "stripes" else 3.0; k.inputs[2].default_value = 0.55
        nt.links.new(fac, k.inputs[0])
        kc = nt.nodes.new("ShaderNodeMath"); kc.operation = "MINIMUM"; kc.inputs[1].default_value = 1.25
        nt.links.new(k.outputs[0], kc.inputs[0])
        m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = "MULTIPLY"
        nt.links.new(mu.outputs[0], m2.inputs[0]); nt.links.new(kc.outputs[0], m2.inputs[1])
        src = m2.outputs[0]
    nt.links.new(col.outputs[0], em.inputs["Color"]); nt.links.new(src, em.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader"); mix.name = "alpha"; mix.inputs["Fac"].default_value = alpha
    nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def eye_material(veins=False):
    m, nt, out = _nodes("eye_veins" if veins else "eye")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nrm = nt.nodes.new("ShaderNodeVectorMath"); nrm.operation = "NORMALIZE"
    nt.links.new(tc.outputs["Object"], nrm.inputs[0])
    dot = nt.nodes.new("ShaderNodeVectorMath"); dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = (0, -1, 0)
    nt.links.new(nrm.outputs[0], dot.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB"); cr = ramp.color_ramp
    cr.interpolation = "EASE"
    cr.elements[0].position = 0.80; cr.elements[0].color = (0.92, 0.9, 0.87, 1)
    e = cr.elements.new(0.83); e.color = (0.06, 0.12, 0.1, 1)
    e = cr.elements.new(0.86); e.color = (0.22, 0.32, 0.2, 1)
    e = cr.elements.new(0.94); e.color = (0.1, 0.14, 0.08, 1)
    cr.elements[-1].position = 0.955; cr.elements[-1].color = (0.01, 0.01, 0.01, 1)
    nt.links.new(dot.outputs["Value"], ramp.inputs["Fac"])
    p = nt.nodes.new("ShaderNodeBsdfPrincipled"); p.inputs["Roughness"].default_value = 0.08
    p.inputs["Coat Weight"].default_value = 1.0
    col = ramp.outputs["Color"]
    if veins:  # red vein network on the white of the eye
        vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.feature = "DISTANCE_TO_EDGE"
        vor.inputs["Scale"].default_value = 260.0
        nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
        vr = nt.nodes.new("ShaderNodeValToRGB"); vr.color_ramp.elements[0].position = 0.0
        vr.color_ramp.elements[0].color = (1, 1, 1, 1); vr.color_ramp.elements[1].position = 0.06
        vr.color_ramp.elements[1].color = (0, 0, 0, 1)
        nt.links.new(vor.outputs["Distance"], vr.inputs["Fac"])
        sclera = nt.nodes.new("ShaderNodeMath"); sclera.operation = "LESS_THAN"; sclera.inputs[1].default_value = 0.8
        nt.links.new(dot.outputs["Value"], sclera.inputs[0])
        amt = nt.nodes.new("ShaderNodeValue"); amt.name = "veins"; amt.outputs[0].default_value = 0.0
        f = nt.nodes.new("ShaderNodeMath"); f.operation = "MULTIPLY"
        nt.links.new(vr.outputs["Color"], f.inputs[0]); nt.links.new(sclera.outputs[0], f.inputs[1])
        f2 = nt.nodes.new("ShaderNodeMath"); f2.operation = "MULTIPLY"
        nt.links.new(f.outputs[0], f2.inputs[0]); nt.links.new(amt.outputs[0], f2.inputs[1])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs["B"].default_value = (0.75, 0.02, 0.02, 1)
        nt.links.new(f2.outputs[0], mx.inputs["Factor"]); nt.links.new(col, mx.inputs["A"])
        col = mx.outputs["Result"]
    nt.links.new(col, p.inputs["Base Color"])
    nt.links.new(p.outputs["BSDF"], out.inputs["Surface"])
    return m


# ----------------------------------------------------------------------------- set
def build_room():
    # wooden floor
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, J["ground"].z))
    floor = bpy.context.object; floor.name = "floor"
    m, nt, out = _nodes("wood")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled"); p.inputs["Roughness"].default_value = 0.35
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 6.0, 1.0)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    w = nt.nodes.new("ShaderNodeTexWave"); w.wave_type = "BANDS"; w.bands_direction = "Y"
    w.inputs["Scale"].default_value = 0.6; w.inputs["Distortion"].default_value = 9; w.inputs["Detail"].default_value = 4
    nt.links.new(mp.outputs[0], w.inputs["Vector"])
    plank = nt.nodes.new("ShaderNodeTexBrick"); plank.inputs["Scale"].default_value = 1.5
    plank.inputs["Brick Width"].default_value = 1.4; plank.inputs["Row Height"].default_value = 0.16
    plank.inputs["Mortar Size"].default_value = 0.004; plank.offset = 0.37
    plank.inputs["Color1"].default_value = (0.32, 0.17, 0.09, 1); plank.inputs["Color2"].default_value = (0.42, 0.24, 0.13, 1)
    plank.inputs["Mortar"].default_value = (0.08, 0.04, 0.02, 1)
    nt.links.new(tc.outputs["Object"], plank.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 0.35
    nt.links.new(plank.outputs["Color"], mx.inputs["A"]); nt.links.new(w.outputs["Color"], mx.inputs["B"])
    nt.links.new(mx.outputs["Result"], p.inputs["Base Color"])
    nt.links.new(p.outputs["BSDF"], out.inputs["Surface"])
    floor.data.materials.append(m)
    # light-blue panelled walls (back + left + right)
    wall = principled("wall", (0.12, 0.42, 0.75), rough=0.6)
    trim = principled("trim", (0.75, 0.88, 0.97), rough=0.5)
    g = J["ground"].z
    for name, loc, rot, size in [("wall_back", (0, 3.2, g + 2), (math.pi / 2, 0, 0), 9),
                                 ("wall_l", (-4.0, 0, g + 2), (math.pi / 2, 0, math.pi / 2), 9),
                                 ("wall_r", (4.0, 0, g + 2), (math.pi / 2, 0, math.pi / 2), 9),
                                 ("wall_f", (0, -6.0, g + 2), (math.pi / 2, 0, 0), 9)]:
        bpy.ops.mesh.primitive_plane_add(size=size, location=loc, rotation=rot)
        wobj = bpy.context.object; wobj.name = name; wobj.data.materials.append(wall)
    # vertical wall battens + a dado rail for depth cues
    for side in ("back", "l", "r"):
        for i in range(-8, 9):
            if side == "back":
                loc, dim = (i * 0.55, 3.17, g + 1.4), (0.05, 0.04, 2.8)
            else:
                xs = -3.97 if side == "l" else 3.97
                loc, dim = (xs, i * 0.55, g + 1.4), (0.04, 0.05, 2.8)
            bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
            b = bpy.context.object; b.scale = dim; b.data.materials.append(trim)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 3.14, g + 1.0) if side == "back" else
                                        ((-3.94 if side == "l" else 3.94), 0, g + 1.0))
        r = bpy.context.object
        r.scale = (9, 0.08, 0.08) if side == "back" else (0.08, 9, 0.08)
        r.data.materials.append(trim)
    # world: soft sky-blue fill
    w = bpy.data.worlds.new("w"); bpy.context.scene.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (0.45, 0.7, 0.95, 1)
    bg.inputs["Strength"].default_value = 0.35


def build_lights():
    def area(name, loc, energy, size, color=(1, 1, 1)):
        bpy.ops.object.light_add(type="AREA", location=loc)
        L = bpy.context.object; L.name = name; L.data.energy = energy; L.data.size = size
        L.data.color = color
        d = Vector((0, 0, 0.55)) - L.location
        L.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        return L
    area("key", (-1.6, -2.2, 1.6), 260, 1.6, (1.0, 0.95, 0.88))
    area("fill", (2.2, -1.8, 0.9), 70, 2.5, (0.8, 0.9, 1.0))
    area("rim", (1.2, 2.0, 1.8), 260, 1.0, (0.85, 0.93, 1.0))
    area("top", (0, 0, 2.6), 80, 3.0)


STADIUM = os.environ.get("STADIUM", "1") == "1"


def build_stands(g, seg_len=10.0, n_seg=14):
    """Covered grandstands on both sides of the track: concrete terraces, individual seats in a stadium
    colour scheme, aisles, a roof on slim columns. Built as 10 m segments that scroll and wrap."""
    import bmesh
    from mathutils import Matrix
    rng = np.random.default_rng(11)
    conc = principled("concrete", (0.48, 0.47, 0.45), rough=0.9, bump=(40.0, 0.15, 6.0))
    seat = _nodes("seats"); sm_, snt, sout = seat
    sb = snt.nodes.new("ShaderNodeBsdfPrincipled"); sb.inputs["Roughness"].default_value = 0.4
    at = snt.nodes.new("ShaderNodeAttribute"); at.attribute_name = "scol"; at.attribute_type = "GEOMETRY"
    snt.links.new(at.outputs["Color"], sb.inputs["Base Color"]); snt.links.new(sb.outputs[0], sout.inputs["Surface"])
    roof = principled("roof", (0.82, 0.83, 0.85), rough=0.5, metal=0.6)
    steel = principled("steel", (0.25, 0.26, 0.28), rough=0.4, metal=0.9)
    BLUE_, NAVY, WHITE, YEL = (0.02, 0.12, 0.45), (0.01, 0.04, 0.16), (0.75, 0.75, 0.75), (0.8, 0.55, 0.02)
    movers = []
    x0, tiers, run_, rise = 7.4, 16, 0.85, 0.42
    for sx in (1, -1):
        bm = bmesh.new(); cl = bm.loops.layers.color.new("scol")
        mats = []   # per-face material index
        def box(c, size, mi, col=None):
            r = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(c) @ Matrix.Diagonal((*size, 1)))
            fs = {f for v in r["verts"] for f in v.link_faces}
            for f in fs:
                f.material_index = mi
                if col:
                    for l in f.loops:
                        l[cl] = (*col, 1)
        # front wall + terraces
        box((sx * (x0 - 0.1), 0, g + 0.6), (0.2, seg_len, 1.2), 0)
        for i in range(tiers):
            xa = x0 + i * run_; z = g + 1.2 + i * rise
            box((sx * (xa + run_ / 2), 0, z - rise / 2), (run_, seg_len, rise), 0)
            for j in range(int(seg_len / 0.5)):
                y = -seg_len / 2 + 0.25 + j * 0.5
                if j in (0, 1):          # aisle stairs at the segment edge
                    continue
                u = (j + i * 0.5) / 20
                col = BLUE_ if (i // 4 + j // 6) % 3 else NAVY
                if 6 <= i <= 8 and 6 <= j <= 13:
                    col = WHITE if (i + j) % 2 else YEL     # a simple pattern block, as many stadiums have
                col = tuple(c * rng.uniform(0.85, 1.1) for c in col)
                xs = sx * (xa + 0.45)
                box((xs, y, z + 0.42), (0.42, 0.44, 0.06), 1, col)                       # seat pan
                box((sx * (xa + 0.68), y, z + 0.62), (0.05, 0.44, 0.38), 1, col)          # backrest
                box((xs, y, z + 0.2), (0.06, 0.06, 0.38), 3)                              # stem
        top = x0 + tiers * run_; ztop = g + 1.2 + tiers * rise
        box((sx * (top + 0.15), 0, (g + ztop + 3.2) / 2), (0.3, seg_len, ztop - g + 3.2), 0)   # back wall
        # roof: slanted canopy on two columns per segment
        rz0, rz1 = ztop + 3.4, ztop + 2.6
        verts = [bm.verts.new((sx * (top + 0.5), yy, rz0)) for yy in (-seg_len / 2, seg_len / 2)] + \
                [bm.verts.new((sx * (x0 - 1.5), yy, rz1)) for yy in (seg_len / 2, -seg_len / 2)]
        f = bm.faces.new(verts if sx > 0 else verts[::-1]); f.material_index = 2
        for yy in (-seg_len / 4, seg_len / 4):
            box((sx * (top - 0.4), yy, (g + rz0) / 2), (0.25, 0.25, rz0 - g), 3)
            box((sx * (top - 0.4 - (top - x0 + 1.1) / 2), yy, (rz0 + rz1) / 2 - 0.25), (top - x0 + 1.1, 0.12, 0.3), 3)
        me = bpy.data.meshes.new(f"stand{sx}"); bm.to_mesh(me); bm.free()
        for m in (conc, sm_, roof, steel):
            me.materials.append(m)
        for k in range(n_seg):
            o = bpy.data.objects.new(f"stand{sx}_{k}", me); bpy.context.collection.objects.link(o)
            y0 = -70 + seg_len / 2 + k * seg_len; o.location = (0, y0, 0); movers.append((o, y0))
    # an apron of grass/concrete between fence and stands
    return movers


def build_track(rng_seed=4):
    """Outdoor running track that scrolls under a runner who stays at the origin (running toward -Y).
    Returns dict(scroll=<value node>, movers=[(obj, y0)]): set scroll to the distance run (m) and wrap movers."""
    g = J["ground"].z
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, g))
    gr = bpy.context.object; gr.name = "ground"; gr.scale = (240, 400, 1)
    bpy.ops.object.transform_apply(scale=True)
    m, nt, out = _nodes("track")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled"); p.inputs["Roughness"].default_value = 0.85
    tc = nt.nodes.new("ShaderNodeTexCoord")
    scroll = nt.nodes.new("ShaderNodeValue"); scroll.name = "scroll"
    cmb = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(scroll.outputs[0], cmb.inputs["Y"])
    add = nt.nodes.new("ShaderNodeVectorMath"); add.operation = "ADD"
    nt.links.new(tc.outputs["Object"], add.inputs[0]); nt.links.new(cmb.outputs[0], add.inputs[1])
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(add.outputs[0], sep.inputs[0])

    def mth(op, a, b=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                nt.links.new(v, n.inputs[i])
        return n.outputs[0]
    x = sep.outputs["X"]
    # lane lines every 1.22 m (runner in the middle of a lane), track |x| < 4.3, grass outside
    lane = mth("LESS_THAN", mth("ABSOLUTE", mth("SUBTRACT", mth("FRACT", mth("DIVIDE", x, 1.22)), 0.5)), 0.022)
    on_track = mth("LESS_THAN", mth("ABSOLUTE", x), 4.3)
    grain = nt.nodes.new("ShaderNodeTexNoise"); grain.inputs["Scale"].default_value = 60; grain.inputs["Detail"].default_value = 8
    nt.links.new(add.outputs[0], grain.inputs["Vector"])
    rub = nt.nodes.new("ShaderNodeMix"); rub.data_type = "RGBA"
    rub.inputs["A"].default_value = (0.42, 0.09, 0.05, 1); rub.inputs["B"].default_value = (0.55, 0.14, 0.07, 1)
    nt.links.new(grain.outputs["Fac"], rub.inputs["Factor"])
    wl = nt.nodes.new("ShaderNodeMix"); wl.data_type = "RGBA"; wl.inputs["B"].default_value = (0.85, 0.85, 0.82, 1)
    nt.links.new(rub.outputs["Result"], wl.inputs["A"]); nt.links.new(lane, wl.inputs["Factor"])
    gn = nt.nodes.new("ShaderNodeTexNoise"); gn.inputs["Scale"].default_value = 3; gn.inputs["Detail"].default_value = 6
    nt.links.new(add.outputs[0], gn.inputs["Vector"])
    grass = nt.nodes.new("ShaderNodeMix"); grass.data_type = "RGBA"
    grass.inputs["A"].default_value = (0.05, 0.16, 0.03, 1); grass.inputs["B"].default_value = (0.12, 0.3, 0.05, 1)
    nt.links.new(gn.outputs["Fac"], grass.inputs["Factor"])
    fin = nt.nodes.new("ShaderNodeMix"); fin.data_type = "RGBA"
    nt.links.new(grass.outputs["Result"], fin.inputs["A"]); nt.links.new(wl.outputs["Result"], fin.inputs["B"])
    nt.links.new(on_track, fin.inputs["Factor"])
    nt.links.new(fin.outputs["Result"], p.inputs["Base Color"])
    _bump(nt, p, 140.0, 0.25, 4.0)
    nt.links.new(p.outputs["BSDF"], out.inputs["Surface"])
    gr.data.materials.append(m)
    # trees (trunk + two crowns) scattered beside the track, wrapped as the ground scrolls
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.18, radius2=0.12, depth=2.4,
                          matrix=__import__("mathutils").Matrix.Translation((0, 0, 1.2)))
    from mathutils import noise as _nz
    trng = np.random.default_rng(5)
    for k in range(16):
        r = trng.uniform(0.45, 0.95); c = Vector((trng.normal(0, 0.75), trng.normal(0, 0.75), 3.4 + trng.uniform(-0.7, 1.6)))
        res = bmesh.ops.create_icosphere(bm, subdivisions=3, radius=r, matrix=__import__("mathutils").Matrix.Translation(c))
        for v in res["verts"]:   # leafy clumps: two noise octaves push the surface in and out
            n = (v.co - c).normalized()
            v.co += n * (0.28 * _nz.noise(v.co * 2.0) + 0.12 * _nz.noise(v.co * 7.0 + Vector((3, 1, 2))))
    tm = bpy.data.meshes.new("tree"); bm.to_mesh(tm); bm.free()
    for poly in tm.polygons:
        poly.use_smooth = True
        poly.material_index = 0 if poly.center.z < 2.0 else 1
    tm.materials.append(principled("bark", (0.12, 0.07, 0.04), rough=0.9))
    leaves = principled("leaves", (0.05, 0.16, 0.03), rough=0.85, bump=(14.0, 1.0, 8.0), sss=0.2)
    lnt = leaves.node_tree; pb = next(n for n in lnt.nodes if n.type == "BSDF_PRINCIPLED")
    oi = lnt.nodes.new("ShaderNodeObjectInfo"); lm_ = lnt.nodes.new("ShaderNodeMix"); lm_.data_type = "RGBA"
    lm_.inputs[6].default_value = (0.035, 0.12, 0.025, 1); lm_.inputs[7].default_value = (0.1, 0.22, 0.04, 1)
    lnt.links.new(oi.outputs["Random"], lm_.inputs["Factor"]); lnt.links.new(lm_.outputs[2], pb.inputs["Base Color"])
    tm.materials.append(leaves)
    rng = np.random.default_rng(rng_seed); movers = []
    if STADIUM:
        movers += build_stands(g)
    for i in range(0 if STADIUM else 70):
        side = 1 if i % 2 else -1
        o = bpy.data.objects.new(f"tree{i}", tm); bpy.context.collection.objects.link(o)
        y0 = rng.uniform(-70, 70); s = rng.uniform(0.8, 1.4)
        o.location = (side * rng.uniform(7.5, 30), y0, g); o.scale = (s, s, s * rng.uniform(0.9, 1.3))
        o.rotation_euler = (0, 0, rng.uniform(0, 6.3))
        movers.append((o, y0))
    # fence (posts scroll, rails are uniform) and floodlight poles
    metal = principled("metal", (0.55, 0.57, 0.6), rough=0.35, metal=0.8)
    pm = bpy.data.meshes.new("post"); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=__import__("mathutils").Matrix.Diagonal((0.05, 0.05, 1.1, 1)) @ __import__("mathutils").Matrix.Translation((0, 0, 0.5)))
    bm.to_mesh(pm); bm.free(); pm.materials.append(metal)
    for sx in (1, -1):
        for i in range(56):
            o = bpy.data.objects.new(f"post{sx}_{i}", pm); bpy.context.collection.objects.link(o)
            y0 = -70 + i * 2.5; o.location = (sx * 5.6, y0, g); movers.append((o, y0))
        for z in (0.55, 1.05):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=400, location=(sx * 5.6, 0, g + z), rotation=(math.pi / 2, 0, 0))
            bpy.context.object.data.materials.append(metal)
    lm = bpy.data.meshes.new("pole"); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.12, radius2=0.07, depth=14,
                          matrix=__import__("mathutils").Matrix.Translation((0, 0, 7)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=__import__("mathutils").Matrix.Translation((0, 0, 14.2)) @ __import__("mathutils").Matrix.Diagonal((2.2, 0.4, 1.0, 1)))
    bm.to_mesh(lm); bm.free(); lm.materials.append(metal)
    for sx in (1, -1):
        for i in range(6):
            o = bpy.data.objects.new(f"pole{sx}_{i}", lm); bpy.context.collection.objects.link(o)
            y0 = -70 + i * 24 + (12 if sx > 0 else 0); o.location = (sx * 9.0, y0, g); movers.append((o, y0))
    # white kerb rails along both edges of the track
    rail = principled("rail", (0.9, 0.9, 0.9), rough=0.4)
    for sx in (1, -1):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(sx * 4.4, 0, g + 0.05))
        r = bpy.context.object; r.scale = (0.12, 400, 0.1); r.data.materials.append(rail)
    # sky
    w = bpy.data.worlds.new("sky"); bpy.context.scene.world = w; w.use_nodes = True
    wn = w.node_tree; bg = wn.nodes["Background"]
    sky = wn.nodes.new("ShaderNodeTexSky")
    print("SKY TYPES", [e.identifier for e in sky.bl_rna.properties["sky_type"].enum_items])
    for st_ in ("MULTIPLE_SCATTERING", "NISHITA", "HOSEK_WILKIE"):
        try:
            sky.sky_type = st_; break
        except TypeError:
            pass
    try:
        sky.sun_elevation = math.radians(28); sky.sun_rotation = math.radians(200); sky.altitude = 200
        sky.air_density = 1.2; sky.dust_density = 2.0
    except AttributeError:
        pass
    try:
        sky.sun_direction = Vector((0.4, -0.5, 0.75)).normalized()
        sky.turbidity = 2.5
    except AttributeError:
        pass
    hdr = os.path.join(DATA_OWN, "sky.hdr")
    if os.path.exists(hdr) and os.environ.get("HDRI", "1") == "1":
        env = wn.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(hdr)
        tc = wn.nodes.new("ShaderNodeTexCoord"); mp = wn.nodes.new("ShaderNodeMapping")
        mp.inputs["Rotation"].default_value = (0, 0, math.radians(float(os.environ.get("HDRI_ROT", "0"))))
        wn.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); wn.links.new(mp.outputs[0], env.inputs["Vector"])
        sky = env
    wn.links.new(sky.outputs["Color"], bg.inputs["Color"])
    if sky.type == "TEX_ENVIRONMENT":
        bg.inputs["Strength"].default_value = float(os.environ.get("SKY", "0.8"))
    else:
        bg.inputs["Strength"].default_value = float(os.environ.get("SKY", "0.06")) if sky.sky_type != "HOSEK_WILKIE" else 0.6
    if hasattr(sky, "sun_disc") and sky.type == "TEX_SKY":
        sky.sun_disc = False
    # sun + soft fill
    bpy.ops.object.light_add(type="SUN"); sun = bpy.context.object; sun.name = "sun"
    sun.data.energy = float(os.environ.get("SUN", "3.2")); sun.data.angle = math.radians(4); sun.data.color = (1.0, 0.95, 0.85)
    sun.rotation_euler = Vector((0.4, -0.5, 0.75)).to_track_quat("Z", "Y").to_euler()
    return dict(scroll=scroll, movers=movers, ground=gr)


# ----------------------------------------------------------------------------- character
def _seg_dist(P, a, b):
    ab = b - a; t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1), t


def make_hair(body, prefix):
    me = body.data
    e, m_, hd = J["l-eye"], J["mouth"], J["head"]
    keep = []
    for p in me.polygons:
        c = p.center
        if c.z < m_.z - 0.02 or p.material_index != 0:
            continue
        back = min(1.0, max(0.0, (c.y - (e.y + 0.035)) / 0.07))      # 0 at the face, 1 at the back
        zt = (e.z + 0.052) * (1 - back) + (m_.z - 0.005) * back
        if abs(c.x) > 0.06 and c.y < e.y + 0.11 and back < 0.9:      # keep clear of the ears
            zt = max(zt, e.z + 0.012)
        if c.z > zt:
            keep.append(p.index)
    import bmesh
    bm = bmesh.new(); bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    ks = set(keep)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in ks], context="FACES")
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True)
    for v in bm.verts:
        v.co += v.normal * 0.0025
    # rings away from the cap's edge -> soft hairline (cap fades out, strands thin out)
    ring = {v.index: (0 if v.is_boundary else 99) for v in bm.verts}
    bm.verts.ensure_lookup_table()
    for r in range(1, 6):
        for v in bm.verts:
            if ring[v.index] == 99 and any(ring[e.other_vert(v).index] == r - 1 for e in v.link_edges):
                ring[v.index] = r
    fade = [min(ring[i] / 5.0, 1.0) for i in range(len(bm.verts))]
    hm = bpy.data.meshes.new(prefix + "hair"); bm.to_mesh(hm); bm.free()
    at = hm.attributes.new("hfade", "FLOAT", "POINT"); at.data.foreach_set("value", fade)
    hair = bpy.data.objects.new(prefix + "hair", hm); bpy.context.collection.objects.link(hair)
    for p in hm.polygons:
        p.use_smooth = True
    cap = principled(prefix + "hairmat", (0.03, 0.017, 0.008), rough=0.9, bump=(220.0, 0.3, 10.0, "wave"), spec=0.1)
    nt = cap.node_tree; out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    src = out.inputs["Surface"].links[0].from_socket
    a = nt.nodes.new("ShaderNodeAttribute"); a.attribute_name = "hfade"
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(a.outputs["Fac"], mx.inputs["Fac"]); nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(src, mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs["Surface"])
    hm.materials.append(cap)
    # strands
    hb = bpy.data.materials.new(prefix + "strands"); hb.use_nodes = True
    nt = hb.node_tree; nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    h = nt.nodes.new("ShaderNodeBsdfHairPrincipled")
    h.parametrization = "MELANIN"
    h.inputs["Melanin"].default_value = 0.85; h.inputs["Melanin Redness"].default_value = 0.6
    h.inputs["Roughness"].default_value = 0.35; h.inputs["Random Roughness"].default_value = 0.3
    nt.links.new(h.outputs[0], o.inputs["Surface"])
    hm.materials.append(hb)
    vg = hair.vertex_groups.new(name="density")
    for i, f in enumerate(fade):
        vg.add([i], 0.25 + 0.75 * f, "REPLACE")
    ps = hair.modifiers.new("hair", "PARTICLE_SYSTEM").particle_system
    ps.vertex_group_density = "density"
    st = ps.settings
    st.type = "HAIR"; st.count = 3500; st.material = 2
    st.use_advanced_hair = True
    st.child_type = "INTERPOLATED"; st.rendered_child_count = 25; st.child_percent = 6
    st.clump_factor = 0.75; st.clump_shape = 0.3
    st.roughness_1 = 0.008; st.roughness_1_size = 0.05; st.roughness_2 = 0.006; st.roughness_endpoint = 0.004
    st.kink = "CURL"; st.kink_amplitude = 0.003; st.kink_frequency = 3.0
    st.root_radius = 1.0; st.tip_radius = 0.2; st.radius_scale = 0.0012
    st.child_length = 0.9; st.child_length_threshold = 0.3
    st.factor_random = 0.004  # random direction = tousled
    st.normal_factor = 0.007
    st.object_align_factor = (0, 0.016, 0.004)  # combed back
    return hair


def build_character(prefix=""):
    """Imports the base mesh and returns dict(body=..., rig=..., parts=...)."""
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=morphed_obj(), use_split_groups=True, global_scale=0.1)
    new = [o for o in bpy.data.objects if o not in before]
    bpy.ops.object.select_all(action="DESELECT")
    for o in new:
        o.select_set(True)
    bpy.context.view_layer.objects.active = new[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.select_all(action="DESELECT")
    keep = {"body", "helper-l-eye", "helper-r-eye", "helper-upper-teeth", "helper-lower-teeth",
            "helper-tongue"}
    objs = {}
    for o in new:
        base = o.name.split(".")[0]
        if base.startswith("joint-"):
            vs = [v.co.copy() for v in o.data.vertices]
            J[base[6:]] = sum(vs, Vector()) / len(vs)
            bpy.data.objects.remove(o)
        elif base in keep and base not in objs:
            objs[base] = o
        else:
            bpy.data.objects.remove(o)
    body = objs["body"]; body.name = prefix + "body"
    for o in objs.values():
        o.data.materials.clear()
        bpy.context.view_layer.objects.active = o; o.select_set(True)
        bpy.ops.object.shade_smooth(); o.select_set(False)

    # --- regions by nearest bone segment
    me = body.data
    P = np.array([(body.matrix_world @ p.center)[:] for p in me.polygons])
    segs = {
        "torso": (J["pelvis"], J["neck"]),
        "head": (J["neck"], J["head-2"]),
        "l_up": (J["l-shoulder"], J["l-elbow"]), "r_up": (J["r-shoulder"], J["r-elbow"]),
        "l_fa": (J["l-elbow"], J["l-hand"]), "r_fa": (J["r-elbow"], J["r-hand"]),
        "l_hand": (J["l-hand"], J["l-hand-3"]), "r_hand": (J["r-hand"], J["r-hand-3"]),
        "l_th": (J["l-upper-leg"], J["l-knee"]), "r_th": (J["r-upper-leg"], J["r-knee"]),
        "l_sh": (J["l-knee"], J["l-ankle"]), "r_sh": (J["r-knee"], J["r-ankle"]),
        "l_ft": (J["l-ankle"], J["l-foot-1"]), "r_ft": (J["r-ankle"], J["r-foot-1"]),
    }
    names = list(segs)
    D, T = [], {}
    for n in names:
        a, b = (np.array(v[:]) for v in segs[n])
        d, t = _seg_dist(P, a, b); D.append(d); T[n] = t
    D = np.array(D); near = np.array(names)[D.argmin(0)]
    z = P[:, 2]
    waist = J["pelvis"].z + 0.07
    neck_cut = J["neck"].z - 0.045
    mat = np.zeros(len(P), int)  # 0 skin (blends to shirt by the 'cloth' attribute), 1 shirt, 2 jeans, 3 shoes
    torso = near == "torso"
    # shirt coverage per VERTEX as a continuous value, so the neckline / sleeve hem is a smooth line
    VP = np.array([v.co[:] for v in me.vertices])
    Dv, Tv = [], {}
    for n in names:
        a_, b_ = (np.array(v[:]) for v in segs[n])
        d, t = _seg_dist(VP, a_, b_); Dv.append(d); Tv[n] = t
    nv = np.array(names)[np.array(Dv).argmin(0)]
    front = np.clip((J["neck"].y - VP[:, 1]) / 0.07, 0, 1)
    neckline = J["neck"].z - 0.035 - (0.06 if OUTFIT == "vest" else 0.03) * front
    cloth = np.zeros(len(VP))
    tor = np.isin(nv, ["torso", "head"])
    cloth[tor] = np.clip((neckline[tor] - VP[tor, 2]) / 0.006 + 0.5, 0, 1)
    for sname in ("l_up", "r_up"):
        k = nv == sname
        cloth[k] = 0.0 if OUTFIT == "vest" else np.clip((0.45 - Tv[sname][k]) / 0.03 + 0.5, 0, 1)
    if OUTFIT == "vest":   # armholes: bare shoulders outside the straps
        sx_ = abs(J["l-shoulder"].x) - 0.065          # strap outer edge
        arm = tor & (VP[:, 2] > J["l-shoulder"].z - 0.15)
        cloth[arm] = np.minimum(cloth[arm], np.clip((sx_ - np.abs(VP[arm, 0])) / 0.008 + 0.5, 0, 1))
    cloth[np.isin(nv, ["l_fa", "r_fa", "l_hand", "r_hand"])] = 0
    attr = me.attributes.new("cloth", "FLOAT", "POINT"); attr.data.foreach_set("value", cloth.tolist())
    for i, p in enumerate(me.polygons):
        c = cloth[list(p.vertices)]
        if near[i] in ("torso", "head", "l_up", "r_up") and c.min() > 0.999:
            mat[i] = 1
    mat[torso & (z <= waist)] = 2
    for s in ("l_th", "r_th", "l_sh", "r_sh"):
        if SHORTS:   # shorts: upper half of the thigh only
            if s.endswith("_th"):
                mat[(near == s) & (T[s] < 0.5)] = 2
        else:
            mat[near == s] = 2
    # straight hem: hip faces above the waistline belong to the shirt, torso faces below it to the trousers
    hip = np.isin(near, ["torso", "l_th", "r_th"])
    mat[hip & (z > waist)] = np.where(mat[hip & (z > waist)] == 2, 1, mat[hip & (z > waist)])
    for s in ("l_ft", "r_ft"):
        mat[near == s] = 3
    mat[(np.isin(near, ["l_sh", "r_sh"])) & (z < J["l-ankle"].z + 0.035)] = 3
    for m in (skin_material(prefix + "skin"),
              xray_wrap(principled(prefix + "shirt", SHIRT, rough=0.95, bump=(180.0, 0.25, 8.0))),
              xray_wrap(principled(prefix + "jeans", PANTS, rough=0.8, bump=(120.0, 0.2, 6.0))),
              xray_wrap(principled(prefix + "shoes", SHOES, rough=0.45))):
        me.materials.append(m)
    me.polygons.foreach_set("material_index", mat.tolist())
    # puff clothing slightly off the skin
    vmat = np.zeros(len(me.vertices), int)
    for p, mi in zip(me.polygons, mat):
        for vi in p.vertices:
            vmat[vi] = max(vmat[vi], mi)
    for i, (v, mi) in enumerate(zip(me.vertices, vmat)):
        if mi == 2:
            v.co += v.normal * 0.008
        elif mi == 3:
            v.co += v.normal * 0.014
        else:
            v.co += v.normal * 0.006 * cloth[i]

    # shoes: a smooth convex shell around each foot (trainer shape), white upper + dark sole
    SHOES_OBJ = []
    for side, sgn in (("l", 1 if J["l-ankle"].x > 0 else -1), ("r", -1 if J["l-ankle"].x > 0 else 1)):
        pts = [me.vertices[i].co.copy() for i, mi in enumerate(vmat) if mi == 3 and me.vertices[i].co.x * sgn > 0]
        if len(pts) < 10:
            continue
        cen = sum(pts, Vector()) / len(pts)
        bm = bmesh.new()
        for q in pts:
            bm.verts.new(cen + (q - cen) * Vector((1.08, 1.05, 1.1)))
        bmesh.ops.convex_hull(bm, input=bm.verts[:])
        zmin = min(v.co.z for v in bm.verts)
        for v in bm.verts:          # flat sole with a little toe spring at the very front
            if v.co.z < zmin + 0.012:
                v.co.z = zmin
        sm = bpy.data.meshes.new(f"shoe_{side}"); bm.to_mesh(sm); bm.free()
        so = bpy.data.objects.new(f"shoe_{side}", sm); bpy.context.collection.objects.link(so)
        for poly in sm.polygons:
            poly.use_smooth = True
        so.modifiers.new("sub", "SUBSURF").levels = 2
        sole_z = min(q.z for q in pts) + 0.016
        smat = _nodes(f"shoe_mat_{side}")
        m_, nt_, out_ = smat
        pb = nt_.nodes.new("ShaderNodeBsdfPrincipled"); pb.inputs["Roughness"].default_value = 0.5
        tc = nt_.nodes.new("ShaderNodeTexCoord"); sp = nt_.nodes.new("ShaderNodeSeparateXYZ")
        nt_.links.new(tc.outputs["Object"], sp.inputs[0])
        zb = zmin
        # bands from the ground up: dark rubber outsole, white foam midsole, coloured knit upper
        def band(z, ca, cb, fac_in=None):
            lt = nt_.nodes.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = z
            nt_.links.new(sp.outputs["Z"], lt.inputs[0])
            mx = nt_.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
            if isinstance(ca, tuple):
                mx.inputs[6].default_value = (*ca, 1)
            else:
                nt_.links.new(ca, mx.inputs[6])
            mx.inputs[7].default_value = (*cb, 1)
            nt_.links.new(lt.outputs[0], mx.inputs["Factor"])
            return mx.outputs[2], lt.outputs[0]
        knit = nt_.nodes.new("ShaderNodeTexWave"); knit.inputs["Scale"].default_value = 180
        knit.inputs["Distortion"].default_value = 2
        nt_.links.new(tc.outputs["Object"], knit.inputs["Vector"])
        kmx = nt_.nodes.new("ShaderNodeMix"); kmx.data_type = "RGBA"
        kmx.inputs[6].default_value = (*SHOE_UP, 1); kmx.inputs[7].default_value = tuple(c * 0.7 for c in SHOE_UP) + (1,)
        nt_.links.new(knit.outputs["Fac"], kmx.inputs["Factor"])
        c1, _ = band(zb + 0.034, kmx.outputs[2], (0.92, 0.92, 0.9))
        sole_z = zb + 0.009
        lt2 = nt_.nodes.new("ShaderNodeMath"); lt2.operation = "LESS_THAN"; lt2.inputs[1].default_value = sole_z
        nt_.links.new(sp.outputs["Z"], lt2.inputs[0])
        mx = nt_.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
        nt_.links.new(c1, mx.inputs[6]); mx.inputs[7].default_value = (0.03, 0.03, 0.035, 1)
        nt_.links.new(lt2.outputs[0], mx.inputs["Factor"]); nt_.links.new(mx.outputs[2], pb.inputs["Base Color"])
        nt_.links.new(pb.outputs["BSDF"], out_.inputs["Surface"])
        sm.materials.append(xray_wrap(m_))
        objs[f"shoe_{side}"] = so; SHOES_OBJ.append(so)
    # --- hair: a cap cut from the scalp + short Cycles hair strands
    hair = make_hair(body, prefix)
    # --- eyes, teeth, tongue
    eye_mat = eye_material(True)
    for side in ("l", "r"):
        e = objs[f"helper-{side}-eye"]; e.name = f"{prefix}{side}_eye"
        bpy.context.view_layer.objects.active = e; e.select_set(True)
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS"); e.select_set(False)
        e.data.materials.append(eye_mat)
        e.modifiers.new("sub", "SUBSURF").levels = 2
    teeth = principled(prefix + "teeth", (0.9, 0.87, 0.78), rough=0.25)
    for k in ("helper-upper-teeth", "helper-lower-teeth"):
        objs[k].data.materials.append(teeth); objs[k].modifiers.new("sub", "SUBSURF").levels = 1
    objs["helper-tongue"].data.materials.append(principled(prefix + "tongue", (0.7, 0.25, 0.25), rough=0.35, sss=0.3))

    # --- eyebrows: thin strips shrink-wrapped onto the brow ridge
    brow = principled(prefix + "brow", (0.05, 0.03, 0.015), rough=0.8, bump=(600.0, 1.0, 4.0))
    for s in (1, -1):
        e = J["l-eye"] if s == 1 else J["r-eye"]
        pts = []
        for i in range(9):
            u = i / 8
            x = e.x + s * (-0.017 + 0.042 * u)
            zc = e.z + 0.019 + 0.008 * math.sin(math.pi * (u * 0.85 + 0.1)) - 0.004 * u
            w = 0.0062 * (1 - 0.6 * u) + 0.0015
            pts.append((x, e.y - 0.03, zc + w / 2)); pts.append((x, e.y - 0.03, zc - w / 2))
        faces = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(8)]
        bm = bpy.data.meshes.new(prefix + "brow"); bm.from_pydata(pts, [], faces)
        bo = bpy.data.objects.new(prefix + f"brow{s}", bm); bpy.context.collection.objects.link(bo)
        bo.data.materials.append(brow)
        sw = bo.modifiers.new("sw", "SHRINKWRAP"); sw.target = body; sw.wrap_method = "PROJECT"
        sw.use_project_y = True; sw.use_negative_direction = True; sw.use_positive_direction = True
        sw.offset = 0.0015
        sol = bo.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.0012
        objs[f"brow{s}"] = bo

    # fabric drape: smooth away nipples / muscle detail under the tee and shorts
    vg = body.vertex_groups.new(name="fabric")
    for i, c in enumerate(cloth):
        w = max(float(c), 1.0 if vmat[i] == 2 else 0.0)
        if w > 0:
            vg.add([i], w, "REPLACE")
    sm = body.modifiers.new("drape", "SMOOTH"); sm.vertex_group = "fabric"
    sm.factor = 0.9; sm.iterations = int(os.environ.get("DRAPE", "12"))
    sub = body.modifiers.new("sub", "SUBSURF"); sub.levels = 1; sub.render_levels = 1
    objs["hair"] = hair

    # --- rig
    arm = bpy.data.armatures.new(prefix + "rig"); rig = bpy.data.objects.new(prefix + "rig", arm)
    bpy.context.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones

    def bone(name, h, t, parent=None, connect=False):
        b = eb.new(name); b.head = h; b.tail = t
        if parent: b.parent = eb[parent]; b.use_connect = connect
        return b
    sp = sorted([k for k in J if k.startswith("spine-")], key=lambda k: J[k].z)
    chain = ["pelvis"] + sp + ["neck", "head", "head-2"]
    chain = [c for c in chain if c in J]
    bone("root", J["pelvis"] + Vector((0, 0, -0.1)), J["pelvis"])
    prev = "root"
    for a, b in zip(chain[:-1], chain[1:]):
        bone(a, J[a], J[b], prev); prev = a
    headb = "head"
    bone("jaw", J["jaw"], J["mouth"], headb)
    for s in ("l", "r"):
        bone(f"{s}_clav", J[f"{s}-clavicle"], J[f"{s}-shoulder"], sp[-1])
        bone(f"{s}_up", J[f"{s}-shoulder"], J[f"{s}-elbow"], f"{s}_clav")
        bone(f"{s}_fa", J[f"{s}-elbow"], J[f"{s}-hand"], f"{s}_up", True)
        bone(f"{s}_hand", J[f"{s}-hand"], J[f"{s}-hand-3"], f"{s}_fa", True)
        bone(f"{s}_th", J[f"{s}-upper-leg"], J[f"{s}-knee"], "pelvis")
        bone(f"{s}_sh", J[f"{s}-knee"], J[f"{s}-ankle"], f"{s}_th", True)
        bone(f"{s}_ft", J[f"{s}-ankle"], J[f"{s}-foot-1"], f"{s}_sh", True)
    for b in eb:  # sensible rolls so local X bends elbows/knees
        b.roll = 0
    # finger bones (3 per finger), rolled so a rotation about local X curls the finger toward the palm
    for s in ("l", "r"):
        fj = lambda f, k: J[f"{s}-finger-{f}-{k}"]
        n = (fj(2, 1) - fj(5, 1)).cross(fj(3, 4) - fj(3, 1)).normalized()
        if s == "r":
            n = -n
        for f in range(1, 6):
            prev = f"{s}_hand"
            for k in range(1, 4):
                name = f"{s}_f{f}{k}"
                b = bone(name, fj(f, k), fj(f, k + 1), prev, k > 1)
                b.align_roll(n)
                prev = name
    bpy.ops.object.mode_set(mode="OBJECT")
    # skin the body
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True); rig.select_set(True); bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    # rigid parts follow bones
    for k, bn in (("helper-l-eye", "head"), ("helper-r-eye", "head"), ("helper-upper-teeth", "head"),
                  ("hair", "head"), ("helper-lower-teeth", "jaw"), ("helper-tongue", "jaw"),
                  ("brow1", "head"), ("brow-1", "head")) + tuple((k, k.replace("shoe_", "") + "_ft") for k in ("shoe_l", "shoe_r") if k in objs):
        o = objs[k]; mw = o.matrix_world.copy()
        o.parent = rig; o.parent_type = "BONE"; o.parent_bone = bn
        o.matrix_world = mw
    # IK handles for arms
    bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode="POSE")
    ik = {}
    for s in ("l", "r"):
        tgt = bpy.data.objects.new(f"{prefix}{s}_ik", None); bpy.context.collection.objects.link(tgt)
        tgt.location = J[f"{s}-hand"]; tgt.empty_display_size = 0.03
        pole = bpy.data.objects.new(f"{prefix}{s}_pole", None); bpy.context.collection.objects.link(pole)
        pole.location = J[f"{s}-elbow"] + Vector((0, 0.5, -0.1))
        c = rig.pose.bones[f"{s}_fa"].constraints.new("IK"); c.target = tgt; c.chain_count = 2
        c.pole_target = pole; c.pole_angle = math.radians(-90); c.influence = 0.0
        ik[s] = dict(target=tgt, pole=pole, con=c)
    bpy.ops.object.mode_set(mode="OBJECT")
    parts = dict(body=body, rig=rig, ik=ik, hair=hair, objs=objs)
    return parts
