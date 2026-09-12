import bpy,bmesh,math,json,ast,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];source=R/'ada_bw6_bracer_initial.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.data.scenes['BW6_RIGHT_BRACER_AUTHORING_ONLY'];bpy.context.window.scene=s;s.frame_set(1)
rig=bpy.data.objects['BW6_Bracer_Independent_Rig'];col=bpy.data.collections['BW6_BRACER_NEW_CONSTRUCTION'];owned=[bpy.data.objects[n] for n in json.loads(s['BW6_bracer_owned'])]
frame=json.loads(s['BW6_bracer_frame']);W=Vector(frame['wrist']);A=Vector(frame['proximal']);D=Vector(frame['dorsal']);T=Vector(frame['transverse'])
ctx=[bpy.data.objects[n] for n in json.loads(s['BW6_bracer_context'])]
body=next(o for o in ctx if o.name.endswith('IndexedBody'));coat=next(o for o in ctx if o.name.endswith('CoatUpper_Continuous'));glove=next(o for o in ctx if o.name.endswith('Glove_Pair_SourceFit'))
p=R/'operations/02_construct.py';tree=ast.parse(p.read_text());names=['bvh','radial','create','grid_surface','underlying','field']
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),globals())
bvs={'body':bvh(body),'padded_sleeve':bvh(coat),'unchanged_glove':bvh(glove)}
leather=bpy.data.materials['BW6_Bracer_Leather_Preview'];steel=bpy.data.materials['BW6_Bracer_Steel_Preview']
for nm in ['BW6_R_Bracer_VolarLeather','BW6_R_Bracer_WristCuff','BW6_R_Bracer_WristRim','BW6_R_Bracer_ElbowRim']:
 o=bpy.data.objects[nm];o.hide_render=True;o.hide_set(True);owned.remove(o);o['status']='RETAINED_INITIAL_INTERFACE_FAILURE'
shell=bpy.data.objects['BW6_R_Bracer_DorsalShell'];N=17
for v in shell.data.vertices:
 q=v.co-W;t=q.dot(A);rad=q-A*t;a=math.atan2(rad.dot(T),rad.dot(D))
 if abs(a)<math.radians(70):v.co+=D*(.0045*max(0,1-abs(a)/math.radians(70)))
crease=shell.data.attributes.new('crease_edge','FLOAT','EDGE')
for e in shell.data.edges:
 if all(i%N==8 for i in e.vertices):crease.data[e.index].value=.62
shell.data.update();shell['method_correction']='Local axial dorsal crest, controlled broad side planes; separate intersecting raised rims rejected, existing physical wall and selective bevel retained.'
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def lining_radius(t,a):
 allowance=.0015+.002*smooth((t-.008)/.018)
 return field(t,a)-allowance
lining=grid_surface('BW6_R_Bracer_LeatherCuffAndLining',[.001,.003,.008,.014,.021,.026,.035,.06,.095,.135,.173,.177],list(range(-180,181,12)),lining_radius,leather,.0012,.0004,1)
# Weld the intentionally closed angular seam before subdivision/solidify.
bm=bmesh.new();bm.from_mesh(lining.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(lining.data);bm.free();lining.data.update()
fore=lining.vertex_groups.get('lowerarm02.R');wrist=lining.vertex_groups.new(name='wrist.R')
for v in lining.data.vertices:
 t=(v.co-W).dot(A);w=1-smooth((t-.007)/.024)
 fore.add([v.index],1-w,'REPLACE');wrist.add([v.index],w,'REPLACE')
lining['owner_bone']='wrist.R at cuff edge; smooth transition to lowerarm02.R by 31mm proximal'
lining['construction']='One continuous leather cuff and lining with closed angular seam, independent of glove; replaces crossing cuff/volar overlap surfaces.'
s['BW6_bracer_owned']=json.dumps([o.name for o in owned]);s['revision']='one substantive correction: interface reconstruction and shell crest'
# Preserve full native context. Only temporary display masks below limit images to the forearm study.
s.view_settings.exposure=-1.3;s.camera=bpy.data.objects['BW6_Bracer_Camera_ThreeQuarter']
outpath=R/'ada_bw6_bracer_correction1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(outpath))
for o in ctx:
 vg=o.vertex_groups.new(name='BW6_DIAGNOSTIC_FOREARM_VIEW_ONLY')
 for v in o.data.vertices:
  q=o.matrix_world@v.co-W;t=q.dot(A);r=(q-A*t).length
  if -.22<t<.29 and r<.145:vg.add([v.index],1,'REPLACE')
 m=o.modifiers.new('Temporary forearm image isolation; not saved','MASK');m.vertex_group=vg.name
for label in ['dorsal','volar','side','three_quarter','axial']:
 camname={'dorsal':'Dorsal','volar':'Volar','side':'Side','three_quarter':'ThreeQuarter','axial':'Axial'}[label]
 s.camera=bpy.data.objects['BW6_Bracer_Camera_'+camname];s.render.filepath=str(R/'captures'/('r001_isolated_'+label+'.png'));bpy.ops.render.render(write_still=True)
(R/'records/correction1.json').write_text(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidate':str(outpath),'owned':[o.name for o in owned],'edits':['New continuous closed-seam cuff/lining, replacing intersecting leather overlap','Local dorsal crest and controlled side-plane transition','Rejected separate rims that crossed source metal edge','Cuff-only wrist to forearm weights; no body/glove/rig/action change'],'render_context':'Forearm-only temporary display mask on unchanged source context, added after blend save. Full context remains in native file.'},indent=2))
print('CORRECTION1_DONE')
