# Creature pipeline preservation — 21 September 2026

**Status: documented and reviewed for reuse.** This checkpoint records the owner's
request to preserve the Meshy-to-Unreal production method in detailed, portable
project instructions. It does not produce or accept any new creature or lighting.

## Deliverable

- [Production handbook](../../production/creature-pipeline/README.md): seven manuals,
  approximately 13,250 words, with stages G0–G8, responsibilities and failure handling.
- [Eight reusable record templates](../../production/creature-pipeline/templates/README.md):
  candidate, lighting, generation, material map, animation cues, audio cues, review,
  and handoff. Unknown results remain unknown; no approval or credit cap is granted.
- [Project-local Codex skill](../../.agents/skills/wc-creature-production/SKILL.md),
  linked from project instructions and the existing AS1 entry skill.
- [Read-only documentation validator](../../tools/production/validate_creature_pipeline.py)
  and a manifest covering the handbook, templates and new skill.

Discovery links were added to `AGENTS.md`, the project `README.md`, successor
`docs/vnext/README.md`, `docs/MESHY_WORKFLOW.md`, and the existing `wca-orchestrate`
skill. Older Meshy/Blender setup instructions remain historical context. Existing
Bellback sources, accepted candidate and gameplay data were preserved.

## Fixed production choices

Meshy provides geometry and accepted color maps. Unreal supplies production rig,
animation, effects, audio integration and packaged verification. Blender has no
production role. Preserve the accepted Meshy palette; establish soft, readable
lighting without individual recoloring or blanket emissive compensation. Use
team rings/UI. Each anatomy receives its own rig and measured contacts/hovering.

The five detailed briefs retain the canonical IDs and gameplay: Cragstoat,
Grandmother Root, Snapvine, Prism Organ and Reefglass. Free sound research separates
provider allowance, commercial rights, local compatibility and actual quality.
Official sources and the date of the observations are included in the manuals.

## Review and verification

An independent agent followed a hypothetical future request to start Cragstoat.
It identified the unresolved shared lighting profile, reference/construction review
and generation authorization before dependent work. The review found three
ambiguities: missing G1 in G3's explicit prerequisites, ability behavior versus an
`Active` filename, and preserving original Bellback recipes when adapting tools.
All were corrected. A second review aligned raw-audio storage with the main layout
and the cue sheet's required fields. Final independent review found no remaining
material contradiction or preservation/completion risk.

Executed checks:

| Check | Actual result |
|---|---|
| Handbook and skill local links | PASS — 11 Markdown documents, 69 local links |
| Unfilled record integrity | PASS — 3 JSON templates and 3 header-only CSV templates |
| In-memory negative cases | PASS — all 11 injected faults rejected; no live files modified by fault injection |
| Project specification/data validation | PASS — 400 checks |
| Project Python unit tests | PASS — 230 tests |
| Generated documents | PASS — 28 match canonical data |
| Legacy catalogue | PASS — 6 artifacts match |
| Successor catalogue | PASS — 6 artifacts match |

Evidence: [documentation manifest](documentation-integrity.json),
[fault results](fault-results.json), [fault-check source](validate_handbook_faults.py),
and [repository check results](repository-checks.json). The tool-returned unit-test
output is explicitly marked truncated; its final test count and successful exit
were retained. These checks do not establish art, runtime or release acceptance.

The skill creator's `quick_validate.py` was attempted with both the project and
bundled Python runtimes; both lack its `yaml`/PyYAML dependency. Its validation is
**blocked by that missing dependency**, not recorded as passed. No package was
installed for this documentation task. The two skills' simple frontmatter and the
new `agents/openai.yaml` were inspected directly; local references and the future
invocation procedure were independently reviewed. Live skill discovery in a new
Codex task was not exercised.

## Actual limits and next production operation

No new Meshy job, art/audio generation, private upload, provider installation,
paid operation, Unreal asset edit, lighting edit or engine/package launch was
performed for this checkpoint. Documentation defaults are engineering proposals,
not measurements or new human art approvals.

The next production operation is G1: a reversible Bellback comparison using its
preserved Meshy colors under proposed soft lighting, followed by review of that
exact look. The actual light values, environment, shadows and display reference
remain unset. Sound-provider account allowance, rights eligibility where relevant,
and local inference speed/quality also remain untested. Existing owner approval of
the prior Bellback candidate is retained for its original scope.

## Resume request

> Use $wc-creature-production for Cragstoat. Read the handbook and latest handoff,
> then resume the first incomplete stage. Preserve accepted Meshy colors and use
> the shared soft lighting profile after its review. Keep Blender out of production.

The handbook alone grants no generation spending. Carry forward existing exact
approvals; obtain only genuinely missing decisions for the next concrete operation.
