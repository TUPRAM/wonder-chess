import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_simple_clamped.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
def mat(name,color,metal=0,rough=.65):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
clay=mat('BW6_Review_Clay',(.43,.43,.43),0,.72)
steel=mat('BW6_ColorLayout_Steel',(.22,.25,.29),.72,.34)
ivory=mat('BW6_ColorLayout_Padding',(.64,.57,.44),0,.84)
navy=mat('BW6_ColorLayout_Navy',(.025,.038,.069),0,.8)
leather=mat('BW6_ColorLayout_Leather',(.105,.055,.026),0,.72)
gold=mat('BW6_ColorLayout_RestrainedGold',(.49,.30,.095),.65,.35)
def assign(o,m):o.data.materials.clear();o.data.materials.append(m)
owned=json.loads(s['BW6_owned_visible_parts'])
# The waist is a sewn material zone on the continuous coat. Reject the
# intersecting duplicate tube, rather than hiding it inside another surface.
duplicate=bpy.data.objects['BW6_NavyWaist'];duplicate.hide_render=True;duplicate.hide_set(True)
owned.remove(duplicate.name)
coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];coat.data.materials.clear();coat.data.materials.append(ivory);coat.data.materials.append(navy)
for f in coat.data.polygons:
 p=f.center;f.material_index=int((p.z<1.245 and abs(p.x)<.21) or (p.z>1.465 and p.x>0))
coat['BW6_waist_representation']='Continuous existing fitted cloth surface is navy below plate; duplicate intersecting navy tube is rejected/hidden. Separate navy fabric pattern piece is represented by a sewn material zone, not two overlapping surfaces.'
for n in owned:
 if n==coat.name:continue
 assign(bpy.data.objects[n],leather if 'Belt' in n else steel)
assign(bpy.data.objects['BW4_CONTEXT_BW1_BeltBuckle'],gold)
# Preserve legacy mesh geometry while assigning diagnostic context colors on
# independent data copies; no texture, UV, bake or runtime material claim.
context=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render or o.name in owned or 'BodyFit' in o.name or 'Head' in o.name or 'Eye' in o.name:continue
 if o.name.startswith('BW4_'):
  o.data=o.data.copy();name=o.name
  m=steel if any(k in name for k in ['Pauldron','Bracer','Greave','Knee']) else navy if any(k in name for k in ['Tabard','Leggings']) else ivory if 'CoatPanel' in name else leather
  assign(o,m);context.append(o.name)
# Two fitted side closures: original steel enclosure remains rigid. Buckles
# are separate readable leather construction over that already-shaped panel.
rig=bpy.data.objects['BW4_Armor_Independent_Rig'];collection=bpy.data.collections['BW6_TORSO_RECONSTRUCTION'];fasteners=[]
for sign in [-1,1]:
 for j,z in enumerate([1.226,1.294]):
  vs=[];fs=[]
  for k,y in enumerate([-.105,-.055,0,.055]):
   x=sign*(.189 if j==0 else .198)
   for dz in [-.008,.008]:vs.append((x,y,z+dz))
   if k:a=(k-1)*2;fs.append((a,a+1,a+3,a+2))
  me=bpy.data.meshes.new('BW6_SideStrap_Cage');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
  o=bpy.data.objects.new(f'BW6_Side_LeatherClosure_{sign}_{j}',me);collection.objects.link(o);assign(o,leather)
  g=o.vertex_groups.new(name='spine01');g.add(list(range(len(vs))),1,'REPLACE')
  wall=o.modifiers.new('Leather thickness','SOLIDIFY');wall.thickness=.0025;wall.offset=1;wall.use_even_offset=False
  be=o.modifiers.new('Leather edge','BEVEL');be.width=.001;be.segments=2
  arm=o.modifiers.new('Chest owner','ARMATURE');arm.object=rig;fasteners.append(o.name)
s['BW6_owned_visible_parts']=json.dumps(owned+fasteners);s['BW6_color_layout_scope']='Diagnostic identity colors only. Not UVs/textures/bakes or material approval. Clay captures use uniform override. Legacy head, hands, lower costume remain contextual.'
s['BW6_status']='ART_REVISE_PENDING_COMBINED_REVIEW'
for layer in s.view_layers:layer.material_override=None
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_upper_color_layout_work.blend'))
s.cycles.samples=24;s.render.threads=4
for kind in ['clay','color_layout']:
 for layer in s.view_layers:layer.material_override=clay if kind=='clay' else None
 for view in ['front','three_quarter','back']:
  s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('layout_'+kind+'_'+view+'.png'));bpy.ops.render.render(write_still=True)
(R/'records/shared_waist_and_layout.json').write_text(json.dumps({'removed_duplicate':duplicate.name,'waist_representation':coat['BW6_waist_representation'],'new_fasteners':fasteners,'context_material_data_copies':context,'scope':s['BW6_color_layout_scope']},indent=2))
print('BW6_LAYOUT_COMPLETE')
