"""Dry-run by default. Launch only the included tools in a separate Blender process.
Does not connect to or terminate an existing GUI/MCP session. No shell interpolation.
"""
from __future__ import annotations
import argparse,json,os,shutil,subprocess,sys
from pathlib import Path
ALLOWED={'scene_audit','reference_setup','render_review'}
def build_command(exe:str,source:Path,tool:str,arguments:list[str]):
    if tool not in ALLOWED:raise ValueError('Tool is not in the reviewed local allowlist.')
    source=source.resolve()
    if not source.is_file() or source.suffix.lower()!='.blend':raise ValueError('An existing .blend source is required.')
    resolved=shutil.which(exe) or (str(Path(exe).resolve()) if Path(exe).is_file() else None)
    if not resolved:raise ValueError('Blender executable not found. Configure the actual BLENDER_EXE.')
    script=Path(__file__).resolve().parent/'blender'/(tool+'.py')
    return [resolved,'--background','--factory-startup','--disable-autoexec','--python-exit-code','23',str(source),'--python',str(script),'--']+arguments

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--blender',default=os.environ.get('BLENDER_EXE','blender'))
    p.add_argument('--source',type=Path,required=True);p.add_argument('--tool',choices=sorted(ALLOWED),required=True)
    p.add_argument('--execute',action='store_true');p.add_argument('--timeout',type=int,default=600);p.add_argument('--log',type=Path)
    p.add_argument('arguments',nargs=argparse.REMAINDER);a=p.parse_args()
    try:
        args=a.arguments[1:] if a.arguments[:1]==['--'] else a.arguments
        cmd=build_command(a.blender,a.source,a.tool,args)
        print(json.dumps({'command':cmd,'will_execute':a.execute},indent=2))
        if not a.execute:return 0
        if not a.log:raise ValueError('Execution requires an explicit new --log file.')
        if a.timeout<=0:raise ValueError('Timeout must be positive.')
        a.log.parent.mkdir(parents=True,exist_ok=True)
        with a.log.open('x',encoding='utf-8') as log:
            log.write(json.dumps({'command':cmd})+'\n');log.flush()
            try:
                r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=a.timeout,check=False)
                log.write(f'\nEXIT_CODE={r.returncode}\n');return r.returncode
            except subprocess.TimeoutExpired:
                log.write('\nTIMEOUT: inspect output files before retry. No approval implied.\n');return 124
    except (ValueError,OSError) as exc:print(f'BLENDER RUNNER ERROR: {exc}',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
