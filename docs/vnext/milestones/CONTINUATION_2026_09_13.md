# B1/B2 continuation — 13 September 2026

The owner explicitly resumed development. The active engineering candidate is **r6**, following r5's diagnostics and preparation-feedback changes. Canonical gameplay is still `wonder_vnext_solo_0.1.0`: six active creatures, twelve relics, inactive traits and proxy art. **B0–M7 is not accepted or complete.** The current pacing screen fails; no external participants, art forms acceptance, independent clean machine or remote human sessions were supplied in this continuation.

## Implemented outcomes

- Purchase feedback identifies cost and completed upgrades; shop copy counts announce an available three-copy merge. Placement, XP, ready, facing, draft/equip/unequip and rejection messages explain their immediate result. Relic inventory describes compatibility with the selected recruit and whether the relic is already equipped.
- The recap separates captain HP lost from creature health damage and effective healing. Scouting revision identity remains visible in the public sidebar.
- Optional native diagnostics explain charge opportunity failures, commitments, release/cancellation and impact; grove diagnostics account for recipients, uninjured pulses, full-health exclusions and invalidated pulses. Diagnostics are disabled by default and preserve the ordinary event stream and combat result.
- Actual r5 input exposed a misleading inspector fallback: clearing selection could display the previous laboratory palette creature with base stats and no relic. r6 now asks the player to select a creature. Selected preparation and combat views still show the actual equipped relic and its transforms. This correction does not change combat or catalogue values.

## B1 findings and decision

The [diagnostic readout](B1_DIAGNOSTIC_READOUT.md) records the full experiment, denominators and limitations. In two new 100-tournament diagnostic arms, control produced 2,552 timeouts / 18,685 encounters and 14 capped tournaments; Root75 produced 1,689 / 19,221 and 35 caps. More deaths leave fewer winning survivors and reduce one part of captain damage; recruitment also changes, so this is an explanation supported by telemetry, not a complete isolated causal estimate. **Root75 remains rejected.** The canonical 1,000-tournament checkpoint still has 26,219 / 186,984 timeouts (14.0221%) and 187 caps.

Of 576,427 eligible charge decisions, 86.00% lack momentum. These repeated opportunities are not independent battles. Cancellations account for 2,807 of 49,338 commitments, so interrupted windup is not the principal measured explanation for charge inactivity.

The new acquisition study runs ordinary shop, reroll, buy, merge and placement commands in 400 trials over 100 development shop seeds. A two-star Cragstoat plus Bellback response is acquired in 23/100 trials with a four-gold total budget and 100/100 with ten gold; all obtained armies win this selected fixed-seed scenario. Two one-star Cragstoats plus Bellback is cheaper, but wins only 51/100 ten-gold acquisition trials. Its fixed-seed result depends on acquired identity/order and seeded initiative.

A 384-encounter follow-up varies three orderings, two placements, two orientations and 32 development combat seeds. The extreme fixed-seed ordering split does not persist as a large average ordering difference. Moving a Cragstoat forward reduces charge hits while improving some results; neither more charge hits nor the original hand-authored victory is a reliable universal lesson. Retain these losses and test player understanding before changing initiative, promoting a counter rule or adding content. Reserved confirmation seeds 900001–900250 remain unused.

## Executed verification

| Evidence | Result and boundary |
|---|---|
| Authoring/generation | 228 Python tests and required validation, document, legacy catalogue and successor staging checks passed again after the r6 correction; logs in `authoring-r6/` |
| Native combat diagnostics | 21,875 assertions; diagnostic replay/result and commitment closure checks passed |
| Native lifecycle | 240,572 assertions; includes a legally reached round-4 preparation fixture for the relic input journey |
| Native scenarios/acquisition/sensitivity | 7,390 assertions in the final extended suite; 400 acquisition trials and 384 sensitivity encounters; sources stable |
| Legacy shared-authority regression | 100 tournaments, 3,379,152 assertions; historical alpha profile only |
| r5 packaged engine | 100 tournaments, 4,288 rounds and 18,685 encounters reconciled exactly against the preserved native reference |
| r6 packaged engine | 10 targeted tournaments, 427 rounds and 1,852 encounters reconciled; r5→r6 changed only inspector presentation and its smoke checks |
| r6 solo handlers | All 20 boolean checks passed, including empty selection in preparation/combat and selected equipped-relic inspection; accelerated 43-round completion, elimination spectating, save/resume and restart are separate from real input |
| r5 actual input | Nine scoped cases with 23 retained screenshots; details below. One inspector clarity defect found and fixed in r6 |
| Clean-checkout builds | Both r5 and r6 completed successfully from independent clean Git checkouts; each matched all 80 build-source inputs before building, passed 81-source/49-payload identity, and reconciled 10 engine tournaments /427 rounds /1,852 encounters |

