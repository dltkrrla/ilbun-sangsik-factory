"""25편 3D shots: why coins have reeded edges. python3 ep25_3d.py OUTDIR [only_prefix]
Real sizes (m): 500원 26.5mm/120 reeds, 100원 24mm/110, 50원 21.6mm/109, 10원 18mm plain (Bank of Korea)."""
import bpy, bmesh, math, sys, os, time, json, random
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

OUT = sys.argv[1]; ONLY = sys.argv[2] if len(sys.argv) > 2 else ""
os.makedirs(OUT, exist_ok=True)
RW, RH, SAMPLES = 640, 654, 28

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True; sc.cycles.max_bounces = 5; sc.cycles.use_adaptive_sampling = True
sc.render.use_persistent_data = True
sc.render.resolution_x, sc.render.resolution_y = RW, RH
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
BGN = world.node_tree.nodes["Background"]
BGN.inputs[0].default_value = (0.1, 0.12, 0.2, 1); BGN.inputs[1].default_value = 0.6
try:
    FONT = bpy.data.fonts.load("/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc")
except Exception:
    FONT = None


def mat(name, base, metal=0.0, rough=0.5, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1); b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*base, 1); b.inputs["Emission Strength"].default_value = emit
    return m


M = dict(
    wood=mat("wood", (0.07, 0.04, 0.022), 0, 0.62), nickel=mat("nickel", (0.78, 0.78, 0.76), 1, 0.3),
    gold=mat("gold", (1.0, 0.62, 0.18), 1, 0.24), copper=mat("copper", (0.85, 0.42, 0.25), 1, 0.3),
    steel=mat("steel", (0.25, 0.26, 0.28), 1, 0.42), handle=mat("handle", (0.3, 0.14, 0.05), 0, 0.5),
    apple=mat("apple", (0.72, 0.04, 0.035), 0, 0.22), stem=mat("stem", (0.18, 0.1, 0.04), 0, 0.7),
    leaf=mat("leaf", (0.1, 0.4, 0.08), 0, 0.45), soft=mat("soft", (1, 1, 1), 0, 1, 2.2),
    cut=mat("cut", (1.0, 0.78, 0.35), 1, 0.12),
)


def root(name, parent=None):
    e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e); e.parent = parent; return e


def vis(r, on):
    for o in [r] + list(r.children_recursive):
        o.hide_render = not on


def link(me, name, m, parent=None, smooth=False):
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.data.materials.append(m); o.parent = parent
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return o


def clipxy(x, y, cuts, R):
    """Pull a point radially inward onto any chord it sticks out of (cuts: (angle_deg, inset))."""
    for ang, inset in cuts:
        a = math.radians(ang); nx, ny = math.cos(a), math.sin(a); d = R - inset
        dot = x * nx + y * ny
        if dot > d:
            x, y = x * d / dot, y * d / dot
    return x, y


def body_mesh(R, t, n, depth, cuts=()):
    """Coin blank, axis z, centred. n reeds of given depth (0 = plain edge)."""
    bm = bmesh.new()
    ring = []
    if n and depth:
        for i in range(n):
            for j, (f, rr) in enumerate(((0.0, R), (0.5, R), (0.5, R - depth), (1.0, R - depth))):
                a = 2 * math.pi * (i + f * 0.999) / n
                ring.append((rr * math.cos(a), rr * math.sin(a)))
    else:
        ring = [(R * math.cos(2 * math.pi * i / 160), R * math.sin(2 * math.pi * i / 160)) for i in range(160)]
    ring = [clipxy(x, y, cuts, R) for x, y in ring]
    top = [bm.verts.new((x, y, t / 2)) for x, y in ring]; bot = [bm.verts.new((x, y, -t / 2)) for x, y in ring]
    bm.faces.new(top); bm.faces.new(list(reversed(bot)))
    k = len(ring)
    for i in range(k):
        bm.faces.new((top[i], bot[i], bot[(i + 1) % k], top[(i + 1) % k]))
    me = bpy.data.meshes.new("coin"); bm.to_mesh(me); bm.free(); return me


def ring_mesh(r0, r1, z0, z1, seg=128, cuts=(), R=1.0):
    bm = bmesh.new()
    def circ_(r, z):
        return [bm.verts.new((*clipxy(r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), cuts, R), z)) for i in range(seg)]
    a, b, c, d_ = circ_(r1, z0), circ_(r1, z1), circ_(r0, z1), circ_(r0, z0)
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((a[i], a[j], b[j], b[i])); bm.faces.new((b[i], b[j], c[j], c[i])); bm.faces.new((c[i], c[j], d_[j], d_[i]))
    me = bpy.data.meshes.new("ring"); bm.to_mesh(me); bm.free(); return me


