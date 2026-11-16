"""22편 3D shots: 수험표(admission ticket) = coupon; don't sell it. python3 ep22_3d.py OUTDIR [only_prefix]"""
import bpy, math, sys, os, time, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

OUT = sys.argv[1]; ONLY = sys.argv[2] if len(sys.argv) > 2 else ""
os.makedirs(OUT, exist_ok=True)
RW, RH, SAMPLES = 480, 490, 14

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True; sc.cycles.max_bounces = 4; sc.cycles.use_adaptive_sampling = True
sc.render.use_persistent_data = True
sc.render.resolution_x, sc.render.resolution_y = RW, RH
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.06, 0.09, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.4


def mat(name, base, metal=0.0, rough=0.5, emit=None, strength=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1); b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = strength
    return m


M = dict(
    wood=mat("wood", (0.16, 0.1, 0.055), 0, 0.45), paper=mat("paper", (0.95, 0.95, 0.92), 0, 0.75),
    ink=mat("ink", (0.3, 0.3, 0.35), 0, 0.8), blue=mat("blue", (0.05, 0.2, 0.6), 0, 0.6),
    photo=mat("photo", (0.6, 0.72, 0.85), 0, 0.5), photo2=mat("photo2", (0.9, 0.7, 0.55), 0, 0.5),
    person=mat("person", (0.12, 0.14, 0.22), 0, 0.6), person2=mat("person2", (0.35, 0.15, 0.1), 0, 0.6),
    yellow=mat("yellow", (0.95, 0.72, 0.1), 0, 0.5), teal=mat("teal", (0.1, 0.6, 0.6), 0, 0.5),
    pink=mat("pink", (0.9, 0.3, 0.45), 0, 0.5), white=mat("white", (0.92, 0.92, 0.94), 0, 0.35),
    phone=mat("phone", (0.03, 0.03, 0.035), 0.4, 0.25),
    screen=mat("screen", (0.9, 0.9, 0.95), emit=(0.95, 0.95, 1.0), strength=0.45),
    green=mat("green", (0.15, 0.5, 0.3), 0, 0.6), metal=mat("metal", (0.8, 0.8, 0.82), 1.0, 0.25),
    tape=mat("tape", (0.9, 0.85, 0.5), 0, 0.3),
)


def box(name, loc, size, m, bev=0.0, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    if bev:
        b = o.modifiers.new("b", "BEVEL"); b.width = bev; b.segments = 4
    o.parent = parent
    return o


def cyl(name, loc, r, d, m, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=32)
    o = bpy.context.object; o.name = name; o.data.materials.append(m); bpy.ops.object.shade_smooth(); o.parent = parent
    return o


def root(name):
    e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e); return e


def vis(r, on):
    for o in [r] + list(r.children_recursive):
        o.hide_render = not on


box("desk", (0, 0, -0.02), (1.4, 1.0, 0.04), M["wood"], 0.004)


def portrait(parent, x, y, z, bg, fg):
    box("ph", (x, y, z), (0.045, 0.058, 0.0006), bg, parent=parent)
    cyl("head", (x, y + 0.008, z + 0.0005), 0.0095, 0.0004, fg, parent=parent)
    box("body", (x, y - 0.018, z + 0.0005), (0.03, 0.02, 0.0004), fg, 0.004, parent=parent)


# --- 수험표 (admission ticket), local frame: lies flat, center at origin ---
CARD = root("card")
box("sheet", (0, 0, 0.0006), (0.2, 0.14, 0.0012), M["paper"], parent=CARD)
box("header", (0, 0.054, 0.0014), (0.19, 0.022, 0.0004), M["blue"], parent=CARD)
portrait(CARD, -0.066, -0.012, 0.0015, M["photo"], M["person"])
for i in range(4):
    box("line", (0.03, 0.022 - i * 0.017, 0.0014), (0.11 - (0.03 if i % 2 else 0), 0.004, 0.0003), M["ink"], parent=CARD)
box("stampbox", (0.07, -0.05, 0.0014), (0.03, 0.02, 0.0003), M["pink"], parent=CARD)

