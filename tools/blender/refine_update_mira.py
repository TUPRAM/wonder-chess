"""Refine Mira's inspected revision6 scene incrementally; preserve the shared rig."""
import argparse, json, math, shutil, sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
UID='wc_u_human_priest'
SOURCE=ROOT/f'art-source/heroes/{UID}/{UID}.blend'
EXPORT=ROOT/f'exports/heroes/{UID}'
sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import sha, components, invariants, render_views

def alter_parts(mesh):
    records=[]; parts=components(mesh)
    for part in parts:
        group=part['groups']; count=part['count']; center=Vector(part['center_m'])
        verts=[mesh.data.vertices[i] for i in part['indices']]
        change=None
        if group==['spine_03'] and count==20:
            # Keep the top bridge over the shoulder; gather the hanging corners.
            for v in verts:
                low=max(0,min(1,(1.34-v.co.z)/.20))
                v.co.y=.0136+(v.co.y-.0136)*(1-.62*low)
                outer=max(0,min(1,(abs(v.co.x)-.25)/.20))
                v.co.x*=1-.085*outer
                v.co.z-=.022*outer*low
            change='mantle tapered over shoulder with gathered lower hem'
        elif group==['pelvis'] and count in (16,24) and center.z<.8 and abs(center.x)<.2:
            for v in verts:
                low=max(0,min(1,(.92-v.co.z)/.34))
                v.co.x*=1-.10*low
                v.co.y+=math.copysign(.012*low*(1-min(1,abs(v.co.x)/.34)),v.co.y)
            change='coat panel tapered with broad curved hem'
        elif group==['head'] and count==5:
            for v in verts:
                v.co.x*=.88; v.co.y=.1309+(v.co.y-.1309)*.60
            change='nose projection and width refined'
        elif group==['head'] and count==15 and center.z>1.55:
            for v in verts:
                v.co.z=center.z+(v.co.z-center.z)*.53-.007
                v.co.y=center.y+(v.co.y-center.y)*.65
            change='brows flatter and less heavy'
        elif group==['head'] and count==112:
            for v in verts:
                v.co.x*=1-.08*max(0,min(1,(1.50-v.co.z)/.095))
            change='lower face contour softened, bun and eye geometry retained'
        elif group==['head'] and count==15 and center.z<1.5:
            for v in verts:
                v.co.x*=.90; v.co.z+=.003
            change='mouth contour refined'
        elif group==['hand_r'] and count==174:
            # Preserve the large opening and enlarge the six-sided ring tube.
            for v in verts:
                delta=v.co-center
                radial=Vector((delta.x,0,delta.z)).normalized()
                median=center+radial*.127
                v.co=median+(v.co-median)*1.32
            change='open circular lantern tube thickened 32 percent'
        elif group==['hand_r'] and count==30 and part['bounds_max_m'][2]-part['bounds_min_m'][2]>1:
            # Existing staff has three ten-vertex rings; retain its original bend.
            for start in range(0,count,10):
                ring=verts[start:start+10]; midpoint=sum((v.co for v in ring),Vector())/10
                for v in ring: v.co=midpoint+(v.co-midpoint)*1.16
            change='staff grip cross-section thickened 16 percent'
        elif group==['pelvis'] and count==16 and .08<center.y<.11 and .8<center.z<.9:
            for v in verts:
                v.co.x=center.x+(v.co.x-center.x)*1.15
                v.co.z=center.z+(v.co.z-center.z)*1.20
            change='two satchel clasps enlarged'
        elif group==['spine_02'] and count==10:
            for start,target in ((0,Vector((-.18,.172,1.371))),(5,Vector((.282,.11,.926)))):
                ring=verts[start:start+5]; midpoint=sum((v.co for v in ring),Vector())/5
                for v in ring: v.co=target+(v.co-midpoint)*.83
            change='front satchel strap reaches shoulder and bag'
        if change: records.append({'first_vertex':part['first_vertex'],'count':count,'change':change})
    mesh.data.update()
    return records

