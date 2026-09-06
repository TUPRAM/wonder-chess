"""Summarize actual WCVerification frame CSVs, preserving missing-load boundaries."""

import argparse
import csv
import hashlib
import json
from pathlib import Path


def metrics(values):
    values = sorted(values)
    if not values:
        return {"status": "NOT_RUN", "samples": 0}
    return {"status": "OBSERVED", "samples": len(values),
            **{f"p{p}_ms": values[int((len(values) - 1) * p / 100)] for p in (50, 95, 99)},
            "max_ms": values[-1], "frames_over_33_33ms": sum(x > 100 / 3 for x in values),
            "frames_over_100ms": sum(x > 100 for x in values)}


def summarize(session_path):
    session = json.loads(session_path.read_text(encoding="utf-8-sig"))
    prefix = f"match-{session['match_namespace']}-seat-{session['seat']}-pid-{session['process_id']}"
    frame_path = session_path.parent / (prefix + "-frames.csv")
    with frame_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = [{key: float(value) for key, value in row.items()} for row in csv.DictReader(stream)]
    subsets = {"all_profiled_frames": rows,
               "active_tournament_frames": [r for r in rows if r["phase"] in (0, 1, 2)],
               "combat_frames": [r for r in rows if r["phase"] == 1],
               "twelve_visible_combatants": [r for r in rows if r["phase"] == 1 and r["visible_alive"] >= 12],
               "twelve_visible_and_four_live_encounters": [r for r in rows if r["phase"] == 1
                                                            and r["visible_alive"] >= 12 and r["encounters"] == 4]}
    result = {"boundary": "Observed instrumented viewport timings; GPU zero samples omitted as unavailable. No inferred hardware or FPS.",
              "hardware_and_settings": {k: session.get(k) for k in
                                        ("cpu", "active_rhi_adapter", "primary_gpu_reported_by_os", "engine", "rhi",
                                         "render_settings", "resolution_x", "resolution_y", "simulation_speed_multiplier",
                                         "peak_process_physical_bytes", "gpu_timing_source")},
              "subsets": {}, "inputs": []}
    for name, selected in subsets.items():
        result["subsets"][name] = {"frames": len(selected),
                                  **{field: metrics([r[field] for r in selected if field != "gpu_ms" or r["gpu_available"]])
                                     for field in ("frame_ms", "game_ms", "render_ms", "gpu_ms")}}
    for path in [session_path, frame_path]:
        result["inputs"].append({"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    result["required_busy_load_status"] = "OBSERVED" if subsets["twelve_visible_and_four_live_encounters"] else "NOT_RUN"
    result["viewport_1080p_observed"] = session.get("resolution_x") == 1920 and session.get("resolution_y") == 1080
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = summarize(args.session)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"required_busy_load_status": report["required_busy_load_status"],
                      "viewport_1080p_observed": report["viewport_1080p_observed"], "output": str(args.output)}, indent=2))
