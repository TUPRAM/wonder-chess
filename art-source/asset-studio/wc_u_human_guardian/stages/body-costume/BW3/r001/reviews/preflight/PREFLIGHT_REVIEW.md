# BW3 bounded preflight

**No detected geometry, rig, shape-key, or action edits are present in the recovered live file.** The observed scene difference is its saved frame: recovery frame **9**, versus BW2 frozen frame **37**. The recovery's saved evaluated pose matches the baseline at frame 9, and both files evaluate identically at common frames 9 and 37. Root can stage the independent BW3 candidate while preserving the recovery snapshot.

## Recovery reconciliation actually executed

Fresh background Blender 5.1.1 opened both saved files with automatic script execution disabled. No `.blend` save, live MCP, modeling, collision query, or game test occurred.

- BW2 frozen baseline SHA-256: `d64d5900317541710d5ef29939d12559e5ecef31777a7e9261158cbccb7a41cf`.
- BW2 working file still matches SHA-256: `5c639f70facb63f5cc16f5a6ee57917606968e31170a41366c9f4a588d47750c`.
- Recovery `bw3_preedit_live_recovery.blend` SHA-256: `90b41de2b655069482eada4fcfe05f31c5fddcb6379335414cc1af8e2f3c5502`.
- All **69 mesh-object source records** match exactly: indexed coordinates/topology, UVs, group weights/order, source-index attributes, and shape-key coordinates/settings included by the reused BW2 helper.
- Modifier stacks, rest-rig bones/object bases, object hierarchy/action bindings, camera optics, scene settings/custom properties, object/scene inventory, and evaluated common-frame rig/object states match exactly.
- All three actions match exactly, including key coordinates, handles, interpolation, and easing: **492** old BW1 curves, **54** BW2 carry curves, and **3** camera curves. Fake-user flags and action slots also match.
- Baseline and recovery hashes were unchanged after the read-only evaluation.

`live_recovery_reconciliation.json` contains the result and an empty difference set for the compared fields. `saved_baseline_semantic_snapshot.json` and `live_recovery_semantic_snapshot.json` retain the detailed snapshots. This is a comparison of serialized, inspected data; screen layouts and other UI state were not treated as geometry, and changes omitted by the recovery save cannot be inferred.

## Package and provided tests

Read `tools/summarize_supplied_contact.py` and `tools/test_summary.py` before execution. They use standard-library JSON/numerical operations and do not invoke Blender, mutate scene data, or issue approvals.

- All **29/29** `MANIFEST.sha256.json` entries match both byte sizes and SHA-256 hashes. No unlisted package files were found, excluding the manifest itself.
- Executed only `python -B -m unittest discover -s tools -p test_summary.py -v` from the BW3 package root, using Python 3.11.8: **8 tests passed**, exit 0. `-B` prevented bytecode files in the package.
- All package files remain unchanged afterward.
- All **498** files sealed by `records/BW2_complete_before.json` remain unchanged, and all **62** older protected inputs still match their recorded hashes.

Full hash records and execution provenance are in `package_tests_and_preservation.json`; exact test output is `provided8_tests.txt`.

The summarizer analyzes supplied records; it performs no new geometry calculation. Its tested result preserves the distinction that contact need not exist before closure while **penetration still counts**: supplied closure frames **4–24** exceed 0.5 mm, reaching **13.906720174744448 mm at frame 14**. The 121 held frames remain within their sampled penetration screen. Those observations do not remove the separate thumb/web self-intersection failure or establish art/runtime/recipe acceptance.

**Preflight scope is complete.** No complete project suite, extra summarizer tests, source replacements, downloads, gameplay changes, or live-session operations were performed.
