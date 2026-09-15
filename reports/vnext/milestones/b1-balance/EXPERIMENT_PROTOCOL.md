# B1 experiment protocol and evidence boundaries

This is an executed native experiment against the preserved six-creature successor control, not an accepted balance change. The source reference is `d80635f615810a93c3161c6bfd6c34c758b08260`; the origin catalog digest is `6f9a4178ec78d48c8f6fb8d487d88069327a5ca526652724dc12a8654f574ebb`. Each run records the actual compiled source hashes, executable hash, process exits and source-stability check. The generated artifact line-ending correction in this checkout preserves the canonical data and its runtime semantics.

## Frozen comparison

- `control`: `wcvnext::WonderVNextCatalog()` without tuning edits.
- `root75`: a copy of that catalog; multiply only Grandmother Root's three base Grove pulse magnitudes by `7500/10000`, using the authoritative `wc::HalfUp` function.
- Preserve timing, geometry, self-healing rule, cooldown, health, basic attacks, relic evaluation, traits, bot-policy code, tournament rules, combat deadline and deadline adjudication.
- Derive both arms from the same generated C++ header. The reported origin digest identifies the source catalog; the separate variant and recipe identify the experimental effective values. The candidate is never written to canonical catalog or generated outputs.
- The parent adopted the existing proposed rejection screen for this experiment: timeout rate below 2% overall, in PvP and in ghost encounters. Each required stratum needs at least 100 observed encounters; fewer is insufficient. Report neutral encounters separately. No numeric round-cap criterion was invented.
- A numerical pass cannot issue tuning, comprehension, art, pacing or release acceptance. A numerical failure blocks promotion of this candidate, while independent engineering can continue.

## Seeds and timing

`seed_reservation.json` was written at `2026-09-12T15:19:04.259359+00:00`, before the first diagnostic compile. It inventories 63 local seed-bearing evidence files and 1,001 explicit unique seed IDs (1–1000 and 314159). It reserves **900001–900250** for future confirmation, outside that inventory and the prior tournament harness bound of 1–10000. This establishes non-overlap with recorded local evidence, not with unknowable unrecorded external executions.

The mechanical diagnostics use seeds 1–10 in both arms. The complete regression uses seeds 1–1000 in both arms, with two native jobs maximum. Diagnostic seeds overlap regression seeds deliberately and are not extra independent samples. They must never be pooled into a nominal sample of 1,010 independent tournaments. The four fixed-formation seeds are 19, 41, 97 and 251. These are known diagnostic inputs, not unfamiliar human-study scenarios.

The Root75 diagnostic already fails the proposed numeric screen; the held-out set remains unexecuted. The full regression quantifies that failure and its composition and round-cap consequences. It does not turn a known failing candidate into a confirmation candidate. Any future selection or tuning use consumes an input's held-out status and must be recorded.

## Fixed armies and manual formation changes

All units and rules retain canonical tuning, except the declared Root75 comparison. Each fixture is run at stars 1, 2 and 3, in both side orientations, for all four seeds: 24 executions per placement, 192 encounters per arm. Each encounter is separately replayed and compared event by event. Both armies have equal investment, counting stars as 1/3/9 acquired copies multiplied by their canonical costs.

| Fixture | Literal player army | Declared placement difference | Purpose and limits |
|---|---|---|---|
| `charge_approach` | Cragstoat, Bellback, Root | Cragstoat row 3 versus row 0 | Compare front-line adjacency with actual approach space. No damage or bot compensation. |
| `charge_own_screen` | Same three units | Bellback column 1 versus column 3; Cragstoat remains in row 0 | Observe the effect of one's own screen. The same move can change guard coverage and later navigation; do not call it a pure damage intervention or assume permanent charge denial. |
| `grove_cluster` | Bellback, Root, Cragstoat | Root column 3 versus column 0 | Compare nearby sustain with an isolated starting position against the same opposing army. |
| `grove_screened_pressure` | The prior army plus Snapvine on both sides | The same single Root column change | Repeat under a source-authored pressure mechanic without adding unavailable free high-cost counters. This is a fixed-army fixture, not proof of recruitment access. |

