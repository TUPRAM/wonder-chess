"""Render actual model silhouettes with a diagnostic black material override."""
from pathlib import Path
import json
import argparse,sys
import bpy
root=Path(__file__).resolve().parents[2]
ids=json.loads((root/'data/rules.alpha.json').read_text())['alpha_unit_ids'];records=[]
parser=argparse.ArgumentParser();parser.add_argument('--ids',nargs='+');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
selected=args.ids or ids
for uid in selected:
    bpy.ops.wm.open_mainfile(filepath=str(root/f'art-source/heroes/{uid}/{uid}.blend'))
    sc=bpy.context.scene;sc.frame_set(1);bpy.data.objects['PRESENTATION_Ground'].hide_render=True
    sc.world.use_nodes=True
    sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(1,1,1,1)
    sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=1
    material=bpy.data.materials.new('WC_DiagnosticSilhouette');material.use_nodes=True
    nodes=material.node_tree.nodes;nodes.clear()
    emission=nodes.new('ShaderNodeEmission');emission.inputs['Color'].default_value=(0,0,0,1)
    output=nodes.new('ShaderNodeOutputMaterial');material.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
    sc.view_layers[0].material_override=material;sc.view_settings.view_transform='Standard'
    sc.render.resolution_x=256;sc.render.resolution_y=256;sc.cycles.samples=4
    sc.render.filepath=str(root/f'reports/WC-330/{uid}/silhouette.png');bpy.ops.render.render(write_still=True)
    manifest=json.loads((root/f'exports/heroes/{uid}/export_manifest.json').read_text())
    records.append({'unit_id':uid,'source_revision':manifest['source_revision'],'source_sha256':manifest['source_sha256'],'render':sc.render.filepath})
target=root/'reports/WC-330/roster/silhouette-render-evidence.json'
if args.ids and target.is_file():records.extend(r for r in json.loads(target.read_text())['records'] if r['unit_id'] not in selected)
records.sort(key=lambda r:ids.index(r['unit_id']))
target.write_text(json.dumps({'records':records,'status':'actual_Blender_silhouette_renders'},indent=2)+'\n')
print('WC_SILHOUETTE_RENDER_COMPLETE',len(records),flush=True)
