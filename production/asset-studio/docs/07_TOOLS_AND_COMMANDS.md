# Implemented tools, adapter contracts and commands

## 1. Actual included tools

| Tool | Implemented behavior | Does NOT do |
|---|---|---|
| `assetctl.py` | Initialize isolated workspace, generate pending review template, seal evidence, record role-based signoff, detect stale gates | Model, view pixels, authenticate humans, enforce OS permissions, promote canonical assets |
| `image_review.py` | Native crops, labeled downsample-only sheets, registered binary-mask overlap | Generate new views, repair perspective, judge beauty, recover hidden detail |
| `run_blender.py` | Dry-run command assembly; explicit execution of three included scripts in separate background process | Connect to/kill live MCP GUI, discover credentials, run arbitrary remote code |
| `blender/reference_setup.py` | Add calibrated hash-checked image empties and save a new candidate .blend | Perfectly align inconsistent AI references |
| `blender/scene_audit.py` | Basic source/evaluated mesh, weights, rest skeleton and image observations | Exhaustive self-intersection/UV-overlap checks or visual/continuous-motion approval |
| `blender/render_review.py` | Temporary fixed-camera clay/material review scene using chosen source collection/current pose | Improve geometry, auto-pose, approve renders or match an unknown concept camera |

The first three are ordinary Python helpers. The three Blender-side scripts are supplied for local verification and were not executed in Blender during kit authoring.

## 2. Workspace and review examples

Commands below assume repository root and package installed at `production/asset-studio`.

```powershell
python production/asset-studio/tools/asset_studio/assetctl.py init --workspace art-source/asset-studio/wc_u_human_guardian --asset-id wc_u_human_guardian --kind hero --name "Ada Brightshield"
python production/asset-studio/tools/asset_studio/assetctl.py report-template --workspace art-source/asset-studio/wc_u_human_guardian --stage brief --output reports/brief_r1.json
```

Fill the report from actual work; defaults are `not_run`. Artifacts use workspace-relative forward-slash paths and categories `source/image/video/audio/report`. List source snapshots as well as reviewed outputs; do not submit only screenshots of a different revision.

An `accepted_minor` defect must include nonempty `reason`, `affected_use`, `owner`, and `later_action` strings. This records the scoped exception required by the system contract; it cannot waive a critical or major defect.

```powershell
python production/asset-studio/tools/asset_studio/assetctl.py prepare --workspace art-source/asset-studio/wc_u_human_guardian --report reports/brief_r1.json
```

This prints a candidate path. It is not approved. A separate technical reviewer may record the brief signoff with its actual reviewer identity, notes and `--ack-reviewed`. Reference/forms/release require role `human`; Codex may not issue those itself.

```powershell
python production/asset-studio/tools/asset_studio/assetctl.py status --workspace art-source/asset-studio/wc_u_human_guardian
```

The human signoff operation is intentionally explicit:

```text
assetctl.py approve --workspace <asset workspace> --candidate <printed candidate path> --reviewer Pram --role human --note "Actual review decision and limitations" --ack-reviewed
```

Only run that after the real human review. This is a declaration, not authenticated identity. Use protected approval infrastructure for stronger separation.

## 3. Image operations

```powershell
python production/asset-studio/tools/asset_studio/image_review.py crop --image <actual concept.png> --boxes <crop plan.json> --out <new crop directory>
python production/asset-studio/tools/asset_studio/image_review.py sheet --images <reference.png> <actual_render.png> --out <new comparison.png>
```

Do not use `mask-metrics --registered` for a differently posed concept and render. The flag acknowledges a registration that this utility does not perform or verify. No acceptance score follows from IoU.

## 4. Blender runner

Set the actual executable path in `BLENDER_EXE` or use `--blender`. The command is dry-run unless `--execute` is present. Passing `--execute` requires a new log file. The source must already exist.

```powershell
python production/asset-studio/tools/asset_studio/run_blender.py --source <candidate.blend> --tool scene_audit -- --collection <candidate export collection> --output <new audit.json>
```

For execution add `--execute --log <new log.txt>` before the final `--`. Rendering has its own approved camera configuration and distinct output directory. Large jobs should use a separately managed process with status/log paths rather than block an interactive MCP call indefinitely.

The runner uses `--factory-startup` before loading the explicit source, `--disable-autoexec`, and a trusted local script. This avoids loading saved user startup preferences and add-ons in the isolated helper process. Scripts in Blender files, add-ons or fetched references are not automatically trustworthy. Inspect dependencies before execution.

## 5. MCP adapter contract — implementation required

Do not install a new server just to satisfy these names. Map the actual user's bridge functions to these semantic operations: inspect scene, inspect part, run trusted bounded script, capture viewport image, save candidate, query operation status and fetch output image. Record their actual names and schemas in `capabilities.json`.

Commands need an operation ID, expected file/scene revision, owned part IDs, allowed outputs and failure strategy. Tool responses must distinguish queued/running/complete/failed. If the bridge lacks those controls, enforce them in a local wrapper and serialize calls. AS1 does not claim to supply that server wrapper.

A render adapter should return a real image or accessible bytes/path plus source hash, camera, pose/frame, render settings and view role. An image-generation adapter needs approved reference inputs, provider/model/settings, consent/cost policy and returned output metadata. Missing keys/settings remain unknown, not fabricated.

## 6. Unreal adapter contract — implementation required locally

Use the project's existing importer and tests where possible. Required semantic operations: inspect target folder/skeleton; import into candidate folder; apply known material preset; inspect skeletal hierarchy/sockets; load review map; play/capture clips; reimport deliberate source change; package/run; collect performance. Each adapter must be verified against the installed editor APIs and return actual logs/captures.

There is no universal auto-export/auto-import button in this package. A measured existing profile should be reused; a changed profile is a new compatibility experiment.
