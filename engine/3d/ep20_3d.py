"""20편 3D shots (Cycles, one process, persistent data). Writes PNG frames + points.json.
python3 ep20_3d.py OUTDIR [only_prefix]"""
import bpy, math, sys, os, json, time
from mathutils import Vector, Euler
from bpy_extras.object_utils import world_to_camera_view

OUT = sys.argv[1]; ONLY = sys.argv[2] if len(sys.argv) > 2 else ""
os.makedirs(OUT, exist_ok=True)
RW, RH, SAMPLES, FPS = 480, 490, 10, 12

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True; sc.cycles.max_bounces = 4; sc.cycles.use_adaptive_sampling = True
sc.render.use_persistent_data = True
sc.render.resolution_x, sc.render.resolution_y = RW, RH
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.03, 0.035, 0.05, 1)


def mat(name, base, metal=0.0, rough=0.5, emit=None, strength=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1); b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = strength
    return m


M = dict(
    steel=mat("steel", (0.62, 0.63, 0.66), 1.0, 0.32), floor=mat("floor", (0.14, 0.14, 0.15), 0, 0.55),
    mirror=mat("mirror", (0.95, 0.95, 0.95), 1.0, 0.01), light=mat("light", (1, 1, 1), emit=(1, .96, .9), strength=12),
    rail=mat("rail", (0.8, 0.8, 0.82), 1.0, 0.15), black=mat("black", (0.02, 0.02, 0.02), 0, 0.4),
    tire=mat("tire", (0.03, 0.03, 0.03), 0, 0.8), frame=mat("frame", (0.05, 0.25, 0.6), 0.6, 0.3),
    seat=mat("seat", (0.05, 0.05, 0.06), 0, 0.7), skin=mat("skin", (0.80, 0.58, 0.44), 0, 0.55),
    hair=mat("hair", (0.04, 0.03, 0.025), 0, 0.6), shirt=mat("shirt", (0.95, 0.55, 0.15), 0, 0.7),
    shirt2=mat("shirt2", (0.18, 0.55, 0.62), 0, 0.7), pants=mat("pants", (0.12, 0.14, 0.22), 0, 0.8),
    tile=mat("tile", (0.55, 0.5, 0.45), 0, 0.4), wallc=mat("wallc", (0.85, 0.83, 0.78), 0, 0.8),
    phone=mat("phone", (0.02, 0.02, 0.025), 0.3, 0.2), flash=mat("flash", (1, 1, 1), emit=(1, 1, 1), strength=0),
)


def box(name, loc, size, m, parent=None):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object; o.name = name; o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(m); o.parent = parent; return o


def cyl(a, b, r, m, parent=None, name="limb"):
    a, b = Vector(a), Vector(b); d = b - a
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, location=(a + b) / 2, vertices=20)
    o = bpy.context.object; o.name = name
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler(); o.data.materials.append(m); o.parent = parent
    bpy.ops.object.shade_smooth()
    for p in (a, b):   # rounded joints
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=p, segments=16, ring_count=8)
        s = bpy.context.object; s.data.materials.append(m); s.parent = parent; bpy.ops.object.shade_smooth()
    return o


def ball(p, r, m, parent=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=p, segments=24, ring_count=12)
    o = bpy.context.object; o.scale = scale; o.data.materials.append(m); o.parent = parent; bpy.ops.object.shade_smooth()
    return o


def empty(name):
    bpy.ops.object.empty_add(location=(0, 0, 0)); e = bpy.context.object; e.name = name; return e


# ---------------- elevator car: x width 1.1, y depth 1.35 (back wall/mirror at +y, door at y=0) ----------------
Wd, D, Ht = 1.1, 1.35, 2.3
box("floor", (0, D / 2, -0.01), (Wd, D, 0.02), M["floor"])
CEIL = [box("ceil", (0, D / 2, Ht + 0.01), (Wd, D, 0.02), M["steel"]),
        box("lightpanel", (0, D / 2, Ht - 0.005), (0.7, 0.9, 0.01), M["light"])]
box("left", (-Wd / 2 - 0.01, D / 2, Ht / 2), (0.02, D, Ht), M["steel"])
box("right", (Wd / 2 + 0.01, D / 2, Ht / 2), (0.02, D, Ht), M["steel"])
box("back", (0, D + 0.02, Ht / 2), (Wd, 0.02, Ht), M["steel"])
MIRROR = box("mirror", (0, D + 0.005, 0.6 + 0.75), (Wd - 0.12, 0.01, 1.5), M["mirror"])
for x in (-Wd / 2 + 0.03, Wd / 2 - 0.03):
    box("rail", (x, D / 2 + 0.1, 0.85), (0.03, D - 0.4, 0.03), M["rail"])