def text(s, size, m, parent, z, flip=False, y=0.0):
    cu = bpy.data.curves.new("t", "FONT"); cu.body = s; cu.size = size; cu.extrude = 0.00012
    cu.align_x = "CENTER"; cu.align_y = "CENTER"
    if FONT:
        cu.font = FONT
    o = bpy.data.objects.new("t", cu); bpy.context.collection.objects.link(o); o.data.materials.append(m); o.parent = parent
    o.location = (0, y, z)
    bpy.context.view_layer.update()
    k = (size * 0.62 * len(s)) / max(o.dimensions.x, 1e-9)   # fit to target width
    cu.size *= k; cu.extrude = 0.00014
    if flip:
        o.rotation_euler = (0, math.pi, 0)
    return o


def dots(parent, r, n, z, m, rad):
    bm = bmesh.new()
    for i in range(n):
        a = 2 * math.pi * i / n
        bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=rad,
                                  matrix=__import__("mathutils").Matrix.Translation((r * math.cos(a), r * math.sin(a), z)))
    me = bpy.data.meshes.new("dots"); bm.to_mesh(me); bm.free()
    return link(me, "dots", m, parent, True)


def coin(parent, R, t, n, m, label, depth=None, cuts=(), style="won"):
    """Returns the root empty of one coin (axis z). cuts = list of (angle_deg, inset) chords clipped off."""
    g = root("coin", parent)
    depth = (R * 0.022 if depth is None else depth)
    b = link(body_mesh(R, t, n, depth, cuts), "body", m, g)
    rim_in = R * 0.88
    parts = [b]
    for s_ in (1, -1):
        r_ = link(ring_mesh(rim_in, R - depth * 1.3 - R * 0.01, s_ * t / 2 - 0.00002 * s_, s_ * (t / 2 + 0.00016), 256, cuts, R - R * 0.012), "rim", m, g, True); parts.append(r_)
    if style == "won":
        parts.append(text(label, R * 0.52, m, g, t / 2))
        parts.append(text(label, R * 0.52, m, g, -t / 2, flip=True))
        parts.append(dots(g, R * 0.8, 60, t / 2, m, R * 0.014)); parts.append(dots(g, R * 0.8, 60, -t / 2, m, R * 0.014))
    else:  # old gold coin: bead circle + star-ish shield, no real design copied
        for s_ in (1, -1):
            parts.append(dots(g, R * 0.78, 44, s_ * t / 2, m, R * 0.024))
            parts.append(link(ring_mesh(R * 0.3, R * 0.36, s_ * t / 2 - 0.00002 * s_, s_ * (t / 2 + 0.00014), 6), "hex", m, g))
            parts.append(link(ring_mesh(R * 0.52, R * 0.56, s_ * t / 2 - 0.00002 * s_, s_ * (t / 2 + 0.00012), 96), "ring2", m, g, True))
    return g


def stand(g, x, y, R, yaw=0.0, lean=0.0):
    """Stand a coin on its edge on the desk (z=0), face turned by yaw (deg) around vertical."""
    g.rotation_euler = (math.radians(90 + lean), 0, math.radians(yaw)); g.location = (x, y, R * math.cos(math.radians(lean)))


def lay(g, x, y, t, yaw=0.0):
    g.rotation_euler = (0, 0, math.radians(yaw)); g.location = (x, y, t / 2 + 0.00016)


def box(name, loc, size, m, bev=0.0, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m)
    if bev:
        b = o.modifiers.new("b", "BEVEL"); b.width = bev; b.segments = 4; bpy.ops.object.shade_smooth()
    o.parent = parent; return o


def flakes(parent, c, n, seed, spread=0.004):
    random.seed(seed); bm = bmesh.new()
    from mathutils import Matrix, Euler
    for i in range(n):
        r = spread * math.sqrt(random.random()); a = random.random() * 6.283
        h = max(0.0, (1 - r / spread)) * spread * 0.45 * random.random()
        mtx = Matrix.Translation((c[0] + r * math.cos(a), c[1] + r * math.sin(a), 0.0002 + h)) @ Euler((random.random() * 3, random.random() * 3, random.random() * 3)).to_matrix().to_4x4()
        bmesh.ops.create_cube(bm, size=0.00035 + random.random() * 0.0004, matrix=mtx @ Matrix.Diagonal((1, 0.5, 0.25, 1)))
    me = bpy.data.meshes.new("fl"); bm.to_mesh(me); bm.free()
    return link(me, "flakes", M["gold"], parent)


