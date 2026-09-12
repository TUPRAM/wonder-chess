import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(__file__).resolve().parents[1]
d=json.loads((OUT/'records/open_glove_geometry.json').read_text())
equipment=json.loads((OUT/'reviews/contract/actual_hilt_and_bind.json').read_text())
proposal=json.loads((OUT/'reviews/contract/hilt_proposal_geometry.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.name='BW4_FIXED_CLOSED_LOCAL'
source=[Vector(v) for v in d['vertices_m']]
joints=d['joints'];points={n:[Vector(joints[f'finger{n}-{j}.R']['head']) for j in (1,2,3)]+[Vector(joints[f'finger{n}-3.R']['tail'])] for n in range(1,6)}
def closest(v,pp):
 best=None;acc=0
 for a,b in zip(pp,pp[1:]):
  t=(b-a).normalized();ln=(b-a).length;u=max(0,min(ln,(v-a).dot(t)));q=a+t*u
  score=(v-q).length_squared
  if best is None or score<best[0]:best=(score,acc+u,q,t)
  acc+=ln
 return best[1:]
def smooth(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
def frame(t):
 xx=Vector((1,0,0));xx=(xx-t*xx.dot(t)).normalized();zz=xx.cross(t).normalized();return xx,zz
def palm(v):
 q=v.copy();q.z+=.006*math.exp(-((q.x+.006)/.042)**2-((q.y-.076)/.041)**2)
 return q
# Four digit centerline arcs are fitted to the selected octagonal grip. Their
# existing cross-sections, tips and knuckle topology come from the source glove.
layouts={2:(.027,.024,-65),3:(.003,.025,-66),4:(-.019,.0235,-65),5:(-.039,.021,-57)}
thumbpath=[Vector(p) for p in [( .025,.038,.006),(.043,.053,.031),(.046,.066,.054),(.015,.061,.027)]]
thumb_old_length=sum((b-a).length for a,b in zip(points[1],points[1][1:]))
thumb_new_length=sum((b-a).length for a,b in zip(thumbpath,thumbpath[1:]))
def sample_path(pp,along):
 for a,b in zip(pp,pp[1:]):
  ln=(b-a).length
  if along<=ln:return a+(b-a)*max(0,along/ln),(b-a).normalized()
  along-=ln
 return pp[-1],(pp[-1]-pp[-2]).normalized()
verts=[];roles=[];padids={str(n):[] for n in range(1,6)}
for i,(v,w) in enumerate(zip(source,d['weights'])):
 fam={n:sum(w.get(f'finger{n}-{j}.R',0) for j in (1,2,3)) for n in range(1,6)}
 n=max(fam,key=fam.get);q=palm(v);roles.append(n if fam[n]>.15 else 0)
 if fam[n]>.02:
  along,oldc,oldt=closest(v,points[n]);xx,zz=frame(oldt);off=v-oldc;dx=off.dot(xx);dz=off.dot(zz)
  if n==1:
   nc,nt=sample_path(thumbpath,along*thumb_new_length/thumb_old_length)
   # Thumb palmar side rotates independently toward the hilt's opposing side.
   nz=Vector((0,1,0));nz=(nz-nt*nz.dot(nt)).normalized();nx=nt.cross(nz).normalized()
   nq=nc+nx*dx+nz*dz
  else:
   xc,rad,start=layouts[n];ang=math.radians(start)+along/rad
   nc=Vector((xc,.085+rad*math.cos(ang),.032+rad*math.sin(ang)))
   nz=Vector((0,-math.cos(ang),-math.sin(ang)));nq=nc+Vector((dx,0,0))+nz*dz
  amount=smooth(fam[n]/.75)
  q=q.lerp(nq,amount)
  if w.get(f'finger{n}-3.R',0)>.55 and dz>.002:padids[str(n)].append(i)
 verts.append(tuple(q))
def meshob(name,v,f):
 me=bpy.data.meshes.new(name+'_Surface');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);return o
o=meshob('BW4_ClosedGlove_Initial',verts,d['faces'])
for k,ids in padids.items():
 vg=o.vertex_groups.new(name='CONTACT_'+k+'_predeclared_from_open');vg.add(ids,1,'REPLACE')
# Replace a local thumb-root transition patch on each side. Old edges inside
# this patch are removed; a new distributed triangulated control surface is
# built against its preserved boundary, then made quad-dominant by edge joins.
bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
patch=[f for f in bm.faces if .022<sum(source[v.index].x for v in f.verts)/len(f.verts)<.046 and .052<sum(source[v.index].y for v in f.verts)/len(f.verts)<.082]
edges={e for f in patch for e in f.edges};boundary=[e for e in edges if sum(f in patch for f in e.link_faces)==1]
oldpatch=len(patch)
bmesh.ops.delete(bm,geom=patch,context='FACES_ONLY')
loose=[e for e in bm.edges if not e.link_faces and e not in boundary]
if loose:bmesh.ops.delete(bm,geom=loose,context='EDGES')
newfaces=bmesh.ops.holes_fill(bm,edges=[e for e in boundary if e.is_valid],sides=0)['faces']
newtris=bmesh.ops.triangulate(bm,faces=newfaces)['faces']
joined=bmesh.ops.join_triangles(bm,faces=list(newtris),angle_face_threshold=3.14,angle_shape_threshold=3.14)
newfaces=[f for f in bm.faces if f in joined.get('faces',[])]
localedges=list({e for f in newfaces for e in f.edges if len(e.link_faces)==2 and all(ff in newfaces for ff in e.link_faces)})
if localedges:bmesh.ops.subdivide_edges(bm,edges=localedges,cuts=1,use_grid_fill=True)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
for p in o.data.polygons:p.use_smooth=True
sub=o.modifiers.new('Source level 1 surface review','SUBSURF');sub.levels=1;sub.render_levels=1
o['representation']='Closed visible glove only, CC0 toigo adaptation; no claim bare hand repaired'
o['method']='Direct source-section remapping and replaced local web topology; no live digit rig'
o['human_forms_approval']='NOT_ISSUED'
def swordcoord(v):
 # Single local rigid placement, selected geometry unchanged. Canonical Z ->
 # anatomical transverse X, canonical X -> distal Y, canonical Y -> palmar Z.
 return (v[2]-.8098999857902527+.059, v[0]+.5824000239372253+.085,v[1]-.10010000318288803+.032)
sword=[]
for p in equipment['sword_components']:
 part=p['identified_part'];v=proposal['proposed']['world_vertices_m'] if part=='handle' else p['world_vertices_m']
 ob=meshob('BW4_SelectedSword_'+part,[swordcoord(q) for q in v],p['faces']);ob.color=(.26,.20,.12,1) if part=='handle' else (.5,.48,.40,1);sword.append(ob)
original=meshob('BW4_OpenReference_HIDDEN',d['vertices_m'],d['faces']);original.hide_render=True;original.hide_set(True)
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='OBJECT';o.color=(.55,.53,.50,1);s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH'
s.world=bpy.data.worlds.new('BW4_ReviewWorld');s.world.color=(.075,.075,.075);s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard';s.view_settings.look='None'
for name,pos in [('palm',(.04,.04,.55)),('dorsal',(0,.06,-.55)),('side',(.55,.08,.07)),('underside',(-.04,-.45,.16)),('oblique',(.30,.35,.45)),('axial',(-.5,.085,.05))]:
 cd=bpy.data.cameras.new('BW4_'+name);c=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector((0,.059,.02))-c.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=.255;s.camera=c;s.render.filepath=str(OUT/'captures'/('initial_'+name+'.png'));bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['BW4_oblique'];sword[2].hide_render=True
for ob in sword:ob.hide_render=True
s.render.filepath=str(OUT/'captures/initial_handle_hidden.png');bpy.ops.render.render(write_still=True)
sub.show_render=False
wire=o.modifiers.new('Actual cage diagnostic','WIREFRAME');wire.thickness=.00032;wire.use_replace=False;s.render.filepath=str(OUT/'captures/initial_cage.png');bpy.ops.render.render(write_still=True);o.modifiers.remove(wire);sub.show_render=True
for ob in sword:ob.hide_render=False
s.camera=bpy.data.objects['BW4_oblique']
s['BW4_scope']='INITIAL_FIXED_CONSTRUCTION_REQUIRES_VISUAL_REVIEW'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ada_fixed_hand_initial.blend'))
(OUT/'records/initial_construction.json').write_text(json.dumps({'method':'Direct closed glove derivative; original finger sections adapted, local web faces removed and reconstructed','old_web_faces_removed':oldpatch,'source_vertices':len(source),'candidate_vertices':len(o.data.vertices),'candidate_faces':len(o.data.polygons),'predeclared_pad_source_ids':padids,'sword_transform':'canonical Z->hand X; X->Y; Y->Z; translation recorded in script','no_live_digit_rig':True,'attempt':'initial'},indent=2))
print('FIXED_INITIAL',len(o.data.vertices),len(o.data.polygons),'WEB_REPLACED',oldpatch)
