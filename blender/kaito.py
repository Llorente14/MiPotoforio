"""Cel-shaded Kaito Kid (fan art), waist-up close-up, flicking his calling card.

Run from the repo root (the card textures come from the vector card first):
    node scripts/card-textures.mjs
    blender -b --factory-startup -P blender/kaito.py

Outputs public/models/kaito.glb (nodes "Kaito" and "Card"; animate the card) and public/renders/kaito.webp.
Faces -Y, z up, metres. His right hand (screen left) holds the card beside his face.
"""
import math
import os
import sys

sys.path.append(os.path.dirname(__file__))
import bpy  # noqa: E402
from toon import (CACHE, ball, box, cur, export_and_render, join, keep, limb, loft, mat, poly,  # noqa: E402
                  strand)

SUIT = mat("Suit", "#f3f0e8", rough=0.5)
LINING = mat("Lining", "#dfe3ee")
SHIRT = mat("Shirt", "#2d4f9e")
TIE = mat("Tie", "#c23a2e")
BAND = mat("HatBand", "#2d4f9e")
SKIN = mat("Skin", "#f2d3ba")
HAIR = mat("Hair", "#2a221e")
EYE = mat("Eye", "#1f2f5c")
SILVER = mat("Silver", "#c9ced6", rough=0.25, metal=1.0)
CLOVER = mat("Clover", "#2f8a57")

# ------------------------------------------------------------------ torso (waist up)
loft("Jacket", [
    ((0, 0.01, 0.9), 0.165, 0.112),
    ((0, 0.01, 1.05), 0.158, 0.106),
    ((0, 0.0, 1.2), 0.178, 0.112),
    ((0, 0.0, 1.32), 0.2, 0.118),
    ((0, 0.0, 1.4), 0.195, 0.108),
    ((0, 0.0, 1.45), 0.12, 0.08),
], SUIT, caps=(True, True))
for sx in (-1, 1):  # shoulder pads
    ball((0.18 * sx, 0.0, 1.4), 0.07, SUIT, scale=(1.05, 0.95, 0.6))

# shirt V, tie and lapels sit just proud of the jacket front (front surface ~ y = -0.115)
poly("ShirtV", [(-0.066, -0.118, 1.43), (0.066, -0.118, 1.43), (0.0, -0.124, 1.2)], [(2, 1, 0)], SHIRT, smooth=False)
poly("Tie", [(-0.021, -0.127, 1.425), (0.021, -0.127, 1.425), (0.03, -0.13, 1.22), (0.0, -0.133, 1.17),
             (-0.03, -0.13, 1.22)], [(4, 3, 2, 1, 0)], TIE, smooth=False)
box((0, -0.125, 1.405), (0, -0.125, 1.43), 0.05, 0.02, TIE, bevel=0.006)  # knot
for sx in (-1, 1):
    poly("Lapel", [(0.07 * sx, -0.12, 1.44), (0.11 * sx, -0.122, 1.38), (0.064 * sx, -0.128, 1.3),
                   (0.005 * sx, -0.126, 1.19), (0.05 * sx, -0.121, 1.42)],
         [(0, 1, 2, 3, 4) if sx > 0 else (4, 3, 2, 1, 0)], SUIT, smooth=False)
ball((0.0, -0.118, 1.12), 0.011, SUIT)  # jacket button

# ------------------------------------------------------------------ cape (behind, billowing to his left)
nu, nv = 18, 12
cv = []
for j in range(nv + 1):
    v = j / nv
    for i in range(nu + 1):
        u = i / nu
        theta = math.radians(-80 + 160 * u)  # sweep around the back
        r = 0.2 + 0.2 * v + (0.14 * v * v if u > 0.5 else 0.04 * v)
        flutter = 0.025 * math.sin(u * 9 + v * 4) * v
        cv.append((math.sin(theta) * r + 0.12 * v * v * (u - 0.3), math.cos(theta) * r * 0.75 + 0.03 + flutter,
                   1.44 - 0.62 * v + 0.12 * v * v * u))
cf = [(j * (nu + 1) + i, j * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i)
      for j in range(nv) for i in range(nu)]
