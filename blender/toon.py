"""Shared helpers for the cel-shaded models (import from a model script).

Models are built from smooth primitives, lofts and tapered strands, exported as plain PBR glTF
(the site applies its own toon shading), then re-dressed with a toon shader and an inverted-hull
ink outline for the still render only.
"""
import math
import os

import bmesh
import bpy
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_MODEL = os.path.join(ROOT, "public", "models")
OUT_RENDER = os.path.join(ROOT, "public", "renders")
CACHE = os.path.join(ROOT, "blender", ".cache")
for d in (OUT_MODEL, OUT_RENDER):
    os.makedirs(d, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)

INK = "#17140f"
parts = []  # objects created since the last join()


def rgb(hex_color):
    c = int(hex_color[1:], 16)
    return ((c >> 16) / 255, (c >> 8 & 255) / 255, (c & 255) / 255)


def mat(name, hex_color, rough=0.7, metal=0.0, image=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m["toon"] = hex_color
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb(hex_color), 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if image:
        tex = m.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(image)
        m.node_tree.links.new(tex.outputs[0], bsdf.inputs["Base Color"])
        m.node_tree.links.new(tex.outputs[1], bsdf.inputs["Alpha"])
    return m


def cur():
    return bpy.context.active_object


def keep(obj, material, smooth=True):
    obj.data.materials.append(material)
    for p in obj.data.polygons:
        p.use_smooth = smooth
    parts.append(obj)
    return obj


def _aim(obj, direction):
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector(direction).to_track_quat("Z", "Y")


def subsurf(obj, levels=1):
    obj.modifiers.new("Smooth", "SUBSURF").levels = levels
    return obj


def limb(a, b, r, material, r2=None, verts=16):
    """Tapered round segment from a (radius r) to b (radius r2)."""
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r if r2 is None else r2,
                                    depth=(b - a).length, location=(a + b) / 2)
    _aim(cur(), b - a)
    return keep(cur(), material)


def ball(p, r, material, scale=(1, 1, 1), segs=24, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=segs // 2, radius=r, location=p, rotation=rot)
    cur().scale = scale
    return keep(cur(), material)


def box(a, b, w, h, material, bevel=0.0, smooth=False):
    """Box spanning a->b with width w (sideways) and height h (up), optionally bevelled."""
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(a + b) / 2)
    o = cur()
    o.scale = (w, h, (b - a).length)
    _aim(o, b - a)
    if bevel:
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        mod = o.modifiers.new("Bevel", "BEVEL")
        mod.width, mod.segments = bevel, 2
    return keep(o, material, smooth)


def spike(p, direction, r, length, material, verts=10):
    d = Vector(direction).normalized()
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=0, depth=length,
                                    location=Vector(p) + d * length / 2)
    _aim(cur(), d)
    return keep(cur(), material)


def poly(name, verts, faces, material, smooth=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    return keep(o, material, smooth)


def loft(name, rings, material, n=24, caps=(True, True), sub=1):
    """Smooth body through horizontal elliptical rings [(centre, rx, ry), ...], bottom to top."""
    verts, faces = [], []
    for c, rx, ry in rings:
        for i in range(n):
            a = math.tau * i / n
            verts.append((c[0] + rx * math.cos(a), c[1] + ry * math.sin(a), c[2]))
    for j in range(len(rings) - 1):
        for i in range(n):
            a, b = j * n + i, j * n + (i + 1) % n
            faces.append((a, b, b + n, a + n))
    if caps[0]:
        faces.append(tuple(reversed(range(n))))
    if caps[1]:
        top = (len(rings) - 1) * n
        faces.append(tuple(range(top, top + n)))
    o = poly(name, verts, faces, material)
    return subsurf(o, sub) if sub else o


def strand(points, radius, material, taper=(1.0, 0.0), res=2):
    """Tapered tube along a smooth curve through points: hair locks, cords, folds."""
    cu = bpy.data.curves.new("Strand", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = res
    cu.resolution_u = 5  # enough for a smooth lock; the default 12 triples the polycount
    cu.use_fill_caps = True
    sp = cu.splines.new("NURBS")
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        t = i / (len(points) - 1)
        sp.points[i].co = (*p, 1)
        sp.points[i].radius = taper[0] + (taper[1] - taper[0]) * t
    sp.order_u = min(4, len(points))
    sp.use_endpoint_u = True
    o = bpy.data.objects.new("Strand", cu)
    bpy.context.collection.objects.link(o)
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target="MESH")
    return keep(cur(), material)


def decal(source, image, x_range, z_range, push=0.0012, facing=-0.2):
    """Paint a transparent texture onto the front of `source` (e.g. a face onto a head).

    Copies the faces of `source` that face the camera (normal.y < facing), pushes them out a hair,
    and maps the image straight on from the front: x_range -> u, z_range -> v.
    """
    bpy.ops.object.select_all(action="DESELECT")
    source.select_set(True)
    bpy.context.view_layer.objects.active = source
    for mod in list(source.modifiers):
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    me = source.data.copy()
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.y > facing], context="FACES")
    for v in bm.verts:
        v.co += v.normal * push
    uv = bm.loops.layers.uv.new("Decal")
    for f in bm.faces:
        for loop in f.loops:
            x, _, z = loop.vert.co
            loop[uv].uv = ((x - x_range[0]) / (x_range[1] - x_range[0]), (z - z_range[0]) / (z_range[1] - z_range[0]))
    bm.to_mesh(me)
    bm.free()
    me.materials.clear()
    o = bpy.data.objects.new("Decal", me)
    bpy.context.collection.objects.link(o)
    m = mat("Decal" + os.path.basename(image), "#ffffff", image=image)
    m["uv"] = "Decal"  # joined meshes carry several UV layers; the decal must sample its own
    tex = next(n for n in m.node_tree.nodes if n.type == "TEX_IMAGE")
    uvmap = m.node_tree.nodes.new("ShaderNodeUVMap")
    uvmap.uv_map = "Decal"
    m.node_tree.links.new(uvmap.outputs[0], tex.inputs[0])
    return keep(o, m)


