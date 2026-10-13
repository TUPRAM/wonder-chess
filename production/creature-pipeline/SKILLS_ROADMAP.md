# Production skills: ownership and roadmap

Skills guide repeatable work; they do not replace tested tools, human art review
or canonical game data. Keep one orchestration entry point and focused specialists.
Names marked proposed below do not represent installed capabilities.

## Available project skills

| Skill | Responsibility and output |
|---|---|
| `wc-creature-production` | Own creature candidate, references, bounded budget, stage status; deliver color, PBR, verified rig, then motion/audio/game work when requested |
| `wc-creature-rigging` (new) | Choose anatomy-appropriate rig route, map actual bones, correct weights, expose controls and prove skin/contact behavior; animation-ready handoff |
| `wca-orchestrate` | AS1 ownership, provenance, immutable revisions and exact human acceptance across asset types |
| `wc-unreal-integration` | Unreal import, runtime presentation integration, build/package and engine-side validation |
| `wc-data-contract` | Canonical roster/rules/contracts, generated outputs and data consistency; prevents art tools from inventing gameplay |
| `wc-release-evidence` | Relevant executable/regression/performance/study evidence; distinguishes local checks from release acceptance |
| `wc-blender-asset` | Existing separate Blender route for explicitly requested work; not part of this creature production route |

The new rigging skill has a Cragstoat execution example: an Unreal fallback after
Meshy quadruped failure, 33 bones/21 controls, corrected disconnected-fur weights,
601 cold-reopened skin/contact samples and a checked FBX reimport. This qualifies
that bounded workflow, not every anatomy or full gameplay animation. Exact owner
acceptance is separate; consult the candidate handoff and measured reports.

## Recommended additions, in production order

| Proposed skill | Main job | Required handoff |
|---|---|---|
| `wc-materials-and-look` | Preserve source colors; UV/map inventory, normal/roughness checks, shared soft lighting and texture revisions | Versioned maps/materials, matched source/board views and measured texture budget |
| `wc-creature-animation` | Author anatomy-specific idle/move/turn/attack/ability/hit/defeat/victory clips on a verified rig | Clips, transitions, motion/event contracts and actual skinned contact evidence |
| `wc-audio-production` | Check current free/commercial rights, generate or select layers, edit in Audacity, create variations and mix | Original/processed WAVs, license/provenance, cue table and listening review |
| `wc-combat-vfx` | Readable Niagara effects/telegraphs synchronized with authoritative gameplay, including cancel/miss cases | Effects, cue bindings, crowded-scene captures and cost measurements |
| `wc-reference-preparation` | Consistent four-view construction and Krita assembly across characters | Layered sources, four PNGs, slot/hash record and part inventory |
| `wc-environment-production` | Boards/arenas/props, modular dimensions, collision and shared look | Sources, modular kit, LOD/collision/material checks and playable board views |
| `wc-ui-production` | In-game shop, bench, selection and readability/accessibility with actual runtime data | Unreal widgets, interaction states, input and readable-layout evidence |
| `wc-gameplay-verification` | Deterministic gameplay scenarios, balance experiments and bug reproduction without hidden bot advantages | Runtime tests, seeded evidence and explicit limits; use existing data/release skills |
| `wc-performance-and-recovery` | Insights traces, representative crowded scenes, memory/streaming, fresh-machine recovery | Hardware/settings, raw timing data, bottleneck evidence and recovery rehearsal |

Create each specialist when its first real task supplies concrete examples and
failure modes; avoid many empty skills with duplicated generic checklists. The
current texture manual supports the first future specialist. Rigging owns skin
and control structure; animation owns clips; gameplay owns event authority;
integration owns importing/binding; release evidence owns final verification.
