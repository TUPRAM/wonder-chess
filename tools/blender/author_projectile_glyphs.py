"""Author two original, compact ranged presentation meshes with a measured export basis."""
import bpy,bmesh,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).resolve().parent))
from author_alpha import Geometry,export_fbx_raw,rgb
from normalized_fbx import export_normalized_copy
out=root/'exports/effects';source=root/'art-source/effects';report=root/'reports/WC-340'
for path in (out,source,report):path.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
def solid_plan(g,polygon,depth):
    n=len(polygon);vertices=[(x,y,z) for z in (-depth/2,depth/2) for x,y in polygon]
    faces=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]
    faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n));g.add(vertices,faces,0)
def material(name,hex_color):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    color=tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in rgb(hex_color))
    bsdf=mat.node_tree.nodes['Principled BSDF'];bsdf.inputs['Base Color'].default_value=(*color,1)
    bsdf.inputs['Metallic'].default_value=.2;bsdf.inputs['Roughness'].default_value=.45;return mat
def project_face_uvs(mesh):
    uv=mesh.uv_layers.new(name='UVMap')
    for face in mesh.polygons:
        points=[mesh.vertices[mesh.loops[i].vertex_index].co for i in face.loop_indices]
        tangent=max((points[(i+1)%len(points)]-p for i,p in enumerate(points)),key=lambda v:v.length_squared).normalized()
        bitangent=face.normal.cross(tangent).normalized()
        coords=[(p.dot(tangent),p.dot(bitangent)) for p in points]
        low=[min(p[i] for p in coords) for i in (0,1)]
        extent=max(max(p[i] for p in coords)-low[i] for i in (0,1))
        if extent<=1e-8:raise RuntimeError('Degenerate glyph face')
        for loop,p in zip(face.loop_indices,coords):
            uv.data[loop].uv=(.05+.9*(p[0]-low[0])/extent,.05+.9*(p[1]-low[1])/extent)
    mesh.calc_loop_triangles()
    areas=[]
    for tri in mesh.loop_triangles:
        a,b,c=(uv.data[i].uv for i in tri.loops)
        areas.append(abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))*.5)
    if min(areas)<=1e-10:raise RuntimeError('Degenerate glyph UV triangle')
    return {'method':'independent planar face projection; overlapping islands are intentional for flat tint',
            'uv_layers':len(mesh.uv_layers),'minimum_triangle_uv_area':min(areas),'checked_triangles':len(areas)}
records=[];objects=[]
previous_manifest=json.loads((out/'projectile_manifest.json').read_text()) if (out/'projectile_manifest.json').exists() else None
for name,uid,color in [('Arrow','wc_u_elf_ranger','#B7CBB0'),('Bolt','wc_u_dwarf_ranger','#B67B55')]:
    g=Geometry()
    if name=='Arrow':
        g.tube([(0,-.29,0),(0,.23,0)],[.011,.011],0,sides=8)
        solid_plan(g,[(-.085,.17),(0,.42),(.085,.17),(0,.215)],.018)
        for side in (-1,1):solid_plan(g,[(0,-.28),(side*.07,-.34),(side*.055,-.20),(0,-.16)],.014)
        tip=(0,.42,0);tail=(0,-.34,0)
    else:
        g.tube([(0,-.22,0),(0,.17,0)],[.017,.017],0,sides=10)
        solid_plan(g,[(0,.35),(.065,.21),(.035,.10),(-.035,.10),(-.065,.21)],.032)
        for side in (-1,1):solid_plan(g,[(0,-.22),(side*.055,-.27),(side*.045,-.11),(0,-.08)],.025)
        tip=(0,.35,0);tail=(0,-.27,0)
    mesh=bpy.data.meshes.new('WC_'+name+'_GlyphGeometry');mesh.from_pydata(g.vertices,[],g.faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
    uv_check=project_face_uvs(mesh)
    obj=bpy.data.objects.new('SM_WC_'+name+'Glyph',mesh);scene.collection.objects.link(obj)
    mesh.materials.append(material('M_WC_'+name+'Glyph',color));objects.append(obj)
    export_normalized_copy(out/f'{obj.name}.fbx',[obj],False,export_fbx_raw)
    mesh.calc_loop_triangles()
    records.append({'mesh':obj.name,'unit_id':uid,'triangles':len(mesh.loop_triangles),'source_tip_m':tip,'source_tail_m':tail,
                    'source_dimensions_m':list(obj.dimensions),'uv_check':uv_check,'expected_forward_after_measured_import':'+X','engine_import':'pending_reimport_after_uv_fix'})
    if previous_manifest:
        previous=next(r for r in previous_manifest['records'] if r['mesh']==obj.name)
        assert previous['triangles']==records[-1]['triangles']
        assert all(abs(a-b)<1e-7 for a,b in zip(previous['source_dimensions_m'],obj.dimensions))
world=bpy.data.worlds.new('WC_GlyphStudio');world.color=(.1,.13,.18);scene.world=world
for name,location,power,size in [('Key',(1,1,2),160,2),('Fill',(-1,0,1),80,2)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.size=size
    ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=location
    ob.rotation_euler=(-ob.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('WC_GlyphReview');camera=bpy.data.objects.new('WC_GlyphReview',data);scene.collection.objects.link(camera)
camera.location=(.7,-.8,1.1);camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=1.05;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.resolution_x=512;scene.render.resolution_y=512
scene.render.film_transparent=True
for obj in objects:
    for other in objects:other.hide_render=other!=obj
    scene.render.filepath=str(report/f'{obj.name}.png');bpy.ops.render.render(write_still=True)
for obj in objects:obj.hide_render=False
blend=source/'WC_ProjectileGlyphs.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
manifest={'status':'uv_corrected_exported_rendered_pending_engine_reimport','revision':2,'source':str(blend.relative_to(root)),
          'source_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,
          'source_units':'meters','source_forward':'+Y','source_up':'+Z','fbx_values':'centimeters via temporary-copy normalization',
          'profile':'tools/blender/profiles/fbx_skeletal_cm_v1.json','material_policy':'one opaque material per mesh; runtime may use its existing tint material',
          'records':records,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.fbx')}}
if previous_manifest:(report/'projectile-manifest-before-uv-fix.json').write_text(json.dumps(previous_manifest,indent=2)+'\n')
(out/'projectile_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('WC_PROJECTILE_GLYPHS_COMPLETE '+json.dumps(manifest),flush=True)
