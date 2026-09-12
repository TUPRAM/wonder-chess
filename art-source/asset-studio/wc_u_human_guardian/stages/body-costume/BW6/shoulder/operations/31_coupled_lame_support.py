import bpy,sys,json
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_checkpoint_r002_LOCAL_REVIEW.blend');cap=bpy.data.objects['BW6_Pauldron_R_Cap'];rig=bpy.data.objects['BW4_Armor_Independent_Rig'];col=bpy.data.collections['BW6_SHOULDER_SUPPORTED_PANELS_AUTHORING_ONLY'];anchor=rig.matrix_world@rig.data.bones['upperarm01.R'].head_local
follow=bpy.data.objects.new('BW6_R_CapRelative_LameAnchor',None);col.objects.link(follow);follow.matrix_world=Matrix.Translation(anchor);follow.empty_display_type='SPHERE';follow.empty_display_size=.016
c=follow.constraints.new('CHILD_OF');c.name='Rest-corrected cap-relative suspension anchor';c.target=cap;c.inverse_matrix=cap.matrix_world.inverted();c.set_inverse_pending=False
for n,amount in [('Lame1',.85),('Lame2',.50)]:
 h=bpy.data.objects['BW6_Pauldron_R_'+n+'_Suspension'];c=h.constraints.new('COPY_TRANSFORMS');c.name='Coupled rigid cap/arm suspension';c.target=follow;c.mix_mode='REPLACE';c.target_space='WORLD';c.owner_space='WORLD';c.influence=amount
 h['BW6_coupling']='Rigid rest-relative anchor/rotation blend between supported cap and arm. Relative attachment travel must be measured; no vertex deformation.';h['BW6_cap_follow']=amount
names=json.loads(s['BW6_SHOULDER_HELPERS']);names.append(follow.name);s['BW6_SHOULDER_HELPERS']=json.dumps(names);s['BW6_SHOULDER_STATUS']='COUPLED_SUPPORT_PENDING_REVIEW';bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_shoulder_coupled_support.blend'))
