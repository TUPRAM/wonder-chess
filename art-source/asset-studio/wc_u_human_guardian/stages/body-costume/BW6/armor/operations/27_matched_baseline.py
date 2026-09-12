import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1]
current=R/'ada_bw6_upper_combined_r001.blend'
source=R.parents[1]/'BW5/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(current),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s
settings={};lights={}
for o in s.objects:
 if o.type=='CAMERA':settings[o.name]={'matrix':[list(v) for v in o.matrix_world],'type':o.data.type,'lens':o.data.lens,'ortho_scale':o.data.ortho_scale,'shift_x':o.data.shift_x,'shift_y':o.data.shift_y}
 if o.type=='LIGHT':lights[o.name]={'matrix':[list(v) for v in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'size':getattr(o.data,'size',0)}
res=[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage]
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
for n,r in settings.items():
 o=bpy.data.objects.get(n)
 if not o:continue
 o.matrix_world=Matrix(r['matrix'])
 for k,v in r.items():
  if k!='matrix':setattr(o.data,k,v)
for n,r in lights.items():
 o=bpy.data.objects.get(n)
 if not o:raise RuntimeError('Missing historical comparison light '+n)
 o.matrix_world=Matrix(r['matrix'])
 for k in ['energy','color']:setattr(o.data,k,r[k])
 if hasattr(o.data,'size'):o.data.size=r['size']
m=bpy.data.materials.new('BW6_Matched_Baseline_Clay');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.43,.43,.43,1);p.inputs['Roughness'].default_value=.72
for layer in s.view_layers:layer.material_override=m
s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=res;s.render.threads=4;s.cycles.samples=20
captures=[]
for view in ['front','profile','three_quarter','back']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];path=R/'captures'/('BW5_matched_'+view+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);captures.append(str(path))
(R/'records/matched_baseline.json').write_text(json.dumps({'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'comparison_setup_source':str(current),'camera':settings,'lights':lights,'resolution':res,'frame':1,'captures':captures,'source_saved':False},indent=2))
print('BW5_MATCHED_BASELINE_COMPLETE')