DESK = box("desk", (0, 0, -0.01), (1.2, 1.2, 0.02), M["wood"])
# softboxes for metal reflections
for loc, size in (((-0.18, -0.1, 0.22), 0.22), ((0.2, -0.16, 0.16), 0.14), ((0, 0.25, 0.2), 0.3)):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc); p = bpy.context.object; p.data.materials.append(M["soft"])
    p.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    p.visible_camera = False
bpy.ops.object.light_add(type="AREA", location=(-0.12, -0.16, 0.25)); L1 = bpy.context.object; L1.data.energy = 1.6; L1.data.size = 0.2
L1.rotation_euler = (Vector((0, 0, 0)) - L1.location).to_track_quat("-Z", "Y").to_euler()
bpy.ops.object.camera_add(); CAM = bpy.context.object; sc.camera = CAM
CAM.data.dof.use_dof = False; CAM.data.dof.aperture_fstop = 5.6


def aim(loc, target, lens=60, fstop=5.6):
    CAM.location = loc; CAM.data.lens = lens; CAM.data.clip_start = 0.002
    CAM.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    CAM.data.dof.focus_distance = (Vector(target) - Vector(loc)).length; CAM.data.dof.aperture_fstop = fstop


R5, R1, R05, R10, TH = 0.01325, 0.012, 0.0108, 0.009, 0.002
RG = 0.014
ROOTS = []
def scene(name):
    r = root(name); ROOTS.append(r); return r


# A: one 500 coin standing, spins (turntable)
A = scene("A"); A_COIN = coin(A, R5, TH, 120, M["nickel"], "500")
# B: three coins standing in a row
B = scene("B")
B5 = coin(B, R5, TH, 120, M["nickel"], "500"); stand(B5, -0.021, 0, R5, yaw=62)
B1 = coin(B, R1, TH * 0.9, 110, M["nickel"], "100"); stand(B1, 0.0, 0, R1, yaw=62)
B05 = coin(B, R05, TH * 0.75, 109, M["nickel"], "50"); stand(B05, 0.019, 0, R05, yaw=62)
# C: old gold coin, plain edge, clipped more and more (6 stages) + file + growing pile of gold dust
C = scene("C"); C_ST = []
CUTS = [(20, 0.0015), (95, 0.0016), (160, 0.0014), (230, 0.0016), (290, 0.0015)]
for k in range(6):
    g = root(f"C{k}", C)
    cg = coin(g, RG, 0.0019, 0, M["gold"], "", cuts=CUTS[:k], style="old"); lay(cg, -0.004, 0.002, 0.0019, yaw=15)
    if k:
        flakes(g, (0.018, -0.012, 0), 30 * k, k, 0.003 + 0.0008 * k)
    C_ST.append(g)
FILE = root("file", C)
box("blade", (0, 0, 0.0012), (0.05, 0.006, 0.0016), M["steel"], 0.0003, parent=FILE)
box("grip", (0.036, 0, 0.003), (0.024, 0.008, 0.006), M["handle"], 0.002, parent=FILE)
FILE.location = (0.012, 0.024, 0.0); FILE.rotation_euler = (0, 0, math.radians(-18))
# D: gold coin WITH reeds: intact / one chord clipped -> the smooth flat spot gives it away
D = scene("D")
D_A = coin(D, RG, 0.0019, 96, M["gold"], "", depth=RG * 0.035, style="old"); stand(D_A, 0, 0, RG, yaw=58)
D_B = coin(D, RG, 0.0019, 96, M["gold"], "", depth=RG * 0.035, cuts=[(160, 0.0016)], style="old"); stand(D_B, 0, 0, RG, yaw=58)
# E: Newton -> an apple next to a stack of silver reeded coins
E = scene("E")
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(-0.018, 0.01, 0.0285), segments=48, ring_count=24)
AP = bpy.context.object; AP.scale = (1, 1, 0.92); AP.data.materials.append(M["apple"]); bpy.ops.object.shade_smooth(); AP.parent = E
for v in AP.data.vertices:  # dimple top and bottom
    d = math.hypot(v.co.x, v.co.y) / 0.03
    v.co.z -= (0.007 * math.exp(-(d / 0.35) ** 2)) * (1 if v.co.z > 0 else -0.6)