# --- tickets / coupons ---
TIX = root("tickets")
TPOS = [(-0.13, 0.13, 18, "yellow"), (0.0, 0.16, 0, "teal"), (0.13, 0.13, -18, "pink")]
for i, (x, y, a, c) in enumerate(TPOS):
    t = root(f"t{i}"); t.parent = TIX; t.location = (x, y, 0.001 + i * 0.0005); t.rotation_euler = (0, 0, math.radians(a))
    box("tk", (0, 0, 0), (0.12, 0.055, 0.001), M[c], parent=t)
    box("tk_w", (-0.035, 0, 0.0007), (0.035, 0.04, 0.0003), M["white"], parent=t)
    for k in range(2):
        box("tk_l", (0.02, 0.008 - k * 0.016, 0.0007), (0.055, 0.005, 0.0003), M["white"], parent=t)

# --- boarding pass + toy plane ---
FLY = root("fly")
box("bp", (0, 0.15, 0.001), (0.2, 0.075, 0.001), M["white"], parent=FLY)
box("bp_b", (0, 0.178, 0.0017), (0.2, 0.018, 0.0003), M["blue"], parent=FLY)
for k in range(3):
    box("bp_l", (-0.03, 0.155 - k * 0.014, 0.0017), (0.1, 0.004, 0.0003), M["ink"], parent=FLY)
PL = root("plane"); PL.parent = FLY; PL.location = (0.05, 0.16, 0.035); PL.rotation_euler = (0, math.radians(-8), math.radians(25))
f = cyl("fus", (0, 0, 0), 0.012, 0.11, M["white"], rot=(0, math.radians(90), 0), parent=PL)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.012, location=(0.055, 0, 0)); n = bpy.context.object; n.scale = (1.6, 1, 1); n.data.materials.append(M["white"]); n.parent = PL; bpy.ops.object.shade_smooth()
box("wing", (0, 0, -0.002), (0.03, 0.13, 0.003), M["white"], 0.001, parent=PL)
box("tailw", (-0.05, 0, 0.002), (0.016, 0.05, 0.002), M["white"], 0.0008, parent=PL)
box("fin", (-0.05, 0, 0.014), (0.02, 0.003, 0.026), M["blue"], 0.0008, parent=PL)

# --- phone (marketplace listing) ---
PH = root("phonegrp")
box("body", (0.17, 0.02, 0.004), (0.075, 0.155, 0.008), M["phone"], 0.006, parent=PH)
box("scr", (0.17, 0.02, 0.0083), (0.068, 0.146, 0.0004), M["screen"], 0.004, parent=PH)
box("thumb", (0.17, 0.055, 0.0087), (0.058, 0.045, 0.0003), M["paper"], parent=PH)
box("thumb_h", (0.17, 0.071, 0.0089), (0.054, 0.008, 0.0002), M["blue"], parent=PH)

# --- second photo (swap) ---
SW = root("swap")
portrait(SW, 0, 0, 0, M["photo2"], M["person2"])
box("tape", (0, 0.03, 0.0009), (0.03, 0.01, 0.0003), M["tape"], parent=SW)

# --- ID card ---
ID = root("idcard")
box("idb", (0.16, -0.02, 0.0008), (0.086, 0.054, 0.0016), M["white"], 0.003, parent=ID)
box("idh", (0.16, 0.0, 0.0018), (0.08, 0.008, 0.0003), M["green"], parent=ID)
box("idp", (0.135, -0.027, 0.0018), (0.022, 0.028, 0.0003), M["photo"], parent=ID)
for k in range(2):
    box("idl", (0.175, -0.02 - k * 0.011, 0.0018), (0.04, 0.004, 0.0003), M["ink"], parent=ID)

# lights
for loc, e, sz in (((-0.4, -0.5, 0.9), 14, 0.8), ((0.5, 0.3, 0.6), 4, 0.5), ((-0.3, 0.4, 0.3), 2.5, 0.3)):
    bpy.ops.object.light_add(type="AREA", location=loc); L = bpy.context.object; L.data.energy = e; L.data.size = sz
    L.rotation_euler = (Vector((0, 0, 0)) - L.location).to_track_quat("-Z", "Y").to_euler()
