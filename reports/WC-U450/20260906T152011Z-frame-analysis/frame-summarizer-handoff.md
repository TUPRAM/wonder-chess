# Frame evidence summarizer handoff

`tests/runtime/summarize_frame_evidence.py` is frozen. It remains callable as `summarize(session_path)` by existing auditors; an optional second sequence of context JSON paths adds hashed workload context. CLI adds repeated `--context-evidence`. CLI output uses exclusive creation, preserving prior reports.

Actual CSV columns drive all classifications. Optional frontend_page supports lobby, mode, gallery, detail, settings and closed. Namespace0/phase-1 rows are grouped as combined frontend; separate lobby, gallery list, detail, gallery+detail, mode/entry and settings groups require their actual page value. Missing columns or unknown values are never inferred from screenshots, names, or elapsed time.

Neutral and PvP groups require the recorded neutral_round flag. Exactly eight unfinished neutral fights requires phase1, neutral_round1, neutral_live_encounters8 and total unfinished encounters8. Round multiples or eight participant names do not satisfy that load. All timing groups retain p50/p95/p99, maximum, strict >33.333ms and >100ms counts, valid sample count and excluded sample count. Percentiles preserve the previous floor((n-1)*p/100) convention. Unavailable/zero/null/nonfinite GPU timing and all NullRHI GPU timing remain NOT_RUN/null, never measured zero cost.

Executed validation: nine focused tests passed in focused-fixtures.log; Python syntax and whitespace checks passed. Fixtures cover percentile/hitch math, exact live-neutral counters, namespace and actual pages, older schemas, missing/header-only evidence, GPU availability, NullRHI, bound capture/context provenance and truncated CSV rejection. They are file fixtures, not game evidence.

Read-only actual application: integrated-gallery-preliminary.json binds reports/WC-U430/20260906T150922Z/packaged-gallery1080/session.json and its exact CSV and launch. That CSV has only its181-byte header; the launch has no -WCProfile. Result NOT_RUN, zero timing rows, every percentile null. The session reports AMD Ryzen7 6800H, NVIDIA RTX3060 Laptop GPU, UE5.7.4, D3D11 and1920x1080 settings; these settings do not manufacture observed timing samples. Its launch explicitly records overlapping Blender and regression; the corresponding regression launch is bound as additional context. No final performance or unobstructed workload acceptance is claimed.

After the root agent captures actual profiled rows with the new frontend_page column:

```powershell
python tests/runtime/summarize_frame_evidence.py '<fresh evidence>/session.json' --output '<fresh report>/frame-summary.json' --context-evidence '<actual concurrent-workload launch.json>'
```

A dedicated final performance run must be measured independently from the capture-heavy development audit. This task changed only the summarizer, its focused fixture test and fresh reports; no Unreal source, game asset or binary was modified and no game was launched.
