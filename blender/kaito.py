"""Cel-shaded Kaito Kid (fan art), head to mid-thigh, holding his calling card between two fingers.

Run from the repo root (the card and face textures come from vector sources first):
    node scripts/textures.mjs
    blender -b --factory-startup -P blender/kaito.py

Outputs public/models/kaito.glb (nodes "Kaito" and "Card"; animate the card) and public/renders/kaito.webp.
Faces -Y, z up. Built in working units, then normalised to 1.0 tall with the origin at the centre of
the thigh cut. The right arm and glove are skinned to an armature and posed through its bones; the
pose is baked into the mesh before export. Hair is clamped inside a 1.12x head ellipsoid.
"""
import math
import os
import sys

sys.path.append(os.path.dirname(__file__))
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from toon import (CACHE, ball, cur, decal, export_and_render, join, keep, limb, loft, mat, parts, poly,  # noqa: E402
                  strand)

SUIT = mat("Suit", "#f4f2ec", rough=0.5)
SUIT_SHADE = mat("SuitSeam", "#dcdad3")
LINING = mat("Lining", "#e3e7f0")
SHIRT = mat("Shirt", "#2f56a8")
TIE = mat("Tie", "#c8323a")
BAND = mat("HatBand", "#2f56a8")
SKIN = mat("Skin", "#f6dcc6")
HAIR = mat("Hair", "#3a2c26")
GLOVE = mat("Glove", "#fbfbf8", rough=0.6)
SILVER = mat("Silver", "#cfd4dc", rough=0.25, metal=1.0)
CLOVER = mat("Clover", "#2f8a57")

FRONT_Y = -0.118  # jacket front surface at chest height
Z_CUT = 0.71  # mid-thigh: 45% of the way from hip (0.9) to knee (0.48)
HEAD_C = Vector((0.0, -0.012, 1.66))  # head ellipsoid before the anime scale-up
HEAD_R = Vector((0.105, 0.1, 0.125))
HAIR_BOUND = 1.12


def thick(obj, t):
    """Give a flat panel real thickness (applied at join)."""
    obj.modifiers.new("Thickness", "SOLIDIFY").thickness = t
    return obj


def n(v):
    return Vector(v).normalized()


# =================================================================== body (static)
# ---- trousers and hips, cut flat at mid-thigh
loft("Hips", [((0, 0.012, 0.84), 0.15, 0.1), ((0, 0.012, 0.92), 0.158, 0.106)], SUIT, n=32)
for sx in (-1, 1):
    loft("Thigh", [((0.078 * sx, 0.012, Z_CUT), 0.074, 0.074), ((0.078 * sx, 0.012, 0.79), 0.08, 0.08),
                   ((0.074 * sx, 0.012, 0.87), 0.084, 0.084)], SUIT, n=28, caps=(True, True), sub=1)

# ---- jacket: chest, waist and a hem that covers the hips
loft("Jacket", [
    ((0, 0.014, 0.82), 0.168, 0.114),
    ((0, 0.012, 0.9), 0.162, 0.11),
    ((0, 0.01, 1.02), 0.152, 0.104),
    ((0, 0.004, 1.14), 0.165, 0.11),
    ((0, 0.0, 1.26), 0.188, 0.118),
    ((0, 0.0, 1.35), 0.2, 0.118),
    ((0, 0.004, 1.41), 0.186, 0.104),
    ((0, 0.01, 1.45), 0.11, 0.075),
], SUIT, n=32, caps=(True, True))
for sx in (-1, 1):  # rounded shoulder caps
    ball((0.178 * sx, 0.004, 1.395), 0.066, SUIT, scale=(1.08, 0.95, 0.62))

poly("ShirtV", [(-0.07, FRONT_Y - 0.002, 1.44), (0.07, FRONT_Y - 0.002, 1.44), (0.0, FRONT_Y - 0.008, 1.16)],
     [(2, 1, 0)], SHIRT, smooth=False)
