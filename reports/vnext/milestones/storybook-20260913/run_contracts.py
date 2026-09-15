"""Verify the current packaged simulation suites without a graphics window."""
import argparse, hashlib, json, subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--revision', required=True)
args = parser.parse_args()
evidence = Path(__file__).resolve().parent
root = evidence.parents[3]
exe = root / f'builds/WonderChess-Storybook-{args.revision}/Windows/WonderChess/Binaries/Win64/WonderChess.exe'
dest = evidence / f'{args.revision}-engine-contracts'
dest.mkdir(exist_ok=False)
command = [str(exe), '-nullrhi', '-nosound', '-unattended', '-WCProfileName=wonder_vnext',
           '-WCCombatClarityExperiment', '-WCStorybook', '-UDPMESSAGING_TRANSPORT_ENABLE=0',
           f'-WCEvidenceDir={dest}', f'-abslog={dest / "engine.log"}',
           '-ExecCmds=Automation RunTests WonderChess.VNext', '-TestExit=Automation Test Queue Empty',
           f'-ReportExportPath={dest / "automation"}']
startup = subprocess.STARTUPINFO()
startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startup.wShowWindow = 0
proc = subprocess.Popen(command, cwd=exe.parent, startupinfo=startup)
(dest / 'launch.json').write_text(json.dumps(dict(executable=str(exe), pid=proc.pid,
    executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(), arguments=command), indent=2))
try:
    code = proc.wait(timeout=240)
except subprocess.TimeoutExpired:
    proc.terminate()
    proc.wait(timeout=15)
    raise
report = json.loads((dest / 'automation/index.json').read_text(encoding='utf-8-sig'))
summary = dict(exit_code=code, succeeded=report.get('succeeded'), failed=report.get('failed'),
               tests=[dict(name=t.get('fullTestPath'), state=t.get('state')) for t in report.get('tests', [])])
summary['passed'] = code == 0 and summary['succeeded'] == 2 and summary['failed'] == 0
(dest / 'verification.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary))
raise SystemExit(not summary['passed'])