def join(name, smooth_angle=None):
    """Join every object made since the last join into one mesh with baked transforms.

    smooth_angle: None keeps per-part shading; a number (degrees) re-smooths by angle.
    """
    for o in parts:
        bpy.ops.object.select_all(action="DESELECT")
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        for mod in list(o.modifiers):
            bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.select_all(action="DESELECT")
    for o in parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    # bake transforms first, otherwise the joined node inherits the first part's scale/rotation
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()
    o = cur()
    o.name = o.data.name = name
    if smooth_angle is not None:
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(smooth_angle))
    parts.clear()
    return o


# ---------------------------------------------------------------- render-only dressing

def _toon_nodes(m):
    """Diffuse -> Shader to RGB -> 3-step ramp, multiplied by the base colour (or texture)."""
    nt = m.node_tree
    tex = next((n for n in nt.nodes if n.type == "TEX_IMAGE"), None)
    for n in list(nt.nodes):
        if tex is None or n.name != tex.name:  # the UV Map node is re-made below
            nt.nodes.remove(n)
    diffuse = nt.nodes.new("ShaderNodeBsdfDiffuse")
    to_rgb = nt.nodes.new("ShaderNodeShaderToRGB")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    stops = ramp.color_ramp.elements
    stops[0].position, stops[0].color = 0.0, (0.48, 0.48, 0.62, 1)  # cool ink-blue shadow
    stops[1].position, stops[1].color = 0.22, (0.74, 0.74, 0.82, 1)
    hi = stops.new(0.5)
    hi.color = (0.92, 0.92, 0.92, 1)  # lit, but never blown out
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type, mix.blend_type = "RGBA", "MULTIPLY"
    mix.inputs["Factor"].default_value = 1
    base = rgb(m.get("toon", "#ffffff"))
    lift = m.get("lift", 0.0)  # lighten toward white without changing the exported colour
    mix.inputs[7].default_value = (*(c + (1 - c) * lift for c in base), 1)
    emit = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(diffuse.outputs[0], to_rgb.inputs[0])
    nt.links.new(to_rgb.outputs[0], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], mix.inputs[6])
    if tex:
        nt.links.new(tex.outputs[0], mix.inputs[7])
        if m.get("uv"):
            uvmap = nt.nodes.new("ShaderNodeUVMap")
            uvmap.uv_map = m["uv"]
            nt.links.new(uvmap.outputs[0], tex.inputs[0])
    nt.links.new(mix.outputs[2], emit.inputs[0])
    if tex:
        transparent = nt.nodes.new("ShaderNodeBsdfTransparent")
        mixs = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(tex.outputs[1], mixs.inputs[0])
        nt.links.new(transparent.outputs[0], mixs.inputs[1])
        nt.links.new(emit.outputs[0], mixs.inputs[2])
        nt.links.new(mixs.outputs[0], out.inputs["Surface"])
    else:
        nt.links.new(emit.outputs[0], out.inputs["Surface"])


def _outline(obj, thickness, ink):
    """Inverted hull: a pushed-out, flipped copy that only shows its back faces."""
    hull = obj.copy()
    hull.data = obj.data.copy()
    hull.name = obj.name + "Outline"
    bpy.context.collection.objects.link(hull)
    bm = bmesh.new()
    bm.from_mesh(hull.data)
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * thickness
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.to_mesh(hull.data)
    bm.free()
    hull.visible_shadow = False  # the hull must not shade the body it wraps
    hull.data.materials.clear()
    hull.data.materials.append(ink)
    for p in hull.data.polygons:
        p.material_index = 0


def export_and_render(name, cam_loc, target, lens=50, res=(1000, 1250), outline=0.006,
                      sun_rot=(48, 0, -35), skip_outline=(), sun_energy=2.7):
    """Write public/models/<name>.glb (Draco) and a cel-shaded transparent public/renders/<name>.webp."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_MODEL, name + ".glb"), export_format="GLB",
                              export_apply=True, export_yup=True, export_draco_mesh_compression_enable=True,
                              export_image_format="WEBP")

    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for m in bpy.data.materials:
        if m.use_nodes:
            _toon_nodes(m)
    ink = bpy.data.materials.new("Ink")
    ink.use_nodes = True
    ink.use_backface_culling = True
    ink.node_tree.nodes.clear()
    e = ink.node_tree.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*rgb(INK), 1)
    o = ink.node_tree.nodes.new("ShaderNodeOutputMaterial")
    ink.node_tree.links.new(e.outputs[0], o.inputs["Surface"])
    for obj in meshes:
        if obj.name not in skip_outline:
            _outline(obj, outline, ink)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.view_settings.view_transform = "Standard"
    s = scene.render.image_settings
    s.file_format, s.color_mode, s.quality = "WEBP", "RGBA", 88

    world = bpy.data.worlds.new("Flat")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (1, 1, 1, 1)
    bg.inputs["Strength"].default_value = 0.18
    scene.world = world
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = sun_energy
    sun.data.use_shadow = False  # shading by normal only: clean anime terminators, no shadow-map jaggies
    sun.rotation_euler = tuple(math.radians(a) for a in sun_rot)
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
