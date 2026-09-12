# Six-creature balance findings

These are findings from `wonder_vnext_lab_0.1.0`, source digest `6f9a4178ec78d48c8f6fb8d487d88069327a5ca526652724dc12a8654f574ebb`. They concern the six active prototypes, provisional bots, inactive traits and basic neutral encounters. They do not establish full-roster balance or human enjoyment.

The first 1,000 native tournaments completed 187,141 encounters. Of those, 26,434 reached the combat deadline: **14.125%**, above the proposed 2% limit. **199 tournaments reached the round cap.** The median simulated tournament lasted 31.332 minutes. Median phase durations were 2.911 minutes of preparation, 24.946 of combat and 3.5 of settlement; phase medians need not sum to the median total. Bots ready early, so these durations do not determine normal human tournament length.

The completed batch and reconciliation are preserved in [native/tournaments-1000](native/tournaments-1000/) and [the analysis](native/tournaments-1000-analysis.json). That batch precedes the save-authority v3 correction. Its balance observations remain valid for that exact source. Final-source evidence is recorded separately in the implementation handoff.

## What the controlled probe found

The [timeout probe](timeout-probe/20260910T153323985Z/) reproduced and inspected the earlier ten-seed sample. All 237 timeouts were PvP or ghost fights: 207 of 1,024 PvP fights, 30 of 75 ghost fights, and zero of 778 neutral fights. Most timeouts still had several surviving units. They were not simply one frozen unit unable to find another.

In seed 1, all 22 inspected timeouts retained a living Grandmother Root and still produced damage and healing during their final five seconds. Healing totaled 51,523,016 centipoints against 98,482,469 centipoints of health damage in those fights. This is evidence of sustained combat and an association with the healer; it is not an isolated estimate of her contribution. Round, star level, duplication and the bot's recruitment preferences are confounders.

Cragstoat also needs a clearer acquisition-to-placement path. Of 54 Cragstoat instances inspected in that seed's timed-out fights, 36 never charged. Adjacent deployment often gave them no completed approach movement from which to build momentum. A mechanically valid ability can still be a poor experience if normal bot or player formations rarely activate it.

One exact fixture, seed 1 / round 7 / encounter 2, illustrates why simply extending the deadline is not an accepted fix:

| Isolated probe | Resolution |
|---|---|
| Current rules | 45-second timeout; A wins the adjudication with two survivors per side |
| Healing disabled in this fixture | 24.4 seconds; A wins, three survivors versus none |
| Basic attacks increased by 25% in this fixture | 19.85 seconds; A wins, four survivors versus none |
| Deadline extended to 90 seconds | Fight resolves at 69.7 seconds; B wins, two survivors versus none |

These temporary probe changes were not adopted into canonical tuning. One fixture cannot select the correct global change, and extending the deadline can change the winner as well as the duration.

## Next controlled tuning batch

1. Keep the current catalogue as the comparison fixture. Test a separate candidate with Grove pulse magnitudes at 75% of their current values, preserving timing and geometry. Re-run the same seeds and equal-investment favorable/unfavorable formations.
2. Independently test Cragstoat formation incentives that leave an actual approach lane. Compare charge exposure, landing success, survival and counterplay before changing charge damage.
3. Log recruitment exposure and purchase opportunity alongside deployed usage. Rare Prism Organ or Reefglass appearances in these bot compositions do not by themselves prove weakness.
4. Measure round caps, neutral outcomes, burst deaths, healing contribution, repeated same-hero formations and timeout-heavy matchups separately. A lower aggregate timeout rate is insufficient if it removes positional sustain as a useful strategy.
5. Use normal-speed human combat sessions to check whether each change is understandable and satisfying. Recruitment and scouting tasks wait for the successor tournament frontend.

The intended outcome is useful positional healing and meaningful movement pressure with practical counters. No tuning change is accepted solely because it shortens a simulation.
