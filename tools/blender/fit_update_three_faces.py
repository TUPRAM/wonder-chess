"""Fit existing Neris/Orla/Tala face layers; retain each actual head and all actions."""
import argparse,bmesh,hashlib,json,math,runpy,shutil,sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,invariants,use_clip
from author_alpha import Geometry,make_mesh,export_fbx_raw
from normalized_fbx import export_normalized_copy
REVISIONS={'wc_u_elf_mage':4,'wc_u_dwarf_priest':3,'wc_u_orc_guardian':3}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def colors(ob):
    result={}
    for p in ob.data.polygons:
        uv=ob.data.uv_layers.active.data[p.loop_start].uv
        for i in p.vertices:result[i]=int(uv.x*4)+4*int(uv.y*4)
    return result
def cleanup(ob):
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));seen=set();remove=[]
    for f in bm.faces:
        key=tuple(sorted(tuple(round(x,5) for x in v.co) for v in f.verts))
        if key in seen or f.calc_area()<1e-8:remove.append(f)
        else:seen.add(key)
    if remove:bmesh.ops.delete(bm,geom=remove,context='FACES_ONLY')
    bm.to_mesh(ob.data);bm.free();ob.data.calc_loop_triangles()
def dimensions(c):return [hi-lo for hi,lo in zip(c['bounds_max_m'],c['bounds_min_m'])]
def is_replaced(c,palette):
    return c['groups']==['head'] and ((c['count']==6 and palette==8) or (c['count']==4 and palette in (9,15)) or (c['count']==28 and palette==14) or (c['count']==18 and palette==7))
def preserved_signature(ob,excluded):
    palette=colors(ob);rows=[]
    for v in ob.data.vertices:
        if v.index in excluded:continue
        rows.append((tuple(round(x,7) for x in v.co),palette[v.index],sorted((ob.vertex_groups[g.group].name,round(g.weight,7)) for g in v.groups)))
    return {'retained_vertex_count':len(rows),'sha256':hashlib.sha256(json.dumps(sorted(rows),sort_keys=True).encode()).hexdigest()}
