# BW2 preparation validation

## Actually executed here

- SHA256 check of both supplied Blender files, the supplied movie, review and verification JSON; all unchanged.
- Review and verification copied byte-for-byte into evidence/source.
- Full video decode: 169 frames; 680×880; 24 FPS; duration 7.041667 seconds. Video hash matches the supplied source report.
- Visual inspection of 22 sampled frames and selected native frames. This is NOT inspection of every frame at full resolution.
- Six native-resolution source stills and two temporal sheets retained in this package.
- 30 standalone synthetic geometry tests passed. Their log is math_tests.txt.
- Synthetic CLI executed; repeated output was rejected without changing the prior result.
- JSON files and Python syntax parsed; local linked image paths checked.
- ZIP CRC/integrity and per-file hashes checked after packaging.

## Not executed here

No Blender installation/bpy was available. No .blend was opened in Blender, modified, re-saved or re-rendered. No bone frame or pad coordinate was extracted from Ada's live scene. No grip IK, cloth correction, armor articulation, weight edit, source replay, second-body fitting, Unreal import or game test was executed.

The source report's 44-input preservation and 17 reopen checks remain source-reported, not repeated here. Source working and frozen hashes differ by design; semantic equality was not re-tested in Blender.

The optional helper is a geometric calculator, not a functioning Blender adapter. Its synthetic tests do not prove real grip quality. Every BW2 asset acceptance criterion remains NOT_RUN. No human approval or recipe promotion was issued.

## Deliverable boundary

A focused Codex task handoff, source evidence, incomplete measurement templates, and a small tested mathematical reference. Not a modeled asset, new engine feature, neural model, or replacement production pipeline.
