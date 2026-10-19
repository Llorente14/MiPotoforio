"""Procedural low-poly Kaito Kid (fan art) in a card-flick pose.

Run from the repo root:
    blender -b --factory-startup -P blender/kaito.py

Outputs:
    public/models/kaito.glb        nodes: "Kaito" (body) and "Card" (animate this one)
    public/renders/kaito.webp      still render for phones / no-WebGL
    public/textures/card-front.png, card-back.png   for the 2D card fallback
"""
import math
import os

import bpy
import numpy as np
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_MODEL = os.path.join(ROOT, "public", "models")
OUT_RENDER = os.path.join(ROOT, "public", "renders")
OUT_TEX = os.path.join(ROOT, "public", "textures")
for d in (OUT_MODEL, OUT_RENDER, OUT_TEX):
    os.makedirs(d, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)

# ---------- materials ----------
def mat(name, hex_color, rough=0.6, metal=0.0, image=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    c = int(hex_color[1:], 16)
    bsdf.inputs["Base Color"].default_value = ((c >> 16) / 255, (c >> 8 & 255) / 255, (c & 255) / 255, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if image:
        tex = m.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = image
        m.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return m

WHITE = mat("Suit", "#f4f3ef")
SHIRT = mat("Shirt", "#2a5db0")
TIE = mat("Tie", "#e0607e")
BAND = mat("HatBand", "#1f6fc4")
SKIN = mat("Skin", "#f2d0b4")
HAIR = mat("Hair", "#2b211f")
SILVER = mat("Monocle", "#c9ced6", rough=0.25, metal=1.0)
CLOVER = mat("Clover", "#3c9a5f")

parts = []


def keep(obj, material):
    obj.data.materials.append(material)
    parts.append(obj)
    return obj


def cur():
    return bpy.context.active_object


# ---------- shape helpers ----------
def limb(a, b, r, material, verts=8):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d.length, location=(a + b) / 2)
    o = cur()
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.to_track_quat("Z", "Y")
    return keep(o, material)


def ball(p, r, material, scale=(1, 1, 1), sub=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r, location=p)
    o = cur()
    o.scale = scale
    return keep(o, material)


def spike(p, direction, r, length, material):
    d = Vector(direction).normalized()
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=r, radius2=0, depth=length, location=Vector(p) + d * length / 2)
    o = cur()
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.to_track_quat("Z", "Y")
    return keep(o, material)


def poly(name, verts, faces, material):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    return keep(o, material)


# ---------- body (faces -Y, feet at z=0, metres) ----------
# legs: slight contrapposto
for hip, knee, ankle in (((-0.1, 0, 0.95), (-0.1, -0.04, 0.5), (-0.11, -0.03, 0.08)),
                         ((0.1, 0, 0.95), (0.12, 0.01, 0.5), (0.14, 0.04, 0.08))):
    limb(hip, knee, 0.07, WHITE)
    ball(knee, 0.07, WHITE)
    limb(knee, ankle, 0.06, WHITE)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(ankle[0], ankle[1] - 0.05, 0.04))
    cur().scale = (0.1, 0.24, 0.08)
    keep(cur(), WHITE)

# torso + jacket tails
bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.17, radius2=0.21, depth=0.5, location=(0, 0, 1.18))
cur().scale = (1, 0.65, 1)
keep(cur(), WHITE)
bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.2, radius2=0.17, depth=0.24, location=(0, 0, 0.84))
cur().scale = (1, 0.7, 1)
keep(cur(), WHITE)
for sx in (-1, 1):  # shoulder ruffles
    ball((0.2 * sx, 0, 1.42), 0.07, WHITE, scale=(1.2, 1, 0.7))

# shirt V + tie on the chest
poly("ShirtV", [(-0.075, -0.137, 1.43), (0.075, -0.137, 1.43), (0, -0.142, 1.13)], [(2, 1, 0)], SHIRT)
poly("Tie", [(-0.02, -0.146, 1.41), (0.02, -0.146, 1.41), (0.028, -0.148, 1.2), (0, -0.15, 1.15), (-0.028, -0.148, 1.2)],
     [(4, 3, 2, 1, 0)], TIE)

# right arm: raised, flicking the card (character's right = -X)
sR, eR, wR = (-0.22, 0, 1.4), (-0.4, -0.1, 1.52), (-0.46, -0.28, 1.7)
limb(sR, eR, 0.055, WHITE)
ball(eR, 0.055, WHITE)
limb(eR, wR, 0.048, WHITE)
ball(wR, 0.045, WHITE, scale=(0.8, 1.2, 1))
# left arm: hand in pocket
sL, eL, wL = (0.22, 0, 1.4), (0.31, 0.04, 1.15), (0.2, -0.05, 0.96)
limb(sL, eL, 0.055, WHITE)
ball(eL, 0.055, WHITE)
limb(eL, wL, 0.048, WHITE)

