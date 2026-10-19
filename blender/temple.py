"""Procedural cel-shaded three-storey pagoda in the style of Kiyomizu-dera's Sanjunoto.

Run from the repo root:
    blender -b --factory-startup -P blender/temple.py

Outputs public/models/temple.glb (node "Temple") and public/renders/temple.webp.
Palette: vermilion body, washi-cream panels, muted copper-green roofs, antique-gold spire.
"""
import os
import sys

sys.path.append(os.path.dirname(__file__))
import bpy  # noqa: E402
from toon import ball, cur, export_and_render, join, keep, limb, mat  # noqa: E402

VERMILION = mat("Vermilion", "#e04a30", rough=0.5)
DARK_RED = mat("DarkRed", "#8e2a22", rough=0.6)
WASHI = mat("Washi", "#efe6d2", rough=0.7)
LATTICE = mat("Lattice", "#3a2a24", rough=0.6)
ROOF = mat("Roof", "#4f7a6a", rough=0.5, metal=0.2)
GOLD = mat("Gold", "#c9a227", rough=0.3, metal=0.9)
STONE = mat("Stone", "#8d8a82", rough=0.9)


def block(cx, cy, cz, sx, sy, sz, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz))
    cur().scale = (sx, sy, sz)
    return keep(cur(), material)


def mesh(name, verts, faces, material, thickness=0.0):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    if thickness:
        o.modifiers.new("T", "SOLIDIFY").thickness = thickness
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier="T")  # join() would drop it otherwise
    return keep(o, material)


def ring(half, z, corner_lift=0.0, corner_push=1.0):
    """8 points CCW from +X: edge midpoints at z, corners lifted/pushed out."""
    pts = []
    for mx, my, cx, cy in ((1, 0, 1, 1), (0, 1, -1, 1), (-1, 0, -1, -1), (0, -1, 1, -1)):
        pts.append((mx * half, my * half, z))
        pts.append((cx * half * corner_push, cy * half * corner_push, z + corner_lift))
    return pts


def roof(z, size):
    """Hipped roof whose eave corners sweep upward (the classic flared silhouette)."""
    outer = ring(size * 0.8, z, corner_lift=0.24, corner_push=1.14)
    inner = ring(size * 0.3, z + 0.3)
    faces = [(i, (i + 1) % 8, 8 + (i + 1) % 8, 8 + i) for i in range(8)] + [tuple(range(8, 16))]
    return mesh("Roof", outer + inner, faces, ROOF, thickness=0.07)


# ---------- stone base (tapered) ----------
mesh("Base", ring(0.8, 0) + ring(0.66, 0.35),
     [(i, (i + 1) % 8, 8 + (i + 1) % 8, 8 + i) for i in range(8)] + [tuple(range(8, 16))], STONE)

# ---------- three storeys ----------
for i, s in enumerate((1.0, 0.85, 0.72)):
    z0 = 0.35 + i * 0.75
    if i:  # balcony deck sitting on the roof below
        block(0, 0, z0 + 0.02, s * 1.18, s * 1.18, 0.04, DARK_RED)
    block(0, 0, z0 + 0.25, s, s, 0.5, VERMILION)
    for ax in ((1, 0), (0, 1), (-1, 0), (0, -1)):  # washi panel + lattice on every face
        nx, ny = ax
        d = s / 2 + 0.005
        w = s * 0.5
        block(nx * d, ny * d, z0 + 0.27, w if ny else 0.01, w if nx else 0.01, 0.3, WASHI)
        for k in (-1, 0, 1):
            off = k * w / 4
            block(nx * (d + 0.004) + ny * off * 0 + (off if ny else 0), ny * (d + 0.004) + (off if nx else 0),
                  z0 + 0.27, 0.015 if ny else 0.01, 0.015 if nx else 0.01, 0.3, LATTICE)
        for k in (-1, 1):  # corner posts
            block(nx * d + (k * s / 2 if ny else 0), ny * d + (k * s / 2 if nx else 0), z0 + 0.25,
                  0.05, 0.05, 0.5, DARK_RED)
    roof(z0 + 0.5, s * (1.25 if i < 2 else 1.15))

# ---------- sorin (spire) ----------
top = 0.35 + 2 * 0.75 + 0.5 + 0.28
limb((0, 0, top), (0, 0, top + 0.8), 0.022, GOLD, verts=8)
for k in range(7):
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.085 - k * 0.006, depth=0.018,
                                        location=(0, 0, top + 0.12 + k * 0.08))
    keep(cur(), GOLD)
ball((0, 0, top + 0.86), 0.05, GOLD)

join("Temple", smooth_angle=30)

# shadowless fill from the camera side so the vermilion walls under the eaves don't go brown
fill = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", "SUN"))
fill.data.energy, fill.data.use_shadow = 2.0, False
fill.rotation_euler = (1.35, 0, 0.62)
bpy.context.collection.objects.link(fill)
export_and_render("temple", cam_loc=(3.3, -4.6, 1.5), target=(0, 0, 1.55), lens=40, res=(900, 1200), outline=0.014)
