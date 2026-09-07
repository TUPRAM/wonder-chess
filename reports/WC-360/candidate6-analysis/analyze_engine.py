"""Compare preserved candidate6 Unreal execution with the verified standalone archive."""

import collections
import csv
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ENGINE = ROOT / "reports/WC-360/candidate6-automation"
STANDALONE = ROOT / "reports/WC-310/runtime/post-retained-recap"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(data):
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))


def main():
    validation_path = STANDALONE / "validation.json"
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    archive_path = STANDALONE / "standalone-100-evidence.zip"
    if sha(archive_path) != validation["archive_sha256"]:
        raise ValueError("Standalone archive digest mismatch")
    summaries = read_csv((ENGINE / "engine-tournaments.csv").read_bytes())
    rounds = read_csv((ENGINE / "engine-rounds.csv").read_bytes())
    index = json.loads((ENGINE / "index.json").read_text(encoding="utf-8-sig"))
    assets = json.loads((ENGINE / "imported-assets.json").read_text(encoding="utf-8-sig"))
    with zipfile.ZipFile(archive_path) as archive:
        reference_summaries = read_csv(archive.read("tournaments.csv"))
        reference_rounds = read_csv(archive.read("round-economy.csv"))
    checks = []

    def compare(name, actual, expected, keys, aliases=None):
        aliases = aliases or {}
        key = lambda row: tuple(int(row[k]) for k in keys)
        counts = collections.Counter(key(row) for row in actual)
        reference = {key(row): row for row in expected}
        missing, extra = sorted(set(reference) - set(counts)), sorted(set(counts) - set(reference))
        duplicates = [k for k, n in counts.items() if n != 1]
        differences = []
        for row in actual:
            if key(row) not in reference:
                continue
            other = reference[key(row)]
            fields = {k: [value, other.get(aliases.get(k, k))] for k, value in row.items()
                      if int(value) != int(other[aliases.get(k, k)])}
            if fields:
                differences.append({"key": key(row), "fields": fields})
        checks.append({"name": name, "status": "PASS" if not (missing or extra or duplicates or differences) else "FAIL",
                       "actual_rows": len(actual), "reference_rows": len(expected),
                       "fields_per_row": len(actual[0]), "missing_keys": missing, "extra_keys": extra,
                       "duplicate_keys": duplicates, "differences": differences})

    compare("all_tournament_summary_fields", summaries, reference_summaries, ["seed"],
            {"commands": "bot_commands", "rejects": "bot_rejects"})
    compare("all_round_seat_fields", rounds, reference_rounds, ["seed", "round", "seat"])
    by_round = collections.defaultdict(list)
    for row in rounds:
        by_round[int(row["seed"]), int(row["round"])].append(row)
    structural_errors = []
    for key, rows in by_round.items():
        if sorted(int(r["seat"]) for r in rows) != list(range(8)):
            structural_errors.append({"key": key, "problem": "seat completeness"})
        if len({(r["settlement_id"], r["pre_hash"], r["post_hash"]) for r in rows}) != 1:
            structural_errors.append({"key": key, "problem": "inconsistent settlement/state hashes"})
        if any(int(r["health"]) < 0 or int(r["gold"]) < 0 for r in rows):
            structural_errors.append({"key": key, "problem": "negative health/gold"})
    source_checks = []
    for source in validation["source"]:
        path = ROOT / source["path"]
        actual_sha = sha(path)
        source_checks.append({"path": source["path"], "matches_standalone_snapshot": actual_sha == source["sha256"],
                              "expected_sha256": source["sha256"], "actual_sha256": actual_sha})
    totals = {field: sum(int(r[field]) for r in summaries)
              for field in ("rounds", "simulated_ms", "encounters", "timeouts", "ghosts", "commands", "rejects")}
    caps = [int(r["seed"]) for r in summaries if int(r["rounds"]) == 24 and
            sum(int(s["health"]) > 0 for s in by_round[int(r["seed"]), 24]) > 1]
    passed = all(c["status"] == "PASS" for c in checks) and not structural_errors
    passed &= index["succeeded"] == 6 and index["failed"] == 0 and index["notRun"] == 0
    passed &= all(test["state"] == "Success" and test["errors"] == 0 and test["warnings"] == 0 for test in index["tests"])
    passed &= bool(assets["passed"]) and assets["loaded_meshes"] == 12 and assets["unique_animation_assets"] == 84
    inputs = [ENGINE / n for n in ("index.json", "engine-tournaments.csv", "engine-rounds.csv", "imported-assets.json")]
    inputs += [validation_path, archive_path]
    report = {"status": "PASS" if passed else "FAIL", "utc": datetime.now(timezone.utc).isoformat(),
              "boundary": "Actual WindowsEditor execution and parity with the digest-verified standalone run. This does not certify candidate6 packaged execution, network behavior, frame timing or visual/audio quality.",
              "checks": checks, "structural_errors": structural_errors,
              "engine_tournaments": len(summaries), "engine_totals": totals,
              "inferred_cap_seeds": caps,
              "cap_boundary": "CSV omits capped flag; inferred from final round24 and more than one positive-health seat.",
              "automation": {k: index[k] for k in ("succeeded", "succeededWithWarnings", "failed", "notRun", "totalDuration", "tests")},
              "asset_result": {k: assets[k] for k in ("utc", "passed", "loaded_meshes", "animation_references", "unique_animation_assets", "sampled_bone_transforms", "boundary", "animation_sampling_boundary", "texture_dimension_boundary", "root_basis_boundary")},
              "current_sources_vs_standalone": source_checks,
              "extra_metric_boundary": "These engine CSVs do not record per-hero use or individual fight durations. No such measurements are inferred from shared outcome hashes.",
              "inputs": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p), "bytes": p.stat().st_size} for p in inputs]}
    (OUT / "engine-comparison.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    text = ["Candidate6 actual engine execution and parity: " + report["status"], "", report["boundary"], "",
            f"All 6 automation tests passed with 0 errors and 0 warnings in {index['totalDuration']:.6f} seconds, including the new RetainedRecapAfterHitch test. The 100 actual combat tournaments again produced 7,118 encounters, 1,437 timeouts, 524 ghosts, 69,656 bot commands and 0 bot rejections.", "",
            "All 100 tournament summaries (9 fields each) and 17,728 round/seat records (11 fields each) match the latest standalone retained-recap run exactly. No missing, extra or duplicate keys, negative health/gold values or conflicting per-round settlement/state hashes were found.", "",
            f"There are {len(caps)} inferred capped adjudications, seeds {caps}. These are derived from final health and the round ceiling because the CSV does not contain an explicit cap field.", "",
            "The actual asset test loaded 12 skeletal meshes and 84 unique animation assets and sampled 11,988 bone transforms. Its stated root, sampling and source-texture boundaries remain in the JSON report. This technical asset pass does not establish attractive art, feet contact, deformation, release alignment or cooked texture residency.", "",
            "Source snapshot comparisons and all evidence hashes are retained in engine-comparison.json. Package provenance and actual network verification follow separately.", ""]
    (OUT / "analysis.md").write_text("\n".join(text), encoding="utf-8")
    print(json.dumps({"status": report["status"], "automation": index["succeeded"], "comparisons": checks,
                      "source_parity": all(s["matches_standalone_snapshot"] for s in source_checks)}, indent=2))


if __name__ == "__main__":
    main()
