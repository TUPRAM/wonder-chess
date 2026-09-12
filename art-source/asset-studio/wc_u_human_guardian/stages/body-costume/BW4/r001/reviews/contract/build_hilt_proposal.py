"""Build an unselected, isolated equipment decision from read-only canonical measurements."""
import bpy
import bmesh
import hashlib
import json
import math
from mathutils import Vector, Matrix
from pathlib import Path

OUT=Path(__file__).resolve().parent
data=json.loads((OUT/'actual_hilt_and_bind.json').read_text())
parts={p['identified_part']:p for p in data['sword_components']}
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=1
scene['status']='PROPOSED_HILT_NOT_SELECTED_NOT_CANONICAL'
scene['canonical_source_sha256']=data['source_sha256']

def material(name,color,metal=0,rough=.4):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metal
    bs.inputs['Roughness'].default_value=rough
    return m

steel=material('Review steel',(.34,.39,.43),.6,.28)
grip=material('Review grip',(.15,.11,.075),0,.7)
ink=material('Annotation',(.035,.045,.06),0,.75)
gold=material('Review guard',(.35,.26,.12),.55,.35)

handle=parts['handle']
center=Vector((sum(v[0] for v in handle['world_vertices_m'])/16,sum(v[1] for v in handle['world_vertices_m'])/16,0))
oldmin=handle['bounds_world_min_m'][2]
oldmax=handle['bounds_world_max_m'][2]
guardmin=parts['guard']['bounds_world_min_m'][2]
newmin=guardmin-.110
newmax=oldmax
oldwidth=handle['bounds_dimensions_m'][0]
proposed=[]
for x,y,z in handle['world_vertices_m']:
    proposed.append([center.x+(x-center.x)*.030/oldwidth,
                     center.y+(y-center.y)*.026/oldwidth,
                     newmin+(z-oldmin)/(oldmax-oldmin)*(newmax-newmin)])

def mesh_object(name,vertices,faces,mat,parent):
    mesh=bpy.data.meshes.new(name+'_MESH')
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(mesh);bm.free()
    obj=bpy.data.objects.new(name,mesh)
    scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    obj.parent=parent
    obj['canonical_coordinates_preserved']=name.startswith('Actual') or 'Handle' not in name
    obj['production_status']='UNSELECTED_PROPOSAL' if name.startswith('Proposal') else 'UNCHANGED_CANONICAL_COPY'
    return obj

objects={}
for variant,column in [('Actual',-.19),('Proposal',.19)]:
    holder=bpy.data.objects.new(variant+'_DisplayOffset_ONLY',None)
    scene.collection.objects.link(holder)
    holder.location=(column-center.x,-center.y,-oldmin)
    holder['purpose']='Presentation translation only; mesh vertex coordinates remain in canonical bind world space.'
    objects[variant]={}
    for name,p in parts.items():
        verts=proposed if variant=='Proposal' and name=='handle' else p['world_vertices_m']
        obj=mesh_object(variant+'_'+name.title(),verts,p['faces'],grip if name=='handle' else gold if name=='guard' else steel,holder)
        objects[variant][name]=obj

def text(body,location,size=.012,align='CENTER'):
    curve=bpy.data.curves.new('Label','FONT')
    curve.body=body;curve.align_x=align;curve.size=size;curve.space_line=1.13
    obj=bpy.data.objects.new('Label_'+body[:24],curve)
    scene.collection.objects.link(obj)
    obj.rotation_euler=(math.pi/2,0,0)
    obj.location=location
    curve.materials.append(ink)
    return obj

def line(name,points):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=.00042;curve.bevel_resolution=0
    spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
    for p,co in zip(spline.points,points):p.co=(*co,1)
    obj=bpy.data.objects.new(name,curve);scene.collection.objects.link(obj);curve.materials.append(ink)

