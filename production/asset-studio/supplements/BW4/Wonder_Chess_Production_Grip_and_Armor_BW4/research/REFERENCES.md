# Research directory — what to study and what it proves



This is a curated reference set, not a claim that every linked asset or video was downloaded and tested. Source-supported observations are separated from our proposed applications. Technical controls should be verified in the installed Blender 5.1.1 / local Unreal versions; references to later documentation do not authorize an upgrade.



**Working study order:** S01 for hand masses; S13/S14 for glove-versus-plate construction; S16/S17 for chest shells; S04–S07 while modeling; S08–S12 for binding and import. Inspect one relevant reference before the corresponding operation. Do not consume the entire directory instead of modeling.



## Primary references



### S01 — Proko — Muscle Anatomy of the Hand

Source: https://www.proko.com/course-lesson/how-to-draw-hands-muscle-anatomy-of-the-hand/

**Access checked:** Public lesson text reviewed; premium downloads not obtained

**What the source supports:** The lesson distinguishes palmar thumb mass, dorsal thumb mass, pinky-side mass, and the changing web relationship.

**Our proposed use:** Shape a substantial thenar pad and a rounded thumb/index web rather than a stretched flat membrane.

**Limit:** An art-anatomy lesson, not a Blender recipe or a numeric contact standard. Do not redistribute its protected lesson media.



### S02 — Proko — Hands Holding Stuff N Things

Source: https://www.proko.com/course-lesson/hands-holding-stuff-n-things

**Access checked:** Public description only; full lesson NOT viewed

**What the source supports:** The public description concerns hands holding objects.

**Our proposed use:** Optional further study of enclosure and contact; not a dependency for this task.

**Limit:** Premium material. No purchase, access, timestamped procedure or full-video analysis is claimed.



### S03 — Blender — Human Base Meshes v1.4.1

Source: https://www.blender.org/download/demo-files/

**Access checked:** Indexed official listing reviewed; archive NOT downloaded

**What the source supports:** The listing identifies a 49 MB CC0 bundle requiring Blender 4.2 LTS or newer.

**Our proposed use:** An optional alternative editable foundation if the existing derived glove cannot be remodeled efficiently.

**Limit:** Inspect the actual archive and its component inventory before choosing a hand. This bundle is not a pre-fitted Ada grip.



### S04 — Blender 5.1 — Poly Build

Source: https://docs.blender.org/manual/id/5.1/modeling/meshes/tools/poly_build.html

**Access checked:** Documentation reviewed; title/interface text partly localized

**What the source supports:** Poly Build combines vertex/face creation, moving and edge extrusion for mesh construction and retopology.

**Our proposed use:** Rebuild the thumb web and reconnect digit roots with explicit faces.

**Limit:** Use the installed keymap and preview each operation. The tool does not determine anatomy.



### S05 — Blender 5.1 — Bevel Modifier

Source: https://docs.blender.org/manual/en/5.1/modeling/modifiers/generate/bevel.html

**Access checked:** Documentation reviewed

**What the source supports:** Bevel has selectable edge control, width interpretation, overlap clamping and normal-treatment options.

**Our proposed use:** Author a restrained edge highlight on plate rims without rounding away the entire shape.

**Limit:** Overlap clamping is not an assembly-level collision solver. A shading fix cannot repair a bad silhouette.



### S06 — Blender 5.1 — Solidify

Source: https://docs.blender.org/manual/pt/5.1/modeling/modifiers/generate/solidify.html

**Access checked:** Documentation reviewed; localized page with English technical passages

**What the source supports:** Thickness is computed in local coordinates; uniform thickness remains an approximation.

**Our proposed use:** Make measured armor shells on new candidates; inspect real section thickness and normals.

**Limit:** Do not re-enable the known failing even-offset settings on the preserved BW1 garments. No guarantee of collision-free thickness.



### S07 — Blender 5.1 — Apply Pose

Source: https://docs.blender.org/manual/id/5.1/animation/armatures/posing/editing/apply.html

**Access checked:** Documentation reviewed

**What the source supports:** Pose as Rest Pose changes the armature rest state and affects the skinning relationship.

**Our proposed use:** Avoid changing the shared rig merely to freeze a hand; transform independent geometry into its verified bind space.

**Limit:** This is not a command to apply the current MPFB pose to the shared game skeleton.



### S08 — Blender — PoseBone matrix semantics

Source: https://docs.blender.org/api/4.5/bpy.types.PoseBone.html

**Access checked:** Matrix semantics reviewed in the documented 4.5 API; local 5.1 API still to verify

**What the source supports:** PoseBone.matrix is the final matrix in armature object space, distinct from matrix_basis.

**Our proposed use:** Include the armature world transform exactly once in hand-local capture and bind-space reconstruction.

**Limit:** The equations in this kit are a proposed transform contract, not code executed on Ada; verify installed API and actual objects.