for sx in (-1, 1):
    thick(poly("ShirtCollar", [(0.008 * sx, FRONT_Y - 0.012, 1.428), (0.058 * sx, FRONT_Y + 0.004, 1.468),
                               (0.066 * sx, FRONT_Y - 0.004, 1.43), (0.03 * sx, FRONT_Y - 0.012, 1.398)],
               [(0, 1, 2, 3) if sx > 0 else (3, 2, 1, 0)], SHIRT, smooth=False), 0.004)
loft("TieKnot", [((0, FRONT_Y - 0.014, 1.398), 0.014, 0.009), ((0, FRONT_Y - 0.016, 1.415), 0.021, 0.012),
                 ((0, FRONT_Y - 0.014, 1.432), 0.017, 0.01)], TIE, n=16, sub=1)
thick(poly("Tie", [(-0.016, FRONT_Y - 0.013, 1.4), (0.016, FRONT_Y - 0.013, 1.4), (0.034, FRONT_Y - 0.016, 1.21),
                   (0.0, FRONT_Y - 0.018, 1.165), (-0.034, FRONT_Y - 0.016, 1.21)], [(4, 3, 2, 1, 0)], TIE,
           smooth=False), 0.004)
ball((0.0, FRONT_Y - 0.02, 1.3), 0.006, SILVER, segs=12)  # tie pin
for sx in (-1, 1):  # notched lapels with thickness
    pts = [(0.074 * sx, FRONT_Y + 0.002, 1.448), (0.122 * sx, FRONT_Y + 0.006, 1.392),
           (0.104 * sx, FRONT_Y - 0.004, 1.372), (0.112 * sx, FRONT_Y - 0.002, 1.35),
           (0.07 * sx, FRONT_Y - 0.01, 1.27), (0.006 * sx, FRONT_Y - 0.012, 1.16),
           (0.054 * sx, FRONT_Y - 0.004, 1.43)]
    thick(poly("Lapel", pts, [tuple(range(7)) if sx > 0 else tuple(reversed(range(7)))], SUIT, smooth=False), 0.006)
for z in (1.12, 1.05):  # jacket buttons
    ball((0.0, FRONT_Y + 0.004, z), 0.011, SUIT_SHADE, scale=(1, 0.5, 1), segs=16)
thick(poly("Pocket", [(0.07, FRONT_Y + 0.004, 1.29), (0.14, FRONT_Y + 0.012, 1.292), (0.14, FRONT_Y + 0.012, 1.28),
                      (0.07, FRONT_Y + 0.004, 1.278)], [(0, 1, 2, 3)], SUIT_SHADE, smooth=False), 0.003)
# hip pocket flap on his left, where that hand rests
thick(poly("HipPocket", [(0.07, -0.116, 0.97), (0.16, -0.088, 0.975), (0.162, -0.088, 0.945), (0.07, -0.117, 0.94)],
           [(0, 1, 2, 3)], SUIT, smooth=False), 0.006)

# ---- cape: on the shoulders, falling past the thigh cut and cut flat with it;
#      his right side is swept back so the card arm reads clearly
nu, nv = 24, 18
cv = []
for j in range(nv + 1):
    v = j / nv
    for i in range(nu + 1):
        u = i / nu
        theta = math.radians(-70 + 152 * u)  # starts further back on his right (swept back)
        r = 0.2 + 0.24 * v + (0.12 * v * v if u > 0.5 else 0.02 * v)
        flutter = 0.03 * math.sin(u * 11 + v * 4) * v
        z = 1.445 - 0.86 * v + 0.1 * v * v * u
        cv.append((math.sin(theta) * r + 0.1 * v * v * (u - 0.3), math.cos(theta) * r * 0.75 + 0.03 + flutter,
                   max(z, Z_CUT)))
cf = [(j * (nu + 1) + i, j * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i)
      for j in range(nv) for i in range(nu)]
