import bpy,sys,json
from pathlib import Path
root=Path(r"C:/Users/iputu/Documents/Wonder Chess")
sys.path.insert(0,str(root/"tools/blender"))
from refine_update_dwarves import weapon_pose,use_clip
u=next(u for u in json.loads((root/"data/units.json").read_text())["units"] if u["id"]=="wc_u_dwarf_warrior")
arm=bpy.data.objects["Armature"]
for clip,end,release in [("Attack",46,22),("Active",43,25)]:
 use_clip(arm,clip,unit_id=u["id"])
 results=[]
 for frame in range(1,end+1):
  bpy.context.scene.frame_set(frame)
  error=weapon_pose(u,arm,clip,frame,end,release)
  results.append((frame,error,list(arm.pose.bones["hand_r"].tail),list(arm.pose.bones["hand_l"].tail)))
 print(clip,sorted(results,key=lambda x:-x[1])[:7],flush=True)
