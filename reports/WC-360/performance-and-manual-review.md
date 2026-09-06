# Performance and manual review

Current status: the final Shipping candidate completed its normal-speed native-TAA measurement with automatic PNG capture disabled and actual process exit0. Its required busy subset recorded frame p95=16.667002ms and p99=16.727901ms, with eight frames above33.33ms and none above100ms. Full manual acceptance remains blocked by the freshly observed Windows Security dialog. Earlier captures and their stalls are retained below; no result is estimated from mesh complexity.

## Machine and measurement

Lenovo 82RG; AMD Ryzen 7 6800H, 8 cores/16 threads; NVIDIA GeForce RTX 3060 Laptop GPU, 6,144 MiB VRAM, driver 580.88; 16,312,393,728 bytes system RAM; Windows 11 build 26200. Actual game adapter telemetry identifies NVIDIA despite the operating system's primary-adapter string naming the integrated AMD GPU. Unreal 5.7.4 CL51494982, D3D11.

The normal run launched the packaged Shipping executable directly from its packaged Windows directory, PID44708, 2026-09-06 07:48:19.492 UTC. It used 1920x1080, 1x simulation speed, primary/secondary screen percentages100/100, dynamic resolution0, VSync0, maximum FPS60, shadow/postprocess quality3, no Lumen/reflections, and the scripted human's actual server commands. The launch used `Start-Process -WindowStyle Hidden`; these are actual rendered viewport measurements, not a foreground interactive or fullscreen benchmark. PNG screenshots, state export and frame CSV instrumentation were enabled. Existing user UnrealEditor38828 and Blender29288 were preserved; no other task-owned game/build/render job overlapped the measured tournament. Ambient application details and GPU snapshot are in `shipping-normal1080/launch.json` and `gpu-before.csv`.

GPU values come from Unreal's `RHIGetGPUFrameCycles` API and are elapsed GPU frame timings, not an isolated shader-pass profile. The median does not establish a guaranteed FPS, and the recorded long frames are retained. The process's profiler stops adding frames when the match completes; work started afterward cannot affect the saved frame rows.

## Completed default-preset match

The match reached results at 08:03:59 UTC after937.36 seconds in its namespace, round20. Captain1 was eliminated in round10/place8, with automatic spectating and later bot rounds continuing. All seven deliberate authority probes passed. `shipping-normal1080/completed-session.json` is an immutable completed snapshot. The tracked inner process subsequently exited0 at08:11:40.848 UTC. The saved frame CSV hash was verified unchanged after exit.

The whole captured tournament contains53,837 frames, including43,249 combat frames. Peak process physical memory was489,902,080 bytes (about467.21 MiB). The exact required load contains1,381 frames with phase=Combat, at least12 living visible heroes and exactly4 live encounters. It is distinct from the4,077 frames with12 visible heroes at any encounter count.

| Measured quantity, required busy subset | Median ms | p95 ms | p99 ms | Maximum ms |
|---|---:|---:|---:|---:|
| Frame interval |16.666901|19.954798|46.974201|248.057007|
| Game thread active |2.0032|6.6501|41.337502|162.555298|
| Render thread active |3.5045|4.6508|5.5705|7.4917|
| GPU elapsed frame |17.009701|21.1999|39.0257|193.703903|

The required busy subset includes37 frame intervals above33.33ms and6 above100ms. Across the full capture, frame interval p50/p95/p99 was16.666901/19.059502/21.017599ms, with190 above33.33ms and68 above100ms. Screenshot capture and instrumentation are included; no measured hitch was silently dropped or attributed conclusively to capture without a separate comparison. **The default-preset measurement does not support a consistent1080p60 pass.**

Detailed values, quantile method and input hashes: `shipping-normal1080/frame-analysis.json` and `tests/runtime/summarize_frame_evidence.py`. The source CSV SHA256 is `1d9d4bff8090823521e12859c9cebdb24dc706b25bfdb521cbbf287c0f15a7a2`. Source-frame counts freeze after completion; confirm this hash again when the bounded process exits.

## Presentation and manual boundaries

The art lane inspected16 actual normal1080 game images covering11 active-recovery definitions and crowded rounds2/6/9/10/11. Twelve visible units fit, team markers remain legible, and the corrected spectator banner stays outside the board. See `reports/WC-330/shipping-normal1080-review.md`. Zura was not a living board piece in this particular tournament's sampled evidence. Still images do not prove continuous animation or exact visual/audio release synchronization.

