"""Bounded Bellback forms study from the accepted r004 construction packet.

Run in a separate factory-startup Blender process. No rig, UV, export or engine import.
"""
from __future__ import annotations
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

HERE = Path(__file__).resolve()
OUT = HERE.parent.parent
ASSET = OUT.parents[2]
SPEC = ASSET / "inputs/references/r004_construction/construction_spec.json"
GEOMETRY = ASSET / "inputs/references/r003_manual/construction_geometry.json"
G = json.loads(SPEC.read_text())
P = json.loads(GEOMETRY.read_text())
assert hashlib.sha256(SPEC.read_bytes()).hexdigest() == "fe748c1a1229f9b6c85a8296137753d21d354ca6791f62dd7bab474d57eb4a13"
assert hashlib.sha256(GEOMETRY.read_bytes()).hexdigest() == G["source_geometry_sha256"]
assert not (OUT / "Bellback_forms_r001.blend").exists(), "Preserve prior source; use a new revision"
OUT.mkdir(parents=True, exist_ok=True)
RENDERS = OUT / "renders"
RENDERS.mkdir(exist_ok=True)
scene = bpy.context.scene
initial = {"filepath": bpy.data.filepath, "objects": [o.name for o in scene.objects], "version": bpy.app.version_string}
assert not bpy.data.filepath, "Only an isolated unsaved factory scene may be initialized"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1

def collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c

SOURCE = collection("SOURCE_MASSES_EDITABLE")
FORMS = collection("BELLBACK_FORMS")
HELPERS = collection("REVIEW_HELPERS")
RIGID = FORMS

