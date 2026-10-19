"""Cel-shaded Kaito Kid (fan art), head to mid-thigh, holding his calling card between two fingers.

Run from the repo root (the face decal is rasterised from its vector source first):
    node scripts/textures.mjs
    blender -b --factory-startup -P blender/kaito.py

The card faces are blender/textures/card-{front,back}.png, cropped from Axel's reference photo.

Outputs public/models/kaito.glb (nodes "Kaito" and "Card"; animate the card) and public/renders/kaito.webp.
Faces -Y, z up. Built in working units, then normalised to 1.0 tall with the origin at the centre of
the thigh cut. Hair flows round the skull and is clamped inside a 1.55x head ellipsoid.
"""
import math
import os
import sys

sys.path.append(os.path.dirname(__file__))
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from toon import CACHE, ball, cur, decal, export_and_render, join, keep, limb, loft, mat, parts, poly, strand  # noqa: E402

TEXTURES = os.path.join(os.path.dirname(__file__), "textures")

SUIT = mat("Suit", "#f4f2ec", rough=0.5)
SUIT_SHADE = mat("SuitSeam", "#dcdad3")
LINING = mat("Lining", "#e3e7f0")
SHIRT = mat("Shirt", "#2f56a8")
TIE = mat("Tie", "#c8323a")
BAND = mat("HatBand", "#2f56a8")
SKIN = mat("Skin", "#d8b594")  # sawo matang
SKIN["lift"] = 0.16  # renders lift it toward white a little
HAIR = mat("Hair", "#2e2420")
GLOVE = mat("Glove", "#fbfbf8", rough=0.6)
SILVER = mat("Silver", "#cfd4dc", rough=0.25, metal=1.0)
CLOVER = mat("Clover", "#2f8a57")

FRONT_Y = -0.118  # jacket front surface at chest height
Z_CUT = 0.71  # mid-thigh: 45% of the way from hip (0.9) to knee (0.48)
HEAD_C = Vector((0.0, -0.012, 1.66))  # head ellipsoid before the anime scale-up
HEAD_R = Vector((0.105, 0.1, 0.125))
HAIR_BOUND = 1.55  # room for the locks to flow and kick out, still no strand sticking straight out


def thick(obj, t):
    """Give a flat panel real thickness (applied at join)."""
    obj.modifiers.new("Thickness", "SOLIDIFY").thickness = t
    return obj


def n(v):
    return Vector(v).normalized()


# =================================================================== body (static)
# ---- trousers and hips, cut flat at mid-thigh
loft("Hips", [((0, 0.012, 0.84), 0.15, 0.1), ((0, 0.012, 0.92), 0.158, 0.106)], SUIT, n=32)
for sx in (-1, 1):
    loft("Thigh", [((0.078 * sx, 0.012, Z_CUT), 0.074, 0.074), ((0.078 * sx, 0.012, 0.79), 0.08, 0.08),
                   ((0.074 * sx, 0.012, 0.87), 0.084, 0.084)], SUIT, n=28, caps=(True, True), sub=1)