cape = poly("Cape", cv, cf, SUIT)
cape.data.materials.append(LINING)
sol = cape.modifiers.new("Thickness", "SOLIDIFY")
sol.thickness, sol.material_offset = 0.01, 1
cape.modifiers.new("Smooth", "SUBSURF").levels = 1

# ---- neck and an anime head with a painted face
loft("Neck", [((0, 0.0, 1.43), 0.044, 0.044), ((0, -0.006, 1.545), 0.04, 0.04)], SKIN, n=20)
head_start = len(parts)  # everything from here to the monocle is the head group
head = loft("Head", [
    ((0, -0.072, 1.532), 0.012, 0.01),
    ((0, -0.06, 1.55), 0.046, 0.042),
    ((0, -0.042, 1.578), 0.076, 0.07),
    ((0, -0.022, 1.615), 0.097, 0.09),
    ((0, -0.012, 1.655), 0.105, 0.099),
    ((0, -0.008, 1.7), 0.104, 0.1),
    ((0, -0.005, 1.74), 0.09, 0.088),
    ((0, -0.004, 1.77), 0.058, 0.058),
    ((0, -0.004, 1.783), 0.018, 0.018),
], SKIN, n=32, caps=(True, True), sub=2)
decal(head, os.path.join(CACHE, "kaito-face.png"), x_range=(-0.11, 0.11), z_range=(1.52, 1.76))
for sx in (-1, 1):
    ball((0.103 * sx, -0.004, 1.632), 0.021, SKIN, scale=(0.45, 1.0, 1.35))  # ears


# ---- hair: clumps that follow the skull, clamped inside the 1.12x head ellipsoid
def on_head(phi, theta, k):
    """Point on the head ellipsoid scaled by k. phi: 0 = front (-Y), +90 = his left; theta from the crown."""
    p, t = math.radians(phi), math.radians(theta)
    return (HEAD_C.x + HEAD_R.x * k * math.sin(t) * math.sin(p),
            HEAD_C.y - HEAD_R.y * k * math.sin(t) * math.cos(p),
            HEAD_C.z + HEAD_R.z * k * math.cos(t))


hair_start = len(parts)
ball((0.0, 0.006, 1.712), 0.104, HAIR, scale=(1.04, 1.07, 0.66), segs=32)  # mass under the hat
for i, phi in enumerate(range(48, 316, 22)):  # sides and back: flowing down, tips flicking only slightly
    tip_theta = 106 + 20 * (1 - abs(math.cos(math.radians(phi))))
    drift = (6, -5, 4, -6, 5)[i % 5]
    pts = [on_head(phi, 54, 1.02), on_head(phi + drift * 0.4, 75, 1.07), on_head(phi + drift * 0.8, 96, 1.085),
           on_head(phi + drift, tip_theta, 1.06)]
    strand(pts, 0.026, HAIR, taper=(1.0, 0.0))
for phi, tip in ((-40, 80), (-26, 83), (-12, 79), (2, 82.5), (16, 79.5), (30, 82), (42, 80)):  # fringe to the brow
    strand([on_head(phi * 0.6, 40, 1.03), on_head(phi * 0.85, 62, 1.065), on_head(phi, tip, 1.05)], 0.022, HAIR,
           taper=(1.0, 0.0))
for sx in (-1, 1):  # sideburns in front of the ears
    strand([on_head(78 * sx, 62, 1.04), on_head(80 * sx, 88, 1.06), on_head(78 * sx, 110, 1.04)], 0.014, HAIR,
           taper=(1.0, 0.0))

