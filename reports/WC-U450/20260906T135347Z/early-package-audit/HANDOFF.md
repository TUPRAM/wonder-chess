# Packaged 24-hero regression audit: FAIL

Passed checks: 120; failed checks: 1.

Packaged evidence: `C:\Users\iputu\Documents\Wonder Chess\reports\WC-U410\20260906T133515Z\early-packaged100`
Native evidence: `C:\Users\iputu\Documents\Wonder Chess\reports\WC-U410\20260906T131435Z\native-100-final`

This audit compares actual retained combat outcomes and exact historical package data. It does not establish visual or human acceptance.

```json
{}
```

- Actual packaged -nullrhi -nosound 0H8B combat regression only; no rendering, listening, human input, two-machine LAN or frame-time acceptance.
- Native and engine process namespaces intentionally produce different settlement IDs; IDs must be unique within the packaged run, while every logical pre/post hash is compared exactly.
- Package SourceData is bound to captured packaging provenance and immutable payload hashes. Current workspace canonical data and current observed source files are not treated as compiled inputs.
- Early package lacks a direct runtime neutrals.json hash observation. Its neutral bytes are bound through package payload, captured stage manifest and native catalog; this is not a direct runtime file-read hash.
- Native round-economy.csv and bot-decisions.csv lack pre-existing summary digests; this audit hashes retained bytes and checks their consistency with hash-bound native summaries/fights/compositions and packaged outcomes.
- Packaged legal-command evidence records aggregate counts and rejections; per-command decisions come from the retained native run, not a claimed packaged command trace.
- Simulated duration and headless wall time are not human match duration or graphical performance measurements.
