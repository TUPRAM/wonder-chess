import bpy,json,ast,math,hashlib,sys
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];B=R.parents[1];frozen=R/'ada_bw6_knee_checkpoint_ART_REVISE.blend';source=B/'BW1/r001/ada_body_costume_checkpoint_r003_ART_REVISE.blend';mode=sys.argv[-1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
if mode=='source':
 bpy.ops.wm.open_mainfile(filepath=str(frozen),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;rig=bpy.data.objects['BW6_Knee_Independent_Rig'];owned=json.loads(s['BW6_knee_owned']);controls=[bpy.data.objects[n+'_RigidControl']for n in owned if 'Greave'not in n];cache={}
 for deg in range(121):
  f=1+deg/3;s.frame_set(int(f),subframe=f%1);bpy.context.view_layer.update();cache[deg]=[c.matrix_world.copy()for c in controls]
 s.frame_set(1);rest=rig.matrix_world@rig.pose.bones['upperleg02.R'].matrix
 with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.actions=[n for n in src.actions if n=='BW1_DIAGNOSTIC_RANGE_ART_REVISE']
 assert len(dst.actions)==1;action=dst.actions[0];action=action.copy();action.name='BW6_Knee_BW1_169_PreservedReplay_AUTHORING_ONLY';rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0]
 for c in controls:c.animation_data_clear()
 record={'source':str(source),'source_sha256':sha(source),'frozen_sha256':sha(frozen),'source_action':'BW1_DIAGNOSTIC_RANGE_ART_REVISE','frames':{},'scope':'Actual copied BW1 169-frame authoring action on same verified bind rig. Cup/lames baked from independent control table and actual thigh world delta. Not game clips.'}
 for f in range(1,170):
  s.frame_set(f);bpy.context.view_layer.update();deg=math.degrees(rig.pose.bones['lowerleg01.R'].rotation_euler.x);assert -.001<=deg<=120.001,(f,deg);d=max(0,min(120,deg));a=int(d);b=min(120,a+1);u=d-a;D=rig.matrix_world@rig.pose.bones['upperleg02.R'].matrix@rest.inverted()
  for i,c in enumerate(controls):
   ma,mb=cache[a][i],cache[b][i];loc=ma.translation.lerp(mb.translation,u);q=ma.to_quaternion().slerp(mb.to_quaternion(),u);c.matrix_world=D@Matrix.LocRotScale(loc,q,Vector((1,1,1)));c.keyframe_insert('location',frame=f);c.keyframe_insert('rotation_quaternion',frame=f)
  record['frames'][f]={'knee_degrees':deg,'knee_world':list(rig.matrix_world@rig.pose.bones['lowerleg01.R'].head)}
 s.frame_end=169;s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(R/'ada_bw6_knee_BW1_169_replay_ART_REVISE.blend'));record['replay_sha256']=sha(R/'ada_bw6_knee_BW1_169_replay_ART_REVISE.blend')
 for p,names in [(B/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R.parent/'analysis/inspect_outside_work.py',['geom','screen'])]:
  t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
 others=['BW4_CONTEXT_BW1_IndexedBody','BW4_CONTEXT_BW1_Leggings','BW4_CONTEXT_BW1_Boot_Pair_SourceFit','BW4_CONTEXT_BW1_FootprintSole_R'];summary={}
 for f in range(1,170):
  s.frame_set(f);bpy.context.view_layer.update();g={n:geom(bpy.data.objects[n])for n in owned+others};row={}
  for n in owned:
   checks={n+'__SELF':screen(g[n],g[n],True)}
   for o in others:checks[n+'__'+o]=screen(g[n],g[o])
   row.update({k:{a:b for a,b in v.items() if a!='hits'}for k,v in checks.items()})
  for i,n in enumerate(owned):
   for o in owned[i+1:]:v=screen(g[n],g[o]);row[n+'__'+o]={a:b for a,b in v.items() if a!='hits'}
  summary[f]=row
  if f in [1,49,121,145,157]:
   s.camera=bpy.data.objects['BW6_KneeCamera_three_quarter'];s.render.filepath=str(R/'captures'/f'BW1_source169_context_{f}.png');bpy.ops.render.render(write_still=True)
  if f%20==0:print('SOURCE_MOTION',f,flush=True)
 record['collision']=summary;record['source_sha256_after']=sha(source);(R/'records/BW1_169_replay.json').write_text(json.dumps(record,indent=2))
else:
 bpy.ops.wm.open_mainfile(filepath=str(frozen),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);cam=bpy.data.objects['BW6_KneeCamera_three_quarter'];cam.data=cam.data.copy();cam.location=(1.6,2.2,1.0);target=Vector((.15,-.13,.4));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.12;s.camera=cam;s.render.resolution_x=720;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.frame_start=1;s.frame_end=81;s.render.fps=24
 frames=R/'motion/frames';frames.mkdir(exist_ok=True);s.render.filepath=str(frames/'frame_');bpy.ops.render.render(animation=True,scene=s.name)
 v=bpy.data.scenes.new('BW6_KNEE_VIDEO_TEMP');bpy.context.window.scene=v;v.render.resolution_x=720;v.render.resolution_y=900;v.render.resolution_percentage=100;v.frame_start=1;v.frame_end=81;v.render.fps=24;v.render.image_settings.media_type='VIDEO';v.render.image_settings.file_format='FFMPEG';v.render.ffmpeg.format='MPEG4';v.render.ffmpeg.codec='H264';v.render.ffmpeg.constant_rate_factor='MEDIUM';v.render.ffmpeg.audio_codec='NONE';v.render.filepath=str(R/'motion/BW6_KNEE_ART_REVISE_AUTHORING_ONLY.mp4');v.view_settings.view_transform='Standard';seq=v.sequence_editor_create();st=seq.strips.new_image('Actual rendered frames',str(frames/'frame_0001.png'),channel=1,frame_start=1)
 for f in range(2,82):st.elements.append(f'frame_{f:04}.png')
 bpy.ops.render.render(animation=True,scene=v.name)
 movie=bpy.data.images.load(str(R/'motion/BW6_KNEE_ART_REVISE_AUTHORING_ONLY.mp4'));record={'source_sha256':sha(frozen),'frame_count':len(list(frames.glob('frame_*.png'))),'native_reopened_duration':movie.frame_duration,'native_size':list(movie.size),'source_bound':True,'scope':'81-frame isolated bend/return authoring diagnostic. ART_REVISE, not game or accepted movement.'};assert movie.frame_duration==81;(R/'motion/verification.json').write_text(json.dumps(record,indent=2));print('MOVIE_VERIFIED',record)
