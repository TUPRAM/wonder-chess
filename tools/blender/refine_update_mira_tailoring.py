"""Targeted Mira mantle replacement and grip tailoring after actual render review."""
import argparse,json,math,shutil,sys
from pathlib import Path
import bmesh,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];UID='wc_u_human_priest'
sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import sha,components,invariants,render_views

def replace_mantle(mesh):
    parts=[p for p in components(mesh) if p['groups']==['spine_03'] and p['count']==20]
    assert len(parts)==2
    indices={i for p in parts for i in p['indices']}
    face=next(p for p in mesh.data.polygons if all(i in indices for i in p.vertices))
    material=mesh.data.materials[face.material_index]
    uv=sum((mesh.data.uv_layers.active.data[i].uv for i in face.loop_indices),Vector((0,0)))/len(face.loop_indices)
    bm=bmesh.new();bm.from_mesh(mesh.data);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.verts[i] for i in indices],context='VERTS')
    bm.to_mesh(mesh.data);bm.free();mesh.data.update()
    angles=[math.radians(120+i*300/24) for i in range(25)]
    # Broad drape rows follow neck, shoulder, gathered hem and rounded edge.
    rings=[(.106,.103,1.354,0),(.185,.148,1.373,0),
           (.320,.174,1.382,-.012),(.410,.188,1.240,.040),(.421,.185,1.222,.040)]
    vertices=[];faces=[];weights=[]
    for inner in (False,True):
        for ring,(rx,ry,z,curve) in enumerate(rings):
            for angle in angles:
                x=rx*math.cos(angle);y=ry*math.sin(angle)
                vertices.append((x,y,z+curve*abs(math.sin(angle))-(.007 if inner else 0)))
                amount=min(.30,max(0,(abs(x)-.21)/.17)*.30)*(ring/4)
                weights.append({'spine_03':1-amount,('clavicle_l' if x>0 else 'clavicle_r'):amount})
    stride=len(angles);layer_size=len(rings)*stride
    for inner in (0,1):
        base=inner*layer_size
        for ring in range(4):
            for i in range(stride-1):
                face=(base+ring*stride+i,base+(ring+1)*stride+i,base+(ring+1)*stride+i+1,base+ring*stride+i+1)
                faces.append(tuple(reversed(face)) if inner else face)
    for ring in (0,4):
        for i in range(stride-1):
            a=ring*stride+i;b=a+1;faces.append((a,b,b+layer_size,a+layer_size))
    for i in (0,stride-1):
        for ring in range(4):
            a=ring*stride+i;b=(ring+1)*stride+i;faces.append((a,b,b+layer_size,a+layer_size))
    data=bpy.data.meshes.new('Mira_DrapedMantle');data.from_pydata(vertices,[],faces);data.materials.append(material);data.update()
    uv_layer=data.uv_layers.new(name=mesh.data.uv_layers.active.name)
    for loop in uv_layer.data:loop.uv=uv
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    mantle=bpy.data.objects.new('Mira_DrapedMantle',data);mesh.users_collection[0].objects.link(mantle)
    for index,mapping in enumerate(weights):
        for name,amount in mapping.items():
            if amount>0:(mantle.vertex_groups.get(name) or mantle.vertex_groups.new(name=name)).add([index],amount,'REPLACE')
    hidden=mesh.hide_get();mesh.hide_set(False);bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True);mantle.select_set(True);bpy.context.view_layer.objects.active=mesh;bpy.ops.object.join();mesh.hide_set(hidden)

def tailor(mesh):
    records=[]
    for part in components(mesh):
        count=part['count'];group=part['groups'];center=Vector(part['center_m'])
        vertices=[mesh.data.vertices[i] for i in part['indices']]
        if count==24 and set(group)=={'pelvis','spine_02','spine_03'}:
            for vertex in vertices[12:16]:vertex.co.y-=.045
            for vertex in vertices[16:20]:vertex.co.y-=.012
            records.append('back strap follows torso surface instead of passing through it')
        elif group==['pelvis'] and count in (16,24) and center.z<.8 and abs(center.x)<.2:
            for vertex in vertices:
                t=max(0,min(1,(.93-vertex.co.z)/.34))
                vertex.co.x*=1-.15*t
                if abs(vertex.co.x)<.07:vertex.co.x+=math.copysign(.013*t,vertex.co.x)
            ids=set(part['indices'])
            for face in mesh.data.polygons:
                if all(i in ids for i in face.vertices) and abs(face.normal.y)<.85:
                    for index in face.loop_indices:mesh.data.uv_layers.active.data[index].uv=(.625,.125)
            records.append('split coat tapered; restrained teal edge seam uses existing atlas')
        elif group==['hand_r'] and count==70:
            for vertex in vertices:
                for axis,radius in ((0,.061),(1,.063)):
                    delta=vertex.co[axis]-center[axis]
                    vertex.co[axis]=center[axis]+math.copysign((abs(delta)/radius)**.70*radius,delta)
                vertex.co.z=center.z+(vertex.co.z-center.z)*.93
            records.append('staff hand shaped into rounded closed mitten grip')
        elif group==['hand_r'] and count==40:
            for vertex in vertices:
                vertex.co.x-=.016;vertex.co.y+=.012
                vertex.co.z=center.z+(vertex.co.z-center.z)*.70+.007
            records.append('thumb closes across the front of the staff grip')
    mesh.data.update();return records

parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);src=args.input.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
refined=json.loads((src/'refinement.json').read_text());candidate=Path(refined['candidate'])
assert sha(candidate)==refined['candidate_sha256'];bpy.ops.wm.open_mainfile(filepath=str(candidate))
arm=bpy.data.objects['Armature'];before=invariants(arm);changes={}
for name in ('SK_'+UID,'BODY_SK_'+UID,'COSTUME_SK_'+UID,'EQUIPMENT_SK_'+UID):
    mesh=bpy.data.objects[name]
    if name in ('SK_'+UID,'COSTUME_SK_'+UID):replace_mantle(mesh)
    changes[name]=tailor(mesh)
assert invariants(arm)==before
action=bpy.data.actions[f'AN_{UID}_Idle'];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
bpy.context.scene.frame_set(1);target=out/'mira-update24-revision7.blend';bpy.ops.wm.save_as_mainfile(filepath=str(target),check_existing=False)
for name in ('before-source.blend','before-export-manifest.json'):shutil.copy2(src/name,out/name)
renders=render_views(out,'after')
refined.update(candidate=str(target),candidate_sha256=sha(target),verified_candidate_invariants=before,
    tailoring_changes=changes,tailoring_script_sha256=sha(Path(__file__)),
    geometry_unchanged_from_rendered_candidate=False,rendered_geometry_source=str(out),renders=renders,
    mantle_replacement='two rigid source islands replaced by one connected 250-vertex draped shell; closed7mm thickness, existing coral atlas, bounded clavicle weights')
(out/'refinement.json').write_text(json.dumps(refined,indent=2)+'\n')
print('WC_MIRA_TAILORING_RENDERED',flush=True)
