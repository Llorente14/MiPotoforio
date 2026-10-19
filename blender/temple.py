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


def roof(z, size, per_side=12, rings=9):
    """Hipped roof with a concave sweep and eave corners that curl upward (the classic flared silhouette)."""
    outer, inner = size * 0.8, size * 0.22
    n = per_side * 4
    verts = []
    for j in range(rings + 1):
        t = j / rings
        half = outer + (inner - outer) * t
        for i in range(n):
            p = i / per_side
            k, f = int(p), p - int(p)
            c = 1 - min(f, 1 - f) * 2  # 1 at a corner, 0 mid-side
            corners = ((1, -1), (1, 1), (-1, 1), (-1, -1))
            ax, ay = corners[k]
            bx, by = corners[(k + 1) % 4]
            push = 1 + 0.13 * c ** 3 * (1 - t)
            x = (ax + (bx - ax) * f) * half * push
            y = (ay + (by - ay) * f) * half * push
            verts.append((x, y, z + 0.34 * t ** 1.7 + 0.24 * c ** 3 * (1 - t) ** 2))
    faces = [(j * n + i, j * n + (i + 1) % n, (j + 1) * n + (i + 1) % n, (j + 1) * n + i)
             for j in range(rings) for i in range(n)]
    faces.append(tuple(range(rings * n, rings * n + n)))
    return mesh("Roof", verts, faces, ROOF, thickness=0.06)


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
    # bracket band (masugumi) carrying the eaves, then the roof
    block(0, 0, z0 + 0.47, s * 1.12, s * 1.12, 0.06, DARK_RED)
    for ax in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        for k in range(-3, 4):
            nx, ny = ax
            block(nx * s * 0.6 + (k * s * 0.14 if ny else 0), ny * s * 0.6 + (k * s * 0.14 if nx else 0), z0 + 0.43,
                  0.05 if ny else 0.06, 0.05 if nx else 0.06, 0.03, GOLD if k == 0 else DARK_RED)
    if i:  # balcony railing round the deck
        for ax in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            nx, ny = ax
            d = s * 0.58
            block(nx * d, ny * d, z0 + 0.11, s * 1.16 if ny else 0.02, s * 1.16 if nx else 0.02, 0.02, DARK_RED)
            for k in range(-4, 5):
                block(nx * d + (k * s * 0.13 if ny else 0), ny * d + (k * s * 0.13 if nx else 0), z0 + 0.07,
                      0.018, 0.018, 0.09, DARK_RED)
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
