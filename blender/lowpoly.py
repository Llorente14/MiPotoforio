"""Shared helpers for the procedural low-poly models (import from a model script)."""
import math
import os

import bpy
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_MODEL = os.path.join(ROOT, "public", "models")
OUT_RENDER = os.path.join(ROOT, "public", "renders")
for d in (OUT_MODEL, OUT_RENDER):
    os.makedirs(d, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)

parts = []  # objects created since the last join()


def mat(name, hex_color, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    c = int(hex_color[1:], 16)
    bsdf.inputs["Base Color"].default_value = ((c >> 16) / 255, (c >> 8 & 255) / 255, (c & 255) / 255, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return m


def keep(obj, material):
    obj.data.materials.append(material)
    parts.append(obj)
    return obj


def cur():
    return bpy.context.active_object


def _aim(obj, direction):
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector(direction).to_track_quat("Z", "Y")


def limb(a, b, r, material, verts=8):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=(b - a).length, location=(a + b) / 2)
    _aim(cur(), b - a)
    return keep(cur(), material)


def box(a, b, w, h, material):
    """Box spanning a->b with width w (sideways) and height h (up)."""
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(a + b) / 2)
    o = cur()
    o.scale = (w, h, (b - a).length)
    _aim(o, b - a)
    return keep(o, material)


def ball(p, r, material, scale=(1, 1, 1), sub=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r, location=p)
    cur().scale = scale
    return keep(cur(), material)


def spike(p, direction, r, length, material):
    d = Vector(direction).normalized()
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=r, radius2=0, depth=length, location=Vector(p) + d * length / 2)
    _aim(cur(), d)
    return keep(cur(), material)


def join(name):
    """Join every object made since the last join into one flat-shaded mesh."""
    bpy.ops.object.select_all(action="DESELECT")
    for o in parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    # bake transforms first, otherwise the joined node inherits the first part's scale/rotation
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()
    o = cur()
    o.name = o.data.name = name
    for p in o.data.polygons:
        p.use_smooth = False
    parts.clear()
    return o


def export_and_render(name, cam_loc, target, lens=45, res=(1200, 900)):
    """Write public/models/<name>.glb (Draco) and a transparent public/renders/<name>.webp."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_MODEL, name + ".glb"), export_format="GLB",
                              export_apply=True, export_yup=True, export_draco_mesh_compression_enable=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.view_settings.view_transform = "Standard"
    s = scene.render.image_settings
    s.file_format, s.color_mode, s.quality = "WEBP", "RGBA", 85

    world = bpy.data.worlds.new("Sky")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.55, 0.6, 0.7, 1)
    bg.inputs["Strength"].default_value = 0.35
    scene.world = world
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3.5
    sun.rotation_euler = (math.radians(50), math.radians(15), math.radians(30))
    bpy.context.collection.objects.link(sun)

    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    bpy.context.collection.objects.link(cam)
    cam.location = cam_loc
    cam.rotation_euler = (Vector(target) - Vector(cam_loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    scene.camera = cam
    scene.render.filepath = os.path.join(OUT_RENDER, name + ".webp")
    bpy.ops.render.render(write_still=True)
    print(name.upper(), "DONE")
