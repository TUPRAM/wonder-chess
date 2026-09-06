"""Read-only capability inventory. Does not install, launch editors, or alter settings."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('reports/environment.json'))
    args = parser.parse_args()
    probes = {
        'python': (sys.executable, ['--version'], True),
        'git': (shutil.which('git'), ['--version'], True),
        'cpp_compiler': (shutil.which('g++') or shutil.which('clang++') or shutil.which('cl'), ['--version'], False),
        'blender': (os.getenv('BLENDER_EXE') or shutil.which('blender'), ['--version'], False),
        'unreal_editor': (os.getenv('UE_EDITOR_EXE') or shutil.which('UnrealEditor'), [], False),
        'unreal_uat': (os.getenv('UE_UAT_SCRIPT'), [], False),
        'powershell': (shutil.which('pwsh') or shutil.which('powershell'), [], False),
    }
    tools = {}
    for name, (candidate, arguments, safe_probe) in probes.items():
        exists = bool(candidate and Path(candidate).is_file())
        item = {'status': 'located_execution_unverified' if exists else 'not_located',
                'executable_basename': Path(candidate).name if candidate else None}
        if exists and safe_probe:
            try:
                completed = subprocess.run([candidate, *arguments], capture_output=True, text=True,
                                           timeout=10, check=False)
                item.update({'probe_exit_code': completed.returncode,
                             'version_output': (completed.stdout + completed.stderr).strip()[:1000]})
            except (OSError, subprocess.SubprocessError) as error:
                item['probe_error'] = str(error)
        tools[name] = item
    report = {
        'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'system': platform.system(), 'machine': platform.machine(),
        'python_version': platform.python_version(), 'tools': tools,
        'claims': {'blender_execution_verified': False, 'unreal_execution_verified': False,
                   'windows_package_verified': False},
        'notes': ['Not located does not prove software is absent from every disk location.',
                  'Set explicit environment paths locally; this script deliberately does not scan private directories.',
                  'Compiler and editor presence does not establish compatible SDKs or successful builds.'],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
