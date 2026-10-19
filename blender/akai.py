"""Procedural cel-shaded Akai Shuichi (fan art), kneeling with a sniper rifle.

Run from the repo root (the face texture comes from a vector source first):
    node scripts/textures.mjs
    blender -b --factory-startup -P blender/akai.py

Outputs public/models/akai.glb (nodes "Akai", "Rifle") and public/renders/akai.webp.
Built facing -Y, then the whole scene is turned so the rifle points to the viewer's front-left.
"""
import math
import os
import sys

sys.path.append(os.path.dirname(__file__))
import bpy  # noqa: E402
from toon import CACHE, ball, cur, decal, export_and_render, join, keep, limb, loft, mat, poly, strand  # noqa: E402

JACKET = mat("Jacket", "#202328", rough=0.45)
JACKET_EDGE = mat("JacketEdge", "#34383f")
SHIRT = mat("Shirt", "#3a3560")
PANTS = mat("Pants", "#2e3238")
SHOE = mat("Shoe", "#141416", rough=0.4)
SOLE = mat("Sole", "#5a5550")
SKIN = mat("Skin", "#ecc9a8")
HAIR = mat("Hair", "#17171b")
BEANIE = mat("Beanie", "#262b33", rough=0.9)
STOCK = mat("RifleBody", "#3d4934", rough=0.5)
GUNMETAL = mat("Gunmetal", "#1a1c20", rough=0.35, metal=0.8)
LENS = mat("Lens", "#9fc3d8", rough=0.05, metal=0.3)


def thick(obj, t, offset=0.0):
    mod = obj.modifiers.new("Thickness", "SOLIDIFY")
    mod.thickness, mod.offset = t, offset
    return obj


def shoe(heel, toe, material):
    """A shoe from heel to toe on the ground: a rounded upper with a toe cap, on a flat sole."""
    hx, hy, hz = heel
    tx, ty, _ = toe
    length = abs(ty - hy)
    mid = ((hx + tx) / 2, (hy + ty) / 2, hz)
    ball((mid[0], mid[1], hz + 0.045), 1.0, material, scale=(0.05, length / 2, 0.045), segs=24)
    ball((tx, ty - 0.02 * (1 if ty > hy else -1), hz + 0.03), 1.0, material, scale=(0.046, 0.04, 0.03), segs=20)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1, depth=0.014, location=(mid[0], mid[1], hz + 0.007))
    sole = cur()
    sole.scale = (0.052, length / 2 + 0.012, 1)
    keep(sole, SOLE)


# ------------------------------------------------------------------ legs: right knee down, left knee up
limb((-0.1, 0, 0.55), (-0.12, 0.12, 0.09), 0.078, PANTS, r2=0.066, verts=24)
ball((-0.12, 0.12, 0.09), 0.068, PANTS, segs=24)
limb((-0.12, 0.12, 0.09), (-0.12, 0.48, 0.1), 0.062, PANTS, r2=0.052, verts=24)
shoe((-0.12, 0.47, 0.0), (-0.12, 0.7, 0.0), SHOE)
limb((0.1, 0, 0.55), (0.14, -0.38, 0.5), 0.078, PANTS, r2=0.068, verts=24)
ball((0.14, -0.38, 0.5), 0.07, PANTS, segs=24)
limb((0.14, -0.38, 0.5), (0.14, -0.4, 0.1), 0.064, PANTS, r2=0.054, verts=24)
shoe((0.14, -0.33, 0.0), (0.14, -0.6, 0.0), SHOE)

# ------------------------------------------------------------------ torso: open jacket leaning into the shot
torso = loft("Torso", [
    ((0, -0.0, 0.54), 0.15, 0.1),
    ((0, -0.02, 0.68), 0.155, 0.105),
    ((0, -0.045, 0.84), 0.18, 0.115),
    ((0, -0.07, 0.98), 0.2, 0.115),
    ((0, -0.08, 1.04), 0.16, 0.095),
    ((0, -0.085, 1.07), 0.07, 0.06),
], JACKET, n=32)
# shirt showing through the open front, jacket edges and zip
thick(poly("ShirtPanel", [(-0.06, -0.16, 1.02), (0.06, -0.16, 1.02), (0.05, -0.142, 0.66), (-0.05, -0.142, 0.66)],
           [(3, 2, 1, 0)], SHIRT, smooth=False), 0.004)
for sx in (-1, 1):
    strand([(0.062 * sx, -0.164, 1.03), (0.058 * sx, -0.158, 0.85), (0.052 * sx, -0.146, 0.62)], 0.009, JACKET_EDGE,
           taper=(1, 1))
# stand-up collar
loft("Collar", [((0, -0.085, 1.04), 0.09, 0.07), ((0, -0.088, 1.1), 0.085, 0.065)], JACKET, n=24, caps=(False, False))
limb((0, -0.09, 1.04), (0, -0.115, 1.13), 0.042, SKIN, verts=20)  # neck

