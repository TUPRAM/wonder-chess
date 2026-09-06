"""Incremental saved-scene tailoring for the three existing Thistlewood heroes."""
import argparse,json,math,shutil,sys
from pathlib import Path
import bmesh,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import sha,components,invariants,render_views

def append_piece(mesh,label,vertices,faces,group,uv):
    data=bpy.data.meshes.new(label);data.from_pydata(vertices,[],faces);data.update()
    data.materials.append(mesh.data.materials[0]);layer=data.uv_layers.new(name=mesh.data.uv_layers.active.name)
    for loop in layer.data:loop.uv=uv
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    piece=bpy.data.objects.new(label,data);mesh.users_collection[0].objects.link(piece)
    if isinstance(group,str):piece.vertex_groups.new(name=group).add(list(range(len(vertices))),1,'REPLACE')
    else:
        for index,mapping in enumerate(group):
            for bone,amount in mapping.items():
                if amount>0:(piece.vertex_groups.get(bone) or piece.vertex_groups.new(name=bone)).add([index],amount,'REPLACE')
    hidden=mesh.hide_get();mesh.hide_set(False);bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True);piece.select_set(True);bpy.context.view_layer.objects.active=mesh;bpy.ops.object.join();mesh.hide_set(hidden)

def remove_parts(mesh,parts):
    ids={i for part in parts for i in part['indices']}
    bm=bmesh.new();bm.from_mesh(mesh.data);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.verts[i] for i in ids],context='VERTS');bm.to_mesh(mesh.data);bm.free();mesh.data.update()

def drape(mesh,part,kind):
    """A closed curved cloth surface replaces only the selected old plate island."""
    center=Vector(part['center_m']);side=1 if center.x>0 else -1
    vertices=[];faces=[];rows=7;cols=9
    for back in (False,True):
        for j in range(rows):
            t=j/(rows-1)
            for i in range(cols):
                a=i/(cols-1)
                if kind=='leaf':
                    width=.089*(.62+.65*math.sin(math.pi*t))*(1-.90*t**4)
                    x=center.x+(2*a-1)*width
                    y=-.178-.036*math.sin(math.pi*a)-.035*t
                    z=1.395-.620*t+.014*math.sin(math.pi*a)
                else:
                    # Over-shoulder drape with a broad curved, tapering petal edge.
                    width=.33+.045*math.sin(math.pi*t)
                    x=side*(.075+width*a)
                    y=(-.19+.38*t)*(.70+.30*a)
                    z=1.491+.022*math.sin(math.pi*t)-.146*a**1.8-.020*(t-.5)**2+.09*math.sin(math.pi*a/2)
                    if kind=='mantle':z-=.08*t*a; x+=side*.025*a
                vertices.append((x,y-(.009 if back else 0),z))
    layer=rows*cols
    for back in (0,1):
        base=back*layer
        for j in range(rows-1):
            for i in range(cols-1):
                face=(base+j*cols+i,base+(j+1)*cols+i,base+(j+1)*cols+i+1,base+j*cols+i+1)
                faces.append(tuple(reversed(face)) if back else face)
    boundary=list(range(cols))+[j*cols+cols-1 for j in range(1,rows)]+list(range(layer-2,layer-cols-1,-1))+[j*cols for j in range(rows-2,0,-1)]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.append((a,b,b+layer,a+layer))
    weights='spine_02'
    if kind!='leaf':
        weights=[]
        for x,y,z in vertices:
            amount=max(0,min(1,(abs(x)-.13)/.13))
            weights.append({'spine_03':1-amount,'upperarm_'+('l' if x>0 else 'r'):amount})
    append_piece(mesh,'Thistlewood_'+kind,vertices,faces,weights,(.125,.125) if kind!='petal' else (.375,.125))

def lantern(mesh):
    # Compact shielded courier lantern at the belt, with dark rim and amber inset.
    def shape(label,rings,uv):
        verts=[(-.235+rx*math.cos(a*math.pi/4),.14+ry*math.sin(a*math.pi/4),z) for rx,ry,z in rings for a in range(8)]
        faces=[tuple(range(7,-1,-1)),tuple(range((len(rings)-1)*8,len(rings)*8))]
        for j in range(len(rings)-1):
            for i in range(8):faces.append((j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i))
        append_piece(mesh,label,verts,faces,'pelvis',uv)
    shape('Sylas_LanternShell',[(.037,.033,.925),(.045,.038,.935),(.045,.038,1.013),(.026,.024,1.029),(.012,.014,1.05)],(.625,.125))
    shape('Sylas_LanternAmberInset',[(.035,.033,.944),(.035,.041,.951),(.034,.041,.997),(.027,.034,1.006)],(.625,.625))