# neck + head
limb((0, 0, 1.42), (0, 0, 1.53), 0.045, SKIN)
ball((0, 0, 1.62), 0.115, SKIN, scale=(1, 1, 1.12), sub=2)

# messy hair: spikes around the back/sides + fringe
for i in range(9):
    a = math.radians(-20 + i * 25)  # sweep around the back
    p = (0.1 * math.sin(a), 0.1 * math.cos(a), 1.66)
    spike(p, (math.sin(a), math.cos(a), -0.6), 0.04, 0.11, HAIR)
for x in (-0.06, -0.02, 0.025, 0.065):
    spike((x, -0.08, 1.71), (x * 2, -0.5, -1), 0.035, 0.09, HAIR)

# monocle on the right eye + string down to the lapel with a clover charm
bpy.ops.mesh.primitive_torus_add(major_radius=0.034, minor_radius=0.006, major_segments=12, minor_segments=4,
                                 location=(-0.045, -0.118, 1.625), rotation=(math.radians(90), 0, 0))
keep(cur(), SILVER)
limb((-0.05, -0.12, 1.59), (-0.075, -0.135, 1.47), 0.0025, SILVER, verts=4)
ball((-0.075, -0.137, 1.46), 0.012, CLOVER)

# top hat, tilted
hat = []
for r, depth, z, m in ((0.19, 0.015, 0.0, WHITE), (0.11, 0.24, 0.12, WHITE), (0.113, 0.04, 0.03, BAND)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=r, depth=depth, location=(0, 0, z))
    hat.append(keep(cur(), m))
pivot = bpy.data.objects.new("HatPivot", None)
bpy.context.collection.objects.link(pivot)
pivot.location = (0.01, 0.01, 1.72)
pivot.rotation_euler = (math.radians(-6), math.radians(8), 0)
for h in hat:
    h.parent = pivot

# cape: wind-blown sheet sweeping to the character's left (+X)
nu, nv = 10, 14
verts = []
for j in range(nv + 1):
    v = j / nv
    for i in range(nu + 1):
        u = i / nu
        x = (-0.22 - 0.15 * v) + u * (0.44 + 0.9 * v)
        y = 0.1 + 0.35 * v + 0.06 * math.sin(u * math.tau + v * 3) * v
        z = 1.42 - 1.25 * v + 0.3 * u * v * v
        verts.append((x, y, z))
faces = [(j * (nu + 1) + i, j * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i)
         for j in range(nv) for i in range(nu)]
cape = poly("Cape", verts, faces, WHITE)
cape.modifiers.new("Thickness", "SOLIDIFY").thickness = 0.012

# join everything except the card into one mesh named "Kaito"
bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier="Thickness") if o.modifiers else None
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
# bake transforms first, otherwise the joined node inherits the first part's rotation
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.join()
body = cur()
body.name = body.data.name = "Kaito"
bpy.data.objects.remove(pivot)
for p in body.data.polygons:
    p.use_smooth = False


# ---------- card textures (numpy, drawn in top-left pixel space) ----------
CW, CH = 256, 358


def blank():
    return np.ones((CH, CW, 4), dtype=np.float32)


yy, xx = np.mgrid[0:CH, 0:CW]


def ink_seg(img, x0, y0, x1, y1, w=3):
    px, py = xx - x0, yy - y0
    dx, dy = x1 - x0, y1 - y0
    t = np.clip((px * dx + py * dy) / (dx * dx + dy * dy), 0, 1)
    img[np.hypot(px - t * dx, py - t * dy) <= w, :3] = 0


def ink_disc(img, cx, cy, r):
    img[np.hypot(xx - cx, yy - cy) <= r, :3] = 0


def ink_ring(img, cx, cy, r, w=3):
    img[np.abs(np.hypot(xx - cx, yy - cy) - r) <= w, :3] = 0


def club(img, cx, cy, s):
    for ox, oy in ((0, -s * 0.55), (-s * 0.5, s * 0.15), (s * 0.5, s * 0.15)):
        ink_disc(img, cx + ox, cy + oy, s * 0.45)
    for k in range(int(s)):  # stem
        ink_seg(img, cx, cy, cx - s * 0.4 + k * 0.8, cy + s * 1.1, 1)


