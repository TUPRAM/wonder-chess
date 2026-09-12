import bpy,sys,json,bmesh,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
s=ck.load(R/'ada_bw6_shoulder_r003_combined_review.blend');col=bpy.data.collections.new('BW6_SHOULDER_UNDERSTRAPS_STUDY');s.collection.children.link(col);parts=[bpy.data.objects['BW6_Pauldron_R_'+n] for n in ['Cap','Lame1','Lame2']];g={o.name:ck.geom(o) for o in parts};material=bpy.data.materials.new('BW6_Support_Leather_Study');material.diffuse_color=(.18,.10,.055,1);material.use_nodes=True;material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.12,.062,.032,1);material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.65;names=[];records=[]
for side,j in [('Rear',3),('Front',9)]:
 vertices=[];owners=[];centers=[];spec=[(parts[0],4),(parts[0],5),(parts[1],4),(parts[2],2)]
 for o,row in spec:
  vi=o.data.vertices[row*13+j];q=o.matrix_world@vi.co;hit,normal,tr,d=g[o.name][2].find_nearest(q);normal=Vector(normal);q=Vector(hit)-normal*.0048;tangent=(o.matrix_world@(o.data.vertices[row*13+j+1].co-o.data.vertices[row*13+j-1].co).to_4d()).to_3d() if False else o.matrix_world.to_3x3()@(o.data.vertices[row*13+j+1].co-o.data.vertices[row*13+j-1].co);tangent.normalize();vertices.extend([q-tangent*.006,q+tangent*.006]);owners.append(o);centers.append(q)
 me=bpy.data.meshes.new('BW6_'+side+'_StrapEditable');me.from_pydata(vertices,[],[(2*i,2*i+1,2*i+3,2*i+2) for i in range(3)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new('BW6_R_Understrap_'+side,me);col.objects.link(o);me.materials.append(material)
 for i,owner in enumerate(owners):
  h=o.modifiers.new('Bound station '+str(i)+' to '+owner.name,'HOOK');h.object=owner;h.matrix_inverse=owner.matrix_world.inverted()@o.matrix_world;h.vertex_indices_set([2*i,2*i+1]);h.falloff_type='NONE';h.strength=1
 sub=o.modifiers.new('Flexible strap interpolation','SUBSURF');sub.levels=2;sub.render_levels=2;sub.boundary_smooth='PRESERVE_CORNERS';wall=o.modifiers.new('2mm strap thickness','SOLIDIFY');wall.thickness=.002;wall.offset=0;wall.use_even_offset=False;names.append(o.name);o['BW6_scope']='Independent flexible under-strap proof; hooks bind distinct stations to rigid plates, not metal deformation or a runtime implementation.';o['BW6_predeclared_terminal_stations']=json.dumps([0,3]);records.append({'object':o.name,'width_m':.012,'thickness_m':.002,'stations':[{'owner':owner.name,'world_m':list(q)} for owner,q in zip(owners,centers)],'rest_polyline_length_m':sum((centers[i+1]-centers[i]).length for i in range(3))})
s['BW6_SHOULDER_SUPPORT_STUDY']=json.dumps(names);out=R/'ada_bw6_shoulder_understrap_initial.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out));(R/'records/understrap_initial_construction.json').write_text(json.dumps(records,indent=2))
for f in [1,49,73,'lowered']:
 sc=ck.load(out);ck.render(sc,'understrap_initial_shoulder_'+str(f),pose=f)
