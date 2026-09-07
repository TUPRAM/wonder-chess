"""Halfling source-production recipes and analytical motion preparation.

This module has no Blender dependency and never writes source or export binaries.
Run ``python tools/blender/halfling_production_profile.py --check-math`` before
consuming its profiles from a separately released Blender production operation.
The reach check proves only the proposed two-link targets, not skin deformation,
prop contact, export validity, or visual acceptance in Blender or Unreal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FPS = 60
RIG_REVISION = 'WC_humanoid_small_v1'
CLIPS = ('Idle', 'Move', 'Attack', 'Active', 'Hit', 'Defeat', 'Victory')
IDS = ('wc_u_halfling_warrior', 'wc_u_halfling_ranger',
       'wc_u_halfling_rogue', 'wc_u_halfling_mage')

# Colors 0..3 come from each canonical palette; face colors are authored material
# choices. Adult head height is about one sixth of the total height, not one third.
PROFILES = {
    IDS[0]: dict(name='Pippa', torso_width=.142, torso_depth=.083, jaw_width=.058,
                 cheek_width=.079, skin='#B77C58', skin_accent='#D49B70',
                 hair='#55321F', iris='#897144', hair_style='dense_short_curls',
                 garment='quilted_waist_jacket', gear='club_and_orchard_buckler',
                 face='freckled_broad_cheeks_adult_jaw', feet_width=.067,
                 rear='square_patch_and_berry_scarf',
                 skill='contained_hop_buckler_brace_personal_shield'),
    IDS[1]: dict(name='Finn', torso_width=.119, torso_depth=.074, jaw_width=.056,
                 cheek_width=.071, skin='#BE8D66', skin_accent='#D6AD82',
                 hair='#AB8752', iris='#423D33', hair_style='short_sandy_curls',
                 garment='fitted_blue_vest_cream_sleeves', gear='upright_bow',
                 face='thoughtful_almond_eyes_adult_nose', feet_width=.057,
                 rear='short_triangle_cape_and_side_quiver',
                 skill='careful_aim_one_tempo_debuff_projectile'),
    IDS[2]: dict(name='Nella', torso_width=.122, torso_depth=.075, jaw_width=.054,
                 cheek_width=.074, skin='#86553E', skin_accent='#AE7554',
                 hair='#352822', iris='#666746', hair_style='swept_curl_clipped_sides',
                 garment='plum_jacket_with_asymmetric_lapel', gear='paired_fan_batons',
                 face='raised_outer_brow_and_adult_chin', feet_width=.057,
                 rear='diamond_cape_diagonal_teal_cord',
                 skill='offhand_feint_one_forward_gesture_zero_damage_no_dash'),
    IDS[3]: dict(name='Milo', torso_width=.151, torso_depth=.098, jaw_width=.061,
                 cheek_width=.079, skin='#C1956E', skin_accent='#D9AF84',
                 hair='#604431', iris='#747C80', hair_style='side_part_waves',
                 garment='round_raincoat_two_lower_panels', gear='spiral_wand',
                 face='small_mustache_longer_nose_adult_cheek_planes', feet_width=.063,
                 rear='folded_rigid_disk_on_short_fixed_bracket',
                 skill='one_circular_stir_and_flick_captured_area_burst'),
}


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def scale(a, amount):
    return tuple(x * amount for x in a)


def length(a):
    return math.sqrt(sum(x * x for x in a))


def smooth(value):
    t = min(1.0, max(0.0, value))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return add(a, scale(sub(b, a), t))


def rotate_xyz(point, degrees):
    """World-space Rx, then Ry, then Rz; matches a Blender XYZ Euler matrix."""
    x, y, z = point
    rx, ry, rz = (math.radians(v) for v in degrees)
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    return (x * math.cos(rz) - y * math.sin(rz),
            x * math.sin(rz) + y * math.cos(rz), z)


def rig_spec():
    """Fixed small-family rest profile, metres normalized by canonical height.

    The established bone names and parents remain unchanged. Proportions are
    independently authored: narrower shoulders and longer legs than the Dwarf
    rig, with adult head planes and hands. This is not a uniform family rescale.
    """
    bones = [
        ('root', (0, 0, 0), (0, 0, .1), None),
        ('pelvis', (0, 0, .47), (0, 0, .545), 'root'),
        ('spine_01', (0, 0, .545), (0, 0, .635), 'pelvis'),
        ('spine_02', (0, 0, .635), (0, 0, .705), 'spine_01'),
        ('spine_03', (0, 0, .705), (0, 0, .79), 'spine_02'),
        ('neck', (0, 0, .79), (0, 0, .846), 'spine_03'),
        ('head', (0, 0, .846), (0, 0, .988), 'neck'),
    ]
    points = {}
    for side, sign in (('l', 1), ('r', -1)):
        p = dict(shoulder=(sign * .17, 0, .765), elbow=(sign * .23, .014, .61),
                 wrist=(sign * .275, .035, .445), hand=(sign * .28, .06, .405),
                 hip=(sign * .082, 0, .47), knee=(sign * .082, .006, .264),
                 ankle=(sign * .082, 0, .065), toe=(sign * .082, .123, .025))
        points[side] = p
        bones.extend([
            (f'clavicle_{side}', (sign * .034, 0, .765), p['shoulder'], 'spine_03'),
            (f'upperarm_{side}', p['shoulder'], p['elbow'], f'clavicle_{side}'),
            (f'lowerarm_{side}', p['elbow'], p['wrist'], f'upperarm_{side}'),
            (f'hand_{side}', p['wrist'], p['hand'], f'lowerarm_{side}'),
            (f'thigh_{side}', p['hip'], p['knee'], 'pelvis'),
            (f'calf_{side}', p['knee'], p['ankle'], f'thigh_{side}'),
            (f'foot_{side}', p['ankle'], p['toe'], f'calf_{side}'),
            (f'toe_{side}', p['toe'], (p['toe'][0], .16, .025), f'foot_{side}'),
        ])
    for side in ('r', 'l'):
        p = points[side]['hand']
        bones.append((f'weapon_{side}', p, add(p, (0, .08, 0)), f'hand_{side}'))
    bones.extend([('cast_origin', (0, .16, .72), (0, .25, .72), 'spine_03'),
                  ('head_ui', (0, 0, 1.025), (0, 0, 1.075), 'head')])
    return bones, points


def clip_spec(unit):
    intervals = dict(Idle=120, Move=60, Attack=max(36, round(unit['stats']['attack_windup_ms'] * .06) + 24),
                     Active=max(30, round((unit['ability']['cast_ms'] + unit['ability']['recovery_ms']) * .06)),
                     Hit=24, Defeat=60, Victory=90)
    result = {}
    for clip in CLIPS:
        ms = unit['stats']['attack_windup_ms'] if clip == 'Attack' else unit['ability']['cast_ms']
        release = 1 + round(ms * FPS / 1000) if clip in ('Attack', 'Active') else None
        result[clip] = dict(frames=[1, intervals[clip] + 1], fps=FPS, release_frame=release,
                            duration_seconds=intervals[clip] / FPS, loop=clip in ('Idle', 'Move'))
    return result


def action_envelope(frame, spec):
    release = spec['release_frame']
    if release is None:
        return 0.0, 0.0
    if frame <= release:
        return smooth((frame - 1) / max(1, release - 1)), 0.0
    return 1.0, smooth((frame - release) / (spec['frames'][1] - release))


def motion_pose(unit, clip, frame):
    """Return bounded normalized world targets; source production must solve IK.

    Root stays fixed. The body translation is only a small pelvis lift/drop;
    shoulder rotation is zero here so the analytical target model is explicit.
    Every future torso-rotation change requires the executed Blender reach audit.
    Hand Euler values rotate rest-hand offsets, not local pose channels.
    """
    uid = unit['id']
    spec = clip_spec(unit)[clip]
    t = (frame - 1) / (spec['frames'][1] - 1)
    phase = math.sin(t * 2 * math.pi)
    load, recover = action_envelope(frame, spec)
    amount = load * (1 - recover)
    release_pulse = math.sin(math.pi * load) * (1 - recover)
    pose = dict(root=(0, 0, 0), body=(0, 0, -.003), head_euler=(0, 0, 0),
                palms={'l': (.18, .105, .535), 'r': (-.18, .105, .535)},
                hand_euler={'l': (0, 0, 0), 'r': (0, 0, 0)},
                feet={'l': (.094, .004, .065), 'r': (-.094, .004, .065)},
                foot_euler={'l': (0, 0, 0), 'r': (0, 0, 0)}, bow_draw=0.0)
    if uid == IDS[0]:
        pose['palms'] = {'l': (.175, .125, .58), 'r': (-.19, .1, .565)}
        pose['hand_euler']['r'] = (-10, 0, -6)
        if clip == 'Attack':
            pose['palms']['r'] = (-.19, .1 + .095 * amount, .565 + .025 * release_pulse)
            pose['hand_euler']['r'] = (-10 - 66 * amount + 25 * release_pulse, 0, -6)
        elif clip == 'Active':
            pose['body'] = (0, 0, -.003 + .012 * release_pulse)
            pose['feet'] = {side: add(foot, (0, 0, .012 * release_pulse))
                            for side, foot in pose['feet'].items()}
            pose['palms']['l'] = (.15, .165, .60 + .035 * amount)
            pose['palms']['r'] = (-.19, .12, .565)
            pose['hand_euler']['l'] = (-12 * amount, 0, 8 * amount)
    elif uid == IDS[1]:
        bow = (.155, .14, .59)
        draw = .080 + .050 * release_pulse
        pose['bow_draw'] = draw
        pose['palms'] = {'l': bow, 'r': (-.105, .10, .59)}
        pose['hand_euler'] = {'l': (0, 0, 0), 'r': (0, 0, 18)}
        if clip in ('Attack', 'Active'):
            pose['palms']['l'] = (.14, .175, .60)
            # The right fingers follow the actual string nock, rather than a
            # distant chest pose. Production attaches the nock to weapon_r.
            pose['palms']['r'] = (-.045, .175 - draw, .60)
            pose['head_euler'] = (-3 * amount, 0, -5 * amount)
    elif uid == IDS[2]:
        pose['palms'] = {'l': (.195, .105, .56), 'r': (-.20, .125, .55)}
        pose['hand_euler'] = {'l': (8, 0, -20), 'r': (-10, 0, 20)}
        pose['head_euler'] = (0, 0, -6)
        if clip == 'Attack':
            pose['palms']['r'] = (-.19, .125 + .10 * amount, .55 + .01 * amount)
            pose['hand_euler']['r'] = (-10 - 53 * amount, 0, 20)
        elif clip == 'Active':
            pose['palms']['l'] = (.195, .105 + .095 * release_pulse, .56 + .022 * release_pulse)
            pose['palms']['r'] = (-.19, .125 + .09 * amount, .55 + .027 * amount)
            pose['hand_euler']['l'] = (8 - 34 * release_pulse, 0, -20)
            pose['hand_euler']['r'] = (-10 - 46 * amount, 0, 20)
    elif uid == IDS[3]:
        pose['palms'] = {'l': (.165, .10, .545), 'r': (-.17, .13, .585)}
        pose['head_euler'] = (0, 0, 5)
        if clip == 'Attack':
            pose['palms']['r'] = (-.17, .13 + .065 * amount, .585)
            pose['hand_euler']['r'] = (-47 * amount, 0, 0)
        elif clip == 'Active':
            angle = load * 2 * math.pi
            pose['palms']['r'] = (-.17 + .021 * math.sin(angle) * (1 - recover),
                                   .13 + .048 * amount, .585 + .021 * (1 - math.cos(angle)) * (1 - recover))
            pose['hand_euler']['r'] = (-48 * amount, 0, 12 * math.sin(angle) * (1 - recover))
    if clip == 'Idle':
        pose['head_euler'] = add(pose['head_euler'], (phase * 1.2, 0, phase * .7))
        pose['palms'] = {side: add(palm, (0, 0, .002 * phase)) for side, palm in pose['palms'].items()}
    elif clip == 'Move':
        pose['body'] = (0, 0, -.009 + .003 * math.cos(t * 4 * math.pi))
        for side, sign in (('l', 1), ('r', -1)):
            cycle = (t + (0 if side == 'l' else .5)) % 1
            if cycle < .5:
                y, lift = .055 - .22 * cycle, 0.0
            else:
                swing = (cycle - .5) * 2
                y, lift = -.055 + .11 * smooth(swing), .025 * math.sin(math.pi * swing)
            pose['feet'][side] = (sign * .094, y, .065 + lift)
            pose['palms'][side] = add(pose['palms'][side], (0, .012 * sign * phase, 0))
    elif clip == 'Hit':
        hit = math.sin(math.pi * t)
        pose['body'] = (0, -.007 * hit, -.003 - .015 * hit)
        pose['head_euler'] = (12 * hit, -5 * hit, 0)
        pose['palms'] = {side: add(palm, (0, -.01 * hit, -.015 * hit)) for side, palm in pose['palms'].items()}
    elif clip == 'Defeat':
        drop = smooth(t / .78)
        pose['body'] = (0, -.022 * drop, -.003 - .115 * drop)
        pose['head_euler'] = (24 * drop, 0, -8 * drop)
        pose['palms'] = {side: lerp(palm, ((1 if side == 'l' else -1) * .185, .12, .37), drop)
                         for side, palm in pose['palms'].items()}
        pose['hand_euler'] = {'l': (10 * drop, 0, 15 * drop), 'r': (20 * drop, 0, -15 * drop)}
    elif clip == 'Victory':
        cheer = smooth(min(t / .3, (1 - t) / .25))
        pose['head_euler'] = (-6 * cheer, 0, 4 * math.sin(t * 4 * math.pi))
        pose['palms']['r'] = lerp(pose['palms']['r'], (-.225, .11, .68), cheer)
        pose['hand_euler']['r'] = (0, 0, -20 * cheer)
    if clip not in ('Defeat', 'Hit'):
        pose['palms'] = {side: add(palm, pose['body']) for side, palm in pose['palms'].items()}
    return pose


def face_sections(uid):
    """Continuous chin/jaw/cheek/temple loft; eye and lip surfaces are separate."""
    p = PROFILES[uid]
    return [((0, .012, .832), p['jaw_width'] * .70, .040),
            ((0, .010, .847), p['jaw_width'], .059),
            ((0, .002, .876), p['cheek_width'], .071),
            ((0, -.003, .910), p['cheek_width'] * .98, .073),
            ((0, -.010, .944), p['cheek_width'] * .94, .068),
            ((0, -.013, .969), p['cheek_width'] * .72, .049)]


def palm_sections(side):
    """Tapered palm contours in the rest pose; no box hand primitive."""
    p = rig_spec()[1][side]
    sign = 1 if side == 'l' else -1
    wrist = p['wrist']
    return [(add(wrist, (0, 0, .005)), .020, .014),
            (add(wrist, (sign * .002, .007, -.016)), .025, .018),
            (add(wrist, (sign * .004, .017, -.031)), .024, .017),
            (add(wrist, (sign * .005, .025, -.045)), .020, .014)]


def finger_paths(side):
    """Four curved fingers plus an opposing thumb around a local grip axis."""
    hand = rig_spec()[1][side]['hand']
    sign = 1 if side == 'l' else -1
    fingers = []
    for index in range(4):
        x = hand[0] + sign * (-.017 + index * .010)
        z = hand[2] + .010 - .0015 * abs(index - 1.5)
        fingers.append([(x, hand[1] - .005, z), (x, hand[1] + .014, z - .011),
                        (x, hand[1] + .020, z - .023), (x, hand[1] + .012, z - .029)])
    fingers.append([add(hand, (-sign * .027, -.005, .026)),
                    add(hand, (-sign * .020, .015, .017)),
                    add(hand, (-sign * .007, .022, .008))])
    return fingers


def reach_interval(first, joint, end):
    a, b = length(sub(joint, first)), length(sub(end, joint))
    return abs(a - b), a + b


def check_math(units):
    bones, points = rig_spec()
    errors, rows = [], []
    assert len(bones) == 27 and len({row[0] for row in bones}) == 27
    known = set()
    for name, start, end, parent in bones:
        assert parent is None or parent in known
        assert length(sub(start, end)) > 0
        known.add(name)
    for unit in units:
        specs = clip_spec(unit)
        h = unit['height_m']
        for clip, spec in specs.items():
            arm_error = leg_error = 0.0
            minimum_margin = 1.0
            for frame in range(1, spec['frames'][1] + 1):
                pose = motion_pose(unit, clip, frame)
                assert pose['root'] == (0, 0, 0)
                for side in ('l', 'r'):
                    p = points[side]
                    wrist = sub(pose['palms'][side], rotate_xyz(sub(p['hand'], p['wrist']), pose['hand_euler'][side]))
                    distance = length(sub(wrist, add(p['shoulder'], pose['body'])))
                    low, high = reach_interval(p['shoulder'], p['elbow'], p['wrist'])
                    # Match the actual shared IK solver's one millimetre margin.
                    margin = min(distance - low, high - distance) * h - .001
                    minimum_margin = min(minimum_margin, margin)
                    arm_error = max(arm_error, -margin)
                    distance = length(sub(pose['feet'][side], add(p['hip'], pose['body'])))
                    low, high = reach_interval(p['hip'], p['knee'], p['ankle'])
                    leg_error = max(leg_error, max(low - distance, distance - high) * h + .001)
                    if not all(math.isfinite(v) for v in (*wrist, *pose['feet'][side])):
                        errors.append(f'{unit["id"]}/{clip}/{frame}/{side}: nonfinite target')
            if arm_error > 1e-8 or leg_error > 1e-8:
                errors.append(f'{unit["id"]}/{clip}: hand excess {arm_error:.6f}m, foot excess {leg_error:.6f}m')
            if clip in ('Idle', 'Move'):
                if motion_pose(unit, clip, 1) != motion_pose(unit, clip, spec['frames'][1]):
                    # Trigonometric roundoff must not become an artificial seam.
                    a = motion_pose(unit, clip, 1)
                    b = motion_pose(unit, clip, spec['frames'][1])
                    error = max(abs(x - y) for key in ('palms', 'feet') for side in ('l', 'r')
                                for x, y in zip(a[key][side], b[key][side]))
                    if error > 1e-10:
                        errors.append(f'{unit["id"]}/{clip}: loop target seam {error}')
            rows.append(dict(unit_id=unit['id'], clip=clip, sampled_frames=spec['frames'][1],
                             release_frame=spec['release_frame'], minimum_hand_reach_margin_m=minimum_margin,
                             maximum_hand_reach_excess_m=max(0, arm_error), maximum_leg_reach_excess_m=max(0, leg_error)))
    return dict(status='PASS' if not errors else 'FAIL', evidence_kind='ANALYTICAL_TARGETS_ONLY',
                blender_executed=False, source_or_export_binaries_written=False,
                rig_revision=RIG_REVISION, bones=len(bones), heroes=len(units), clip_rows=len(rows),
                samples=sum(row['sampled_frames'] for row in rows), errors=errors, clips=rows,
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                units_sha256=hashlib.sha256((ROOT / 'data/units.json').read_bytes()).hexdigest(),
                open_checks=['actual armature reach after all torso transforms', 'deformation and skin weights',
                             'finger contact and weapon sweep clearance', 'foot contact and floor clearance',
                             'all seven continuous clips', 'Blender and Unreal execution', 'visual art quality'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-math', action='store_true', required=True)
    opt = parser.parse_args()
    units = {unit['id']: unit for unit in json.loads((ROOT / 'data/units.json').read_text(encoding='utf-8'))['units']}
    result = check_math([units[uid] for uid in IDS])
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
