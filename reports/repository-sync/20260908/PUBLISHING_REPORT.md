# Wonder Chess GitHub publication — 2026-09-08

Destination: https://github.com/TUPRAM/wonder-chess (public), branch `main`.

All 15 initial publication batches were accepted and their remote commit IDs verified. Original history was retained; no force push, history rewrite, branch replacement, release upload or permission change was used.

- Original checkpoint: `c6276928b902bddbf22e9c691ae3c6aa202892d4` (13 existing commits).
- Complete source/evidence upload tip, before this publication report: `4dd4f5ebbb6a56be36b492c4c017e2ff5b0164a0`.
- Initial upload: 20,691 tracked files; reviewed working-file payload 7,677,709,495 bytes. This is not the compressed Git transfer size.
- This closing commit adds the portable MCP example and publication evidence, clarifies fresh-clone setup, and allows the MCP verifier to default its working directory to the repository.
- `pushed.jsonl` records all 15 verified batch commits and times.

## Included

Unreal C++ source/configuration, imported Content assets, Blender source/revision assets, exports, canonical data, generated documents/catalog, tests, tools, task specifications, research, and retained screenshots/videos/animation frames/match logs/measurement records. The game remains subject to the open acceptance gates in `reports/UPDATE24_CHECKPOINT_HANDOFF.md`; repository publication does not certify completed art, physical LAN acceptance or full playability.

## Kept local

Existing ignore rules retain packaged builds, Unreal caches/intermediates/binaries, Python environments, environment files and automatic Blender backups. New rules exclude `.codex/config.toml` and disposable native test compiler objects/executables under reports. Tiny executable-shaped negative-test fixtures remain versioned. No ignored files were force-added or deleted. The separately installed Blender MCP environment remains under Project Support; `.codex/config.example.toml` documents local configuration without publishing active machine settings.

## Checks executed

- PASS: 400 specification/data checks (`validate-kit.log`).
- PASS: 147 Python tests (`unittest.log`).
- PASS: 28 generated documents match canonical data (`documents.log`).
- PASS: 6 generated catalog artifacts match canonical data (`catalog.log`).
- PASS: credential-pattern scan of candidate text and all reachable initial-history blobs; 5,112 text inputs, 2,164 historical blobs, no pattern findings (`audit.json`). This is a bounded scan, not a guarantee that all sensitive content can be detected.
- PASS: no candidate or initial-history blob exceeded 100 MiB.
- PASS: MCP example TOML parse, verifier syntax/default-working-directory check, and focused diff whitespace check.
- ACCEPTED WARNING: GitHub warned about a 53.48 MiB historical snapshot JSONL file; its batch push succeeded.
- NOT RUN for this publication task: new Unreal builds, game matches, physical LAN verification or new art acceptance. Existing recorded evidence is retained as-is.

GitHub file and push limits were checked against its official documentation:
https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github
https://docs.github.com/en/get-started/using-git/troubleshooting-the-2-gb-push-limit