# validation: clamp every hair vertex radially onto the 1.12x ellipsoid if it pokes out
bound = Vector((HEAD_R.x * HAIR_BOUND, HEAD_R.y * HAIR_BOUND, HEAD_R.z * HAIR_BOUND))
hair_clamped = hair_total = 0
bpy.context.view_layer.update()
for o in parts[hair_start:]:
    mw, mwi = o.matrix_world.copy(), o.matrix_world.inverted()
    for v in o.data.vertices:
        d = (mw @ v.co) - HEAD_C
        q = math.sqrt((d.x / bound.x) ** 2 + (d.y / bound.y) ** 2 + (d.z / bound.z) ** 2)
        hair_total += 1
        if q > 1.0:
            v.co = mwi @ (HEAD_C + d / q)
            hair_clamped += 1

# ---- top hat (white, blue band), tilted
hat = []
loft("Crown", [((0, 0, 0.0), 0.11, 0.102), ((0, 0, 0.11), 0.104, 0.097), ((0, 0, 0.205), 0.11, 0.103),
               ((0, 0, 0.214), 0.1, 0.094)], SUIT, n=40, sub=1)
hat.append(cur())
loft("Band", [((0, 0, 0.004), 0.1135, 0.1055), ((0, 0, 0.048), 0.1095, 0.1015)], BAND, n=40, sub=1)
hat.append(cur())
loft("Brim", [((0, 0, -0.009), 0.196, 0.183), ((0.0, 0, 0.0), 0.204, 0.19), ((0, 0, 0.004), 0.198, 0.185),
              ((0, 0, -0.002), 0.112, 0.104)], SUIT, n=56, caps=(True, False), sub=1)
hat.append(cur())
pivot = bpy.data.objects.new("HatPivot", None)
bpy.context.collection.objects.link(pivot)
pivot.location = (0.012, 0.004, 1.74)
pivot.rotation_euler = (math.radians(-8), math.radians(9), math.radians(4))
for h in hat:
    h.parent = pivot

# ---- monocle over his right eye, cord to the lapel
bpy.ops.mesh.primitive_torus_add(major_radius=0.031, minor_radius=0.004, major_segments=40, minor_segments=10,
                                 location=(-0.042, -0.118, 1.645), rotation=(math.radians(90), 0, 0))
keep(cur(), SILVER)
strand([(-0.068, -0.12, 1.625), (-0.098, -0.132, 1.55), (-0.094, -0.136, 1.46), (-0.08, -0.13, 1.395)], 0.0018,
       SILVER, taper=(1, 1))
for ox, oz in ((0, 0.012), (-0.011, 0.0), (0.011, 0.0)):  # clover charm
    ball((-0.08 + ox, -0.134, 1.375 + oz), 0.0075, CLOVER, segs=14)
strand([(-0.08, -0.134, 1.375), (-0.084, -0.136, 1.356)], 0.0018, CLOVER, taper=(1, 1))

# anime proportions and a 10 degree turn toward the card: scale and rotate the head group about the neck top
bpy.context.view_layer.update()
grow = (Matrix.Translation((0.0, -0.01, 1.508)) @ Matrix.Rotation(math.radians(-10), 4, "Z")
        @ Matrix.Scale(1.12, 4) @ Matrix.Translation((0.0, 0.01, -1.53)))
for o in [o for o in parts[head_start:] if o.parent is None] + [pivot]:
    o.matrix_world = grow @ o.matrix_world

# ---- his left arm: relaxed, hand slipped into the hip pocket
sL, eL, wL = (0.195, 0.0, 1.38), (0.272, 0.04, 1.16), (0.13, -0.09, 0.97)
limb(sL, eL, 0.062, SUIT, r2=0.055, verts=24)
ball(eL, 0.055, SUIT, segs=24)
limb(eL, wL, 0.054, SUIT, r2=0.047, verts=24)
limb(Vector(wL) + (Vector(eL) - Vector(wL)).normalized() * 0.03, wL, 0.049, SHIRT, verts=20)  # shirt cuff

body = join("KaitoBody", smooth_angle=None)
bpy.data.objects.remove(pivot)

