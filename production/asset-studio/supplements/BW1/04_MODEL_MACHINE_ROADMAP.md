# 4. Toward a 2D-to-editable-3D model machine

## Product definition

The useful product is not 'one image produces an attractive render'. It is 'approved references produce a coherent, editable, fitting, rig-compatible asset with a documented route into Wonder Chess'. Exact recovery of unseen geometry from one stylized image is underdetermined: more than one 3D construction can create a similar projection. Treat hidden shape as a prior/proposed design, and request a second view when the ambiguity matters.

Initial supported domain: stylized humanoids, simple soft garments, separate rigid armor/equipment, and a small number of validated body families. Avoid starting with arbitrary creatures, loose layered cloth, flying anatomy and every possible art style.

## Architecture proposal

Reference input -> semantic part/layer graph -> rights-cleared retrieval -> constrained fitting -> specialist construction -> pose/clearance correction -> materials/rig/export -> visual and engine evaluation -> accepted recipe/episode library.

A garment is not the same task as an eyeball, armor plate or braid. Route by part type rather than asking one general vertex generator to solve them all.

### Components and proposed responsibilities

| Component | Input -> output |
|---|---|
| Reference interpreter | Images + user decisions -> parts, silhouette priorities, landmarks, confidence, uncertain regions |
| Asset retriever | Part requirements + rights policy -> suitable templates with provenance |
| Body fitter | Visible proportions + MPFB family -> editable body parameters and correspondence |
| Soft-garment fitter | Body envelope + construction template -> allowance, openings, seams and pose corrections |
| Rigid-part builder | Attachment regions + outlines/cross-sections -> thickness-controlled plates/gear |
| Contact evaluator | Equipment + body/rig poses -> grip/clearance defects and correction proposals |
| Render comparator | Matched observations -> visual mismatch regions; not one universal aesthetic score |
| Recipe executor | Versioned parameters/preconditions -> bounded Blender operations and outputs |
| Export evaluator | Candidate + actual Unreal contract -> calibrated engine-ready candidate or explicit failures |
| Dataset recorder | Executed episodes + permission labels -> lineage-aware records for future research |

These are proposed interfaces to implement only as repeated use earns them. They are not callable tools installed by this handoff.

## Phase A — no new model training

Start with existing image understanding, creator-authored/licensed bases, parametric body controls, a few original garment/armor templates and direct visual review. Use a small searchable catalog rather than scraping thousands of assets.

The expected advantage is a much smaller decision space: choosing a suitable glove and fitting a handful of meaningful dimensions, instead of generating every vertex from scratch. This is an engineering hypothesis, not a measured productivity claim from the MPFB head trial.

Exit evidence: one coherent dressed Ada; one second human/elf-compatible body; one stockier pilot showing which assumptions break; independently replayable glove/boot/sleeve/armor recipes. Do not count the same file renamed as a new successful variant.

## Phase B — fit parameters to references

After the recipes work manually, automate bounded searches over their meaningful parameters. Calibrate/reconcile camera and pose first. Mark shield/cloth occlusions and down-weight inferred/hidden landmarks.

A possible objective is a weighted combination of silhouette discrepancy, selected visible landmark error, surface regularity, garment clearance and shape priors. Not all components need a differentiable renderer; coordinate search or other bounded optimizers can be piloted against a small problem first.

The fitting objective must not win by distorting the camera, hiding geometry, inflating textures or memorizing one view. Evaluate side/back, the intended gameplay camera, required motion and an independent reference. A painted concept's lighting is not geometry ground truth.

Store uncertainty and several candidates when the reference cannot decide a shape. No arbitrary numerical '95% likeness' score.

## Phase C — build a deliberate dataset

Collect original and reviewed CC0 input meshes plus executed construction/correction episodes. Keep visual/adaptation permission and training permission/status distinct. An asset catalog license is not automatically a reviewed license for every imported texture, depiction, dependency or distribution scenario.

For geometry/image pairs, render the actual mesh with recorded cameras, masks, depth, normals, material IDs and several light conditions. Keep reference crops, canonical orientation/scale, part names, fit parameters, rig family and approved final geometry. Include edited before/after pairs for defect correction.