### S09 — MPFB — Export Copy

Source: https://static.makehumancommunity.org/mpfb/docs/exporting/export_copy.html

**Access checked:** Documentation reviewed

**What the source supports:** Export-copy operations preserve the original character while preparing a derived output hierarchy.

**Our proposed use:** Keep indexed MPFB masters intact and explicitly author a separate fixed-hand output representation.

**Limit:** Choose operations deliberately; baked subdivision, modifiers and masks can change output geometry. No installed-version test performed here.



### S10 — Epic — Skeletal Mesh Sockets

Source: https://dev.epicgames.com/documentation/unreal-engine/skeletal-mesh-sockets-in-unreal-engine

**Access checked:** Documentation reviewed

**What the source supports:** Sockets carry bone-relative attachment offsets; mesh-specific sockets can be used when a shared skeleton needs asset-specific attachments.

**Our proposed use:** Verify the actual sword attachment and isolate any candidate offset instead of editing all characters' shared socket.

**Limit:** Docs may describe a newer engine than the local project. Do not upgrade or mutate the canonical skeleton implicitly.



### S11 — Epic — FBX Import Options Reference

Source: https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-import-options-reference-in-unreal-engine

**Access checked:** Documentation reviewed

**What the source supports:** Import settings include skeleton/reference-pose changes and separate normal/tangent policies.

**Our proposed use:** Use an isolated import, preserve reference pose, and verify the selected normal convention.

**Limit:** An import success is not an art or animation pass; map settings to the actual installed importer.



### S12 — Epic — FBX Skeletal Mesh Pipeline

Source: https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-skeletal-mesh-pipeline-in-unreal-engine

**Access checked:** Documentation reviewed

**What the source supports:** The pipeline supports skeletal meshes/animations and recommends controlling triangulation.

**Our proposed use:** Export a reviewed runtime copy with explicit triangulation and test it on the existing clips.

**Limit:** The documented FBX 2020.2 pipeline does not imply Blender exports an identical SDK/version; use the already calibrated local profile.



### S13 — The Met — Gauntlet for the Right Hand, 29.158.215

Source: https://www.metmuseum.org/art/collection/search/23255

**Access checked:** Collection page and search-returned palm image reviewed

**What the source supports:** The record identifies a Milanese steel-and-gold gauntlet; the palm image shows construction unlike the plated dorsal side.

**Our proposed use:** Study separation of the palm covering, finger backing and cuff; keep Ada's palm comparatively simple.

**Limit:** Do not infer a complete moving mechanism from one still. This is historical structure inspiration, not Ada's final design.



### S14 — The Met — Right Gauntlet, 2002.507

Source: https://www.metmuseum.org/art/collection/search/26586

**Access checked:** Collection text and dorsal image reviewed; alternate image endpoints located

**What the source supports:** The listed gauntlet combines steel, textile/leather and rich surface decoration; its image distinguishes cuff, hand plates and finger defenses.

**Our proposed use:** Use the large-to-small plate hierarchy, not its densely ornamented visual treatment.

**Limit:** The historic object does not validate our closed-hand geometry. Do not reproduce all engraving on Ada.



### S15 — The Met — Locking Gauntlet, 36.149.13

Source: https://www.metmuseum.org/art/collection/search/24645

**Access checked:** Detailed curator text reviewed

**What the source supports:** A specific mitten-type example has articulated metacarpal/finger lames and could be secured closed.

**Our proposed use:** Study overlapping protection and cuff construction. It reinforces the distinction between a designed closed shape and a universal articulated hand.

**Limit:** Not a requirement to give Ada a mitten or add a locking mechanism; no physical weapon-making guidance intended.



### S16 — The Met — Breastplate, 2014.673

Source: https://www.metmuseum.org/art/collection/search/667458

**Access checked:** Detailed curator text reviewed; front/back image endpoints located

**What the source supports:** The record describes a main shell, movable armhole gussets, turned edges, shoulder fastening and lower overlapping lames.

**Our proposed use:** Construct breast/back interfaces, edges and waist transition as assemblies, not a single inflated torso.

**Limit:** Museum dimensions are not Ada dimensions. Some surviving/replaced hardware is explicitly modern; do not infer all original kinematics.



### S17 — The Met — Breastplate, German or Austrian

Source: https://www.metmuseum.org/art/collection/search/23143

**Access checked:** Collection page and front image reviewed

**What the source supports:** The image provides a readable example of a broad central shell, arm openings and separately readable lower bands.

**Our proposed use:** Study cross-sectional curvature and restrained form hierarchy before adding decoration.

**Limit:** Not a female-body fitting blueprint or an exact costume match; use Ada's own approved reference for identity.



### S18 — The Met — Breastplate with Tassets, 2013.28

