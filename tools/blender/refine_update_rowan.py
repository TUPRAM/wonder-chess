"""Refine the saved Rowan collar, vest, book and focus without rebuilding him."""
import argparse,json,math,shutil,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];UID='wc_u_human_mage'
sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import sha,components,invariants,render_views

def alter(mesh):
    changes=[]
    for part in components(mesh):
        center=Vector(part['center_m']);count=part['count'];group=part['groups']
        vertices=[mesh.data.vertices[i] for i in part['indices']];change=None
        if group==['spine_03'] and count==16:
            for vertex in vertices:
                t=max(0,min(1,(vertex.co.z-1.2638)/.2492))
                vertex.co.y=.08+(vertex.co.y-.0445)*(.40+.18*t)
                vertex.co.x+=math.copysign(.025*(1-t),vertex.co.x)
                vertex.co.z-=.018*t
            change='high collar folded into shallower open lapels'
        elif group==['spine_02'] and count==16 and abs(center.x)<.01 and center.y>.2:
            for vertex in vertices:
                t=max(0,min(1,(vertex.co.z-1.0324)/.3382))
                vertex.co.x*=.92+.23*t
                vertex.co.z-=.024*t
                vertex.co.y-=.010*t
            change='amber vest fitted beneath open lapels'
        elif group==['pelvis'] and count in (16,24) and center.z<.82 and abs(center.x)<.2:
            for vertex in vertices:
                low=max(0,min(1,(.975-vertex.co.z)/.36))
                vertex.co.x*=1-.085*low
                vertex.co.y+=math.copysign(.008*low,vertex.co.y)
            change='coat tails taper and separate below belt'
        elif group==['head'] and count==5:
            for vertex in vertices:vertex.co.x*=.93;vertex.co.y=.13706+(vertex.co.y-.13706)*.68
            change='nose projection refined beneath spectacles'
        elif group==['head'] and count==15 and center.z>1.6:
            for vertex in vertices:
                vertex.co.z=center.z+(vertex.co.z-center.z)*.65-.004
            change='brows less blocky with expression retained'
        elif group==['head'] and count==24:
            tip=vertices[16:24];midpoint=sum((v.co for v in tip),Vector())/8
            for vertex in tip:vertex.co=midpoint+(vertex.co-midpoint)*1.8+Vector((0,-.004,-.003))
            change='curl tips broadened into rounded locks'
        elif group==['hand_r'] and count in (32,138):
            stride=8 if count==32 else 6
            for index in range(0,count,stride):
                ring=vertices[index:index+stride];midpoint=sum((v.co for v in ring),Vector())/stride
                for vertex in ring:vertex.co=midpoint+(vertex.co-midpoint)*(1.20 if count==32 else 1.16)
            change='bronze support grip and open asymmetric bracket thickened'
        elif group==['hand_r'] and count==126:
            for vertex in vertices:vertex.co=center+(vertex.co-center)*.9
            change='bounded orb reveals more open bracket and supporting hand'
        elif group==['hand_r'] and count==70:
            for vertex in vertices:
                for axis in (0,1):
                    radius=(part['bounds_max_m'][axis]-part['bounds_min_m'][axis])/2
                    delta=vertex.co[axis]-center[axis]
                    vertex.co[axis]=center[axis]+math.copysign((abs(delta)/radius)**.76*radius,delta)
            change='rounded closed hand supports the bronze handle'
        elif group==['hand_r'] and count==40:
            for vertex in vertices:
                vertex.co.x-=.017;vertex.co.y+=.012
                vertex.co.z=center.z+(vertex.co.z-center.z)*.72+.007
            change='thumb wraps across bracket grip'
        elif group==['pelvis'] and count==16 and center.x>.25 and center.z>.9:
            indices=set(part['indices'])
            for face in mesh.data.polygons:
                if all(i in indices for i in face.vertices) and abs(face.normal.y)>.7:
                    for loop in face.loop_indices:mesh.data.uv_layers.active.data[loop].uv=(.125,.125)
            change='book covers use existing indigo cloth swatch, parchment page edges retained'
        if change:changes.append({'first_vertex':part['first_vertex'],'count':count,'change':change})
    mesh.data.update();return changes

parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
out=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).output.resolve();out.mkdir(parents=True,exist_ok=False)
source=ROOT/f'art-source/heroes/{UID}/{UID}.blend';export=ROOT/f'exports/heroes/{UID}'
manifest=json.loads((export/'export_manifest.json').read_text());assert manifest['source_revision']==6 and sha(source)==manifest['source_sha256']
shutil.copy2(source,out/'before-source.blend');shutil.copy2(export/'export_manifest.json',out/'before-export-manifest.json')
bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature'];before=invariants(arm)
changes={name:alter(bpy.data.objects[name]) for name in ('SK_'+UID,'BODY_SK_'+UID,'COSTUME_SK_'+UID,'EQUIPMENT_SK_'+UID)}
assert invariants(arm)==before
action=bpy.data.actions[f'AN_{UID}_Idle'];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
bpy.context.scene.frame_set(1);candidate=out/'rowan-update24-revision7.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(candidate),check_existing=False);renders=render_views(out,'after')
assert sha(source)==manifest['source_sha256']
(out/'refinement.json').write_text(json.dumps({'status':'SOURCE_REFINEMENT_RENDERED_NOT_PROMOTED',
    'source_before_sha256':manifest['source_sha256'],'candidate':str(candidate),'candidate_sha256':sha(candidate),
    'preserved_invariants':before,'changes':changes,'renders':renders,
    'limits':['Seven clips need current geometry review','LODs pending regeneration','Unreal not imported','Final art not accepted']},indent=2)+'\n')
print('WC_ROWAN_SOURCE_REFINEMENT_RENDERED',flush=True)