# ------------------------------------------------------------------ head: cheek on the stock, beanie, black hair
head = loft("Head", [
    ((-0.03, -0.172, 1.105), 0.012, 0.01),
    ((-0.03, -0.165, 1.12), 0.045, 0.04),
    ((-0.03, -0.15, 1.15), 0.075, 0.07),
    ((-0.03, -0.132, 1.19), 0.095, 0.09),
    ((-0.03, -0.124, 1.23), 0.1, 0.096),
    ((-0.03, -0.12, 1.27), 0.096, 0.094),
    ((-0.03, -0.118, 1.31), 0.07, 0.07),
    ((-0.03, -0.118, 1.33), 0.02, 0.02),
], SKIN, n=32, sub=2)
decal(head, os.path.join(CACHE, "akai-face.png"), x_range=(-0.13, 0.07), z_range=(1.08, 1.32))
for sx in (-1, 1):
    ball((-0.03 + 0.098 * sx, -0.118, 1.2), 0.02, SKIN, scale=(0.45, 1.0, 1.3))
# beanie: a knitted dome with a ribbed turn-up
loft("Beanie", [((-0.03, -0.112, 1.235), 0.108, 0.106), ((-0.03, -0.11, 1.29), 0.104, 0.102),
                ((-0.03, -0.11, 1.34), 0.08, 0.08), ((-0.03, -0.11, 1.37), 0.035, 0.035),
                ((-0.03, -0.11, 1.375), 0.005, 0.005)], BEANIE, n=32, sub=1)
for k in range(4):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.11, minor_radius=0.007, major_segments=40, minor_segments=8,
                                     location=(-0.03, -0.112, 1.238 + k * 0.012))
    cur().scale = (1.0, 0.98, 1.0)
    keep(cur(), BEANIE)
# black hair: long locks falling from under the beanie, and the curl over his right eye
for i in range(11):
    a = math.radians(-70 + i * 14)
    root = (-0.03 + 0.1 * math.sin(a), -0.112 + 0.1 * math.cos(a), 1.235)
    tip = (-0.03 + 0.13 * math.sin(a + 0.15), -0.112 + 0.125 * math.cos(a + 0.15), 1.14 + 0.02 * (i % 3))
    mid = ((root[0] + tip[0]) / 2 + 0.015 * math.sin(a), (root[1] + tip[1]) / 2 + 0.015 * math.cos(a), 1.19)
    strand([root, mid, tip], 0.024, HAIR, taper=(1.0, 0.0))
for x, z in ((-0.1, 1.17), (-0.065, 1.19), (0.01, 1.2), (0.045, 1.185)):  # fringe under the turn-up
    strand([(x * 0.8 - 0.006, -0.19, 1.25), (x, -0.215, 1.225), (x + 0.01, -0.222, z)], 0.016, HAIR, taper=(1, 0))
strand([(-0.08, -0.21, 1.24), (-0.1, -0.226, 1.2), (-0.085, -0.228, 1.165), (-0.07, -0.224, 1.18)], 0.008, HAIR,
       taper=(1, 0.4))  # the curl

# ------------------------------------------------------------------ arms: right on the grip, left under the handguard
sR, eR, hR = (-0.19, -0.08, 1.0), (-0.3, -0.22, 0.88), (-0.1, -0.33, 1.0)
sL, eL, hL = (0.19, -0.08, 1.0), (0.12, -0.32, 0.82), (-0.07, -0.56, 1.04)
for s, e, h in ((sR, eR, hR), (sL, eL, hL)):
    ball(s, 0.066, JACKET, segs=24)
    limb(s, e, 0.058, JACKET, r2=0.052, verts=24)
    ball(e, 0.052, JACKET, segs=24)
    limb(e, h, 0.05, JACKET, r2=0.042, verts=24)
    ball(h, 0.036, SKIN, scale=(0.9, 1.25, 0.8), segs=20)
    for k in range(3):  # fingers wrapped round the grip / handguard
        strand([(h[0] - 0.02 + k * 0.016, h[1] - 0.02, h[2] + 0.01), (h[0] - 0.018 + k * 0.016, h[1] - 0.04, h[2] - 0.01),
                (h[0] - 0.012 + k * 0.016, h[1] - 0.03, h[2] - 0.035)], 0.0085, SKIN, taper=(1, 0.8))
body = join("Akai")

# ------------------------------------------------------------------ rifle (separate node for recoil), scope at eye height
X, Z = -0.08, 1.08
# stock and receiver as one profile in the YZ plane: butt, comb, wrist, pistol grip, receiver, fore-end
profile = [(0.04, 0.95), (0.04, 1.1), (-0.08, 1.11), (-0.2, 1.085), (-0.26, 1.08), (-0.3, 1.06), (-0.31, 0.96),
           (-0.27, 0.94), (-0.25, 1.0), (-0.2, 1.02), (-0.08, 0.99)]
