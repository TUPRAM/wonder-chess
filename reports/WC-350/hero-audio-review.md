# Hero active sound variants - generation and PCM checks

Twelve original, deterministic active-skill variants were generated with Python 3.11.8 using only wave, math, random and other standard-library modules. Source sound directions were read from each alpha dossier and compared with canonical data/units.json. No recordings, voices, samples, downloads or external services were used.

Each file is mono, 16-bit PCM at 22050 Hz. The synthesis executed twice per hero and produced identical PCM both times. All twelve file hashes are distinct; each file has zero clipped samples and starts/ends at zero. The existing nineteen shared cue families and courtyard music were preserved byte-for-byte by SHA-256.

| Hero | Skill | Duration (s) | Peak dBFS | RMS dBFS |
|---|---|---:|---:|---:|
| Ada Brightshield | Sunward Guard | 0.84 | -9.94 | -24.44 |
| Mira Dawnwell | Mend | 1.04 | -13.29 | -27.33 |
| Rowan Emberwick | Ember Orb | 0.72 | -8.56 | -24.15 |
| Liora Leafstep | Leafstep | 0.44 | -13.24 | -26.75 |
| Elin Moonsong | Quickening Song | 1.12 | -10.46 | -30.42 |
| Sylas Duskrun | Backline Dash | 0.56 | -15.23 | -26.38 |
| Borin Stonebell | Bell Stomp | 0.70 | -9.22 | -24.01 |
| Tessa Brassbolt | Heavy Bolt | 0.47 | -10.51 | -24.73 |
| Dagna Anvilheart | Anvil Sweep | 0.66 | -8.18 | -26.53 |
| Rok Sunward | Battle Tempo | 0.70 | -12.37 | -25.19 |
| Zura Stormcall | Storm Ring | 1.10 | -8.40 | -24.70 |
| Kesh Quickwind | Closing Dash | 0.36 | -14.80 | -27.33 |

The corpus totals 384,640 bytes. The highest measured peak is -8.18 dBFS; this is linear digital headroom, not a claim about perceptual loudness or sound pressure. Mira is deliberately quieter than the damage variants, Elin uses plucked string synthesis instead of bells, and Kesh has a shorter envelope than Sylas. Rok uses filtered noise for a breath-like accent without a human voice.

The detailed provenance, exact authored cue mapping, recipe rationale, seeds, source/dossier hashes, file hashes and per-file measurements are in hero-audio.json. Reproduce with `python tools/audio/hero_variants.py`. Actual command output is preserved in hero-audio-generation.log.

At the generation checkpoint, Unreal import and listening review were not run. No perceptual quality or packaged acceptance is inferred from the PCM checks.

The subsequent audio-only full-editor import completed with exit 0 at 14:38:16 Singapore time using the existing root-owned importer with PCM encoding. A separate cold commandlet then loaded all 32 current SoundWaves (12 variants, 19 shared cue families and music), verified mono PCM format and each source WAV duration within 1 ms, and recorded saved-asset hashes in `hero-audio-import-cold.json`. The full-editor import output is `hero-audio-import.log`; the cold read appears in `reports/WC-340/effect-import-uv2-console.log` before the glyph reimport. That commandlet exited 0 at 14:39:05 and reported 0 commandlet errors and 0 warnings.

Listening review remains NOT RUN by this task. Observed-action mapping, voice grouping, in-game effects volume, mix clarity and packaged playback remain the integration lane's verification responsibility.
