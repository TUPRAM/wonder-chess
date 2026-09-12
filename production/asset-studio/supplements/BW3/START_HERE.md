# Wonder Chess — Collision-First Grip Recovery BW3

**A focused continuation of BW2. Design/instructions only; no new Blender asset or art approval is included.**

## Decision

Retain the calibrated BW2 hand frame, the fixed fixture, baseline pad definitions, the useful wrap study, and all protected sources. Change the order of work:

**valid hand shape and collision-free movement → neighbor clearance → handle contact → real equipment → runtime proof.**

The next assignment is not another whole-hand curl search. It may change a separately derived right-hand/body/glove region when diagnosis supports doing so. It must not change the indexed MPFB master or canonical game skeleton.

## Read order

1. `FIRST_MESSAGE_TO_CODEX.md` — the active bounded assignment.
2. `docs/01_FINDINGS_AND_DECISIONS.md` — evidence and the newly identified closure penetration.
3. `docs/02_THUMB_WEB_RECONSTRUCTION.md` — diagnose, correct, and integrate the hand.
4. `docs/03_ACCEPTANCE_AND_CONTACT.md` — measurements, animation coverage, and honest gates.
5. `docs/04_FIXED_GRIP_OPTION.md` — optional game-production branch; not silently substituted for animated-grip success.

Install this folder under the existing repository, for example `production/asset-studio/supplements/BW3/`. Do not overwrite AS1, BW1, BW2, AGENTS.md, or existing skills. No new extension, paid service, model download, AI training, or large framework is needed for this assignment.

## What is new

BW2's held contact screen covered frames 25–145. Read-only analysis of its supplied measurements finds penetration over the existing 0.5 mm screen in **21 closure frames, 4–24**. The largest recorded vertex penetration is **13.906720 mm at frame 14**. This is glove-versus-handle penetration, separate from the reported hand self-crossings.

The original phase label correctly means contact is not required during approach. It must not become permission to pass through the fixture. The new instructions require nonpenetrating movement during approach and contact only during the held interval.

See `evidence/BW2_phase_analysis.json`. Its inputs are provided unchanged and its small recomputation script is included. This analysis does not evaluate the .blend geometry or implement a collision solver.

## Source and next output

Source: `ada_bw2_grip_checkpoint_r001_ART_REVISE.blend`, SHA256
`d64d5900317541710d5ef29939d12559e5ecef31777a7e9261158cbccb7a41cf`.

Scene: `BW2_RIGHT_GRIP`; baseline inspection frame: 37. The actual local file may have newer work: inspect and reconcile, never overwrite it automatically.

Create an unused candidate directory below:
`art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW3/`.

The desired output is one corrected right-hand candidate and its real rendered/motion evidence. A method limitation should return a small, exact blocker and the next independent body task, not restart the entire pipeline.

## What this package does not establish

No Blender model was edited, saved, reopened, or rendered here. No hand self-collision was recomputed from mesh data. No Unreal or gameplay work was performed. The old movie's extracted images remain evidence of a rejected BW2 state. No source licenses or original modeling histories were altered.
