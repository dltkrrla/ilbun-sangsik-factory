"""21편 3D shots: AI glasses & banned items on an exam desk (Cycles). python3 ep21_3d.py OUTDIR [only_prefix]"""
import bpy, math, sys, os, time
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

OUT = sys.argv[1]; ONLY = sys.argv[2] if len(sys.argv) > 2 else ""
os.makedirs(OUT, exist_ok=True)
RW, RH, SAMPLES, FPS = 480, 490, 12, 12

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True; sc.cycles.max_bounces = 4; sc.cycles.use_adaptive_sampling = True
sc.render.use_persistent_data = True
sc.render.resolution_x, sc.render.resolution_y = RW, RH
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.06, 0.08, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.25


def mat(name, base, metal=0.0, rough=0.5, emit=None, strength=0.0, trans=0.0, ior=1.45):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1); b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    b.inputs["Transmission Weight"].default_value = trans; b.inputs["IOR"].default_value = ior
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = strength
    return m


M = dict(
    wood=mat("wood", (0.3, 0.19, 0.1), 0, 0.4), paper=mat("paper", (0.93, 0.93, 0.9), 0, 0.8),
    ink=mat("ink", (0.25, 0.25, 0.3), 0, 0.8), frame=mat("frame", (0.015, 0.015, 0.018), 0, 0.25),
    lens=mat("lens", (0.95, 0.97, 1.0), 0, 0.02, trans=1.0, ior=1.5), camlens=mat("camlens", (0.02, 0.03, 0.06), 0.2, 0.05),
    led=mat("led", (0.2, 0.6, 1.0), emit=(0.2, 0.6, 1.0), strength=0.0), metal=mat("metal", (0.75, 0.75, 0.78), 1.0, 0.2),
    black=mat("black", (0.02, 0.02, 0.025), 0.2, 0.3), screen=mat("screen", (0.01, 0.01, 0.015), 0.0, 0.08),
    white=mat("white", (0.92, 0.92, 0.94), 0, 0.3), strap=mat("strap", (0.12, 0.12, 0.13), 0, 0.6),
    face=mat("face", (0.96, 0.95, 0.9), 0, 0.4), lcd=mat("lcd", (0.1, 0.9, 0.5), emit=(0.1, 0.9, 0.5), strength=3),
    pen=mat("pen", (0.05, 0.05, 0.05), 0, 0.4), ecig=mat("ecig", (0.35, 0.36, 0.42), 0.8, 0.3),
    phonebody=mat("phonebody", (0.55, 0.56, 0.6), 0.9, 0.25),
)


def bevel(o, w=0.003, seg=4):
    m = o.modifiers.new("b", "BEVEL"); m.width = w; m.segments = seg


