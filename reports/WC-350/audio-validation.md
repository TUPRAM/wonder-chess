# Audio source validation

Measured 20 actual WAV files at 2026-09-06T06:30:15.700586+00:00. All19 required shared cue families and one courtyard music file are present. All are nonempty mono PCM16 at22050Hz; all20 corresponding runtime .uasset files exist. This is file/source evidence, not proof that every cooked sound loads or plays.

Full-scale rail samples: 0; samples at or above99% full scale: 0. Highest sampled peak: -4.935dBFS. These checks do not measure intersample true peak or clipping after sounds are mixed.

| Cue | Duration s | RMS dBFS | Sample peak dBFS | Rail samples |
|---|---:|---:|---:|---:|
| buy | 1.100000 | -21.399 | -7.763 | 0 |
| courtyard | 24.000000 | -27.864 | -15.919 | 0 |
| dash | 0.400000 | -22.530 | -9.347 | 0 |
| defeat | 1.800000 | -21.720 | -6.009 | 0 |
| draw | 1.100000 | -21.345 | -8.047 | 0 |
| heal | 1.100000 | -19.629 | -5.782 | 0 |
| health_loss | 1.100000 | -21.097 | -7.841 | 0 |
| magic_impact | 0.649977 | -22.157 | -10.520 | 0 |
| melee | 0.249977 | -18.799 | -5.895 | 0 |
| merge | 1.800000 | -20.643 | -5.250 | 0 |
| movement | 0.129977 | -31.054 | -17.264 | 0 |
| phase | 1.100000 | -19.715 | -5.769 | 0 |
| ranged_impact | 0.180000 | -23.318 | -10.215 | 0 |
| ranged_launch | 0.240000 | -22.423 | -8.930 | 0 |
| ready | 1.100000 | -21.393 | -7.735 | 0 |
| reroll | 1.100000 | -19.631 | -6.005 | 0 |
| sell | 1.100000 | -21.387 | -7.792 | 0 |
| shield | 1.100000 | -21.394 | -6.880 | 0 |
| stun | 1.100000 | -21.566 | -8.860 | 0 |
| victory | 1.800000 | -20.593 | -4.935 | 0 |

The courtyard file contains exactly529200 frames /24seconds. Last-to-first PCM step is 0.000000000 full scale (zero). First/last20ms RMS: -64.354/-72.198dBFS. The synthesis tapers both ends over1.5seconds. Runtime starts a new sound every24wall seconds, so finite frame scheduling can still create a gap; this is not a sample-accurate loop or perceptual listening pass.

Effects have a shared12-voice StopOldest concurrency object with25ms voice-steal release and80ms per-name debounce. Only the inspected encounter supplies combat sound events. One impact cue is emitted per update batch, grouping area hits but potentially suppressing other simultaneous cue families. Movement and ranged-launch cues are separately triggered by observed action transitions. Master/music/effects settings persist through GGameUserSettingsIni; no live persistence or mute check was performed in this audit.

All twelve dossiers contain individual audio directions. The current runtime and20 files implement shared family cues, without per-hero variants; this remains an unfinished content/review requirement. The sounds are attributed by their local provenance file and generator to original mathematical synthesis with no external samples. Numerical analysis cannot establish a polished fantasy soundscape, balanced loudness or unobtrusive repetition.

The earlier first-ui.log initialized XAudio2 on Headphones (Realtek(R) Audio),48000Hz stereo output,1024-frame callback,32 configured voices. That proves initialization only. No human audition or live audio output recording was performed.

Packaged regression source snapshot review: present fields cover attempted seeds/errors, engine/catalog digest, actual fight durations/winners/timeouts/ghost pairs, match durations and final placements. At this snapshot, command/reject totals, per-hero deployment/placement links, start/endUTC, separate profile/source/build provenance, explicit cap/final phase and WCEvidenceDir override are missing. The routine also exits normally regardless of failed trials. Root has authorized a bounded enhancement after this read-only audit; this paragraph records the pre-change state rather than predicting its result.

audio-validation.json includes individual file metrics, source/uasset hashes, exact paths, root continuity measurements, each hero audio direction and explicit evidence boundaries. Source/audio/binary files were not changed by these measurements.
