"""Post-exit evidence summary; does not control the game or inspect images/audio."""

import argparse
import csv
import hashlib
import heapq
import json
import math
from array import array
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


PHASES = {-1: "entry_or_frontend", 0: "preparation", 1: "combat", 2: "settlement", 3: "finished", 4: "aborted"}
METRICS = ("frame_ms", "game_ms", "render_ms", "gpu_ms")
SOURCE_BOUNDARIES = [
    "All recorded CSV samples are retained, including spikes. The engine writer omits the first 5 seconds of each namespace and stops profiling after completion/abort; this analysis cannot recover unrecorded frames.",
    "Normal speed means the recorded simulation_speed_multiplier is 1. Elapsed duration is wall time, including Solo Options pauses. No explicit bOptions/paused signal exists in the inspected CSV, snapshot, or session formats; paused combat frames cannot be separated reliably.",
    "frontend_page describes the frontend page, not the in-game Solo Options overlay. Repeated state snapshots are not treated as proof of a pause.",
    "Visible combat means phase=1 and visible_alive>0; the twelve-unit subset means phase=1 and visible_alive>=12. Both can include unidentified paused frames.",
    "GPU zero/unavailable samples are counted as unavailable, not as zero-cost GPU frames. Other finite nonnegative timing samples are retained.",
    "Percentiles use sorted_values[floor((n-1)*p)], matching WCVerification.cpp. Frame interval, game-thread active time, render-thread active time and RHI GPU timing are distinct metrics.",
    "State evidence of completion, elimination and namespace restart does not prove continuous visual quality, results-screen interaction, audio quality, all animation clips, network hosting, or release acceptance.",
    "Manual command acknowledgments do not necessarily include request payload/type. Missing intent-request records are not inferred from reply IDs or state changes.",
]


def number(value, default=None):
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def integer(value, default=-1):
    n = number(value)
    return int(n) if n is not None else default


def utc(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError):
        return None


def public_object(value):
    if isinstance(value, dict):
        return value
    try:
        result = json.loads(value or "{}")
        return result if isinstance(result, dict) else {}
    except (TypeError, ValueError):
        return {}


def selected(mapping, keys):
    return {key: mapping[key] for key in keys if key in mapping}