The [r5 actual input record](../../../reports/vnext/milestones/resume-20260913/actual-input-r5/review.json) covers:

- At 1280×720: normal-mode load, Patient Lantern draft/equip/unequip/re-equip, deployment, Right/Enter movement, facing, an equipped three-copy upgrade and save/exit.
- At 1600×1000 in a new process: protected startup choice, restored two-star Cragstoat at D2 facing right with Patient Lantern, gold 25, level 4/2 XP, 45 paused seconds and purchased shop slots. Ready/resume reached normal-speed combat and a round-4 loss from 100 to 94 captain HP. A disabled shop click during paused round-5 combat changed neither roster nor gold. Selecting the live creature showed its actual relic and transformed ability.
- At 1920×1080: a separate checksum-valid old-version save was rejected through actual Load with specific content-version feedback; live round-1 state and the original valid save were preserved.

These are agent-operated checks on the development PC. They do not establish full-bench input, all-resolution full journeys, external comprehension, normal-speed final-winner duration, enjoyment, visual acceptance or superiority over Auto Chess. A screenshot named `captain-loss-recap-1600x1000.png` actually captures the current combat inspector; it is not evidence that the recap text was visually reviewed. Captain HP loss is evidenced by the before/after status and phase log.

The actual r6 follow-up remains **BLOCKED_OPERATOR_DIALOG**. Its scripted checks have completed independently. No r5 pointer check is relabeled as an r6 pointer pass.

## Source, package and failed-attempt provenance

r5 actual engine executable SHA-256: `fe6ce54720c16f0991f410652911cc366660e1856e30b3063ba0ab4ee4173db6`.

r6 actual engine executable SHA-256: `f2ac31a8e00e77c7e5b2013525ab3474a94b17195ef454eb47aadf449c202d76`. Its [manifest](../../../reports/vnext/milestones/resume-20260913/package-identity-r6/package-manifest.json) binds 81 source files and 49 package files. r5→r6 changes exactly `WCVNextLab.cpp`, `WCVNextSolo.cpp` and the compiled executable in that source inventory. Shared combat, saves, transport and catalogue bytes remain identical.

Local unpushed build snapshots preserve r5 at `5df9876255c5d68c2105a9f01d01a14fe5dd50b9` (`codex/milestones-r5-study-build-20260913`) and r6 at `b0cc92571735f74a01592f01e018f2d9bbd13b68` (`codex/milestones-r6-study-build-20260913`). They were made with an alternate index; the active implementation branch/index remains uncommitted. Build archives, logs, pre-build source parity and engine reconciliation are retained under `C:/Users/iputu/Documents/Project Support/Wonder Chess/study-builds/r5-clean-20260913` and `r6-clean-20260913`. Clean temporary checkouts are removed only after their package and evidence are retained and Git cleanliness is verified.

The initial Windows checkout failed on long archived paths; command-scoped `core.longpaths=true` recovered it without changing global Git settings. Installed UE 5.7.4, MSVC and shared machine caches were available. This is a clean **project checkout** build, not a clean-machine install or bit-identical executable proof. A build path change can change the executable hash; each archive has its own identity.

Earlier failures are preserved: a diagnostic test's establishment interval was too short and was corrected in the isolated fixture; r5's first compile used a private test API and was corrected to use public evidence; the first r6 identity capture omitted the required UnrealPak argument and was rerun successfully with the installed executable. No failed candidate or assertion is relabeled as a pass.

## Next work and acceptance limits

1. Finish the remaining actual B2 journeys: full-bench merge, all-resolution rejected-command/recovery paths, elimination/spectating, final results and restart. r6's current window is blocked pending manual dismissal of a Windows firewall dialog; the local solo study needs no incoming network permission. Never automate security prompts.
2. Use the clean-checkout candidate for the specified B1/B2 external studies when actual participants and devices are available. Record unfamiliar predictions, explanations before recap, independent revisions, acquisition/adaptation and full normal-speed endpoints. No participant contact is authorized by this record.
3. Select one justified interaction experiment from those findings, preserving the six-creature control and Root75's rejection. Do not manufacture pacing with extra waiting or consume holdouts for a known failed candidate.
4. Continue Bellback by changing the failed modeling method, preserving the already accepted r004 reference. Forms remain ART_REVISE; three candidates are retained. Obtain adequate forms and exact owner review before downstream topology/material/rig/animation/export stages. The full three-pilot visual slice remains open.
5. Close M2/M3 before ecosystem and solo-beta promotion in M4/M5. Complete dedicated-server/authenticated remote prerequisites and independent-device sessions for M6, then verify actual accepted release content, installation, performance and owner release acceptance for M7.

The [current tracker](MILESTONE_STATUS.md) and [current verification inventory](../../../reports/vnext/milestones/resume-20260913/verification.json) govern current status. Historical r4 evidence remains frozen in `reports/vnext/milestones/verification.json`.