def harp_grip(mesh):
    first=Vector((.546,.102,.773));last=Vector((.573,.259,.715))
    direction=(last-first).normalized();axis=direction.cross(Vector((1,0,0))).normalized();other=direction.cross(axis)
    vertices=[tuple(center+.015*(axis*math.cos(i*math.pi/4)+other*math.sin(i*math.pi/4))) for center in (first,last) for i in range(8)]
    faces=[tuple(range(7,-1,-1)),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
    append_piece(mesh,'Elin_HarpSupportGrip',vertices,faces,'hand_l',(.875,.125))

def alter(mesh,uid):
    records=[];parts=components(mesh);replace=[]
    for part in parts:
        count=part['count'];groups=part['groups'];center=Vector(part['center_m'])
        verts=[mesh.data.vertices[i] for i in part['indices']]
        if groups==['head'] and count==5:
            for v in verts:v.co.y=part['bounds_min_m'][1]+(v.co.y-part['bounds_min_m'][1])*.68;v.co.x*=.91
            records.append('refined nose projection')
        elif groups==['head'] and count==15 and center.z>1.69:
            for v in verts:v.co.z=center.z+(v.co.z-center.z)*.56-.006
            records.append('slender eyebrows preserve visible eyes')
        elif groups==['head'] and count==112:
            for v in verts:
                low=max(0,min(1,(center.z-.04-v.co.z)/.10));v.co.x*=1-.07*low
            records.append('defined lower cheek and jaw')
        elif groups==['pelvis'] and count in (16,24) and center.z<.92 and abs(center.x)>.05:
            for v in verts:
                t=max(0,min(1,(1.01-v.co.z)/.37));v.co.x*=1-.23*t
                v.co.y+=math.copysign(.012*math.sin(math.pi*t),v.co.y)
                if abs(v.co.x)<.065:v.co.x+=math.copysign(.012*t,v.co.x)
            indices=set(part['indices'])
            for face in mesh.data.polygons:
                if all(i in indices for i in face.vertices) and abs(face.normal.y)<.75:
                    for loop in face.loop_indices:mesh.data.uv_layers.active.data[loop].uv=(.375,.125)
            records.append('tapered split garment with existing pale edge seam')
        elif groups in (['hand_l'],['hand_r']) and count==70:
            for v in verts:
                for axis in (0,1):
                    radius=(part['bounds_max_m'][axis]-part['bounds_min_m'][axis])/2;delta=v.co[axis]-center[axis]
                    v.co[axis]=center[axis]+math.copysign((abs(delta)/radius)**.73*radius,delta)
                v.co.z=center.z+(v.co.z-center.z)*.91
            records.append('closed rounded grip palm')
        elif groups in (['hand_l'],['hand_r']) and count==40:
            for v in verts:
                v.co.x+=.016 if groups==['hand_l'] else -.016;v.co.y+=.012;v.co.z=center.z+(v.co.z-center.z)*.72+.006
            records.append('thumb wrapped onto visual grip')
        if count==112 and (uid=='wc_u_elf_priest' and 'upperarm_l' in groups or uid=='wc_u_elf_priest' and 'upperarm_r' in groups or uid=='wc_u_elf_rogue' and 'upperarm_l' in groups):
            first=sum((v.co for v in verts[:16]),Vector())/16
            second=sum((v.co for v in verts[16:32]),Vector())/16
            for v in verts[:16]:v.co=first.lerp(second,.12)+(v.co-first)*.52
            for v in verts[16:32]:v.co=second+(v.co-second)*.85
            records.append('shoulder cap tapered beneath its cloth drape to remove exposed intersection')
        if uid=='wc_u_elf_ranger':
            if groups==['spine_02'] and count==20 and center.y>-.25:replace.append((part,'leaf'))
            elif groups==['hand_l'] and count==56:
                for ring in range(7):
                    section=verts[ring*8:(ring+1)*8];mid=sum((v.co for v in section),Vector())/8
                    for v in section:
                        v.co=mid+(v.co-mid)*1.15
                        v.co.x-=.074*math.exp(-((v.co.z-.785)/.15)**2)
                records.append('broader bow limbs with center grip aligned to palm; tips preserved')
            elif groups==['spine_02'] and center.y<-.28:
                for v in verts:v.co.y-=.012
                records.append('quiver and arrows moved clear of draped cloak')
        elif uid=='wc_u_elf_priest':
            if groups==['spine_03'] and count==20:replace.append((part,'petal'))
            elif groups==['hand_l'] and count==186:
                for j in range(0,count,6):
                    section=verts[j:j+6];mid=sum((v.co for v in section),Vector())/6
                    for v in section:v.co=mid+(v.co-mid)*.78
                records.append('slimmer crescent rim expands negative space')
            elif groups==['hand_l'] and count==10:
                for v in verts:v.co.x=center.x+(v.co.x-center.x)*1.18;v.co.y=center.y+(v.co.y-center.y)*1.18
                records.append('four thicker harp strings retained')
        else:
            if groups==['spine_03'] and count==20:replace.append((part,'mantle'))
            elif groups in (['hand_l'],['hand_r']) and count==24:
                sign=1 if groups==['hand_l'] else -1
                for v in verts:
                    t=max(0,min(1,(v.co.z-.89)/.44));v.co.x+=sign*.033*math.sin(t*math.pi/2)
                    if sign<0:v.co.z=.89+(v.co.z-.89)*.83
                records.append('paired curved blades differentiated in length and sweep')
            elif groups==['neck'] and count==40:
                for v in verts:v.co.z-=.014
                records.append('scarf lowered clear of chin')
            elif groups==['head'] and count==24:
                for v in verts:v.co.x+=.014*(v.co.z-part['bounds_min_m'][2])/.085
                records.append('short side-swept locks')
            elif count==60 and ('thigh_l' in groups or 'thigh_r' in groups):
                ids=set(part['indices'])
                for face in mesh.data.polygons:
                    if all(i in ids for i in face.vertices):
                        for loop in face.loop_indices:mesh.data.uv_layers.active.data[loop].uv=(.375,.125)
                records.append('fog-gray trousers match existing authored costume')
    mesh.data.update()
    if replace:
        remove_parts(mesh,[p for p,k in replace])
        for part,kind in replace:drape(mesh,part,kind)
        records.append('replaced selected rigid cloth plates with closed curved draped surfaces')
    if uid=='wc_u_elf_rogue' and mesh.name in ('SK_'+uid,'EQUIPMENT_SK_'+uid):lantern(mesh);records.append('compact shielded cosmetic courier lantern')
    if uid=='wc_u_elf_priest' and mesh.name in ('SK_'+uid,'EQUIPMENT_SK_'+uid):harp_grip(mesh);records.append('supporting hand wraps a bracket physically connected to the crescent')
    return records

parser=argparse.ArgumentParser();parser.add_argument('--unit',choices=['wc_u_elf_ranger','wc_u_elf_priest','wc_u_elf_rogue'],required=True);parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);uid=args.unit;out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
shutil.copy2(Path(__file__),out/'executed-refinement.py')
source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';export=ROOT/f'exports/heroes/{uid}'
manifest=json.loads((export/'export_manifest.json').read_text());assert manifest['source_revision']==6 and sha(source)==manifest['source_sha256']
shutil.copy2(source,out/'before-source.blend');shutil.copy2(export/'export_manifest.json',out/'before-export-manifest.json')
bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature'];before=invariants(arm)
changes={name:alter(bpy.data.objects[name],uid) for name in ('SK_'+uid,'BODY_SK_'+uid,'COSTUME_SK_'+uid,'EQUIPMENT_SK_'+uid)}
assert invariants(arm)==before
action=bpy.data.actions[f'AN_{uid}_Idle'];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0];bpy.context.scene.frame_set(1)
candidate=out/(uid+'-update24-revision7.blend');bpy.ops.wm.save_as_mainfile(filepath=str(candidate),check_existing=False);renders=render_views(out,'after')
assert sha(source)==manifest['source_sha256']
(out/'refinement.json').write_text(json.dumps({'status':'SOURCE_REFINEMENT_RENDERED_NOT_PROMOTED','source_before_sha256':manifest['source_sha256'],'candidate':str(candidate),'candidate_sha256':sha(candidate),'preserved_invariants':before,'changes':changes,'renders':renders,'refinement_script_sha256':sha(Path(__file__)),'limits':['Seven clips need current geometry review','LODs pending regeneration','Unreal not imported','Final art not accepted']},indent=2)+'\n')
print('WC_EXISTING_ELF_REFINED '+uid,flush=True)
