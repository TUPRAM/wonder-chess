"""Render labelled sparse poses from saved sources, never a continuous acceptance claim."""
import bpy
import json
from pathlib import Path

ROOT=Path(r'C:/Users/iputu/Documents/Wonder Chess')
REPORT=Path(__file__).resolve().parent/'pose-samples'
REPORT.mkdir(exist_ok=True)
records=[]
for out in sorted((ROOT/'exports/neutrals').glob('wc_n_*')):
    manifest=json.loads((out/'export_manifest.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art-source/neutrals'/out.name/(out.name+'.blend')))
    scene=bpy.context.scene
    scene.render.engine='BLENDER_WORKBENCH'
    scene.display.shading.light='STUDIO'
    scene.display.shading.color_type='TEXTURE'
    scene.display.shading.show_shadows=True
    scene.display.shading.show_cavity=True
    scene.render.image_settings.media_type='IMAGE'
    scene.render.image_settings.file_format='PNG'
    scene.render.resolution_x=240
    scene.render.resolution_y=240
    arm=bpy.data.objects['Armature']
    for name,clip in manifest['clips'].items():
        action=bpy.data.actions[clip['action']]
        arm.animation_data.action=action
        arm.animation_data.action_slot=action.slots[0]
        end=clip['frames'][1]
        release=clip['release_frame']
        frames=([1,max(1,release-1),release,round((release+end)/2),end]
                if release else [1,1+round((end-1)*.25),1+round((end-1)*.5),1+round((end-1)*.75),end])
        for column,frame in enumerate(frames):
            scene.frame_set(frame)
            path=REPORT/(out.name+'_'+name+'_'+str(column)+'.png')
            scene.render.filepath=str(path)
            bpy.ops.render.render(write_still=True)
            records.append({'creature':out.name,'clip':name,'column':column,'frame':frame,'path':str(path)})
(REPORT/'index.json').write_text(json.dumps(records,indent=2)+'\n')
print('WC_NEUTRAL_SPARSE_POSES '+str(len(records)))