class Reader:
    def __init__(self):
        self.files = []
        self.errors = []
        self.diagnostics = []

    def lines(self, path):
        before = path.stat()
        digest = hashlib.sha256()
        count = 0
        with path.open("rb") as stream:
            for count, raw in enumerate(stream, 1):
                digest.update(raw)
                try:
                    yield raw.decode("utf-8-sig" if count == 1 else "utf-8")
                except UnicodeDecodeError as exc:
                    self.errors.append({"file": str(path), "line": count, "error": str(exc)})
        after = path.stat()
        self.files.append({
            "path": str(path.resolve()), "bytes": after.st_size, "lines": count,
            "sha256": digest.hexdigest(),
            "stable_during_read": before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns,
            "modified_utc": datetime.fromtimestamp(after.st_mtime, timezone.utc).isoformat(),
        })

    def json_file(self, path):
        try:
            return json.loads("".join(self.lines(path)))
        except (ValueError, OSError) as exc:
            self.errors.append({"file": str(path), "error": str(exc)})
            return {}

    def jsonl(self, path):
        for line_number, line in enumerate(self.lines(path), 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                if not isinstance(item, dict):
                    raise ValueError("JSONL record is not an object")
                yield item
            except ValueError as exc:
                self.errors.append({"file": str(path), "line": line_number, "error": str(exc)})


class Timing:
    def __init__(self):
        self.rows = 0
        self.values = {key: array("d") for key in METRICS}
        self.gpu_unavailable = 0
        self.invalid = Counter()

    def add(self, row):
        self.rows += 1
        for key in METRICS:
            value = number(row.get(key))
            if key == "gpu_ms" and (integer(row.get("gpu_available"), 0) != 1 or value is None or value <= 0):
                self.gpu_unavailable += 1
                continue
            if value is None or value < 0:
                self.invalid[key] += 1
            else:
                self.values[key].append(value)

    def finish(self):
        result = {"rows": self.rows, "gpu_unavailable_rows": self.gpu_unavailable, "invalid_metric_rows": dict(self.invalid)}
        for key, values in self.values.items():
            ordered = sorted(values)
            n = len(ordered)
            stats = {"samples": n, "available": bool(n)}
            if n:
                stats.update({
                    "mean_ms": sum(ordered) / n,
                    "p50_ms": ordered[int((n - 1) * .50)],
                    "p95_ms": ordered[int((n - 1) * .95)],
                    "p99_ms": ordered[int((n - 1) * .99)],
                    "max_ms": ordered[-1], "min_ms": ordered[0],
                    "sum_sample_seconds": sum(ordered) / 1000,
                    "over_33_333_ms": sum(x > 1000 / 30 for x in ordered),
                    "over_50_ms": sum(x > 50 for x in ordered),
                    "over_100_ms": sum(x > 100 for x in ordered),
                })
            result[key] = stats
        return result


def analyze_frames(path, reader, spike_writer, pid, namespace):
    groups = defaultdict(Timing)
    counters = Counter()
    first = last = previous_counter = previous_wall = None
    top = {key: [] for key in METRICS}
    maxima = Counter()
    rows = 0
    spikes = 0
    csv_reader = csv.DictReader(reader.lines(path))
    header_fields = csv_reader.fieldnames or []
    header_occurrence = 1
    for raw in csv_reader:
        line_number = csv_reader.line_num
        if header_fields and len(raw) == len(header_fields) and all(raw.get(field) == field for field in header_fields):
            header_occurrence += 1
            reader.diagnostics.append({
                "file": str(path.resolve()), "line": line_number,
                "kind": "identical_csv_header_repeated", "header_occurrence": header_occurrence,
                "header_fields": header_fields, "process_id": pid, "match_namespace": namespace,
                "handling": "Recognized only because every ordered header field is repeated exactly; structural row is not a timing sample. Other invalid rows remain errors."})
            continue
        wall = number(raw.get("wall_seconds"))
        if wall is None or number(raw.get("frame_ms")) is None:
            reader.errors.append({"file": str(path), "line": line_number, "error": "invalid wall_seconds or frame_ms"})
            continue
        rows += 1
        phase = integer(raw.get("phase"))
        round_number = integer(raw.get("round"))
        visible = integer(raw.get("visible_alive"), 0)
        row = {key: number(raw.get(key)) for key in METRICS}
        row.update(selected(raw, ["gpu_available", "frontend_page"]))
        row.update(wall_seconds=wall, phase=phase, round=round_number, visible_alive=visible,
                   logical_alive=integer(raw.get("logical_alive"), 0), encounters=integer(raw.get("encounters"), 0),
                   neutral_round=integer(raw.get("neutral_round"), 0), frame_counter=integer(raw.get("frame_counter")))
        for name in ["all_recorded", f"phase:{phase}:{PHASES.get(phase, 'unknown')}", f"round:{round_number}:phase:{phase}"]:
            groups[name].add(row)
        if phase == 1:
            groups["combat_neutral" if row["neutral_round"] else "combat_pvp"].add(row)
            if visible > 0:
                groups["visible_combat"].add(row)
            if visible >= 12:
                groups["twelve_unit_visible_combat"].add(row)
        counters[str(raw.get("frontend_page", "unavailable"))] += 1
        for key in ["visible_alive", "logical_alive", "encounters"]:
            maxima[key] = max(maxima[key], row[key])
        if previous_counter is not None:
            delta = row["frame_counter"] - previous_counter
            if delta > 1:
                maxima["missing_frame_counter_values_between_rows"] += delta - 1
            elif delta <= 0:
                maxima["nonincreasing_frame_counters"] += 1
        if previous_wall is not None:
            maxima["largest_wall_gap_seconds"] = max(maxima["largest_wall_gap_seconds"], wall - previous_wall)
            if wall < previous_wall:
                maxima["nonmonotonic_wall_rows"] += 1
        first = wall if first is None else min(first, wall)
        last = wall if last is None else max(last, wall)
        previous_wall, previous_counter = wall, row["frame_counter"]
        valid_values = []
        for key in METRICS:
            value = row[key]
            if value is None or value < 0 or (key == "gpu_ms" and integer(row.get("gpu_available"), 0) != 1):
                continue
            valid_values.append(value)
            item = (value, rows, dict(row))
            if len(top[key]) < 20:
                heapq.heappush(top[key], item)
            elif value > top[key][0][0]:
                heapq.heapreplace(top[key], item)
        if valid_values and max(valid_values) > 1000 / 30:
            spikes += 1
            spike_writer.writerow({"process_id": pid, "match_namespace": namespace, **row})
    return {"rows": rows, "first_wall_seconds": first, "last_wall_seconds": last,
            "recorded_wall_span_seconds": last - first if first is not None else None,
            "groups": {name: value.finish() for name, value in sorted(groups.items())},
            "frontend_page_rows": dict(counters), "coverage_observations": dict(maxima),
            "spike_rows_any_metric_over_33_333ms": spikes,
            "top_20_by_metric": {key: [item[2] for item in sorted(value, reverse=True)] for key, value in top.items()}}


def seat_summary(public):
    return [selected(seat, ["id", "name", "human", "health", "place", "level", "wins", "takeover"])
            for seat in public.get("seats", []) if isinstance(seat, dict)]


def analyze_states(records):
    first = last = finish = None
    transitions, eliminations = [], []
    previous = None
    eliminated = set()
    rounds_after_human = set()
    human_eliminated = False
    encounters = {}
    epochs = []
    seeds, observed_seats, digests = set(), set(), set()
    total = 0
    for record in records:
        public = public_object(record.get("public", record.get("public_snapshot")))
        if not public:
            continue
        total += 1
        phase = integer(record.get("phase", public.get("phase")))
        round_number = integer(record.get("round", public.get("round")))
        wall = number(record.get("elapsed_wall_seconds"))
        summary = {"utc": record.get("utc"), "wall_seconds": wall, "phase": phase,
                   "round": round_number, "seats": seat_summary(public), "capped": public.get("capped"),
                   "requested_humans": public.get("requestedHumans"), "network": public.get("network"),
                   "entry_state": public.get("entryState"), "error": public.get("error")}
        owner = public_object(record.get("owner_private", record.get("own_private_snapshot")))
        summary["owner_private_summary"] = selected(owner, ["seat", "gold", "xp", "level", "revision", "sequence", "locked"])
        if "units" in owner:
            summary["owner_private_summary"]["unit_count"] = len(owner["units"])
        first = first or summary
        last = summary
        if phase == 3 and finish is None:
            finish = summary
        state_key = (phase, round_number, summary["entry_state"])
        if state_key != previous:
            transitions.append({key: summary[key] for key in ["utc", "wall_seconds", "phase", "round", "entry_state"]})
            previous = state_key
        timestamp = utc(record.get("utc"))
        if timestamp and wall is not None:
            epochs.append(timestamp.timestamp() - wall)
        if record.get("match_seed_authority") is not None:
            seeds.add(record["match_seed_authority"])
        if record.get("observed_seat") is not None:
            observed_seats.add(record["observed_seat"])
        if public.get("contentDigest"):
            digests.add(public["contentDigest"])
        for seat in summary["seats"]:
            identity = seat.get("id")
            if number(seat.get("health"), 1) <= 0 and identity not in eliminated:
                eliminated.add(identity)
                eliminations.append({"utc": record.get("utc"), "wall_seconds": wall, "phase": phase,
                                     "round": round_number, "already_eliminated_at_first_sample": total == 1, **seat})
                human_eliminated |= bool(seat.get("human"))
        if human_eliminated:
            rounds_after_human.add((round_number, phase))
        for battle in public.get("encounters", []):
            key = (round_number, battle.get("a"), battle.get("b"), bool(battle.get("ghost")), bool(battle.get("neutral")))
            tick = integer(battle.get("tick"), 0)
            if key not in encounters:
                encounters[key] = {"round": round_number, **selected(battle, ["a", "b", "ghost", "neutral", "waveId"]),
                                   "first_tick": tick, "maximum_tick": tick, "observed_complete": False,
                                   "observed_timeout": False, "samples": 0}
            item = encounters[key]
            item["samples"] += 1
            item["maximum_tick"] = max(item["maximum_tick"], tick)
            item["observed_complete"] |= bool(battle.get("complete"))
            item["observed_timeout"] |= bool(battle.get("timeout"))
            if battle.get("complete"):
                item["last_complete_result"] = selected(battle, ["winner", "survivors", "healthLoss", "captainDamage"])
    rankings = (finish or last or {}).get("seats", [])
    places = [integer(s.get("place"), 0) for s in rankings]
    return {"snapshot_records": total, "first": first, "last": last, "first_finished": finish,
            "namespace_epoch_utc_estimate": datetime.fromtimestamp(min(epochs), timezone.utc).isoformat() if epochs else None,
            "clock_epoch_estimate_spread_seconds": max(epochs) - min(epochs) if epochs else None,
            "initial_round_one_observed": bool(first and first["phase"] == 0 and first["round"] == 1),
            "finished_public_state_observed": finish is not None,
            "eight_unique_placements_observed": len(places) == 8 and sorted(places) == list(range(1, 9)),
            "state_level_full_tournament_observed": bool(first and first["phase"] == 0 and first["round"] == 1 and finish),
            "eliminations": eliminations, "human_elimination_observed": human_eliminated,
            "round_phase_pairs_after_human_elimination": sorted(rounds_after_human),
            "phase_round_transitions": transitions, "authority_seeds_seen": sorted(seeds),
            "observed_seats_seen": sorted(observed_seats), "content_digests_seen": sorted(digests),
            "encounters_observed": list(encounters.values())}


def analyze_commands(records):
    events, reasons = Counter(), Counter()
    replies, intents, notices, duplicates = [], [], [], []
    seen = set()
    for row in records:
        event = row.get("event", "unavailable")
        events[event] += 1
        if event == "actual_client_reply":
            item = selected(row, ["utc", "elapsed_wall_seconds", "phase", "round", "accepted", "reason", "reply_serial", "request_id", "session_notice"])
            identity = (row.get("reply_serial"), row.get("request_id"))
            if identity in seen:
                duplicates.append(item)
            seen.add(identity)
            (notices if row.get("session_notice") else replies).append(item)
            reasons[str(row.get("reason", "unavailable"))] += 1
        elif "intent" in event or "requested" in event:
            intents.append(selected(row, ["utc", "event", "elapsed_wall_seconds", "phase", "round", "type", "unit", "slot", "to_board", "column", "row", "request_id"]))
    return {"events": dict(events), "actual_command_replies": replies, "session_notices": notices,
            "accepted_command_replies": sum(r.get("accepted") is True for r in replies),
            "rejected_command_replies": sum(r.get("accepted") is False for r in replies),
            "duplicate_reply_records": duplicates, "reasons": dict(reasons), "intent_records": intents,
            "payload_coverage": "Intent records are listed where present; manual acknowledgments alone cannot identify payload or validate command-state conservation."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).resolve().parent / "normal-speed")
    parser.add_argument("--pid", type=int, default=36432)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--confirm-process-exited", action="store_true", help="Required acknowledgment: run only after the measured process exits.")
    args = parser.parse_args()
    if not args.confirm_process_exited:
        parser.error("Wait for the measured process to exit, then pass --confirm-process-exited. This flag is an operator declaration, not process-exit detection.")
    files = sorted(args.input.glob(f"match-*-seat-*-pid-{args.pid}-session.json"))
    if not files:
        parser.error("No matching per-namespace session files found; session.json alias is not counted as a separate match.")
    args.output.mkdir(parents=True, exist_ok=True)
    reader = Reader()
    matches = []
    spike_path = args.output / "run_analysis_spikes.csv"
    spike_columns = ["process_id", "match_namespace", "wall_seconds", "phase", "round", "visible_alive", "logical_alive", "encounters", "neutral_round", "frame_counter", "frontend_page", *METRICS, "gpu_available"]
    with spike_path.open("w", newline="", encoding="utf-8") as handle:
        spike_writer = csv.DictWriter(handle, fieldnames=spike_columns)
        spike_writer.writeheader()
        for path in files:
            session = reader.json_file(path)
            if not session:
                continue
            prefix = path.name.removesuffix("-session.json")
            namespace = session.get("match_namespace")
            frame_path = path.with_name(prefix + "-frames.csv")
            snapshot_path = path.with_name(prefix + "-snapshots.jsonl")
            command_path = path.with_name(prefix + "-commands.jsonl")
            match = {"session_file": str(path.resolve()), "match_namespace": namespace, "process_id": session.get("process_id"),
                     "session": selected(session, [key for key, value in session.items() if not isinstance(value, (dict, list)) and key not in {"public_snapshot", "own_private_snapshot"}]),
                     "render_settings": session.get("render_settings", {}),
                     "session_metric_summaries": selected(session, ["frame_interval", "game_thread_active", "render_thread_active", "gpu", "twelve_unit_combat_subset"])}
            if snapshot_path.exists():
                match["states"] = analyze_states(reader.jsonl(snapshot_path))
                match["state_evidence_source"] = "streamed snapshots.jsonl"
            else:
                match["states"] = analyze_states(session.get("phase_round_transitions", []) + [session])
                match["state_evidence_source"] = "fallback session transitions and final state; snapshot file missing"
            if frame_path.exists():
                match["frames"] = analyze_frames(frame_path, reader, spike_writer, args.pid, namespace)
            else:
                match["frames"] = {"status": "MISSING", "rows": 0}
            match["commands"] = analyze_commands(reader.jsonl(command_path)) if command_path.exists() else {"status": "NO_COMMAND_FILE", "accepted_command_replies": 0, "rejected_command_replies": 0}
            last_state_wall = (match["states"].get("last") or {}).get("wall_seconds")
            match["observed_namespace_wall_seconds"] = max(x for x in [number(session.get("elapsed_wall_seconds"), 0), last_state_wall or 0, match["frames"].get("last_wall_seconds") or 0])
            match["wall_seconds_to_first_finished_state"] = (match["states"].get("first_finished") or {}).get("wall_seconds")
            reported_samples = session.get("frame_interval", {}).get("samples")
            match["csv_vs_session_frame_count"] = {
                "csv_rows": match["frames"]["rows"], "session_reported_samples": reported_samples,
                "difference": match["frames"]["rows"] - reported_samples if isinstance(reported_samples, int) else None,
                "boundary": "A nonzero difference is retained; final session-write and frame-flush timing can differ. No missing CSV samples are reconstructed from a percentile summary."}
            match["declared_normal_speed"] = session.get("simulation_speed_multiplier") == 1
            match["pause_adjusted_simulation_duration_seconds"] = None
            epoch = match["states"].get("namespace_epoch_utc_estimate")
            if not epoch and utc(session.get("utc")):
                epoch = (utc(session["utc"]) - timedelta(seconds=number(session.get("elapsed_wall_seconds"), 0))).isoformat()
            match["epoch_utc_estimate"] = epoch
            matches.append(match)
    matches.sort(key=lambda item: item.get("epoch_utc_estimate") or "")
    restarts = []
    for before, after in zip(matches, matches[1:]):
        initial = after["states"].get("first") or {}
        seats = initial.get("seats", [])
        restarts.append({
            "from_namespace": before["match_namespace"], "to_namespace": after["match_namespace"],
            "prior_finished_observed": before["states"]["finished_public_state_observed"],
            "new_round_one_observed": after["states"]["initial_round_one_observed"],
            "eight_positive_health_seats_observed": len(seats) == 8 and all(number(s.get("health"), 0) > 0 for s in seats),
            "eight_zero_placements_observed": len(seats) == 8 and all(integer(s.get("place"), -1) == 0 for s in seats),
            "state_level_restart_after_completion": before["states"]["finished_public_state_observed"] and after["states"]["initial_round_one_observed"],
            "initial_owner_private_summary": initial.get("owner_private_summary"),
            "boundary": "Namespace/round/seat reset evidence; does not prove which UI button was used or full fresh-state correctness."})
    changing = [item["path"] for item in reader.files if not item["stable_during_read"]]
    report = {"generated_utc": datetime.now(timezone.utc).isoformat(), "process_id": args.pid,
              "analysis_status": "COMPLETE_READ" if not reader.errors and not changing else "INCOMPLETE_OR_CHANGED_INPUT",
              "process_exit": "Operator supplied --confirm-process-exited; not independently detected by this script.",
              "boundaries": SOURCE_BOUNDARIES, "input_files": reader.files, "parse_errors": reader.errors,
              "diagnostics": reader.diagnostics,
              "files_changed_during_read": changing, "matches": matches, "namespace_transitions": restarts,
              "sum_observed_namespace_wall_seconds": sum(m["observed_namespace_wall_seconds"] for m in matches),
              "sum_declared_1x_namespace_wall_seconds": sum(m["observed_namespace_wall_seconds"] for m in matches if m["declared_normal_speed"]),
              "normal_speed_namespace_count": sum(m["declared_normal_speed"] for m in matches),
              "maximum_recorded_ms_across_namespaces": {key: max((m["frames"]["groups"]["all_recorded"][key]["max_ms"] for m in matches if "max_ms" in m["frames"].get("groups", {}).get("all_recorded", {}).get(key, {})), default=None) for key in METRICS},
              "spike_csv": str(spike_path.resolve()),
              "not_assessed": ["audio/listening", "continuous rendered motion", "uninspected screenshots", "physical GPU/CPU validation beyond recorded metadata", "balanced gameplay", "Unreal asset art approval", "eight-human/network hosting", "release readiness"]}
    (args.output / "run_analysis.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# Native normal-speed run: recorded evidence analysis", "", f"Generated {report['generated_utc']}; PID {args.pid}; status **{report['analysis_status']}**.", "",
             "Wall durations include unidentified Solo Options pauses. All recorded frame samples and spikes are included. The writer's first-five-seconds and post-completion omissions remain explicit limits.", "",
             "| Namespace | Declared speed | Observed wall seconds | CSV frames | Finished state | Round-one through finish | Accepted/rejected command replies |",
             "| --- | --- | ---: | ---: | --- | --- | --- |"]
    for match in matches:
        states, frames, commands = match["states"], match["frames"], match["commands"]
        lines.append(f"| {match['match_namespace']} | {match['session'].get('simulation_speed_multiplier', 'unavailable')} | {match['observed_namespace_wall_seconds']:.3f} | {frames['rows']} | {states['finished_public_state_observed']} | {states['state_level_full_tournament_observed']} | {commands['accepted_command_replies']}/{commands['rejected_command_replies']} |")
    for match in matches:
        lines += ["", f"## Namespace {match['match_namespace']}", "", "Recorded authority seeds: " + str(match["states"]["authority_seeds_seen"]) + ". Scripted default seed fields are not substituted for the authority seed.", "",
                  "| Frame subset | Samples | p50 ms | p95 ms | p99 ms | Maximum ms | >50 ms | >100 ms |",
                  "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for name, group in match["frames"].get("groups", {}).items():
            if name.startswith("round:"):
                continue
            timing = group["frame_ms"]
            if timing["samples"]:
                lines.append(f"| {name} | {timing['samples']} | {timing['p50_ms']:.3f} | {timing['p95_ms']:.3f} | {timing['p99_ms']:.3f} | {timing['max_ms']:.3f} | {timing['over_50_ms']} | {timing['over_100_ms']} |")
        s = match["session"]
        lines += ["", f"Recorded machine: {s.get('cpu', 'unavailable')}; active adapter {s.get('active_rhi_adapter', 'unavailable')}; RHI {s.get('rhi', 'unavailable')}; viewport {s.get('resolution_x', '?')}×{s.get('resolution_y', '?')}; engine {s.get('engine', 'unavailable')}.",
                  "", "Human elimination observed: " + str(match["states"]["human_elimination_observed"]) + ". Round/phase continuation, rankings, all per-round timings, encounter progress, command replies, settings and maximum-spike context are in run_analysis.json."]
    lines += ["", "## Input diagnostics", "", "Identical repeated CSV headers recognized: " + str(len(reader.diagnostics)) + ". Their exact file, physical line, header occurrence and fields are recorded in run_analysis.json. Arbitrary malformed rows remain parse errors.",
              "", "## Restart evidence", "", json.dumps(restarts, indent=2), "", "## Boundaries", ""]
    lines += ["- " + item for item in SOURCE_BOUNDARIES]
    lines += ["", "No audio or continuous visual review was performed by this analyzer. See run_analysis_spikes.csv for every recorded row where any available timing metric exceeded 33.333 ms, and run_analysis.json for the top 20 rows per metric without outlier trimming."]
    (args.output / "run_analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["analysis_status"], "namespaces": len(matches), "recorded_frames": sum(m["frames"]["rows"] for m in matches),
                      "parse_errors": len(reader.errors), "changing_inputs": len(changing), "outputs": ["run_analysis.json", "run_analysis.md", "run_analysis_spikes.csv"]}, indent=2))
    return 0 if report["analysis_status"] == "COMPLETE_READ" else 2


if __name__ == "__main__":
    raise SystemExit(main())