Source: https://www.metmuseum.org/art/collection/search/35917

**Access checked:** Collection description reviewed

**What the source supports:** The description distinguishes the breastplate, movable gussets, waist plate, skirt and tassets.

**Our proposed use:** Keep hip/waist protection separate from the chest shell so stepping can be designed.

**Limit:** Do not add all these elements if absent from Ada's approved design.



### S19 — Cleveland Museum — Pauldron (right), 1916.1816.c

Source: https://www.clevelandart.org/art/1916.1816.c

**Access checked:** Object text reviewed; extracted page reported image unavailable

**What the source supports:** The record identifies shoulder armor with etched decorative bands and roundels.

**Our proposed use:** A research target for shoulder silhouette and later restrained surface accents.

**Limit:** No detailed image or motion was obtained here. The gallery links to the object rather than inventing a plate arrangement.



### S20 — Blue Spirit — Fantasy Armor

Source: https://sketchfab.com/3d-models/fantasy-armor-2ee22efb91424935a633a735884f04a0

**Access checked:** Indexed creator description reviewed; viewer/archive NOT inspected

**What the source supports:** The creator lists Blender 3.5, Substance texturing, 15.5k triangles and CC Attribution licensing.

**Our proposed use:** Optional one-model inspection of part organization and material hierarchy.

**Limit:** License/archive must be checked on acquisition. No claim that the model is rigged, compatible, high quality under motion, or licensed for every intended use.



### S21 — Customizable Armor set with damage — original ArtStation breakdown

Source: https://www.artstation.com/artwork/NqAZaP

**Access checked:** Indexed creator text reviewed; full page/visual breakdown not loaded

**What the source supports:** The author describes staged damage layers, planned UVs and packed masks for Unreal materials.

**Our proposed use:** Defer damage variants; retain intentional UV/material-mask planning after the undamaged silhouette works.

**Limit:** Do not claim the videos/images were reviewed. This is optional pipeline inspiration, not instructions copied from a paid course.



### S22 — The Met — Open Access image/data policy

Source: https://www.metmuseum.org/policies/image-resources

**Access checked:** Policy reviewed

**What the source supports:** The Met makes designated public-domain images available under CC0; other images may have restrictions.

**Our proposed use:** Use only individually verified Public Domain/OA images when caching references.

**Limit:** A museum-wide policy is not blanket clearance for every page image. No third-party media is bundled in this kit.



### S23 — Blender 5.1 — Render Baking

Source: https://docs.blender.org/manual/it/5.1/render/cycles/baking.html

**Access checked:** Documentation reviewed; localized title, relevant technical passages readable

**What the source supports:** Selected-to-active transfers surface detail; tangent-space normals can be used on animated objects.

**Our proposed use:** Bake fine quilting, shallow engraving and edge treatment after geometry and the runtime mesh are stable.

**Limit:** Normal detail does not change silhouette or solve collision; inspect cage, rays, seams and engine convention.



## Optional creator-video discovery queue — not watched in this task



- Grant Abbitt, *Make a Detailed Sword in Blender: Topology Tips & Hard Surface Techniques*: https://www.youtube.com/watch?v=f320TtEpGYQ . The title/link was found through public indexing; direct video access failed. Do not invent frames, exact modifier values or the demonstrated sequence.

- Grant Abbitt, *Detailed Low Poly Characters: My Workflow & Essential Tips*: https://www.youtube.com/watch?v=7QiewPqkG80 . Discovered as optional silhouette/workflow study. Its intentionally faceted low-poly finish is not Ada's polished style target. Video not watched here.

- *Quick & Easy Secrets to Stylized 3D Art in Blender*: https://www.youtube.com/watch?v=XnfBBdnA8Tw . Discovery link only. Do not treat an automatically generated third-party summary as an original demonstrated recipe.



## Not selected as working references



- British Museum OA.2187 and OA.2188 are described by the museum as later fakes in a sixteenth-century style. They are not selected to establish period authenticity. A curator's detailed description is not a motion test.

- Do not reintroduce the `culturalibre_hero_boots_1` asset rejected in BW1 for a licensing discrepancy without resolving the actual archive headers.

- Downloadable models do not reveal their full creation history. Adaptation should be credited as adaptation; observed mesh structure and inferred construction sequence must be labeled separately.

- No new paid course, add-on, generation service or private artwork upload is required for the BW4 assignment.



## Image and source handling



Only the supplied Ada concept and rejected BW3 cage image are bundled, plus native crops. Museum images in the HTML navigator use public endpoints and require internet; local downloads were attempted but unavailable. Individual Met records selected for illustration state Public Domain; S22 explains the OA policy. Do not assume every image on a museum or artist page has the same rights.



No third-party meshes, fonts, paid lessons, videos, or texture packs are included. No claim is made that a linked archive imports correctly in Blender. No learned model was trained.
