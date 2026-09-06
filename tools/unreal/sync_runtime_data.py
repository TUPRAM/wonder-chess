"""Validate and stage exact canonical data for the intentional Unreal JSON adapter."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
DESTINATION = ROOT / 'game/Content/WonderChess/SourceData'
ROW_HEADER = ROOT / 'game/Source/WonderChessRuntime/Public/WCDataRows.h'


def outputs() -> dict[str, bytes]:
    subprocess.run([sys.executable, str(ROOT / 'tools/validate_kit.py')], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / 'tools/compile_catalog.py'), '--check'], cwd=ROOT, check=True)
    sources = {p.relative_to(ROOT / 'data').as_posix(): p for p in (ROOT / 'data').glob('*.json')}
    sources.update({p.relative_to(ROOT / 'data').as_posix(): p for p in (ROOT / 'data/locales').glob('*.json')})
    for name in ('DT_Units_Alpha.json', 'DT_Abilities_Alpha.json'):
        sources['generated/unreal/' + name] = ROOT / 'generated/unreal' / name
    sources['generated/catalog_digest.json'] = ROOT / 'generated/catalog_digest.json'
    staged = {name: source.read_bytes() for name, source in sorted(sources.items())}
    rules = json.loads(staged['rules.alpha.json'])
    digest = json.loads(staged['generated/catalog_digest.json'])
    manifest = {
        'schema_version': rules['schema_version'],
        'balance_version': rules['balance_version'],
        'catalog_digest': digest['combined_sha256'],
        'alpha_unit_ids': rules['alpha_unit_ids'],
        'files': {
            name: {
                'source': sources[name].relative_to(ROOT).as_posix(),
                'bytes': len(content),
                'sha256': hashlib.sha256(content).hexdigest(),
                'sha1': hashlib.sha1(content).hexdigest(),
            }
            for name, content in staged.items()
        },
        'evidence': 'Byte-identical staging only; Unreal load and packaged use require execution.',
    }
    staged['runtime_stage_manifest.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    return staged


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if staged data differs; do not write files.')
    args = parser.parse_args()
    expected = outputs()
    existing = {p.relative_to(DESTINATION).as_posix() for p in DESTINATION.rglob('*') if p.is_file()}
    extra = existing - expected.keys()
    if extra:
        raise SystemExit('Unexpected staged files require review: ' + ', '.join(sorted(extra)))
    stale = []
    for name, content in expected.items():
        path = DESTINATION / name
        if args.check:
            if not path.is_file() or path.read_bytes() != content:
                stale.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.is_file() or path.read_bytes() != content:
                temporary = path.with_name(path.name + '.staging')
                temporary.write_bytes(content)
                temporary.replace(path)
    header_bytes = (ROOT / 'generated/unreal/WCDataRows.h').read_bytes()
    if args.check:
        if not ROW_HEADER.is_file() or ROW_HEADER.read_bytes() != header_bytes:
            stale.append('game/Source/WonderChessRuntime/Public/WCDataRows.h')
    else:
        ROW_HEADER.parent.mkdir(parents=True, exist_ok=True)
        if not ROW_HEADER.is_file() or ROW_HEADER.read_bytes() != header_bytes:
            ROW_HEADER.write_bytes(header_bytes)
    if stale:
        raise SystemExit('Stale runtime staging: ' + ', '.join(stale))
    print(f'PASS: {len(expected)} runtime data files and reflected row header ' + ('match exact source bytes and hashes.' if args.check else 'staged; engine loading remains to be verified.'))


if __name__ == '__main__':
    main()
