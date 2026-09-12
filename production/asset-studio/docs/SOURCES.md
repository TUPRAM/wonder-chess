# Sources, proposed rules and verification boundary

**Prepared:** 2026-09-08. References below support narrow technical facts. AS1's stage graph, approval roles, budgets, capture plan, retry limits and Ada pilot are proposed production decisions—not vendor guarantees or established industry requirements.

## Project basis

The user supplied six stages: concept/reference, base modeling, retopology, UV/texturing, rigging and skinning, and explicitly requested expansion into reusable skills/tools. Their supplied Ada concept and rejected model image are included as provenance-recorded inputs, not approved geometric blueprints. Crops preserve original pixels and do not invent additional views.

The existing `TUPRAM/wonder-chess/.agents/skills/wc-blender-asset/SKILL.md` was read through the GitHub connector while preparing this package. Its returned blob SHA was `9a56ab1651f9f570a7fe5a68162d7eeab0514558`. It already requires source inspection, bounded edits, seven-clip review, export/import and separate visual/structural evidence. AS1 expands that routing without claiming a new audit of all repository files or the user's local unpublished work.

The older high-fantasy production brief supports editable source, one reference hero, rig-family planning, camera-specific budgets and a measured reimport pipeline. Its obsolete game naming, website-first priority and old playable scope are **not** carried forward here.

## Official technical documentation

| Key | Document | Supports | Does not establish |
|---|---|---|---|
| O1 | [OpenAI — Agent skills](https://developers.openai.com/codex/skills/) | `SKILL.md` procedures, resources/scripts, staged loading and skill discovery concepts | That copying files successfully installs or invokes a skill in every client/version |
| O2 | [OpenAI — Codex MCP](https://developers.openai.com/codex/mcp/) | Connecting external tool capabilities through MCP | A working Blender connection, an art judgement system or authorization to upload files |
| B1 | [Blender 5.0 — Mirror Modifier](https://docs.blender.org/manual/en/5.0/modeling/modifiers/generate/mirror.html) | Local-axis/origin or explicit mirror-object behavior, clipping and merging | That clothing and equipment should all be symmetric |
| B2 | [Blender 5.0 — Retopology / Remeshing](https://docs.blender.org/manual/en/5.0/modeling/meshes/retopology.html) | Rebuilding topology and remesh limitations | That every sculpt requires retopology or remeshing produces animation-ready loops |
| B3 | [Blender 5.0 — Render Baking](https://docs.blender.org/manual/id/5.0/render/cycles/baking.html) | Selected-to-active transfer, cages/rays, tangent-space normals and bake outputs | Automatic clean UVs, correct export tangent conventions or artistic material quality |
| B4 | [Blender 5.0 — Rigify Introduction](https://docs.blender.org/manual/en/5.0/addons/rigging/rigify/introduction.html) | Automated bone/control construction; skinning remains separate | Automatic good deformation or a ready Unreal export rig |
| B5 | [Blender 5.0 — Armature Deform Parent](https://docs.blender.org/manual/sr/5.0/animation/armatures/skinning/parenting.html) | Automatic weight estimation, possible unwanted influences and need for manual correction | Guaranteed elbow/hand/cloth quality |
| B6 | [Blender — Armature Modifier](https://docs.blender.org/manual/en/5.3/modeling/modifiers/deform/armature.html) | Preserve Volume's different, quaternion-based deformation behavior | Matching deformation in the project's Unreal skinning path |
| E1 | [Epic — FBX Skeletal Mesh Pipeline](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-skeletal-mesh-pipeline-in-unreal-engine) | Skeletal assets, animation, triangulation, LOD/import and FBX compatibility considerations | That Blender exposes a matching FBX-version menu or every exported candidate is compatible |
| E2 | [Epic — FBX Import Options](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-import-options-reference-in-unreal-engine) | Normal/tangent modes, skeleton and reference-pose import settings | Which choices are correct without testing the actual pipeline |
| E3 | [Epic — Scripting Unreal Editor Using Python](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python) | Editor automation and content tooling | Python as a packaged gameplay runtime |

Some direct English/latest Blender page fetches were unavailable during research. Official indexed excerpts and accessible localized manual pages supplied the narrow facts listed above. The localized URLs are sources, not a request to change the project's language. Documentation versions are references, **not claims about installed tools**. Read the installed Blender/Unreal API before executing version-sensitive code; do not upgrade the project just to match a linked manual.

## Implementation status

The local ledger, image helper and command-construction logic were exercised by standalone tests. Blender scripts were syntax checked, not run inside Blender. No Unreal adapter, external image-generation service, automatic retopology system, image-to-3D service, protected identity service or new MCP server was deployed. A provided operation contract is not a callable installed tool.

See `../reports/VALIDATION.md` for actual commands and outcomes. No cited documentation proves the proposed art direction will be attractive, the bots/game are complete, or the user has approved a rendered asset.
