# B1 diagnostic continuation — 13 September 2026

The owner resumed implementation with "Continue the work". The control remains `wonder_vnext_solo_0.1.0`, source SHA-256 `6e80932173071ef05e58d90a44db3490cfcfde86d48edf33f4a940ff1748efa0`. No balance change or additional creature has been promoted. Root75 still fails pacing. These automated development observations are not external-user or enjoyment evidence.

## Instrumentation and verification

Combat can opt into a separate diagnostic trace before its first tick. Charge traces distinguish eligible attempts, commitments, releases, cancellations and impacts. Grove traces include empty pulses, full-health exclusions, source movement, stun/epoch invalidation, defeat and combat completion. Ordinary gameplay events, save/protocol formats and catalogue rules are unchanged. Diagnostics are disabled by default.

The native suite passed 21,875 assertions. It compares every combat-event field with tracing on/off, timing and final state; exercises own-screen obstruction, absent momentum, moving targets, death and timeout cancellation, establishment, empty/full-health pulses and displacement. The first new fixture failed because its 50 ms establishment period had already expired; a separate 200 ms waiting fixture corrected the test without changing a combat rule.

Every encounter in the two new 100-seed tournament arms also ran as a copy made before its first tick, with tracing enabled. Copies matched the match's full event fields, results and final states. Every commitment had exactly one release or cancellation. Healing and captain damage reconcile with actual events and settlement. All 18,685 current control encounter results also match r4's native seeds 1–100.

## Fewer combat deadlines, more tournament caps

Both arms use development seeds 1–100, current solo catalogue inputs and identical compiled sources. Root75 changes only in-memory base pulse magnitudes by its recorded 75% recipe. These arms are separate from the older 1,000-seed lab-catalogue experiments. Confirmation seeds 900001–900250 remain unused.

| Measurement | Current control | Root75 |
|---|---:|---:|
| Tournaments | 100 | 100 |
| Encounters | 18,685 | 19,221 |
| Combat deadlines | 2,552 | 1,689 |
| PvP deadlines / encounters | 2,270 / 10,205 | 1,524 / 10,507 |
| Ghost deadlines / encounters | 282 / 706 | 165 / 745 |
| Neutral deadlines / encounters | 0 / 7,774 | 0 / 7,969 |
| Tournaments at the 45-round cap | 14 | 35 |
| Mean deaths per PvP encounter | 7.96 | 8.65 |
| Mean positive captain damage, rounds 31–40 | 10.48 | 9.69 |
| Captains alive at the cap | 28 | 72 |
| Median remaining HP among those captains | 13.5 | 15 |

Settlement charges a losing PvP/ghost captain the authored stage base plus opposing survivors. The reduced-healing arm produces more creature deaths and smaller positive captain losses. This explains the direction of the cap regression; recruitment and subsequent composition also change, so it does not explain every tournament outcome by healing alone. Draws are rare and do not explain the caps. Both arms fail the below-2% PvP/ghost screen.

D01 preserves elimination as primary resolution and forbids timer padding or damage compensation. Extending the tournament or silently increasing captain losses would not close the gate. Root75 stays rejected.

## Charge and grove findings

The control records 576,427 eligible charge decisions: 495,732 (86.00%) report no momentum. These are repeated cooldown-ready opportunities, not unique creatures or independent battles. There are 49,338 commitments, 46,531 releases and 2,807 cancellations (5.69%). Cancellation reasons distinguish moved/dead targets, occupied routes/corners, source defeat and combat completion. There are 46,162 resolved impacts; 369 released attacks reach an already defeated target.

Interrupted windups are therefore not the principal recorded cause of charge inactivity. An adjacent Cragstoat without stored movement cannot charge under the current contract. Approach placement and players' ability to explain that condition need investigation before changing the rule. A valid adjacent impact need not create a movement event.

Grove records 855,988 impacts with recipients, 23,062 without injured recipients and 2,055,871 full-health ally-pulse exclusions. Effective healing reconciles to 15,388,797,753 centipoints. Full-health exclusions describe geometry and health; they are not discarded heal packets or an inferred unused healing budget. Source movement, defeat, epoch invalidation and combat completion explicitly close pending pulses.

## Actual counter acquisition changes the conclusion

The old F07 fixtures constrained army purchase investment but did not execute recruitment. The continuation runs both level-3 plans through ordinary owner commands, real shops, starting gold and automatic merges. Its policy buys needed visible recruits and rerolls only if the remaining total budget can still buy missing copies. No income, XP or elapsed preparation is granted; another captain's shop stream stays unchanged.

There are 400 trials: two plans × two total gold limits × 100 development shop seeds (61001–61100). Budget arms share seeds. Acquired instance identities/order and real placement commands form the response army, which fights the F07 pressure formation at fixed combat seed 42007. Failed acquisitions remain in the results and run no substitute fight.