bpy.ops.mesh.primitive_cylinder_add(radius=0.0011, depth=0.014, location=(-0.017, 0.01, 0.058), rotation=(0.25, 0.1, 0))
bpy.context.object.data.materials.append(M["stem"]); bpy.context.object.parent = E
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.01, location=(-0.008, 0.012, 0.06)); LF = bpy.context.object
LF.scale = (1, 0.45, 0.08); LF.rotation_euler = (0.2, -0.5, 0.3); LF.data.materials.append(M["leaf"]); bpy.ops.object.shade_smooth(); LF.parent = E
for i in range(6):
    cg = coin(E, R5, TH, 120, M["nickel"], "", style="old")
    cg.location = (0.03 + 0.0006 * math.sin(i * 2.1), -0.012 + 0.0007 * math.cos(i * 1.7), TH / 2 + 0.0002 + i * (TH + 0.00034)); cg.rotation_euler = (0, 0, i * 0.7)
E_ST = coin(E, R5, TH, 120, M["nickel"], "", style="old"); stand(E_ST, 0.052, -0.03, R5, yaw=40, lean=0)
# F: 10 won (plain copper) next to 500 (reeded)
F_ = scene("F")
F10 = coin(F_, R10, 0.0013, 0, M["copper"], "10"); stand(F10, -0.014, 0, R10, yaw=62)
F5 = coin(F_, R5, TH, 120, M["nickel"], "500"); stand(F5, 0.013, 0, R5, yaw=62)

PTS = {}
def shot(name, only, points=None, hide=(), show=()):
    if ONLY and not name.startswith(ONLY):
        return
    for r in ROOTS:
        vis(r, r is only)
    for o in hide:
        vis(o, False)
    for o in show:
        vis(o, True)
    bpy.context.view_layer.update()
    if points:
        PTS[name] = {k: (lambda v: (v.x, 1 - v.y))(world_to_camera_view(sc, CAM, Vector(p))) for k, p in points.items()}
    sc.render.filepath = os.path.join(OUT, name + ".png")
    t0 = time.time(); bpy.ops.render.render(write_still=True)
    print("shot", name, round(time.time() - t0, 1), "s", flush=True)


# A: spin, 20 frames = half turn (coin is symmetric front/back so it loops)
NSPIN = 20
for i in range(NSPIN):
    stand(A_COIN, 0, 0, R5, yaw=20 + 180 * i / NSPIN)
    aim((0.0, -0.062, 0.02), (0, 0, R5), 62, 8)
    shot(f"spin_{i:03d}", A, dict(c=(0, 0, R5), top=(0, 0, 2 * R5)))
# A2: macro on the edge
stand(A_COIN, 0, 0, R5, yaw=68)
aim((0.0, -0.07, 0.022), (-0.004, 0, R5 + 0.001), 105, 9); shot("edge", A, dict(c=(0, -0.001, R5)))
# B
aim((0.0, -0.125, 0.032), (0, 0, 0.012), 70, 9)
shot("three", B, dict(c500=(-0.021, 0, 2 * R5), c100=(0, 0, 2 * R1), c50=(0.019, 0, 2 * R05), b500=(-0.021, 0, 0), b100=(0, 0, 0), b50=(0.019, 0, 0)))
# C
aim((0.004, -0.058, 0.06), (0.004, 0.004, 0.0), 58, 8)
for k in range(6):
    FILE.location = (0.012 - 0.004 * (k % 2), 0.024, 0.0)
    shot(f"clip_{k:03d}", C, dict(coin=(-0.004, 0.002, 0.002), pile=(0.018, -0.012, 0.001)), hide=[g for j, g in enumerate(C_ST) if j != k])
# D
aim((0.0, -0.062, 0.022), (0, 0, RG), 62, 8)
a_ = math.radians(160)
flat = (RG * 0.84 * math.cos(a_) * math.cos(math.radians(58)), RG * 0.84 * math.cos(a_) * math.sin(math.radians(58)), RG + RG * 0.84 * math.sin(a_))
shot("reed_a", D, dict(c=(0, 0, RG)), hide=[D_B]); shot("reed_b", D, dict(c=(0, 0, RG), flat=flat), hide=[D_A])
# E
aim((0.012, -0.21, 0.075), (0.008, 0, 0.027), 62, 9); shot("newton", E, dict(apple=(-0.018, 0.01, 0.03), coins=(0.03, -0.012, 0.016)))
# F
aim((0.0, -0.085, 0.024), (0, 0, 0.011), 70, 9)
shot("ten", F_, dict(c10=(-0.014, 0, 2 * R10), c500=(0.013, 0, 2 * R5), b10=(-0.014, 0, 0), b500=(0.013, 0, 0)))
f = os.path.join(OUT, "points.json")
d = json.load(open(f)) if os.path.exists(f) else {}
d.update(PTS); json.dump(d, open(f, "w"))
print("DONE")
