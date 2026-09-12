import bpy,hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];BW4=OUT.parents[1]/'BW4/r001';source=BW4/'ada_fixed_hand_checkpoint_ART_REVISE.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);s=bpy.context.scene;record={'source':str(source),'sha256':before,'captures':[]}
for name in ('palm','dorsal','side','underside','oblique','axial'):
 s.camera=bpy.data.objects['BW4_'+name]
 for ob in s.objects:
  if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=not ob.name.endswith('handle')
 path=OUT/'captures'/('bw4_fresh_hilt_only_'+name+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);record['captures'].append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'camera':s.camera.name,'matrix_world':[list(r) for r in s.camera.matrix_world],'ortho_scale':s.camera.data.ortho_scale})
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
(OUT/'records/fresh_baseline_manifest.json').write_text(json.dumps(record,indent=2))
# Raw cage of rejected final experiment, labeled as a failure in the review.
source=OUT/'ada_bw5_hand_correction2.blend';before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);s=bpy.context.scene;o=bpy.data.objects['BW5_ClosedGlove_Correction2']
for ob in s.objects:
 if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=True
o.modifiers[0].show_render=False
overlay=bpy.data.objects.new('BW5_REJECTED_Actual_Cage',o.data.copy());s.collection.objects.link(overlay);overlay.color=(.015,.02,.025,1);mod=overlay.modifiers.new('Actual raw edges','WIREFRAME');mod.thickness=.00022;mod.use_replace=True
s.camera=bpy.data.objects['BW4_palm'];s.render.filepath=str(OUT/'captures/rejected_correction2_actual_cage.png');bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
