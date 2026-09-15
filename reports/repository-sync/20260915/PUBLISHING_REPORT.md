# Wonder Chess GitHub publication — 15 September 2026

## Scope

The owner requested: "commit every stuff here to the github repo" after consolidating Wonder Chess into one transferable folder.

Destination: the existing public [TUPRAM/wonder-chess](https://github.com/TUPRAM/wonder-chess) repository. Target branches are `main` and `codex/milestones-b0-m7-20260912`, starting from the verified remote/base commit `d80635f615810a93c3161c6bfd6c34c758b08260`. This record is prepared before the payload push; the closing publication record will report the verified remote result.

## Included

The preflight inventory contains **2,215 new/changed payload files**, totaling **1,095,883,867 working-file bytes** before Git compression, plus this publication report and its audit/validation receipts.

- All pending milestone and Storybook r20 C++/Python source, canonical/generated data, Unreal Content, tests and production tools.
- Bellback candidates, source paintings, portraits/icons, reference/approval records, screenshots and existing successful/failed execution evidence.
- Consolidation documentation, relative launchers, the transfer verifier, and the Python dependency fix.
- Relocated support plans, review packages, original Wonder Chess production ZIPs, reviewed Blender MCP sources and original ZIP, MPFB source archive/license, recovered autosave, and migration evidence.
- The historical checkout's distinct pause marker. Other historical tracked files remain available in existing Git history; their duplicate on-disk checkout is retained locally.

The broad `support/` exclusion was narrowed so transferable source and review material is versioned. [inventory.json](inventory.json) records payload paths, sizes and working-file SHA-256 hashes. Git text conversion follows the existing `.gitattributes`; working-file digests are not Git blob IDs.

## Local-only material

The physical transfer folder remains more complete than the Git repository:

- Packaged game/study builds and Unreal Binaries, Intermediate, Saved and DerivedDataCache directories.
- Python environments/caches, disposable compiler products and copied test dependencies.
- Duplicate historical checkout contents, original Git-internal index/configuration/reflog recovery snapshots, machine-specific MCP configuration, Blender preferences and AppData state.
- Previously ignored Auto Chess reference screenshots and generated export sidecars/native build outputs.
- The full `gloves01_cc0.zip`, `shoes01_cc0.zip` and incomplete download in both copies of the documented source quarantine. The selected cleared assets and rights review remain versioned; publication does not resolve the recorded license-header conflict.
- The local transfer manifest, which binds mutable local Git metadata and must be refreshed after publication.

No source archive was deleted, no Git history was rewritten, no repository visibility was changed, and no paid storage or release upload was introduced. GitHub [blocks ordinary Git files larger than 100 MiB](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github). No file in this publication payload reaches that limit.

## Verification

- **PASS:** 230 Python tests on bundled CPython 3.12.14 with Pillow 12.3.0 and jsonschema 4.26.0.
- **PASS:** 400 specification/data checks; 28 generated documents; six legacy and six successor catalogue artifacts.
- **PASS:** preflight scan of 1,356 pending text files and inspection of 2,860 ZIP members; no credential-pattern or sensitive-filename findings. This bounded scan is not a guarantee of detecting all sensitive data.
- **PASS:** file-size inventory; no payload file at or above 100 MiB.
- **PASS:** staged inventory covers the preflight payload. Seven working-file entries already match their existing Git blobs under the current attributes; the initial commit changes 2,217 files including nine publication metadata files.
- **PASS:** whitespace check for the publication's authored source/navigation changes. The unrestricted staged whitespace check reports preexisting raw logs, immutable art evidence, vendor files and earlier blank lines; these are retained without formatting changes to their recorded contents.
- The preceding consolidation verified the preserved Storybook r20 package against 122 source files and 49 package files, 11 launcher paths, all moved payload hashes, and Git integrity. Those results remain scoped to the recorded checks.
- **NOT RUN for publication:** new Unreal build, game launch, tournament campaign, physical-input review, new-PC installation, human study or release acceptance. Product and art gates remain unchanged.

After both branches are verified on GitHub, the local transfer manifest is refreshed separately to include the new commits and refs. The original pre-publication manifest remains preserved locally for provenance.
