"""Render all three authored LOD meshes at a small inspection scale."""
import bpy
import json
import argparse,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
ids=json.loads((root/'data/rules.alpha.json').read_text())['alpha_unit_ids']
parser=argparse.ArgumentParser();parser.add_argument('--ids',nargs='+');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
selected=args.ids or ids
records=[]
for uid in selected:
    bpy.ops.wm.open_mainfile(filepath=str(root/f'art-source/heroes/{uid}/{uid}.blend'))
    sc=bpy.context.scene;sc.render.resolution_x=192;sc.render.resolution_y=192;sc.cycles.samples=8;sc.frame_set(1)
    objects=[bpy.data.objects[f'SK_{uid}']]+[bpy.data.objects[f'SK_{uid}_LOD{i}'] for i in (1,2)]
    for index,ob in enumerate(objects):
        for other in objects:other.hide_render=other!=ob;other.hide_set(other!=ob)
        sc.render.filepath=str(root/f'reports/WC-330/{uid}/LOD{index}_192px.png');bpy.ops.render.render(write_still=True)
        manifest=json.loads((root/f'exports/heroes/{uid}/export_manifest.json').read_text())
        ob.data.calc_loop_triangles();records.append({'unit_id':uid,'source_revision':manifest['source_revision'],'source_sha256':manifest['source_sha256'],'lod':index,'triangles':len(ob.data.loop_triangles),'render':sc.render.filepath})
target=root/'reports/WC-330/roster/lod-render-evidence.json'
if args.ids and target.is_file():records.extend(r for r in json.loads(target.read_text())['records'] if r['unit_id'] not in selected)
records.sort(key=lambda r:(ids.index(r['unit_id']),r['lod']))
target.write_text(json.dumps({'status':'actual_small_scale_renders_require_visual_review','records':records},indent=2)+'\n')
print('WC_LOD_RENDERS_COMPLETE',len(records),flush=True)
