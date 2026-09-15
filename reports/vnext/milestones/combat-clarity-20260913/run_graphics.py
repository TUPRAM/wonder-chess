import subprocess,json,time,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
project=root.parents[3]
exe=project/'builds/WonderChess-CombatClarity-r13/Windows/WonderChess/Binaries/Win64/WonderChess.exe'
cases=[('r13-lab-720',1280,720,['-WCLab','-WCLabExercise'],'lab-exercise.json'),('r13-lab-1080',1920,1080,['-WCLab','-WCLabExercise'],'lab-exercise.json'),('r13-status-1080',1920,1080,['-WCLab','-WCCueExercise'],'lab-exercise.json'),('r13-solo-1600',1600,1000,['-WCSolo','-WCSoloExercise'],'solo-exercise.json')]
records=[]
for name,w,h,mode,result_file in cases:
    dest=root/name;dest.mkdir(exist_ok=False)
    args=[str(exe),*mode,'-WCProfileName=wonder_vnext','-WCCombatClarityExperiment','-unattended','-windowed',f'-ResX={w}',f'-ResY={h}','-nosplash','-UDPMESSAGING_TRANSPORT_ENABLE=0',f'-WCEvidenceDir={dest}',f'-abslog={dest/"engine.log"}']
    if '-WCSolo' in mode:args.append(f'-WCSavePath={dest/"preparation.wcsave"}')
    startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    proc=subprocess.Popen(args,cwd=exe.parent,startupinfo=startup)
    (dest/'launch.json').write_text(json.dumps({'pid':proc.pid,'executable':str(exe),'sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'arguments':args},indent=2))
    deadline=time.monotonic()+150;result=None
    while time.monotonic()<deadline and proc.poll() is None:
        path=dest/result_file
        if path.exists():
            try: result=json.loads(path.read_bytes());break
            except (ValueError,OSError):pass
        time.sleep(.5)
    time.sleep(1)
    if proc.poll() is None:proc.terminate();proc.wait(timeout=10)
    checks=result.get('checks',result) if result else {}
    boolean_checks={k:v for k,v in checks.items() if type(v) is bool}
    passed=bool(boolean_checks) and all(boolean_checks.values()) and (result.get('passed',True) is True)
    record={'case':name,'result_exists':result is not None,'passed':passed,'checks':checks}
    records.append(record);print(json.dumps({'case':name,'passed':record['passed'],'false_checks':[k for k,v in record['checks'].items() if v is False]}),flush=True)
(root/'graphics-results.json').write_text(json.dumps(records,indent=2))
if not all(x['passed'] for x in records):raise SystemExit(1)