def box(name, loc, size, m, bev=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    if bev: bevel(o, bev)
    return o


def cyl(name, loc, r, d, m, rot=(0, 0, 0), v=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=v)
    o = bpy.context.object; o.name = name; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o


GROUPS = {}
def group(name, objs):
    GROUPS[name] = objs


def show(names):
    for g, objs in GROUPS.items():
        for o in objs:
            o.hide_render = g not in names


# desk (units: meters; desk top at z=0)
box("desk", (0, 0, -0.02), (1.2, 0.8, 0.04), M["wood"], 0.004)
paper = [box("paper", (0.02, 0.0, 0.0006), (0.21, 0.297, 0.001), M["paper"], rot=(0, 0, math.radians(-6)))]
for i in range(9):
    paper.append(box("line", (0.02 - 0.01 * math.sin(math.radians(6)) * 0, 0.11 - i * 0.025, 0.0013), (0.16, 0.003, 0.0004), M["ink"], rot=(0, 0, math.radians(-6))))
pen = [cyl("pen", (0.17, -0.05, 0.006), 0.0055, 0.14, M["pen"], rot=(math.radians(90), 0, math.radians(20)))]
group("paper", paper + pen)

# --- AI glasses: wayfarer front built from 2D outlines (squircle, tapered, thick brow), slight wrap ---
import bmesh, json
acetate = bpy.data.materials.new("acetate"); acetate.use_nodes = True
_b = acetate.node_tree.nodes["Principled BSDF"]
_b.inputs["Base Color"].default_value = (0.006, 0.006, 0.007, 1); _b.inputs["Roughness"].default_value = 0.38
_b.inputs["Specular IOR Level"].default_value = 0.25
_b.inputs["Coat Weight"].default_value = 0.25; _b.inputs["Coat Roughness"].default_value = 0.12
tint = mat("tint", (0.35, 0.42, 0.5), 0, 0.03, trans=0.85, ior=1.55)
N = 96


def contour(cx, cz, a0, b0, taper, n=4.5, lift=0.0):
    pts = []
    for i in range(N):
        t = 2 * math.pi * i / N
        c, s_ = math.cos(t), math.sin(t)
        z = b0 * (abs(s_) ** (2 / n)) * (1 if s_ >= 0 else -1)
        a = a0 * (1 + taper * z / b0)
        x = a * (abs(c) ** (2 / n)) * (1 if c >= 0 else -1)
        if s_ > 0:
            z += lift * max(0, c * (1 if cx > 0 else -1))   # outer top corner raised (wayfarer)
        pts.append((cx + x, cz + z))
    return pts


def ring_mesh(name, outer, inner, depth, m):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    vo = [bm.verts.new((x, 0, z)) for x, z in outer]; vi = [bm.verts.new((x, 0, z)) for x, z in inner]
    for i in range(N):
        j = (i + 1) % N
        bm.faces.new((vo[i], vo[j], vi[j], vi[i]))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.data.materials.append(m)
    so = o.modifiers.new("s", "SOLIDIFY"); so.thickness = depth; so.offset = 0
    bv = o.modifiers.new("b", "BEVEL"); bv.width = 0.0016; bv.segments = 4; bv.limit_method = "ANGLE"
    for f in o.data.polygons: f.use_smooth = True
    return o


def disc_mesh(name, pts, depth, m):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    vs = [bm.verts.new((x, 0, z)) for x, z in pts]; bm.faces.new(vs); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.data.materials.append(m)
    so = o.modifiers.new("s", "SOLIDIFY"); so.thickness = depth; so.offset = 0
    return o


FZ = 0.034
G = []
EYE = {}
for s in (-1, 1):
    cx = s * 0.0345
    outer = contour(cx, FZ + 0.0015, 0.0335, 0.0245, 0.10, lift=0.004)
    inner = contour(cx, FZ - 0.0012, 0.0268, 0.0178, 0.12, lift=0.0015)
    rim = ring_mesh("rim", outer, inner, 0.0075, acetate)
    lens = disc_mesh("lens", inner, 0.0018, tint)
    piv = bpy.data.objects.new("eye", None); bpy.context.collection.objects.link(piv)
    piv.location = (s * 0.004, 0, 0)
    for o in (rim, lens):
        o.parent = piv; o.location.x -= s * 0.004
    extras = []
    if s < 0:
        extras += [cyl("cam", (-0.063, -0.0044, FZ + 0.016), 0.0028, 0.0014, M["camlens"], rot=(math.radians(90), 0, 0)),
                   cyl("camring", (-0.063, -0.0040, FZ + 0.016), 0.0039, 0.0009, M["metal"], rot=(math.radians(90), 0, 0)),
                   cyl("led2", (-0.0555, -0.0044, FZ + 0.018), 0.0009, 0.0012, M["led"], rot=(math.radians(90), 0, 0))]
    else:
        extras += [cyl("led", (0.063, -0.0044, FZ + 0.016), 0.0013, 0.0012, M["led"], rot=(math.radians(90), 0, 0))]
    for o in extras:
        o.parent = piv; o.location.x -= s * 0.004
    G += extras
    piv.rotation_euler = (0, 0, math.radians(-s * 7))       # wrap
    G += [rim, lens, piv]
    EYE[s] = (cx, FZ - 0.0012)
    # tapered temple: thick at the hinge (electronics), thinner at the tip, sloping to the desk
    me = bpy.data.meshes.new("temple"); bm = bmesh.new()
    L, h0, h1, w = 0.145, 0.016, 0.009, 0.0065
    vv = [bm.verts.new(p) for p in [(-w/2, 0, -h0/2), (w/2, 0, -h0/2), (w/2, 0, h0/2), (-w/2, 0, h0/2),
                                     (-w/2, L, -h1/2), (w/2, L, -h1/2), (w/2, L, h1/2), (-w/2, L, h1/2)]]
    for f in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]:
        bm.faces.new([vv[k] for k in f])
    bm.to_mesh(me); bm.free()
    t = bpy.data.objects.new("temple", me); bpy.context.collection.objects.link(t); t.data.materials.append(acetate)
    bv = t.modifiers.new("b", "BEVEL"); bv.width = 0.0025; bv.segments = 4
    for f in t.data.polygons: f.use_smooth = True
    t.location = (s * 0.0695, 0.006, FZ + 0.008); t.rotation_euler = (math.radians(-12), 0, math.radians(s * 4))
    G.append(t)
    G.append(box("hinge", (s * 0.0688, 0.0045, FZ + 0.008), (0.005, 0.006, 0.009), M["metal"], 0.0012))
