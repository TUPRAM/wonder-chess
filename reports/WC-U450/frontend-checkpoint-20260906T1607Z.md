# Native UI correction checkpoint

Recorded 2026-09-06 16:07 UTC. Runtime source is frozen for root-owned compilation. This is a source handoff, not a build or playability pass.

- The prior actual editor build failed in `reports/WC-U430/20260906T160000Z/editor-build-icons-preview-audits/build.log`: a missing closing Slate bracket in the partner-portrait button and the `Owner` local shadowing `AActor::Owner`. Both source errors are corrected.
- `AWCMatchHUD::SelectPreviewForReview(const FString& Id, const FString& Clip)` now delegates to the native front end. An initialized front end and known catalog hero are required; active entry rejects selection. It selects Detail / Skill / star 1, restores the real preview camera, disables turntable, loads the actual mesh and requested animation, and returns the actual clip-load result. Review motion override is local to the front-end instance. It does not write showcase or motion preferences or change the controller's saved motion setting.
- `git diff --check` passed for the four correction files; Git emitted the existing LF-to-CRLF conversion notices. Root must compile and execute the corrected source.

## Queued actual UI checks

Selection rejection: launch the current real game target with `-WCAutoStart -WCHumans=1 -WCSelectionAudit -WCEvidenceDir=<fresh-directory>`. Do not combine with `WCExercise`. The bounded audit purchases an actual offered hero, selects its actual bench copy, sends an invalid move through HUD dispatch, verifies a real rejected reply and retained state/selection, places it legally, tests an actual unowned sale rejection, then sells the owned copy. Inspect `selection-rejection-audit.json` and its actual PNGs. This is a software-driven authority/UI fixture, not a human match.

Connection recovery: launch an idle real host with `-WCHost -Port=<live-port>` and no auto-start/exercise. Confirm a separate test port is unused. Launch the client with `-WCJoin=127.0.0.1:<unused-port> -WCFrontEndRecoveryAudit -WCRecoveryTarget=127.0.0.1:<live-port> -WCEvidenceDir=<fresh-directory>`. It waits for an actual Unreal failure callback, checks the visible retry UI, activates native Slate Join, verifies actual two-controller protocol/digest agreement, then activates Leave LAN and verifies return to the local title. Inspect `network-recovery-audit.json` and PNGs. This two-process loopback fixture is not two-physical-machine LAN evidence.

The existing full front-end audit now additionally exercises combined race/cost/role filters and gallery scroll restoration. Native original line emblems and model-derived partner portraits are authored in runtime code but await visual inspection in the corrected build. The shop preview uses root's shared `PreviewRosterCommand` authority helper; root separately verified meaningful purchase/merge/cascade/full-bench/swap/sale parity.

## Independent evidence tooling

`reports/WC-U450/20260906T160147Z-gallery-frame-analysis/reference-suite.log` records 119/119 passing reference tests. The focused summarizer log records 10/10 passing fixtures, including correctly parsing quoted Windows launch arguments. The context-bound preliminary frame summary in that folder uses the actual 4,053-row editor-game gallery capture and binds root's actual Pippa/Ada/native-compilation workload context. It is preliminary instrumented editor evidence, not final package performance. It contains no combat or eight-neutral samples.
