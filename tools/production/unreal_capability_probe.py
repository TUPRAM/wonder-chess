"""Read-only Unreal capability discovery. Run inside the installed project editor."""
import json
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'reports/pipeline-tools-20260921'
OUT.mkdir(parents=True, exist_ok=True)
names = ['DynamicMesh', 'GeometryScript_AssetUtils', 'GeometryScript_MeshUVs',
         'GeometryScript_Primitives', 'GeometryScript_Bake', 'SkeletonModifier',
         'EditorValidatorBase', 'EditorValidatorSubsystem', 'DataValidationUsecase',
         'SkeletalMeshEditorSubsystem', 'LevelSequence', 'ControlRigBlueprint',
         'SceneCaptureComponent2D', 'RenderingLibrary', 'GeometryScript_NewAssetUtils']
names += [n for n in dir(unreal) if ('GeometryScript' in n and 'Bake' in n)]
result = {'engine': unreal.SystemLibrary.get_engine_version(), 'classes': {}, 'apis': {}}
for name in sorted(set(names)):
    cls = getattr(unreal, name, None)
    result['classes'][name] = cls is not None
    if cls:
        result['apis'][name] = {'doc': cls.__doc__, 'methods': {
            m: getattr(cls, m).__doc__ for m in dir(cls)
            if not m.startswith('_') and any(s in m for s in
                ('bake', 'uv', 'mesh', 'bone', 'validat', 'texture', 'render', 'export', 'append', 'create'))}}
(OUT / 'unreal-capabilities.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
unreal.log('WC capability discovery complete: ' + str(OUT))
