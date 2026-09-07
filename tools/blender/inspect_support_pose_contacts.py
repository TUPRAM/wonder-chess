"""Measure actual saved-source focus, shield floor and prop contact cues read-only."""
import hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import components,use_clip
OUT=Path(sys.argv[sys.argv.index('--')+1]).resolve();OUT.mkdir(parents=True,exist_ok=False);records=[]
for uid in ['wc_u_elf_mage','wc_u_orc_guardian']:
    source=ROOT/f'art-source/heroes/{uid}/{uid}.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest();m=json.loads((ROOT/f'exports/heroes/{uid}/export_manifest.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(source));arm=bpy.data.objects['Armature'];ob=bpy.data.objects['SK_'+uid];group_names={g.index:g.name for g in ob.vertex_groups};groups={v.index:{group_names[g.group] for g in v.groups if g.weight>.5} for v in ob.data.vertices};spec=m['clips']['Active'];row={'unit_id':uid,'source_sha256':digest,'release_frame':spec['release_frame']};use_clip(arm,'Active',spec['release_frame'],unit_id=uid);ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();points=[ev.matrix_world@v.co for v in mesh.vertices]
    if uid=='wc_u_elf_mage':
        palette={}
        for polygon in ob.data.polygons:
            uv=ob.data.uv_layers.active.data[polygon.loop_start].uv
            for index in polygon.vertices:palette[index]=int(uv.x*4)+4*int(uv.y*4)
        eyes=[points[i] for i in groups if 'head' in groups[i] and palette.get(i)==9];assert len(eyes)>8
        ring=max((part for part in components(ob) if part['groups']==['weapon_l']),key=lambda part:part['count']);focus=sum((points[i] for i in ring['indices']),Vector())/ring['count'];eye=sum(eyes,Vector())/len(eyes);row.update({'actual_eye_color_vertices':len(eyes),'actual_focus_ring_vertices':ring['count'],'focus_center_m':list(focus),'eye_color_centroid_m':list(eye),'focus_minus_eye_height_m':focus.z-eye.z});assert abs(focus.z-eye.z)<.08
    else:
        shield=[i for i in groups if 'weapon_l' in groups[i]];mace=[i for i in groups if 'weapon_r' in groups[i]];target={i for i in groups if groups[i]&{'weapon_l','lowerarm_l'}};polys=[list(poly.vertices) for poly in mesh.polygons if all(i in target for i in poly.vertices)];tree=BVHTree.FromPolygons(points,polys);nearest=min(tree.find_nearest(points[i])[3] for i in mace);row.update({'shield_minimum_z_m':min(points[i].z for i in shield),'mace_to_shield_or_left_forearm_surface_minimum_m':nearest});(OUT/'partial-contact-measurements.json').write_text(json.dumps(records+[row],indent=2)+'\n');assert -.003<row['shield_minimum_z_m']<.025,row
        ev.to_mesh_clear();ev=None;grips=[];shield_floor=[]
        for frame in range(1,spec['frames'][1]+1):
            use_clip(arm,'Active',frame,unit_id=uid);release=spec['release_frame'];end=spec['frames'][1];t=(frame-1)/(release-1) if frame<=release else (frame-release)/(end-release);progress=t*t*(3-2*t) if frame<=release else 1-t*t*(3-2*t)
            deformed_ob=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());deformed_mesh=deformed_ob.to_mesh();shield_floor.append({'frame':frame,'minimum_z_m':min((deformed_ob.matrix_world@deformed_mesh.vertices[i].co).z for i in shield)});deformed_ob.to_mesh_clear()
            if progress<=.60:
                weapon=arm.pose.bones['weapon_r'];deformation=weapon.matrix@weapon.bone.matrix_local.inverted();grip=deformation@arm.data.bones['hand_r'].tail_local;grips.append({'frame':frame,'grip_error_m':(grip-arm.pose.bones['hand_r'].tail).length})
        row['held_transfer_grip_samples']=grips;row['maximum_held_transfer_grip_error_m']=max(x['grip_error_m'] for x in grips);row['all_Active_shield_floor_samples']=shield_floor;row['minimum_shield_z_all_Active_frames_m']=min(x['minimum_z_m'] for x in shield_floor);assert row['maximum_held_transfer_grip_error_m']<.002;assert row['minimum_shield_z_all_Active_frames_m']>=-.003,row
    if ev:ev.to_mesh_clear()
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest;records.append(row)
(OUT/'pose-contact-measurements.json').write_text(json.dumps({'status':'MEASURED_ACTUAL_SAVED_SOURCE_CUES','heroes':records,'limits':['Nearest-surface distance does not prove collision-free sustained support','Finger geometry remains fixed; no finger-opening animation claim','No continuous Unreal visual acceptance']},indent=2)+'\n');(OUT/'executed-measurement.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(records,indent=2))
