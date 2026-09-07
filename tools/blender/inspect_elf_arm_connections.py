"""Read actual saved elf shoulder/arm geometry and animation before scoped repair."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,invariants,use_clip
p=argparse.ArgumentParser();p.add_argument('--unit',choices=['wc_u_elf_ranger','wc_u_elf_rogue'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.output.mkdir(parents=True,exist_ok=False);source=ROOT/f'art-source/heroes/{a.unit}/{a.unit}.blend';before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature'];ob=bpy.data.objects['SK_'+a.unit];palette={}
for poly in ob.data.polygons:
    uv=ob.data.uv_layers.active.data[poly.loop_start].uv
    for i in poly.vertices:palette[i]=int(uv.x*4)+4*int(uv.y*4)
parts=[]
for c in components(ob):
    if any(s in g for g in c['groups'] for s in ['arm','hand','chest','clavicle']):
        c['palette']=palette[c['indices'][0]];c.pop('indices');parts.append(c)
bones={b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'parent':b.parent.name if b.parent else None} for b in arm.data.bones}
clip=[]
for frame in range(1,46,3):
    use_clip(arm,'Attack',frame,unit_id=a.unit);clip.append({'frame':frame,'bones':{b.name:{'rotation_euler':list(b.rotation_euler),'location':list(b.location)} for b in arm.pose.bones if any(s in b.name for s in ['arm','hand','chest'])}})
(a.output/'arm-inspection.json').write_text(json.dumps({'source_sha256':before,'parts':parts,'bones':bones,'invariants':invariants(arm),'Attack_samples':clip},indent=2)+'\n');(a.output/'executed-inspection.py').write_bytes(Path(__file__).read_bytes());assert hashlib.sha256(source.read_bytes()).hexdigest()==before;print('WC_ELF_ARM_READONLY_INSPECTION',a.unit)
