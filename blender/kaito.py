"""Cel-shaded Kaito Kid (fan art), waist-up close-up, flicking his calling card.

Run from the repo root (the card and face textures come from vector sources first):
    node scripts/textures.mjs
    blender -b --factory-startup -P blender/kaito.py

Outputs public/models/kaito.glb (nodes "Kaito" and "Card"; animate the card) and public/renders/kaito.webp.
Faces -Y, z up, metres. His right hand (screen left) holds the card beside his face.
"""
import math
import os
import sys

sys.path.append(os.path.dirname(__file__))
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from toon import CACHE, ball, cur, decal, export_and_render, join, keep, limb, loft, mat, parts, poly, strand  # noqa: E402

SUIT = mat("Suit", "#f4f2ec", rough=0.5)
SUIT_SHADE = mat("SuitSeam", "#dcdad3")
LINING = mat("Lining", "#e3e7f0")
SHIRT = mat("Shirt", "#2f56a8")
TIE = mat("Tie", "#c8323a")
BAND = mat("HatBand", "#2f56a8")
SKIN = mat("Skin", "#f6dcc6")
HAIR = mat("Hair", "#3a2c26")
SILVER = mat("Silver", "#cfd4dc", rough=0.25, metal=1.0)
CLOVER = mat("Clover", "#2f8a57")
FRONT_Y = -0.118  # jacket front surface at chest height


def thick(obj, t):
    """Give a flat panel real thickness (applied at join)."""
    obj.modifiers.new("Thickness", "SOLIDIFY").thickness = t
    return obj


