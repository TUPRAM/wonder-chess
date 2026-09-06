"""Execute the non-mutating normalized-copy exporter on the stable Ada source."""
import bpy,sys,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).resolve().parent))
from normalized_fbx import export_normalized_copy
from author_alpha import export_fbx_raw as export_fbx
uid='wc_u_human_guardian';source=root/f'art-source/heroes/{uid}/{uid}.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
arm=bpy.data.objects['Armature'];mesh=bpy.data.objects['SK_'+uid];scene=bpy.context.scene
action=bpy.data.actions[f'AN_{uid}_Idle'];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0];scene.frame_set(1)
def snapshot():
    return {'vertices':[list(v.co) for v in mesh.data.vertices],'bones':{b.name:[list(b.head_local),list(b.tail_local)] for b in arm.data.bones},
            'units':scene.unit_settings.scale_length,'action':arm.animation_data.action.name,'names':[arm.name,mesh.name],
            'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
before=snapshot();out=root/'exports/calibration/import-probe-normalized-cm-copy';out.mkdir(parents=True,exist_ok=True)
export_normalized_copy(out/'SK_Ada.fbx',[arm,mesh],False,export_fbx)
manifest=json.loads((root/f'exports/heroes/{uid}/export_manifest.json').read_text())
for clip,spec in manifest['clips'].items():
    current=bpy.data.actions[spec['action']];arm.animation_data.action=current;arm.animation_data.action_slot=current.slots[0]
    scene.frame_start=spec['frames'][0];scene.frame_end=spec['frames'][1];scene.frame_set(scene.frame_start)
    export_normalized_copy(out/f'AN_Ada_{clip}.fbx',[arm],True,export_fbx)
arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0];scene.frame_set(1)
after=snapshot()
if before!=after:raise RuntimeError('Export modified the original in-memory source or saved file')
report={'status':'executed_copy_export_preserved_original_data','source_sha256':before['source_sha256'],'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.fbx')}}
(out/'trial_manifest.json').write_text(json.dumps(report,indent=2)+'\n');print('WC_NORMALIZED_COPY_PASS '+json.dumps(report),flush=True)
