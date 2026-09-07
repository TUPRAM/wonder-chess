"""Actual Blender readback: source invariants, exported bytes, video timing and silhouettes."""
import bpy,hashlib,json,sys
from pathlib import Path
ROOT=Path(r"C:/Users/iputu/Documents/Wonder Chess")
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"tools/blender"))
from refine_update_ada import invariants,action_curve_digest,use_clip
from refine_update_dwarves import camera_view
ids=("wc_u_dwarf_guardian","wc_u_dwarf_ranger","wc_u_dwarf_warrior")
units={u["id"]:u for u in json.loads((ROOT/"data/units.json").read_text())["units"]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
errors=[];records=[];videos=[]
for uid in ids:
 out=OUT/uid;original=out/"before-source.blend"
 if not original.exists():original=Path(json.loads((out/"geometry-input.json").read_text())["retained_geometry_evidence"])/"before-source.blend"
 before=json.loads((out/"before-export-manifest.json").read_text())
 if sha(original)!=before["source_sha256"]:errors.append(uid+" preserved revision6 hash mismatch")
 bpy.ops.wm.open_mainfile(filepath=str(original));arm=bpy.data.objects["Armature"]
 prior_rest=invariants(arm)["rest_skeleton_sha256"]
 protected={clip:action_curve_digest(bpy.data.actions[before["clips"][clip]["action"]]) for clip in ("Idle","Move","Hit","Defeat","Victory")}
 source=ROOT/"art-source/heroes"/uid/(uid+".blend");export=ROOT/"exports/heroes"/uid
 manifest=json.loads((export/"export_manifest.json").read_text())
 bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects["Armature"]
 if invariants(arm)["rest_skeleton_sha256"]!=prior_rest:errors.append(uid+" rest skeleton changed")
 if sha(source)!=manifest["source_sha256"]:errors.append(uid+" current source hash mismatch")
 for clip,expected in protected.items():
  if action_curve_digest(bpy.data.actions[before["clips"][clip]["action"]])!=expected:errors.append(uid+" unexpected changed clip "+clip)
 for filename,expected in manifest["files"].items():
  if sha(export/filename)!=expected:errors.append(uid+" export hash mismatch "+filename)
 for clip,spec in manifest["clips"].items():
  path=out/("continuous_"+clip+".mp4");video=bpy.data.movieclips.load(str(path))
  record={"unit_id":uid,"clip":clip,"fps":video.fps,"frames":video.frame_duration,"dimensions":list(video.size),"sha256":sha(path)}
  videos.append(record)
  if video.fps!=60 or video.frame_duration!=spec["frames"][1]-spec["frames"][0]+1 or list(video.size)!=[384,384]:errors.append(uid+" video metadata mismatch "+clip)
  bpy.data.movieclips.remove(video)
 mesh=bpy.data.objects["SK_"+uid]
 mesh.data.calc_loop_triangles()
 records.append({"unit_id":uid,"source_revision":manifest["source_revision"],"source_sha256":sha(source),"manifest_sha256":sha(export/"export_manifest.json"),"triangles":len(mesh.data.loop_triangles),"rest_skeleton_sha256":prior_rest,"unchanged_clip_sha256":protected,"animation_changes":["Attack","Active"],"unit_scale_m":bpy.context.scene.unit_settings.scale_length,"materials":len(mesh.material_slots),"uv_layers":len(mesh.data.uv_layers),"bones":len(arm.data.bones)})
 use_clip(arm,"Idle",unit_id=uid)
 for view in ("front","game-angle"):
  scene=bpy.context.scene;camera_view(units[uid],view,96)
  scene.render.engine="BLENDER_WORKBENCH";scene.view_settings.view_transform="Standard"
  scene.display.shading.light="FLAT";scene.display.shading.color_type="SINGLE"
  scene.display.shading.single_color=(.02,.02,.02);scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=False
  scene.display.shading.background_type="WORLD";scene.world.color=(1,1,1)
  bpy.data.objects["PRESENTATION_Ground"].hide_render=True
  scene.render.filepath=str(out/("silhouette96_"+view+".png"));bpy.ops.render.render(write_still=True)
summary={"status":"PASS_SOURCE_EXPORT_VIDEO_READBACK" if not errors else "FAIL","blender_version":bpy.app.version_string,"heroes":records,"recordings":videos,"recorded_frames":sum(x["frames"] for x in videos),"recorded_duration_seconds":sum(x["frames"]/x["fps"] for x in videos),"errors":errors,"limits":["Metadata and numeric checks are not continuous visual review or finished-art acceptance.","No current Unreal import/reimport, gallery, both team orientations, busy combat, LOD or audio synchronization approval.","Actual Workbench videos are darker than the Cycles material stills; judge final material response in Unreal."]}
(OUT/"source-export-video-validation.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps({k:v for k,v in summary.items() if k not in ("heroes","recordings")},indent=2))
if errors:raise RuntimeError("; ".join(errors))
