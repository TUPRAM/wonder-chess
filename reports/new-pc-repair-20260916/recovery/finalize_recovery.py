import collections, datetime, hashlib, json, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3]; OUT=pathlib.Path(__file__).resolve().parent
original=json.loads((ROOT/'reports/new-pc-20260916/missing-inventory.json').read_text())['paths']
manifest={}
for line in (ROOT/'TRANSFER_MANIFEST.jsonl').read_text().splitlines():
    r=json.loads(line)
    if 'path' in r:manifest[r['path']]=r
records=[json.loads(line) for line in (OUT/'restored.jsonl').read_text().splitlines()]
recovered={r['path']:r for r in records}
assert len(records)==len(recovered), 'Unexpected duplicate recovery record'
audit=[]
for p in original:
    row=manifest[p];path=ROOT/p
    record={'path':p,'expected_bytes':row['bytes'],'expected_sha256':row['sha256'],'recovery_recorded':p in recovered}
    if not path.is_file():record['status']='missing'
    else:
        raw=path.read_bytes();record.update(actual_bytes=len(raw),actual_sha256=hashlib.sha256(raw).hexdigest())
        exact=record['actual_bytes']==row['bytes'] and record['actual_sha256']==row['sha256']
        if exact:record['status']='restored_exact' if p in recovered else 'exact_present_unrecorded'
        elif p=='tools/blender/Start-Mcp.ps1' and p in recovered:record['status']='restored_then_intentionally_updated_by_main_agent'
        elif p not in recovered and '__pycache__' in p:record['status']='newly_generated_cache_not_recovered'
        else:record['status']='unexpected_mismatch'
    audit.append(record)
(OUT/'final-path-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
unresolved=[manifest[r['path']] for r in audit if r['status'] in {'missing','newly_generated_cache_not_recovered'}]
(OUT/'unresolved.json').write_text(json.dumps(unresolved,indent=2),encoding='utf-8')
active=[r for r in unresolved if r['path'].startswith(('tools/','tests/')) and '__pycache__' not in r['path']]
(OUT/'unresolved-active-source.json').write_text(json.dumps(active,indent=2),encoding='utf-8')
fsck=subprocess.run(['git','fsck','--full'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(OUT/'git-fsck-after.txt').write_bytes(fsck.stdout)
result={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'original_missing_count':len(original),'exact_recoveries_recorded':len(records),
    'recovery_source_counts':dict(collections.Counter(r['source']['kind'] for r in records)),
    'final_status_counts':dict(collections.Counter(r['status'] for r in audit)),
    'unresolved_original_payload_count':len(unresolved),'unresolved_active_source_count':len(active),
    'restored_groups':dict(collections.Counter(r['path'].split('/')[0] for r in records)),
    'unresolved_groups':dict(collections.Counter(r['path'].split('/')[0] for r in unresolved)),
    'git_fsck_exit_code':fsck.returncode,
    'scope':'Original 709 missing paths only; this is not a new full-manifest audit. Every recovery matched the immutable transfer size/SHA256 before and after writing. Existing files were never overwritten by recovery.'}
(OUT/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
lines=['# Exact missing-file recovery — 16 September 2026','',
    f"Recovered **{len(records)} of {len(original)} original missing files**, using only exact size and SHA-256 matches to the unchanged `TRANSFER_MANIFEST.jsonl`. **{len(unresolved)} original payloads remain unrecovered**, including **{len(active)} active source files**.",'',
    '## Verified result','',
    '- Recovery never overwrote existing files, reset/checked out/staged Git content, changed gameplay, or replaced older sources under current names.',
    '- Each recovery records its source and verifies the written bytes in [restored.jsonl](restored.jsonl).',
    f"- Final rehash statuses: `{dict(collections.Counter(r['status'] for r in audit))}`.",
    '- The main agent intentionally updated the restored `tools/blender/Start-Mcp.ps1` for the installed Blender path; its original matching bytes and restoration source remain recorded.',
    '- A cache produced by running Python is classified separately from an exact historical recovery.',
    f'- `git fsck --full` after recovery exited **{fsck.returncode}**. The recovered capture ref points to the existing tree object; index and branch refs remain untouched by recovery.','',
    '## Active source files still requiring original backup','',
    '| Path | Original bytes |','|---|---:|']
lines += [f"| `{r['path']}` | {r['bytes']} |" for r in active]
lines += ['','## Search performed','',
    '- Existing manifest-identical copies, including preserved older checkouts.',
    '- All available Git object metadata and eligible blobs, including dangling objects; original, LF, and CRLF representations.',
    '- 302,360 bounded newline/BOM/ref representations across 5,005 distinct normalized text blobs. This recovered the mixed-newline `tests/test_vnext_catalog.py` and the missing capture tree ref.',
    '- Unreachable Git trees indexed by missing source filenames; some retained versions predate the missing current files.',
    '- Size-matched files across this project, Downloads and Desktop; 16 local ZIP archives. No additional matches.','',
    '## Remaining payload and boundaries','',
    '- [Full unresolved inventory with expected sizes/hashes](unresolved.json)',
    '- [Final audit of all 709 original missing paths](final-path-audit.json)',
    '- [Machine-readable summary](summary.json)',
    '- [Post-recovery Git integrity output](git-fsck-after.txt)','',
    'The remainder includes historical Python caches/dependencies, migration evidence, download archives, validation evidence, and two files in the preserved r6 clean-study package. They are not declared disposable or recovered. A complete original folder or backup is required to finish exact recovery. The retained playable candidate packages were not changed. This report does not claim complete transfer integrity or a complete authoring/test pass.','']
(OUT/'README.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(result,indent=2))
