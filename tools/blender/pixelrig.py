"""Reusable pixel-art render rig for Idle Kingdom sprite pilots.

Design targets, taken from the existing Gemini sprites (raw_hero_knight_v3.png):
  - exactly 3 flat tones per surface, palette-exact (no gradients, no specular)
  - thick pure-black outline
  - hard pixel edges (no anti-aliasing)
  - alpha background (the magenta key step becomes unnecessary)
"""

import bpy
import bmesh
import math
import os

OUTLINE_RGBA = (0.02, 0.02, 0.05, 1.0)


def out_dir():
    """Render output lives next to this file, so nothing here hardcodes a
    machine path. tools/blender/out/ is gitignored."""
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(d, exist_ok=True)
    return d


# --------------------------------------------------------------------------
# scene / rig
# --------------------------------------------------------------------------

def get_scene(name="PixelPilot"):
    return bpy.data.scenes.get(name) or bpy.data.scenes.new(name)


def setup_render(scn, res=96, ortho=4.0):
    scn.render.engine = 'BLENDER_EEVEE'
    scn.render.resolution_x = res
    scn.render.resolution_y = res
    scn.render.resolution_percentage = 100
    scn.render.filter_size = 0.01
    scn.render.film_transparent = True
    scn.render.image_settings.file_format = 'PNG'
    scn.render.image_settings.color_mode = 'RGBA'
    scn.view_settings.view_transform = 'Standard'
    scn.view_settings.look = 'None'
    # Sampling must be EXACT, not averaged. The tone ramp is a hard step, so any
    # sample-to-sample jitter turns into speckle instead of a clean band. One
    # sample plus no stochastic shadows/raytracing makes every pixel deterministic.
    try:
        ee = scn.eevee
        ee.taa_render_samples = 1
        ee.use_shadows = False
        ee.use_raytracing = False
        ee.use_fast_gi = False
    except Exception as e:
        print("eevee cfg:", e)
    if scn.camera:
        scn.camera.data.ortho_scale = ortho
    return scn.render.resolution_x


SPRITE_PX = 0.0390625   # world units per rendered pixel, shared by ALL character sprites


def sprite_cam(scn, res, target_z, rx_deg=87):
    """Camera for a character sprite, locked to SPRITE_PX.

    Every character must render at the same world-units-per-pixel or figures come
    out at inconsistent sizes relative to each other and to the battle backdrop.
    Choose the CELL RESOLUTION to fit the character, never the ortho scale --
    ortho is derived. A bigger cell buys room (for a raised weapon, say) without
    changing how large the figure renders.
    """
    scn.render.resolution_x = res
    scn.render.resolution_y = res
    return place_cam(scn, target=(0, 0, target_z), rx_deg=rx_deg, rz_deg=0,
                     dist=20, ortho=SPRITE_PX * res)


def place_cam(scn, target, rx_deg, rz_deg, dist=20.0, ortho=None):
    """Aim the ortho camera at `target` from elevation/azimuth given in degrees.
    rx=90 is dead level (character sprites); rx=60 is a game-isometric down-angle
    (buildings). Same call = same angle on every asset, forever."""
    cam = scn.camera
    rx, rz = math.radians(rx_deg), math.radians(rz_deg)
    d = (-math.sin(rx) * math.sin(rz), math.sin(rx) * math.cos(rz), -math.cos(rx))
    cam.rotation_euler = (rx, 0, rz)
    cam.location = tuple(target[i] - d[i] * dist for i in range(3))
    if ortho:
        cam.data.ortho_scale = ortho
    return cam


def pixel_size(scn):
    """World units covered by one rendered pixel."""
    return scn.camera.data.ortho_scale / scn.render.resolution_x


def clear_scene(scn, keep=("PixelCam", "KeySun")):
    for ob in list(scn.collection.objects):
        if ob.name not in keep:
            scn.collection.objects.unlink(ob)
            if ob.users == 0:
                bpy.data.objects.remove(ob)


# --------------------------------------------------------------------------
# materials
# --------------------------------------------------------------------------

def hexcol(h):
    """'#7fa8c9' -> linear RGBA. sRGB -> linear so the Standard view transform
    round-trips the palette exactly."""
    h = h.lstrip('#')
    srgb = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]

    def to_lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return tuple(to_lin(c) for c in srgb) + (1.0,)


