# Actual Unreal PNG motion encoder — technical handoff

The new `tools/unreal/encode_engine_motion.py` validates a completed root `WCAnimationReview` capture and encodes its original PNGs through installed Blender 5.1.1 VSE. It does not reconstruct the scene or modify the input evidence. No encoder was downloaded. Standalone ffmpeg/ffprobe were not found on PATH.

```powershell
python tools/unreal/encode_engine_motion.py '<actual capture>/engine-motion.json' --output '<fresh output>' --blender 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
```

The command refuses any existing output path. A started output is retained on failure and must not be reused. Review `encoding-report.json` and retained `blender-encode.log`; exit 0 means `ENCODING_PASS_REVIEW_PENDING` only.

Validation requires completed report and clip statuses, the requested clip count, stable unique hero/clip identities, the exact expected numbered PNG and CSV inventories, positive recorded/current bytes, PNG integrity and decoded dimensions, monotonic wall timestamps, finite animation times, 20 Hz advancement, at most one legitimate loop, and at least one complete authored clip of accumulated animation time. Paused, skipped, half-speed and incomplete timelines fail. Capture begins at zero or at most one 50 ms step after reset. H.264 requires even dimensions; the utility refuses rather than crops or resizes.

The recorded endpoint is preserved. Therefore the encoded duration is `frame_count / 20` and can exceed `clip_seconds` by one capture sample plus the final fractional interval. Movie readback checks actual frame count, fps, dimensions and duration. Input report, CSV and every PNG are hashed and revalidated after conversion. Videos are H.264 MP4 using Standard/sRGB and high-quality encoding; PNGs remain the lossless source.

Executed evidence in this directory:

- `probe_blender_vse.log`: actual Blender 5.1.1 confirms the installed `sequence_editor.strips` API and MP4 encoder support.
- `unit-tests.log`: 13 focused tests PASS, including missing frame, reused output without mutation and paused timeline. Fixtures are synthetic.
- `synthetic-encoded/encoding-report.json`: real Blender execution and movie metadata readback PASS for the explicitly labeled synthetic fixture, 21 frames, 20 fps, 64 × 64, 1.05 seconds, 2,251 bytes. Raw input bytes remained unchanged. This is encoder integration evidence, not Unreal capture evidence.
- `synthetic-encoded/encoder-readback.json`: generated movie SHA256 `ab3331df7fe89c76b2b3423ae79a4175520f404ac8578d5628dfe4ac854b925c`.

Encoder source SHA256: `47eea4f47c32ca1529b958fee7707e9c9b668676700ab7ec1f02c5f1f00a1fcb`.
Test source SHA256: `db919a4809408d4767353dfa68fb6fff641abf78aae3d22e772040acf257f3f4`.

Actual Unreal capture conversion was NOT RUN at this handoff because root's pilot capture was still pending. No normal-speed continuous visual review, audio approval, final animation approval or performance acceptance is implied. Offline fixed-step viewport capture does not measure real-time frame performance.
