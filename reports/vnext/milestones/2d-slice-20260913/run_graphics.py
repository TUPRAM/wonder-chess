"""Run actual packaged UI captures and native engine automation in a single queue."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
ap=argparse.ArgumentParser()
ap.add_argument('--revision',default='r14')
ap.add_argument('--attempt',default='1')
ap.add_argument('--case',default='')
args=ap.parse_args()
evidence=Path(__file__).resolve().parent
root=evidence.parents[3]
exe=root/f'builds/WonderChess-2DSlice-{args.revision}/Windows/WonderChess/Binaries/Win64/WonderChess.exe'
cases=[
 ('lab-720',1280,720,['-WCLab','-WCLabExercise','-WCArtSlice'],'lab-exercise.json'),
 ('lab-1080',1920,1080,['-WCLab','-WCLabExercise','-WCArtSlice'],'lab-exercise.json'),
 ('status-1080',1920,1080,['-WCLab','-WCCueExercise','-WCArtSlice'],'lab-exercise.json'),
 ('solo-720',1280,720,['-WCSolo','-WCSoloExercise','-WCArtSlice'],'solo-exercise.json'),
 ('solo-1080',1920,1080,['-WCSolo','-WCSoloExercise','-WCArtSlice'],'solo-exercise.json'),
 ('comparison-lab-720',1280,720,['-WCLab','-WCLabExercise'],'lab-exercise.json'),
]
records=[]
for name,w,h,mode,result_file in cases:
 if args.case and name!=args.case:continue
 dest=evidence/f'{args.revision}-{name}-a{args.attempt}'
 dest.mkdir(exist_ok=False)
 command=[str(exe),*mode,'-WCProfileName=wonder_vnext','-WCCombatClarityExperiment','-unattended','-windowed',f'-ResX={w}',f'-ResY={h}','-nosplash','-UDPMESSAGING_TRANSPORT_ENABLE=0',f'-WCEvidenceDir={dest}',f'-abslog={dest/"engine.log"}']
 if '-WCSolo' in mode:command.append(f'-WCSavePath={dest/"preparation.wcsave"}')
 startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
 proc=subprocess.Popen(command,cwd=exe.parent,startupinfo=startup)
 (dest/'launch.json').write_text(json.dumps(dict(pid=proc.pid,executable=str(exe),sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),arguments=command),indent=2))
 deadline=time.monotonic()+180;result=None
 try:
  while time.monotonic()<deadline and proc.poll() is None:
   path=dest/result_file
   if path.exists():
    try:result=json.loads(path.read_bytes());break
    except(ValueError,OSError):pass
   time.sleep(.5)
  time.sleep(1)
 finally:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=15)
 checks=result.get('checks',result) if result else {}
 booleans={k:v for k,v in checks.items() if type(v)is bool}
 passed=bool(booleans) and all(booleans.values()) and result.get('passed',True) is True
 rec=dict(case=name,result_exists=result is not None,passed=passed,checks=booleans)
 records.append(rec)
 print(json.dumps(dict(case=name,passed=passed,false_checks=[k for k,v in booleans.items() if not v])),flush=True)
(evidence/f'{args.revision}-graphics-a{args.attempt}{("-"+args.case) if args.case else ""}.json').write_text(json.dumps(records,indent=2))
raise SystemExit(not records or not all(x['passed'] for x in records))

