"""Read-only structural observations in Blender. Not a visual, overlap, or rig-quality pass.
Unexecuted in Blender when this kit was authored. Inspect against installed bpy APIs.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys
from pathlib import Path
from collections import Counter
import bpy
from mathutils import Vector

def inspect(collection_name:str):
    c=bpy.data.collections.get(collection_name)
    if c is None:raise ValueError(f'Collection not found: {collection_name}')
    objects=sorted(c.all_objects,key=lambda o:o.name);rows=[]
    for ob in objects:
        row={'name':ob.name,'type':ob.type,'semantic_part_id':ob.get('wc_part_id'),'negative_transform_determinant':ob.matrix_world.determinant()<0,
             'scale':list(ob.scale),'modifiers':[{'name':m.name,'type':m.type,'enabled':m.show_viewport} for m in ob.modifiers]}
        if ob.type=='MESH':
            me=ob.data;me.calc_loop_triangles();edge_use=Counter()
            for poly in me.polygons:
                verts=list(poly.vertices)
                for i,a in enumerate(verts):edge_use[tuple(sorted((a,verts[(i+1)%len(verts)])))]+=1
            arm_mods=[m for m in ob.modifiers if m.type=='ARMATURE' and m.object]
            deform_names={b.name for m in arm_mods for b in m.object.data.bones if b.use_deform}
            groups={v.index:v.name for v in ob.vertex_groups};weights=[]
            if arm_mods:
                for v in me.vertices:
                    ws=[g.weight for g in v.groups if groups.get(g.group) in deform_names and g.weight>1e-6]
                    weights.append((sum(ws),len(ws)))
            row.update({'vertices_source':len(me.vertices),'triangles_source':len(me.loop_triangles),'polygons_source':len(me.polygons),
                 'degenerate_source_triangles':sum(1 for t in me.loop_triangles if t.area<1e-12),
                 'wire_edges':sum(edge_use.get(tuple(sorted(e.vertices)),0)==0 for e in me.edges),
                 'boundary_edges':sum(n==1 for n in edge_use.values()),'edges_over_two_faces':sum(n>2 for n in edge_use.values()),
                 'uv_layers':[u.name for u in me.uv_layers], 'materials':[m.name if m else None for m in me.materials],
                 'unweighted_vertices':sum(n==0 for _,n in weights) if arm_mods else None,
                 'non_normalized_vertices':sum(abs(s-1)>1e-4 for s,n in weights) if arm_mods else None,
                 'max_deform_influences':max((n for _,n in weights),default=0) if arm_mods else None,
                 'preserve_volume_enabled':any(m.use_deform_preserve_volume for m in arm_mods),
                 'finite_coordinates':all(math.isfinite(float(a)) for v in me.vertices for a in v.co)})
            # Evaluated counts are separate; topology-changing modifiers can invalidate source UV/weight indices.
            ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());em=ev.to_mesh()
            try:
                em.calc_loop_triangles();row['triangles_evaluated']=len(em.loop_triangles)
                world=[ob.matrix_world@Vector(p) for p in ob.bound_box]
                row['world_bbox_dimensions']= [max(v[i] for v in world)-min(v[i] for v in world) for i in range(3)]
            finally:ev.to_mesh_clear()
        elif ob.type=='ARMATURE':
            bones=[{'name':b.name,'parent':b.parent.name if b.parent else None,'deform':b.use_deform,
                    'matrix_local':[list(r) for r in b.matrix_local]} for b in ob.data.bones]
            row['bones']=bones;row['deform_bones']=sum(b['deform'] for b in bones)
            row['rest_skeleton_sha256']=hashlib.sha256(json.dumps(bones,sort_keys=True).encode()).hexdigest()
        rows.append(row)
    images=[]
    for im in bpy.data.images:
        if im.source=='FILE':
            path=Path(bpy.path.abspath(im.filepath))
            images.append({'name':im.name,'size':list(im.size),'color_space':im.colorspace_settings.name,
                           'packed':bool(im.packed_file),'external_file_exists':path.is_file()})
    return {'status':'observations_only_not_acceptance','blender_version':bpy.app.version_string,
            'source_blend_name':Path(bpy.data.filepath).name if bpy.data.filepath else None,
            'source_blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest() if bpy.data.filepath and Path(bpy.data.filepath).is_file() else None,
            'collection':collection_name,'objects':rows,'file_images':images,
            'limitations':['No exhaustive self-intersection check.','Boundary edges are not automatically errors on open garments.','No UV overlap or texel-density calculation.','No visual likeness or continuous-motion judgement.','Source/evaluated mesh counts may differ.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('--collection',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    result=inspect(a.collection);a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print('AS1_SCENE_OBSERVATIONS_WRITTEN',str(a.output))
if __name__=='__main__':main()
