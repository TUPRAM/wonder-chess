import bpy,json,ast,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];B=R.parents[1];frozen=R/'ada_bw6_knee_checkpoint_ART_REVISE.blend';baseline=B/'BW5/armor/ada_bw5_armor_checkpoint_r003_ART_REVISE.blend'
for p,names in [(B/'BW2/r001/integrated-independent/audit_integrated_geometry.py',['segment_triangle']),(R.parent/'analysis/inspect_outside_work.py',['geom','screen'])]:
 t=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
bpy.ops.wm.open_mainfile(filepath=str(frozen),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;cameras={v:{'matrix':[list(r)for r in bpy.data.objects['BW6_KneeCamera_'+v].matrix_world],'ortho':bpy.data.objects['BW6_KneeCamera_'+v].data.ortho_scale}for v in ['front','profile','three_quarter']};out={'baseline_checks':{},'sections':{},'camera_spec':cameras,'scope':'Matched new construction cameras; baseline posed to same isolated leg angles. Sections are exact evaluated triangle-plane segments in world coordinates, not a proposed outline.'}
for label,path in [('candidate',frozen),('baseline',baseline)]:
 bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False,load_ui=False);s=bpy.data.scenes['BW4_ARMOR_LOCAL_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1);rig=bpy.data.objects['BW6_Knee_Independent_Rig'if label=='candidate'else'BW4_Armor_Independent_Rig']
 if label=='baseline':
  rig.animation_data_clear()
  for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
  allow=['BW4_CONTEXT_BW1_IndexedBody','BW4_CONTEXT_BW1_Leggings','BW4_CONTEXT_BW1_KneeCup_R_ThighAttachment','BW4_CONTEXT_BW1_KneeCup_ThighStrap_R','BW4_CONTEXT_BW1_Greave_R','BW4_CONTEXT_BW1_Boot_Pair_SourceFit','BW4_CONTEXT_BW1_FootprintSole_R','BW4_CONTEXT_BW1_BootVampStrap_R']
  for o in s.objects:
   if o.type=='MESH':o.hide_render=o.name not in allow;o.color=(.52,.56,.6,1) if 'Knee' in o.name or 'Greave' in o.name else(.24,.25,.26,1)
  for v,spec in cameras.items():
   d=bpy.data.cameras.new('BW6_Matched_'+v);o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.matrix_world=Matrix(spec['matrix']);d.type='ORTHO';d.ortho_scale=spec['ortho']
 s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=850;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.display.shading.color_type='OBJECT';s.display.shading.light='STUDIO';s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.show_shadows=True;s.display.shading.background_type='WORLD';s.world.color=(.07,.07,.07);s.view_settings.view_transform='Standard'
 for deg in [0,30,60,90,120]:
  if label=='candidate':s.frame_set(1+deg//3)
  else:rig.pose.bones['lowerleg01.R'].rotation_mode='XYZ';rig.pose.bones['lowerleg01.R'].rotation_euler.x=math.radians(deg)
  bpy.context.view_layer.update();kn=rig.matrix_world@rig.pose.bones['lowerleg01.R'].head
  if label=='baseline':
   g=geom(bpy.data.objects['BW4_CONTEXT_BW1_Greave_R']);out['baseline_checks'][deg]={'greave_SELF':screen(g,g,True),'greave_BODY':screen(g,geom(bpy.data.objects['BW4_CONTEXT_BW1_IndexedBody'])),'greave_LEGGINGS':screen(g,geom(bpy.data.objects['BW4_CONTEXT_BW1_Leggings'])),'greave_BOOT':screen(g,geom(bpy.data.objects['BW4_CONTEXT_BW1_Boot_Pair_SourceFit']))}
  if deg in [0,90]:
   names=['BW4_CONTEXT_BW1_IndexedBody','BW4_CONTEXT_BW1_Leggings']+(json.loads(s['BW6_knee_owned'])if label=='candidate'else['BW4_CONTEXT_BW1_KneeCup_R_ThighAttachment','BW4_CONTEXT_BW1_Greave_R']);sec={'knee':list(kn),'plane_world_x':kn.x,'surfaces':{}}
   for name in names:
    pts,tris,tree,groups=geom(bpy.data.objects[name]);segments=[]
    for tri in tris:
     vs=pts[list(tri)];hits=[]
     for a,b in [(vs[i],vs[(i+1)%3])for i in range(3)]:
      if (a[0]-kn.x)*(b[0]-kn.x)<0:
       h=a+(b-a)*((kn.x-a[0])/(b[0]-a[0]));hits.append(h.tolist())
     if len(hits)==2 and any(abs(h[2]-kn.z)<.17 and abs(h[1]-kn.y)<.22 for h in hits):segments.append(hits)
    sec['surfaces'][name]=segments
   out['sections'][label+'_'+str(deg)]=sec
   if label=='baseline':
    for v in ['profile','three_quarter']:
     s.camera=bpy.data.objects['BW6_Matched_'+v];s.render.filepath=str(R/'captures'/f'baseline_{v}_{deg}.png');bpy.ops.render.render(write_still=True)
(R/'records/baseline_sections.json').write_text(json.dumps(out,indent=2));print('BASELINE_SECTIONS_DONE')