# ------------------------------------------------------------------ torso: chest, waist, shoulders
loft("Jacket", [
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

# shirt front (V between the lapels) and its collar points, tie with a real knot
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

# notched lapels with thickness, rolling over the chest
for sx in (-1, 1):
    pts = [(0.074 * sx, FRONT_Y + 0.002, 1.448), (0.122 * sx, FRONT_Y + 0.006, 1.392),
           (0.104 * sx, FRONT_Y - 0.004, 1.372), (0.112 * sx, FRONT_Y - 0.002, 1.35),
           (0.07 * sx, FRONT_Y - 0.01, 1.27), (0.006 * sx, FRONT_Y - 0.012, 1.16),
           (0.054 * sx, FRONT_Y - 0.004, 1.43)]
    thick(poly("Lapel", pts, [tuple(range(7)) if sx > 0 else tuple(reversed(range(7)))], SUIT, smooth=False), 0.006)
for z in (1.12, 1.05):  # jacket buttons
    ball((0.0, FRONT_Y + 0.004, z), 0.011, SUIT_SHADE, scale=(1, 0.5, 1), segs=16)
thick(poly("Pocket", [(0.07, FRONT_Y + 0.004, 1.29), (0.14, FRONT_Y + 0.012, 1.292), (0.14, FRONT_Y + 0.012, 1.28),
                      (0.07, FRONT_Y + 0.004, 1.278)], [(0, 1, 2, 3)], SUIT_SHADE, smooth=False), 0.003)

# ------------------------------------------------------------------ cape: behind him, billowing to his left
nu, nv = 24, 14
cv = []
for j in range(nv + 1):
    v = j / nv
    for i in range(nu + 1):
        u = i / nu
        theta = math.radians(-82 + 164 * u)  # sweep around the back
        r = 0.2 + 0.2 * v + (0.14 * v * v if u > 0.5 else 0.04 * v)
        flutter = 0.03 * math.sin(u * 11 + v * 4) * v
        cv.append((math.sin(theta) * r + 0.12 * v * v * (u - 0.3), math.cos(theta) * r * 0.75 + 0.03 + flutter,
                   1.445 - 0.62 * v + 0.12 * v * v * u))
cf = [(j * (nu + 1) + i, j * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i)
      for j in range(nv) for i in range(nu)]
cape = poly("Cape", cv, cf, SUIT)
cape.data.materials.append(LINING)
sol = cape.modifiers.new("Thickness", "SOLIDIFY")
sol.thickness, sol.material_offset = 0.01, 1
cape.modifiers.new("Smooth", "SUBSURF").levels = 1

# ------------------------------------------------------------------ neck and an anime head (pointed chin)
loft("Neck", [((0, 0.0, 1.43), 0.044, 0.044), ((0, -0.006, 1.545), 0.04, 0.04)], SKIN, n=20)
head_start = len(parts)  # everything from here to the monocle is the head group (scaled up below)
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

# ------------------------------------------------------------------ hair: messy, spiky, a layered fringe
ball((0.0, 0.006, 1.712), 0.108, HAIR, scale=(1.04, 1.07, 0.66), segs=32)  # mass under the hat
for layer, (rad, z0, count, lean) in enumerate(((0.1, 1.715, 17, 0.0), (0.104, 1.69, 13, 0.18))):
    for i in range(count):
        a = math.radians(-118 + i * (236 / (count - 1))) + lean
        kick = (0.06, -0.035, 0.03, -0.055, 0.01, 0.045)[(i + layer) % 6]
        root = (rad * math.sin(a), rad * math.cos(a) - 0.008, z0)
        mid = (0.16 * math.sin(a + 0.1), 0.145 * math.cos(a + 0.1), z0 - 0.035 + kick * 0.25)
        tip = (0.21 * math.sin(a + 0.24), 0.175 * math.cos(a + 0.24), z0 - 0.085 + kick)
        strand([root, mid, tip], 0.03 - layer * 0.006, HAIR, taper=(1.0, 0.0))
for sx in (-1, 1):  # sideburn locks in front of the ears
    strand([(0.088 * sx, -0.05, 1.71), (0.1 * sx, -0.066, 1.66), (0.094 * sx, -0.07, 1.6)], 0.016, HAIR,
           taper=(1.0, 0.0))
# fringe: pointed bangs in two layers, alternating length, tips curling to his left
for x, dx, z in ((-0.088, -0.04, 1.648), (-0.058, -0.022, 1.622), (-0.026, -0.004, 1.66), (0.006, 0.014, 1.63),
                 (0.038, 0.03, 1.655), (0.07, 0.046, 1.636), (0.094, 0.06, 1.662)):
    strand([(x * 0.6, -0.055, 1.745), (x, -0.108, 1.712), (x + dx, -0.124, z)], 0.025, HAIR, taper=(1.0, 0.0))
for x, dx, z in ((-0.07, -0.02, 1.672), (-0.01, 0.01, 1.676), (0.05, 0.035, 1.68)):
    strand([(x * 0.5, -0.07, 1.75), (x, -0.114, 1.722), (x + dx, -0.128, z)], 0.018, HAIR, taper=(1.0, 0.0))

# ------------------------------------------------------------------ top hat (white, blue band), tilted
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

# ------------------------------------------------------------------ monocle over his right eye, cord to the lapel
bpy.ops.mesh.primitive_torus_add(major_radius=0.031, minor_radius=0.004, major_segments=40, minor_segments=10,
                                 location=(-0.042, -0.118, 1.645), rotation=(math.radians(90), 0, 0))
keep(cur(), SILVER)
strand([(-0.068, -0.12, 1.625), (-0.098, -0.132, 1.55), (-0.094, -0.136, 1.46), (-0.08, -0.13, 1.395)], 0.0018,
       SILVER, taper=(1, 1))
for ox, oz in ((0, 0.012), (-0.011, 0.0), (0.011, 0.0)):  # clover charm
    ball((-0.08 + ox, -0.134, 1.375 + oz), 0.0075, CLOVER, segs=14)
strand([(-0.08, -0.134, 1.375), (-0.084, -0.136, 1.356)], 0.0018, CLOVER, taper=(1, 1))

# anime proportions: a bigger head on a shorter neck. Scale the whole head group about the neck top.
bpy.context.view_layer.update()
grow = (Matrix.Translation((0.0, -0.01, 1.508)) @ Matrix.Scale(1.12, 4)
        @ Matrix.Translation((0.0, 0.01, -1.53)))  # scale about the neck top, then sit 22 mm lower
for o in [o for o in parts[head_start:] if o.parent is None] + [pivot]:
    o.matrix_world = grow @ o.matrix_world

# ------------------------------------------------------------------ arms and gloves
# his right arm: raised, hand beside the face flicking the card (screen left)
sR, eR, wR = (-0.195, 0.0, 1.38), (-0.33, -0.13, 1.25), (-0.25, -0.2, 1.53)
limb(sR, eR, 0.062, SUIT, r2=0.055, verts=24)
ball(eR, 0.055, SUIT, segs=24)
limb(eR, wR, 0.054, SUIT, r2=0.047, verts=24)
cuff = loft("CuffR", [((0, 0, 0), 0.049, 0.049), ((0, 0, 0.024), 0.049, 0.049)], SHIRT, n=20, sub=0)
cuff.location = wR
cuff.rotation_mode = "QUATERNION"
cuff.rotation_quaternion = (Vector(wR) - Vector(eR)).to_track_quat("Z", "Y")
palm = (-0.245, -0.215, 1.585)
ball(palm, 0.04, SUIT, scale=(0.85, 0.6, 1.1), segs=24)
# index and middle fingers extended, pinching the card; three knuckles each
for dx, length in ((-0.012, 0.075), (0.012, 0.082)):
    strand([(palm[0] + dx, palm[1] - 0.01, palm[2] + 0.034), (palm[0] + dx * 1.2, palm[1] - 0.026, palm[2] + 0.058),
            (palm[0] + dx * 1.4 - 0.008, palm[1] - 0.042, palm[2] + 0.034 + length * 0.7),
            (palm[0] + dx * 1.6 - 0.016, palm[1] - 0.056, palm[2] + 0.034 + length)], 0.0125, SUIT, taper=(1, 0.75))
for dx in (0.03, 0.042):  # ring and little fingers curled in
    strand([(palm[0] + dx * 0.6, palm[1] - 0.012, palm[2] + 0.03), (palm[0] + dx, palm[1] - 0.045, palm[2] + 0.04),
            (palm[0] + dx * 0.8, palm[1] - 0.04, palm[2] + 0.005)], 0.0115, SUIT, taper=(1, 0.8))
strand([(palm[0] + 0.03, palm[1], palm[2] - 0.02), (palm[0] + 0.05, palm[1] - 0.04, palm[2] + 0.0),
        (palm[0] + 0.045, palm[1] - 0.06, palm[2] + 0.03)], 0.0125, SUIT, taper=(1, 0.8))  # thumb
for k in range(3):  # glove stitching on the back of the hand
    strand([(palm[0] - 0.012 + k * 0.012, palm[1] + 0.022, palm[2] - 0.012),
            (palm[0] - 0.012 + k * 0.012, palm[1] + 0.024, palm[2] + 0.022)], 0.0016, SUIT_SHADE, taper=(1, 1))

# his left arm: relaxed, half hidden by the cape
sL, eL, wL = (0.195, 0.0, 1.38), (0.29, 0.03, 1.15), (0.25, -0.05, 0.96)
limb(sL, eL, 0.062, SUIT, r2=0.055, verts=24)
ball(eL, 0.055, SUIT, segs=24)
limb(eL, wL, 0.054, SUIT, r2=0.049, verts=24)

body = join("Kaito", smooth_angle=None)
bpy.data.objects.remove(pivot)

# ------------------------------------------------------------------ the calling card (two back-to-back planes)
card_parts = []
for side, flip in (("front", 0.0), ("back", math.pi)):
    bpy.ops.mesh.primitive_plane_add(size=1, rotation=(math.radians(90), 0, flip))
    o = cur()
    o.scale = (0.1, 0.14, 1)  # 1.6x real size so it reads beside the face
    o.location.y = -0.0007 if flip == 0 else 0.0007
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
card.location = (-0.285, -0.255, 1.715)
card.rotation_euler = (math.radians(-6), math.radians(14), math.radians(-18))
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)  # keep the origin at the card centre

export_and_render("kaito", cam_loc=(-0.4, -1.95, 1.58), target=(-0.06, 0.0, 1.5), lens=55, res=(1000, 1250),
                  outline=0.0035, sun_rot=(48, 0, -35), skip_outline=("Card",))
