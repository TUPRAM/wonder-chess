# 3. Learn construction recipes, not just collect files

## Four things that must not be conflated

An asset library stores shapes. A reference library stores images and observations. A procedural library stores repeatable operations. A trained model has parameters updated through a separate optimization/training process. AS1 skills and a folder of .blend files do not automatically update the model used by Codex. [codex_skills]

Our immediate deliverable is the first three, with measured usefulness. Neural training is a later candidate, not the default explanation for every modeling failure.

## The study-to-recipe loop

**Inspect -> explain -> adapt or rebuild -> deform -> compare -> replay -> generalize.**

For one licensed glove:

1. **Inspect:** record actual palm/thumb structure, open boundaries, cuff, UVs, groups and rest pose; capture underside and finger spaces, not only the most attractive angle.
2. **Explain:** write observed geometric facts separately from your hypothesis about how to construct it. A flattened imported FBX may contain no authoring history.
3. **Build:** adapt the licensed mesh or build a new envelope. Record which path was used and source ancestry. Do not describe adaptation as from-scratch generation.
4. **Deform:** test relaxed/open/equipment grips with the target hand. Review the glove and hand together.
5. **Compare:** use matched views and a criteria-based review for silhouette, fit, topology and movement separately.
6. **Replay:** run the executed procedure on an independent copy. A transcript of clicks is not necessarily a reproducible tool.
7. **Generalize:** use a second hand/body preset. Expose actual parameters and declared bounds rather than blindly increasing scale.

Use the same loop for a boot, pauldron or garment panel. Do not archive hundreds of variants before one construction survives replay.

## Minimal recipe contract

A proven recipe needs a stable ID/version, source licenses and hashes, required body/mesh/skeleton family, preconditions, semantic part selectors, parameter names and units, execution stages, outputs, validation checks, known failure modes and a tested applicability range.

An operation can be implemented through Blender Python or an approved native tool. Codex should call a stable operation with deliberate parameters rather than repeatedly regenerate a long untested script. Do not invent a working operation because a JSON example names it.

Use part IDs and persistent source correspondence where valid. Geometry-specific vertex indices must be bound to the exact source topology hash. Topology-changing operations invalidate later index-based edits unless a new verified mapping exists.

Parameter values must be inspectable and meaningful: sleeve length, cuff opening, allowance, shell thickness, pauldron overlap, handle clearance. Do not use unexplained 'quality=high' as a substitute for construction parameters.

Keep fitting correspondence, skinning weights, cloth pinning, thickness masks and rendering masks separate even when they all use Blender vertex groups.

## Episode data worth retaining

Each meaningful operation episode records:

| Field | Why it exists |
|---|---|
| Input reference identity and rights | Reproducible target and permitted data use |
| Before-state hash and topology family | Know what the operation actually acted on |
| Observed defect | Connect the action to a visible problem |
| Operation/parameters/version | Replay rather than paraphrase |
| After-state and matched renders | Inspect change instead of trusting narrative |
| Pose/geometry checks | Separate technical fit from visual likeness |
| Reviewer and accepted/rejected status | Distinguish labels from automated guesses |
| Reversion and failure reason | Useful negative examples and safe recovery |
| Lineage group and split assignment | Prevent sibling variants leaking between train/test |
| Tool/render/runtime versions | Identify environment effects |

Do not store hidden chain-of-thought as training material. Store concise observable decisions, tool actions, outcomes and human/technical labels.

The examples in `examples/` are empty proposals, not successful episodes. A recipe is not promoted on a schema test alone.

## Minimal benchmarks

Start with a small deliberately varied suite: one glove, one boot, one padded sleeve, one pauldron, one tunic, one belt. Repeat the promising parts on another compatible body before expanding. This is an exploratory engineering set, not a statistically representative dataset.

Measure time to first accepted candidate, human correction time, failed/repeated operations, visible clipping in required poses, source/engine roundtrip, style judgment and predictability of controls. Record accepted count / total attempted, not only successful screenshots.

As a suggested reuse gate, require two different body fits and an independent replay. This is a project rule to test, not proof of universal generalization. Keep failures in the denominator.

## Implementation sequence

Do not add a new 20-skill layer immediately. Extend existing AS1 skills after demonstrated need: source intake, MPFB body fitting, garment fitting, rigid costume fitting, and pose-based fit review. Retain the existing export/material/motion skills. Simple file metadata search is enough for a small library; embeddings and databases become useful only when retrieval quality or scale justifies them.

Keep the game moving while the recipe library improves. At least one output from every research iteration should be an asset candidate or a measured correction directly useful to Wonder Chess, not only more infrastructure.
