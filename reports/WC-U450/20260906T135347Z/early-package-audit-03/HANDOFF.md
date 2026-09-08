# Packaged 24-hero regression audit: PASS

Passed checks: 585084; failed checks: 0.

Packaged evidence: `C:\Users\iputu\Documents\Wonder Chess\reports\WC-U410\20260906T133515Z\early-packaged100`
Native evidence: `C:\Users\iputu\Documents\Wonder Chess\reports\WC-U410\20260906T131435Z\native-100-final`

This audit compares actual retained combat outcomes and exact historical package data. It does not establish visual or human acceptance.

```json
{
  "totals": {
    "fights": 12748,
    "timeouts": 1864,
    "ghosts": 602,
    "commands": 78791,
    "rounds": 3158,
    "round_seat_rows": 25264
  },
  "hero_deployed_unit_rounds": {
    "wc_u_dragonkin_guardian": 3510,
    "wc_u_dragonkin_priest": 825,
    "wc_u_dragonkin_ranger": 1671,
    "wc_u_dragonkin_rogue": 586,
    "wc_u_dwarf_guardian": 11327,
    "wc_u_dwarf_priest": 1158,
    "wc_u_dwarf_ranger": 3364,
    "wc_u_dwarf_warrior": 6806,
    "wc_u_elf_mage": 48,
    "wc_u_elf_priest": 530,
    "wc_u_elf_ranger": 8937,
    "wc_u_elf_rogue": 2662,
    "wc_u_halfling_mage": 466,
    "wc_u_halfling_ranger": 9303,
    "wc_u_halfling_rogue": 2540,
    "wc_u_halfling_warrior": 9392,
    "wc_u_human_guardian": 11655,
    "wc_u_human_mage": 436,
    "wc_u_human_priest": 1923,
    "wc_u_human_warrior": 7242,
    "wc_u_orc_guardian": 5720,
    "wc_u_orc_mage": 116,
    "wc_u_orc_rogue": 5792,
    "wc_u_orc_warrior": 12022
  },
  "neutral_outcomes": {
    "1": {
      "encounters": 800,
      "wins": 800,
      "losses": 0,
      "draws": 0,
      "timeouts": 0
    },
    "2": {
      "encounters": 800,
      "wins": 800,
      "losses": 0,
      "draws": 0,
      "timeouts": 0
    },
    "3": {
      "encounters": 800,
      "wins": 800,
      "losses": 0,
      "draws": 0,
      "timeouts": 0
    },
    "5": {
      "encounters": 800,
      "wins": 800,
      "losses": 0,
      "draws": 0,
      "timeouts": 0
    },
    "10": {
      "encounters": 800,
      "wins": 800,
      "losses": 0,
      "draws": 0,
      "timeouts": 0
    },
    "15": {
      "encounters": 770,
      "wins": 770,
      "losses": 0,
      "draws": 0,
      "timeouts": 0
    },
    "20": {
      "encounters": 555,
      "wins": 555,
      "losses": 0,
      "draws": 0,
      "timeouts": 0
    },
    "25": {
      "encounters": 315,
      "wins": 315,
      "losses": 0,
      "draws": 0,
      "timeouts": 0
    },
    "30": {
      "encounters": 142,
      "wins": 142,
      "losses": 0,
      "draws": 0,
      "timeouts": 0
    },
    "35": {
      "encounters": 28,
      "wins": 28,
      "losses": 0,
      "draws": 0,
      "timeouts": 0
    }
  },
  "simulated_seconds": {
    "count": 100,
    "min": 1011.05,
    "median": 1229.225,
    "mean": 1236.0845,
    "p95": 1458.25,
    "max": 1523.8
  }
}
```

- Actual packaged -nullrhi -nosound 0H8B combat regression only; no rendering, listening, human input, two-machine LAN or frame-time acceptance.
- Native and engine process namespaces intentionally produce different settlement IDs; IDs must be unique within the packaged run, while every logical pre/post hash is compared exactly.
- Package SourceData is bound to captured packaging provenance and immutable payload hashes. Current workspace canonical data and current observed source files are not treated as compiled inputs.
- Early package lacks a direct runtime neutrals.json hash observation. Its neutral bytes are bound through package payload, captured stage manifest and native catalog; this is not a direct runtime file-read hash.
- Native round-economy.csv and bot-decisions.csv lack pre-existing summary digests; this audit hashes retained bytes and checks their consistency with hash-bound native summaries/fights/compositions and packaged outcomes.
- Packaged legal-command evidence records aggregate counts and rejections; per-command decisions come from the retained native run, not a claimed packaged command trace.
- Simulated duration and headless wall time are not human match duration or graphical performance measurements.