text('ADA | ACTUAL HILT AND SEPARATE FIT PROPOSAL',(0,-.12,.366),.019)
text('UNSELECTED equipment decision | same scale | blade and guard unchanged',(0,-.12,.339),.0105)
text('ACTUAL SOURCE',(-.19,-.12,.291),.014)
text('PROPOSAL - NOT SELECTED',(.19,-.12,.291),.014)
text('77.3 x 77.3 mm section\n164.9 mm exposed grip\n209.3 mm total handle',(-.19,-.12,-.040),.012)
text('30 x 26 mm section\n110 mm exposed grip\n154.4 mm total handle',(.19,-.12,-.040),.012)
text('No separate pommel in the source. Upper overlap retained inside the guard.',(0,-.12,-.101),.010)
for x,lower in [(-.19,0),(.19,newmin-oldmin)]:
    xpos=x+.137
    top=guardmin-oldmin
    line('Exposed grip dimension',[(xpos,-.06,lower),(xpos,-.06,top)])
    for height in [lower,top]:line('Dimension tick',[(xpos-.006,-.06,height),(xpos+.006,-.06,height)])

camd=bpy.data.cameras.new('Hilt comparison camera')
cam=bpy.data.objects.new('Hilt comparison camera',camd);scene.collection.objects.link(cam)
cam.location=(0,-3,.135)
cam.rotation_euler=(Vector((0,0,.135))-cam.location).to_track_quat('-Z','Y').to_euler()
camd.type='ORTHO';camd.ortho_scale=.82;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world=bpy.data.worlds.new('Neutral review world');scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.75,.75,.75,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.65
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast'
for name,location,power,size in [('Key',(-.5,-.6,.8),80,.5),('Fill',(.6,-.4,.3),45,.45)]:
    ld=bpy.data.lights.new(name,'AREA');lo=bpy.data.objects.new(name,ld);scene.collection.objects.link(lo)
    lo.location=location;lo.rotation_euler=(Vector((0,0,.15))-lo.location).to_track_quat('-Z','Y').to_euler()
    ld.energy=power;ld.shape='DISK';ld.size=size

# Store reusable mesh in original bind/world coordinates, with display transforms separate.
bind=Matrix(data['hand_r_rest_world'])
record={'status':'UNSELECTED_HILT_PROPOSAL_REQUIRES_USER_DECISION','canonical_source_sha256':data['source_sha256'],
        'actual':handle,'proposed':{'world_vertices_m':proposed,'faces':handle['faces'],
        'hand_bind_vertices_m':[list(bind.inverted()@Vector(v)) for v in proposed],
        'section_across_corners_mm':[30,26],'usable_exposed_length_mm':110,
        'overall_length_mm':(newmax-newmin)*1000,'upper_overlap_in_guard_mm':(newmax-guardmin)*1000,
        'axis_world':[0,0,1],'center_xy_world_m':list(center)[:2]},
        'guard_and_blade_geometry_unchanged':True,'pommel_added':False,
        'hand_r_bind_world':data['hand_r_rest_world'],
        'display_offsets':{k:list(next(iter(v.values())).parent.location) for k,v in objects.items()},
        'notes':['No hand fit has been tested. This is an explicit equipment proposal, not an accepted target.',
                 'The handle is a closed 8-sided prism with two end caps; proposed section is anisotropic.',
                 'The exposed interval ends at the lowest guard surface; full clearance still needs actual glove testing.']}
(OUT/'hilt_proposal_geometry.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
scene.render.filepath=str(OUT/'actual_vs_unselected_hilt_proposal.png')
target=OUT/'ada_bw4_hilt_proposal_UNSELECTED.blend'
assert not target.exists(),target
bpy.ops.wm.save_as_mainfile(filepath=str(target))
bpy.ops.render.render(write_still=True)
assert hashlib.sha256(Path(data['source']).read_bytes()).hexdigest()==data['source_sha256']
(OUT/'hilt_proposal_manifest.json').write_text(json.dumps({'status':'UNSELECTED_PROPOSAL',
  'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [target,OUT/'actual_vs_unselected_hilt_proposal.png',OUT/'hilt_proposal_geometry.json']},
  'canonical_source_preserved':True,'hand_fit_tested':False,'human_approval':False},indent=2)+'\n',encoding='utf-8')
print('BW4_UNSELECTED_HILT_PROPOSAL_SAVED',target)