def material(name, color, roughness=.65, metallic=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return m

CLAY = material("Review_clay", (.36, .34, .30), .78)
BARK = material("ID_bark_warm", (.18, .095, .047), .82)
FACE = material("ID_bark_face", (.29, .19, .09), .8)
MOSS = material("ID_moss", (.20, .28, .07), .9)
BELL = material("ID_weathered_bronze", (.36, .22, .075), .43, .55)
TRIM = material("ID_bell_edges", (.48, .32, .115), .45, .5)
EYE = material("Eye_dark_hazel", (.055, .037, .018), .32)
PUPIL = material("Pupil", (.007, .004, .002), .3)

def mesh(name, verts, faces, part, mat=CLAY, coll=FORMS):
    data = bpy.data.meshes.new(name + "_mesh")
    data.from_pydata(verts, [], faces)
    data.update()
    ob = bpy.data.objects.new(name, data)
    coll.objects.link(ob)
    ob["wc_part_id"] = part
    ob["asset_id"] = "wc_vn_bellback"
    ob["stage"] = "forms_candidate_not_topology_or_rig"
    ob.data.materials.append(mat)
    for poly in data.polygons:
        poly.use_smooth = True
    return ob

def ellipsoid(name, center, radii, part, mat=BARK, coll=SOURCE, shape=1.0):
    verts = []
    faces = []
    n, rings = 40, 22
    for j in range(rings + 1):
        v = -math.pi / 2 + math.pi * j / rings
        for i in range(n):
            a = math.tau * i / n
            x, y, z = math.cos(v) * math.cos(a), math.cos(v) * math.sin(a), math.sin(v)
            if shape != 1:
                x = math.copysign(abs(x) ** shape, x)
                y = math.copysign(abs(y) ** shape, y)
                z = math.copysign(abs(z) ** shape, z)
            verts.append(tuple(center[k] + radii[k] * (x, y, z)[k] for k in range(3)))
    for j in range(rings):
        for i in range(n):
            a = j * n + i; b = j * n + (i + 1) % n
            faces.append((a, b, b + n, a + n))
    return mesh(name, verts, faces, part, mat, coll)

def tube(name, points, widths, part, mat=BARK, coll=SOURCE, sides=16, flatten=1):
    verts, faces = [], []
    for j, point in enumerate(points):
        p = Vector(point)
        tangent = Vector(points[min(j + 1, len(points) - 1)]) - Vector(points[max(j - 1, 0)])
        tangent.normalize()
        axis = tangent.cross(Vector((0, 1, 0)))
        if axis.length < .001:
            axis = tangent.cross(Vector((1, 0, 0)))
        axis.normalize(); other = tangent.cross(axis).normalized()
        for i in range(sides):
            angle = math.tau * i / sides
            v = p + widths[j] * (math.cos(angle) * axis + flatten * math.sin(angle) * other)
            verts.append(tuple(v))
    faces.append(tuple(reversed(range(sides))))
    for j in range(len(points) - 1):
        for i in range(sides):
            a = j * sides + i; b = j * sides + (i + 1) % sides
            faces.append((a, b, b + sides, a + sides))
    faces.append(tuple((len(points) - 1) * sides + i for i in range(sides)))
    return mesh(name, verts, faces, part, mat, coll)

def loft_body():
    # Deliberate longitudinal cage: broad shoulders, tapering rump and a low weight-bearing belly.
    profile = [(-.9,.02,.75,.035),(-.84,.34,.75,.23),(-.67,.62,.76,.34),(-.42,.74,.78,.375),
               (-.08,.795,.77,.398),(.24,.79,.765,.39),(.48,.70,.76,.35),(.67,.52,.77,.29),
               (.81,.33,.82,.245),(.91,.17,.87,.17),(.94,.025,.89,.04)]
    verts, faces = [], []
    n = 48
    for y, width, z, height in profile:
        for i in range(n):
            a = math.tau * i / n
            xx = math.copysign(abs(math.cos(a)) ** .88, math.cos(a))
            zz = math.sin(a)
            if zz < 0: zz = -abs(zz) ** .65
            verts.append((width * xx, y, z + height * zz))
    for j in range(len(profile) - 1):
        for i in range(n):
            a = j*n+i; b = j*n+(i+1)%n
            faces.append((a,a+n,b+n,b))
    faces += [tuple(reversed(range(n))), tuple((len(profile)-1)*n+i for i in range(n))]
    return mesh("Body_anatomical_cage", verts, faces, "body_core", BARK, SOURCE)

loft_body()
ellipsoid("Neck_transition", (0,.72,.88), (.29,.30,.24), "body_core")
ellipsoid("Head_cage", (0,.9,.95), (.325,.245,.228), "head_shell", FACE, shape=.9)
ellipsoid("Forehead_plane", (0,.985,1.072), (.265,.137,.105), "head_shell", FACE, shape=.87)
ellipsoid("Cheek_left", (-.20,1.007,.902), (.122,.118,.131), "head_shell", FACE)
ellipsoid("Cheek_right", (.20,1.007,.902), (.122,.118,.131), "head_shell", FACE)
ellipsoid("Muzzle_foundation", (0,1.062,.877), (.233,.084,.098), "head_shell", FACE, shape=.82)
ellipsoid("Jaw_chin", (0,1.016,.795), (.213,.118,.062), "lower_jaw", FACE, shape=.86)
ellipsoid("Nose_bridge", (0,1.102,.958), (.087,.045,.085), "head_shell", FACE, shape=.8)

def leg_joints(leg):
    root = Vector(leg["joint"]) / 1000
    foot = Vector(leg["foot"]) / 1000
    ankle = foot + Vector((0,0,.420 * leg["paw_scale"]))
    dy, dz = ankle.y - root.y, ankle.z - root.z
    distance = math.hypot(dy,dz)
    upper, lower = [x/1000 for x in leg["segment_lengths"]]
    along = (upper*upper-lower*lower+distance*distance)/(2*distance)
    away = math.sqrt(max(0,upper*upper-along*along))
    bend = leg["bend_sign"]
    knee = Vector((root.x,root.y+along*dy/distance+bend*away*(-dz)/distance,
                   root.z+along*dz/distance+bend*away*dy/distance))
    return root,knee,ankle

joint_records = []
for leg in G["legs"]:
    name, scale = leg["id"], leg["paw_scale"]
    root,knee,ankle = leg_joints(leg)
    front = name.startswith("F")
    tube(name+"_limb_continuity", [root,knee,ankle,(ankle.x,ankle.y-.015,.24*scale)],
         [.19 if front else .22,.155 if front else .17,.125,.16],
         "foreleg_pair" if front else "hindleg_pair", sides=24, flatten=.93)
    ellipsoid(name+"_shoulder_transition", tuple(root), (.235,.265,.25) if front else (.26,.25,.25),
              "foreleg_pair" if front else "hindleg_pair")
    foot = Vector(leg["foot"])/1000
    # Four broad toes emerge from one coherent paw, each with a flattened actual floor plane.
    ellipsoid(name+"_paw_bridge", (foot.x,foot.y-.040*scale,.155*scale),
              (.218*scale,.205*scale,.155*scale), "paw_pairs", shape=.66)
    ellipsoid(name+"_wrist_slope", (foot.x,foot.y-.055*scale,.30*scale),
              (.16*scale,.145*scale,.122*scale), "paw_pairs", shape=.87)
    for digit in P["paw"]["toes"]:
        pos = (foot.x+digit["center_x"]*.001*scale,foot.y+digit["center_y"]*.001*scale,.085*scale)
        toe = ellipsoid(name+"_toe_"+digit["id"],pos,(.043*scale,.070*scale,.085*scale),"paw_pairs",shape=.72)
        toe["digit_id"] = name+"_"+digit["id"]
    joint_records.append({"leg":name,"root":list(root),"knee":list(knee),"ankle":list(ankle),"paw_scale":scale})

tube("Tail_root_stub", [(0,-.82,.8),(0,-.95,.77),(0,-1.06,.76)], [.074,.061,.032], "body_core", sides=20)
tube("Shoulder_branch_right", [tuple(v/1000 for v in G["branch"][k]) for k in ("base","elbow","tip")],
     [.05,.035,.020], "shoulder_branch_right", sides=20)

# Preserve the complete editable shape vocabulary, and make one continuous sculpt surface.
bpy.ops.object.select_all(action="DESELECT")
for ob in list(SOURCE.objects):
    copied = ob.copy(); copied.data = ob.data.copy(); FORMS.objects.link(copied); copied.select_set(True)
bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
bpy.ops.object.join()
organic = bpy.context.object
organic.name = "Bellback_organic_continuous_forms"
organic["wc_part_id"] = "body_head_legs_paws_continuous"
remesh = organic.modifiers.new("Continuous_sculpt_union", "REMESH")
remesh.mode = "VOXEL"; remesh.voxel_size = .008; remesh.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier=remesh.name)
smooth = organic.modifiers.new("Bounded_form_relaxation", "SMOOTH")
smooth.factor = .45; smooth.iterations = 3
bpy.ops.object.modifier_apply(modifier=smooth.name)
organic.data.materials.clear(); organic.data.materials.append(BARK)
for vertex in organic.data.vertices:
    if vertex.co.z < .012: vertex.co.z = 0

