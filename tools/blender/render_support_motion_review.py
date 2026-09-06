"""Render anticipation/release/recovery of the five support-hand heroes."""
import bpy,json
import argparse,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
ids=['wc_u_elf_ranger','wc_u_elf_priest','wc_u_dwarf_guardian','wc_u_dwarf_ranger','wc_u_dwarf_warrior']
parser=argparse.ArgumentParser();parser.add_argument('--ids',nargs='+');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
selected=args.ids or ids
records=[]
for uid in selected:
    bpy.ops.wm.open_mainfile(filepath=str(root/f'art-source/heroes/{uid}/{uid}.blend'))
    manifest=json.loads((root/f'exports/heroes/{uid}/export_manifest.json').read_text())
    arm=next(o for o in bpy.data.objects if o.type=='ARMATURE');sc=bpy.context.scene
    sc.render.resolution_x=256;sc.render.resolution_y=256;sc.cycles.samples=10
    for clip in ('Move','Attack','Active'):
        spec=manifest['clips'][clip];action=bpy.data.actions[spec['action']]
        arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
        release=spec['release_frame'] or spec['frames'][1]//2
        for stage,frame in [('anticipation',max(2,release//2)),('release',release),('recovery',min(spec['frames'][1],release+9))]:
            sc.frame_set(frame)
            path=root/f'reports/WC-330/{uid}/contact_{clip}_{stage}.png';sc.render.filepath=str(path)
            bpy.ops.render.render(write_still=True)
            records.append({'unit_id':uid,'clip':clip,'stage':stage,'frame':frame,'render':str(path.relative_to(root)),
                            'source_revision':manifest['source_revision'],'source_sha256':manifest['source_sha256']})
target=root/'reports/WC-330/roster/support-motion-render-evidence.json'
if args.ids and target.is_file():records.extend(r for r in json.loads(target.read_text())['records'] if r['unit_id'] not in selected)
records.sort(key=lambda r:(ids.index(r['unit_id']),r['clip'],r['stage']))
target.write_text(json.dumps({'records':records,'status':'actual_key_pose_renders_require_review'},indent=2)+'\n')
print('WC_SUPPORT_MOTION_RENDERS_COMPLETE',len(records),flush=True)
