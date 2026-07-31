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


def _srgb_lerp(a, b, t):
    """Blend two '#rrggbb' strings in sRGB and return a hex string."""
    a, b = a.lstrip('#'), b.lstrip('#')
    out = []
    for i in (0, 2, 4):
        va, vb = int(a[i:i + 2], 16), int(b[i:i + 2], 16)
        out.append(int(round(va + (vb - va) * t)))
    return '#%02x%02x%02x' % tuple(out)


def toon_ramp(shadow, mid, light, steps):
    """Expand three palette anchors into `steps` shades, shadow to light."""
    if steps <= 3:
        return [shadow, mid, light][:steps]
    out = []
    for i in range(steps):
        t = i / (steps - 1)
        out.append(_srgb_lerp(shadow, mid, t / 0.5) if t <= 0.5
                   else _srgb_lerp(mid, light, (t - 0.5) / 0.5))
    return out


def toon_mat(name, shadow, mid, light, bands=(0.30, 0.66), steps=3, top=0.82, lo=0.0,
             positions=None):
    """Hard-stepped material. Diffuse -> Shader-to-RGB -> constant ColorRamp
    whose stops ARE the palette colours -> Emission. No gradient can appear;
    a surface is one of the stop colours or it is outline.

    `steps` is how many shades the ramp holds. THREE is right for a character
    sprite, where curved parts turn through all three across a few pixels and
    flatness reads as punch. It is wrong for a backdrop: large surfaces then
    hold one tone each and the whole scene reads as cut paper. Pass steps=5 or
    6 for terrain, stone and foliage, which keeps the banding but gives slopes
    somewhere to go.

    `lo` and `top` are the shading values the steps are spread BETWEEN, and
    raising the count alone is useless without setting them. A scene's incoming
    light only occupies part of the 0..1 range, so steps outside that window are
    never reached and the extra shades cost render time and change nothing.

    `positions` overrides them with explicit stop positions, which is what a
    scene with HARD SHADOWS actually needs. Shadowed and lit surfaces cluster at
    two ends with nothing between, so evenly spaced stops strand half of
    themselves in the empty middle and the render comes back looking two-tone no
    matter how many stops there are. Put a group of stops in each cluster.

    Measure before choosing either. Render with the ramp swapped for a linear
    black-to-white one and read the pixel values back, remembering that the
    saved image is sRGB-encoded while the ramp reads linear.
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
    if steps == 3:
        e[0].position, e[0].color = 0.0, hexcol(shadow)
        e[1].position, e[1].color = bands[0], hexcol(mid)
        e.new(bands[1]).color = hexcol(light)
    else:
        # Stop 0 sits at zero and catches everything below `lo`; the remaining
        # stops divide lo..top evenly. Spacing them from lo + step instead leaves
        # the darkest shade covering an extra band's width, which swallows the
        # fill light's contribution and puts every cast shadow back on one colour.
        shades = toon_ramp(shadow, mid, light, steps)
        if positions:
            pos = list(positions)[:steps]
        else:
            step = (top - lo) / (steps - 1)
            pos = [0.0] + [lo + (k - 1) * step for k in range(1, steps)]
        e[0].position, e[0].color = pos[0], hexcol(shades[0])
        e[1].position, e[1].color = pos[1], hexcol(shades[1])
        for k in range(2, steps):
            e.new(pos[k]).color = hexcol(shades[k])

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

def enable_hard_shadows(scn):
    """Deterministic cast shadows, safe with the hard tone ramp.

    setup_render() turns shadows off because the DEFAULT settings are stochastic
    and a hard ramp turns any jitter into speckle. Three settings make them exact
    instead: no sun angular size, no shadow filter radius, one ray and one step.
    `shadow_filter_radius` is the one that matters -- left at its default of 1.0
    it covers every lit surface in shadow acne.

    Worth it on backdrops, where cast shadows are most of what makes flat ground
    read as having depth. Character sprites stay unshadowed.
    """
    sun = scn.collection.objects.get("KeySun")
    if sun:
        sun.data.shadow_soft_size = 0.0
        sun.data.angle = 0.0
        sun.data.shadow_filter_radius = 0.0
        sun.data.shadow_maximum_resolution = 0.00005
    ee = scn.eevee
    ee.use_shadows = True
    ee.shadow_ray_count = 1
    ee.shadow_step_count = 1
    ee.taa_render_samples = 1
    return ee


def add_terrain(scn, name, x0, x1, y0, y1, cell, hfunc, mat):
    """Flat-shaded ground grid displaced by hfunc(x, y).

    A flat plane has ONE normal, so the tone ramp can only ever give it one
    colour, which is what makes a rendered ground look dead beside a character
    built from curved parts. Gentle relief varies the normal per face and the
    ramp then lays down all three tones as terrain texture.
    """
    nx = max(1, int((x1 - x0) / cell))
    ny = max(1, int((y1 - y0) / cell))
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    grid = [[bm.verts.new((x0 + i * (x1 - x0) / nx,
                           y0 + j * (y1 - y0) / ny,
                           hfunc(x0 + i * (x1 - x0) / nx, y0 + j * (y1 - y0) / ny)))
             for j in range(ny + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(ny):
            bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    me.materials.append(mat)
    scn.collection.objects.link(ob)
    return ob


def tile_top(scn, x0, x1, y0, y1, z, bu, bv, mats, gap=0.06, rise=0.09,
             clip=None, stagger=True, name="block", snap_u=None, snap_v=None):
    """Lay staggered flagstones over a horizontal surface.

    Masonry cannot be faked with colour at this resolution. A single box reads as
    poured concrete because it is one flat tone. Real blocks, each a touch taller
    than its neighbour, let the hard shadows cut the mortar lines for free, and
    cycling two or three stone tones stops the courses looking printed.

    Give the base slab underneath a DARKER material so the gaps read as mortar.

    **Pass snap_u and snap_v.** They are the world size of ONE rendered pixel
    along each axis, and they quantise both the block pitch and the tiling
    origin onto the pixel grid. Without them the mortar gap is a fraction of a
    pixel wide and its phase drifts across the surface, so the lines fade in and
    out in broad patches -- which looks like a texture bug and is really moire.
    For a horizontal surface, snap_u is the pixel size and snap_v is the pixel
    size divided by cos(camera elevation), since depth foreshortens.
    """
    def q(v, step):
        return v if not step else max(step, round(v / step) * step)

    bu, bv = q(bu, snap_u), q(bv, snap_v)
    gap_u = q(gap, snap_u)
    gap_v = q(gap, snap_v)
    if snap_u:                                  # world x=0 sits on a pixel edge
        x0 = round(x0 / snap_u) * snap_u
    if snap_v:
        y0 = round(y0 / snap_v) * snap_v
    obs = []
    ny = max(1, int(round((y1 - y0) / bv)))
    nx = max(1, int(round((x1 - x0) / bu))) + 1
    for j in range(ny):
        y = y0 + (j + 0.5) * bv
        if y > y1:
            continue
        off = bu * 0.5 if (stagger and j % 2) else 0.0
        for i in range(nx):
            x = x0 + (i + 0.5) * bu + off
            if x > x1 or x < x0:
                continue
            if clip and not clip(x, y):
                continue
            h = rise * (1.0 + 0.55 * ((i * 5 + j * 3) % 3))
            m = mats[(i * 7 + j * 13) % len(mats)]
            obs.append(add_box(scn, name, (x, y, z + h * 0.5),
                               (bu - gap_u, bv - gap_v, h), m))
    return obs


def tile_face_y(scn, x0, x1, z0, z1, y, bu, bv, mats, gap=0.06, out=0.09,
                stagger=True, name="brick"):
    """Same idea on a vertical face looking down -Y: courses of blocks that stand
    proud of the wall behind them, so each course shadows the one below."""
    obs = []
    nz = max(1, int(round((z1 - z0) / bv)))
    nx = max(1, int(round((x1 - x0) / bu))) + 1
    for j in range(nz):
        z = z0 + (j + 0.5) * (z1 - z0) / nz
        off = bu * 0.5 if (stagger and j % 2) else 0.0
        for i in range(nx):
            x = x0 + (i + 0.5) * bu + off
            if x > x1 or x < x0:
                continue
            d = out * (1.0 + 0.5 * ((i * 3 + j * 7) % 3))
            m = mats[(i * 11 + j * 5) % len(mats)]
            obs.append(add_box(scn, name, (x, y - d * 0.5, z),
                               (bu - gap, d, (z1 - z0) / nz - gap), m))
    return obs


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


def two_bone_ik(shoulder, target, len_a, len_b, pole, stretch=0.0):
    """Planar two-bone solve. Returns (elbow, hand, len_a, len_b).

    Needed for a two-handed grip, which is a closed loop: both hands must stay
    ON the weapon. Turning each arm rigidly about its own shoulder does NOT keep
    the hands a fixed distance apart, because the gap between the shoulders is
    fixed while each hand's offset from its shoulder rotates. The weapon then
    floats free of the fists. The fix is to drive the weapon and let the arms
    reach for it.

    `pole` steers which way the elbow breaks; only its component perpendicular
    to the shoulder-to-target line matters, so a fully extended arm cannot be
    steered at all.

    `stretch` is the fraction the bones may lengthen to reach a target beyond
    arm's length, e.g. 0.2 for twenty percent. Without it an out-of-reach target
    is clamped, which drops the hand off the weapon it is meant to be gripping.
    Figures posed with nearly straight arms need this, because almost any motion
    then puts a hand out of reach. At sprite resolution the stretch is invisible.
    Pass the returned lengths to aim_segment so the limb actually spans the gap.
    """
    from mathutils import Vector
    S, H, p = Vector(shoulder), Vector(target), Vector(pole)
    v = H - S
    if v.length < 1e-6:
        v = Vector((0, 0, -1))
    d = v.length
    reach = len_a + len_b
    if d > reach and stretch > 0.0:
        k = min(d / reach, 1.0 + stretch)
        len_a, len_b, reach = len_a * k, len_b * k, reach * k
    d = min(max(d, abs(len_a - len_b) + 1e-4), reach - 1e-4)
    u = v.normalized()
    H = S + u * d
    cos_a = max(-1.0, min(1.0, (len_a * len_a + d * d - len_b * len_b) / (2 * len_a * d)))
    alpha = math.acos(cos_a)
    n = p - u * p.dot(u)
    if n.length < 1e-6:
        n = Vector((0, 0, 1)) - u * u.z
    if n.length < 1e-6:
        n = Vector((1, 0, 0))
    n.normalize()
    E = S + (u * math.cos(alpha) + n * math.sin(alpha)) * len_a
    return E, H, len_a, len_b


def aim_segment(ob, a, b, rest_len=None):
    """Place a Z-axis cylinder so it spans a -> b.

    With rest_len given, the cylinder is scaled along Z to span the gap exactly,
    which is what keeps a stretched limb solid instead of leaving a hole at the
    elbow.
    """
    from mathutils import Vector
    A, B = Vector(a), Vector(b)
    ob.location = (A + B) / 2.0
    ob.rotation_euler = (B - A).to_track_quat('Z', 'Y').to_euler()
    if rest_len:
        ob.scale = (ob.scale[0], ob.scale[1], (B - A).length / rest_len)


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
