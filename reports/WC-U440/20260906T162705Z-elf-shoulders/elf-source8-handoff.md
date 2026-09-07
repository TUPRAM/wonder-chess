# Liora8 and Sylas8 source/export handoff

Both sources and exports are frozen. The existing continuous sleeve roots now extend into the torso with spine/upper-arm blending. This is an incremental repair to observed detached shoulders; costume, hair, gear, palette and the rest skeleton remain intact.

| Hero | Source / geometry / animation | LOD triangles | Retained animation FBXs |
|---|---|---|---|
| Liora | 8 / 8 / 6 | 3772 / 1885 / 933 | 7 /7 |
| Sylas | 8 / 8 / 7 | 3566 / 1779 / 884 | 6 /7 |

Each saved source passed skin/structural/all7 motion invariants,14 export hashes and3 actual independent mesh-FBX readbacks. Sylas Attack also passed a fresh actual animation-FBX import:40 frames at60fps,27 bones, finite poses and an animated left recovery guard. No animation timing or damage event was added.

For both heroes I inspected actual front/side/back/three-quarter renders,35 candidate deformation poses, and all7 final Cycles contact sheets. All14 source movies were encoded at20fps/1x with frame/duration readback. Those sampled frames and valid movies do not certify continuous visual approval.

## Liora

Source: `C:\Users\iputu\Documents\Wonder Chess\art-source\heroes\wc_u_elf_ranger\wc_u_elf_ranger.blend`
Source SHA256: `06ec80da5d8dacc6bdd87dbe504edc2e7f64560e85529fb7d22c82e127d63d4c`
Manifest SHA256: `ccd1c4f46895c156df97a4501d5c3e15d0415d4c22fdeeca19ef92a6ac5afea1`
Review: `C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T162705Z-elf-shoulders\liora-verified8`
Actual encoded source samples: 142 frames / 7100ms across7 clips.

## Sylas

Source: `C:\Users\iputu\Documents\Wonder Chess\art-source\heroes\wc_u_elf_rogue\wc_u_elf_rogue.blend`
Source SHA256: `223d2ed2a46e09387479ea854f555f0219ca3b5ce1138658f8956b065416b7d9`
Manifest SHA256: `8cbca14e3b99e37f0b94412a11950f0a2d7b4c659eca32c9211b82a87b460a1a`
Review: `C:\Users\iputu\Documents\Wonder Chess\reports\WC-U440\20260906T162705Z-elf-shoulders\sylas-verified8`
Actual encoded source samples: 141 frames / 7050ms across7 clips.

## Remaining limits

Sylas has a right strike followed by an off-hand recovery guard in one composite Attack cycle. The brief asks for alternating successive cuts; that runtime presentation remains open. Fine grip/cuff contact, cloth/gear intersections, bow draw, dash landing and crowded board readability remain continuous Unreal review obligations. No hero is labelled finished from this handoff.

## Retained failures and cleanup blocker

The first candidate selection failed before publication and is retained. The initial quick arm-review renderer wrote70 PNGs outside the workspace because its output path was relative. Both reviews were rerun successfully to fresh, resolved absolute paths under `arm-review-v2`; those are the current arm evidence.

Automatic approval review rejected the `tools.exec_command` PowerShell move/empty-directory cleanup action with **“blocked by policy”**, before execution. No retry or bypass was attempted. The two `C:/reports/WC-U440/20260906T162705Z-elf-shoulders/<liora-candidate8-v2|sylas-candidate8-v2>/arm-review` directories remain supplemental orphan evidence. Their exact paths and the denied action are recorded in the JSON.

Root may reimport the frozen exports now. The independent24 brief/20 portrait audit is in `brief-audit/24-hero-brief-audit.md`.
