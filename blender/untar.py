"""Procedural cel-shaded UNTAR Building 2 (Universitas Tarumanagara).

Run from the repo root:
    blender -b --factory-startup -P blender/untar.py

Outputs public/models/untar.glb (node "Untar") and public/renders/untar.webp.
Front faces -Y. Units are arbitrary (tower ~3.1 high).
"""
import math
import os
import sys

sys.path.append(os.path.dirname(__file__))
import bpy  # noqa: E402
from toon import cur, export_and_render, join, keep, mat  # noqa: E402

CLADDING = mat("Cladding", "#d9d3c7", rough=0.5)
RIB = mat("Rib", "#b9b2a4", rough=0.5)
GLASS = mat("Glass", "#4a78b0", rough=0.12, metal=0.35)
FRAME = mat("Frame", "#9aa3ad", rough=0.4, metal=0.4)
STRIPE = mat("Stripe", "#2d4f9e", rough=0.3)
CONCRETE = mat("Concrete", "#c7c9cc", rough=0.8)
EMBLEM = mat("Emblem", "#3a3d42", rough=0.5)
LETTER = mat("Letter", "#e9e6df", rough=0.4)
WINDOW = mat("Window", "#f1eee6", rough=0.6)


def block(x0, x1, y0, y1, z0, z1, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    cur().scale = (x1 - x0, y1 - y0, z1 - z0)
    return keep(cur(), material)


def text(body, loc, size, material, depth=0.01):
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(90), 0, 0))
    t = cur()
    t.data.body = body
    t.data.size = size
    t.data.extrude = depth
    t.data.align_x = "CENTER"
    bpy.ops.object.convert(target="MESH")
    return keep(cur(), material)


# ---------- podium ----------
block(-1.25, 1.1, -0.75, 0.7, 0, 0.36, CONCRETE)
block(-1.0, 0.05, -0.76, -0.74, 0.07, 0.3, GLASS)  # glass shopfront
block(-1.3, 0.3, -1.0, -0.4, 0.36, 0.39, CONCRETE)  # entrance canopy
text("UNIVERSITAS TARUMANAGARA", (-0.47, -0.775, 0.17), 0.07, LETTER, depth=0.003)

# ---------- blue curtain-wall block (left) ----------
block(-1.1, -0.3, -0.15, 0.6, 0.36, 2.55, GLASS)
for x, z in ((-0.95, 2.05), (-0.75, 1.4), (-0.52, 1.85), (-0.85, 0.85), (-0.45, 0.65)):  # white window frames
    block(x - 0.05, x + 0.05, -0.16, -0.15, z - 0.14, z + 0.14, WINDOW)
for i in range(6):  # floor lines
    block(-1.1, -0.3, -0.155, -0.15, 0.6 + i * 0.32, 0.615 + i * 0.32, FRAME)
text("UNTAR", (-0.72, -0.17, 2.38), 0.15, LETTER, depth=0.02)

# ---------- beige tower slab with sloped roof ----------
x0, x1, y0, y1, zl, zr = 0.1, 0.95, -0.35, 0.35, 2.75, 3.15
verts = [(x0, y0, 0.36), (x1, y0, 0.36), (x1, y1, 0.36), (x0, y1, 0.36),
         (x0, y0, zl), (x1, y0, zr), (x1, y1, zr), (x0, y1, zl)]
faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
me = bpy.data.meshes.new("Slab")
me.from_pydata(verts, [], faces)
slab = bpy.data.objects.new("Slab", me)
bpy.context.collection.objects.link(slab)
keep(slab, CLADDING)
for i in range(1, 9):  # vertical ribs on the front face, following the slope
    x = x0 + i * (x1 - x0) / 9
    top = zl + (zr - zl) * (x - x0) / (x1 - x0) - 0.25
    block(x - 0.01, x + 0.01, y0 - 0.02, y0, 0.4, top, RIB)
block(x0 - 0.01, x0 + 0.015, y0 - 0.025, y0 + 0.02, 0.4, zl, STRIPE)  # blue edge stripe

# emblem: dark hexagon with a light rim, near the top of the front face
for r, y, m in ((0.17, y0 - 0.03, LETTER), (0.14, y0 - 0.04, EMBLEM)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=r, depth=0.02, location=(0.62, y, 2.72),
                                        rotation=(math.radians(90), 0, math.radians(0)))
    keep(cur(), m)

# ---------- glass bay with horizontal fins, in front of the slab's left side ----------
block(-0.32, 0.12, -0.5, 0.25, 0.36, 2.62, GLASS)
for i in range(13):
    z = 0.5 + i * 0.165
    block(-0.34, 0.14, -0.52, 0.25, z, z + 0.02, FRAME)
block(-0.36, 0.16, -0.56, 0.25, 2.62, 2.66, CONCRETE)  # top canopy
block(-0.34, -0.32, -0.52, 0.25, 0.36, 2.62, FRAME)  # corner mullions
block(0.12, 0.14, -0.52, 0.25, 0.36, 2.62, FRAME)

join("Untar", smooth_angle=30).scale.z = 1.35  # the real tower is slender
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
export_and_render("untar", cam_loc=(-2.8, -5.6, 1.1), target=(-0.1, 0, 2.05), lens=42, res=(900, 1200), outline=0.016)
