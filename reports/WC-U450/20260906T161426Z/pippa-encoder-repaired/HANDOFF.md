# Real Unreal encoding repair

The retained failed encoding at reports/WC-U450/20260906T161327Z/pippa-engine-motion-encoded failed on Python's strict ceiling of a float-published duration. Unreal recorded Hit as 0.40000000596046448 seconds and correctly required nine frames; Active is 0.55000001192092896 seconds with twelve frames. The helper now subtracts only 0.00001 frames before ceiling, while independently enforcing each recorded 20 Hz advance and a full accumulated authored duration. No input capture was changed.

Fourteen targeted tests pass, including the exact actual Hit duration/timestamps and a paused-final-frame negative. Fresh actual Blender 5.1.1 VSE execution and movie readback pass for all seven original Unreal captures: 151 total frames, 1280 x 720, 20 fps, 7.55 encoded seconds including endpoint frames. Report, CSV and PNG hashes remained unchanged. See encoded/encoding-report.json and encoder-readback.json for exact clip hashes, durations and source binding.

Encoder source SHA256 d55a5a22bb77e2db5da6e2ab5201f36c7042f40a22dc550be3b7cee2db5b9a14.
Tests source SHA256 1f9fd0ea769895fe4e84b7d076bf7a9be911b8fa4ee65476944169d66f7438f0.

This is real Unreal capture plus successful offline encoding. Continuous normal-speed visual review, audio approval, finished art acceptance and performance measurements remain separate. The earlier failed record remains failed.