def candidate(uid,report):
    source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';out=ROOT/f'exports/heroes/{uid}';report.mkdir(parents=True,exist_ok=False);m=json.loads((out/'export_manifest.json').read_text());assert m['source_revision']==REVISIONS[uid] and sha(source)==m['source_sha256'];shutil.copy2(source,report/'before.blend');shutil.copy2(out/'export_manifest.json',report/'before-export-manifest.json');(report/'executed-refinement.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature'];saved=invariants(arm);use_clip(arm,'Idle',unit_id=uid);mesh=bpy.data.objects['SK_'+uid];mat=mesh.data.materials[0];u=next(x for x in json.loads((ROOT/'data/units.json').read_text())['units'] if x['id']==uid);h=u['height_m'];scale=h/1.86;palette=colors(mesh);parts=components(mesh);head=next(c for c in parts if c['groups']==['head'] and c['count']==140 and palette[c['indices'][0]]==6);ids=set(head['indices']);bvh=BVHTree.FromPolygons([v.co.copy() for v in mesh.data.vertices],[list(p.vertices) for p in mesh.data.polygons if set(p.vertices)<=ids])
    def surface(x,z):
        point=bvh.ray_cast(Vector((x,1,z)),Vector((0,-1,0)))[0];assert point is not None;return point.y
    g=Geometry()
    def add(v,f,c):g.add([tuple(x/h for x in p) for p in v],f,c,'head')
    def disc(cx,cz,rx,rz,c,depth):
        n=24;v=[(cx,surface(cx,cz)+depth,cz)]
        for ring in range(1,5):
            r=ring/4
            for i in range(n):
                a=i*2*math.pi/n;x=cx+rx*r*math.cos(a);z=cz+rz*r*math.sin(a);v.append((x,surface(x,z)+depth*(1-.15*r),z))
        f=[(0,i+1,(i+1)%n+1) for i in range(n)]
        for ring in range(3):
            q=1+ring*n;f.extend((q+i,q+(i+1)%n,q+n+(i+1)%n,q+n+i) for i in range(n))
        add(v,f,c)
    for eye in (c for c in parts if c['groups']==['head'] and c['count']==6 and palette[c['indices'][0]]==8):
        cx,_,cz=eye['center_m'];rx,_,rz=[v*.5 for v in dimensions(eye)];iris=next(c for c in parts if c['groups']==['head'] and c['count']==4 and palette[c['indices'][0]]==9 and cx*c['center_m'][0]>0);irx,_,irz=[v*.5 for v in dimensions(iris)];disc(cx,cz,rx,rz,8,.0022*scale);disc(cx,cz,irx,irz,9,.0037*scale);disc(cx,cz,irx*.48,irz*.54,15,.0046*scale);disc(cx-.0025*scale,cz+.0032*scale,.0013*scale,.0013*scale,8,.0052*scale)
        for upper in (True,False):
            v=[]
            for i in range(17):
                a=i*math.pi/16;x=cx+rx*math.cos(a);z=cz+(rz if upper else -rz)*math.sin(a)
                for dz in (-.0012*scale,.0012*scale):v.append((x,surface(x,z+dz)+.0028*scale,z+dz))
            add(v,[(j,j+1,j+3,j+2) for j in range(0,len(v)-2,2)],14)
    for brow in (c for c in parts if c['groups']==['head'] and c['count']==18 and palette[c['indices'][0]]==7):
        cx,_,cz=brow['center_m'];width=dimensions(brow)[0]*.93;thick=dimensions(brow)[2]*.22;v=[]
        for i in range(17):
            dx=-width*.5+i*width/16;x=cx+dx;z=cz+.003*scale-.004*scale*abs(dx/(width*.5))
            for dz in (-thick,thick):v.append((x,surface(x,z+dz)+.0035*scale,z+dz))
        add(v,[(j,j+1,j+3,j+2) for j in range(0,len(v)-2,2)],7)
    removed_main={i for c in parts if is_replaced(c,palette[c['indices'][0]]) for i in c['indices']};before_geometry=preserved_signature(mesh,removed_main);changes=[]
    for ob in (mesh,*list(bpy.data.collections['BODY'].objects)):
        if ob.type!='MESH':continue
        pal=colors(ob);remove={i for c in components(ob) if is_replaced(c,pal[c['indices'][0]]) for i in c['indices']}
        if remove:
            bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in sorted(remove)],context='VERTS');bm.to_mesh(ob.data);bm.free();changes.append({'object':ob.name,'old_facial_detail_vertices_removed':len(remove)})
    assert preserved_signature(mesh,set())==before_geometry
    # Track added vertices explicitly to prove no retained geometry or skin weights changed.
    retained_count=len(mesh.data.vertices);extra=make_mesh(g,u,arm,mat);extra.name='Fitted_Face_'+uid;part=extra.copy();part.data=extra.data.copy();bpy.data.collections['BODY'].objects.link(part);part.hide_render=True;part.hide_set(True);bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);extra.select_set(True);bpy.context.view_layer.objects.active=mesh;bpy.ops.object.join();mesh=bpy.context.object;cleanup(mesh);assert len(mesh.data.materials)==len(mesh.data.uv_layers)==1;assert invariants(arm)==saved;after_geometry=preserved_signature(mesh,set(range(retained_count,len(mesh.data.vertices))));assert after_geometry==before_geometry;use_clip(arm,'Idle',unit_id=uid);bpy.ops.wm.save_as_mainfile(filepath=str(report/'candidate.blend'),check_existing=False)
    scene=bpy.context.scene;scene.cycles.samples=12;scene.render.resolution_x=scene.render.resolution_y=768;z=head['center_m'][2];size=max(dimensions(head))*2.08
    for name,loc,target,ortho in [('face',(0,4,z+.14),(0,.01,z+.018),size),('face-three-quarter',(2.5,4,z+.18),(0,.01,z+.018),size),('front',(0,4,1.8),(0,0,h*.54),h*1.42),('side',(4,0,1.8),(0,0,h*.54),h*1.42),('back',(0,-4,1.8),(0,0,h*.54),h*1.42),('three-quarter',(3,5,2.7),(0,0,h*.54),h*1.42)]:
        scene.camera.data.ortho_scale=ortho;scene.camera.location=loc;scene.camera.rotation_euler=(Vector(target)-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(report/(name+'.png'));bpy.ops.render.render(write_still=True)
    assert sha(source)==m['source_sha256'];(report/'candidate-result.json').write_text(json.dumps({'status':'ACTUAL_FACE_CANDIDATE_RENDERED_NOT_PUBLISHED','unit_id':uid,'source_before_sha256':m['source_sha256'],'candidate_sha256':sha(report/'candidate.blend'),'preserved_invariants':saved,'preserved_geometry':before_geometry,'changes':changes,'preserved':['Head shell, nose, lips, ears, tusks, headpiece, hair and braids','All costume and equipment vertices, swatches and skin weights','Seven action curves and rest skeleton']},indent=2)+'\n');print('WC_FITTED_FACE_CANDIDATE_RENDERED',uid)
def publish(uid,report):
    source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';out=ROOT/f'exports/heroes/{uid}';(report/'executed-publish.py').write_bytes(Path(__file__).read_bytes());info=json.loads((report/'candidate-result.json').read_text());m=json.loads((report/'before-export-manifest.json').read_text());assert sha(source)==info['source_before_sha256'];assert sha(report/'candidate.blend')==info['candidate_sha256'];bpy.ops.wm.open_mainfile(filepath=str(report/'candidate.blend'));arm=bpy.data.objects['Armature'];assert invariants(arm)==info['preserved_invariants'];mesh=bpy.data.objects['SK_'+uid];saved=sys.argv
    try:
        sys.argv=['inspect_scene.py','--','--collection','EXPORT','--require-skin','--output',str(report/'candidate-structure.json')];runpy.run_path(str(ROOT/'tools/blender/inspect_scene.py'),run_name='__main__')
        sys.argv=['audit_motion.py','--','--unit',uid,'--output',str(report/'candidate-motion.json')];runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
    finally:sys.argv=saved
    assert not json.loads((report/'candidate-structure.json').read_text())['errors'];assert not json.loads((report/'candidate-motion.json').read_text())['errors'];arm.data.pose_position='REST';stage=report/'normalized-export';stage.mkdir(exist_ok=False);lods=[]
    for level,ratio in ((1,.5),(2,.25)):
        bpy.data.objects.remove(bpy.data.objects[f'SK_{uid}_LOD{level}'],do_unlink=True);lod=mesh.copy();lod.data=mesh.data.copy();lod.name=f'SK_{uid}_LOD{level}';bpy.data.collections['LOD_SOURCE'].objects.link(lod);bpy.context.view_layer.objects.active=lod;mod=lod.modifiers.new('WC_SilhouetteReduction','DECIMATE');mod.ratio=ratio;bpy.ops.object.modifier_apply(modifier=mod.name);cleanup(lod);export_normalized_copy(stage/(lod.name+'.fbx'),[arm,lod],False,export_fbx_raw);lods.append({'lod':level,'triangles':len(lod.data.loop_triangles),'ratio_target':ratio,'visual_acceptance':'pending'});lod.hide_render=True;lod.hide_set(True)
    export_normalized_copy(stage/('SK_'+uid+'.fbx'),[arm,mesh],False,export_fbx_raw);arm.data.pose_position='POSE';use_clip(arm,'Idle',unit_id=uid);scene=bpy.context.scene;scene.camera.data.ortho_scale=m['height_m']*1.42;scene.camera.location=(3,5,2.7);scene.camera.rotation_euler=(Vector((0,0,m['height_m']*.54))-scene.camera.location).to_track_quat('-Z','Y').to_euler();assert invariants(arm)==info['preserved_invariants'];bpy.ops.wm.save_as_mainfile(filepath=str(source),check_existing=False)
    for f in stage.glob('*.fbx'):shutil.copy2(f,out/f.name)
    shutil.copy2(out/'portrait.png',report/'before-portrait.png');shutil.copy2(report/'three-quarter.png',out/'portrait.png');m.update({'source_revision':m['source_revision']+1,'geometry_source_revision':m['geometry_source_revision']+1,'source_sha256':sha(source),'triangles':len(mesh.data.loop_triangles),'lods':lods,'update_refinement_script_sha256':sha(report/'executed-refinement.py'),'update_export_script_sha256':sha(report/'executed-publish.py'),'update_refinement_evidence':str(report),'files':{f.name:sha(f) for f in out.iterdir() if f.is_file() and f.name!='export_manifest.json'}});(out/'export_manifest.json').write_text(json.dumps(m,indent=2)+'\n');(report/'published-result.json').write_text(json.dumps({'status':'SOURCE_EXPORTED_PENDING_FRESH_VERIFICATION','unit_id':uid,'source_revision':m['source_revision'],'source_sha256':sha(source),'manifest_sha256':sha(out/'export_manifest.json'),'triangles':m['triangles'],'lods':lods},indent=2)+'\n');print('WC_FITTED_FACE_PUBLISHED',uid)
p=argparse.ArgumentParser();p.add_argument('--unit',choices=list(REVISIONS),required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--publish',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);publish(a.unit,a.report.resolve()) if a.publish else candidate(a.unit,a.report.resolve())
