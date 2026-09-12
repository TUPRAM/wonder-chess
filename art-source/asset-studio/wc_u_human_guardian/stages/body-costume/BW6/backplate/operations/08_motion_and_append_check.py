import bpy,json,hashlib,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[1];source=R/'ada_bw6_backplate_checkpoint_REVIEW.blend'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.camera=bpy.data.objects['BW4_Camera_back'];s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='OBJECT';s.display.shading.light='STUDIO';s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100
for ob in s.objects:
 if ob.type=='MESH':ob.color=(.55,.55,.55,1)
motion=R/'motion';frames=motion/'frames';frames.mkdir(parents=True,exist_ok=True);fps=s.render.fps;hashes=[]
for fr in range(1,98):
 s.frame_set(fr);p=frames/f'frame_{fr:04}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);hashes.append({'frame':fr,'path':str(p),'sha256':sha(p)})
video=bpy.data.scenes.new('BW6_BACKPLATE_AUTHORING_97_NOT_GAME');bpy.context.window.scene=video;video.frame_start=1;video.frame_end=97;video.render.resolution_x=800;video.render.resolution_y=800;video.render.resolution_percentage=100;video.render.fps=fps;video.render.image_settings.media_type='VIDEO';video.render.image_settings.file_format='FFMPEG';video.render.ffmpeg.format='MPEG4';video.render.ffmpeg.codec='H264';video.render.ffmpeg.constant_rate_factor='MEDIUM';video.render.ffmpeg.audio_codec='NONE';video.view_settings.view_transform='Standard';video.view_settings.look='None';movie=motion/'BW6_BACKPLATE_97_AUTHORING_ONLY.mp4';video.render.filepath=str(movie)
ed=video.sequence_editor_create();strip=ed.strips.new_image('Actual authoring frames',str(frames/'frame_0001.png'),channel=1,frame_start=1)
for fr in range(2,98):strip.elements.append(f'frame_{fr:04}.png')
label=ed.strips.new_effect('Review scope',type='TEXT',channel=2,frame_start=1,length=97);label.text='BW6 BACKPLATE / LOCAL REVIEW CANDIDATE\nOriginal authoring frames 1-97 / NOT GAME CLIPS\nOther body, costume and shoulders are unchanged context';label.font_size=17;label.location=(.5,.94);label.color=(1,1,1,1);label.use_shadow=True;video.render.use_sequencer=True;bpy.ops.render.render(animation=True,scene=video.name)
moviehash=sha(movie);bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;ed=sc.sequence_editor_create();st=ed.strips.new_movie('Actual movie reopen',str(movie),channel=1,frame_start=1)
assert st.frame_duration==97 and [st.elements[0].orig_width,st.elements[0].orig_height]==[800,800]
decode=motion/'decoded';decode.mkdir(exist_ok=True);sc.render.resolution_x=800;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.use_sequencer=True;sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
for fr in [1,25,49,73,97]:sc.frame_set(fr);sc.render.filepath=str(decode/f'frame_{fr:04}.png');bpy.ops.render.render(write_still=True)
report={'source':str(source),'source_sha256':sha(source),'movie':str(movie),'sha256':moviehash,'frames':97,'fps':fps,'dimensions':[800,800],'native_movie_reopen':True,'native_decoded_frames':[1,25,49,73,97],'geometry_animation':'Existing independent 97-frame authoring action; not game clips','frame_hashes':hashes}
(motion/'verification.json').write_text(json.dumps(report,indent=2))
# Execute the isolated append helper against the original root context without
# writing that source. This confirms one object and its rigid owner are usable.
baseline=R.parent/'armor/ada_bw6_torso_recut_neck.blend';beforehash=sha(baseline);bpy.ops.wm.open_mainfile(filepath=str(baseline),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
spec=importlib.util.spec_from_file_location('bw6_append_backplate',R/'append_backplate.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);res=mod.append_backplate();ob=bpy.data.objects[res['owned'][0]];assert all(m.object==bpy.data.objects['BW4_Armor_Independent_Rig'] for m in ob.modifiers if m.type=='ARMATURE');assert sha(baseline)==beforehash
res.update(baseline=str(baseline),baseline_sha256=beforehash,source_preserved=True,helper_executed=True,assembly_saved=False);(R/'records/append_helper_test.json').write_text(json.dumps(res,indent=2));print('BACKPLATE_MOTION_AND_APPEND_CHECK_OK')