The game reports `music_component_playing=true`; this is engine state, not a listening test. Human audio audition remains NOT_RUN.

The fresh native launch at approximately08:05 UTC exposed a real WonderChess window, then `sky.get_window_state` showed the Windows Security Allow/Cancel permission dialog covering the desktop. No game input or permission action was performed. The exact new idle process42804 was stopped and recorded in `shipping-manual-recheck/blocked.json`; the completed profile process44708 remained untouched. Earlier blocked evidence is preserved in `shipping-manual/blocked.json`.

The installed computer-use guidance prohibits acting on security/privacy permission requests, so user dismissal is needed before the full manual menu/practice/drag/click/settings/language/persistence/match/results/restart matrix can continue. No security settings were changed. Scripted match/RPC passes do not substitute for this manual gate.

## Preceding native-TAA candidate

The candidate sets native TAA explicitly (`r.AntiAliasingMethod=2`) while preserving1920x1080,100% render scale and game rules. The prior package did not export the anti-aliasing CVar; its use of Unreal's default TSR is inferred from unchanged renderer defaults and installed `SceneView.cpp`, not retrospectively measured. The TAA package built successfully and its actual telemetry confirms AA2,100/100 render scale and the settings above.

The bounded600-second normal1x run started08:25:48.217 UTC, inner PID49972, after all other task-owned game processes closed. It selected initial seed49 and read-only public scouting for definition10/Zura; it cannot alter rosters or fights. This differs from the baseline seed271828, so the two observed workloads are not a controlled causal A/B test. It retained Hidden launch style, PNG/state/profile instrumentation and existing user editor applications. The tracked inner process exited0 at08:35:49.819 UTC, with the match still in round13 combat after597.039 seconds in its namespace. This is a bounded performance sample, not a completed tournament.

The capture contains35,092 frames. Exact phase=Combat, at least12 living visible heroes and4 live encounters produced1,479 frames. Peak process physical memory was466,599,936 bytes. Actual AA2 and all settings are preserved in `shipping-normal1080-taa/frame-analysis.json`.

| Measured quantity, required busy subset | Median ms | p95 ms | p99 ms | Maximum ms |
|---|---:|---:|---:|---:|
| Frame interval |16.6668|16.667002|49.047802|136.643402|
| Game thread active |1.9011|5.8855|47.068901|122.644798|
| Render thread active |2.9127|3.8061|4.6415|5.7425|
| GPU elapsed frame |16.656401|20.5681|22.437901|141.498306|

This busy subset includes20 frame intervals above33.33ms and9 above100ms. Across all frames, p50/p95/p99 was16.6668/16.667002/16.748302ms, with103 above33.33ms and40 above100ms. Frame CSV SHA256 is `167f23a496481acf448a08cc7614bff39394172d5e254a792bffd91f4c065a85`. The result supports approximately60FPS at the95th percentile for this observed sample but does not erase the recorded stalls or certify consistently smooth gameplay.

The previous run's screenshot instrumentation is a potential confounder; it has not been proven to cause every stall. Game rules, art and graphics settings are unchanged by the subsequent namespace seed-summary correction. The distinct executable and capture mode of the final observation are explicit below.

## Final Shipping measurement without automatic PNGs

The final candidate is `builds/WonderChess-Alpha-Candidate/Windows/WonderChess.exe`, inner binary SHA256 `b3114876d3d75e6d89677f42b2a6117b5989ba8dfe91d4f50ef50e965a2103ac`, bound to immutable `alpha-candidate-provenance.json` SHA256 `89d6e2129cf28e491fb69d9d2fb2c68f2f50e0562dcdbc792322c2fe04786415`. Actual inner PID52460 ran from08:46:42.593 to08:56:43.868 UTC and exited0. The launch was normal1x,1920x1080, explicit nativeTAA2,100/100 screen percentages, no dynamic resolution, D3D11, VSync0 and60FPS cap on the same named hardware above.

