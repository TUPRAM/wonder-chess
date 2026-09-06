---
name: wc-release-evidence
description: Run or review Wonder Chess playable-alpha acceptance, bot tournaments, visual quality and release evidence.
---

# wc-release-evidence

1. Read `docs/QA_ACCEPTANCE.md` and distinguish provided reference tests from actual game tests.
2. Execute 1H7B, actual 0H8B combat trials, 2H6B authority checks, all hero clips, reimport and packaged launch according to the gate.
3. Report actual sample counts, seeds, data/build hashes, settings, hardware, measurements and defects.
4. Inspect screenshots/video instead of inferring quality from asset metadata.
5. Update evidence/status only for tests executed. Mark missing engine/art/package tests NOT_RUN, never successful skips.
6. A release needs a concrete executable path and full-match evidence; do not declare balance, mobile performance or eight-human hosting without their own tests.

Never overwrite another lane’s binaries, expose secrets, install untrusted helpers, make purchases, or publish without authorization. Maintain explicit rollback and execution evidence.
