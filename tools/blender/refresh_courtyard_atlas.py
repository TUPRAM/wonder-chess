"""Correct file-texture color decoding in the actual authored courtyard source."""
import sys
from pathlib import Path
import json
import hashlib
import shutil
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from author_alpha import material_for,ROOT
out=ROOT/'exports/arena'
unit={'id':'wc_seven_lantern_courtyard','art':{'palette':'#C8B891 #E7DAB9 #375B86 #765A3E #A1AAB0 #685137 #637B4C #405B40 #EDE1C5 #283B50 #CBA65D #8FBDCD #EFAE63 #857592 #BCAA87 #B87B60'}}
mat=material_for(unit,out)
for ob in bpy.data.objects:
    if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(mat)
for folder in out.glob('*.fbm'):
    for file in out.glob('T_*.png'):shutil.copy2(file,folder/file.name)
print('WC_ARENA_TEXTURES_STABLE',flush=True)
sc=bpy.context.scene
for w,h in ((1920,1080),(1280,720)):
    sc.render.resolution_x=w;sc.render.resolution_y=h;sc.render.filepath=str(ROOT/f'reports/WC-330/arena/courtyard_{w}x{h}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
manifest=out/'arena_manifest.json';record=json.loads(manifest.read_text());record['texture_revision']=3
record['source_sha256']=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
record['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.name!='arena_manifest.json'}
manifest.write_text(json.dumps(record,indent=2)+'\n')
sc.camera.location=(21,29,24);sc.camera.rotation_euler=(Vector((0,0,1))-sc.camera.location).to_track_quat('-Z','Y').to_euler();sc.camera.data.ortho_scale=39
sc.render.resolution_x=1600;sc.render.resolution_y=1000;sc.render.filepath=str(ROOT/'reports/WC-330/arena/courtyard_three_quarter.png');bpy.ops.render.render(write_still=True)
print('WC_ARENA_TEXTURE_REVIEW_COMPLETE',flush=True)