# =================================================================== right arm and glove (rigged)
# Rest pose: arm straight out along -X, palm down. Hand-local axes at rest:
#   along (bone Y) = -X world, spread (bone X, index side +) = -Y world, palm normal (bone Z) = -Z world.
S = Vector((-0.195, 0.0, 1.385))
UPPER, FORE, PALM = 0.17, 0.16, 0.055
HS = 1.2  # anime gloves read a size larger than life
E0 = S + Vector((-UPPER, 0, 0))
W0 = E0 + Vector((-FORE, 0, 0))
ALONG, SPREAD, PALMN = Vector((-1, 0, 0)), Vector((0, -1, 0)), Vector((0, 0, -1))


def hp(a, b, c):
    """Hand-local rest coordinates (spread, palm-normal, along) -> world."""
    return W0 + (SPREAD * a + PALMN * b + ALONG * c) * HS


# name: (spread, base along, segment lengths, radius)
FINGERS = {
    "index": (0.0205, 0.053, (0.03, 0.021, 0.018), 0.0085),
    "middle": (0.0005, 0.055, (0.032, 0.023, 0.019), 0.0085),
    "ring": (-0.0165, 0.053, (0.03, 0.021, 0.017), 0.008),
    "pinky": (-0.031, 0.049, (0.024, 0.017, 0.015), 0.007),
}
THUMB_BASE, THUMB_LEN, THUMB_R = (0.022, 0.006, 0.012), (0.024, 0.02, 0.017), 0.009
THUMB_REST = n((0.6, 0.3, 0.75))
tdir = SPREAD * THUMB_REST.x + PALMN * THUMB_REST.y + ALONG * THUMB_REST.z

limb(S, E0, 0.062, SUIT, r2=0.055, verts=24)
ball(E0, 0.055, SUIT, segs=24)
limb(E0, W0, 0.054, SUIT, r2=0.047, verts=24)
limb(hp(0, 0, -0.045), hp(0, 0, -0.024), 0.05, SHIRT, verts=24)  # shirt cuff
limb(hp(0, 0, -0.026), hp(0, 0, 0.012), 0.056, GLOVE, r2=0.04, verts=24)  # flared glove cuff over it
ball(hp(0.0, 0.0, 0.03), HS, GLOVE, scale=(0.033, 0.035, 0.0155), segs=28)  # palm, a rounded slab
limb(hp(-0.03, -0.004, 0.05), hp(0.028, -0.004, 0.05), 0.0105 * HS, GLOVE, verts=16)  # knuckle ridge
for k in range(3):  # stitching on the back of the glove
    strand([hp(-0.012 + k * 0.012, -0.0152, 0.008), hp(-0.012 + k * 0.012, -0.0158, 0.038)], 0.0013, SUIT_SHADE,
           taper=(1, 1))
for name, (s, base, lens, r) in FINGERS.items():  # three phalanges, rounded joints, a fingertip
    p = hp(s, 0, base)
    ball(p, r * HS * 1.05, GLOVE, segs=16)
    for i, length in enumerate(lens):
        q = p + ALONG * length * HS
        rr = r * HS * (1 - 0.06 * (i + 1))
        limb(p, q, r * HS * (1 - 0.06 * i), GLOVE, r2=rr, verts=16)
        ball(q, rr, GLOVE, segs=16)
        p = q
p = hp(*THUMB_BASE)
ball(p, THUMB_R * HS * 1.1, GLOVE, segs=16)
for i, length in enumerate(THUMB_LEN):
    q = p + tdir * length * HS
    limb(p, q, THUMB_R * HS * (1 - 0.07 * i), GLOVE, r2=THUMB_R * HS * (1 - 0.07 * (i + 1)), verts=16)
    ball(q, THUMB_R * HS * (1 - 0.07 * (i + 1)), GLOVE, segs=16)
    p = q
arm = join("ArmR", smooth_angle=None)