def add_back_strap(mesh):
    # Continue the existing strap around the shoulder and down to the same satchel.
    old=next(p for p in components(mesh) if p['groups']==['spine_02'] and p['count']==10)
    source_face=next(p for p in mesh.data.polygons if all(i in old['indices'] for i in p.vertices))
    strap_material=mesh.data.materials[source_face.material_index]
    uv=sum((mesh.data.uv_layers.active.data[i].uv for i in source_face.loop_indices),Vector((0,0)))/len(source_face.loop_indices)
    # Give the original front ribbon enough sections to follow the chest,
    # rather than allowing its straight chord to pass through the torso.
    bm=bmesh.new(); bm.from_mesh(mesh.data); bm.verts.ensure_lookup_table()
    original={bm.verts[i] for i in old['indices']}
    edges=[edge for edge in bm.edges if all(v in original for v in edge.verts) and edge.calc_length()>.25]
    seed_position=bm.verts[old['indices'][0]].co.copy()
    bmesh.ops.subdivide_edges(bm,edges=edges,cuts=3,use_grid_fill=True)
    seed=min(bm.verts,key=lambda vertex:(vertex.co-seed_position).length_squared)
    pending=[seed]; connected={seed}
    while pending:
        for edge in pending.pop().link_edges:
            for vertex in edge.verts:
                if vertex not in connected: connected.add(vertex); pending.append(vertex)
    for vertex in connected:
        t=max(0,min(1,(1.371-vertex.co.z)/.445))
        depth=vertex.co.y-(.172+(.11-.172)*t)
        stations_y=[(0,.181),(.27,.225),(.70,.215),(1,.133)]
        for j in range(1,len(stations_y)):
            if t<=stations_y[j][0]:
                start,y0=stations_y[j-1]; end,y1=stations_y[j]
                vertex.co.y=y0+(y1-y0)*(t-start)/(end-start)+depth
                break
    bm.to_mesh(mesh.data); bm.free(); mesh.data.update()
    stations=[((-.18,.175,1.35),(0,1,0),'spine_03'),
              ((-.18,.01,1.372),(0,0,1),'spine_03'),
              ((-.18,-.13,1.33),(0,-1,0),'spine_03'),
              ((.07,-.16,1.13),(0,-1,0),'spine_02'),
              ((.285,-.13,.938),(0,-1,0),'pelvis'),
              ((.315,.026,.926),(1,0,0),'pelvis')]
    vertices=[]; faces=[]
    for i,(point,normal,bone) in enumerate(stations):
        point=Vector(point); normal=Vector(normal)
        tangent=Vector(stations[min(len(stations)-1,i+1)][0])-Vector(stations[max(0,i-1)][0])
        lateral=tangent.cross(normal).normalized()*.025
        vertices.extend([point-lateral-normal*.004,point+lateral-normal*.004,
                         point+lateral+normal*.004,point-lateral+normal*.004])
        if i:
            for j in range(4): faces.append(((i-1)*4+j,(i-1)*4+(j+1)%4,i*4+(j+1)%4,i*4+j))
    faces.extend([(3,2,1,0),tuple(range(len(vertices)-4,len(vertices)))])
    data=bpy.data.meshes.new('Mira_ContinuedSatchelStrap'); data.from_pydata(vertices,[],faces); data.update()
    data.materials.append(strap_material)
    layer=data.uv_layers.new(name=mesh.data.uv_layers.active.name)
    for item in layer.data: item.uv=uv
    strap=bpy.data.objects.new('Mira_ContinuedSatchelStrap',data); mesh.users_collection[0].objects.link(strap)
    for i,(_,_,name) in enumerate(stations):
        group=strap.vertex_groups.get(name) or strap.vertex_groups.new(name=name)
        group.add(list(range(i*4,i*4+4)),1,'REPLACE')
    hidden=mesh.hide_get(); mesh.hide_set(False)
    bpy.ops.object.select_all(action='DESELECT'); mesh.select_set(True); strap.select_set(True)
    bpy.context.view_layer.objects.active=mesh; bpy.ops.object.join(); mesh.hide_set(hidden)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).output.resolve(); out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((EXPORT/'export_manifest.json').read_text())
    assert manifest['source_revision']==6 and sha(SOURCE)==manifest['source_sha256']
    shutil.copy2(SOURCE,out/'before-source.blend'); shutil.copy2(EXPORT/'export_manifest.json',out/'before-export-manifest.json')
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE)); arm=bpy.data.objects['Armature']; before=invariants(arm)
    changes={}
    for name in ('SK_'+UID,'BODY_SK_'+UID,'COSTUME_SK_'+UID,'EQUIPMENT_SK_'+UID):
        mesh=bpy.data.objects[name]; changes[name]=alter_parts(mesh)
        if name in ('SK_'+UID,'COSTUME_SK_'+UID): add_back_strap(mesh)
    assert invariants(arm)==before
    arm.animation_data.action=bpy.data.actions[f'AN_{UID}_Idle']; arm.animation_data.action_slot=arm.animation_data.action.slots[0]
    bpy.context.scene.frame_set(1)
    candidate=out/'mira-update24-revision7.blend'; bpy.ops.wm.save_as_mainfile(filepath=str(candidate),check_existing=False)
    renders=render_views(out,'after')
    assert sha(SOURCE)==manifest['source_sha256']
    report={'status':'SOURCE_REFINEMENT_RENDERED_NOT_PROMOTED','source_before_sha256':manifest['source_sha256'],
            'candidate':str(candidate),'candidate_sha256':sha(candidate),'changes':changes,
            'strap_refinement':'original front subdivided to follow chest, 24-vertex rear continuation added',
            'preserved_invariants':before,'renders':renders,
            'limits':['Existing actions preserved; seven clips still require current geometry review',
                      'LODs pending regeneration','Unreal not imported','Final art not accepted']}
    (out/'refinement.json').write_text(json.dumps(report,indent=2)+'\n')
    print('WC_MIRA_SOURCE_REFINED '+str(candidate),flush=True)

if __name__=='__main__':main()
