# Wonder Chess — Body Contact & Articulation BW2

**Purpose:** Resume the retained BW1 r003 candidate. Prove attachment and motion relationships before adding cosmetic detail or promoting recipes.

**Primary next deliverable:** one dimensioned, convincing anatomical-right sword grip that remains attached during wrist/arm motion, in an editable candidate. Shield grip and arm assembly follow only when their prerequisites work. Cloth and knee tasks are separately scoped, not obligations to finish everything in one run.

This is a task supplement to the existing AS1/BW1 workflow. It does not install another framework, replace Wonder Chess, approve artwork, modify the supplied Blender files, or claim that a new grip has already been made.

## Read order

1. `FIRST_MESSAGE_TO_CODEX.md`.
2. `docs/01_DIAGNOSIS_AND_SCOPE.md`.
3. `docs/02_GRIP_FRAME_AND_CONTACT.md` — primary assignment.
4. Read the corresponding section of `docs/03_ARM_CLOTH_KNEE.md` only when working on that assembly.
5. `docs/04_ACCEPTANCE_RUNTIME_AND_REPLAY.md` before integration or recipe promotion.

Use the existing local review and live-Blender tools. Do not copy a new root AGENTS.md, overwrite skills, download more models, or run a project bootstrap. Suggested location: `production/body-contact-bw2/`. Work in a separate new asset stage such as `stages/body-contact/BW2/r001/`; reconcile actual local paths first.

## Retain

The full indexed MPFB source, original 38 shape keys and BW1 six added target keys; head/hair work; approved reference/rear tabard split; right footprint-sole improvement; qualified CC0 glove/boot adaptations; frozen r003 and historical failures; canonical game and shared runtime skeleton; BW1 Solidify fixes.

A new candidate may change copied glove fit, weights, temporary poses, derived clothing topology and explicitly scoped armor attachments. Preserve original asset evidence. A derived garment need not preserve failed topology merely because the source body preserves its indices.

## Evidence supplied

The source report and verification are copied unchanged under `evidence/source/`. The source `.blend` files are not duplicated in this ZIP; use the original upload or local protected copy after hash validation. `evidence/input_manifest.json` records exact provided bytes. Native video extracts and two contact sheets are under `evidence/`; no generated or improved art is presented.

## Small optional numerical helper

From this packet root:

```powershell
python -m unittest discover -s tests -v
python tools/contact_math.py examples/synthetic_open_hand.json --output reports/synthetic_frame_run.json
```

Use a new output filename on each run; the CLI refuses overwriting. The example is synthetic, not Ada measurements. The helper constructs a proper hand frame, handles rigid relative transforms, and screens supplied contact points against a finite ideal cylinder. It does not pose fingers, inspect Blender meshes, test all collisions, or issue art approval.

No new dependency is required for the helper or its tests. The 30 supplied tests ran in this preparation environment; Blender-dependent work did not. Read `reports/VALIDATION.md`.

## Status language

- `MEASURED_LOCAL_FRAME`: the actual local calibration has evidence.
- `GRIP_PROOF_REVIEWABLE`: a candidate is numerically screened and visually reviewed, pending prescribed approval.
- `GRIP_ART_REVISE`: the candidate still fails its scoped grip review.
- `AUTHORING_ONLY`: runtime representation is unresolved.
- `REPLAY_CANDIDATE`: one successful operation has been parameterized, but second-body evidence is pending.

These are task-report labels, not replacements for the existing approval ledger. Do not generate human approval or reclassify major defects to pass a gate.
