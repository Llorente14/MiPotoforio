"""Procedural cel-shaded Akai Shuichi (fan art), kneeling with a sniper rifle.

Run from the repo root:
    blender -b --factory-startup -P blender/akai.py

Outputs public/models/akai.glb (nodes "Akai", "Rifle") and public/renders/akai.webp.
Built facing -Y, then the whole scene is turned so the rifle points to the viewer's front-left.
"""
import math
import os
import sys

sys.path.append(os.path.dirname(__file__))
import bpy  # noqa: E402
from toon import ball, box, cur, export_and_render, join, keep, limb, mat, spike  # noqa: E402

JACKET = mat("Jacket", "#1f2226", rough=0.45)
SHIRT = mat("Shirt", "#34325a")
PANTS = mat("Pants", "#3d3f43")
SHOE = mat("Shoe", "#141416", rough=0.4)
SKIN = mat("Skin", "#e2b98f")
HAIR = mat("Hair", "#18181c")
BEANIE = mat("Beanie", "#2f3742", rough=0.9)
OLIVE = mat("RifleBody", "#3f4a36", rough=0.5)
GUNMETAL = mat("Gunmetal", "#141518", rough=0.35, metal=0.8)
LENS = mat("Lens", "#9fc3d8", rough=0.05, metal=0.3)

# ---------- legs: right knee down, left knee up ----------
limb((-0.1, 0, 0.55), (-0.12, 0.12, 0.08), 0.075, PANTS)
ball((-0.12, 0.12, 0.08), 0.07, PANTS)
limb((-0.12, 0.12, 0.08), (-0.12, 0.5, 0.1), 0.06, PANTS)
box((-0.12, 0.5, 0.06), (-0.12, 0.66, 0.02), 0.09, 0.08, SHOE)
limb((0.1, 0, 0.55), (0.14, -0.38, 0.5), 0.075, PANTS)
ball((0.14, -0.38, 0.5), 0.072, PANTS)
limb((0.14, -0.38, 0.5), (0.14, -0.4, 0.09), 0.06, PANTS)
box((0.14, -0.36, 0.04), (0.14, -0.6, 0.04), 0.1, 0.08, SHOE)

# ---------- torso (leaning into the shot) ----------
bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.16, radius2=0.2, depth=0.52, location=(0, -0.04, 0.8),
                                rotation=(math.radians(12), 0, 0))
cur().scale = (1, 0.7, 1)
keep(cur(), JACKET)
box((0, -0.15, 1.0), (0, -0.17, 0.72), 0.12, 0.01, SHIRT)  # shirt showing through the open jacket
limb((0, -0.1, 1.02), (0, -0.12, 1.12), 0.045, SKIN)  # neck

# ---------- head: cheek on the stock, beanie, curly fringe ----------
head = (-0.03, -0.12, 1.2)
ball(head, 0.11, SKIN, scale=(1, 1, 1.12))
ball((head[0], head[1] + 0.01, head[2] + 0.05), 0.12, BEANIE, scale=(1.02, 1.05, 0.85))
limb((head[0], head[1] + 0.01, 1.2), (head[0], head[1] + 0.01, 1.24), 0.118, BEANIE, verts=12)  # folded brim
for i in range(7):  # hair peeking out at the back and sides
    a = math.radians(-60 + i * 20)
    spike((head[0] + 0.1 * math.sin(a), head[1] + 0.1 * math.cos(a), 1.2),
          (math.sin(a), math.cos(a), -0.9), 0.035, 0.1, HAIR)
spike((head[0] - 0.05, head[1] - 0.09, 1.22), (-0.3, -0.4, -1), 0.02, 0.1, HAIR)  # the curl over his eye
spike((head[0] - 0.02, head[1] - 0.1, 1.22), (0.1, -0.4, -1), 0.018, 0.08, HAIR)

# ---------- arms: right on the grip, left supporting the handguard ----------
sR, eR, hR = (-0.2, -0.08, 1.02), (-0.3, -0.22, 0.88), (-0.1, -0.33, 1.0)
sL, eL, hL = (0.2, -0.08, 1.02), (0.12, -0.32, 0.82), (-0.07, -0.56, 1.04)
for s, e, h in ((sR, eR, hR), (sL, eL, hL)):
    ball(s, 0.065, JACKET)
    limb(s, e, 0.055, JACKET)
    ball(e, 0.055, JACKET)
    limb(e, h, 0.048, JACKET)
    ball(h, 0.04, SKIN, scale=(0.9, 1.2, 0.8))
body = join("Akai", smooth_angle=50)

# ---------- rifle (separate node for recoil) along -Y, scope at eye height ----------
X, Z = -0.08, 1.08
box((X, 0.02, Z - 0.04), (X, -0.3, Z), 0.05, 0.11, OLIVE)  # stock
box((X, -0.3, Z), (X, -0.62, Z), 0.06, 0.08, OLIVE)  # receiver + handguard
box((X, -0.34, Z - 0.04), (X, -0.4, Z - 0.13), 0.04, 0.05, GUNMETAL)  # magazine
limb((X, -0.62, Z + 0.01), (X, -1.18, Z + 0.01), 0.012, GUNMETAL, verts=6)  # barrel
limb((X, -1.12, Z + 0.01), (X, -1.2, Z + 0.01), 0.02, GUNMETAL, verts=6)  # muzzle brake
limb((X, -0.24, Z + 0.09), (X, -0.56, Z + 0.09), 0.022, GUNMETAL, verts=8)  # scope tube
limb((X, -0.22, Z + 0.09), (X, -0.27, Z + 0.09), 0.032, GUNMETAL, verts=8)  # eyepiece
limb((X, -0.53, Z + 0.09), (X, -0.6, Z + 0.09), 0.036, GUNMETAL, verts=8)  # objective bell
limb((X, -0.6, Z + 0.09), (X, -0.602, Z + 0.09), 0.03, LENS, verts=8)
for y in (-0.33, -0.48):  # scope rings
    box((X, y, Z + 0.03), (X, y, Z + 0.07), 0.03, 0.02, GUNMETAL)
for sx in (-1, 1):  # folded bipod
    limb((X, -0.6, Z - 0.03), (X + sx * 0.03, -0.75, Z - 0.08), 0.007, GUNMETAL, verts=4)
rifle = join("Rifle", smooth_angle=35)

# turn the scene so the rifle aims at the viewer's front-left
for o in (body, rifle):
    o.select_set(True)
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

export_and_render("akai", cam_loc=(1.7, -2.6, 1.0), target=(0, -0.35, 0.6), lens=45, res=(1200, 900), outline=0.005)
