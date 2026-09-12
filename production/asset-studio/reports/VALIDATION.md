# AS1 validation report

**Prepared:** 2026-09-08. **Result:** standalone helpers tested; editor-dependent work unexecuted.

## Executed checks

| Check | Actual result |
|---|---|
| `python -m unittest discover -s tests -v` | 52 tests passed; exit code 0 |
| Asset route fixtures | All nine routes traversed with synthetic evidence |
| Skill inventory | 22 `SKILL.md` procedures present with declared names/descriptions |
| Helper source parsing | Six Python helper scripts parsed successfully |
| JSON parsing/schema fixtures | Passed the checks exercised by the test suite |
| Native reference crops | Eleven crops created from the supplied Ada concept; source hashes and rectangles recorded |
| Package construction | Manifest hashes and ZIP integrity checked after this report was written |

Environment: Python 3.13.5, Pillow 12.3.0, jsonschema 4.26.0. The tests used temporary directories and small synthetic image/audio fixtures. They did not run actual battles, model characters, evaluate an artist's approval or test Unreal.

## What the tests cover

Role requirements, missing/rejected/unexecuted checks, evidence presence, serious-defect blocking, separate declared reviewers, source/report/manifest changes, upstream staleness, safe output paths, lock/non-overwrite behavior, native crops, mask preconditions, route graphs, package contracts and Blender command construction. A dry-run command test is not a successful Blender operation.

## Not executed

Blender was not installed on the path and its `bpy` module was unavailable. The reference setup, scene audit and render scripts are therefore **local-verification candidates**. No Unreal Editor, import, cook/package, gameplay, live MCP, external generation service or protected human-review service was run.

No new Ada geometry, textures, rig, animation or replacement image was produced. Included reference images were supplied by the user; crops are not newly generated orthographic views. No real asset gate was approved. The current game repository and canonical asset files were not modified.

## Important limitations

The gate ledger records declared reviews, source hashes and dependencies. It does not inspect pixels, authenticate a human, prove an image came from Blender or prevent bypass by someone who can rewrite its metadata. Use a protected human-owned review mechanism for stronger operational enforcement. The included scripts do not implement automatic retopology, exhaustive mesh intersection/UV overlap checks, a new MCP server, a complete Unreal adapter or automatic asset promotion.

The first production test is the isolated Ada reference reconciliation and head/torso study, followed by real Blender and Unreal checks. Passing this package's tests does not imply any artistic, engine, performance or gameplay guarantee.

Detailed logs: `standalone-tests.txt`, `crop-generation.json`, `validation.json`.
