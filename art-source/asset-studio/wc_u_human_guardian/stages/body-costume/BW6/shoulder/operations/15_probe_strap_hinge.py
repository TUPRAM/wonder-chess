"""Bounded rigid-support feasibility probe; no source mesh/rig mutations."""
import bpy,sys,json,math,numpy as np,itertools,hashlib
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'operations'));import check_shoulder as ck
args=sys.argv[sys.argv.index('--')+1:];src=R/args[0];fr='lowered' if args[1]=='lowered' else int(args[1]);label=args[2];s=ck.load(src)
if fr=='lowered':ck.lowered(s)
else:s.frame_set(fr)
bpy.context.view_layer.update()
cap=bpy.data.objects['BW6_Pauldron_R_Cap'];base=ck.geom(cap);pivot=cap.parent.matrix_world.translation.copy();support=bpy.data.objects['BW6_R_Shoulder_RestDelta'].matrix_world.to_quaternion();ax=support@Vector((1,0,0));ay=support@Vector((0,1,0));up=support@Vector((0,0,1));names=[s['BW6_SHOULDER_COAT'],'BW6_Pauldron_R_Lame1','BW6_Pauldron_R_Lame2'];targets={n:ck.geom(bpy.data.objects[n]) for n in names};records=[]
for tx,ty,slack in itertools.product([-30,-20,-10,0,10],[-12,-6,0,6,12],[0,.003,.006]):
 delta=Matrix.Translation(pivot+up*slack)@Quaternion(ax,math.radians(tx)).to_matrix().to_4x4()@Quaternion(ay,math.radians(ty)).to_matrix().to_4x4()@Matrix.Translation(-pivot);mat=np.array(delta);q=base[0]@mat[:3,:3].T+mat[:3,3];g=(q,base[1],BVHTree.FromPolygons(q,base[1],all_triangles=True));counts={n:ck.cross(g,target)['count'] for n,target in targets.items()};row={'posterior_hinge_degrees':tx,'abduction_relief_degrees':ty,'vertical_strap_allowance_m':slack,'counts':counts,'cost':abs(tx)+abs(ty)*1.5+slack*5000,'delta_world':[list(x) for x in delta]};records.append(row)
best=min(records,key=lambda r:(sum(r['counts'].values())>0,sum(r['counts'].values()),r['cost']));zero=[r for r in records if sum(r['counts'].values())==0]
if zero:best=min(zero,key=lambda r:r['cost'])
out={'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'frame':fr,'method':'Rigid cap hinge about fixed medial strap pivot with bounded posterior tilt/abduction relief and <=6mm upward strap allowance. Exact finite transverse collider checks. No shell inflation or surface projection.','attempts':len(records),'feasible_count':len(zero),'best':best,'trials':records};(R/'records'/f'{label}_rigid_probe.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='trials'},indent=2))
if zero:
 cap.matrix_world=Matrix(best['delta_world'])@cap.matrix_world;bpy.context.view_layer.update();ck.render(s,label+'_feasible_probe','rear_three_quarter',fr)