fore = [(-0.3, 1.06), (-0.66, 1.07), (-0.68, 1.05), (-0.66, 1.03), (-0.34, 1.025)]
for name, pts in (("Stock", profile), ("Fore", fore)):
    o = poly(name, [(X - 0.024, y, z) for y, z in pts], [tuple(range(len(pts)))], STOCK, smooth=False)
    thick(o, 0.048)
    o.modifiers.new("Bevel", "BEVEL").width = 0.006
loft("Receiver", [((0, 0, 0), 0.022, 0.022), ((0, 0, 0.52), 0.019, 0.019)], GUNMETAL, n=20, sub=0)
r = cur()
r.rotation_euler = (math.radians(90), 0, 0)
r.location = (X, -0.18, Z + 0.035)
limb((X, -0.68, Z + 0.035), (X, -1.18, Z + 0.035), 0.012, GUNMETAL, r2=0.01, verts=16)  # barrel
loft("Muzzle", [((0, 0, 0), 0.019, 0.019), ((0, 0, 0.07), 0.019, 0.019)], GUNMETAL, n=16, sub=0)
m = cur()
m.rotation_euler = (math.radians(90), 0, 0)
m.location = (X, -1.12, Z + 0.035)
for y in (-1.13, -1.15, -1.17):  # muzzle brake ports
    limb((X - 0.02, y, Z + 0.035), (X + 0.02, y, Z + 0.035), 0.004, SHOE, verts=8)
# scope: tube, eyepiece, objective bell, turrets, rings, lenses
limb((X, -0.24, Z + 0.1), (X, -0.56, Z + 0.1), 0.021, GUNMETAL, verts=20)
limb((X, -0.2, Z + 0.1), (X, -0.27, Z + 0.1), 0.03, GUNMETAL, r2=0.023, verts=20)
limb((X, -0.53, Z + 0.1), (X, -0.62, Z + 0.1), 0.023, GUNMETAL, r2=0.036, verts=20)
limb((X, -0.62, Z + 0.1), (X, -0.623, Z + 0.1), 0.032, LENS, verts=20)
limb((X, -0.2, Z + 0.1), (X, -0.197, Z + 0.1), 0.026, LENS, verts=20)
limb((X, -0.4, Z + 0.12), (X, -0.4, Z + 0.15), 0.013, GUNMETAL, verts=16)  # elevation turret
limb((X + 0.02, -0.4, Z + 0.1), (X + 0.05, -0.4, Z + 0.1), 0.013, GUNMETAL, verts=16)  # windage turret
for y in (-0.31, -0.49):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.026, minor_radius=0.006, major_segments=24, minor_segments=8,
                                     location=(X, y, Z + 0.1), rotation=(math.radians(90), 0, 0))
    keep(cur(), GUNMETAL)
    limb((X, y, Z + 0.06), (X, y, Z + 0.075), 0.008, GUNMETAL, verts=12)
# bolt handle, magazine, trigger guard, folded bipod
limb((X - 0.02, -0.33, Z + 0.04), (X - 0.07, -0.34, Z + 0.02), 0.006, GUNMETAL, verts=12)
ball((X - 0.072, -0.34, Z + 0.018), 0.012, GUNMETAL, segs=16)
loft("Mag", [((0, 0, 0), 0.02, 0.035), ((0, 0, 0.08), 0.02, 0.035)], GUNMETAL, n=8, sub=0)
cur().location = (X, -0.4, Z - 0.13)
bpy.ops.mesh.primitive_torus_add(major_radius=0.025, minor_radius=0.004, major_segments=20, minor_segments=6,
                                 location=(X, -0.29, Z - 0.06), rotation=(0, math.radians(90), 0))
keep(cur(), GUNMETAL)
for sx in (-1, 1):
    limb((X, -0.6, Z - 0.02), (X + sx * 0.03, -0.78, Z - 0.06), 0.007, GUNMETAL, verts=10)
    ball((X + sx * 0.03, -0.78, Z - 0.06), 0.009, SHOE, segs=12)
rifle = join("Rifle", smooth_angle=35)

# turn the scene so the rifle aims at the viewer's front-left
pivot = bpy.data.objects.new("Pivot", None)
bpy.context.collection.objects.link(pivot)
for o in (body, rifle):
    o.parent = pivot
pivot.rotation_euler.z = math.radians(-35)
bpy.context.view_layer.update()
for o in (body, rifle):
    mw = o.matrix_world.copy()
    o.parent = None
    o.matrix_world = mw
bpy.data.objects.remove(pivot)
for o in (body, rifle):  # bake the turn so both nodes keep their origin at 0,0,0
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

export_and_render("akai", cam_loc=(1.7, -2.6, 1.0), target=(0, -0.35, 0.6), lens=45, res=(1200, 900), outline=0.004)