# Cut actual eye sockets before inserting small eyes; integrate broad upper/lower lids with the head.
for sign in (-1,1):
    cutter=ellipsoid("socket_cutter",(sign*.218,1.070,1.034),(.077,.075,.068),"construction_helper",coll=FORMS)
    bpy.context.view_layer.objects.active=organic
    modifier=organic.modifiers.new("Eye_socket_concavity", "BOOLEAN"); modifier.operation="DIFFERENCE";modifier.object=cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    ellipsoid("Eye_"+str(sign),(sign*.218,1.068,1.034),(.047,.044,.046),"eye_pair",EYE,FORMS)
    ellipsoid("Pupil_"+str(sign),(sign*.217,1.109,1.035),(.019,.009,.027),"eye_pair",PUPIL,FORMS)
    lid_points=[]
    for i in range(19):
        a=math.pi*i/18
        lid_points.append((sign*.218+.072*math.cos(a),1.083+.005*math.sin(a),1.030+.062*math.sin(a)))
    tube("Brow_lid_"+str(sign),lid_points,[.018+.009*math.sin(math.pi*i/18) for i in range(19)],
         "head_shell",FACE,FORMS,sides=12,flatten=.85)
    # Broad brow root continues into the temple instead of floating as a symbolic eyebrow.
    tube("Temple_brow_root_"+str(sign),[(sign*.05,1.10,1.095),(sign*.14,1.10,1.118),
         (sign*.26,1.033,1.105),(sign*.313,.96,1.01)], [.016,.026,.039,.047],"root_armature_surface",BARK,FORMS)
    # Nostrils are inset dark openings on the blunt shared muzzle plane.
    ellipsoid("Nostril_"+str(sign),(sign*.046,1.143,.945),(.020,.006,.013),"head_shell",PUPIL,FORMS)