G.append(box("bridge", (0, 0, FZ + 0.012), (0.012, 0.0075, 0.009), acetate, 0.002))
GL = bpy.data.objects.new("glasses_root", None); bpy.context.collection.objects.link(GL)
for o in G:
    if o.parent is None:
        o.parent = GL
GL.location = (0.0, -0.06, 0.0)
group("glasses", [o for o in G if o.type == "MESH"])


def save_points(name):
    """Image coords (u, v from top-left) of both lens centers for 2D HUD overlays."""
    bpy.context.view_layer.update()
    pts = {}
    for s_, key in ((-1, "lensL"), (1, "lensR")):
        cx, cz = EYE[s_]
        w = GL.matrix_world @ Vector((cx, -0.004, cz))
        v = world_to_camera_view(sc, CAM, w); pts[key] = (v.x, 1 - v.y)
    camo = [o for o in G if o.name.startswith("cam")][0]
    v = world_to_camera_view(sc, CAM, camo.matrix_world.translation); pts["cam"] = (v.x, 1 - v.y)
    f = os.path.join(OUT, "points.json")
    d = json.load(open(f)) if os.path.exists(f) else {}
    d[name] = pts; json.dump(d, open(f, "w"))

# --- banned items ---
phone = [box("phone", (-0.15, 0.06, 0.004), (0.072, 0.15, 0.008), M["phonebody"], 0.006),
         box("phscreen", (-0.15, 0.06, 0.0082), (0.066, 0.143, 0.0004), M["screen"], 0.004)]
watch = [cyl("swatch", (0.0, 0.08, 0.008), 0.02, 0.011, M["black"]), cyl("swscreen", (0.0, 0.08, 0.0137), 0.017, 0.0006, M["lcd"]),
         box("swstrap", (0.0, 0.08, 0.002), (0.022, 0.13, 0.003), M["strap"], 0.002)]
buds = [box("budcase", (0.14, 0.07, 0.012), (0.06, 0.045, 0.024), M["white"], 0.01),
        cyl("bud1", (0.115, -0.0, 0.006), 0.008, 0.012, M["white"]), cyl("bud2", (0.16, -0.0, 0.006), 0.008, 0.012, M["white"])]
ecig = [cyl("ecig", (-0.06, -0.08, 0.008), 0.008, 0.11, M["ecig"], rot=(math.radians(90), 0, math.radians(70)))]
group("banned", phone + watch + buds + ecig)

# --- watches: analog (allowed) vs digital (banned) ---
A = [cyl("aw_case", (-0.06, 0, 0.007), 0.021, 0.01, M["metal"]), cyl("aw_face", (-0.06, 0, 0.0122), 0.0185, 0.0005, M["face"]),
     box("aw_strap", (-0.06, 0, 0.002), (0.02, 0.14, 0.003), M["strap"], 0.002),
     box("aw_h", (-0.06 + 0.004, 0.003, 0.0128), (0.0016, 0.011, 0.0004), M["black"], rot=(0, 0, math.radians(-40))),
     box("aw_m", (-0.06 - 0.002, 0.007, 0.013), (0.0012, 0.016, 0.0004), M["black"], rot=(0, 0, math.radians(15)))]
