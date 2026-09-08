# Packaged 24-hero regression audit: PASS

Passed checks: 581951; failed checks: 0.

Packaged evidence: `C:\Users\iputu\Documents\Wonder Chess\reports\WC-U450\20260907T172100Z-r4\packaged100`
Native evidence: `C:\Users\iputu\Documents\Wonder Chess\reports\WC-U450\20260907T170300Z-closeout\native100`

This audit compares actual retained combat outcomes and exact historical package data. It does not establish visual or human acceptance.

```json
{
  "totals": {
    "fights": 12597,
    "timeouts": 1844,
    "ghosts": 524,
    "commands": 80759,
    "rounds": 3093,
    "round_seat_rows": 24744
  },
  "hero_deployed_unit_rounds": {
    "wc_u_dragonkin_guardian": 2704,
    "wc_u_dragonkin_priest": 579,
    "wc_u_dragonkin_ranger": 1797,
    "wc_u_dragonkin_rogue": 417,
    "wc_u_dwarf_guardian": 10904,
    "wc_u_dwarf_priest": 1361,
    "wc_u_dwarf_ranger": 3341,
    "wc_u_dwarf_warrior": 12366,
    "wc_u_elf_mage": 69,
    "wc_u_elf_priest": 356,
    "wc_u_elf_ranger": 7770,
    "wc_u_elf_rogue": 1266,
    "wc_u_halfling_mage": 1904,
    "wc_u_halfling_ranger": 6763,
    "wc_u_halfling_rogue": 1637,
    "wc_u_halfling_warrior": 8572,
    "wc_u_human_guardian": 11357,
    "wc_u_human_mage": 1481,
    "wc_u_human_priest": 2111,
    "wc_u_human_warrior": 7528,
    "wc_u_orc_guardian": 7444,
    "wc_u_orc_mage": 1119,
    "wc_u_orc_rogue": 3341,
    "wc_u_orc_warrior": 10646
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
      "encounters": 781,
      "wins": 780,
      "losses": 1,
      "draws": 0,
      "timeouts": 1
    },
    "20": {
      "encounters": 547,
      "wins": 431,
      "losses": 113,
      "draws": 3,
      "timeouts": 12
    },
    "25": {
      "encounters": 309,
      "wins": 249,
      "losses": 60,
      "draws": 0,
      "timeouts": 17
    },
    "30": {
      "encounters": 132,
      "wins": 32,
      "losses": 100,
      "draws": 0,
      "timeouts": 1
    },
    "35": {
      "encounters": 14,
      "wins": 13,
      "losses": 1,
      "draws": 0,
      "timeouts": 2
    },
    "40": {
      "encounters": 2,
      "wins": 0,
      "losses": 2,
      "draws": 0,
      "timeouts": 0
    }
  },
  "simulated_seconds": {
    "count": 100,
    "min": 1054.3,
    "median": 1284.525,
    "mean": 1270.7765,
    "p95": 1426.95,
    "max": 1574.6
  }
}
```

- Actual packaged -nullrhi -nosound 0H8B combat regression only; no rendering, listening, human input, two-machine LAN or frame-time acceptance.
- Native and engine process namespaces intentionally produce different settlement IDs; IDs must be unique within the packaged run, while every logical pre/post hash is compared exactly.
- Package SourceData is bound to captured packaging provenance and immutable payload hashes. Current workspace canonical data and current observed source files are not treated as compiled inputs.
- This package records a runtime neutrals.json hash observation; its bytes are checked against the captured SourceData.
- Native round-economy.csv and bot-decisions.csv lack pre-existing summary digests; this audit hashes retained bytes and checks their consistency with hash-bound native summaries/fights/compositions and packaged outcomes.
- Packaged legal-command evidence records aggregate counts and rejections; per-command decisions come from the retained native run, not a claimed packaged command trace.
- Simulated duration and headless wall time are not human match duration or graphical performance measurements.
