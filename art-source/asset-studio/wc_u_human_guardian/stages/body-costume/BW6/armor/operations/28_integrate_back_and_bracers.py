import bpy,json,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_upper_combined_r001.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);rig=bpy.data.objects['BW4_Armor_Independent_Rig']
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
back=module('bw6_back',R.parent/'backplate/append_backplate.py').append_backplate()
bracers=module('bw6_bracers',R.parent/'bracer/append_bracers.py').append_bracers(rig,s)
hidden=[]
for o in s.objects:
 if o.type=='MESH' and o.name.startswith('BW4_') and 'Bracer' in o.name:
  o.hide_render=True;o.hide_set(True);hidden.append(o.name)
steel=bpy.data.materials['BW6_ColorLayout_Steel'];leather=bpy.data.materials['BW6_ColorLayout_Leather']
for n in back['owned']+bracers['objects']:
 o=bpy.data.objects[n];o.data.materials.clear();o.data.materials.append(steel if 'DorsalShell' in n or 'BackPlate' in n else leather)
owned=[n for n in json.loads(s['BW6_owned_visible_parts']) if n not in back['hidden_baseline']]
s['BW6_owned_visible_parts']=json.dumps(owned+back['owned']+bracers['objects'])
s['BW6_append_records']=json.dumps({'backplate':back,'bracers':bracers,'hidden_old_bracers':hidden})
s['BW6_combined_status']='ART_REVISE; new front/back/collar/side/shoulder/bracer assembly. Hand, left shoulder, lower armor and head contextual. Failed straps excluded as rejected experiments, not accepted hidden support.'
for layer in s.view_layers:layer.material_override=None
out=R/'ada_bw6_upper_integrated_r002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
s.render.threads=4;s.cycles.samples=20
for kind,view in [('clay','front'),('clay','profile'),('clay','back'),('color_layout','three_quarter')]:
 for layer in s.view_layers:layer.material_override=bpy.data.materials['BW6_Review_Clay'] if kind=='clay' else None
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/f'integrated_r002_{kind}_{view}.png');bpy.ops.render.render(write_still=True)
(R/'records/integrated_r002_sources.json').write_text(json.dumps({'source':str(out),'backplate':back,'bracers':bracers,'hidden_old_bracers':hidden,'status':s['BW6_combined_status']},indent=2));print('BW6_INTEGRATED_R002_COMPLETE')