for k in range(12):
    a = k * math.pi / 6
    A.append(box("tick", (-0.06 + 0.015 * math.sin(a), 0.015 * math.cos(a), 0.0127), (0.0012, 0.003, 0.0003), M["black"], rot=(0, 0, -a)))
D = [box("dw_case", (0.06, 0, 0.007), (0.036, 0.04, 0.012), M["black"], 0.004), box("dw_lcd", (0.06, 0, 0.0132), (0.028, 0.02, 0.0005), M["lcd"]),
     box("dw_strap", (0.06, 0, 0.002), (0.022, 0.14, 0.003), M["strap"], 0.002)]
group("watches", A + D)

# light
bpy.ops.object.light_add(type="AREA", location=(-0.4, -0.5, 0.9)); L = bpy.context.object; L.data.energy = 90; L.data.size = 0.8
L.rotation_euler = (Vector((0, 0, 0)) - L.location).to_track_quat("-Z", "Y").to_euler()
bpy.ops.object.light_add(type="AREA", location=(0.5, 0.3, 0.6)); L2 = bpy.context.object; L2.data.energy = 15; L2.data.size = 0.6
L2.rotation_euler = (Vector((0, 0, 0)) - L2.location).to_track_quat("-Z", "Y").to_euler()

for loc, e in (((0.35, 0.35, 0.25), 25), ((-0.35, 0.3, 0.2), 18)):
    bpy.ops.object.light_add(type="AREA", location=loc); R = bpy.context.object; R.data.energy = e; R.data.size = 0.25
    R.rotation_euler = (Vector((0, -0.05, 0.03)) - R.location).to_track_quat("-Z", "Y").to_euler()
bpy.ops.object.camera_add(); CAM = bpy.context.object; sc.camera = CAM
CAM.data.dof.use_dof = True; CAM.data.dof.aperture_fstop = 8.0


def aim(loc, target, lens=50, focus=None):
    CAM.location = loc; CAM.data.lens = lens
    CAM.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    CAM.data.dof.focus_distance = (Vector(target) - Vector(loc)).length if focus is None else focus


def shot(name):
    if ONLY and not name.startswith(ONLY):
        return
    if "glasses" in GROUPS and not GROUPS["glasses"][0].hide_render:
        save_points(name)
    sc.render.filepath = os.path.join(OUT, name + ".png")
    t0 = time.time(); bpy.ops.render.render(write_still=True)
    print("shot", name, round(time.time() - t0, 1), "s", flush=True)


def ease(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


# S1 glasses on the exam paper, slow orbit (looks normal)
show({"paper", "glasses"})
for i in range(30):
    a = math.radians(-40 + 32 * ease(i / 29))
    aim((0.27 * math.sin(a), -0.06 - 0.27 * math.cos(a), 0.09), (0.0, -0.035, 0.032), 58)
    shot(f"orbit_{i:03d}")
# S2 macro on the temple: the hidden camera (LED off -> on)
for i, on in enumerate([0, 0, 1, 1]):
    M["led"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 30.0 * on
    aim((-0.11, -0.2, 0.08), (-0.063, -0.065, 0.05), 90 + 15 * i)
    shot(f"macro_{i}")
M["led"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 30.0
# S3 glasses looking at the paper (POV-ish, the lens 'sees' the questions)
aim((0.03, -0.26, 0.045), (0.0, -0.06, 0.033), 55); shot("look")
# S4 banned items, top-down-ish
show({"banned"})
aim((0.0, -0.22, 0.42), (0.0, 0.01, 0.0), 40); shot("banned")
# S5 watches
show({"watches"})
aim((0.0, -0.16, 0.2), (0.0, 0.0, 0.0), 50); shot("watches")
# S6 end: clean desk with paper + pen + analog watch
show({"paper", "watches"})
for o in D: o.hide_render = True
aim((0.25, -0.35, 0.3), (0.0, 0.0, 0.0), 45); shot("end")
print("DONE")