mouth=[]
for i in range(25):
    x=-.20+.40*i/24
    mouth.append((x,1.128-.22*x*x,.824+.11*abs(x)))
tube("Closed_mouth_crease",mouth,[.0055]*len(mouth),"lower_jaw",PUPIL,FORMS,sides=8)

# Broad bark forms follow shoulder and limb flow; no stochastic surface noise or decorative scatter.
for sign in (-1,1):
    for index, offset in enumerate((-.13,0,.13)):
        tube("Fore_bark_root_"+str(sign)+"_"+str(index),
             [(sign*(.42+offset),.53,1.03),(sign*(.55+offset),.64,.85),
              (sign*(.58+offset*.75),.69,.64),(sign*(.55+offset*.8),.60,.40),
              (sign*(.55+offset*.75),.68,.22)], [.030,.042,.043,.031,.009],
             "root_armature_surface",FACE,FORMS,sides=12,flatten=.6)
    for index, offset in enumerate((-.10,.04)):
        tube("Hind_bark_root_"+str(sign)+"_"+str(index),
             [(sign*(.47+offset),-.51,.98),(sign*(.63+offset),-.56,.82),
              (sign*(.60+offset*.7),-.72,.61),(sign*(.49+offset),-.55,.26)],
             [.027,.045,.038,.012],"root_armature_surface",FACE,FORMS,sides=12,flatten=.65)

SOURCE.hide_render=True
SOURCE.hide_viewport=True

def lathe(name, profile, part, mat, ratio=.92, n=96):
    verts,faces=[],[]
    for radius,z in profile:
        for i in range(n):
            a=math.tau*i/n
            verts.append((ratio*radius*math.cos(a),radius*math.sin(a),z))
    for j in range(len(profile)):
        nxt=(j+1)%len(profile)
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n
            faces.append((a,b,nxt*n+(i+1)%n,nxt*n+i))
    return mesh(name,verts,faces,part,mat,RIGID)

outer=[(.720,1.320),(.665,1.500),(.535,1.750),(.350,2.000),(.200,2.120),(.080,2.200),(0,2.200)]
inner=[(0,2.160),(.10,2.120),(.255,2.000),(.430,1.750),(.560,1.500),(.625,1.320)]
bell=lathe("Dorsal_bell_hollow_shell",outer+inner,"dorsal_bell_shell",BELL)
bevel=bell.modifiers.new("Soft_cast_edges","BEVEL");bevel.width=.012;bevel.segments=3
bpy.context.view_layer.objects.active=bell;bpy.ops.object.modifier_apply(modifier=bevel.name)
lathe("Bell_mouth_rim",[(.720,1.32),(.726,1.335),(.710,1.355),(.619,1.355),(.619,1.32)],"bell_trim",TRIM)
lathe("Bell_crown_collar",[(.16,2.142),(.164,2.155),(.142,2.164),(.130,2.152)],"bell_trim",TRIM)

def box(name,low,high,part,mat=BARK,bevel=.012):
    verts=[(x,y,z) for z in (low[2],high[2]) for y in (low[1],high[1]) for x in (low[0],high[0])]
    faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
    ob=mesh(name,verts,faces,part,mat,RIGID)
    if bevel > 0:
        mod=ob.modifiers.new("Construction_edges","BEVEL");mod.width=bevel;mod.segments=3
        bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob

