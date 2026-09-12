# Wonder Chess successor programme

Adopted from the user's implementation instruction on 2026-09-10. This is the authority for the new **`wonder_vnext`** candidate profile. The existing `alpha_24` product, sources, assets and packaged evidence remain the legacy comparison lane. The old fixed 24-hero rule and visual-only equipment restriction apply to that legacy profile; the successor has an uncapped design roster and gameplay relics. No unrelated project supplies code, art or lore.

The intended product is an eight-seat Windows Unreal auto-battler about extraordinary creatures, readable spatial combinations, preparation decisions and automatic combat. The creative direction is mythic storybook in Aurelune, beginning with the Wondergrove sanctuary board. The target full tournament duration is 35–45 minutes. This is a tuning target, not a measured result.

## What exists in this lane

- `data/vnext/catalog.json` is the only authored source for successor hero definitions, executable tuning, trait membership and thresholds, relics, neutral layouts, bots and world identity.
- Fourteen new hero dossiers are authored. Six are enabled for the gameplay laboratory. Eight future heroes have prose ability contracts and **no fabricated executable stand-ins**. Six prototypes are a milestone batch, not a final roster cap.
- Nine races and nine classes have asymmetric membership, variable thresholds and behavioral design contracts. They are deliberately inactive in the laboratory until their actual behavior is implemented. Missing members at a threshold are recorded as design gaps.
- Twelve relics have concrete geometry, timing and magnitude tradeoffs, compatibility and generated runtime definitions. Runtime and transaction verification are recorded separately by the implementation owner.
- Seven original neutral identities and twelve wave layouts support a complete provisional schedule. They currently use basic combat: special boss behavior and the teaching value of the layouts remain unfinished.
- Art briefs, pipeline contracts and review requirements are authored. A successful source build or a proxy model is not finished art or human approval.

## Reading and execution

Read [the gameplay contract](PRODUCT_AND_COMBAT.md), [the art/UI production contract](ART_UI_PRODUCTION.md), and [the validation and rollout gates](VALIDATION_AND_ROLLOUT.md). Generated [hero dossiers](generated/hero_dossiers.md), [trait coverage](generated/coverage.json), and [relic catalogue](generated/relic_catalogue.md) are derived views and must not be edited independently.

Use the [laboratory play guide](LAB_PLAYGUIDE.md) for the packaged six-creature experiment and the [implementation matrix](IMPLEMENTATION_MATRIX.md) for the exact boundary between this checkpoint and the complete programme.

From the repository root:

```powershell
python tools/vnext/catalog.py --stage
python tools/vnext/catalog.py --check --stage
python -m unittest discover -s tests -p test_vnext_catalog.py -v
```

The compiler generates identical native headers for standalone tests and Unreal, plus the exact runtime JSON. The registry loads the successor only with `-WCProfileName=wonder_vnext`; the ordinary launch retains the legacy default. Use the dedicated laboratory frontend with `-WCLab -WCProfileName=wonder_vnext`. Its executable/package path is supplied by the actual build evidence, not invented here.

The engine refuses a missing or modified staged catalog and refuses unknown profile names. Regenerating data requires rebuilding the native adapter: the staged runtime bytes, compiled header and source digest must agree. This prevents stale binaries from silently executing different tuning. The digest establishes identity and consistency, not security certification or balance acceptance.

## Milestone ownership and progression

M0 produces this successor contract, canonical designs, generated dossiers, inventory and test matrix. M1 proves six mechanics in real combat and then with five external players. M2 produces three serial art pilots, one board and a complete preparation/combat/recap visual slice. M3 establishes tournament progression, relic lifecycle and interruption recovery. M4 expands the roster in coherent small batches. M5 proves solo usability and repeat play. M6 proves remote dedicated-server play. M7 freezes exact content and completes release evidence.

These milestones have independent evidence columns: authored, executed, imported, visually reviewed, packaged, externally tested and accepted. Do not advance all columns because one test passed. `reports/implementation_state.json` remains the actual status ledger. No document here self-issues creative approval, proves fun, promises off-turn work, authorizes paid services, or authorizes public deployment.

One owner writes each canonical source, shared schema and binary. New data changes are generated once by the source owner and reviewed through the native fixture. Existing art stays intact. Changing an AS1 critical form twice without improvement requires a different construction method or a local stage stop, while independent work continues.
