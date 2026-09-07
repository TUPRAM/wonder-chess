"""Audit candidate6 actual packaged network exports without launching the engine."""

import collections
import hashlib
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "reports/WC-360/candidate6-network"


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tests/runtime" / (name + ".py"))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


AUDIT = module("audit_network_evidence")
FRAMES = module("summarize_frame_evidence")


def fingerprint(path):
    return {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    paths = [next((BASE / role).glob(f"match-1-seat-{seat}-*-session.json"))
             for seat, role in enumerate(("host", "client"))]
    sessions = [AUDIT.load(path) for path in paths]
    if not all(s["complete"] for s in sessions):
        print(json.dumps({"status": "IN_PROGRESS", "sessions": [{k: s[k] for k in
                          ("utc", "seat", "phase", "round", "complete", "aborted")} for s in sessions]}, indent=2))
        return
    output = BASE / "audit"
    output.mkdir(exist_ok=True)
    pair = AUDIT.audit(*paths, require_complete=True)
    (output / "paired-state-audit.json").write_text(json.dumps(pair, indent=2) + "\n", encoding="utf-8")
    details, inputs = [], []
    for role, session, path in zip(("host", "client"), sessions, paths):
        rows, snapshot_path = AUDIT.received(session, path)
        commands_path = path.with_name(path.name.replace("-session.json", "-commands.jsonl"))
        commands = [json.loads(line) for line in commands_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        replies = [c for c in commands if c.get("event") == "actual_client_reply"]
        log_path = path.parent / "game.log"
        log_lines = log_path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        oversize = [line for line in log_lines if "Attempted to send bunch exceeding max allowed size" in line]
        sizes = [int(re.search(r"BunchSize=(\d+)", line)[1]) for line in oversize]
        final = json.loads(session["public_snapshot"])
        recap_rounds = sorted({r["public"]["recap"]["round"] for r in rows if r["public"].get("recap")})
        stale_recaps = [{"utc": r["utc"], "current_round": r["round"], "phase": r["phase"],
                        "recap_round": r["public"]["recap"]["round"]}
                       for r in rows if r["public"].get("recap") and
                       r["public"]["recap"]["round"] < r["round"] - (1 if r["phase"] in (0, 1) else 0)]
        bounds = session.get("projected_hero_bounds_samples", [])
        bounds_summary = {"sample_count": len(bounds),
                          "boundary": "Conservative projected skeletal component AABBs; does not establish pixel occlusion, feet contact, animation quality or interface usability."}
        for key in ("bounds_outside_safe_ids", "unprojectable_ids", "missing_or_invisible_component_ids"):
            bounds_summary[key] = sorted({item for sample in bounds for item in sample.get(key, [])})
            bounds_summary[key + "_sample_count"] = sum(bool(sample.get(key)) for sample in bounds)
        public_keys = ("public_json_chars_current", "public_json_chars_max", "public_json_utf8_bytes_current",
                       "public_json_utf8_bytes_max", "distinct_public_payload_samples")
        item = {"role": role, **{k: session[k] for k in ("process_id", "seat", "match_namespace", "complete", "aborted", "round", "intent_requests", "actual_accepted_replies", "actual_rejected_replies", "simulation_speed_multiplier", "resolution_x", "resolution_y", "max_living_visible_units", "max_living_logical_units", "max_simultaneous_encounters")},
                "first_observation_utc": rows[0]["utc"], "last_observation_utc": rows[-1]["utc"],
                "first_result_utc": next((r["utc"] for r in rows if r["phase"] == 3), None),
                "snapshot_count": len(rows), "combat_rounds": sorted({r["round"] for r in rows if r["phase"] == 1}),
                "recap_rounds": recap_rounds, "stale_retained_recap_observations": stale_recaps,
                "actual_reply_reasons": dict(collections.Counter(r["reason"] for r in replies)),
                "probe_statuses": {p["name"]: p["status"] for p in session["command_probes"]},
                "public_payload": {k: session.get(k) for k in public_keys},
                "payload_boundary": "Actual received public FString character/UTF8 lengths. These exclude replication headers and are not wire packet sizes. Oversized-bunch log checks inspect the actual engine rejection path separately.",
                "projected_component_bounds": bounds_summary,
                "oversized_replication_bunches": len(oversize), "oversized_bunch_bytes_max": max(sizes) if sizes else None,
                "error_level_log_lines": [line for line in log_lines if ": Error:" in line],
                "final_standings": [{k: seat[k] for k in ("id", "name", "human", "health", "wins", "place")} for seat in final["seats"]]}
        frame = FRAMES.summarize(path)
        (output / f"{role}-frames.json").write_text(json.dumps(frame, indent=2) + "\n", encoding="utf-8")
        item["profiling"] = frame
        details.append(item)
        inputs += [fingerprint(p) for p in (path, snapshot_path, commands_path, log_path)]
    provenance_path = ROOT / "reports/WC-360/candidate6-provenance.json"
    provenance = AUDIT.load(provenance_path)
    packaged_executables = [r for r in provenance["files"] if r["group"] == "packaged_payload" and Path(r["path"]).suffix.lower() == ".exe"]
    identity = [{"path": row["path"], "recorded_sha256": row["sha256"],
                 "current_sha256": hashlib.sha256(Path(row["path"]).read_bytes()).hexdigest()} for row in packaged_executables]
    for row in identity:
        row["matches"] = row["recorded_sha256"] == row["current_sha256"]
    status = pair["status"]
    if any(d["stale_retained_recap_observations"] or d["oversized_replication_bunches"] for d in details) or not all(r["matches"] for r in identity):
        status = "FAIL"
    result = {"status": status, "utc": datetime.now(timezone.utc).isoformat(),
              "boundary": "Two actual packaged processes over local loopback with separate human seat bindings and real scripted RPCs. This is not manual play, a second physical PC, normal-speed profiling, or visual/audio acceptance.",
              "paired_reader_status": pair["status"], "paired_reader_checks": len(pair["checks"]),
              "nonpassing_pair_checks": [c for c in pair["checks"] if c["status"] != "PASS"],
              "sessions": details, "packaged_executable_identity": identity,
              "provenance": fingerprint(provenance_path), "inputs": inputs}
    (output / "network-analysis.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    text = ["Candidate6 actual two-process network acceptance: " + status, "", result["boundary"], "",
            f"Paired evidence reader: {pair['status']} across {len(pair['checks'])} checks. The candidate6 packaged executable hashes match its immutable provenance manifest: {all(r['matches'] for r in identity)}.", ""]
    for item in details:
        text += [f"- {item['role'].title()} PID {item['process_id']}, human seat {item['seat']}: completed round {item['round']}. Combat rounds observed: {item['combat_rounds']}. Recap rounds observed: {item['recap_rounds']}.",
                 f"- {item['role'].title()}: {item['intent_requests']} requests; {item['actual_accepted_replies']} accepted and {item['actual_rejected_replies']} rejected actual replies. Reasons: {item['actual_reply_reasons']}. Probes: {item['probe_statuses']}.",
                 f"- {item['role'].title()}: actual maximum public JSON {item['public_payload']['public_json_chars_max']} characters / {item['public_payload']['public_json_utf8_bytes_max']} UTF8 bytes; {item['oversized_replication_bunches']} oversized-bunch engine errors; {len(item['stale_retained_recap_observations'])} stale recap observations."]
    text += ["", "Payload lengths exclude protocol overhead; the actual engine log check is separate. Accepted replies include the deliberately replayed idempotent request and therefore do not equal distinct accepted mutations. Frame data is a 1280x720 accelerated 5x two-process workload and cannot pass the 1080p normal-speed performance gate.", "",
             "Candidate5 remains preserved as a failure with 60 oversized bunches and missing combat rounds 2-16. This report describes the separately packaged candidate6 run only.", ""]
    (output / "analysis.md").write_text("\n".join(text), encoding="utf-8")
    print(json.dumps({"status": status, "checks": len(pair["checks"]), "sessions": [{"role": d["role"], "round": d["round"], "combat_rounds": d["combat_rounds"], "payload": d["public_payload"], "oversized_bunches": d["oversized_replication_bunches"]} for d in details]}, indent=2))


if __name__ == "__main__":
    main()
