"""Show declared patch selections, without altering the frozen mesh."""
import bpy,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parents[1];p=OUT/'ada_bw6_hand_checkpoint_ART_REVISE.blend';digest=hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False);s=bpy.context.scene;o=bpy.data.objects['BW6_ClosedGlove_Retained']
colors=[(.43,.44,.46,1),(.95,.26,.22,1),(.25,.66,.95,1),(.3,.85,.4,1),(.93,.67,.2,1),(.81,.37,.92,1)]
names=['glove','index','middle','ring','little','thumb'];o.data.materials.clear()
for name,col in zip(names,colors):
 m=bpy.data.materials.new('BW6_Patch_'+name);m.diffuse_color=col;o.data.materials.append(m)
groups={g.index:names.index(g.name.replace('BW6_CONTACT_','')) for g in o.vertex_groups if g.name.startswith('BW6_CONTACT_')}
for f in o.data.polygons:
 counts={}
 for i in f.vertices:
  for g in o.data.vertices[i].groups:
   if g.group in groups and g.weight>.999:counts[groups[g.group]]=counts.get(groups[g.group],0)+1
 if counts:
  n=max(counts,key=counts.get)
  if counts[n]>=len(f.vertices)*.5:f.material_index=n
s.display.shading.color_type='MATERIAL'
for ob in s.objects:
 if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=True
captures=[]
for view in ('palm','oblique','side'):
 s.camera=bpy.data.objects['BW4_'+view];out=OUT/'captures'/('provisional_pad_regions_'+view+'.png');s.render.filepath=str(out);bpy.ops.render.render(write_still=True);captures.append({'path':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
(OUT/'records/pad_region_visualization.json').write_text(json.dumps({'source':str(p),'source_sha256':digest,'geometry_saved':False,'legend':dict(zip(names,colors)),'scope':'Face color shows >=half vertices in provisional cage region. Actual scored evaluated vertices are recorded separately. Patch membership is not contact or approval.','captures':captures},indent=2))
