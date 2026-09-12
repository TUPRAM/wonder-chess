"""Import only hash-verified, explicitly calibrated image empties into a candidate scene.
No automatic AI-view alignment. New collection and new .blend destination only.
Unexecuted in Blender at kit authoring.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Matrix

def main():
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True);p.add_argument('--spec',type=Path,required=True)
    p.add_argument('--output-blend',type=Path,required=True);p.add_argument('--collection',default='AS1_REFERENCES')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=a.workspace.resolve();spec=json.loads(a.spec.read_text())
    dest=a.output_blend.resolve()
    if dest.exists() or dest.suffix.lower()!='.blend':raise ValueError('Require a new .blend output.')
    dest.relative_to(root)
    if a.collection in bpy.data.collections:raise ValueError('Reference collection exists; use a new revision name.')
    if spec.get('status')!='calibrated_candidate':raise ValueError('Calibration decisions must precede scene setup.')
    rows=spec.get('views',[])
    if not rows:raise ValueError('No reference views.')
    checked=[]
    for v in rows:
        path=(root/v['path']).resolve();path.relative_to(root)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=v['image_sha256']:raise ValueError('Image hash mismatch.')
        mat=v['matrix_world']
        if len(mat)!=4 or any(len(r)!=4 for r in mat):raise ValueError('Need explicit 4x4 matrix.')
        if any(not isinstance(x,(int,float)) or not math.isfinite(x) for r in mat for x in r):raise ValueError('Matrix must contain finite numbers.')
        if not math.isfinite(float(v['display_size_m'])) or float(v['display_size_m'])<=0:raise ValueError('Invalid display size.')
        checked.append((v,path,Matrix(mat)))
    c=bpy.data.collections.new(a.collection);bpy.context.scene.collection.children.link(c)
    try:
        for v,path,matrix in checked:
            ob=bpy.data.objects.new('AS1_REF_'+v['part_id']+'_'+v['view'],None);c.objects.link(ob)
            ob.empty_display_type='IMAGE';ob.data=bpy.data.images.load(str(path),check_existing=True)
            ob.empty_display_size=float(v['display_size_m']);ob.matrix_world=matrix;ob.hide_render=True
            ob['wc_part_id']=v['part_id'];ob['reference_sha256']=v['image_sha256'];ob['reference_role']='construction_candidate'
        dest.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=True)
    except Exception:
        for ob in list(c.objects):bpy.data.objects.remove(ob,do_unlink=True)
        bpy.data.collections.remove(c);raise
    print('AS1_REFERENCE_SCENE_CANDIDATE',str(dest))
if __name__=='__main__':main()
