#!/usr/bin/env python3
"""Stage isolated Blender source copies. Dry-run default; never launch Blender.

This protects against accidental replacement, not malicious concurrent filesystem
writers. 'baseline' is a workflow convention, not OS-enforced immutability.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def make_plan(source: Path, output: Path, expected_sha256: str | None = None) -> dict[str, Any]:
    source = source.expanduser()
    if source.is_symlink():
        raise ValueError('Choose an explicit source file, not a symlink.')
    source = source.resolve(strict=True)
    if not source.is_file() or source.suffix.lower() != '.blend':
        raise ValueError('Source must be an explicit .blend file; .blend1 is not an automatic baseline.')
    output = output.expanduser().resolve()
    if output.exists():
        raise FileExistsError(f'Output already exists; choose a new revision: {output}')
    if source == output or output in source.parents:
        raise ValueError('Output cannot be the source or an ancestor containing the source.')
    if expected_sha256 is not None:
        expected_sha256 = expected_sha256.lower()
        if not re.fullmatch(r'[0-9a-f]{64}', expected_sha256):
            raise ValueError('Expected SHA-256 must be 64 hexadecimal characters.')
    digest = sha256(source)
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError('Source hash differs. Inspect newer local work; do not overwrite it to match an upload.')
    return {'status': 'DRY_RUN', 'source': str(source), 'source_sha256': digest,
            'source_bytes': source.stat().st_size, 'output': str(output),
            'baseline_name': 'baseline_source.blend', 'candidate_name': 'ada_method_proof_work.blend',
            'geometry_evaluated': False, 'blender_executed': False,
            'note': 'Review unsaved Blender changes before copying disk files. Copies are not approved assets.'}


def exclusive_copy(source: Path, target: Path) -> None:
    with source.open('rb') as src, target.open('xb') as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)


def stage(plan: dict[str, Any]) -> dict[str, Any]:
    source, output = Path(plan['source']), Path(plan['output'])
    if sha256(source) != plan['source_sha256']:
        raise RuntimeError('Source changed after planning; inspect it before continuing.')
    output.mkdir(parents=True, exist_ok=False)
    # If an I/O error occurs, retain only this new partial directory for inspection.
    # Never delete user files or recursively clean an unexpected existing directory.
    baseline = output / plan['baseline_name']
    candidate = output / plan['candidate_name']
    exclusive_copy(source, baseline)
    exclusive_copy(baseline, candidate)
    expected = plan['source_sha256']
    if any(sha256(p) != expected for p in (source, baseline, candidate)):
        raise RuntimeError('Copy/source hash changed. Treat this new staging directory as invalid; original was not written.')
    result = dict(plan, status='STAGED_UNAPPROVED_SOURCE_COPIES',
                  staged_utc=datetime.now(timezone.utc).isoformat(),
                  baseline_sha256=sha256(baseline), candidate_sha256=sha256(candidate))
    with (output / 'staging_record.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--expected-sha256', default=None)
    parser.add_argument('--execute', action='store_true', help='Actually create a new directory and source copies.')
    args = parser.parse_args()
    try:
        plan = make_plan(args.source, args.output, args.expected_sha256)
        print(json.dumps(stage(plan) if args.execute else plan, indent=2))
        return 0
    except (ValueError, OSError, RuntimeError) as exc:
        print(f'MR1 STAGING ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