box("rail_b", (0, D - 0.03, 0.85), (Wd - 0.2, 0.03, 0.03), M["rail"])
box("panel", (Wd / 2 - 0.005, 0.25, 0.85), (0.01, 0.35, 0.18), M["black"])
DOORS = [box("doorL", (-0.275, -0.02, 1.05), (0.55, 0.03, 2.1), M["steel"]),
         box("doorR", (0.275, -0.02, 1.05), (0.55, 0.03, 2.1), M["steel"])]
box("lintel", (0, -0.02, 2.2), (Wd, 0.04, 0.2), M["steel"])
box("corridor_floor", (0, -1.5, -0.01), (3, 3, 0.02), M["tile"])
box("corridor_wall", (0, -3.0, 1.2), (3, 0.05, 2.4), M["wallc"])
bpy.ops.object.light_add(type="AREA", location=(0, -1.5, 2.3)); bpy.context.object.data.energy = 120
bpy.ops.object.light_add(type="SUN", location=(0, 0.7, 6)); SUN = bpy.context.object; SUN.data.energy = 0.0


def set_door(op):
    op = max(0.0, min(1.0, op))
    DOORS[0].location.x = -0.275 - 0.52 * op; DOORS[1].location.x = 0.275 + 0.52 * op


# ---------------- wheelchair + seated person (local: faces +y) ----------------
CH = empty("chair")
def wheel(x, y, r, w=0.03):
    bpy.ops.mesh.primitive_torus_add(location=(x, y, r), rotation=(0, math.pi / 2, 0), major_radius=r, minor_radius=w)
    o = bpy.context.object; o.data.materials.append(M["tire"]); o.parent = CH
    bpy.ops.mesh.primitive_torus_add(location=(x + (0.045 if x > 0 else -0.045), y, r), rotation=(0, math.pi / 2, 0), major_radius=r - 0.04, minor_radius=0.008)
    o = bpy.context.object; o.data.materials.append(M["rail"]); o.parent = CH
for s in (-1, 1):
    wheel(s * 0.31, -0.1, 0.3); wheel(s * 0.22, 0.32, 0.08, 0.02)
    box("tube", (s * 0.24, 0.1, 0.48), (0.025, 0.55, 0.025), M["frame"], CH)
    box("upright", (s * 0.24, -0.2, 0.75), (0.025, 0.025, 0.55), M["frame"], CH)
    box("arm", (s * 0.24, 0.0, 0.72), (0.04, 0.35, 0.025), M["frame"], CH)
    box("foot", (s * 0.1, 0.38, 0.12), (0.1, 0.12, 0.02), M["frame"], CH)
box("seat", (0, 0.05, 0.5), (0.45, 0.42, 0.04), M["seat"], CH)
box("backrest", (0, -0.2, 0.78), (0.45, 0.03, 0.42), M["seat"], CH)
# seated person
cyl((0, -0.11, 0.6), (0, -0.11, 1.0), 0.15, M["shirt2"], CH, "torso")
ball((0, -0.09, 1.2), 0.105, M["skin"], CH, (1, 1, 1.12))
ball((0, -0.11, 1.24), 0.108, M["hair"], CH, (1.02, 1.04, 0.9))
cyl((0, -0.11, 1.0), (0, -0.1, 1.09), 0.045, M["skin"], CH)
for s in (-1, 1):
    cyl((s * 0.09, -0.02, 0.58), (s * 0.1, 0.32, 0.58), 0.065, M["pants"], CH)
    cyl((s * 0.1, 0.33, 0.56), (s * 0.1, 0.36, 0.17), 0.055, M["pants"], CH)
    box("shoe", (s * 0.1, 0.4, 0.15), (0.09, 0.16, 0.06), M["black"], CH)
    cyl((s * 0.17, -0.1, 0.97), (s * 0.25, -0.02, 0.76), 0.045, M["shirt2"], CH)
    cyl((s * 0.25, -0.02, 0.76), (s * 0.33, 0.06, 0.62), 0.038, M["skin"], CH)

# ---------------- standing person with phone (local: faces +y) ----------------
ST = empty("stand")
for s in (-1, 1):
    cyl((s * 0.09, 0, 0.08), (s * 0.09, 0, 0.88), 0.07, M["pants"], ST)
    box("shoe", (s * 0.09, 0.04, 0.04), (0.1, 0.24, 0.08), M["black"], ST)
