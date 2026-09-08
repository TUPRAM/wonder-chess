# Packaged 24-hero regression audit: FAIL

Passed checks: 0; failed checks: 1.

Packaged evidence: `C:\Users\iputu\Documents\Wonder Chess\reports\WC-U450\20260907T172100Z-r4\packaged100`
Native evidence: `C:\Users\iputu\Documents\Wonder Chess\reports\WC-U450\20260907T170300Z-closeout\native100`

This audit compares actual retained combat outcomes and exact historical package data. It does not establish visual or human acceptance.

```json
{}
```

- Actual packaged -nullrhi -nosound 0H8B combat regression only; no rendering, listening, human input, two-machine LAN or frame-time acceptance.
- Native and engine process namespaces intentionally produce different settlement IDs; IDs must be unique within the packaged run, while every logical pre/post hash is compared exactly.
- Package SourceData is bound to captured packaging provenance and immutable payload hashes. Current workspace canonical data and current observed source files are not treated as compiled inputs.
- This package records a runtime neutrals.json hash observation; its bytes are checked against the captured SourceData.
- Native round-economy.csv and bot-decisions.csv lack pre-existing summary digests; this audit hashes retained bytes and checks their consistency with hash-bound native summaries/fights/compositions and packaged outcomes.
- Packaged legal-command evidence records aggregate counts and rejections; per-command decisions come from the retained native run, not a claimed packaged command trace.
- Simulated duration and headless wall time are not human match duration or graphical performance measurements.
