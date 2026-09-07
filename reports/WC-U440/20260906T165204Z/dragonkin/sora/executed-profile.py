"""Sora production targets on a separately calibrated draconic rest skeleton.

The prepared geometry helper remains frozen. These are normalized world-space
contact targets; actual Blender solving, exports and Unreal calibration are
separate evidence. Other Dragonkin are deliberately gated out of this pilot.
"""
import math

RIG_REVISION = 'WC_humanoid_draconic_v1'


def smooth(t):
    t = max(0., min(1., t))
    return t * t * (3 - 2 * t)


def motion_pose(unit, clip, frame):
    from prepare_dragonkin_family import clip_contract
    if unit['id'] != 'wc_u_dragonkin_guardian':
        raise ValueError('Only the released Sora pilot is authorized in this profile')
    spec = clip_contract(unit)[clip]
    t = (frame - 1) / (spec['frames'][1] - 1)
    wave = math.sin(t * math.tau)
    pose = dict(body=(0, 0, -.006), head_euler=(0, 0, 0),
                palms={'l': (.24, .15, .55), 'r': (-.23, .14, .54)},
                hand_euler={'l': (-8, 0, 0), 'r': (-25, 0, 0)},
                feet={'l': (.085, 0, .07), 'r': (-.085, 0, .07)})
    release = spec['release_frame']
    if release:
        anticipation = smooth((frame - 1) / max(1, release * .55 - 1))
        recovery = smooth((frame - release) / max(1, spec['frames'][1] - release))
        amount = anticipation * (1 - recovery)
        if clip == 'Active':
            pose['palms']['l'] = (.235, .15 + .035 * amount, .55 + .075 * amount)
            pose['hand_euler']['l'] = (-8 - 24 * amount, 0, 0)
            pose['head_euler'] = (-3 * amount, 0, 0)
        elif clip == 'Attack':
            # Raised short mace is held before release, then snaps forward.
            strike = smooth((frame - release + 3) / 6) * (1 - recovery)
            pose['palms']['r'] = (-.23, .14 - .025 * amount + .105 * strike, .54 + .05 * amount)
            pose['hand_euler']['r'] = (-25 + 12 * amount - 65 * strike, 0, 0)
    if clip == 'Idle':
        pose['head_euler'] = (.45 * wave, 0, .7 * wave)
        pose['palms'] = {side: (p[0], p[1], p[2] + .0015 * wave) for side, p in pose['palms'].items()}
    elif clip == 'Move':
        pose['body'] = (0, 0, -.010 + .002 * math.cos(t * 4 * math.pi))
        for side, sign in (('l', 1), ('r', -1)):
            cycle = (t + (0 if side == 'l' else .5)) % 1
            if cycle < .5:
                y, lift = .048 - .192 * cycle, 0.
            else:
                step = (cycle - .5) * 2
                y, lift = -.048 + .096 * smooth(step), .018 * math.sin(math.pi * step)
            pose['feet'][side] = (sign * .085, y, .07 + lift)
            p = pose['palms'][side]
            pose['palms'][side] = (p[0], p[1] + .007 * sign * wave, p[2])
    elif clip == 'Hit':
        amount = math.sin(t * math.pi)
        pose['body'] = (0, -.010 * amount, -.006 - .012 * amount)
        pose['head_euler'] = (7 * amount, 0, 0)
        pose['palms'] = {side: (p[0], p[1] - .015 * amount, p[2] - .014 * amount) for side, p in pose['palms'].items()}
    elif clip == 'Defeat':
        amount = smooth(t / .8)
        pose['body'] = (0, -.018 * amount, -.006 - .10 * amount)
        pose['head_euler'] = (18 * amount, 0, 0)
        pose['palms'] = {side: (p[0], p[1] + .015 * amount, p[2] - .08 * amount) for side, p in pose['palms'].items()}
        pose['hand_euler']['l'] = (-8 + 12 * amount, 0, 0)
        pose['hand_euler']['r'] = (-25 + 18 * amount, 0, 0)
    elif clip == 'Victory':
        amount = smooth(min(t / .3, (1 - t) / .25))
        pose['palms']['r'] = (-.23, .14, .54 + .11 * amount)
        pose['hand_euler']['r'] = (-25 + 18 * amount, 0, 0)
        pose['head_euler'] = (-4 * amount, 0, 2 * wave)
    if clip not in ('Hit', 'Defeat'):
        pose['palms'] = {side: tuple(p[i] + pose['body'][i] for i in range(3)) for side, p in pose['palms'].items()}
    return pose