# ---- armature: spine, neck, head, clavicles, arms, hand and three bones per finger
arm_data = bpy.data.armatures.new("Rig")
rig = bpy.data.objects.new("Rig", arm_data)
bpy.context.collection.objects.link(rig)
bpy.ops.object.select_all(action="DESELECT")
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
eb = arm_data.edit_bones


def bone(name, head_pt, tail_pt, parent=None, roll_to=None, connect=False):
    b = eb.new(name)
    b.head, b.tail = Vector(head_pt), Vector(tail_pt)
    if roll_to is not None:
        b.align_roll(Vector(roll_to))
    if parent:
        b.parent = eb[parent]
        b.use_connect = connect
    return b


bone("spine", (0, 0, Z_CUT), (0, 0, 1.3))
bone("neck", (0, 0, 1.43), (0, 0, 1.53), "spine")
bone("head", (0, 0, 1.53), (0, 0, 1.78), "neck", connect=True)
for side, sx in (("R", -1), ("L", 1)):
    bone(f"clavicle_{side}", (0.02 * sx, 0, 1.4), (0.195 * sx, 0, 1.385), "spine")
bone("upper_arm_R", S, E0, "clavicle_R", roll_to=PALMN, connect=True)
bone("forearm_R", E0, W0, "upper_arm_R", roll_to=PALMN, connect=True)
bone("hand_R", W0, hp(0, 0, PALM), "forearm_R", roll_to=PALMN, connect=True)
for name, (s, base, lens, r) in FINGERS.items():
    p, parent = hp(s, 0, base), "hand_R"
    for i, length in enumerate(lens):
        q = p + ALONG * length * HS
        bone(f"{name}_0{i + 1}_R", p, q, parent, roll_to=PALMN, connect=i > 0)
        p, parent = q, f"{name}_0{i + 1}_R"
p, parent = hp(*THUMB_BASE), "hand_R"
for i, length in enumerate(THUMB_LEN):
    q = p + tdir * length * HS
    bone(f"thumb_0{i + 1}_R", p, q, parent, roll_to=PALMN, connect=i > 0)
    p, parent = q, f"thumb_0{i + 1}_R"
bone("upper_arm_L", sL, eL, "clavicle_L")
bone("forearm_L", eL, wL, "upper_arm_L", connect=True)
bpy.ops.object.mode_set(mode="OBJECT")

# ---- skinning: automatic weights, with a nearest-bone fallback if the heat solve leaves vertices unweighted
deform = ["upper_arm_R", "forearm_R", "hand_R"] + [f"{f}_0{i}_R" for f in (*FINGERS, "thumb") for i in (1, 2, 3)]
for b in arm_data.bones:
    b.use_deform = b.name in deform
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type="ARMATURE_AUTO")
unweighted = [v.index for v in arm.data.vertices if sum(g.weight for g in v.groups) < 1e-4]
weighting = "automatic"
if unweighted:
    weighting = f"nearest-bone fallback ({len(unweighted)} vertices had no automatic weight)"
    segs = {b.name: (rig.matrix_world @ b.head_local, rig.matrix_world @ b.tail_local) for b in arm_data.bones
            if b.name in deform}
    groups = {name: arm.vertex_groups.get(name) or arm.vertex_groups.new(name=name) for name in segs}
    for g in groups.values():
        g.remove(list(range(len(arm.data.vertices))))
    for v in arm.data.vertices:
        w = arm.matrix_world @ v.co
        dists = []
        for name, (a, b) in segs.items():
            ab = b - a
            t = max(0.0, min(1.0, (w - a).dot(ab) / ab.length_squared))
            dists.append(((w - (a + ab * t)).length, name))
        dists.sort()
        (d0, n0), (d1, n1) = dists[0], dists[1]
        w0, w1 = 1 / (d0 ** 4 + 1e-12), 1 / (d1 ** 4 + 1e-12)
        groups[n0].add([v.index], w0 / (w0 + w1), "REPLACE")
        groups[n1].add([v.index], w1 / (w0 + w1), "REPLACE")

