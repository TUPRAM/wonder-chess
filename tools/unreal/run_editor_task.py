"""Run an owned editor task after full editor initialization and record its result."""
from pathlib import Path
import json
import os
import runpy
import traceback
import unreal

root=Path(unreal.Paths.project_dir()).resolve().parent
name=os.environ.get('WC_EDITOR_TASK','')
allowed={'import_arena','import_alpha_assets'}
if name not in allowed: raise RuntimeError('Select one known WC_EDITOR_TASK')
report={'task':name,'success':False,'engine':unreal.SystemLibrary.get_engine_version()}
try:
    runpy.run_path(str(root/'tools/unreal'/(name+'.py')),run_name='__main__')
    report['success']=True
except Exception:
    report['error']=traceback.format_exc()
    unreal.log_error(report['error'])
finally:
    output=root/'reports/editor-runs'
    output.mkdir(parents=True,exist_ok=True)
    (output/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    unreal.SystemLibrary.quit_editor()
