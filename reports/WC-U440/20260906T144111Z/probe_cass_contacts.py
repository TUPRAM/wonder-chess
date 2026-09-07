import sys,json
from pathlib import Path
import bpy
ROOT=Path('C:/Users/iputu/Documents/Wonder Chess');sys.path.insert(0,str(ROOT/'tools/blender'))
import author_update_four as a
from author_alpha import rig_for,animate
u=next(x for x in json.loads((ROOT/'data/units.json').read_text())['units'] if x['id']=='wc_u_human_warrior')
bpy.ops.wm.read_factory_settings(use_empty=True);arm,p=rig_for(u);clips=animate(u,arm,ROOT,export_animation=False)
original=a.place_hand
def probe(arm,side,palm,rotation,height):
    result=original(arm,side,palm,rotation,height);print('CONTACT',side,'palm',list(palm),'shoulder',list(arm.pose.bones['upperarm_'+side].head),'actualpalm',list(arm.pose.bones['hand_'+side].tail),'clamp',result);return result
a.place_hand=probe
act=bpy.data.actions[clips['Defeat']['action']];arm.animation_data.action=act;arm.animation_data.action_slot=act.slots[0]
for frame in (1,7,16,31,46,61):bpy.context.scene.frame_set(frame);print('FRAME',frame);a.contacts(u,arm,'Defeat',frame,60,1)
