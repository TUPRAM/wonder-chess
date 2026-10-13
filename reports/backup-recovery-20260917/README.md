# D: backup recovery — 17 September 2026

**Recovered all nine previously missing source/tool files.** The active development folder remains `C:/Users/USER/Documents/Wonder Chess`; `D:/Wonder Chess` was read only and remains the backup.

## Recovery

- The D: transfer manifest exactly matches the original C: manifest.
- Recovered **275 additional original files**, verifying original byte size and SHA-256 before copying and again afterward.
- Combined with the earlier 424 recoveries, **699 of the original 709 missing files have been recovered**.
- All previously missing tools, tests, migration records and settings are now recovered. One locally generated cache was preserved separately before restoring its original bytes.
- Existing project edits, repaired Blender configuration, the updated Blender launcher, and current reports were preserved.
- This was a targeted recovery of the remaining 285 entries, not a new full hash scan of the entire backup. The earlier complete audit and recovery evidence remain available.

The remaining ten original files are historical ZIP acquisition/recovery packages in `support/archives/downloads/`: nine are absent from the backup; `blender-mcp-main (1).zip` has the expected length but a different SHA-256 and raises `BadZipFile: File is not a zip file`. It was not substituted for the original. The installed Blender bridge uses the separately preserved source and previously passed connection checks.

[Per-file results](recovery-files.json) · [Recovery summary](recovery-summary.json) · [Nonmatching ZIP evidence](nonmatching-archive.json)

## Validation

- All four authoring commands pass: **400 specification/data checks**, 28 generated documents, six legacy catalogue artifacts, and six successor artifacts.
- Full Python discovery now runs **230 tests: 229 pass, one fails, zero import errors**. The sole failure is the existing launcher fixture invoking Windows PowerShell with `Restricted` script execution policy. No policy was changed or bypassed. [Test log](python-tests.log).
- The restored Storybook launcher passes `-Storybook -ValidateOnly` and resolves the preserved r20 executable. This is a path check, not a game launch.
- Visual Studio Build Tools **2022 17.14.37710.0** is now installed. An isolated C++20 program compiled, linked against **Windows SDK 10.0.22621.0**, and executed successfully with compiler identity **194435229** (19.44.35229). The installation's toolchain family directory is `14.44.35207`; the executed compiler identity is recorded independently. [Compiler evidence](compiler-smoke/result.json).
- Unreal **5.7** is still absent from the checked Epic install location; only **5.8.2** is present. The actual game was not opened, converted or built. The earlier isolated Blender/Unreal connection checks remain separately scoped.

## Remaining setup

Install the matching Unreal **5.7.4** through Epic Games Launcher before the original-version project build. The one Windows PowerShell launcher test still needs an approved policy/setup resolution; the full suite is not marked passed. Recover the ten historical ZIPs from another source if complete archival identity is required.

No new art, gameplay, performance or release acceptance is implied.
