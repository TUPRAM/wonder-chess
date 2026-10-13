# Meshy four-view reference procedure — G2 and G3

**Pipeline 1.2 · 21 September 2026 · Required default for new creature geometry.**

Use [engineering sections 2–3](ENGINEERING.md#2-three-kinds-of-reference) to separate
identity, construction and generator inputs. Save the fixed pose/camera contract in
[camera-set.json](templates/camera-set.json); match framing and landmarks before
export. The [qualified studio tool](TOOLCHAIN.md#4-four-fixed-views-and-reference-comparison)
provides repeatable Unreal cameras and captures. Ambiguous hidden construction gets
a proxy/section review before generation, not a silently invented fourth side.

Use Meshy's **Main View, Left, Back and Right** inputs to describe one complete
creature. This implements the owner's requested feature shown in the Meshy panel.
Keep the Meshy → Unreal route, accepted colors and soft lighting standard. This
document edits the method; it does not authorize or execute a generation.

Four consistent views can constrain shape better than one. They do not guarantee
correct geometry, unseen interiors, usable topology or a good rig. Inconsistent
views can make reconstruction worse. Preserve existing accepted models; do not
regenerate Bellback or another approved asset just to retrofit this input method.

## 1. Four slots, one design

These are Wonder Chess's input conventions. Use four separate full-body files.

| Meshy slot | Our default image | What it must establish |
|---|---|---|
| **Main View** | Front, looking toward the creature's face or designated front | Identity, face/core, width, front contacts and main silhouette |
| **Left** | Camera looking at the creature's anatomical left side | Body depth, spine/torso profile, attachments on that side |
| **Back** | Rear, opposite Main View | Hindquarters/rear assembly, rear attachments and back surface |
| **Right** | Camera looking at the creature's anatomical right side | Opposite profile and genuine asymmetric differences |

For a floating assembly or plant, name its front and left/right in the construction
record before preparing images. A part on the creature's left appears on the
viewer's right in a frontal image. Record the camera direction and check Meshy's
actual thumbnail/slot presentation; never rely on screen position alone.

Do not horizontally flip Left to make Right. A hidden branch or limb may be
occluded; it has not disappeared from the design. Use the same part inventory in
all four views. Every feature should be identifiable wherever it is actually visible.

The default Main View is front-facing. If a particular asset needs a three-quarter
main image, record that specific exception and its exact accepted view set; keep
the other slots correctly identified. Do not silently relabel a three-quarter
illustration as a front view. Keep three-quarter beauty views, underside, open-jaw,
cutaway and exploded diagrams as **supplemental construction evidence**. They must
not replace a required slot or mix different poses into one generation set.

## 2. Prepare the images

**Owner-selected preparation tool: Krita.** On 21 September 2026 the owner chose
“Use Krita for precise reference preparation,” including making it the default for
scaling, padding and sheet assembly. Carry this choice forward without asking again.
Use image generation for missing visual information; use Krita for exact document
transforms. Do not ask a generator to redraw an accepted image just to add margins.

1. Start with the exact approved design revision and color direction. Keep its
   original files. Record whether each new image is an exact crop, a new drawing,
   an AI-inferred view, or an actual render of a named existing model. A render of
   a rejected model is not independent confirmation that the geometry is right.
2. Use one neutral rest pose across all four images: identical spine curve, root
   arrangement, jaw opening, petals, fins, tail and floating-part placement. Plan
   moving clearances in that pose. Do not impose a humanoid T-pose on a quadruped.
3. Keep the camera height, perspective and scale consistent. Prefer restrained
   perspective. Align body height and the contact/hover baseline; do not stretch
   a narrow front view to match a long side view's width. If canvas padding is
   needed, pad rather than distort anatomy. Retain branch, tail and toe tips.
4. Use a plain, visually separating background, even illumination and matching
   colors. Avoid cast-shadow shapes, sharp highlights, depth of field, motion blur,
   scenery, effect clouds, labels, dimension arrows or material swatches in uploads.
   Keep annotation on the review sheet, outside the four source images.
5. Prefer PNG as this project's interchange format. Preserve the original when
   converting another format; record the conversion and hash the actual upload.
   Web and API accepted formats differ; follow the verified interface, not its neighbor.
6. Inspect the images at useful zoom before submission. Increasing resolution of
   a blurry image does not restore missing anatomical evidence. Mark unresolved
   underside/internal construction explicitly for the later model review.

**Project starting convention:** use a consistent square canvas at 2048×2048 where
the source supports it, with padding around the whole creature. This is an authoring
preference, not a Meshy minimum or proof of detail. Do not regenerate accepted art
solely to satisfy a canvas size.

### Repeatable Krita preparation

1. Make a new view-set revision; record source hashes before opening the originals.
2. Record the intended canvas, color profile, image-space landmarks, uniform scale
   and translation for each view. Distinguish manual pixel estimates from measured
   3D correspondence. Never normalize a long side view to a narrow front-view width.
3. Scale a working copy uniformly using Krita. Pad the canvas without stretching
   the creature. Save the transformation/interpolation recipe: resampling changes
   bytes even when no color adjustment was applied.
4. Keep background padding free of streaks or seams that could be mistaken for
   geometry. Extending edge pixels is suitable for a diagnostic trial only when
   the background stays clean; inspect the exported PNG, not just the canvas size.
5. Save individual `.kra` sources and clean PNGs, plus a layered review sheet with
   labels outside the images. Record profiles, PNG hashes and source-integrity checks.
6. Inspect head, shoulders, hips, attachments and every contact. Matching tail-top
   and lowest-paw coordinates only aligns framing; it cannot repair different poses
   or head/body proportions. Keep G2 open when those differ. Use the construction
   proxy route in [engineering](ENGINEERING.md#2-three-kinds-of-reference) when needed.

The [Cragstoat Krita recipe](../../art-source/asset-studio/wc_vn_cragstoat/stages/production_r001/recipes/krita_align_references.py)
was executed inside Krita 5.3.4 Scripter. It is a candidate-specific example, not a
universal set of landmarks. Copy it to a new recipe, replace all source/output paths
and measured landmarks, and preserve existing revisions before running it.

## 3. If a view is missing

Use an existing consistent reference when available. Otherwise prepare a proposed
missing view with authorized image tools, including Meshy's view-generation helper
when appropriate. The helper's small **Generate / Generate Multi-View** action
creates reference images; the model's **Generate** action starts 3D production.
They are separate operations with separate receipts when jobs are exposed.

Before either operation, check its actual allowance, upload scope and settings.
The public tutorial's price or "free" label is not evidence of the account's current
entitlement. Carry forward existing applicable authorization; do not ask for it again.

After view generation, save and review all four images. An AI-generated back is an
inference, not an observation of an approved hidden surface. Compare it with the
construction inventory. Correct inconsistent views before generating the mesh.
Do not rely on unseen automatic completion at 3D submission. If the interface cannot
expose/preserve the generated views for review, prepare them separately or record
the blocked step. Do not silently fall back to one image or Batch Images to 3D.

## 4. G2 consistency review

Create a four-panel review sheet labeled **Main / anatomical Left / Back /
anatomical Right**, and keep the four original upload files separate. This sheet
is a review artifact; the four individual images are the default Meshy inputs.

Check and record:

- **Identity:** matching face, muzzle/core, body proportions and silhouette.
- **Inventory:** the same approved limbs, roots, toes, pipes, petals, fins and
  accessories, including parts hidden in some views. Do not invent counts from
  a class label or copy Bellback's counts into another hero.
- **Attachment:** matching parent part, height, side and clearance. Follow a branch,
  tail or pipe around the creature rather than judging each image independently.
- **Pose:** matching joint positions and opening states, including the far limbs.
- **Color:** the same bark/moss/stone/ceramic/glass regions across visible surfaces.
- **Framing:** no crop or distortion; consistent camera elevation and body scale.
- **Coverage:** a real rear and two distinct sides; unresolved hidden surfaces named.
- **Origin:** originals versus crops versus inferred views labeled truthfully.

Use the [character-specific checks](CHARACTER_BRIEFS.md). If a mismatch is critical,
revise the offending view and inspect the set together again. Do not expect four
conflicting pictures to average into the intended design.

Record the owner's exact G2 decision on the whole view set and construction record,
with hashes. Existing approval of the same unchanged set remains valid. A new
inferred side or revised rear is a new reference revision, not inherited approval.
Shared G1 lighting remains a prerequisite for G3; G2 preparation may run alongside it.

**Owner-directed trial tolerance:** exact pixel registration is not a goal by
itself. The owner allowed small Cragstoat alignment differences on 21 September
2026 and approved one geometry-only trial, with final color/lighting review later.
For that scope, keep the current four images and inspect the generated geometry;
do not keep redrawing them or require a proxy solely to perfect alignment. Record
the remaining discrepancies and the actual approval/hash/cost limit. This does not
claim that Meshy will repair them or waive limb counts, geometry, rig or final look
review. Other stage-order exceptions also need an actual owner instruction.

## 5. Submit through the website

After G1/G2 and the concrete job scope are ready:

1. Open **Image to 3D**, select the currently supported model/mode, and enable
   **Multi-view**. Use the mode where all four slots are available. If a topology
   mode hides them, use the documented geometry route and remesh afterward.
2. Fill **Main View → Left → Back → Right** from the accepted view-set record.
   Open/inspect the previews; filenames alone do not prove correct slot assignment.
3. Confirm all four are present, correctly oriented and unchanged. Save the actual
   slot preview, model/mode, geometry resolution and toggles as preflight evidence.
4. Keep the first pass geometry-only, consistent with the handbook. Record the
   visible cost before submitting. Disable unrequested texture/split/extra options;
   an Ultra default must not silently exceed the authorized budget.
5. Submit one authorized job and save its ID/result. Apply the existing uncertain-
   submission reconciliation procedure before any retry.

The [Meshy tutorial](https://www.meshy.ai/tutorials/multi-view-image-to-3d) documents
the four slots, web PNG/JPG/JPEG/WebP uploads up to 20 MB each, and the mode-specific
availability of Multi-view. Recheck these details in the actual account before use.
Public labels may lag newer model versions; record what was actually selected.

## 6. Automation mapping — do not assume MCP support

Website slot assignment and API array order are different interfaces. Keep a local
`main, left, back, right` order for auditable requests. Inspect the installed MCP
tool schema first; if it accepts only one image, it cannot perform this four-view
job. Use the website or a verified multi-image API path within the same authorization.
Do not issue four single-image jobs.

The current [Multi-Image to 3D API](https://docs.meshy.ai/en/api/multi-image-to-3d)
uses `/openapi/v1/multi-image-to-3d` with `image_urls` accepting 1–4 PNG/JPEG images
as URLs or data URIs. For `meshy-7.1`, first is primary/front; remaining order is
unconstrained. Pin the supported version. Our normal request supplies four images,
with `should_texture: false`; no executable paid request is embedded here.

Texture references use the independent `texture_image_urls` array; geometry inputs
do not automatically populate it. That field requires supported `meshy-7.1`/`latest`
and `should_texture: true`, and conflicts with `texture_image_url` and `texture_prompt`.
Verify the selected endpoint before building a separate texture request.

Record actual transmitted image hashes and order without publishing private art to
a public host merely to make an API URL. Preserve sanitized settings and receipt;
avoid logging credentials or image data URIs as massive request dumps. Confirm
parameter spelling and capability against current docs before submission.

## 7. Compare geometry, then texture using the accepted views

Compare the geometry-only result with all four inputs using matched front, side,
rear and opposite-side views in neutral/clay shading. Review silhouette and actual
attachment geometry, not only a pleasing Main View. Color/texture checks remain
`NOT_RUN` until the separately authorized textured result exists; then repeat the
matched views in textured shading. Inspect supplemental underside, interior and
difficult-joint evidence separately. Record per-view defects in G3.

Proceed through geometry review, remesh/UV and texturing as documented in
[MESHY.md](MESHY.md). Prefer the accepted four-view color set for multi-view texturing
when supported. Inspect carried-over slot previews rather than assuming they are
correct. A deliberately different texture reference set needs its own identity and
review. Preserve the accepted final Meshy base color; do not compensate by recoloring
in Unreal. Use the existing 2K starting texture budget.

**Material-map limitation:** Meshy's website
[Multiview Upgrade description](https://www.meshy.ai/blog/multiview-upgrade) currently
describes multi-view texture output as base color only. Its API separately exposes
PBR options. Treat that as an interface/capability distinction requiring verification,
not a guarantee that a website download contains roughness, metallic and normal maps.
Inventory the actual maps. Record missing maps; use a reviewed material-property
solution or a supported separately scoped map-generation step. A base-color-only
result cannot pass a check requiring delivered PBR maps by relabeling it.

## 8. Records, revisions and handoff

Use [view-set.json](templates/view-set.json). Before generation, preserve:

```text
art-source/asset-studio/<asset_id>/inputs/references/four_view_r001/
  01_main_front.png
  02_left.png
  03_back.png
  04_right.png
  view-set.json
  review-sheet.png
  supplemental/
```

Names above illustrate a PNG set; record actual extensions. Keep reference job IDs,
source hashes, transformations and review evidence with the set. The candidate and
every geometry/texture receipt reference its immutable record/hash. The generation's
`input-images/` archive preserves the exact submitted bytes and mapping even if
the working reference folder later changes. Supplemental images are not extra API
inputs beyond the selected four.

Changing any view creates a new set revision and reopens the affected G2/G3 evidence.
It does not silently replace a pending job's inputs, invalidate an older accepted
package for its original use, or authorize another charged generation. Preserve the
original source, resulting geometry and rejected attempts for comparison.

The [official best-practices guide](https://help.meshy.ai/en/articles/16102789-meshy-multi-view-best-practices-angles-and-images)
supports using consistent views and reviewing inputs; more images alone do not
prove greater accuracy. Provider sources in this manual were checked 21 September 2026.

**Completion of this document is not completion of a four-view trial.** The method,
slots and records are defined; actual images, account capability and improved model
accuracy must be demonstrated in the next authorized production candidate.