# ---- pose through the bones
WR = Vector((-0.25, -0.15, 1.52))  # wrist beside the face, a little above shoulder height
POLE = S + Vector((-0.3, -0.05, -0.25))  # elbow out and down


def elbow(s, w, a, b, pole):
    d = min((w - s).length, a + b - 1e-4)
    u = (w - s).normalized()
    cos_a = (a * a + d * d - b * b) / (2 * a * d)
    side = (pole - s) - u * (pole - s).dot(u)
    return s + u * (a * cos_a) + side.normalized() * (a * math.sqrt(max(0.0, 1 - cos_a * cos_a)))


ER = elbow(S, WR, UPPER, FORE, POLE)

# hand frame: fingers up, palm facing out (-X) so the index finger is in front; then tilted 15 degrees to camera
yh = n((-0.05, -0.05, 1.0))
zh = n(Vector((-1, 0, 0)) - yh * yh.dot(Vector((-1, 0, 0))))
xh = yh.cross(zh)
tilt = Matrix.Rotation(math.radians(-15), 3, yh)
xh, zh = tilt @ xh, tilt @ zh


def frame(head_pt, y, x_hint):
    y = y.normalized()
    z = x_hint.cross(y).normalized()
    x = y.cross(z).normalized()
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = head_pt
    return m


def posed(a, b, c):
    return WR + (xh * a + zh * b + yh * c) * HS


targets = {
    "upper_arm_R": frame(S, ER - S, Vector((0, -1, 0))),
    "forearm_R": frame(ER, WR - ER, Vector((0, -1, 0))),
    "hand_R": frame(WR, yh, xh),
}
CURL = {"index": (8, 6, 4), "middle": (8, 6, 4), "ring": (70, 85, 55), "pinky": (75, 85, 55)}  # degrees per joint
finger_joints = {}
for name, (s, base, lens, r) in FINGERS.items():
    p, angle = posed(s, 0, base), 0.0
    joints = [p]
    for i, length in enumerate(lens):
        angle += math.radians(CURL[name][i])
        d = yh * math.cos(angle) + zh * math.sin(angle)
        targets[f"{name}_0{i + 1}_R"] = frame(p, d, xh)
        p = p + d * length * HS
        joints.append(p)
    finger_joints[name] = joints
p = posed(*THUMB_BASE)
for i, (a, b, c) in enumerate(((-0.15, 0.55, 0.8), (-0.6, 0.6, 0.5), (-0.85, 0.45, 0.25))):  # folded over the palm
    d = n(xh * a + zh * b + yh * c)
    targets[f"thumb_0{i + 1}_R"] = frame(p, d, zh.cross(d))
    p = p + d * THUMB_LEN[i] * HS
for name in ["upper_arm_R", "forearm_R", "hand_R"] + [f"{f}_0{i}_R" for f in (*FINGERS, "thumb") for i in (1, 2, 3)]:
    rig.pose.bones[name].matrix = rig.matrix_world.inverted() @ targets[name]
    bpy.context.view_layer.update()