def toon_mat(name, shadow, mid, light, bands=(0.30, 0.66)):
    """3-tone flat material. Diffuse -> Shader-to-RGB -> constant ColorRamp
    whose three stops ARE the palette colours -> Emission.

    Result: no gradient can appear, the sprite can only ever contain the three
    colours passed in, and the tone break follows real geometry.
    """
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    diff = nt.nodes.new('ShaderNodeBsdfDiffuse')
    diff.inputs['Color'].default_value = (1, 1, 1, 1)
    diff.location = (-600, 0)

    s2rgb = nt.nodes.new('ShaderNodeShaderToRGB')
    s2rgb.location = (-400, 0)

    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.location = (-220, 0)
    ramp.color_ramp.interpolation = 'CONSTANT'
    e = ramp.color_ramp.elements
    e[0].position = 0.0
    e[0].color = hexcol(shadow)
    e[1].position = bands[0]
    e[1].color = hexcol(mid)
    e3 = e.new(bands[1])
    e3.color = hexcol(light)

    emit = nt.nodes.new('ShaderNodeEmission')
    emit.location = (60, 0)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (260, 0)

    nt.links.new(diff.outputs['BSDF'], s2rgb.inputs['Shader'])
    nt.links.new(s2rgb.outputs['Color'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], emit.inputs['Color'])
    nt.links.new(emit.outputs['Emission'], out.inputs['Surface'])
    return mat