# ---- jacket: chest, waist and a hem that covers the hips
loft("Jacket", [
    ((0, 0.014, 0.82), 0.168, 0.114),
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
for sx in (-1, 1):  # notched lapels with thickness
    pts = [(0.074 * sx, FRONT_Y + 0.002, 1.448), (0.122 * sx, FRONT_Y + 0.006, 1.392),
           (0.104 * sx, FRONT_Y - 0.004, 1.372), (0.112 * sx, FRONT_Y - 0.002, 1.35),
           (0.07 * sx, FRONT_Y - 0.01, 1.27), (0.006 * sx, FRONT_Y - 0.012, 1.16),
           (0.054 * sx, FRONT_Y - 0.004, 1.43)]
    thick(poly("Lapel", pts, [tuple(range(7)) if sx > 0 else tuple(reversed(range(7)))], SUIT, smooth=False), 0.006)
for z in (1.12, 1.05):  # jacket buttons
    ball((0.0, FRONT_Y + 0.004, z), 0.011, SUIT_SHADE, scale=(1, 0.5, 1), segs=16)
thick(poly("Pocket", [(0.07, FRONT_Y + 0.004, 1.29), (0.14, FRONT_Y + 0.012, 1.292), (0.14, FRONT_Y + 0.012, 1.28),
                      (0.07, FRONT_Y + 0.004, 1.278)], [(0, 1, 2, 3)], SUIT_SHADE, smooth=False), 0.003)
# hip pocket flap on his left, where that hand rests
thick(poly("HipPocket", [(0.07, -0.116, 0.97), (0.16, -0.088, 0.975), (0.162, -0.088, 0.945), (0.07, -0.117, 0.94)],
           [(0, 1, 2, 3)], SUIT, smooth=False), 0.006)

# ---- cape: on the shoulders, falling past the thigh cut and cut flat with it;
#      his right side is swept back so the card arm reads clearly
nu, nv = 24, 18
cv = []
for j in range(nv + 1):
    v = j / nv
    for i in range(nu + 1):
        u = i / nu
        theta = math.radians(-70 + 152 * u)  # starts further back on his right (swept back)
        r = 0.2 + 0.24 * v + (0.12 * v * v if u > 0.5 else 0.02 * v)
        flutter = 0.03 * math.sin(u * 11 + v * 4) * v
        z = 1.445 - 0.86 * v + 0.1 * v * v * u
        cv.append((math.sin(theta) * r + 0.1 * v * v * (u - 0.3), math.cos(theta) * r * 0.75 + 0.03 + flutter,
                   max(z, Z_CUT)))
cf = [(j * (nu + 1) + i, j * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i)
      for j in range(nv) for i in range(nu)]
cape = poly("Cape", cv, cf, SUIT)
cape.data.materials.append(LINING)
sol = cape.modifiers.new("Thickness", "SOLIDIFY")
sol.thickness, sol.material_offset = 0.01, 1
cape.modifiers.new("Smooth", "SUBSURF").levels = 1

# ---- neck and an anime head with a painted face
loft("Neck", [((0, 0.0, 1.43), 0.044, 0.044), ((0, -0.006, 1.545), 0.04, 0.04)], SKIN, n=20)
head_start = len(parts)  # everything from here to the monocle is the head group
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


# ---- hair: flowing clumps that follow the skull, clamped inside the head volume
def on_head(phi, theta, k):
    """Point on the head ellipsoid scaled by k. phi: 0 = front (-Y), +90 = his left; theta from the crown."""
    p, t = math.radians(phi), math.radians(theta)
    return (HEAD_C.x + HEAD_R.x * k * math.sin(t) * math.sin(p),
            HEAD_C.y - HEAD_R.y * k * math.sin(t) * math.cos(p),
            HEAD_C.z + HEAD_R.z * k * math.cos(t))


hair_start = len(parts)
ball((0.0, 0.008, 1.71), 0.1, HAIR, scale=(1.02, 1.05, 0.64), segs=32)  # mass under the hat
# locks round the sides and back: each S-curves away from the face, swells, then kicks out at the tip.
# Lengths, sweep and kick vary lock to lock so the silhouette is ragged and spiky, never a bowl line.
for i, phi in enumerate(range(36, 332, 16)):
    rnd = ((i * 37) % 11) / 10  # deterministic 0..1 jitter
    sign = 1 if phi < 180 else -1  # sweep toward the back
    sweep = (6 + 10 * rnd) * sign
    tip_theta = 94 + 12 * rnd  # short: the locks end around the ears
    kick = 1.2 + 0.12 * ((i * 53) % 7) / 6  # the tip flicks outward, visible from the front
    pts = [on_head(phi, 48, 1.02), on_head(phi + sweep * 0.3, 66, 1.1), on_head(phi + sweep * 0.7, 82, 1.16),
           on_head(phi + sweep, tip_theta, kick)]
    strand(pts, 0.031 - 0.008 * rnd, HAIR, taper=(1.0, 0.0))
for i, phi in enumerate(range(52, 316, 24)):  # a shorter inner layer for volume between the long locks
    sign = 1 if phi < 180 else -1
    strand([on_head(phi, 54, 1.02), on_head(phi + 6 * sign, 80, 1.14), on_head(phi + 12 * sign, 88 + 5 * (i % 3), 1.22)],
           0.025, HAIR, taper=(1.0, 0.0))
# fringe: clumps parted off-centre, sweeping hard toward his left, ragged lengths, tips curling off the brow
for phi, tip, sw in ((-52, 90, 18), (-38, 86, 28), (-24, 90, 32), (-10, 85, 34), (4, 90, 34), (18, 84, 32),
                     (32, 88, 28), (46, 84, 22), (58, 90, 16)):
    strand([on_head(phi * 0.5, 36, 1.03), on_head(phi * 0.8 + sw * 0.25, 56, 1.09), on_head(phi + sw * 0.65, 72, 1.12),
            on_head(phi + sw, tip, 1.2)], 0.034, HAIR, taper=(1.0, 0.0))
for phi, tip, sw in ((-40, 85, 8), (-27, 89, 10), (-14, 84, 12), (-1, 88, 12), (12, 83, 12), (25, 88, 10), (38, 84, 8)):
    # a second, shorter layer of bangs filling the gaps so the fringe reads dense, as in the figure
    strand([on_head(phi * 0.5, 40, 1.03), on_head(phi * 0.8 + sw * 0.25, 58, 1.08), on_head(phi + sw * 0.65, 70, 1.1),
            on_head(phi + sw, tip, 1.14)], 0.032, HAIR, taper=(1.0, 0.0))
for sx in (-1, 1):  # sideburns in front of the ears
    strand([on_head(78 * sx, 62, 1.04), on_head(82 * sx, 84, 1.07), on_head(84 * sx, 100, 1.08)], 0.015, HAIR,
           taper=(1.0, 0.0))

# validation: clamp every hair vertex radially back inside the bounding ellipsoid if it pokes out
bound = Vector((HEAD_R.x * HAIR_BOUND, HEAD_R.y * HAIR_BOUND, HEAD_R.z * HAIR_BOUND))
hair_clamped = hair_total = hair_tucked = 0
HAT_BRIM_Z, HAT_AXIS, HAT_INNER_R = 1.712, (0.01, 0.004), 0.078  # brim height, crown axis, a safe inner radius
bpy.context.view_layer.update()
for o in parts[hair_start:]:
    mw, mwi = o.matrix_world.copy(), o.matrix_world.inverted()
    for v in o.data.vertices:
        d = (mw @ v.co) - HEAD_C
        q = math.sqrt((d.x / bound.x) ** 2 + (d.y / bound.y) ** 2 + (d.z / bound.z) ** 2)
        hair_total += 1
        if q > 1.0:
            v.co = mwi @ (HEAD_C + d / q)
            hair_clamped += 1
        # above the brim the hair must stay inside the crown, or it shows through the hat and its band
        w = mw @ v.co
        # the brim plane tilts with the hat: higher at the front, lower on his left
        brim_z = HAT_BRIM_Z - (w.y - HAT_AXIS[1]) * 0.105 - (w.x - HAT_AXIS[0]) * 0.122
        if w.z > brim_z + 0.004:
            r = Vector((w.x - HAT_AXIS[0], w.y - HAT_AXIS[1], 0))
            if r.length > HAT_INNER_R:
                w.xy = Vector(HAT_AXIS) + r.xy * (HAT_INNER_R / r.length)
                v.co = mwi @ w
                hair_tucked += 1

# ---- top hat (white, blue band), tilted
hat = []
loft("Crown", [((0, 0, 0.0), 0.11, 0.102), ((0, 0, 0.11), 0.104, 0.097), ((0, 0, 0.205), 0.11, 0.103),
               ((0, 0, 0.214), 0.1, 0.094)], SUIT, n=40, sub=1)
hat.append(cur())
loft("Band", [((0, 0, 0.002), 0.113, 0.105), ((0, 0, 0.05), 0.109, 0.101)], BAND, n=48, sub=0)  # crisp: subdivision would shrink it into the crown
hat.append(cur())
loft("Brim", [((0, 0, -0.009), 0.196, 0.183), ((0.0, 0, 0.0), 0.204, 0.19), ((0, 0, 0.004), 0.198, 0.185),
              ((0, 0, -0.002), 0.112, 0.104)], SUIT, n=56, caps=(True, False), sub=1)
hat.append(cur())
pivot = bpy.data.objects.new("HatPivot", None)
bpy.context.collection.objects.link(pivot)
pivot.location = (0.01, 0.004, 1.712)  # sits low, the brim just above the eyes
pivot.rotation_euler = (math.radians(-6), math.radians(7), math.radians(3))
pivot.scale = (1.1, 1.1, 1.06)  # wide enough to cover the crown of the head
for h in hat:
    h.parent = pivot

# ---- monocle over his right eye, cord to the lapel
bpy.ops.mesh.primitive_torus_add(major_radius=0.031, minor_radius=0.004, major_segments=40, minor_segments=10,
                                 location=(-0.042, -0.118, 1.645), rotation=(math.radians(90), 0, 0))
keep(cur(), SILVER)
strand([(-0.068, -0.12, 1.625), (-0.098, -0.132, 1.55), (-0.094, -0.136, 1.46), (-0.08, -0.13, 1.395)], 0.0018,
       SILVER, taper=(1, 1))
for ox, oz in ((0, 0.012), (-0.011, 0.0), (0.011, 0.0)):  # clover charm
    ball((-0.08 + ox, -0.134, 1.375 + oz), 0.0075, CLOVER, segs=14)
strand([(-0.08, -0.134, 1.375), (-0.084, -0.136, 1.356)], 0.0018, CLOVER, taper=(1, 1))

# anime proportions and a 10 degree turn toward the card: scale and rotate the head group about the neck top
bpy.context.view_layer.update()
grow = (Matrix.Translation((0.0, -0.01, 1.508)) @ Matrix.Rotation(math.radians(-10), 4, "Z")
        @ Matrix.Scale(1.12, 4) @ Matrix.Translation((0.0, 0.01, -1.53)))
for o in [o for o in parts[head_start:] if o.parent is None] + [pivot]:
    o.matrix_world = grow @ o.matrix_world

# ---- his left arm: relaxed, hand slipped into the hip pocket
sL, eL, wL = (0.195, 0.0, 1.38), (0.272, 0.04, 1.16), (0.13, -0.09, 0.97)
limb(sL, eL, 0.062, SUIT, r2=0.055, verts=24)
ball(eL, 0.055, SUIT, segs=24)
limb(eL, wL, 0.054, SUIT, r2=0.047, verts=24)
limb(Vector(wL) + (Vector(eL) - Vector(wL)).normalized() * 0.03, wL, 0.049, SHIRT, verts=20)  # shirt cuff

# ---- his right arm: raised, gloved hand beside the face holding the card between two fingers (screen left)
sR, eR, wR = (-0.195, 0.0, 1.38), (-0.33, -0.13, 1.25), (-0.25, -0.2, 1.53)
limb(sR, eR, 0.062, SUIT, r2=0.055, verts=24)
ball(eR, 0.055, SUIT, segs=24)
limb(eR, wR, 0.054, SUIT, r2=0.047, verts=24)
cuff = loft("CuffR", [((0, 0, 0), 0.049, 0.049), ((0, 0, 0.024), 0.049, 0.049)], SHIRT, n=20, sub=0)
cuff.location = wR
cuff.rotation_mode = "QUATERNION"
cuff.rotation_quaternion = (Vector(wR) - Vector(eR)).to_track_quat("Z", "Y")
palm = (-0.245, -0.215, 1.585)
ball(palm, 0.04, GLOVE, scale=(0.85, 0.6, 1.1), segs=24)
# index and middle fingers extended, pinching the card; three knuckles each
for dx, length in ((-0.012, 0.075), (0.012, 0.082)):
    strand([(palm[0] + dx, palm[1] - 0.01, palm[2] + 0.034), (palm[0] + dx * 1.2, palm[1] - 0.026, palm[2] + 0.058),
            (palm[0] + dx * 1.4 - 0.008, palm[1] - 0.042, palm[2] + 0.034 + length * 0.7),
            (palm[0] + dx * 1.6 - 0.016, palm[1] - 0.056, palm[2] + 0.034 + length)], 0.0125, GLOVE, taper=(1, 0.75))
for dx in (0.03, 0.042):  # ring and little fingers curled in
    strand([(palm[0] + dx * 0.6, palm[1] - 0.012, palm[2] + 0.03), (palm[0] + dx, palm[1] - 0.045, palm[2] + 0.04),
            (palm[0] + dx * 0.8, palm[1] - 0.04, palm[2] + 0.005)], 0.0115, GLOVE, taper=(1, 0.8))
strand([(palm[0] + 0.03, palm[1], palm[2] - 0.02), (palm[0] + 0.05, palm[1] - 0.04, palm[2] + 0.0),
        (palm[0] + 0.045, palm[1] - 0.06, palm[2] + 0.03)], 0.0125, GLOVE, taper=(1, 0.8))  # thumb
for k in range(3):  # glove stitching on the back of the hand
    strand([(palm[0] - 0.012 + k * 0.012, palm[1] + 0.022, palm[2] - 0.012),
            (palm[0] - 0.012 + k * 0.012, palm[1] + 0.024, palm[2] + 0.022)], 0.0016, SUIT_SHADE, taper=(1, 1))

kaito = join("Kaito", smooth_angle=None)
bpy.data.objects.remove(pivot)

# ---- the calling card: Axel's reference photo of the ace of clubs and its harlequin back, two faces 1 mm apart
card_parts = []
for side, flip in (("front", 0.0), ("back", math.pi)):
    bpy.ops.mesh.primitive_plane_add(size=1, rotation=(math.radians(90), 0, flip))
    o = cur()
    o.scale = (0.092, 0.15, 1)  # the photo's own proportions, about 1.5x a real card so it reads beside the face
    o.location.y = -0.0006 if flip == 0 else 0.0006
    o.data.materials.append(mat("Card" + side.title(), "#ffffff", rough=0.4,
                                image=os.path.join(TEXTURES, f"card-{side}.png")))
    card_parts.append(o)
bpy.ops.object.select_all(action="DESELECT")
for o in card_parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = card_parts[0]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.join()
card = cur()
card.name = card.data.name = "Card"
card.location = (-0.285, -0.262, 1.715)
card.rotation_euler = (math.radians(-6), math.radians(14), math.radians(-18))

# ---- normalise: 1.0 tall, origin at the centre of the thigh cut
bpy.context.view_layer.update()
H = max((kaito.matrix_world @ Vector(c)).z for c in kaito.bound_box) - Z_CUT
norm = Matrix.Scale(1 / H, 4) @ Matrix.Translation((0, 0, -Z_CUT))
for o in (kaito, card):
    o.matrix_world = norm @ o.matrix_world
bpy.ops.object.select_all(action="DESELECT")
kaito.select_set(True)
bpy.context.view_layer.objects.active = kaito
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.select_all(action="DESELECT")
card.select_set(True)
bpy.context.view_layer.objects.active = card
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)  # keep the origin at the card centre

print("SUMMARY vertices:", sum(len(o.data.vertices) for o in (kaito, card)))
print(f"SUMMARY hair: {hair_clamped} of {hair_total} vertices clamped into the {HAIR_BOUND}x head ellipsoid, "
      f"{hair_tucked} tucked inside the hat")

export_and_render("kaito", cam_loc=(-0.36, -1.75, 0.62), target=(-0.05, 0.0, 0.5), lens=55, res=(1000, 1250),
                  outline=0.003, sun_rot=(48, 0, -35), skip_outline=("Card",))
