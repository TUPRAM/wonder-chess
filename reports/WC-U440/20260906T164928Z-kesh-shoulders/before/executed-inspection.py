"""Read current Kesh sleeve topology and arm bones without saving the asset."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,invariants
p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);report=a.report.resolve();report.mkdir(parents=True,exist_ok=False);uid='wc_u_orc_rogue';source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature'];objects={}
for name in ['SK_'+uid,'BODY_SK_'+uid,'COSTUME_SK_'+uid]:
    ob=bpy.data.objects[name];objects[name]=[]
    for c in components(ob):
        if any(('arm' in g or 'hand' in g) for g in c['groups']):
            c.pop('indices');objects[name].append(c)
record={'source_sha256':digest,'objects':objects,'invariants':invariants(arm),'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local)} for b in arm.data.bones}}
(report/'arm-inspection.json').write_text(json.dumps(record,indent=2)+'\n');(report/'executed-inspection.py').write_bytes(Path(__file__).read_bytes());assert hashlib.sha256(source.read_bytes()).hexdigest()==digest;print('WC_KESH_READONLY_ARM_INSPECTION_PASS')