| Response | Total gold limit including rerolls | Obtained / 100 | Wins among obtained armies | Median spent when obtained |
|---|---:|---:|---:|---:|
| Two-star Cragstoat + Bellback | 4 | 23 | 23 / 23 | 4 |
| Two-star Cragstoat + Bellback | 10 | 100 | 100 / 100 | 6 |
| Two one-star Cragstoats + Bellback | 4 | 56 | 37 / 56 | 3 |
| Two one-star Cragstoats + Bellback | 10 | 100 | 51 / 100 | 3 |

The upgraded pressure response was affordable in all sampled ten-gold trials, but its four-gold army price did not guarantee acquisition. The width response's original authored win did not transfer reliably to actual acquired identities/order. Retain its losses; do not describe the hand-authored result as a generally reliable counter. This supports an initiative/order and placement follow-up, rather than adding a seventh creature.

Tournament recruitment traces also show Reefglass absent before level 7 and rarely bought/deployed later. Prism begins appearing at level 5 but has sparse deployment. The reported level is the level when a shop transition is observed: an offer and its purchase can straddle a level-up. Purchases divided by same-level observed offers would not be a valid conversion rate.

## Completed ordering and approach follow-up

The initial width acquisition results split by actual roster order: Bellback-first loses all 49 sampled fights, while Cragstoat-first wins all 51, at combat seed 42007. Combat assigns seeded initiative by shuffling the input unit indexes, so that fixed seed does not assign the same initiative to the same physical cells when acquisition order changes. This is a selected-seed observation, not a population estimate of order advantage.

A subsequent bounded experiment uses three roster-order permutations, 32 different development combat seeds (61401–61432), both orientations, and one physical change: moving only the first Cragstoat from local row 0 to row 3. All 384 rows preserve the three-gold army. They share seeds/formations and are not 384 independent balance samples.

| Placement | Orientation | Wins / encounters | Mean charge hits | Deadlines |
|---|---|---:|---:|---:|
| Original two rear Cragstoats | Normal | 74 / 96 | 3.39 | 0 |
| Original two rear Cragstoats | Mirrored | 66 / 96 | 2.78 | 0 |
| First Cragstoat moved forward | Normal | 73 / 96 | 2.48 | 0 |
| First Cragstoat moved forward | Mirrored | 96 / 96 | 2.29 | 0 |

Across these seeds, original-formation wins by roster permutation are 48/64, 46/64 and 46/64. The extreme fixed-seed order split therefore does not persist as a comparable average difference. Moving forward reduces charge hits but does not consistently reduce wins, and orientation matters in this selected sample. A "more charge hits means better placement" lesson would be misleading. Preserve encounter-level results and test what players understand before promoting a general positioning rule or changing initiative.

The extended native suite passes 7,390 assertions. [Full acquisition identities and order](../../../reports/vnext/milestones/resume-20260913/width-sensitivity/counter-acquisition-inputs.csv) and [width follow-up results](../../../reports/vnext/milestones/resume-20260913/width-sensitivity/width-summary.json) preserve this investigation. No runtime balance change resulted.

## Next bounded work

1. Use the preserved ordering/approach results to select unfamiliar normal-speed examples with useful and unfavorable outcomes. Keep seed, orientation, identity/order and the one changed physical variable explicit.
2. Test charge approach/no-momentum and relic tradeoffs in normal-speed B1/B2 tasks. Collect independent predictions, explanations and revisions; agent input checks are not participants.
3. Select at most one targeting, movement or interaction candidate from those findings. Stop promotion if PvP/ghost deadlines remain above 2%, caps regress or the changed mechanism is unclear. Do not activate Plant, spend confirmation seeds on Root75, or expand the roster to conceal sustain failures.

## Evidence

- [Comparison, source/evidence hashes and metric definitions](../../../reports/vnext/milestones/resume-20260913/mechanic-comparison-v2.json). Seven evidence-accounting tests reject incomplete/unstable runs, missing seeds, orphan traces, unclosed commitments and healing/captain-damage mismatches.
- [Control run](../../../reports/vnext/milestones/b1-balance/resumed-diagnostics-control-20260913T034708422Z/process.json) and [Root75 run](../../../reports/vnext/milestones/b1-balance/resumed-diagnostics-root75-20260913T034708429Z/process.json).
- [r4 result parity](../../../reports/vnext/milestones/resume-20260913/r4-control-parity.json).
- [Acquisition summary](../../../reports/vnext/milestones/resume-20260913/counter-acquisition/acquisition-summary.json). The subsequent `counter-acquisition-inputs` run additionally preserves full formation identities/order and combat signatures. Both use development seeds.