cape = poly("Cape", cv, cf, SUIT)
cape.data.materials.append(LINING)
for p in cape.data.polygons:  # blue-grey lining on the inner face via solidify's rim/shell material offset
    p.material_index = 0
sol = cape.modifiers.new("Thickness", "SOLIDIFY")
sol.thickness, sol.material_offset = 0.012, 1
cape.modifiers.new("Smooth", "SUBSURF").levels = 1

# ------------------------------------------------------------------ neck and head
loft("Neck", [((0, 0.0, 1.43), 0.045, 0.045), ((0, -0.005, 1.53), 0.042, 0.042)], SKIN, n=16)
HEAD = (0.0, -0.01, 1.64)
ball(HEAD, 0.112, SKIN, scale=(0.95, 0.98, 1.06), segs=32)
ball((0.0, -0.05, 1.575), 0.072, SKIN, scale=(0.95, 0.9, 1.0), segs=24)  # jaw, tapering to an anime chin
for sx in (-1, 1):
    ball((0.105 * sx, -0.005, 1.63), 0.022, SKIN, scale=(0.5, 1.0, 1.3))  # ears
# eyes (his left eye; the monocle covers the right), brows and a smirk
ball((0.042, -0.103, 1.645), 0.019, EYE, scale=(0.75, 0.35, 1.15))
strand([(0.022, -0.106, 1.677), (0.045, -0.11, 1.684), (0.068, -0.1, 1.678)], 0.0045, HAIR, taper=(0.6, 1.0))
strand([(-0.022, -0.106, 1.677), (-0.045, -0.11, 1.682), (-0.068, -0.1, 1.672)], 0.0045, HAIR, taper=(0.6, 1.0))
ball((-0.042, -0.103, 1.645), 0.017, EYE, scale=(0.75, 0.35, 1.1))
strand([(-0.03, -0.098, 1.575), (0.0, -0.104, 1.571), (0.03, -0.1, 1.58)], 0.003, HAIR, taper=(0.8, 1.0))

# messy hair: spiky locks flaring out from under the hat brim, each with its own kick
for i in range(15):
    a = math.radians(-120 + i * 17)
    kick = (0.06, -0.04, 0.03, -0.06, 0.0)[i % 5]
    root = (0.1 * math.sin(a), 0.1 * math.cos(a) - 0.01, 1.715)
    mid = (0.15 * math.sin(a + 0.1), 0.14 * math.cos(a + 0.1), 1.68 + kick * 0.3)
    tip = (0.2 * math.sin(a + 0.22), 0.17 * math.cos(a + 0.22), 1.63 + kick)
    strand([root, mid, tip], 0.032, HAIR, taper=(1.0, 0.0))
# fringe: pointed bangs falling over the brow, alternating length
for x, dx, z in ((-0.085, -0.045, 1.645), (-0.05, -0.02, 1.62), (-0.015, 0.0, 1.655), (0.02, 0.02, 1.625),
                 (0.055, 0.04, 1.65), (0.09, 0.06, 1.64)):
    strand([(x * 0.7, -0.06, 1.74), (x, -0.108, 1.71), (x + dx, -0.12, z)], 0.026, HAIR, taper=(1.0, 0.0))
ball((0.0, -0.112, 1.615), 0.011, SKIN, scale=(0.8, 1.0, 1.2))  # nose
for sx in (-1, 1):  # shirt collar points either side of the knot
    poly("ShirtCollar", [(0.012 * sx, -0.125, 1.44), (0.06 * sx, -0.112, 1.47), (0.05 * sx, -0.123, 1.405)],
         [(0, 1, 2) if sx > 0 else (2, 1, 0)], SUIT, smooth=False)
ball((0.0, 0.0, 1.69), 0.108, HAIR, scale=(1.02, 1.04, 0.62))  # hair mass under the hat

# ------------------------------------------------------------------ top hat (tilted toward his left)
hat = []
loft("Crown", [((0, 0, 0.0), 0.112, 0.104), ((0, 0, 0.12), 0.106, 0.098), ((0, 0, 0.215), 0.112, 0.104)],
     SUIT, n=32, sub=1)
