# 05 — Acceptance and practical delivery

## Status vocabulary

- `NOT_RUN`: no execution evidence.
- `ART_REVISE`: a visible or geometric failure remains for this part's intended use.
- `LOCAL_READY_FOR_REVIEW`: the stated local tests were performed and no blocking local defect remains; not human approval.
- `SOURCE_CLIPS_REVIEWED`: actual current source animation was inspected on the candidate; not an engine pass.
- `ENGINE_REVIEWED_CANDIDATE`: an isolated engine candidate has been inspected, with provenance and limits.
- `HUMAN_APPROVED`: only an actual user approval of the specified scope, not inferred from “getting better.”

BW1/BW2/BW3 and MP1 retain their own historical status. The fixed hand does not clear their dynamic-grip or likeness gates.

## H1 — local fixed-hand criteria

The full selected glove exterior has a readable closed gesture with four fingers, an opposing thumb, and rounded web volume. No confirmed unintended self-crossing, degenerate surface or visible sharp fold. The actual selected handle fits; its guard and pommel do not cut into the hand. Pad contact is supported by inspected regions and surfaces, not a cherry-picked nearest vertex.

The cuff is structurally interpretable and no visible hole or discarded body is exposed. Any intentional hidden-body omission is declared in the export representation. License/provenance and source preservation are explicit. No “open-to-close” pass is reported.

## H2 — use in the existing game

The candidate uses the unchanged game skeleton, actual hand-space alignment, and one equipment chain. The seven source clips and representative blends preserve grip, wrist coverage and equipment clearance. Source and runtime checks are separate. Engine import must not update the shared rest pose or canonical asset silently.

For a source-only session, state exactly what could not be verified. Do not create a false engine-ready flag merely because FBX exists.

## A1/A2 — armor criteria

The bracer, breast/back and shoulder shells have deliberate profiles, thickness, edge treatment and fastening. They are not smooth primitives with rivets. Sleeve movement works with armor hidden. Plate movement does not expose empty underarm holes, create major interpenetration or turn steel into soft rubber. Detail and material work reinforce the approved forms.

Keep a full-character context view so improvements do not destroy proportion or silhouette. If head/hair remains pending, label it; do not use their absence to hide neck/collar clearance.

## Evidence worth producing

1. Three or four matched diagnostic hand views plus actual control surface, with the real sword and with it hidden.
2. A short full-resolution contact/wrist review and continuous playback of the seven source clips; engine capture separately when run.
3. Front, back, profile and three-quarter chest/shoulder views, sleeve-only and assembled action extremes.
4. One closeup explaining the wrist/bracer and one explaining shoulder overlaps.
5. A concise review table: goal, actual change, result, remaining defect, next dependency.
6. New editable work and frozen checkpoint, save/reopen evidence, source/content hashes, and explicit export allowlist.

Use recorded settings and real captures. No generated “after” artwork, camera changes presented as geometry improvement, hidden defective objects reintroduced by wildcard export, or screenshots falsely labeled as continuous animation review.

## Keep checking proportional to the change

Use existing tested collision/measurement helpers. Do not build a grasp simulator, collect a training dataset or create a new approval server for this run. Run all affected frames/poses and boundary checks; do not re-run unrelated gameplay suites after every vertex change.

Retain significant failures. Their provenance is useful, but a higher file count is not progress. Record which previously failed geometry relationship is now actually corrected.

## Suggested output names (new isolated paths)

```
stages/body-costume/BW4/r001/
  ada_fixed_hand_work.blend
  ada_fixed_hand_checkpoint.blend
  ada_armor_work.blend
  ada_armor_checkpoint.blend
  equipment_fit.json
  representation_decision.json
  actual_clip_matrix.json
  captures/
  motion/
  REVIEW.md
  verification.json
```

These are planned names, not files already produced by this package. Separate files may be combined if scene retention and independence are verified. Do not overwrite the old working file in the parent BW3 folder.

## Stop conditions and continuation

One initial construction plus two substantive corrective revisions per chosen method; do not reset the limit through renaming. A stopped hand does not inherit an armor pass. Independent chest/shoulder work can continue after a short local handoff, with explicit ownership.

If direct fixed-hand geometry still fails, report the exact geometry relationship and deliver a narrow specialist task. Do not silently resume the failed dynamic opposition search. Conversely, if the fixed output works, move on instead of adding an unnecessary opening animation.

## Reuse policy

A successful result may be stored as an **Ada-specific fixed-hand asset**. A repeatable fixed-grip recipe additionally needs a clean replay and a second supported fit. Neither result becomes a general animated-grasp training success. Armor can be reused as controlled templates only after another body/pose test; appendages of a different race need a separate fit.

## Final summary format

Lead with what geometry changed, which intended uses passed and what remains blocked. Give actual files and images. Separate authoring, source-animation, engine, user-approval and recipe claims. The phrase “finished hand” must specify whether it means a static study or the seven-clip game-ready candidate.
