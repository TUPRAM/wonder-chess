# Ada: new clay study and face/hair method limit

**Status: REVISE. The new editable study exists, but it does not demonstrate the approved likeness. Ada is not finished.** Reference approval is current; modeled forms and final release remain unapproved.

Pram approved the reference identity and documented construction decisions on 2026-09-08, including retaining the rear tabard split. This allowed the new head, neck, torso, collar, hair and one shoulder study. All geometry in this AS1 study was built from scratch in the visible Blender session. The earlier canonical Ada and AQ1 candidate were not used as starting geometry.

Pram's subsequent feedback was **"Mostly face and hair"**. The focused r002 pass broadened the jaw, replaced the jagged initial eye outlines, revised brows and hair sweep, and retained the shortened braid and more closely nested shoulder plates. Root and a separate reviewer inspected actual Blender captures. Both still rejected the facial likeness and hair construction.

![Current restored clay study, unapproved](</C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r003/captures/three_quarter_restored.png>)

## Files to use

- [Current editable live file](</C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/live/ada_clay_study_r003.blend>) — the better r002 face/hair restored after the failed r003 regional experiment. This is the file loaded in Blender. At the final native-window check, the tool reported the window minimized; a restore attempt was interrupted by detected user input, so no further activation was attempted.
- [Frozen checkpoint](</C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r003/ada_clay_checkpoint.blend>) — retain unchanged; continue in a newly named working revision.
- [Face closeup](</C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r003/captures/face_restored.png>), [front](</C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r003/captures/front_restored.png>), [profile](</C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r003/captures/profile_restored.png>), and [back](</C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r003/captures/back_restored.png>).
- [Separate review of the restored forms](</C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r002/review_independent.md>) and [review of the failed regional method](</C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r003/review_method_limit.md>).
- [Session evidence and source hashes](</C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r003/session_report.json>).

## Defects that block advancement

The eyes read as raised almond patches with embossed iris relief. The lids, corners, cheek transition and brow structure do not establish Ada's calm, alert expression. Horizontal bands remain below the eyes, and the nose, lips, jaw-to-neck transition and ears need anatomical shaping. A technical mesh audit cannot approve these visible forms.

The hair reads as regular tubes above a cap. Profile and rear views expose raised arches, gaps, abrupt root transitions and mechanical braid gathering. The shorter braid is a useful proportion change, but neither it nor additional lock count proves the approved hairstyle.

The shoulder, chest and collar remain an early construction study. This partial bust cannot approve the whole hero. The rear tabard split is an approved future full-body construction decision, not geometry already completed in this bust.

## Why the last experiment was rejected

Code diagnosis linked the cheek bands to substantial orbital depth changes followed by all-axis smoothing inside a hard rectangular selection. The hair paths had nearly circular sections and no scalp-contact constraint. The r003 test therefore changed those relationships: spherical ocular geometry with a continuous lid patch, followed by a broad hair mass projected onto the actual scalp.

The actual captures still failed. The eye patch developed radial artifacts, excessive hollows and corner cuts. A later continuous spatial blend reduced the radial artifacts but did not yield acceptable lids. The supported hair mass pinched near the temple and lost the intended sweep. These are documented failures, not approved improvements.

The pre-experiment session and [failed regional proof](</C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/clay-study/r003/failed_region_proof.blend>) are preserved. The current live file restores the better r002 appearance while retaining hidden experimental geometry for diagnosis. Hidden experiments must be excluded from any later export. No export has been produced for this study.

## Verified technical boundary

The current saved scene has 53 visible source meshes and 189,972 evaluated triangles. The narrow source audit found zero degenerate faces, zero zero-length edges and zero inconsistent internal edge winding. Deliberate and unfinished boundaries remain; this is neither production topology acceptance nor a shipping triangle-budget pass. There are no armatures or actions.

The actual visible Blender session accepted edits and saved the new source. Native Computer Use selected and inspected the Blender window. The repaired launcher was run locally. All five enabled MCP tools passed against the final live file, with its disk hash unchanged by verification. See [verification.json](</C:/Users/iputu/Documents/Wonder Chess/reports/AS1/live-mcp/clay-session-final-verification/verification.json>). The verifier's image-success result is separate from the root's actual image inspection.

Current repository verification passed: 154 Python tests, 400 kit checks, 28 generated documents matching and six compiled catalog artifacts matching. All 22 authored clay operation scripts parsed. These results validate tooling and repository contracts; they do not turn the rejected art study into a pass.

No production UV/bake, texture/material stage, rig, skinning, animation, LOD, FBX, Unreal import/reimport or packaged test has been completed for this new Ada. Existing gameplay and old asset evidence remain separate.

## Next bounded work

The current formula-driven mesh method has not reached the reference. [wca-organic/SKILL.md](</C:/Users/iputu/Documents/Wonder Chess/.agents/skills/wca-organic/SKILL.md>) requires: "Two no-improvement attempts require a method review or focused human intervention." This study is held at that method limit; it is not being presented for whole-character approval.

The next useful operation is a focused artist-authored control cage or sculpt pass on one eye/socket/cheek and one asymmetric hair mass. Prove lid wrapping, corner construction, cheek continuity, calm expression and scalp contact in fixed front/profile/three-quarter captures before extending the method. Another broad formula-grid regeneration or more repeated tubes is not supported by these results.
