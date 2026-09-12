"""Preserve the sound cage; transfer only ring/little distal surfaces to new target."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[1]
source=OUT/'ada_bw6_hand_reconstructed_correction1.blend'
targetfile=OUT/'ada_bw6_hand_target_local_c2.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
s=bpy.context.scene;o=bpy.data.objects['BW6_ClosedGlove_Reconstructed'];o.data=o.data.copy()
with bpy.data.libraries.load(str(targetfile),link=False) as (a,b):
 b.objects=['BW6_Anatomical_PalmThenar_SculptTarget']
t=b.objects[0];t.name='BW6_Distal_Corrected_FormTarget';s.collection.objects.link(t);t.hide_render=True;t.hide_set(True)
me=t.data;me.calc_loop_triangles();points=[t.matrix_world@v.co for v in me.vertices]
regions={'ring':(-.029,-.009),'little':(-.055,-.029)}
records={}
for name,(xmin,xmax) in regions.items():
 tris=[tuple(tr.vertices) for tr in me.loop_triangles if all(xmin<p.x<xmax and p.y<.102 and p.z>.023 for p in [points[i] for i in tr.vertices])]
 tree=BVHTree.FromPolygons(points,tris,all_triangles=True)
 vg=o.vertex_groups.new(name='BW6_LOCAL_TARGET_TRANSFER_'+name)
 changes=[]
 for v in o.data.vertices:
  p=v.co.copy()
  if not (xmin<p.x<xmax and p.y<.094 and p.z>.029):continue
  q,n,idx,d=tree.find_nearest(p)
  if q is None or d>.012:continue
  # Declared anatomical DIP-to-pad strip, anchored to unchanged middle phalanx.
  w=max(0,min(1,(.094-p.y)/.006));w=w*w*(3-2*w)
  v.co=p+(q-p)*w;vg.add([v.index],w,'REPLACE')
  changes.append({'id':v.index,'before_m':list(p),'target_m':list(q),'after_m':list(v.co),'weight':w})
 records[name]={'anatomical_region_before_projection':{'x_range_m':[xmin,xmax],'y_below_m':.094,'z_above_m':.029},'changed':changes}
o.data.update();o['method']='Preserved correction-1 cage; local ring/little distal reconstruction transferred to corrected volume target. No whole-hand remeshing or palm changes.'
s.name='BW6_LOCAL_DISTAL_TARGET_TRANSFER'
s.camera=bpy.data.objects['BW4_oblique']
outfile=OUT/'ada_bw6_hand_local_transfer_initial.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(outfile))
for name in ('palm','oblique','side'):
 s.camera=bpy.data.objects['BW4_'+name];s.render.filepath=str(OUT/'captures'/('local_transfer_initial_'+name+'.png'));bpy.ops.render.render(write_still=True)
 for ob in s.objects:
  if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=True
 s.render.filepath=str(OUT/'captures'/('local_transfer_initial_'+name+'_isolated.png'));bpy.ops.render.render(write_still=True)
 for ob in s.objects:
  if ob.name.startswith('BW4_SelectedSword_'):ob.hide_render=not ob.name.endswith('handle')
(OUT/'records/local_transfer_initial.json').write_text(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'target':str(targetfile),'target_sha256':hashlib.sha256(targetfile.read_bytes()).hexdigest(),'method':'Same metric rest space; local closest target point within anatomically constrained digit surfaces; existing sound cage preserved elsewhere','no_topology_change':True,'equipment_change':False,'regions':records},indent=2))
print('LOCAL_TARGET_TRANSFER_DONE',sum(len(r['changed']) for r in records.values()),flush=True)
