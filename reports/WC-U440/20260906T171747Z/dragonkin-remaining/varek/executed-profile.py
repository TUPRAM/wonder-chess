"""Released Dragonkin targets on a separately calibrated draconic rest skeleton.

The prepared geometry helper remains frozen. These are normalized world-space
contact targets; actual Blender solving, exports and Unreal calibration are
separate evidence. Source production follows the root's explicit family order.
"""
import math

RIG_REVISION = 'WC_humanoid_draconic_v1'


def smooth(t):
    t = max(0., min(1., t))
    return t * t * (3 - 2 * t)


def sora_pose(unit, clip, frame):
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
            pose['hand_euler']['l'] = (-8 + 32 * amount, 0, 0)
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


def clip_spec(unit):
    from prepare_dragonkin_family import clip_contract
    clips=clip_contract(unit)
    if unit['id']=='wc_u_dragonkin_rogue':
        cycle=clips['Attack']['frames'][1]-1
        offset=round(unit['stats']['attack_windup_ms']*.06)
        clips['Attack']['frames']=[1,cycle*2+1]
        clips['Attack']['presentation_windows']=[
            dict(name='R',start_frame=1,release_frame=1+offset,end_frame=1+cycle),
            dict(name='L',start_frame=1+cycle,release_frame=1+cycle+offset,end_frame=1+cycle*2)]
    return clips


def motion_pose(unit,clip,frame):
    if unit['id']=='wc_u_dragonkin_guardian':return sora_pose(unit,clip,frame)
    cls=unit['unit_class'];spec=clip_spec(unit)[clip]
    attack_side='r'
    if cls=='rogue' and clip=='Attack':
        window=spec['presentation_windows'][0 if frame<=spec['presentation_windows'][0]['end_frame'] else 1]
        attack_side=window['name'].lower();frame=frame-window['start_frame']+1
        spec=dict(frames=[1,window['end_frame']-window['start_frame']+1],release_frame=window['release_frame']-window['start_frame']+1)
    t=(frame-1)/(spec['frames'][1]-1);wave=math.sin(t*math.tau)
    release=spec['release_frame']
    load=smooth((frame-1)/max(1,(release or 1)-1)) if release else 0.
    recovery=smooth((frame-(release or 1))/max(1,spec['frames'][1]-(release or 1))) if release else 0.
    amount=load*(1-recovery)
    ready=smooth((frame-1)/max(1,(release or 1)*.45))*(1-recovery) if release else 0.
    pose=dict(body=(0,0,-.008),head_euler=(0,0,0),palms={},hand_euler={},
        feet={'l':(.085,0,.07),'r':(-.085,0,.07)})
    if cls=='ranger':
        bow=(.10,.16+.025*ready,.54+.075*ready)
        snap=smooth((frame-(release or 1))/5) if release else 1.
        draw=.035+.080*load*(1-snap)
        pose['palms']={'l':bow,'r':(bow[0]-.040,bow[1]-draw,bow[2])}
        pose['hand_euler']={'l':(-6*ready if clip=='Active' else 0,0,-4*ready if clip=='Active' else 0),'r':(0,0,0)}
        pose['head_euler']=(-3*ready,0,-4*ready)
    elif cls=='rogue':
        pose['palms']={'l':(.205,.12,.535),'r':(-.205,.13,.535)}
        pose['hand_euler']={'l':(-22,0,-8),'r':(-22,0,8)}
        pose['head_euler']=(2,0,-3)
        if clip=='Attack':
            sign=1 if attack_side=='l' else -1
            strike=smooth((frame-(release or 1)+3)/6)*(1-recovery)
            pose['palms'][attack_side]=(sign*(.205-.03*strike),(.12 if sign==1 else .13)-.027*load*(1-recovery)+.10*strike,.535+.033*amount)
            pose['hand_euler'][attack_side]=(-22+15*amount-56*strike,0,-sign*8)
        elif clip=='Active':
            hold=smooth((frame-1)/max(1,(release or 1)*.5))*(1-recovery)
            strike=smooth((frame-(release or 1)+2)/4)*(1-recovery)
            pose['palms']['r']=(-.205+.055*hold,.13-.035*hold+.075*strike,.535+.036*hold)
            pose['hand_euler']['r']=(-22+14*hold-44*strike,0,8)
    elif cls=='priest':
        pose['palms']={'l':(.19,.11,.49),'r':(-.215,.12,.52)}
        pose['hand_euler']={'l':(-8,0,0),'r':(-4,0,0)}
        if clip=='Attack':
            pose['palms']['r']=(-.215,.12+.045*amount,.52+.018*amount)
            pose['hand_euler']['r']=(-4-12*amount,0,0)
        elif clip=='Active':
            pose['palms']['l']=(.17,.11+.12*amount,.49+.15*amount)
            pose['hand_euler']['l']=(-8-28*amount,0,0)
            pose['palms']['r']=(-.215,.12+.035*amount,.52+.05*amount)
            pose['hand_euler']['r']=(-4-6*amount,0,-7*amount)
            pose['head_euler']=(-3*amount,0,-7*amount)
    else:raise ValueError('Unknown released Dragonkin class')
    if clip=='Idle':
        pose['head_euler']=(pose['head_euler'][0]+.6*wave,0,pose['head_euler'][2]+.8*wave)
        pose['palms']={side:(p[0],p[1],p[2]+.0015*wave) for side,p in pose['palms'].items()}
    elif clip=='Move':
        pose['body']=(0,0,-.013+.002*math.cos(t*4*math.pi))
        for side,sign in (('l',1),('r',-1)):
            cycle=(t+(0 if side=='l' else .5))%1
            if cycle<.5:y,lift=.052-.208*cycle,0.
            else:
                step=(cycle-.5)*2;y,lift=-.052+.104*smooth(step),.023*math.sin(math.pi*step)
            pose['feet'][side]=(sign*.085,y,.07+lift)
    elif clip=='Hit':
        hit=math.sin(t*math.pi);pose['body']=(0,-.010*hit,-.008-.015*hit)
        pose['head_euler']=(9*hit,0,0)
        pose['palms']={side:(p[0],p[1]-.008*hit,p[2]-.014*hit) for side,p in pose['palms'].items()}
    elif clip=='Defeat':
        fall=smooth(t/.8);pose['body']=(0,-.018*fall,-.008-.11*fall)
        pose['head_euler']=(21*fall,0,-5*fall)
        pose['palms']={side:(p[0],p[1],p[2]-.082*fall) for side,p in pose['palms'].items()}
    elif clip=='Victory':
        celebrate=smooth(min(t/.3,(1-t)/.25));pose['head_euler']=(-4*celebrate,0,3*wave)
        if cls=='ranger':pose['palms']={side:(p[0],p[1],p[2]+.07*celebrate) for side,p in pose['palms'].items()}
        else:
            side='l' if cls=='priest' else 'r';p=pose['palms'][side]
            pose['palms'][side]=(p[0],p[1],p[2]+.075*celebrate)
    if clip not in ('Hit','Defeat'):
        pose['palms']={side:tuple(p[i]+pose['body'][i] for i in range(3)) for side,p in pose['palms'].items()}
    return pose
