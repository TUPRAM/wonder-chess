"""Execute gameplay-safe framing and a whole-courtyard inspection render."""
import bpy
from mathutils import Vector
from pathlib import Path
import json
root=Path(__file__).resolve().parents[2]
sc=bpy.context.scene;cam=sc.camera
cam.location=(0,22,25.5);cam.rotation_euler=(Vector((0,1.5,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=34
for w,h in ((1920,1080),(1280,720)):
    sc.render.resolution_x=w;sc.render.resolution_y=h;sc.render.filepath=str(root/f'reports/WC-330/arena/courtyard_{w}x{h}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
manifest=root/'exports/arena/arena_manifest.json';record=json.loads(manifest.read_text());record['camera'].update({'location_m':list(cam.location),'target_m':[0,1.5,0],'ortho_width_m':34});manifest.write_text(json.dumps(record,indent=2)+'\n')
cam.location=(21,29,24);cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=39
sc.render.resolution_x=1600;sc.render.resolution_y=1000;sc.render.filepath=str(root/'reports/WC-330/arena/courtyard_three_quarter.png');bpy.ops.render.render(write_still=True)
