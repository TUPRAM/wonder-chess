"""Local asset review ledger. Does not generate art, invoke editors, or authenticate humans.

Approvals are declarations with content hashes, not cryptographic identity proofs.
Untrusted code with write access can bypass this tool. Use external permissions for enforcement.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import uuid
from datetime import datetime, timezone
from typing import Any
from contextlib import contextmanager

PACKAGE = Path(__file__).resolve().parents[2]
DEFAULT_RULES = PACKAGE / 'config' / 'routes.json'

class GateError(ValueError):
    pass

def load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise GateError(f'Cannot read JSON {path}: {exc}') from exc

def encoded(data: Any) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)+'\n').encode('utf-8')

def digest(data: Any) -> str:
    return hashlib.sha256(encoded(data)).hexdigest()

def file_hash(path: Path) -> str:
    h=hashlib.sha256()
    try:
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024*1024), b''):
                h.update(chunk)
    except OSError as exc:
        raise GateError(f'Cannot hash {path}: {exc}') from exc
    return h.hexdigest()

def utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def relative_path(root: Path, rel: str, exists: bool=True) -> Path:
    if not isinstance(rel,str) or not rel or '\\' in rel or ':' in rel:
        raise GateError('Use nonempty workspace-relative POSIX paths; no drive/UNC paths.')
    p=Path(rel)
    if p.is_absolute() or '..' in p.parts:
        raise GateError(f'Path escapes workspace: {rel}')
    root=root.resolve(); out=(root/p).resolve()
    try: out.relative_to(root)
    except ValueError as exc: raise GateError(f'Symlink/path escapes workspace: {rel}') from exc
    if exists and (not out.is_file() or out.stat().st_size==0):
        raise GateError(f'Evidence is missing, empty, or not a regular file: {rel}')
    return out

def write_new(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    try:
        with path.open('xb') as f:
            f.write(encoded(data)); f.flush(); os.fsync(f.fileno())
    except FileExistsError as exc:
        raise GateError(f'Refusing to overwrite {path}') from exc

def replace_json(path: Path, data: Any) -> None:
    temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        write_new(temp,data);os.replace(temp,path)
    finally:
        if temp.exists():temp.unlink()

@contextmanager
def locked(root: Path):
    path=root/'.assetctl.lock'
    try: fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError as exc:
        raise GateError('Workspace locked. Inspect owner/process before manual stale-lock recovery.') from exc
    try:
        os.write(fd,encoded({'pid':os.getpid(),'created_utc':utc()}));os.close(fd)
        yield
    finally:
        path.unlink(missing_ok=True)

class Studio:
    def __init__(self,root:Path,rules:Path=DEFAULT_RULES):
        self.root=root.resolve();self.rules_path=rules.resolve();self.rules=load(self.rules_path);self.manifest=load(self.root/'asset.json')
        self.validate_manifest()
        self.gates=self.rules['routes'][self.manifest['kind']]['gates']
        self.contract_hash=digest({'manifest':self.manifest,'rules':self.rules})

    def validate_manifest(self):
        m=self.manifest
        required={'schema_version','asset_id','name','kind','design_revision','rules_version','contract','rights'}
        if not isinstance(m,dict) or not required.issubset(m):raise GateError('Invalid asset manifest fields.')
        if m['schema_version']!='1.0.0' or m['rules_version']!=self.rules['version']:raise GateError('Version mismatch.')
        if not re.fullmatch(r'[a-z][a-z0-9_]{2,79}',m['asset_id']):raise GateError('Invalid stable asset ID.')
        if m['kind'] not in self.rules['routes']:raise GateError('Unsupported asset kind.')
        if not isinstance(m['contract'],dict) or not isinstance(m['rights'],dict):raise GateError('Contract and rights must be objects.')
        if not isinstance(m['design_revision'],str) or not m['design_revision'].strip():raise GateError('Missing design revision.')
        if not isinstance(m['name'],str) or not m['name'].strip():raise GateError('Missing name.')

    def assert_contract_current(self):
        current=digest({'manifest':load(self.root/'asset.json'),'rules':load(self.rules_path)})
        if current!=self.contract_hash:raise GateError('Manifest/rules changed during this operation; reopen workspace.')

    def state(self):
        p=self.root/'state.json'
        return load(p) if p.exists() else {'schema_version':'1.0.0','accepted':{}}

    def check_stage(self,stage:str):
        if stage not in self.gates:raise GateError(f'{stage} is not applicable to {self.manifest["kind"]}.')

    def accepted(self,stage:str,stack=None):
        self.check_stage(stage);stack=set(stack or [])
        if stage in stack:raise GateError('Gate dependency cycle.')
        stack.add(stage)
        rel=self.state()['accepted'].get(stage)
        if not rel:raise GateError(f'{stage}: no acceptance record')
        p=relative_path(self.root,rel);record=load(p)
        if record.get('stage')!=stage:raise GateError('Acceptance stage mismatch.')
        c=record['candidate']
        self.validate_snapshot(c,stack)
        if record['signoff'].get('candidate_sha256')!=digest(c):raise GateError('Acceptance digest mismatch.')
        required=self.gates[stage]['role']
        if record['signoff'].get('role')!=required:raise GateError('Acceptance role mismatch.')
        if not record['signoff'].get('acknowledged_review'):raise GateError('Review not acknowledged.')
        return file_hash(p)

    def validate_snapshot(self,c:dict,stack=None):
        self.assert_contract_current()
        stage=c['stage'];self.check_stage(stage)
        if c.get('contract_sha256')!=self.contract_hash:raise GateError(f'{stage}: manifest/rules changed; stale review')
        if c.get('asset_id')!=self.manifest['asset_id']:raise GateError('Asset identity mismatch.')
        if set(c['dependencies'])!=set(self.gates[stage]['deps']):raise GateError('Missing/extra dependencies.')
        for dep,h in c['dependencies'].items():
            if self.accepted(dep,stack)!=h:raise GateError(f'{stage}: upstream {dep} acceptance changed')
        for item in c['evidence']:
            if file_hash(relative_path(self.root,item['path']))!=item['sha256']:
                raise GateError(f'{stage}: evidence changed: {item["path"]}')
        if file_hash(relative_path(self.root,c['report_path']))!=c['report_sha256']:
            raise GateError(f'{stage}: original report changed')

    def report_template(self,stage):
        self.check_stage(stage)
        return {'schema_version':'1.0.0','asset_id':self.manifest['asset_id'],'stage':stage,'author':'REPLACE_WITH_AUTHOR',
                'method':'Describe actual operations and reviewed outputs.',
                'checks':[{'id':x,'status':'not_run','evidence':[],'notes':''} for x in self.gates[stage]['checks']],
                'artifacts':[], 'defects':[], 'executed_commands':[],
                'notes':['Not approved. Populate only after actual work and inspection.','Artifact fields: path (relative), category (source/image/video/audio/report).']}

    def prepare(self,report_rel):
        with locked(self.root):
            self.assert_contract_current()
            report_path=relative_path(self.root,report_rel);r=load(report_path)
            stage=r.get('stage');self.check_stage(stage)
            if r.get('asset_id')!=self.manifest['asset_id'] or r.get('schema_version')!='1.0.0':raise GateError('Report identity/version mismatch.')
            if not r.get('author') or 'REPLACE' in r['author']:raise GateError('Actual author declaration required.')
            if not isinstance(r.get('method'),str) or len(r['method'].strip())<10:raise GateError('Describe actual method.')
            deps={d:self.accepted(d) for d in self.gates[stage]['deps']}
            checks=r.get('checks',[])
            if len(checks)!=len(self.gates[stage]['checks']) or {x.get('id') for x in checks}!=set(self.gates[stage]['checks']):
                raise GateError('Required check inventory is incomplete or duplicated.')
            artifacts=r.get('artifacts',[])
            if not artifacts:raise GateError('No evidence artifacts.')
            seen=set();evidence=[]
            for a in artifacts:
                if a.get('category') not in {'source','image','video','audio','report'}:raise GateError('Invalid evidence category.')
                path=a.get('path')
                if path in seen:raise GateError('Duplicate artifact path.')
                seen.add(path);p=relative_path(self.root,path)
                evidence.append({'path':path,'category':a['category'],'sha256':file_hash(p),'bytes':p.stat().st_size})
            if not any(a['category']=='source' for a in evidence):
                raise GateError('List the actual source snapshot as evidence, not only captures.')
            if self.gates[stage]['visual'] and not any(a['category'] in ('image','video') for a in evidence):
                raise GateError('This gate requires actual image/video evidence.')
            if self.manifest['kind']=='audio' and stage not in ('brief',) and not any(a['category']=='audio' for a in evidence):
                raise GateError('Audio review requires a listening artifact.')
            for check in checks:
                if check.get('status')!='pass':raise GateError(f'{check.get("id")}: not an executed/reviewed pass')
                if not check.get('notes','').strip():raise GateError('Each check needs an actual observation.')
                if not check.get('evidence') or not set(check['evidence']).issubset(seen):raise GateError('Check evidence is absent or unlisted.')
            for d in r.get('defects',[]):
                if d.get('severity') not in ('critical','major','minor'):raise GateError('Unknown defect severity.')
                if d.get('status') not in ('fixed','open','accepted_minor'):raise GateError('Unknown defect disposition.')
                if d['severity'] in ('critical','major') and d['status']!='fixed':raise GateError('Unresolved critical/major defect blocks gate.')
                if d['status']=='accepted_minor':
                    required_exception=('reason','affected_use','owner','later_action')
                    if d['severity']!='minor' or any(not isinstance(d.get(field),str) or not d[field].strip() for field in required_exception):
                        raise GateError('A minor exception requires a reason, affected_use, owner and later_action.')
                if d['status']=='open':raise GateError('Open defect needs correction or explicit minor acceptance.')
            c={'schema_version':'1.0.0','asset_id':self.manifest['asset_id'],'stage':stage,'created_utc':utc(),
               'contract_sha256':self.contract_hash,'report_path':report_rel,'report_sha256':file_hash(report_path),
               'dependencies':deps,'evidence':evidence,'author':r['author'],'method':r['method']}
            rel=f'reviews/{stage}/candidate_{uuid.uuid4().hex}.json';write_new(relative_path(self.root,rel,False),c)
            return rel

    def approve(self,candidate_rel,reviewer,role,note,ack=False):
        if not ack:raise GateError('Explicit acknowledgement of reviewing actual evidence is required.')
        if not reviewer.strip() or not note.strip():raise GateError('Reviewer and note required.')
        with locked(self.root):
            c=load(relative_path(self.root,candidate_rel));stage=c['stage'];self.validate_snapshot(c)
            if role!=self.gates[stage]['role']:raise GateError(f'{stage} requires {self.gates[stage]["role"]}.')
            if role!='human' and reviewer==c['author']:raise GateError('Declare a separate review pass/reviewer, not the author.')
            record={'stage':stage,'candidate':c,'signoff':{'candidate_sha256':digest(c),'reviewer':reviewer,'role':role,
                    'note':note,'acknowledged_review':True,'created_utc':utc(),'identity_authenticated':False}}
            rel=f'reviews/{stage}/accepted_{uuid.uuid4().hex}.json';write_new(relative_path(self.root,rel,False),record)
            state=self.state();state['accepted'][stage]=rel;replace_json(self.root/'state.json',state)
            return rel

    def status(self):
        result=[]
        for stage,g in self.gates.items():
            try:self.accepted(stage);status='accepted_current';reason='Evidence hashes and dependencies match.'
            except (GateError,KeyError,TypeError) as exc:
                status='stale_or_invalid' if stage in self.state()['accepted'] else 'pending';reason=str(exc)
            result.append({'stage':stage,'status':status,'review_role':g['role'],'reason':reason})
        return result

def initialize(root:Path,asset_id:str,kind:str,name:str,rules:Path=DEFAULT_RULES):
    if not re.fullmatch(r'[a-z][a-z0-9_]{2,79}',asset_id):raise GateError('Invalid asset ID.')
    r=load(rules)
    if kind not in r['routes']:raise GateError('Unsupported asset kind.')
    if root.exists() and any(root.iterdir()):raise GateError('Initialize only an empty/new workspace, never a canonical asset folder.')
    root.mkdir(parents=True,exist_ok=True)
    manifest={'schema_version':'1.0.0','asset_id':asset_id,'name':name,'kind':kind,'design_revision':'draft_r1',
      'rules_version':r['version'],'contract':{'scope':'art_only_no_gameplay_changes','max_candidates_per_stage':2,'max_external_spend':0},
      'rights':{'status':'review_required','external_upload_authorized':False},'notes':['Not approved. Fill scope and budget before the brief gate.']}
    write_new(root/'asset.json',manifest);write_new(root/'state.json',{'schema_version':'1.0.0','accepted':{}})
    for folder in ['inputs','reports','reviews','exports']+[f'stages/{s}' for s in r['routes'][kind]['gates']]:
        (root/folder).mkdir(parents=True,exist_ok=True)
    return manifest

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rules',type=Path,default=DEFAULT_RULES)
    sub=p.add_subparsers(dest='command',required=True)
    init=sub.add_parser('init');init.add_argument('--workspace',required=True,type=Path);init.add_argument('--asset-id',required=True);init.add_argument('--kind',required=True);init.add_argument('--name',required=True)
    for cmd in ['status','report-template','prepare','approve']:
        s=sub.add_parser(cmd);s.add_argument('--workspace',type=Path,required=True)
        if cmd=='report-template':s.add_argument('--stage',required=True);s.add_argument('--output',required=True)
        if cmd=='prepare':s.add_argument('--report',required=True)
        if cmd=='approve':
            s.add_argument('--candidate',required=True);s.add_argument('--reviewer',required=True);s.add_argument('--role',required=True,choices=['human','art_reviewer','technical_reviewer']);s.add_argument('--note',required=True);s.add_argument('--ack-reviewed',action='store_true')
    a=p.parse_args(argv)
    try:
        if a.command=='init':out=initialize(a.workspace,a.asset_id,a.kind,a.name,a.rules)
        else:
            studio=Studio(a.workspace,a.rules)
            if a.command=='status':out=studio.status()
            elif a.command=='report-template':
                path=relative_path(studio.root,a.output,False);write_new(path,studio.report_template(a.stage));out={'template':str(path),'status':'not_run'}
            elif a.command=='prepare':out={'candidate':studio.prepare(a.report),'approved':False}
            else:out={'acceptance':studio.approve(a.candidate,a.reviewer,a.role,a.note,a.ack_reviewed),'identity_authenticated':False}
        print(json.dumps(out,indent=2));return 0
    except (GateError,KeyError,TypeError,OSError) as exc:
        print(f'AS1 ERROR: {exc}',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
