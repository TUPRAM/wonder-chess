import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'ada_bw6_torso_sideclosure.blend'),use_scripts=False)
s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
coat=bpy.data.objects['BW6_PaddedCoat_Tailored'];before=[list(v.co) for v in coat.data.vertices]
# Newly constructed collar has an ordered 7-ring layout at the end of the cage.
record=json.loads((R/'records/correction1_changes.json').read_text());n=record['neck_outer_loop_count'];first=len(coat.data.vertices)-7*n
assert first>0
for j in range(7):
 for i in range(n):
  v=coat.data.vertices[first+j*n+i];p=v.co.copy();a=math.atan2((p.y+.049)/.124,p.x/.130)
  # The side base rides over the trapezius; the front neckline stays lower.
  rise=.046*math.cos(a)**2+.013*max(0,-math.sin(a))
  influence=[.35,.75,1,.95,.65,.10,0][j]
  v.co.z+=rise*influence
coat.data.update()
# A garment-only outside constraint operates in evaluated pose space. It does
# not drive the metal, change the body, or claim a physics/runtime solution.
g=coat.vertex_groups.new(name='BW6_Torso_Body_Clearance')
for v in coat.data.vertices:
 if 1.06<v.co.z<1.565 and abs(v.co.x)<.205:
  w=max(0,min(1,(.215-abs(v.co.x))/.035))
  if w:g.add([v.index],w,'REPLACE')
m=coat.modifiers.new('BW6 Local garment outside-body clearance AUTHORING_ONLY','SHRINKWRAP')
m.target=bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody'];m.wrap_method='NEAREST_SURFACEPOINT';m.wrap_mode='OUTSIDE_SURFACE';m.offset=.012;m.vertex_group=g.name
coat['BW6_clearance']='Saddle collar base plus evaluated-space outside-body clearance restricted to torso/neck garment. No rigid-armor shrinkwrap. This is an authoring surface constraint, not simulated collision or certified runtime equivalent.'
out={'method':'Saddle collar control edit plus native localized garment outside constraint after deformation','wrap_modes_available':list(m.bl_rna.properties['wrap_mode'].enum_items.keys()),'group':g.name,'offset_m':m.offset,'modifier_order':[x.type for x in coat.modifiers],'new_collar_ring_count':7,'ring_vertices':n,'changed_vertices':sum(tuple(a)!=tuple(v.co) for a,v in zip(before,coat.data.vertices)),'body_edits':0}
(R/'records/collar_saddle_clearance.json').write_text(json.dumps(out,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_torso_saddle_clearance.blend'))
s.cycles.samples=12;s.render.threads=4
for view in ['front','profile','back','three_quarter']:
 s.camera=bpy.data.objects['BW4_Camera_'+view];s.render.filepath=str(R/'captures'/('saddle_'+view+'.png'));bpy.ops.render.render(write_still=True)
print('BW6_SADDLE_CLEARANCE_RENDERED')