lathe("Open_carrier_ring",[(.720,1.27),(.720,1.32),(.670,1.32),(.670,1.27)],"bell_carrier_frame",BARK)
box("Carrier_spine",(-.045,-.720,1.270),(.045,.720,1.320),"bell_carrier_frame")
for y in (-.450,.450):
    box("Carrier_crossbeam_"+str(y),(-.50,y-.045,1.27),(.50,y+.045,1.32),"bell_carrier_frame")
    verts,faces=[],[]
    nx,ny=20,6
    for top in (False,True):
        for j in range(ny+1):
            yy=y-.09+.18*j/ny
            for i in range(nx+1):
                xx=-.35+.7*i/nx
                zz=1.27 if top else .77+.4*math.sqrt(max(0,1-(xx/.8)**2-(yy/.9)**2))-.008
                verts.append((xx,yy,zz))
    plane=(nx+1)*(ny+1)
    for j in range(ny):
        for i in range(nx):
            a=j*(nx+1)+i;b=a+1;c=a+nx+2;d=a+nx+1
            faces.extend([(a,d,c,b),(a+plane,b+plane,c+plane,d+plane)])
    boundary=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+list(range(ny*(nx+1)+nx-1,ny*(nx+1)-1,-1))+[j*(nx+1) for j in range(ny-1,0,-1)]
    for i,a in enumerate(boundary):
        b=boundary[(i+1)%len(boundary)];faces.append((a,b,b+plane,a+plane))
    mesh("Conforming_saddle_"+str(y),verts,faces,"saddle_pad_pair",FACE,RIGID)

tube("Crown_fixed_hanger",[(0,0,2.16),(0,0,2.02)],[.018,.018],"clapper_crown_hanger",TRIM,RIGID)
tube("Clapper_rod",[(0,0,2.02),(0,0,1.66)],[.008,.008],"bell_clapper",BELL,RIGID)
ellipsoid("Clapper_striker",(0,0,1.66),(.055,.055,.055),"bell_clapper",BELL,RIGID)

# Six restrained moss masses clarify the creature material and silhouette without hiding the face or joints.
for name,center,radii in [
    ("Shoulder_R",(.52,.55,1.07),(.22,.23,.085)),("Shoulder_L",(-.52,.55,1.07),(.22,.23,.085)),
    ("Haunch_R",(.55,-.44,1.04),(.22,.25,.08)),("Haunch_L",(-.55,-.44,1.04),(.22,.25,.08)),
    ("Brow",(0,.90,1.16),(.23,.16,.048)),("Rump",(0,-.78,.97),(.25,.13,.065))]:
    ellipsoid("Moss_"+name,center,radii,"moss_clumps",MOSS,FORMS,shape=.78)

root=bpy.data.objects.new("Bellback_root_meter_+Y",None);FORMS.objects.link(root)
root["wc_part_id"]="root";root["authoring_unit"]="meter";root["source_forward"]="+Y"
for ob in list(FORMS.objects):
    if ob!=root:ob.parent=root

