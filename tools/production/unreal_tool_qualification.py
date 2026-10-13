"""Run with UE PythonScript commandlet. Writes only its diagnostic namespace.

This qualifies authoring APIs with synthetic fixtures; it does not approve art.
"""
import json
import traceback
from pathlib import Path
import unreal as u

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'reports/pipeline-tools-20260921'
BASE = '/Game/WonderChess/Diagnostics/PipelineTools20260921'
report = {'engine': u.SystemLibrary.get_engine_version(), 'scope': 'synthetic_tool_qualification', 'steps': {}}


def record(name, fn):
    try:
        report['steps'][name] = {'status': 'pass', 'result': fn()}
    except Exception:
        report['steps'][name] = {'status': 'fail', 'error': traceback.format_exc()}
    (OUT / 'unreal-qualification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


def mesh_test():
    global low, high
    low, high = u.DynamicMesh(), u.DynamicMesh()
    for mesh, steps in [(low, 0), (high, 5)]:
        u.GeometryScript_Primitives.append_box(mesh, u.GeometryScriptPrimitiveOptions(), u.Transform(),
                                             100, 100, 100, steps, steps, steps)
        repack = getattr(u.GeometryScript_UVs, next(n for n in dir(u.GeometryScript_UVs) if n.startswith('repack_mesh')))
        repack(mesh, 0, u.GeometryScriptRepackUVsOptions())
        u.GeometryScript_Normals.compute_tangents(mesh, u.GeometryScriptTangentsOptions())
    assets = []
    for name, mesh in [('SM_QualificationLow', low), ('SM_QualificationHigh', high)]:
        path = BASE + '/' + name
        asset = u.load_asset(path)
        if asset is None:
            asset, outcome = u.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(
                mesh, path, u.GeometryScriptCreateNewStaticMeshAssetOptions())
            if not asset:
                raise RuntimeError(str(outcome))
        u.EditorAssetLibrary.save_loaded_asset(asset)
        assets.append(asset.get_path_name())
    return {'assets': assets, 'low_triangles': low.get_triangle_count(), 'high_triangles': high.get_triangle_count()}


def bake_test():
    textures = u.GeometryScript_Bake.bake_texture(
        low, u.Transform(), u.GeometryScriptBakeTargetMeshOptions(),
        high, u.Transform(), u.GeometryScriptBakeSourceMeshOptions(),
        [u.GeometryScript_Bake.make_bake_type_tangent_normal()], u.GeometryScriptBakeTextureOptions())
    if not textures:
        raise RuntimeError('Bake produced no texture')
    path = BASE + '/T_QualificationNormal'
    asset = u.load_asset(path)
    if not asset:
        asset, outcome = u.GeometryScript_NewAssetUtils.create_new_texture2d_asset(
            textures[0], path, u.GeometryScriptCreateNewTexture2DAssetOptions())
        if not asset:
            raise RuntimeError(str(outcome))
    u.EditorAssetLibrary.save_loaded_asset(asset)
    return {'asset': asset.get_path_name(), 'width': asset.blueprint_get_size_x(), 'height': asset.blueprint_get_size_y(),
            'note': 'Synthetic matched surfaces; not a creature UV or projection quality approval.'}


def sequence_test():
    path = BASE + '/LS_Qualification'
    seq = u.load_asset(path)
    if not seq:
        seq = u.AssetToolsHelpers.get_asset_tools().create_asset('LS_Qualification', BASE, u.LevelSequence, u.LevelSequenceFactoryNew())
    seq.set_display_rate(u.FrameRate(30, 1))
    seq.set_playback_end(60)
    u.EditorAssetLibrary.save_loaded_asset(seq)
    return {'asset': seq.get_path_name(), 'frames': [seq.get_playback_start(), seq.get_playback_end()]}


def skeleton_test():
    # Duplicate before editing: never change the accepted Bellback skeleton or mesh.
    path = BASE + '/SK_QualificationEditable'
    mesh = u.load_asset(path)
    source = u.load_asset('/Game/WonderChess/VNext/Characters/Bellback_r001/SK_Bellback')
    skeleton = source.get_editor_property('skeleton')
    private = u.load_asset(BASE + '/SKEL_QualificationBellback')
    if not private:
        private = u.EditorAssetLibrary.duplicate_asset(skeleton.get_path_name(), BASE + '/SKEL_QualificationBellback')
    if not mesh:
        dm = u.DynamicMesh()
        _, outcome = u.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(source, dm,
            u.GeometryScriptCopyMeshFromAssetOptions(), u.GeometryScriptMeshReadLOD(lod_index=0))
        mesh, outcome = u.GeometryScript_NewAssetUtils.create_new_skeletal_mesh_asset_from_mesh(
            dm, private, path, u.GeometryScriptCreateNewSkeletalMeshAssetOptions())
        if not mesh:
            raise RuntimeError(str(outcome))
    mod = u.SkeletonModifier()
    if not mod.set_skeletal_mesh(mesh):
        raise RuntimeError('SkeletonModifier refused the duplicate')
    names = [str(x) for x in mod.get_all_bone_names()]
    if 'qualification_socket_bone' not in names:
        if not mod.add_bone('qualification_socket_bone', names[0], u.Transform(location=u.Vector(0, 0, 3))):
            raise RuntimeError('Could not add test bone')
        if not mod.commit_skeleton_to_skeletal_mesh():
            raise RuntimeError('Skeleton commit failed')
    u.EditorAssetLibrary.save_loaded_asset(mesh)
    u.EditorAssetLibrary.save_loaded_asset(private)
    return {'mesh': path, 'bones_before': len(names), 'bones_after': len(mod.get_all_bone_names()),
            'added_bone': 'qualification_socket_bone', 'production_mesh_edited': False}


def discover():
    names = [n for n in dir(u) if n.startswith('GeometryScript_') and ('UV' in n or 'Query' in n or 'Queries' in n)]
    details = {}
    for c in names + ['ValidateAssetsSettings', 'ValidateAssetsResults', 'EditorValidatorBase', 'SkeletonModifier']:
        cls = getattr(u, c)
        details[c] = {'doc': cls.__doc__, 'methods': {n: getattr(cls, n).__doc__ for n in dir(cls)
                     if any(w in n for w in ('uv', 'validat', 'asset_pass', 'asset_fail', 'commit', 'bone')) and not n.startswith('_')}}
    (OUT / 'unreal-extra-api.json').write_text(json.dumps(details, indent=2), encoding='utf-8')
    return names


record('discover', discover)
record('modeling', mesh_test)
record('baking', bake_test)
record('sequencer', sequence_test)
record('skeleton_editing', skeleton_test)
if any(s['status'] == 'fail' for s in report['steps'].values()):
    raise RuntimeError('Qualification step failed; see unreal-qualification.json')
