# Current asset readiness inventory

Generated from canonical paths and seven explicitly selected import/cold-load reports. This is a file/hash inventory; finished art, continuous visual review, audio and performance approval are not inferred.

| Hero | Source revision | Export hashes | Bound importer report | Mesh present | Portrait present |
|---|---:|---|---|---|---|
| Ada | 8 | PASS | True | True | True |
| Mira | 7 | PASS | True | True | True |
| Rowan | 7 | PASS | True | True | True |
| Liora | 7 | PASS | True | True | True |
| Elin | 7 | PASS | True | True | True |
| Sylas | 7 | PASS | True | True | True |
| Borin | 7 | PASS | True | True | True |
| Tessa | 7 | PASS | True | True | True |
| Dagna | 7 | PASS | True | True | True |
| Rok | 7 | PASS | False | True | True |
| Zura | 7 | PASS | False | True | True |
| Kesh | 7 | PASS | False | True | True |
| Cass | None | MISSING_MANIFEST | False | False | False |
| Neris | None | MISSING_MANIFEST | False | False | False |
| Orla | None | MISSING_MANIFEST | False | False | False |
| Tala | None | MISSING_MANIFEST | False | False | False |
| Pippa | None | MISSING_MANIFEST | False | False | False |
| Finn | None | MISSING_MANIFEST | False | False | False |
| Nella | None | MISSING_MANIFEST | False | False | False |
| Milo | None | MISSING_MANIFEST | False | False | False |
| Sora | None | MISSING_MANIFEST | False | False | False |
| Varek | None | MISSING_MANIFEST | False | False | False |
| Iri | None | MISSING_MANIFEST | False | False | False |
| Oren | None | MISSING_MANIFEST | False | False | False |

Files: `asset-readiness.json` contains source/export/Content hashes, revisions, every missing ID, all selected report identities and binding decisions. `hero-clips-168.csv` contains exactly 168 required cells. `neutral-clips.csv` contains all 40 applicable clips for seven canonical creatures.

Verification: eight focused utility cases passed, plus final row-count/current-script-hash readback and an actual overwrite-refusal invocation. The refusal preserved existing evidence bytes. See `verification.json` and its referenced focused-case report.

The nine source/export-bound hero importer records cover Ada, Mira, Rowan, the three Elves and the three Dwarves. Current Orc exports exist but were not bound to an explicit current import in this invocation. A new import must be supplied explicitly on the next run.

All seven neutral source/export imports bind. Cold-load reports without source/export hashes remain unknown, and a report-level failure never establishes import readiness. Importer reports currently lack Unreal output binary hashes, so this utility records current Content hashes separately and does not claim those bytes are bound to the recorded import.

No report or candidate movie directory is scanned. Continuous review may exist elsewhere; it is unassessed here. Snapshot assets while their lanes are frozen, because reading the filesystem is not an atomic editor transaction.

Repeat with a new directory and the desired explicit report set:

```powershell
python tools/report_update_assets.py --output reports/WC-U450/<fresh-UTC>/asset-readiness `
  --import-report reports/WC-U430/20260906T135823Z/ada8-audio-import/import-wc_u_human_guardian.json `
  --import-report reports/WC-U440/20260906T140552Z/mira-import/import-wc_u_human_priest.json `
  --import-report reports/WC-U440/20260906T141648Z/rowan-import/import-wc_u_human_mage.json `
  --import-report reports/WC-U440/20260906T142439Z/import_alpha_assets/import-wc_u_elf_ranger.json `
  --import-report reports/WC-U440/20260906T142908Z/elves-dwarves-import/import-selected.json `
  --import-report reports/WC-U440/20260906T133639Z/neutral-import/neutral-import.json `
  --import-report reports/WC-U440/20260906T143108Z/cold-all-current/imported-assets.json
```
