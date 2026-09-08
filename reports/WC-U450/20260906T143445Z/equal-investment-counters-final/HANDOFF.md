# Equal-investment counter measurements — executed 2026-09-06

**PASS execution: 192 actual native Combat fights, 352,876 assertions, 42,594 events, 27 timeouts, zero combat or measurement failures. These are selected composition measurements, not balance acceptance.**

The current bot-policy report showed Neris at 69 deployed unit-rounds, Elin at 356 and Iri at 417 across its 100 tournaments. This separate experiment checks usable contexts for those heroes with fully assembled teams. It does not replace that tournament evidence or measure shop acquisition.

Sources: `tests/runtime/measure_update_counters.cpp` and `tests/runtime/run_update_counters.ps1`. Existing simulation, canonical data, fixture generator, bot policy and other tests were read-only. The compiler consumed retained copies of the exact combat source/header and measurement source in this directory's `source/` folder, plus its generated `CatalogFixture.h`.

## Experiment

Every fight has six distinct heroes per side. Each formation costs 12 base gold. The one-star condition represents 6 purchased copies costing 12 gold per side; the uniform two-star condition represents 18 purchased copies costing 36 gold per side. This accounts for the three-copy merge rule. It excludes reroll costs, shop availability, XP and the time needed to acquire a formation.

Four subjects × three pressures × two star conditions × four seeds × both sides = 192 fights. Seeds are 1103, 2207, 3301 and 4409. The seed changes actual initiative ordering. Both sides use the same canonical simulation and modifiers. All starting cells and the transformed encounter cells are retained in `deployments.csv`.

| Subject | Six-hero deployment |
|---|---|
| Neris / Mage 4 | Ada, Borin, Rowan, Zura, Neris, Milo |
| Elin / Priest 4 | Sora, Dagna, Mira, Elin, Orla, Oren |
| Elin / Elf 4 | Ada, Tala, Sylas, Elin, Liora, Neris |
| Iri / Rogue 4 | Ada, Borin, Sylas, Kesh, Nella, Iri |

| Pressure | Six-hero deployment |
|---|---|
| Warrior 4 frontline | Cass, Dagna, Rok, Pippa, Sora, Neris |
| Ranger 4 spread | Sora, Sylas, Liora, Tessa, Finn, Varek |
| Mixed control | Borin, Tala, Nella, Sylas, Neris, Finn |

Positions are deliberately different for their roles: Mage backline behind two Guardians; Priests near their frontline; Rogues on the forward edges; Rangers spread across columns 0, 2, 5 and 7 in the back row. These are curated formations, not exhaustive or optimized best responses. Their results do not isolate the effect of a single hero.

## Results

Each entry is subject wins out of 16 fights, pooling the two star conditions and both sides. `counter-summary.csv` retains all 24 separate subject/pressure/star groups, eight fights per group.

| Subject | Warrior frontline | Spread Rangers | Mixed control |
|---|---:|---:|---:|
| Neris / Mage 4 | 16 / 16 | 0 / 16 | 16 / 16 |
| Elin / Priest 4 | 7 / 16 | 0 / 16 | 14 / 16 |
| Elin / Elf 4 | 2 / 16 | 0 / 16 | 9 / 16 |
| Iri / Rogue 4 | 9 / 16 | 0 / 16 | 16 / 16 |

The spread Ranger formation won all 64 comparisons against these subjects. That is a concrete follow-up priority for positioning and counter-composition testing; this sample cannot establish a global Ranger win rate or justify a numerical nerf by itself. Neris's low bot usage does not mean every assembled Mage team is ineffective: this Mage formation won every tested frontline/control comparison.

There were 27 canonical timeouts, including 18 in Priest 4 fights. Those outcomes used the actual combat timeout comparison and remain labeled as timeouts. Side dependence is material in the Priest 4/frontline pair: six subject wins from side 0 versus one from side 1 across eight trials per side. Do not hide this through pooled percentages; the formations and fixed seed set need broader follow-up before attributing it to a particular cause.

Elin is a tempo support, not a healer. Actual focus-hero events recorded 290 positive rate applications at 2600 bp in Priest 4/one-star fights and 297 at 3250 bp at two stars; Elf 4 recorded 130 applications at 2000 bp and 130 at 2500 bp respectively. These values show the real Priest source bonus and different recipient opportunities. They are packet counts, not independent beneficiaries or causal damage attribution. Neris delivered 97 focus stun packets across the two star conditions; all followed same-action damage at the same tick. Applied packet milliseconds can overlap, so actual target `stunned_ms` is measured separately. Iri emitted damage events and no invented dash event.

## Evidence and versions

- `summary.json` and `run.log`: matching assertion count and complete execution totals.
- `deployments.csv`: 2,304 unit deployments with costs, purchased-copy budgets, stars, positions, initiative, effective health/armor/resistance and all trait bonuses.
- `events.csv`: all 42,594 actual events with stable source/target/action, raw/resolved/absorbed/health/overkill values, damage types and mitigation inputs.
- `unit-outcomes.csv`: 2,304 final unit records, effective damage/healing/shield absorption, resolved-action counts and observed alive/moving/stunned/buff intervals.
- `outcomes.csv`, `counter-summary.csv`, `counter-analysis.json`: complete fight outcomes, timeouts, per-star groups, both-side pooled results and independent CSV reconciliation.
- `analyze_measurements.py`: executed readback checks for current output hashes, equal budgets, all unit/fight/event row counts and agreement between console and summary.
- `process.json`, `compile.log`, `compile.cmd`: actual compiler/process identity and input/output SHA-256 hashes. Every monitored input was unchanged during the run.

Schema `3.1.0`; balance `alpha_24_v0.4.1`; content digest `5ba20f6687bcd100616cd095c9741f1ad29bbb19b22c47204c0526adb8f3931a`. This digest includes the current descriptive Neris correction; no numeric catalog edits were made here.

Executed compiler: MSVC `19.44.35226.0`, installed through Visual Studio Community 2022. Hardware reported by Windows: AMD Ryzen 7 6800H with Radeon Graphics; 16,312,393,728 bytes system RAM. Native CPU combat only. No graphical frame-time measurement was made.

The first run at `reports/WC-U450/20260906T143320Z/equal-investment-counters` is retained. Its combats passed, but its console counted the summary-write assertion one higher than the JSON. The reporter was corrected and this fresh complete run now reports the same count in both places. No gameplay changes were required.

To repeat, choose a new directory:

```powershell
& tests/runtime/run_update_counters.ps1 -OutputDirectory "$PWD/reports/WC-U450/<fresh-UTC>/equal-investment-counters"
```

The runner refuses to overwrite an existing directory. No canonical tuning was adopted. Gallery/animation/audio quality, full tournament behavior, rendered frame times, 1H7B and physical 2H6B are outside this native comparison and remain subject to their separate evidence gates.
