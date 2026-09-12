# GPT Pro review entry point

This repository snapshot is being published on 2026-09-12 so the owner can discuss Wonder Chess's next development decisions. Review and propose next steps; this document does not authorize additional implementation or imply that the complete game is finished.

## Read in this order

1. [Successor contract](README.md): the adopted direction and M0–M7 programme. The old fixed 24-hero limit applies only to the preserved `alpha_24` baseline.
2. [Implementation handoff](../../reports/vnext/IMPLEMENTATION_HANDOFF.md): exact current package, executed checks, open defects and acceptance limits.
3. [Implementation matrix](IMPLEMENTATION_MATRIX.md): what is authored, executed, exposed to players and still missing.
4. [Gameplay contract](PRODUCT_AND_COMBAT.md), [hero dossiers](generated/hero_dossiers.md), [relic catalogue](generated/relic_catalogue.md) and [canonical source](../../data/vnext/catalog.json).
5. [Timeout findings](../../reports/vnext/TIMEOUT_FINDINGS.md), [1,000 native tournament analysis](../../reports/vnext/native/final-analysis.json) and [100 packaged tournament reconciliation](../../reports/vnext/engine-tournaments/r3/reconciliation.json).
6. [Art/UI production](ART_UI_PRODUCTION.md), [validation gates](VALIDATION_AND_ROLLOUT.md) and [Bellback detailed reference packet](../../art-source/asset-studio/wc_vn_bellback/inputs/references/r004_construction/README.md).

## Current state to preserve in the discussion

- There is a real packaged Unreal six-creature formation/combat laboratory with directional guard, momentum charge, stationary healing, screened backline strikes, crossing beams and a directional tide/push. Its primitive bodies and board are unapproved gameplay proxies.
- Native economy/tournament/relic/snapshot foundations execute. The new recruitment, scouting, relic-draft and packaged save/resume interfaces remain unfinished.
- Fourteen hero dossiers are authored; only six are active. Eighteen race/class traits are deliberately inactive. Additional roster growth has no predetermined final cap.
- The 1,000 native runs contain 187,141 encounters, 26,434 timeouts (14.125%) and 199 round-capped tournaments. The technical checks pass while the proposed timeout gate fails. Median 31.332-minute bot simulation is not human match-duration evidence.
- The timeout probe associates long fights with sustained healing. Many inspected Cragstoats never charge because their formation supplies no approach distance. The investigation specifies separate controlled experiments; no global tuning fix has been accepted.
- Shared mythic-storybook art direction is owner-approved. Bellback's detailed reference decision is pending. Prism Organ's first detailed reference is ART_REVISE. Finished models, motion, audio and visual slice acceptance remain open.
- Human playtests, comparative Auto Chess preference, full performance, clean-machine installation and remote multiplayer acceptance remain open. Passing technical checks does not prove enjoyment, retention or superiority.
- Historical `alpha_24`, Ada, AQ1 and AS1 evidence is preserved for provenance. It must not be mistaken for completed successor work. The published Git snapshot is not the packaged executable: `builds/`, caches and local configuration remain excluded.

## Questions for the next-step discussion

1. Does the six-creature spatial-combination premise create enough distinct, understandable preparation decisions? Identify duplicated decisions, missing counters and the smallest experiments that could falsify the premise.
2. How should we test positional sustain and Cragstoat approach incentives without overfitting to these provisional bots or erasing useful healing strategies?
3. What is the minimum recruitment/scouting/relic interface needed for the five-player M1 study, and which questions can the existing combat lab answer before that interface is complete?
4. Which race/class behaviors should be implemented first to connect these six creatures into multiple viable teams? Separate executable proposals from longer-term roster aspirations.
5. Does the art direction support recognition at the gameplay camera? Review Bellback and the proposed Prism Organ/Thimblewake rig-family pilots without treating generated references as finished models.
6. Propose a prioritized next three implementation batches. For each, specify the player-facing outcome, dependencies, bounded scope, tests, human evidence, stop criteria and what should explicitly wait.

Please distinguish source-backed findings, design judgments and hypotheses. Cite repository paths. Challenge weak assumptions; avoid expanding content merely to increase the hero or mechanic count. Do not claim that automatic tests establish a better or more enjoyable game than Auto Chess.