`alpha-candidate-normal1080/launch.json` records seed49, definition10 read-only scouting, `automatic_screenshots=false`, `projected_bounds=false`, `null_rhi=false` and Hidden window style. The folder contains no automatic PNGs. Public-state/command/frame CSV instrumentation remained active. No other task-owned game/build/render job overlapped this measurement; the user's existing UnrealEditor and Blender applications were preserved and their process/memory snapshots recorded. This is an actual rendered viewport test, not a foreground interactive/fullscreen benchmark or clean-machine result.

The bounded600-second observation ended during round13 combat at597.392 seconds in its match namespace, `complete=false`. It is not a whole-match pass; the final candidate's separate rendered restart run supplies two complete tournaments. There are35,455 recorded frames and1,551 frames satisfying all three requirements together: Combat phase, at least12 living visible heroes and exactly4 unfinished encounters. Peak process physical memory is414,691,328 bytes (395.4805MiB).

| Measured quantity, final required busy subset | Median ms | p95 ms | p99 ms | Maximum ms |
|---|---:|---:|---:|---:|
| Frame interval |16.6668|16.667002|16.727901|55.200199|
| Game thread active |1.8962|5.7533|7.8283|55.124699|
| Render thread active |2.9393|3.6622|4.3592|6.0558|
| GPU elapsed frame |16.6574|20.4053|21.3811|23.5746|

The final busy subset contains eight frame intervals above33.33ms and zero above100ms. Across the entire capture, frame p50/p95/p99 is16.6668/16.667002/16.7136ms, maximum109.393997ms, with37 above33.33ms and one above100ms. GPU elapsed-frame timing is reported separately from display/frame interval and must not be read as isolated GPU shader execution time. The observed distribution is approximately the60FPS frame budget through the99th percentile, with occasional stalls retained; it is not a guarantee of smooth60FPS on every frame or another machine.

`alpha-candidate-normal1080/frame-analysis.json` records the quantile method through the checked-in analysis script, sample counts, settings and input hashes. Final frame CSV SHA256: `ce922ebb2cf86986ae825094cda4a0fb55cf7beb12ad06a8ab3e349a14698aff`; final session SHA256: `6070b058c06670b848407a89c02b2dd961654abb49257a24d75ccc9479d21dfb`. The final781-file byte audit passed without mismatches after all tests. The prior TAA run used the same seed/config/art but a different evidence-writer binary and enabled automatic capture, so it is not a same-binary causal A/B experiment.

## Final native manual recheck

After the profiler exited, `sky.launch_app` launched the final package bootstrap55048 and inner1276. Fresh native window4068378 was found. Its actual `sky.get_window_state` screenshot again showed Windows Security asking whether public/private networks may access Wonder Chess, with Allow/Cancel buttons and Epic Games publisher. No game input or permission action was performed. The record is `alpha-candidate-manual/blocked.json`, written08:58:08 UTC; the capture is displayed in the conversation, not invented as a local PNG. Only that verified idle process was stopped. `alpha-candidate-manual/final-process-state.json` confirms zero remaining task-owned games at08:58:41 UTC.

At the historical 08:58 checkpoint, the computer-use skill's `docs/guidance.md:242` instruction, "Do not act on security or privacy permission requests," caused the pause. The user subsequently explicitly authorized dismissal and continuation, superseding that skill restriction for Cancel. This is no longer an authorization blocker.

The authorized resume launched bootstrap55768/inner55080 and observed game window4855012. The Cancel click at (1063,683) was rejected by Computer Use: `point (1063, 683) is over PickerHost.exe "Windows Security", not target window WonderChess-Win64-Shipping.exe "WonderChess  "; activate the target or take a fresh screenshot before retrying`. A subsequent application inventory found running `process:C:\Windows\System32\PickerHost.exe` with an empty targetable-window list. This is a native targeting failure, not an automatic approval-review rejection. The actual record is `alpha-candidate-manual-resume/attempt.json`, written09:04:48 UTC. No successful permission action or game input occurred; the game remains open for the user to click Cancel. The historical zero-game inventory above does not describe this later live process.

Manual menu/practice/drag/click/options/language/persistence/full-match/results/restart checks remain blocked until the modal is dismissed. Full continuous animation/effect synchronization and human audio audition also remain open. All twelve heroes do now have reviewed living active-recovery samples, with additional actual final-package crowded images in `reports/WC-330/shipping-normal1080-taa-review.md`; a sampled still review is not continuous playback approval.