hat.append(cur())
loft("Band", [((0, 0, 0.004), 0.116, 0.108), ((0, 0, 0.05), 0.112, 0.104)], BAND, n=32, sub=1)
hat.append(cur())
loft("Brim", [((0, 0, -0.008), 0.198, 0.184), ((0, 0, 0.0), 0.204, 0.19), ((0, 0, 0.008), 0.198, 0.184)], SUIT, n=48, sub=0)
hat.append(cur())
pivot = bpy.data.objects.new("HatPivot", None)
bpy.context.collection.objects.link(pivot)
pivot.location = (0.012, 0.004, 1.735)
pivot.rotation_euler = (math.radians(-8), math.radians(9), math.radians(4))
for h in hat:
    h.parent = pivot

# ------------------------------------------------------------------ monocle over his right eye, cord to the lapel
bpy.ops.mesh.primitive_torus_add(major_radius=0.034, minor_radius=0.0045, major_segments=32, minor_segments=8,
                                 location=(-0.043, -0.112, 1.645), rotation=(math.radians(90), 0, 0))
keep(cur(), SILVER)
strand([(-0.07, -0.118, 1.625), (-0.1, -0.13, 1.55), (-0.095, -0.135, 1.46), (-0.08, -0.128, 1.39)], 0.0022, SILVER,
       taper=(1, 1))
for ox, oz in ((0, 0.012), (-0.011, 0.0), (0.011, 0.0)):  # clover charm
    ball((-0.08 + ox, -0.132, 1.37 + oz), 0.008, CLOVER, segs=12)
strand([(-0.08, -0.132, 1.37), (-0.084, -0.134, 1.352)], 0.002, CLOVER, taper=(1, 1))

# ------------------------------------------------------------------ arms
# his right arm: raised, hand beside the face flicking the card (screen left)
sR, eR, wR = (-0.2, -0.0, 1.38), (-0.33, -0.13, 1.25), (-0.25, -0.2, 1.53)
limb(sR, eR, 0.062, SUIT, r2=0.056)
ball(eR, 0.056, SUIT)
limb(eR, wR, 0.055, SUIT, r2=0.048)
loft("CuffR", [((0, 0, 0), 0.05, 0.05), ((0, 0, 0.022), 0.05, 0.05)], SHIRT, n=16, sub=0)
cuff = cur()
cuff.location = wR
cuff.rotation_mode = "QUATERNION"
from mathutils import Vector  # noqa: E402

cuff.rotation_quaternion = (Vector(wR) - Vector(eR)).to_track_quat("Z", "Y")
# gloved hand: palm, two extended fingers (index, middle) pinching the card, curled ring/little fingers, thumb
palm = (-0.245, -0.215, 1.585)
ball(palm, 0.042, SUIT, scale=(0.85, 0.6, 1.1))
for dx, length in ((-0.012, 0.075), (0.012, 0.082)):
    strand([(palm[0] + dx, palm[1] - 0.01, palm[2] + 0.035), (palm[0] + dx * 1.3, palm[1] - 0.03, palm[2] + 0.07),
            (palm[0] + dx * 1.6 - 0.015, palm[1] - 0.055, palm[2] + 0.035 + length)], 0.013, SUIT, taper=(1, 0.75))
for dx in (0.03, 0.042):
    strand([(palm[0] + dx * 0.6, palm[1] - 0.012, palm[2] + 0.03), (palm[0] + dx, palm[1] - 0.045, palm[2] + 0.04),
            (palm[0] + dx * 0.8, palm[1] - 0.04, palm[2] + 0.005)], 0.012, SUIT, taper=(1, 0.8))
strand([(palm[0] + 0.03, palm[1], palm[2] - 0.02), (palm[0] + 0.05, palm[1] - 0.04, palm[2] + 0.0),
        (palm[0] + 0.045, palm[1] - 0.06, palm[2] + 0.03)], 0.013, SUIT, taper=(1, 0.8))

# his left arm: relaxed, half hidden by the cape
sL, eL, wL = (0.2, 0.0, 1.38), (0.29, 0.03, 1.15), (0.25, -0.05, 0.96)
limb(sL, eL, 0.062, SUIT, r2=0.056)
ball(eL, 0.056, SUIT)
limb(eL, wL, 0.055, SUIT, r2=0.05)

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
                  outline=0.0045, sun_rot=(48, 0, -35), skip_outline=("Card",))