# ---- the calling card, pinched between index and middle near the second joint
body_top = max((body.matrix_world @ Vector(c)).z for c in body.bound_box)
H = body_top - Z_CUT  # working units per final unit (the model is normalised to 1.0 tall below)
# 63 x 88 card ratio, shown 1.35x so the doodle reads at hero size; faces 1 mm apart so they never z-fight
CARD_SCALE = 1.35
CARD_W, CARD_H, CARD_T, CLEAR = 0.063 * H * CARD_SCALE, 0.088 * H * CARD_SCALE, 0.0012, 0.0005 * H
pi, pm = finger_joints["index"][1], finger_joints["middle"][1]
normal = xh.normalized()
up0 = (finger_joints["index"][1] - finger_joints["index"][0]).normalized()
up0 = (up0 - normal * up0.dot(normal)).normalized()
lean_a, lean_b = Matrix.Rotation(math.radians(22), 3, normal) @ up0, Matrix.Rotation(math.radians(-22), 3, normal) @ up0
up = lean_a if lean_a.x < lean_b.x else lean_b  # lean the top away from his face
right = up.cross(normal).normalized()
out = right if right.x < 0 else -right  # away from his face
# the fingers pinch the lower inner corner, leaving the doodle clear
centre = (pi + pm) / 2 + up * (CARD_H * 0.5 - CARD_H * 0.16) + out * (CARD_W * 0.3)
card_parts = []
for side, sign in (("front", 1), ("back", -1)):
    bpy.ops.mesh.primitive_plane_add(size=1)
    o = cur()
    basis = Matrix((right * sign, up, normal * sign)).transposed().to_4x4()
    basis.translation = centre + normal * (CARD_T / 2) * sign
    o.matrix_world = basis @ Matrix.Diagonal((CARD_W, CARD_H, 1, 1))
    o.data.materials.append(mat("Card" + side.title(), "#ffffff", rough=0.4,
                                image=os.path.join(CACHE, f"card-{side}.png")))
    card_parts.append(o)
bpy.ops.object.select_all(action="DESELECT")
for o in card_parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = card_parts[0]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.join()
card = cur()
card.name = card.data.name = "Card"
bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
mw = card.matrix_world.copy()  # parent to the index finger bone so it follows the hand
card.parent, card.parent_type, card.parent_bone = rig, "BONE", "index_02_R"
bpy.context.view_layer.update()
card.matrix_world = mw

# ---- bake the pose into the mesh, check the card against both fingers
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.modifier_apply(modifier=arm.modifiers[0].name)
pinch = {g.index for g in arm.vertex_groups if g.name.startswith(("index_", "middle_"))}
min_gap, inside = 1e9, 0
for v in arm.data.vertices:
    if not v.groups or max(v.groups, key=lambda g: g.weight).group not in pinch:
        continue
    rel = (arm.matrix_world @ v.co) - centre
    if abs(rel.dot(up)) <= CARD_H / 2 and abs(rel.dot(right)) <= CARD_W / 2:
        inside += 1
        min_gap = min(min_gap, abs(rel.dot(normal)) - CARD_T / 2)
mw = card.matrix_world.copy()
card.parent = None
card.matrix_world = mw
bpy.data.objects.remove(rig)
arm.vertex_groups.clear()

# ---- one mesh for the figure, then normalise: 1.0 tall, origin at the centre of the thigh cut
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
kaito = cur()
kaito.name = kaito.data.name = "Kaito"
norm = Matrix.Scale(1 / H, 4) @ Matrix.Translation((0, 0, -Z_CUT))
for o in (kaito, card):
    o.matrix_world = norm @ o.matrix_world
bpy.ops.object.select_all(action="DESELECT")
kaito.select_set(True)
bpy.context.view_layer.objects.active = kaito
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.select_all(action="DESELECT")
card.select_set(True)
bpy.context.view_layer.objects.active = card
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)  # keep the origin at the card centre

print("SUMMARY vertices:", sum(len(o.data.vertices) for o in (kaito, card)))
print(f"SUMMARY hair: {hair_clamped} of {hair_total} vertices clamped into the {HAIR_BOUND}x head ellipsoid")
print(f"SUMMARY skinning: {weighting}")
gap_txt = f"{min_gap / H:.5f}" if inside else "n/a"
print(f"SUMMARY card vs fingers: {inside} finger vertices over the card, min clearance {gap_txt} "
      f"(need >= {CLEAR / H:.4f}) -> {'OK' if inside and min_gap >= CLEAR else 'CHECK'}")

export_and_render("kaito", cam_loc=(-0.36, -1.75, 0.62), target=(-0.05, 0.0, 0.5), lens=55, res=(1000, 1250),
                  outline=0.003, sun_rot=(48, 0, -35), skip_outline=("Card",))
