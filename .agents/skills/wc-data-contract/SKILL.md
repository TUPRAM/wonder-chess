---
name: wc-data-contract
description: Validate or change Wonder Chess canonical roster, ability, trait, profile or generated data.
---

# wc-data-contract

1. Read `docs/GAME_RULES.md` and only the affected hero/data records.
2. Edit canonical JSON through one owner; do not patch imported tables or generated dossiers independently.
3. Run `python tools/validate_kit.py`, `python -m unittest discover -s tests -v`, `python tools/build_documents.py`, and `python tools/compile_catalog.py`.
4. Review the diff, rerun both `--check` modes, and port changed fixtures to engine tests.
5. Record deliberate balance changes/version and actual failures. Data checks do not establish gameplay balance.

Never overwrite another lane’s binaries, expose secrets, install untrusted helpers, make purchases, or publish without authorization. Maintain explicit rollback and execution evidence.