`fixture_inputs.csv` records actual local positions, facing, stars, relics, stable IDs and represented-copy counts. `fixtures.csv` records outcomes and whole-encounter metrics. `fixture_charge_actions.csv` records native `CastWindup` commitments with action identity, origin, committed aim, momentum and expected release tick. Actor-specific analysis isolates the deliberately positioned Cragstoat (owned ID 1) from its opponent.

Side mirroring swaps the local armies through the actual combat constructor, which rotates the opponent through both board axes. Initiative and tie-breaking remain seeded; four seeds per star are not a population estimate or a promise of exact symmetric win rates.

## Metric definitions

- Health damage is the sum of authoritative damage-event `healthLoss`. Every damage event must reconcile `resolved = healthLoss + absorbed + overkill`; event-reconstructed final health must equal every unit's actual final health.
- Effective healing is the sum of heal-event `resolved`. Logged-recipient overheal is `requested - resolved` for those events. The engine does not emit heal events for full-health recipients or cancelled tethered pulses, so total unused potential healing cannot be inferred from this field.
- Guard prevention is the sum of event `prevented` values. It is not a guessed geometric uptime metric.
- A charging source has at least one resolved MomentumCharge damage event. Charge movement landings count MomentumCharge Dash events. Zero-distance charges can resolve without a movement event; these measures have different denominators.
- An observed commitment without any resolved charge event is explicitly unclassified. Current public telemetry cannot definitively distinguish pre-release interruption, moved/dead target, invalid landing or other missing-recipient cases. No-attempt opportunities and rejection reasons remain an instrumentation gap.
- First action means the first event with health loss, positive resolved value, or movement. First death comes from event-reconstructed health. The descriptive two-second first-death count has no adopted pass/fail threshold.
- Survivor count and represented-copy investment, Root occurrences and largest same-hero multiplicity are recorded per encounter. Associations in these strata are not isolated causal strength estimates.
- Round caps are reported per complete tournament. Durations are actual simulated preparation/combat/settlement time; phases reconcile to the tournament elapsed time. Early-ready bots do not establish the duration of a human match.

## Recruitment and composition

During preparation the observer records newly drawn offer slots and whether the offer is affordable and legal for the current roster at its first observed appearance. A consumed nonempty shop slot counts a purchased copy; each tournament's total must equal the authoritative bot log's accepted `buy` replies. This verification includes the final purchase that changes phase. These are offer-time opportunities, not the number of ticks during which an unchanged slot later becomes affordable.

Deployment counts are taken once at each real combat lock for each living seat. Ghost copies do not count as additional ownership. Both physical unit-rounds and star-represented copy-rounds are retained. Modified healing magnitude can change the existing bot's valuation and therefore its purchases; unchanged bot code is not unchanged composition. Tournament differences include that drift. Fixed-army fixtures provide the separate controlled mechanic comparison.

## Reproduction

Run from the verified successor worktree:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tests/runtime/run_vnext_balance_experiment.ps1 -Variant control -Seeds 1000 -FirstSeed 1 -RunLabel regression
powershell -NoProfile -ExecutionPolicy Bypass -File tests/runtime/run_vnext_balance_experiment.ps1 -Variant root75 -Seeds 1000 -FirstSeed 1 -RunLabel regression
python tools/vnext/analyze_balance_experiment.py --control <control-run-directory> --candidate <root75-run-directory> --output reports/vnext/milestones/b1-balance/comparison
```

The analyzer rejects failed, incomplete or source-drift runs, missing/duplicate seeds, different paired input sets and mismatched tournament/encounter totals. It reports numerical failure separately from successful technical execution. Native experiment builds and full regression output are evidence for their exact source hashes; future shared-core changes need their own scoped validation.

Normal-speed external-player sessions, a human sustain-utility judgment, practical level-specific counter acquisition, exact charge failure instrumentation, a held-out confirmation candidate and adoption of any balance change remain separate work. No result here completes those gates.
