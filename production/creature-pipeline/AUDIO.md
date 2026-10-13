# Creature sound production procedure

Version 1.2 · Sources checked **2026-09-21** · Companion to the [pipeline handbook](README.md).

## Qualified local fallback

Audacity 4.0 import, editable session save and 48kHz PCM export are now exercised;
see [toolchain](TOOLCHAIN.md). Keep self-recorded physical sounds and authored
procedural layers as a dependable route: wood/leaf/stone/water/ceramic contacts can
be combined without another generative provider. Record source ownership, processing
and exact variants. AI is optional and its actual terms/account allowance still
need checking before use. Save `.aup4` plus original layers and exported waves;
close the saved session before bundling. The qualification tone is not a creature cue.

## 1. Scope and entry conditions

Produce original, reusable creature effects, then prove they communicate the correct events inside Wonder Chess. This document authorizes no installation, generation, upload, purchase or account agreement. Those operations follow the active task's authorization. Preserve accepted Meshy colors; sound production has no material-editing role.

Begin with the creature's stable ID, accepted design revision, animation/event contract, candidate directory and named owner. Read current mechanics and timing from [the canonical catalogue](../../data/vnext/catalog.json) and their implemented runtime. Record authored-but-unimplemented events explicitly. Never add a heal, push, stun or damage event to justify a sound.

Use the [audio cue sheet](templates/audio-cue-sheet.csv) to record event ID, trigger, emitter/socket, intended duration, priority, variants, cancellation behavior and test. Proposed initial inventory: four contact variants, three impacts, two hit reactions, one ability preparation layer, one successful ability layer, one defeat and one victory. Add idle/hover layers only when their contribution survives a crowded-board audition. Counts are starting defaults, not generation obligations.

## 2. Choose and document the actual tool

Recheck the exact feature, selected model, applicable terms and allowance before the first batch and after any provider/model/plan change. This research did **not** inspect an account, confirm its balance, download a model or test local inference.

| Route | Verified public position on 2026-09-21 | Production decision |
|---|---|---|
| Adobe Firefly **Generate sound effects**, released Firefly model | Limited free daily generations are advertised; quantity and available features/models can change. Commercial use is described for commercially released Firefly sound generation, subject to its terms. | Preferred browser audition if the actual account offers the feature without payment. Record the visible model/feature label; if version is hidden, write `not exposed`. Do not infer another partner model's rights. |
| `stabilityai/stable-audio-3-small-sfx`, inference model ID `small-sfx` | Official weights and tooling exist. Documentation includes Windows CPU inference. Access requires a gated agreement, contact sharing and Gemma terms. | Candidate local route. Record exact model revision, file hashes and tool commit. Availability does not prove speed, quality or compatibility on this PC. Use the generation checkpoint, not the `-base` fine-tuning checkpoint. |
| ElevenLabs Free | Free-plan outputs do not receive commercial rights; upgrading later does not retroactively license earlier free generations. | Exclude from production asset sources for this commercial-game pipeline. |

