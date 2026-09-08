# Editor-task wrapper review

The corrected wrapper passed 16 checks: the same fourteen refusal cases plus two explicit environment-restoration cases. **No editor process was launched.** Only report-scoped test files were authored by this lane; the wrapper, game source and art files were unchanged during these tests.

Tested wrapper: `tools/unreal/invoke_editor_task.ps1`, SHA256 `f8ca0b3ac209b12445159ebad68629adefb1ed715688487ee0d3b1a6e1c6a298`. Runtime: PowerShell 7.6.5. Detailed inputs, errors, hashes and cleanup values are in `result.json`; the replayable report-scoped fixture is `run-refusal-tests.ps1`. The fixture refuses to overwrite its own prior result.

## Executed results

- Invalid and path-shaped hero IDs refused before launch/output creation.
- Existing paths outside `reports`, a normalized `reports/../docs` traversal, and the reports root itself refused at the reports-boundary check.
- An existing evidence directory retained its marker SHA256 `04af1d63fa6d8954469665ab6fcf112ce907478381e7cfb717d05e54127cf4d5`.
- Hero, audio, and audio-only selectors on incompatible tasks refused; audio-only combined with hero selection refused.
- Missing editor and unknown task refused.
- Wrong-case hero and task now refuse before launch/output creation.
- Two controlled Start-Process interceptions exercise the wrapper's actual catch/finally path after its environment assignments. Previously absent variables remain absent; a mixture of retained values and absent variables is restored exactly. Their process reports correctly remain FAIL with null PID/exit code because no process was created. These are cleanup tests, not failed Unreal tasks.

The Start-Process function in the fixture is a defensive interception, not a pretend editor. Fourteen refusal tests require zero calls to it. The two cleanup tests deliberately require exactly one intercepted call each. Both paths record zero real process launches.

## Findings and fixes

The initial reviewed wrapper used case-insensitive PowerShell validation while the Python runner/importer compares exact canonical spellings. `WC_U_HUMAN_GUARDIAN` and `IMPORT_ALPHA_ASSETS` reached the intercepted launch boundary and created report directories. Root fixed these with exact-case hero membership and explicit lowercase task validation. The corrected refusal results prove both cases now stop before side effects.

The initial wrapper also restored absent helper variables as empty strings under this installed PowerShell runtime. Root changed the null restoration path to remove only the five whitelisted environment variables. The two new cleanup tests verify exact null/value restoration.

The first fixture invocation in `../20260906T162820Z-editor-wrapper-refusals` had a test-interceptor script-scope counter error. It remains retained and must not be treated as a valid launch-count result for those two cases. The fresh corrected fixture in `../20260906T1630Z-editor-wrapper-refusals` recorded 12/14 passing refusals and two actual intercepted launch attempts, corroborating the source findings. This current run records 16/16 after root's fixes.

## Process/parser evidence and remaining boundaries

Read-only inspection of the actual `reports/WC-U440/20260906T162355Z/three-face-import` evidence corroborates the intended successful path: the quoted project/Python script/log arguments use forward slashes, the real process exited 0, and `import_alpha_assets.json` records task success in Unreal 5.7.4. `import-selected.json` identifies the three requested heroes and explicitly leaves cold-reload validation pending in a separate process. This review does not promote that import report to art acceptance.

The wrapper explicitly fails when the required task report is absent; its success label appropriately requires inspection of import details. No editor launch, missing-task-report process simulation, or import rerun was performed by this review.

Read-only limits remain: `WaitForExit()` has no wrapper timeout, so a hung editor needs external supervision; the path guard is lexical normalization, and this suite did not test reparse-point traversal; a failure writing the final process JSON would occur before environment restoration in the same finally block. These are source-inspection observations, not executed hang, filesystem-link or disk-failure tests. The requested refusal and ordinary cleanup cases have passed.
