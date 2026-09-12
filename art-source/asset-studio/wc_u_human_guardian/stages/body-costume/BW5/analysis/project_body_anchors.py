import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).parent;source=R.parent/'armor/ada_bw5_armor_checkpoint_ART_REVISE.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW5_REFERENCE_POSE_APPROXIMATE'];bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW5_ReferencePose_Rig'];cam=bpy.data.objects['BW5_Reference_front'];s.camera=cam
cl=(rig.matrix_world@rig.pose.bones['clavicle.R'].head+rig.matrix_world@rig.pose.bones['clavicle.L'].head)/2;waist=rig.matrix_world@rig.pose.bones['spine03'].head
def proj(p):
 q=world_to_camera_view(s,cam,p);return [q.x*960,(1-q.y)*960]
anchors={'clavicle_midpoint':{'world_m':list(cl),'render_px':proj(cl),'reference_proxy_px':[255,214],'reference_uncertainty_px':[5,12],'reference_visibility':'Occluded by collar; inferred anatomical placement, not a measured bone in the artwork.'},'natural_waist_spine03_head':{'world_m':list(waist),'render_px':proj(waist),'reference_proxy_px':[255,350],'reference_uncertainty_px':[5,8],'reference_visibility':'Occluded by belt/underlayer; inferred natural-waist placement, not a measured bone in the artwork.'}}
a,b=anchors.values();scale=(b['reference_proxy_px'][1]-a['reference_proxy_px'][1])/(b['render_px'][1]-a['render_px'][1]);tx=sum(x['reference_proxy_px'][0]-scale*x['render_px'][0] for x in anchors.values())/2;ty=a['reference_proxy_px'][1]-scale*a['render_px'][1]
out={'source_blend':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scene':s.name,'frame':1,'camera':cam.name,'camera_world_matrix':[list(x) for x in cam.matrix_world],'resolution':[960,960],'ortho_scale_m':cam.data.ortho_scale,'anchors':anchors,'uniform_model_to_reference_transform':{'scale_xy_same':scale,'translation_px':[tx,ty],'rotation_degrees':0},'scale_uncertainty_interval_from_proxy_vertical_allowances':[(136-20)/(b['render_px'][1]-a['render_px'][1]),(136+20)/(b['render_px'][1]-a['render_px'][1])],'policy':'One uniform image scale and translation, chosen from occluded body-landmark proxies. No plate corner is used to register. The residual artwork perspective and proxy uncertainty prevent exact silhouette matching or likeness scoring. The upper arm pose is approximate; not a changed shared rest pose.'}
(R/'registration_body_anchors.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
