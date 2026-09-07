"""Read-only reflected API/marker probe. It loads one existing sequence and never saves assets."""
from pathlib import Path
import json
import os
import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
output = Path(os.environ['WC_EDITOR_REPORT_DIR']).resolve()
output.mkdir(parents=True, exist_ok=True)
report_path = output / 'attack-window-api-probe.json'
if report_path.exists():
    raise RuntimeError('Existing probe evidence will not be overwritten')
report = {'status': 'STARTED', 'boundary': 'Read-only reflected API and existing sequence query; no saves or imports', 'engine': unreal.SystemLibrary.get_engine_version()}
try:
    api = unreal.AnimationLibrary
    names = ('get_animation_sync_markers', 'remove_animation_sync_markers_by_name',
             'is_valid_anim_notify_track_name', 'add_animation_notify_track', 'add_animation_sync_marker')
    report['script_class'] = 'unreal.AnimationLibrary'
    report['callable_methods'] = {name: callable(getattr(api, name, None)) for name in names}
    if not all(report['callable_methods'].values()):
        raise RuntimeError('Required reflected method absent')
    sequence = unreal.load_asset('/Game/WonderChess/Heroes/wc_u_elf_mage/AN_wc_u_elf_mage_Attack')
    if not isinstance(sequence, unreal.AnimSequence):
        raise RuntimeError('Existing Neris Attack sequence missing')
    report['sequence'] = sequence.get_path_name()
    report['sequence_seconds'] = float(sequence.sequence_length)
    report['markers'] = [{'name': str(marker.marker_name), 'time': float(marker.time)} for marker in api.get_animation_sync_markers(sequence)]
    report['owned_track_present'] = api.is_valid_anim_notify_track_name(sequence, 'WC_Attack_Windows')
    report['status'] = 'PASS_READ_ONLY_API_QUERY'
except Exception as error:
    report['status'] = 'FAIL'
    report['error'] = repr(error)
    raise
finally:
    report_path.write_text(json.dumps(report, indent=2)+'\n')