def flat_mat(name, color):
    """Single-tone emission (for eyes, gems, pure-black gaps)."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    emit = nt.nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value = hexcol(color) if isinstance(color, str) else color
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (200, 0)
    nt.links.new(emit.outputs['Emission'], out.inputs['Surface'])
    return mat


def outline_mat():
    mat = bpy.data.materials.get("OUTLINE")
    if mat is None:
        mat = flat_mat("OUTLINE", OUTLINE_RGBA)
    mat.use_backface_culling = True   # the half of the inverted hull facing us is dropped
    return mat


# --------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------

def add_box(scn, name, loc, size, mat, rot=(0, 0, 0), bevel=0.0):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.scale = size
    ob.rotation_euler = rot
    me.materials.append(mat)
    scn.collection.objects.link(ob)
    if bevel:
        b = ob.modifiers.new("bevel", 'BEVEL')
        b.width = bevel
        b.segments = 1
    return ob


def add_cyl(scn, name, loc, radius, depth, mat, rot=(0, 0, 0), verts=8, scale=(1, 1, 1)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts,
                          radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    ob.scale = scale
    me.materials.append(mat)
    scn.collection.objects.link(ob)
    return ob


def add_cone(scn, name, loc, r1, r2, depth, mat, rot=(0, 0, 0), verts=8):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts,
                          radius1=r1, radius2=r2, depth=depth)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    me.materials.append(mat)
    scn.collection.objects.link(ob)
    return ob


def add_sphere(scn, name, loc, radius, mat, scale=(1, 1, 1), segs=10, rings=6):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=radius)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.scale = scale
    me.materials.append(mat)
    scn.collection.objects.link(ob)
    return ob


def add_prism(scn, name, pts_xz, depth, mat, loc=(0, 0, 0), rot=(0, 0, 0)):
    """Extrude a 2D outline (list of (x, z) points, counter-clockwise) along Y.
    This is the workhorse for shields, blades, roofs, banners -- anything whose
    silhouette matters more than its volume."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts = [bm.verts.new((x, -depth / 2.0, z)) for (x, z) in pts_xz]
    face = bm.faces.new(verts)
    bmesh.ops.translate(bm, verts=verts, vec=(0, 0, 0))
    r = bmesh.ops.extrude_face_region(bm, geom=[face])
    ev = [v for v in r['geom'] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=ev, vec=(0, depth, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    me.materials.append(mat)
    scn.collection.objects.link(ob)
    return ob


def add_ridged(scn, name, loc, size, mat, splay=11.0, bevel=0.0):
    """Two half-boxes splayed into a shallow convex ridge down the middle.

    A flat box shows ONE tone, which is what makes blocky armour read dead. This
    gives the form a left plane and a right plane, so the 3-tone ramp lands two
    different tones on one piece the way hand-drawn plate does.
    Returns both halves.
    """
    w, d, h = size
    out = []
    for s in (-1, 1):
        ob = add_box(scn, name, (loc[0] + s * w * 0.25, loc[1], loc[2]),
                     (w * 0.56, d, h), mat,
                     rot=(0, 0, math.radians(s * splay)), bevel=bevel)
        out.append(ob)
    return out


def make_root(scn, name, rot=(0, 0, 0), loc=(0, 0, 0)):
    """Empty that parts parent to, so an assembly moves and turns as one.
    `rot` is in DEGREES. Used for whole-figure facing and for sub-assemblies
    such as a sword or a shield that are easier to model axis-aligned."""
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.3
    e.location = loc
    e.rotation_euler = tuple(math.radians(a) for a in rot)
    scn.collection.objects.link(e)
    return e


def parent_all(root, objs):
    """Children keep their local coordinates and INHERIT the root transform
    (identity parent-inverse). Model the part upright at the origin, let the
    root place and angle it."""
    from mathutils import Matrix
    for ob in objs:
        ob.parent = root
        ob.matrix_parent_inverse = Matrix.Identity(4)


def outline(ob, px, width_px=1.3):
    """Inverted-hull outline sized in RENDERED PIXELS, not world units.
    That is what keeps outline weight identical across every sprite."""
    mats = ob.data.materials
    om = outline_mat()
    if om.name not in [m.name for m in mats if m]:
        mats.append(om)
    idx = [i for i, m in enumerate(mats) if m and m.name == "OUTLINE"][0]
    mod = ob.modifiers.new("outline", 'SOLIDIFY')
    mod.thickness = px * width_px
    mod.offset = 1.0
    mod.use_flip_normals = True
    mod.use_rim = False
    mod.material_offset = idx
    mod.material_offset_rim = idx
    return mod


def outline_all(scn, px, width_px=1.3, skip=()):
    for ob in scn.collection.objects:
        if ob.type == 'MESH' and ob.name not in skip:
            if not any(m.type == 'SOLIDIFY' for m in ob.modifiers):
                outline(ob, px, width_px)


# --------------------------------------------------------------------------
# render
# --------------------------------------------------------------------------

def find(scn, *bases):
    """Objects whose name matches any base, ignoring Blender's .001 suffixes."""
    want = set(bases)
    return [o for o in scn.collection.objects if o.name.split('.')[0] in want]


def reparent_keep(root, objs):
    """Parent WITHOUT moving anything: the child keeps its current world
    position and only follows the root from now on.

    This is the opposite of parent_all(), which makes a child's coordinates
    local to the root. Animation needs this form -- an arm is modelled in place
    and then handed a pivot to swing around.
    """
    for ob in objs:
        ob.parent = root
        ob.matrix_parent_inverse = root.matrix_world.inverted()


def render_to(scn, path):
    scn.render.filepath = path
    bpy.ops.render.render(write_still=True, scene=scn.name)
    return path


def render_strip(scn, poses, out_path, cell=None):
    """Render one frame per pose and lay them out as a horizontal sprite sheet.

    `poses` is a list of callables. Each one sets up a frame and is called with
    no arguments; frame 0 should be the rest pose. Returns the strip path.
    """
    import numpy as np
    import tempfile
    cell = cell or scn.render.resolution_x
    frames = []
    tmp = tempfile.mkdtemp(prefix="pixelrig_")
    for i, pose in enumerate(poses):
        pose()
        bpy.context.view_layer.update()
        p = os.path.join(tmp, "f%02d.png" % i)
        render_to(scn, p)
        img = bpy.data.images.load(p, check_existing=False)
        w, h = img.size
        buf = np.empty(w * h * 4, dtype=np.float32)
        img.pixels.foreach_get(buf)
        bpy.data.images.remove(img)
        frames.append(buf.reshape(h, w, 4))

    h = frames[0].shape[0]
    sheet = np.zeros((h, cell * len(frames), 4), dtype=np.float32)
    for i, f in enumerate(frames):
        sheet[:, i * cell:i * cell + f.shape[1]] = f
    out = bpy.data.images.new("strip", sheet.shape[1], sheet.shape[0], alpha=True)
    out.pixels.foreach_set(sheet.ravel())
    out.file_format = 'PNG'
    out.filepath_raw = out_path
    out.save()
    bpy.data.images.remove(out)
    return out_path


def upscale_nearest(src_path, dst_path, factor=10, bg=None):
    """Nearest-neighbour upscale so the pixel grid stays hard when viewed large.
    bg: optional (r,g,b) sRGB tuple to composite over (e.g. magenta for
    side-by-side comparison against the existing keyed sprites)."""
    import numpy as np
    img = bpy.data.images.load(src_path, check_existing=False)
    w, h = img.size
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    a = buf.reshape(h, w, 4)

    if bg is not None:
        bgl = np.array(hexcol(bg)[:3] if isinstance(bg, str) else bg, dtype=np.float32)
        alpha = a[:, :, 3:4]
        a = np.concatenate([a[:, :, :3] * alpha + bgl * (1 - alpha),
                            np.ones_like(alpha)], axis=2)

    big = np.repeat(np.repeat(a, factor, axis=0), factor, axis=1)
    out = bpy.data.images.new("upscaled", w * factor, h * factor, alpha=True)
    out.pixels.foreach_set(big.ravel())
    out.file_format = 'PNG'
    out.filepath_raw = dst_path
    out.save()
    bpy.data.images.remove(img)
    bpy.data.images.remove(out)
    return dst_path