Sources: [Firefly sound effects](https://www.adobe.com/products/firefly/features/sound-effect-generator.html), [Adobe allowance and commercial-use FAQ](https://helpx.adobe.com/creative-cloud/apps/generative-ai/generative-credits-faq.html), [Small-SFX model card](https://huggingface.co/stabilityai/stable-audio-3-small-sfx), [official runtime](https://github.com/Stability-AI/stable-audio-3), [ElevenLabs publishing rights](https://help.elevenlabs.io/hc/en-us/articles/13313564601361-Can-I-publish-the-content-I-generate-on-the-platform).

For Stable Audio, verify commercial eligibility rather than treating downloadable weights as unrestricted. The Small-SFX access page currently links a [Community agreement hosted with Stable Audio Open](https://huggingface.co/stabilityai/stable-audio-open-1.0/blob/main/LICENSE.md): commercial registration is required, and revenue conditions include affiliates and unrelated revenue. Its introduction describes free access below US$1 million annually; do not assume eligibility at the threshold. Follow the exact current download agreement and [licensing guidance](https://stability.ai/license), plus the linked [Gemma terms](https://ai.google.dev/gemma/terms). Preserve the agreement URL/version and the owner's eligibility/registration confirmation without unnecessary financial details. Record required notices for the intended distribution; distinguish shipping audio outputs from distributing model weights. If documents conflict or eligibility is unclear, hold that source and use a cleared alternative. Never silently accept an agreement for the owner.

For a later authorized local installation, pin dependencies in an isolated environment under project support, inspect installation scripts before running them, keep credentials outside Git, and keep any local UI on loopback. Do not copy documentation's remote-script execution one-liners blindly. The first capability test should be one short sound with recorded runtime, memory use, format and actual listening result.

If allowance is exhausted, authentication fails or local inference is unavailable: record the limitation, continue editing cleared audio, and use original procedural synthesis or owner-recorded material if authorized. Do not purchase credits, switch to a paid API, or use an unlicensed placeholder in the release.

## 3. Prompt and audition isolated layers

**Manual:** define the physical event first. Generate a short dry layer rather than a complete combat scene. Separate preparation, travel and contact so runtime can time each correctly. Omit dialogue, music, ambience and baked reverberation unless explicitly required.

Prompt pattern:

> One [material/object] performing [single action], [weight and texture], close and dry, isolated with quiet surroundings, short natural decay, no speech, no music, no repeated rhythm.

| Character | First prompt studies; generate each separately |
|---|---|
| Cragstoat | Heavy padded paw contacting dry stone; small stone ridges ticking together; short rushing lunge; compact rocky impact |
| Grandmother Root | Thick root settling into soil; gentle wood flex; soft leaf rustle; warm short flowering shimmer |
| Snapvine | Dry vine pulling taut; quick flexible lash; crisp thorn-jaw closure; small leaves settling |
| Prism Organ | Soft breath through one ceramic pipe; short glass resonance; two individually authored complementary note events |
| Reefglass | Small contained water swirl; delicate glass-shell tick; pressure sweep; brief breaking wave |

These are sonic proposals, not extra gameplay abilities. Start with one cue per character to compare tool quality. Then target three or four variations for frequently repeated events within the confirmed allowance. Save every raw result before selecting. Record rejected IDs and specific reasons: hiss, accidental voices, long delay, harsh transient, inconsistent weight or unwanted extra hits. After two unsuccessful focused revisions, change the prompt, source or synthesis method; do not generate indefinitely.

Audition equal-level A/B comparisons with the animation at normal speed, then in a mixed encounter. Listen on headphones and ordinary speakers at comfortable volume. Check whether an effect reads without looking at its label. Keep the owner's exact selection tied to candidate IDs; an automated waveform check cannot choose the artistic winner.

## 4. Preserve sources and make clean derivatives

Preserve raw inputs under `art-source/asset-studio/<asset_id>/inputs/audio/<provider>/<job_id>/`, including original audio, prompt and rights/provenance records. For local synthesis use a provider label such as `procedural` and a unique local job ID. Keep processed versions and recipes under the candidate's `audio/edited/` and `audio/recipes/`; place actual listening and mixed-game evidence in `reports/creature-production/<asset_id>/<candidate_id>/audio/`. The cue sheet links these locations; do not create a second authoritative raw-audio folder. Name files using stable asset ID, event, revision and variation, for example `wc_vn_cragstoat_footstep_r001_v03.wav`.

**Automatic where tooling exists:** compute SHA-256 immediately after download; inspect encoding, duration, channels, sample rate and peak. **Manual:** listen and verify the downloaded file matches the selected result. Never overwrite raw audio. Complete a [generation receipt](templates/generation-receipt.json): generation date, provider/model revision, task ID if exposed, prompt, settings/seed if exposed, allowance consumed, input hashes, terms URLs/check date, rights decision, raw hash and owner/reviewer. Use `not exposed` rather than inventing seeds or exact reproducibility.

Editing recipe, in order:

1. Copy raw material to a new derivative revision; preserve its original sample rate.
2. Select the intended action; trim excessive leading silence without removing its attack. Mark the audible onset for synchronization.
3. Remove clicks and unwanted DC offset where present. Apply short fades only where needed; inspect their effect on transients and tail.
4. Use restrained cleanup/EQ when justified by listening. Record parameters and tools; do not erase useful texture through aggressive denoising.
5. Resample once to **48 kHz** with a documented quality setting. Do not relabel 44.1 kHz samples as 48 kHz.
6. Export PCM WAV, normally mono for positional one-shots. Preserve stereo only when purposeful; audition mono compatibility before downmixing. Keep float/24-bit edit masters; create the import format actually tested with this Unreal build.
7. Measure again and hash the derivative. Verify zero clipped/export-clamped samples, intact decay, no unwanted silence and no audible edit boundary. Dither when reducing integer bit depth where appropriate; record the choice.

Follow the centralized [acceptance defaults](ACCEPTANCE.md): zero clipped/export-clamped samples and delivered one-shot/actual crowded-mix peaks at or below **−3 dBFS**, plus listening review. These are proposed policies, not new measured results. Leave more source headroom when layering requires it. Do not force one LUFS target onto every short effect; compare perceived level and transient behavior. `dBFS` describes digital sample headroom; true peak estimates reconstructed peaks; LUFS estimates perceived loudness. If measured, record true peak and loudness with method/duration/gating. Unavailable measurements are `not measured`, not passes. Preserve intentional dynamics and explain approved exceptions.

## 5. Bind sound to Unreal events

Import derivatives into the isolated character candidate audio folder. Record SoundWave paths, import settings, SoundCue/MetaSound or runtime selection, gains, pitch range, attenuation, concurrency group and submix route. Reimport must preserve references. Never change combat results or timing to fit audio.

| Event | Binding and cancellation rule |
|---|---|
| Foot/root contact | Fire on a contact-phase crossing during actual travel; avoid duplicate triggers during blends, wraparound and start/stop. Hovering creatures have no fabricated footsteps. |
| Attack preparation/travel | Start from real attack/cast state. Stop sustained preparation if canceled or the actor dies. |
| Damage/hit | Play contact or reaction only for the actual corresponding resolved event, with event-ID deduplication. |
| Heal/guard | Trigger successful healing or prevented-damage feedback from the recorded result; a generic animation label is insufficient. |
| Push/control | Reflect actual resolution and displacement; distinguish blocked/no-op outcomes when needed. |
| Defeat/victory | Play once for the corresponding state; prevent replay while a pose loops. |

Set an explicit voice budget. Start by comparing Bellback's shared 16-voice limit with a mixed roster; it is a measured precedent, not a universal budget. Prioritize ability outcomes and defeat over decorative rustles. Test retrigger intervals, randomized variants without immediate repetition, voice stealing, interrupted loops, off-screen emitters and listener/camera distance. Pitch variation must not corrupt Prism Organ's intentional notes. Do not claim spatial audio merely because a WAV has two channels.

## 6. Verify the real mix and package

Run one-character, duplicate-character and mixed **20-unit** encounters in the packaged game. Include simultaneous abilities, canceled casts, target death, successful and ineffective healing, prevented damage, blocked/successful pushes, movement stops and battle end as applicable. Compare sound dispatch logs with authoritative event IDs/timestamps. Audio must not create or suppress gameplay events.

Capture the **actual game master submix**, including silent intervals, alongside route timestamps and event counts. Do not substitute concatenated source WAVs. Bellback's [audio evidence](../../reports/bellback-production-20260920/audio-content-audit-r3.json) documents two traps: unfocused muting produced silence, and submix auto-disable shortened recordings. Its successful run used temporary process overrides `-ini:Engine:[Audio]:UnfocusedVolumeMultiplier=1.0` and `au.NeverDisableSubmixes 1`. Revalidate these against the installed engine when needed; do not change global defaults. Test normal focused playback separately.

Wait for WAV finalization, validate RIFF/data size and stable file size, compare sample duration against wall time, and inspect the exporter's actual clamp value. Bellback's exporter could clamp near 0.9999 rather than full integer scale, so counting only ±32767 was insufficient. Record peak, nonzero samples, channel relation, duration discrepancy, clamp count and hash. Listen to the entire scenario and key event excerpts. Silence during quiet intervals is valid; a completely silent combat recording is not.

Measure performance in a **separate unrecorded run** with representative normal settings. Recording overrides and capture overhead are not the benchmark baseline. Retain failed captures with reasons and identify the accepted run unambiguously.

## 7. Exit and later changes

Required evidence: rights/provenance record, immutable originals, editable recipes, imported-file hashes, event-binding sheet, dispatched-event checks, individual auditions, actual packaged mix, numerical audit, performance reference and owner's listening acceptance of this exact revision. Complete the [review record](templates/review.md) with technical and human outcomes separately. Bellback's approved sound does not approve the next creature.

A changed source/model, waveform, gain, concurrency rule, timing or mix invalidates the affected checks and listening decision. Re-run those dependencies, retain prior accepted evidence and provide a rollback path. Stop only the blocked audio gate while independent model/animation work continues. Report missing evidence plainly; file presence, tool success and silence-free output do not establish finished sound.