def letter_a(img, x, y, h, flip=False):
    s = -1 if flip else 1
    ink_seg(img, x, y + s * h, x + h * 0.35, y, 3)
    ink_seg(img, x + h * 0.35, y, x + h * 0.7, y + s * h, 3)
    ink_seg(img, x + h * 0.15, y + s * h * 0.6, x + h * 0.55, y + s * h * 0.6, 2)


front = blank()
letter_a(front, 16, 18, 34)
club(front, 33, 78, 16)
letter_a(front, CW - 42, CH - 18, 34, flip=True)
club(front, CW - 33, CH - 92, 16)
# Kaito doodle: top hat + monocle + grin
cx, cy = CW / 2, CH / 2
for a, b in (((cx - 38, cy - 80), (cx + 38, cy - 80)), ((cx - 38, cy - 80), (cx - 38, cy - 10)),
             ((cx + 38, cy - 80), (cx + 38, cy - 10)), ((cx - 70, cy - 8), (cx + 70, cy - 14)),
             ((cx - 38, cy - 24), (cx + 38, cy - 24))):
    ink_seg(front, *a, *b)
ink_ring(front, cx - 24, cy + 14, 16)
ink_seg(front, cx - 30, cy + 30, cx - 44, cy + 60, 2)
ink_disc(front, cx - 44, cy + 62, 5)
grin = (np.abs(np.hypot(xx - cx, yy - (cy - 6)) - 46) <= 3) & (yy > cy + 20)
front[grin, :3] = 0
for k in range(-3, 4):
    ink_seg(front, cx + k * 11, cy + 26, cx + k * 11, cy + 38, 1)

back = blank()
u, v = (xx - 12) / 34.0, (yy - 12) / 46.0
diamond = (np.abs(u - np.floor(u) - 0.5) + np.abs(v - np.floor(v) - 0.5)) < 0.5
inside = (xx > 12) & (xx < CW - 12) & (yy > 12) & (yy < CH - 12)
back[diamond & inside, :3] = (0.12, 0.3, 0.6)


def to_image(name, arr):
    img = bpy.data.images.new(name, CW, CH, alpha=True)
    img.pixels.foreach_set(np.flipud(arr).ravel())
    img.filepath_raw = os.path.join(OUT_TEX, name + ".png")
    img.file_format = "PNG"
    img.save()
    img.pack()
    return img


# ---------- card: two back-to-back planes held in the right hand ----------
card_parts = []
for img_name, arr, flip in (("card-front", front, 0), ("card-back", back, math.pi)):
    bpy.ops.mesh.primitive_plane_add(size=1, rotation=(math.radians(90), 0, flip))
    o = cur()
    o.scale = (0.144, 0.2, 1)  # 1.6x real size so it reads on screen
    o.location.y = -0.0006 if flip == 0 else 0.0006
    o.data.materials.append(mat(img_name, "#ffffff", rough=0.4, image=to_image(img_name, arr)))
    card_parts.append(o)
bpy.ops.object.select_all(action="DESELECT")
for o in card_parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = card_parts[0]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.join()
card = cur()
card.name = card.data.name = "Card"
card.location = (-0.5, -0.33, 1.84)
card.rotation_euler = (math.radians(-10), math.radians(20), math.radians(-12))

# ---------- export ----------
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=os.path.join(OUT_MODEL, "kaito.glb"),
    export_format="GLB",
    export_apply=True,
    export_yup=True,
    export_draco_mesh_compression_enable=True,
)

# ---------- still render (transparent WebP) ----------
scene = bpy.context.scene
for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try:
        scene.render.engine = engine
        break
    except TypeError:
        pass
scene.render.film_transparent = True
scene.render.resolution_x, scene.render.resolution_y = 900, 1200
scene.view_settings.view_transform = "Standard"
scene.render.image_settings.file_format = "WEBP"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.quality = 85

world = bpy.data.worlds.new("Night")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.05, 0.07, 0.16, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.2
scene.world = world

moon = bpy.data.lights.new("Moon", "SUN")
moon.energy = 3.5
moon.color = (0.85, 0.9, 1.0)
moon_obj = bpy.data.objects.new("Moon", moon)
moon_obj.rotation_euler = (math.radians(50), math.radians(-20), math.radians(-35))
bpy.context.collection.objects.link(moon_obj)

cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
bpy.context.collection.objects.link(cam)
cam.location = (-1.1, -3.6, 1.15)
cam.rotation_euler = (Vector((0.15, 0, 1.0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.lens = 45
scene.camera = cam

scene.render.filepath = os.path.join(OUT_RENDER, "kaito.webp")
bpy.ops.render.render(write_still=True)
print("KAITO DONE")
