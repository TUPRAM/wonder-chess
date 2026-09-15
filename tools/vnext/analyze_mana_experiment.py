"""Audit and summarize a paired, opt-in mana activation experiment."""
import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path


def rows(root, name):
    with (root / name).open(newline='', encoding='utf-8-sig') as handle:
        return list(csv.DictReader(handle))


def activity_summary(records):
    if not records:
        return {'instances': 0}
    cast_times = [int(r['first_cast_tick']) * .05 for r in records if int(r['first_cast_tick']) >= 0]
    return {
        'instances': len(records),
        'casts_per_instance': sum(int(r['casts']) for r in records) / len(records),
        'median_first_commit_seconds_among_casters': statistics.median(cast_times) if cast_times else None,
        'never_cast_count': sum(int(r['casts']) == 0 for r in records),
        'dead_before_any_cast_count': sum(r['alive'] == '0' and r['casts'] == '0' for r in records),
        'dead_with_mana_count': sum(int(r['mana_on_death']) > 0 for r in records),
        'ready_blocked_instances': sum(int(r['blocked_ready_decisions']) > 0 for r in records),
        'mana_from_attacks': sum(int(r['mana_from_attacks']) for r in records) / 100,
        'mana_from_damage': sum(int(r['mana_from_damage']) for r in records) / 100,
    }


def summarize(root):
    tournaments = rows(root, 'tournaments.csv')
    encounters = rows(root, 'encounters.csv')
    formations = rows(root, 'mana_formations.csv')
    activity = rows(root, 'ability_activity.csv')
    fixed_activity = rows(root, 'mana_formation_activity.csv')
    for record in activity + fixed_activity:
        earned = int(record['mana_from_attacks']) + int(record['mana_from_damage'])
        accounted = sum(int(record[key]) for key in ('mana_spent', 'mana_remaining', 'mana_on_death'))
        if earned != accounted:
            raise ValueError('Mana conservation failed in zero-start experiment: ' + str(record))
    result = {'directory': str(root.resolve()), 'tournaments': len(tournaments),
              'capped_tournaments': sum(int(r['capped']) for r in tournaments),
              'median_simulated_minutes': statistics.median(int(r['simulated_ms']) for r in tournaments) / 60000,
              'encounters': len(encounters), 'timeouts': sum(int(r['timeout']) for r in encounters),
              'fixed_formation_encounters': len(formations), 'fixed_timeouts': sum(int(r['timeout']) for r in formations),
              'activity_rows_audited': len(activity) + len(fixed_activity), 'strata': {}, 'heroes': {}, 'fixed_heroes': {}}
    for kind in ('pvp', 'ghost', 'neutral'):
        group = [r for r in encounters if r['kind'] == kind]
        result['strata'][kind] = {'encounters': len(group), 'timeouts': sum(int(r['timeout']) for r in group)}
    for hero in sorted({r['hero'] for r in activity}):
        result['heroes'][hero] = {kind: activity_summary([r for r in activity if r['hero'] == hero and (kind == 'all' or r['kind'] == kind)]) for kind in ('all', 'pvp', 'ghost', 'neutral')}
    for hero in ('wc_vn_snapvine', 'wc_vn_prism_organ', 'wc_vn_reefglass'):
        result['fixed_heroes'][hero] = {}
        for layout in ('protected', 'exposed'):
            for star in ('1', '2', '3'):
                group = [r for r in fixed_activity if r['hero'] == hero and r['kind'] == layout and r['star'] == star]
                result['fixed_heroes'][hero][layout + '_star' + star] = activity_summary(group)
    return result, tournaments, formations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', required=True, type=Path)
    parser.add_argument('--mana', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--baseline-label', default='control')
    parser.add_argument('--candidate-label', default='mana100')
    args = parser.parse_args()
    if args.baseline_label == args.candidate_label or {args.baseline_label, args.candidate_label} & {'status', 'fixed_pairs', 'boundary'}:
        raise ValueError('Distinct, non-reserved arm labels required')
    control, ct, cf = summarize(args.control)
    mana, mt, mf = summarize(args.mana)
    if [r['seed'] for r in ct] != [r['seed'] for r in mt]:
        raise ValueError('Tournament seeds differ')
    key = lambda r: tuple(r[x] for x in ('hero', 'layout', 'star', 'mirror', 'seed'))
    if [key(r) for r in cf] != [key(r) for r in mf]:
        raise ValueError('Fixed formation keys differ')
    pairs = {'winner_changed': 0, 'mana_shorter': 0, 'mana_longer': 0, 'same_duration': 0}
    for a, b in zip(cf, mf):
        pairs['winner_changed'] += a['winner'] != b['winner']
        delta = int(b['ticks']) - int(a['ticks'])
        pairs['mana_shorter' if delta < 0 else 'mana_longer' if delta > 0 else 'same_duration'] += 1
    result = {'status': 'AUDITED_EXPERIMENT_NOT_ACCEPTED_BALANCE', args.baseline_label: control, args.candidate_label: mana,
              'fixed_pairs': pairs, 'boundary': 'Development seeds only. Fixed formations isolate activation; tournament composition can diverge after changed results. Bot simulation is not human duration, enjoyment or balance acceptance.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise ValueError('Preserve the earlier analysis; select a fresh output')
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({arm: {k: v for k, v in values.items() if k not in ('heroes', 'fixed_heroes')} for arm, values in ((args.baseline_label, control), (args.candidate_label, mana))}, indent=2))


if __name__ == '__main__':
    main()