cyl((0, 0, 0.92), (0, 0, 1.38), 0.16, M["shirt"], ST, "torso")
cyl((0, 0, 1.4), (0, 0, 1.5), 0.045, M["skin"], ST)
ball((0, 0.01, 1.6), 0.105, M["skin"], ST, (1, 1, 1.12))
ball((0, -0.01, 1.64), 0.108, M["hair"], ST, (1.02, 1.04, 0.9))
cyl((-0.2, 0, 1.35), (-0.24, 0.02, 0.95), 0.045, M["shirt"], ST)          # left arm down
cyl((-0.24, 0.02, 0.95), (-0.25, 0.06, 0.72), 0.04, M["skin"], ST)
cyl((0.2, 0, 1.35), (0.27, 0.18, 1.2), 0.045, M["shirt"], ST)             # right arm up holding phone
cyl((0.27, 0.18, 1.2), (0.16, 0.3, 1.5), 0.04, M["skin"], ST)
PH = box("phone", (0.15, 0.33, 1.56), (0.075, 0.012, 0.15), M["phone"], ST)
FL = box("flashdot", (0.17, 0.34, 1.61), (0.015, 0.004, 0.015), M["flash"], ST)


def place(obj, x, y, yaw_deg=0.0, show=True):
    obj.location = (x, y, 0); obj.rotation_euler = (0, 0, math.radians(yaw_deg))
    for c in [obj] + list(obj.children_recursive):
        c.hide_render = not show


# ---------------- cameras ----------------
def camera(name, loc, target, lens=18, ortho=None):
    bpy.ops.object.camera_add(location=loc); c = bpy.context.object; c.name = name
    c.data.lens = lens
    if ortho:
        c.data.type = "ORTHO"; c.data.ortho_scale = ortho
    c.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return c

CAMS = dict(
    hook=camera("hook", (-0.38, 0.12, 1.62), (0.05, D, 1.25), 17),
    hero=camera("hero", (0.25, -0.35, 1.55), (-0.05, D, 1.0), 16),
    top=camera("top", (0, 0.55, 5.0), (0, 0.55, 0), ortho=2.05),
    pov=camera("pov", (0.0, 0.42, 1.2), (0.0, D, 1.15), 18),
    law=camera("law", (0.0, 0.05, 0.95), (0.0, D, 0.95), 15),
)
CAMS["top"].rotation_euler = (0, 0, 0)

FLASH_B = M["flash"].node_tree.nodes["Principled BSDF"]


def shot(name, cam, top=False, mirror=True, door=0.0, chair=None, stand=None, flash=0.0):
    if ONLY and not name.startswith(ONLY):
        return
    sc.camera = CAMS[cam]
    for o in CEIL:
        o.hide_render = top
    SUN.data.energy = 3.0 if top else 0.0
    MIRROR.hide_render = not mirror
    set_door(door)
    if chair: place(CH, *chair)
    else: place(CH, 0, 0, 0, False)
    if stand: place(ST, *stand)
    else: place(ST, 0, 0, 0, False)
    FLASH_B.inputs["Emission Strength"].default_value = flash
    sc.render.filepath = os.path.join(OUT, name + ".png")
    t0 = time.time(); bpy.ops.render.render(write_still=True)
    print("shot", name, round(time.time() - t0, 1), "s", flush=True)


def ease(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


# points for 2D overlays (law shot): floor and mirror-bottom on the back wall, in normalized camera coords
pts = {}
for nm, p in dict(floor=(0, D, 0.0), mirror_bottom=(0, D, 0.6), mirror_top=(0, D, 2.1)).items():
    v = world_to_camera_view(sc, CAMS["law"], Vector(p)); pts[nm] = (v.x, 1 - v.y)
json.dump(pts, open(os.path.join(OUT, "points.json"), "w"))

# ---- the shot list ----
shot("hook_a", "hook", door=0.0, stand=(0.12, 0.62, 0))
shot("hook_f", "hook", door=0.0, stand=(0.12, 0.62, 0), flash=400)
shot("hook_b", "hook", door=1.0, chair=(0.05, 0.62, 0))
shot("hero", "hero", door=1.0, chair=(0, 0.72, 0))
for i in range(48):                                    # can't turn: wobble, bumping
    t = i / FPS; yaw = 28 * math.sin(t * 2.6) * min(1, t / 0.6)
    shot(f"turn_{i:03d}", "top", top=True, door=1.0, chair=(0, 0.7, yaw))
for i in range(40):                                    # in forwards, out backwards
    t = i / FPS
    y = (-0.55 + 1.25 * ease(t / 1.4)) if t < 1.5 else (0.7 - 0.45 * ease((t - 1.6) / 1.6))
    shot(f"inout_{i:03d}", "top", top=True, door=1.0, chair=(0, y, 0))
shot("pov_blind", "pov", mirror=False, door=0.6)
for i in range(26):                                    # door opens behind, seen in the mirror
    shot(f"pov_{i:03d}", "pov", door=ease((i / FPS - 0.3) / 1.2))
shot("law", "law", door=0.0)
shot("tip", "hero", door=1.0, chair=(0.05, 0.75, 0), stand=(-0.42, 0.2, 140))
print("DONE")
