"""Summarize actual AQ1 WCProfile CSVs; optionally compare matched round/phase strata.

Read-only inputs. No editor, renderer, subprocess, or synthetic timing generation.
"""

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path


COLUMNS = (
    "wall_seconds,phase,round,visible_alive,logical_alive,encounters,frame_ms,"
    "game_ms,render_ms,gpu_ms,gpu_available,public_chars,public_utf8_bytes,"
    "neutral_round,neutral_live_encounters,frontend_page,frame_counter"
).split(",")
CHANNELS = ("frame_ms", "game_ms", "render_ms", "gpu_ms")
INT_COLUMNS = set(COLUMNS) - set(CHANNELS) - {"wall_seconds", "frontend_page"}
SUBSETS = {
    "all": lambda r: True,
    "preparation": lambda r: r["phase"] == 0,
    "combat": lambda r: r["phase"] == 1,
    "settlement": lambda r: r["phase"] == 2,
    "pvp_combat": lambda r: r["phase"] == 1 and not r["neutral_round"],
    "neutral_combat": lambda r: r["phase"] == 1 and bool(r["neutral_round"]),
    "eight_live_neutral_fights": lambda r: r["phase"] == 1 and r["neutral_live_encounters"] == 8,
    "twelve_visible_combat": lambda r: r["phase"] == 1 and r["visible_alive"] >= 12,
    "four_live_pvp_fights": lambda r: r["phase"] == 1 and not r["neutral_round"] and r["encounters"] == 4,
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metrics(values):
    values = sorted(values)
    if not values:
        return {"samples": 0, "available": False}
    result = {"samples": len(values), "available": True, "mean_ms": statistics.fmean(values),
              "min_ms": values[0], "max_ms": values[-1]}
    for label, fraction in (("p50", .5), ("p90", .9), ("p95", .95), ("p99", .99), ("p999", .999)):
        result[label + "_ms"] = values[int((len(values) - 1) * fraction)]
    result["strict_exceedance_counts"] = {
        "20_ms": sum(v > 20 for v in values),
        "33_333_ms": sum(v > 1000 / 30 for v in values),
        "50_ms": sum(v > 50 for v in values),
        "100_ms": sum(v > 100 for v in values),
    }
    bounds = (16.7, 20, 1000 / 30, 50, 100, math.inf)
    result["histogram_counts"] = {
        label: sum(low < v <= high for v in values)
        for low, high, label in zip((-math.inf,) + bounds[:-1], bounds,
                                   ("le_16_7", "16_7_to_20", "20_to_33_333", "33_333_to_50", "50_to_100", "gt_100"))
    }
    return result


def summarize(rows):
    return {
        "rows": len(rows),
        "summed_frame_delta_seconds": sum(r["frame_ms"] for r in rows) / 1000,
        "rounds": sorted({r["round"] for r in rows}),
        "visible_alive_histogram": dict(sorted(Counter(r["visible_alive"] for r in rows).items())),
        "logical_alive_range": [min((r["logical_alive"] for r in rows), default=None),
                                max((r["logical_alive"] for r in rows), default=None)],
        "channels": {c: metrics([r[c] for r in rows if c != "gpu_ms" or r["gpu_available"]]) for c in CHANNELS},
    }


def load_run(directory):
    directory = directory.resolve()
    session_path = directory / "session.json"
    session = json.loads(session_path.read_text(encoding="utf-8-sig"))
    launch = json.loads((directory / "launch.json").read_text(encoding="utf-8-sig"))
    path = directory / f"match-{session['match_namespace']}-seat-{session['seat']}-pid-{session['process_id']}-frames.csv"
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != COLUMNS:
            raise ValueError(f"Unexpected timing schema in {path}: {reader.fieldnames}")
        rows = []
        for line, raw in enumerate(reader, 2):
            row = {k: (v if k == "frontend_page" else int(v) if k in INT_COLUMNS else float(v))
                   for k, v in raw.items()}
            if any(not math.isfinite(row[k]) or row[k] < 0 for k in CHANNELS + ("wall_seconds",)):
                raise ValueError(f"Invalid time at {path}:{line}")
            if row["frame_ms"] <= 0 or row["gpu_available"] not in (0, 1):
                raise ValueError(f"Invalid timing availability at {path}:{line}")
            if rows and (row["frame_counter"] <= rows[-1]["frame_counter"] or row["wall_seconds"] < rows[-1]["wall_seconds"]):
                raise ValueError(f"Non-monotonic sample at {path}:{line}")
            rows.append(row)
    if not rows:
        raise ValueError(f"No frame samples: {path}")
    if launch.get("exit_code") != 0 or session.get("simulation_speed_multiplier") != 1:
        raise ValueError("Comparison requires exited normal-speed runs; keep failed/accelerated evidence separately")
    if "-WCProfile" not in launch["arguments"] or "-WCShots" in launch["arguments"]:
        raise ValueError("Expected profiling without screenshot capture")
    log = (directory / "game.log").read_text(encoding="utf-8-sig", errors="replace")
    hardware_patterns = {"driver_version": r"Driver Version: ([^\r\n]+)", "driver_date": r"Driver Date: ([^\r\n]+)",
                         "ram": r"Memory total: Physical=([^\r\n]+)", "startup_physical_memory": r"Physical Memory: ([^\r\n]+)"}
    hardware = {k: (match.group(1).strip() if (match := re.search(pattern, log)) else None)
                for k, pattern in hardware_patterns.items()}
    hardware.update({k: session.get(k) for k in ("cpu", "active_rhi_adapter", "primary_gpu_reported_by_os", "rhi", "engine")})
    stage_keys = sorted({(r["round"], r["phase"]) for r in rows})
    payload = {
        "source_directory": str(directory), "csv": str(path), "csv_sha256": digest(path),
        "session_sha256": digest(session_path), "game_log_sha256": digest(directory / "game.log"),
        "launch": launch, "hardware": hardware, "render_settings": session["render_settings"],
        "resolution": [session["resolution_x"], session["resolution_y"]],
        "seed": session["match_seed_authority"], "simulation_speed_multiplier": session["simulation_speed_multiplier"],
        "final_round": session["round"], "final_phase": session["phase"], "terminal_complete": session["complete"],
        "process_exit_requested": session["process_exit_requested"], "peak_process_physical_bytes": session["peak_process_physical_bytes"],
        "recorded_match_wall_range_seconds": [rows[0]["wall_seconds"], rows[-1]["wall_seconds"]],
        "recorded_wall_span_seconds": rows[-1]["wall_seconds"] - rows[0]["wall_seconds"],
        "unrecorded_frame_counter_gaps": sum(max(0, b["frame_counter"] - a["frame_counter"] - 1) for a, b in zip(rows, rows[1:])),
        "frontend_pages": sorted({r["frontend_page"] for r in rows}),
        "subsets": {key: summarize([r for r in rows if select(r)]) for key, select in SUBSETS.items()},
        "round_phase_strata": {f"r{q:02}_p{p}": summarize([r for r in rows if (r["round"], r["phase"]) == (q, p)]) for q, p in stage_keys},
        "largest_frame_deltas": sorted(rows, key=lambda r: r["frame_ms"], reverse=True)[:10],
        "session_metric_parity": {},
    }
    for c, key in zip(CHANNELS, ("frame_interval", "game_thread_active", "render_thread_active", "gpu")):
        actual = payload["subsets"]["all"]["channels"][c]
        reported = session[key]
        payload["session_metric_parity"][c] = actual["samples"] == reported["samples"] and all(
            abs(actual[k] - reported[k]) < 0.000002 for k in ("p50_ms", "p95_ms", "p99_ms", "max_ms"))
    return payload


def compare(baseline, candidate):
    keys = ("resolution", "render_settings", "seed", "simulation_speed_multiplier")
    mismatches = [k for k in keys if baseline[k] != candidate[k]]
    for k in ("cpu", "active_rhi_adapter", "rhi", "engine", "driver_version"):
        if baseline["hardware"][k] != candidate["hardware"][k]:
            mismatches.append("hardware." + k)
    ignore = ("-WCEvidenceDir=", "-abslog=", "-WCAQ1HeroRoot=")
    normalized = lambda r: [x for x in r["launch"]["arguments"] if not x.startswith(ignore)]
    if normalized(baseline) != normalized(candidate):
        mismatches.append("normalized_launch_arguments")
    result = {"settings_match": not mismatches, "mismatches": mismatches,
              "interpretation": "Descriptive single-run differences only; frame cap, scene mix, instrumentation, caching and thermal conditions prevent an isolated causal art-cost estimate.",
              "subsets": {}, "matched_round_phase_strata": {}}
    for key, target in (("subsets", "subsets"), ("round_phase_strata", "matched_round_phase_strata")):
        for name in baseline[key].keys() & candidate[key].keys():
            a, b = baseline[key][name], candidate[key][name]
            differences = {}
            for channel in CHANNELS:
                am, bm = a["channels"][channel], b["channels"][channel]
                if am["available"] and bm["available"]:
                    differences[channel] = {stat: bm[stat] - am[stat] for stat in ("mean_ms", "p50_ms", "p95_ms", "p99_ms", "max_ms")}
            result[target][name] = {"baseline_rows": a["rows"], "candidate_rows": b["rows"],
                                    "baseline_rounds": a["rounds"], "candidate_rounds": b["rounds"],
                                    "delta_candidate_minus_baseline_ms": differences}
    return result


def write_markdown(report, path):
    lines = ["# AQ1 measured performance review", "", "Actual completed normal-speed profiling inputs; no generated timings or performance pass inferred.", ""]
    for key in ("baseline", "candidate"):
        if key not in report:
            continue
        run = report[key]
        lines += [f"## {key.capitalize()}", "", f"Source: `{run['source_directory']}`.", "",
                  f"{run['hardware']['cpu'].strip()} / {run['hardware']['active_rhi_adapter']} / {run['hardware']['rhi']} / driver {run['hardware']['driver_version']}. RAM record: {run['hardware']['ram']}.", "",
                  f"Resolution {run['resolution']}, frame cap {run['render_settings']['t.MaxFPS']}, VSync {run['render_settings']['r.VSync']}, seed {run['seed']}. Final round {run['final_round']}, phase {run['final_phase']}, terminal complete={run['terminal_complete']}.", "",
                  f"Recorded match-relative wall span {run['recorded_match_wall_range_seconds']} seconds. The process exit request and five-second per-namespace warmup are separate clocks; do not call this 360 seconds of sampled combat.", "",
                  "| Subset | Samples | Summed frame seconds | Channel | p50 ms | p95 ms | p99 ms | Maximum ms | >33.333 ms samples |", "|---|---:|---:|---|---:|---:|---:|---:|---:|"]
        for subset in ("all", "combat", "twelve_visible_combat", "eight_live_neutral_fights"):
            group = run["subsets"][subset]
            for channel in CHANNELS:
                v = group["channels"][channel]
                if not v["available"]:
                    continue
                lines.append(f"| {subset} | {v['samples']} | {group['summed_frame_delta_seconds']:.3f} | {channel} | {v['p50_ms']:.3f} | {v['p95_ms']:.3f} | {v['p99_ms']:.3f} | {v['max_ms']:.3f} | {v['strict_exceedance_counts']['33_333_ms']} |")
        lines += ["", "Per-round/phase distributions, channel histograms, thresholds, worst frames and source hashes are in the JSON companion.", ""]
    lines += ["## Interpretation boundaries", ""] + ["- " + text for text in report["boundaries"]]
    if "comparison" in report:
        comp = report["comparison"]
        lines += ["", "## Candidate comparison", "", f"Matched settings: {comp['settings_match']}. Mismatches: {comp['mismatches']}.", "",
                  "The JSON gives candidate-minus-baseline differences for common round/phase strata and each workload subset. Different sample counts and scene mixes are retained; no arbitrary regression threshold or numeric approval is applied."]
    else:
        lines += ["", "Candidate comparison: **NOT RUN**; this report currently contains the baseline only."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    report = {"baseline": load_run(args.baseline), "percentile_method": "Sorted sample at floor((n-1)*p), matching WCVerification.cpp; GPU unavailable rows excluded.",
              "boundaries": [
                  "frame_ms is the world tick Delta*1000 under the engine frame cap, not an uncapped benchmark or presentation-time trace.",
                  "game_ms/render_ms use engine active-thread counters; gpu_ms uses RHIGetGPUFrameCycles. These asynchronously reported channels are not additive or guaranteed to describe the same frame.",
                  "All rows after the built-in five-second namespace warmup are retained, including transitions and hitches; no failed/slow sample is silently removed.",
                  "Eight-neutral subset requires combat and exactly eight unfinished neutral encounters; it is eight simulations, not eight rendered boards. Twelve-visible subset requires combat and visible_alive>=12.",
                  "One capped run per revision is descriptive. Same seed/flags alone do not prove identical scene mix, exact wall timing, cache state, thermal or background conditions.",
                  "Uncooked Editor target -game with scripted seat input is not packaged/manual human evidence. No terminal tournament result is inferred from process exit0.",
                  "closed frontend_page provides no lobby/gallery profile. Late neutral waves absent from recorded combat are not extrapolated.",
              ]}
    if args.candidate:
        report["candidate"] = load_run(args.candidate)
        report["comparison"] = compare(report["baseline"], report["candidate"])
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "performance.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_markdown(report, args.out / "PERFORMANCE.md")
    print(json.dumps({"status": "DESCRIPTIVE_MEASUREMENT_NOT_ACCEPTANCE", "baseline_rows": report["baseline"]["subsets"]["all"]["rows"],
                      "candidate_rows": report.get("candidate", {}).get("subsets", {}).get("all", {}).get("rows"), "out": str(args.out.resolve())}))


if __name__ == "__main__":
    main()
