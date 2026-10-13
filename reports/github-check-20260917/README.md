# GitHub and transfer-guide check — 17 September 2026

## Findings

- Read the user-specified `C:/Users/USER/Downloads/TRANSFER_TO_NEW_PC.md`. Its text matches the current GitHub guide after normalizing line endings. The local project-root copy predates publication and differs in two paragraphs describing source control/publication.
- Verified both GitHub `main` and `codex/milestones-b0-m7-20260912` at **123647ae220efc4b34e34baa13f8ac0dea87eb17**. The active local branch remains at **d80635f615810a93c3161c6bfd6c34c758b08260** with preserved working changes. GitHub's comparison reports two later commits: the milestone/Storybook/support publication and its final evidence record.
- The publication includes gameplay/source assets, tools/tests, production kits and selected support records. Built packages, machine state, caches/environments and some duplicate archives remain local. The guide's requirement for a whole-folder transfer remains appropriate.
- The guide still identifies the original engine as Unreal **5.7.4**, Blender **5.1**, SDK **22621** and Visual Studio **2022**. It does not prove the new machine is build-ready. Current recorded checks verify the installed compiler/SDK and Blender 5.2.1/Unreal 5.8.2 diagnostic exchange; the actual original-version project build remains unverified.

## Final archive recovery

The published repository contains all ten historical ZIP files that remained unresolved after D: recovery. Downloaded each file from the fixed revision above, compared its byte length and SHA-256 with the unchanged original transfer manifest, copied it only after an exact match, and rehashed the destination. **All ten passed.** No ZIP contents were executed.

Together with 424 initial and 275 D: recoveries, **all 709 originally missing files have now been recovered**. This closes the missing-payload recovery issue. It does not claim the whole working folder equals the old manifest: intentional machine configuration, launcher and evidence changes have occurred since that snapshot. The mismatching ZIP on D: remains untouched.

The document was treated as reference material. This review did not execute its transfer/build examples, pull or merge remote commits, reset the branch, rewrite the transfer manifest, or overwrite local development changes. Recovery continued under the owner's earlier explicit recovery authorization.

## Evidence

- [Remote comparison and recovery summary](summary.json)
- [Every restored archive, pinned source URL and hashes](archive-recovery.json)
- [Published transfer guide copy](github-TRANSFER_TO_NEW_PC.md)
- [Published publication report copy](github-PUBLISHING_REPORT.md)
- [GitHub checkpoint](https://github.com/TUPRAM/wonder-chess/tree/123647ae220efc4b34e34baa13f8ac0dea87eb17)

Remaining recorded setup issues: install/verify Unreal 5.7.4 for the original-version project build; resolve the single Windows PowerShell policy-dependent test failure. Git reconciliation with the publication commits is separate from this inspection and targeted recovery.
