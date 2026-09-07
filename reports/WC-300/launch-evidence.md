# WC-300 minimal packaged title checkpoint

Evidence date: 2026-09-06, Singapore time (UTC+08:00).

The integration lane built a Development Windows package, launched it outside Unreal Editor, and directly inspected its native Wonder Chess title window at approximately 13:20. This is the initial title-screen/package checkpoint. It is not evidence of an interactive full game or of complete 1H7B or 2H6B matches.

## Executable and launch

Packaged launcher:

`C:\Users\iputu\Documents\Wonder Chess\builds\WC-300-Minimal\Windows\WonderChess.exe`

Launch in PowerShell:

```powershell
& 'C:\Users\iputu\Documents\Wonder Chess\builds\WC-300-Minimal\Windows\WonderChess.exe' -windowed -ResX=1280 -ResY=720 -NoSplash
```

Keep the complete `Windows` package directory together. The launcher depends on the packaged executable and content beneath it.

## Actual evidence

- `reports/WC-300/build-and-package-no-hotreload.log` records the successful minimal build/cook/package run.
- `reports/WC-300/minimal-launch.log` opened at 13:16:37 and records `/Game/WonderChess/Maps/L_WC_Menu` loading at 13:16:48 with `WCGameMode`.
- The root integration lane directly inspected the running native title window at approximately 13:20. An actual screenshot-tool capture was displayed in the task conversation. No durable image file was retained for that first capture, so this report does not claim a screenshot file exists.
- The launch log records normal game shutdown and closes at 13:20:49.
- Later runtime, UI, art, data import and tournament verification belong to their subsequent builds and reports. They must not be attributed retroactively to this minimal executable.

## Artifact hashes checked after launch

| File relative to the workspace | Bytes | SHA-256 |
|---|---:|---|
| `builds/WC-300-Minimal/Windows/WonderChess.exe` | 164864 | `e3c22795d6f2265fcbd88b66e1c5b33b7b017aac916be1f3dca4d0232020a93a` |
| `builds/WC-300-Minimal/Windows/WonderChess/Binaries/Win64/WonderChess.exe` | 291253248 | `ae81cdd1f88e6fb013b9f7389c2e3384852f9cf88abd20beda26e0073119b589` |

Engine: Unreal 5.7.4, changelist 51494982. Platform: Windows 11 on Lenovo 82RG, Ryzen 7 6800H and RTX 3060 Laptop GPU. The title launch was requested at 1280×720 windowed; no frame-time, full-match, hero-quality or multiplayer acceptance is established by this checkpoint.
