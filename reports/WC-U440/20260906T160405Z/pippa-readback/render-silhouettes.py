"""Read-only source render of final Pippa LOD0 at the required96-pixel scale."""
import bpy,hashlib,json,sys
from pathlib import Path
ROOT=Path(r'C:/Users/iputu/Documents/Wonder Chess')
sys.path.insert(0,str(ROOT/'tools/blender'))
from author_update_pippa import camera_view,use_clip
UID='wc_u_halfling_warrior';OUT=Path(__file__).resolve().parent
source=ROOT/'art-source/heroes'/UID/(UID+'.blend')
before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
manifest=json.loads((ROOT/'exports/heroes'/UID/'export_manifest.json').read_text())
unit=next(row for row in json.loads((ROOT/'data/units.json').read_text())['units'] if row['id']==UID)
scene=bpy.context.scene;use_clip(bpy.data.objects['Armature'],manifest['clips']['Idle'])
scene.render.engine='BLENDER_WORKBENCH';scene.view_settings.view_transform='Standard'
scene.render.resolution_x=scene.render.resolution_y=96;scene.render.resolution_percentage=100
scene.display.shading.light='FLAT';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.02,.02,.02)
scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=False
scene.display.shading.background_type='WORLD';scene.world.color=(1,1,1)
bpy.data.objects['PRESENTATION_Ground'].hide_render=True
for view in ('front','game-angle'):
    camera_view(unit,view);scene.render.filepath=str(OUT/('silhouette96-'+view+'.png'))
    bpy.ops.render.render(write_still=True)
assert before==hashlib.sha256(source.read_bytes()).hexdigest()
print('PIPPA_SILHOUETTES_SOURCE_UNCHANGED '+before,flush=True)