Synthetic expansion creates useful views but not new independent objects. For example, **30 part variants × 12 views × 3 lights = 1,080 renders**, still only 30 underlying variants. This is an arithmetic illustration, not a recommended sufficient training-set size.

Split siblings, recolors, near-duplicates and different-camera images from the same source together. Report two evaluations separately: interpolation within a known template family, and generalization to an unseen family/creator. Keep held-out assets and human-labeled defects fixed while tuning.

Retain failed trials with accurate causes, not as positive demonstrations. Separate suspected causes from confirmed intervention results. Do not use an automatic mesh checker as the label for 'beautiful'.

Objaverse's documentation includes per-asset license metadata; it is a mixed-license source, not blanket permission to ingest everything. Start curated and traceable before considering such collections. [objaverse]

## Phase D — train narrowly, only against a baseline

Good first learned tasks include template retrieval/ranking, parameter initialization from one or more images, a narrow pose-clipping detector, or a constrained choice among tested corrective operations.

For each, define input, output, metric, existing non-trained baseline and failure cost. Train only when you can evaluate whether it lowers correction work on held-out examples. A few hundred useful episodes may support an exploratory narrow study; this is not a guaranteed threshold and no sample size is claimed sufficient.

Fine-tuning a language model to propose valid action JSON does not automatically teach coherent geometry generation. A classifier that notices clipping does not fix it without an effective operation. An image model that recreates Ada's appearance does not itself create rig-ready topology.

A Codex skill is a procedure/resource package, not weight training. Do not claim the Pro account is learning new weights merely because it has opened files. Any actual training needs a separately supported model, implementation, data rights and compute plan. [codex_skills]

OpenAI's May 8, 2026 service notice says its fine-tuning platform is winding down and unavailable to new users. Therefore this architecture does not depend on being able to fine-tune the current Codex model or assume future API access. Re-check the chosen service at implementation time; an appropriately licensed trainable open model is a separate option. [openai_training_status]

## Phase E — optional existing image-to-3D models

Benchmark existing published systems on an isolated shield ornament, pouch or prop before considering training a general 3D generator.

- **TripoSR:** original project declares MIT for code and pretrained models; default single-image inference is documented at approximately 6 GB VRAM. Useful as a candidate-generation baseline, not a promise of polished game assets. [triposr]
- **TRELLIS.2:** Microsoft declares model/code MIT with separate dependency terms. Its documented tested environment is Linux and an NVIDIA GPU with at least 24 GB memory. Do not presume the current local PC satisfies this or install it into Blender's Python environment. [trellis2]

These generate candidate geometry, not automatically the required separate wardrobe, topology, weights, skeleton, UV quality, gameplay budget and likeness. Integration and correction remain part of the pipeline. Generated asset rights depend on inputs and applicable model/dependency terms; model-code licensing alone does not clear every source image.

Do not buy hardware, rent GPUs, subscribe to services or upload private assets without explicit authorization. Free model weights do not mean zero compute or operating cost. No system above was run or compared in this handoff.

## Milestones that keep the project useful

| Milestone | Tangible outcome | What would justify the next investment |
|---|---|---|
| Body pilot | Full MPFB-derived body plus useful limb/costume proofs | Shapes and poses succeed locally |
| Complete reference hero | Ada assembled and reviewed in Unreal | Source-to-engine pipeline works, not just clay |
| Recipe reuse | Same construction on another hero/body | Measured repeatability and known limits |
| Small generator UI | User chooses reference/template, fits parameters, sees previews | Recipes stable enough to expose as tools |
| Dataset and benchmark | Provenance, lineage splits, fixed tests, correction outcomes | Repeated failure type with sufficient evidence |
| Narrow learned component | Improvement over retrieval/optimization baseline | Held-out results improve without regressions |
| Broader machine | Multiple validated part/body families | Coverage expands through tests rather than assumptions |

Prefer one model-generation R&D lane alongside game production. The long-term machine should be built from the working game-asset pipeline, not delay the beta until general 3D generation is solved.
