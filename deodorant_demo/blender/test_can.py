"""Blender test: glossy aerosol can on a glowing display platform (reference-style diorama)."""
import bpy, math, sys, time

out = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "/tmp/can.png"
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

def mat(name, color, metal=0.0, rough=0.4, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m

def add(obj, m):
    obj.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return obj

# platform (like the reference's round dioramas) with glowing rim
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=2.2, depth=0.25, location=(0, 0, -0.125))
add(bpy.context.object, mat("plat", (0.12, 0.11, 0.10), rough=0.35))
bpy.ops.mesh.primitive_torus_add(major_radius=2.2, minor_radius=0.03, location=(0, 0, 0.0))
add(bpy.context.object, mat("rim", (1, 0.5, 0.15), emit=(1, 0.45, 0.1), strength=12))
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.26))
add(bpy.context.object, mat("floor", (0.02, 0.02, 0.025), rough=0.5))

# can body
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.42, depth=2.2, location=(0, 0, 1.1))
can = add(bpy.context.object, mat("paint", (0.05, 0.16, 0.6), metal=0.6, rough=0.22))
bev = can.modifiers.new("bev", "BEVEL"); bev.width = 0.06; bev.segments = 6
# shoulder dome + cap + nozzle
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=0.42, location=(0, 0, 2.2))
dome = add(bpy.context.object, mat("alu", (0.8, 0.8, 0.82), metal=1.0, rough=0.18))
dome.scale.z = 0.35
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.2, depth=0.25, location=(0, 0, 2.42))
add(bpy.context.object, mat("cap", (0.9, 0.9, 0.92), rough=0.3))
bpy.ops.mesh.primitive_cube_add(size=0.12, location=(0.16, 0, 2.5))
add(bpy.context.object, mat("noz", (0.1, 0.1, 0.1), rough=0.5))
# white label band
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.425, depth=0.7, location=(0, 0, 1.15))
add(bpy.context.object, mat("label", (0.92, 0.92, 0.9), rough=0.45))
# 3D text on the label
bpy.ops.object.text_add(location=(0, -0.44, 1.07), rotation=(math.radians(90), 0, 0))
t = bpy.context.object
t.data.body = "DEO"; t.data.align_x = "CENTER"; t.data.size = 0.32; t.data.extrude = 0.01
t.data.materials.append(mat("txt", (0.05, 0.16, 0.6), rough=0.3))

# spray mist: small emissive spheres
import random
r = random.Random(3)
mist = mat("mist", (0.8, 0.9, 1), emit=(0.7, 0.85, 1), strength=2.5)
for i in range(60):
    d = r.uniform(0.2, 2.2)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.02 + 0.03 * d,
        location=(0.25 + d, r.uniform(-0.2, 0.2) * d, 2.5 + r.uniform(-0.15, 0.25) * d))
    bpy.context.object.data.materials.append(mist)

# lights: key, rim, warm fill
def light(kind, loc, energy, color, size=2):
    bpy.ops.object.light_add(type=kind, location=loc)
    L = bpy.context.object
    L.data.energy = energy; L.data.color = color
    if kind == "AREA":
        L.data.size = size
    L.rotation_euler = (0, 0, 0)
    c = L.constraints.new("TRACK_TO"); c.target = can
    return L
light("AREA", (-3, -4, 5), 900, (1, 0.95, 0.9), 3)
light("AREA", (4, 3, 4), 700, (0.4, 0.6, 1.0), 2)
light("AREA", (3, -3, 0.8), 250, (1, 0.6, 0.3), 2)

# camera
bpy.ops.object.camera_add(location=(0, -7.2, 2.6))
cam = bpy.context.object
c = cam.constraints.new("TRACK_TO"); c.target = can
cam.data.lens = 45
sc.camera = cam

w = sc.world = bpy.data.worlds.new("w")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.008, 0.008, 0.012, 1)

sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = int(sys.argv[sys.argv.index("--") + 2]) if len(sys.argv) > sys.argv.index("--") + 2 else 32
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.filepath = out
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Punchy"
t0 = time.time()
bpy.ops.render.render(write_still=True)
print("RENDER_SECONDS", round(time.time() - t0, 1))