# Fixed neutral lighting and mathematically declared cameras; material-ID render is not textured acceptance.
scene.render.engine="CYCLES";scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=960;scene.render.resolution_y=960;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG";scene.render.film_transparent=False
scene.view_settings.view_transform="AgX";scene.view_settings.look="AgX - Medium High Contrast"
world=bpy.data.worlds.new("Neutral_review_world");world.use_nodes=True;scene.world=world
world.node_tree.nodes["Background"].inputs["Color"].default_value=(.32,.34,.37,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.45
for name,loc,power,size in [("Key",(3,4,5),650,4),("Fill",(-4,2,3),450,4),("Back",(0,-4,4),650,3)]:
    data=bpy.data.lights.new(name,"AREA");data.energy=power;data.shape="DISK";data.size=size
    ob=bpy.data.objects.new(name,data);HELPERS.objects.link(ob);ob.location=loc
    ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat("-Z","Y").to_euler()
floor_mat=material("Review_floor",(.30,.30,.285),.85)
floor=box("Review_floor",(-200,-200,-.04),(200,200,-.012),"review_helper",floor_mat,0)
FORMS.objects.unlink(floor);HELPERS.objects.link(floor)
cam_data=bpy.data.cameras.new("Review_camera");camera=bpy.data.objects.new("Review_camera",cam_data);HELPERS.objects.link(camera)
scene.camera=camera;cam_data.type="ORTHO";cam_data.ortho_scale=2.75;cam_data.lens=55
cam_data.dof.use_dof=False
camera.location=(4,6,3.2)
camera.rotation_euler=(Vector((0,0,1.05))-camera.location).to_track_quat("-Z","Y").to_euler()
for area in bpy.context.screen.areas:
    if area.type == "VIEW_3D":
        area.spaces.active.region_3d.view_location=(0,0,1.05)
        area.spaces.active.region_3d.view_distance=4.2
        area.spaces.active.region_3d.view_rotation=camera.rotation_euler.to_quaternion()
views=[("front_clay",(0,6,1.1),(0,0,1.1)),("right_clay",(6,0,1.1),(0,0,1.1)),
       ("back_clay",(0,-6,1.1),(0,0,1.1)),("left_clay",(-6,0,1.1),(0,0,1.1)),
       ("threequarter_clay",(4,6,3.2),(0,0,1.05)),("threequarter_ids",(4,6,3.2),(0,0,1.05))]

def bounds(objects):
    points=[ob.matrix_world@Vector(v) for ob in objects if ob.type=="MESH" for v in ob.bound_box]
    return {"min":[min(p[i] for p in points) for i in range(3)],"max":[max(p[i] for p in points) for i in range(3)]}

bpy.context.view_layer.update()
model_objects=[o for o in FORMS.objects if o.type=="MESH"]
source_path=OUT/"Bellback_forms_r001.blend"
scene.view_layers[0].material_override=None
bpy.ops.wm.save_as_mainfile(filepath=str(source_path),check_existing=False)
source_hash=hashlib.sha256(source_path.read_bytes()).hexdigest()
records=[]
for name,loc,target in views:
    camera.location=loc;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    scene.view_layers[0].material_override=CLAY if name.endswith("clay") else None
    scene.render.filepath=str(RENDERS/(name+".png"));bpy.ops.render.render(write_still=True)
    records.append({"view":name,"location":list(loc),"target":list(target),"orthographic_scale":cam_data.ortho_scale,"image":name+".png"})

audit={"stage":"forms_candidate_not_approved","blender_version":bpy.app.version_string,"initial_isolated_scene":initial,
       "source":source_path.name,"source_sha256":source_hash,"construction_source_sha256":hashlib.sha256(SPEC.read_bytes()).hexdigest(),
       "source_geometry_sha256":hashlib.sha256(GEOMETRY.read_bytes()).hexdigest(),
       "method":"Custom longitudinal anatomy cage, joint-constrained swept limbs, four-toe masses, voxel-fused continuous sculpt, actual concave eye sockets, related muzzle/brow/jaw forms; separately lathed hollow bell and open carrier with conforming saddles. Preserved editable masses.",
       "bounds_m":bounds(model_objects),"joint_points_m":joint_records,
       "parts":[{"name":o.name,"wc_part_id":o.get("wc_part_id"),"vertices":len(o.data.vertices),"triangles":sum(len(p.vertices)-2 for p in o.data.polygons),"bounds_m":bounds([o])} for o in model_objects],
       "render_settings":{"engine":scene.render.engine,"samples":scene.cycles.samples,"resolution":[960,960],"view_transform":scene.view_settings.view_transform,"look":scene.view_settings.look},
       "views":records,"limitations":["No human modeled-forms acceptance","Not production topology/UV/material/rig/animation/export","No Unreal import or performance acceptance","Raster aesthetic artwork is not registered to these orthographic cameras"]}
(OUT/"model_audit.json").write_text(json.dumps(audit,indent=2)+"\n")
print("BELLBACK_FORMS_BUILT",source_path,source_hash,flush=True)