bpy.ops.object.camera_add(); CAM = bpy.context.object; sc.camera = CAM
CAM.data.dof.use_dof = True; CAM.data.dof.aperture_fstop = 8.0


def aim(loc, target, lens=45):
    CAM.location = loc; CAM.data.lens = lens
    CAM.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    CAM.data.dof.focus_distance = (Vector(target) - Vector(loc)).length


PTS = {}
def shot(name, points=None):
    if ONLY and not name.startswith(ONLY):
        return
    bpy.context.view_layer.update()
    if points:
        PTS[name] = {}
        for k, p in points.items():
            v = world_to_camera_view(sc, CAM, Vector(p)); PTS[name][k] = (v.x, 1 - v.y)
    sc.render.filepath = os.path.join(OUT, name + ".png")
    t0 = time.time(); bpy.ops.render.render(write_still=True)
    print("shot", name, round(time.time() - t0, 1), "s", flush=True)


def scene(card=True, tix=False, fly=False, phone=False, swap=False, idc=False):
    vis(CARD, card); vis(TIX, tix); vis(FLY, fly); vis(PH, phone); vis(SW, swap); vis(ID, idc)


def ease(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


CARD.location = (0, 0, 0); CARD.rotation_euler = (0, 0, math.radians(-5))
# 1 hero card
scene(); aim((0.05, -0.3, 0.26), (0, 0.0, 0), 50); shot("card", dict(card=(0, 0, 0), photo=(-0.066, -0.012, 0)))
# 2 card + coupons
scene(tix=True); CARD.location = (0, -0.03, 0)
aim((0.0, -0.33, 0.42), (0, 0.06, 0), 42)
shot("benefit", dict(t0=(TPOS[0][0], TPOS[0][1], 0), t1=(TPOS[1][0], TPOS[1][1], 0), t2=(TPOS[2][0], TPOS[2][1], 0), card=(0, -0.03, 0)))
# 3 boarding pass + plane
scene(fly=True)
aim((-0.05, -0.33, 0.36), (0.0, 0.07, 0.01), 42); shot("fly", dict(bp=(-0.02, 0.15, 0), plane=(0.05, 0.16, 0.035), card=(0, -0.03, 0)))
# 4 selling on a phone
scene(phone=True); CARD.location = (-0.06, 0, 0)
aim((0.02, -0.4, 0.42), (0.02, 0.01, 0), 40); shot("sell", dict(phone=(0.17, 0.0, 0.008), card=(-0.06, 0, 0)))
# 5 photo swap (sequence): a different photo slides onto the card
scene(swap=True); CARD.location = (0, 0, 0); CARD.rotation_euler = (0, 0, 0)
aim((-0.02, -0.2, 0.2), (-0.03, 0.0, 0), 55)
for i in range(16):
    k = ease(i / 12)
    SW.location = (-0.066 + 0.09 * (1 - k), -0.012 + 0.04 * (1 - k), 0.0022 + 0.02 * (1 - k))
    SW.rotation_euler = (0, 0, math.radians(25 * (1 - k) + 4))
    shot(f"swap_{i:03d}", dict(photo=(-0.066, -0.012, 0), card=(0.03, 0, 0)))
# 6 card + ID
scene(idc=True); CARD.location = (-0.06, 0, 0); CARD.rotation_euler = (0, 0, math.radians(-5))
aim((0.05, -0.42, 0.42), (0.05, -0.005, 0), 40); shot("ids", dict(card=(-0.06, 0, 0), id=(0.16, -0.02, 0)))
# 7 end: card + coupons, wider
scene(tix=True); CARD.location = (0, -0.03, 0)
aim((0.18, -0.36, 0.3), (0, 0.05, 0), 42); shot("end", dict(card=(0, -0.03, 0)))
f = os.path.join(OUT, "points.json")
d = json.load(open(f)) if os.path.exists(f) else {}
d.update(PTS); json.dump(d, open(f, "w"))
print("DONE")
