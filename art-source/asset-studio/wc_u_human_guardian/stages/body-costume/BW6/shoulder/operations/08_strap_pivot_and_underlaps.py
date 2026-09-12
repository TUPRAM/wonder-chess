import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_new_coat_context.blend');rig=bpy.data.objects['BW4_Armor_Independent_Rig'];basis=json.loads((R/'records/initial_construction.json').read_text())['basis'];axis=Vector(basis['axis']);front=Vector(basis['front']);out=Vector(basis['out']);col=bpy.data.collections['BW6_SHOULDER_SUPPORTED_PANELS_AUTHORING_ONLY'];cap=bpy.data.objects['BW6_Pauldron_R_Cap'];h=cap.parent
old_anchor=h.matrix_world.translation.copy();pivot=Vector((.163,-.04636,1.524));anchor=bpy.data.objects.new('BW6_R_Cap_StrapPivot',None);col.objects.link(anchor);anchor.location=pivot;anchor.empty_display_type='SPHERE';anchor.empty_display_size=.012
c=anchor.constraints.new('CHILD_OF');c.target=rig;c.subtarget='shoulder01.R';c.inverse_matrix=(rig.matrix_world@rig.data.bones['shoulder01.R'].matrix_local).inverted();c.set_inverse_pending=False
# Change the mechanical pivot, preserving the exact rest surface in world space.
for v in cap.data.vertices:v.co-=pivot-old_anchor
cap.data.update();loc=h.constraints[0];loc.target=anchor;loc.subtarget='';h.location=pivot
h['BW6_support']='Medial strap pivot above deltoid follows shoulder support; rigid cap swings from that pivot, not the center of the upperarm joint.'
names=json.loads(s['BW6_SHOULDER_HELPERS']);names.append(anchor.name);s['BW6_SHOULDER_HELPERS']=json.dumps(names)
for n,rows in [('Lame1',[(.083,.098,.101,70),(.092,.099,.099,71),(.119,.096,.093,69),(.150,.091,.087,63)]),('Lame2',[(.139,.081,.087,64),(.149,.082,.085,64),(.17,.078,.081,66),(.191,.073,.076,66)])]:
 ob=bpy.data.objects['BW6_Pauldron_R_'+n]
 for i,(u,rw,rv,theta) in enumerate(rows):
  for j in range(13):
   t=(j/12*2-1)*math.radians(theta);v=rv*math.sin(t)*(1.04 if t<0 else .96);w=rw*math.cos(t);ob.data.vertices[i*13+j].co=axis*u+front*v+out*w
 ob.data.update();ob['BW6_revision']='Reconstructed nested anterior/posterior openings and lowest corner; same apex sections, no global growth.'
 c=ob.parent.constraints['Partial arm roll, rigid plate suspension']
 try:c.driver_remove('influence')
 except TypeError:pass
 c.influence=1.0;ob.parent['arm_rotation_influence']=1.0
# Remove old collar diagnostics from the refreshed coat context; new collar belongs to the appended continuous coat.
for o in s.objects:
 if o.type=='MESH' and ('Collar' in o.name or 'collar' in o.name) and o.name!='BW6_PaddedCoat_Tailored':o.hide_render=True;o.hide_set(True)
s['BW6_SHOULDER_STATUS']='CORRECTION2_PENDING_REVIEW';s.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_shoulder_correction2.blend'))
(R/'records/correction2_mechanism.json').write_text(json.dumps({'cap_pivot_world_m':list(pivot),'cap_rest_world_surface_preserved':True,'cap_rotation':'Native shoulder-delta / arm-delta interpolation remains, around relocated fixed shoulder-strap pivot.','lames':'Rigid full upperarm rest-relative tracking; nested front/rear borders reconstructed.','basis':basis,'guardrails':'No original rig/bone/action/coat/sleeve modifications.'},indent=2))
