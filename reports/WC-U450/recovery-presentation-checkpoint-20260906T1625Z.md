# Recovery presentation source checkpoint

Runtime source is frozen for root-owned compilation. The changes below have passed `git diff --check`; they have not yet been compiled or executed. Prior recovery evidence and its problematic screenshots remain unchanged in `reports/WC-U430/20260906T161534Z/network-recovery-ui`.

## Installed API investigation

The installed Unreal 5.7 source at `C:/Program Files/Epic Games/UE_5.7/Engine/Source/Runtime/Engine/Private/PlayerController.cpp` initializes `bAutoManageActiveCameraTarget` to true (line 230), calls `AutoManageActiveCameraTarget(GetPawn())` after restart/possession, and falls back to `SetViewTarget(SuggestedTarget)` in that method. The matching public header explicitly describes setting this flag false when the game controls its camera manually. Wonder Chess's board presenter and front-end scene already choose their own cameras explicitly. This establishes a real camera-override path; the retained older recovery audit did not record its actual view target, so the previous screenshots alone cannot prove the exact call that replaced it.

The controller constructor now sets `bAutoManageActiveCameraTarget=false`. No other controller behavior was changed in this checkpoint. The Scene file, introduction transition, fades and explicit camera restoration are untouched; there is no per-frame camera override that could interrupt Introduction.

## Actual-readiness audit changes

`WCFrontEndAudit.cpp` retains the seven original recovery checks and adds three scene-restoration checks: after failed connection, successful retry, and return to title. Each capture now waits before requesting the screenshot. Per-frame samples record actual/expected view-target paths, equality, automatic-camera flag, asset compilation count, shader count/state, streaming resources pending and consecutive ready frames. Editor compilation counter availability is explicit.

Readiness requires the actual view target to be the scene, no pending observed compilation/streaming work, at least twelve consecutive ready frames, and at least 0.5 seconds of readiness. A separate check confirms the imported original approach plus actual hero mesh and animation. The APIs were read from the installed `AssetCompilingManager.h`, `ShaderCompiler.h` and `ContentStreaming.h`. No compilation/streaming completion is forced, no callbacks are fabricated, and no screen warnings are hidden. The existing 100-second overall timeout fails if recovery cannot complete. Capture keeps the four-frame write interval before the next action; Leave LAN is sent once.

`WCFrontEnd.cpp` now displays concise human guidance, including Indonesian for the known unreachable-host, host-start and session-load cases. Raw `NetworkDetail` remains in logs and the audit report rather than being displayed by default.

## Required next evidence

Root should compile these files together with the already frozen compact HUD patch, then rerun the actual idle-host / refused-endpoint / retry scenario into a fresh evidence folder. Inspect all three screenshots and the per-frame camera/readiness samples. Run the existing Introduction/cancel checks because the controller camera-management default changed. Passing the previous seven functional checks alone does not establish the new presentation correction or package readiness.
