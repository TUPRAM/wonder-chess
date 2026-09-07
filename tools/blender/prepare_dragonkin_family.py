"""Prepared Dragonkin geometry and animation library; production has not executed.

The CLI only prints the source-backed preparation contract. Geometry/rig/action
functions change an explicitly supplied Blender scene in memory when an authorized
production driver calls them. This module never saves a blend, renders or exports.
Sora must pass family calibration before Varek/Iri/Oren production is released.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FPS = 60
CLIPS = ('Idle', 'Move', 'Attack', 'Active', 'Hit', 'Defeat', 'Victory')
FROZEN_HELPERS = {
    'author_alpha.py': 'ddaed7bb350bafb94c1743bc31c4b613524f971af01a5611835402590d8ae6f0',
    'hand_contacts.py': 'c36f8064fa5ab7ff136c399c68c7b012b5987234734aca0580bede3483017c1a',
    'normalized_fbx.py': '13646d355744f5293d573816e5cd54459cf88f3b647c6c2a22aa61ae29200779',
    'profiles/fbx_skeletal_cm_v1.json': '3bcc0d2c3fe17c404800b25de8f156b623da15d514f3ae2ac1891c65a0ae58ae',
}
PROFILES = {
    'wc_u_dragonkin_guardian': {
        'name': 'Sora', 'shoulder': .208, 'waist': .133, 'limb': .059, 'head_width': .087,
        'muzzle_front': .143, 'horns': 'short swept-back pair', 'crest': True,
        'anatomy': 'Broad chest, forward-set thick neck, rounded short closed muzzle, calm amber eyes, plantigrade armored feet.',
        'equipment': 'Upright oval beacon shield on left hand; short blunt ceremonial mace on right. No free-floating gem.',
        'motion': 'Tall still guard; deliberate steps; compact mace basic; upward shield angle with held anticipation before beacon release. Victory salutes with mace below horn height.',
        'clearances': ['muzzle versus shield rim', 'crest versus rear collar', 'horns versus clavicle armor', 'mace versus shield at release'],
        'palette': '#E0D8C1 #486A9A #C4A367 #4D5B67 #A5B3BA #675D50 #DDD0AB #A79A76 #EEE7D5 #B5833B #C4A367 #B7D4D0 #C5B99A #7D9BBD #A28B69 #34404C',
    },
    'wc_u_dragonkin_ranger': {
        'name': 'Varek', 'shoulder': .170, 'waist': .107, 'limb': .046, 'head_width': .079,
        'muzzle_front': .153, 'horns': 'short outward blunt fins', 'crest': False,
        'anatomy': 'Long narrow chest, short angular integrated muzzle, gold eyes, blunt horn fins; no human nose or ears.',
        'equipment': 'Broad horizontal opaque prism bow with dark central grip and a readable second-hand draw; hip-length forked cloak and flat rear quiver.',
        'motion': 'Low bow rest; two-hand raise/draw/release; active aligns opaque facets before a finite-travel magic shot. Lower bow during defeat and turn, never an overhead sweep.',
        'clearances': ['bow versus muzzle', 'bow versus neighbor health anchors', 'quiver versus forked cloak', 'horn fins versus shoulder panels'],
        'palette': '#3F567A #E6DFC9 #8BC9CA #304057 #A9BEC9 #546173 #7996AC #647F94 #EBE7D0 #D0B76D #C4B582 #8BC9CA #B5DADC #567A94 #526D83 #29394A',
    },
    'wc_u_dragonkin_rogue': {
        'name': 'Iri', 'shoulder': .159, 'waist': .104, 'limb': .044, 'head_width': .075,
        'muzzle_front': .137, 'horns': 'close backward pair', 'crest': True,
        'anatomy': 'Slim adult proportions, copper rounded short muzzle, violet eyes, neck crest ending above shoulders, visible elbow and knee shapes.',
        'equipment': 'Two broad decorative crescent blades, compact pale inset gems, coral diagonal sash over a closed charcoal jacket. No dash apparatus.',
        'motion': 'Low balanced idle; short alternating crescent basic; one blade draws inward, pauses for glint and releases deliberately. No teleport, leap or immunity pose.',
        'clearances': ['neck crest versus jacket in crouch', 'crescent versus forearm', 'paired blades versus torso', 'coral sash versus hip panels'],
        'palette': '#454552 #CB7B6B #837B9E #353641 #A8A4AE #705849 #AF7C60 #8C674F #E4D9CD #756581 #C7AC86 #D2CEDC #A77366 #D99380 #7B5343 #2E303A',
    },
    'wc_u_dragonkin_priest': {
        'name': 'Oren', 'shoulder': .178, 'waist': .112, 'limb': .048, 'head_width': .080,
        'muzzle_front': .140, 'horns': 'rounded swept arch pair', 'crest': False,
        'anatomy': 'Tall narrow adult torso, moss-gray rounded muzzle, attentive gold eyes and rounded swept horns with clear neck motion.',
        'equipment': 'Open hexagonal lantern staff in right hand, free left palm, closed rectangular map case; ankle-clearing white/teal split robe. No floating book.',
        'motion': 'Balanced staff rest; small light-mote basic; lantern turns toward recipient and free palm lifts for directional ward. No healing, revival or full-body glow.',
        'clearances': ['staff head versus horn arch', 'lantern rim versus free palm', 'mantle versus neck', 'robe panels versus boots in kneel'],
        'palette': '#E5E2D3 #3E7F83 #C4AC72 #425F61 #ADBDB4 #706951 #92A69D #9B9D82 #E8E5D4 #B99C54 #C4AC72 #C4D8C9 #749B93 #629795 #687E75 #354744',
    },
}


def source_unit(unit_id):
    unit = next(row for row in json.loads((ROOT / 'data/units.json').read_text())['units'] if row['id'] == unit_id)
    if unit_id not in PROFILES or unit['race'] != 'dragonkin' or unit['rig_family'] != 'humanoid_draconic':
        raise ValueError('The prepared family requires the canonical Dragonkin identity and rig family')
    return unit


def dependencies():
    actual = {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest() for name in FROZEN_HELPERS}
    if actual != FROZEN_HELPERS:
        raise RuntimeError('A frozen shared helper changed; review its contract before using this prepared library')
    return actual


def clip_contract(unit):
    active = int(round((unit['ability']['cast_ms'] + unit['ability'].get('recovery_ms', 300)) * FPS / 1000))
    basic_release = int(round(unit['stats']['attack_windup_ms'] * FPS / 1000))
    active_release = int(round(unit['ability']['cast_ms'] * FPS / 1000))
    ends = {'Idle': 120, 'Move': 60, 'Attack': max(36, basic_release + 24), 'Active': max(30, active),
            'Hit': 24, 'Defeat': 60, 'Victory': 90}
    return {clip: {'frames': [1, end + 1], 'release_frame': 1 + (active_release if clip == 'Active' else basic_release)
                   if clip in ('Attack', 'Active') else None} for clip, end in ends.items()}


def preparation_contract():
    return {'status': 'PREPARED_NOT_EXECUTED_IN_BLENDER', 'production_order': list(PROFILES),
            'canonical_units_sha256': hashlib.sha256((ROOT / 'data/units.json').read_bytes()).hexdigest(),
            'dossier_sha256': {uid: hashlib.sha256((ROOT / 'docs/heroes' / (uid + '.md')).read_bytes()).hexdigest() for uid in PROFILES},
            'shared_helper_sha256': dependencies(), 'family': 'humanoid_draconic_candidate_v1',
            'rig_contract': 'Frozen 27-bone naming/parent/socket topology; separately calibrated Dragonkin head/neck/shoulder proportions. No compatibility acceptance from matching names.',
            'wings': False, 'tail': False, 'feet': 'plantigrade', 'source_unit': 'meter', 'source_forward': '+Y', 'up': '+Z',
            'export_profile': 'fbx_skeletal_cm_v1.json; temporary independent centimeter copies; unit actor scale in Unreal',
            'heroes': [{**PROFILES[uid], 'id': uid, 'height_m': source_unit(uid)['height_m'],
                        'dossier': 'docs/heroes/' + uid + '.md', 'clips': clip_contract(source_unit(uid))} for uid in PROFILES],
            'calibration_required': [
                'Sora front/side/back/three-quarter and 96px silhouette; closed intentional muzzle, no human face underneath.',
                'New family measured standing height, toe-forward vector, root at ground, unit armature/object scale and unchanged source after normalized export.',
                'Every authored frame: normalized <=4 weights, <=60 bones, no animated scale/root translation, finite transforms, sole/gear floor penetration and two-hand reach.',
                'Visual continuous seven-clip review including muzzle/horn/crest/collar/weapon clearances; numeric bounds are not collision or quality approval.',
                'Fresh Unreal import: +X forward, expected centimeter height, root scale1, all seven clips sampled and played; actual gallery/board/neighbor captures.',
                'Reversible Sora costume revision/reimport preserving skeleton/material/animation references before family acceptance and the remaining three heroes.',
            ]}


@lru_cache(maxsize=1)
def _blender():
    dependencies()
    import bpy
    from mathutils import Vector, Matrix
    from author_alpha import Geometry
    return bpy, Vector, Matrix, Geometry


def build_rig(unit):
    """New in-memory proportions; never edits any shared rig or existing source."""
    bpy, V, _, _ = _blender()
    profile = PROFILES[unit['id']]
    shoulder = profile['shoulder']
    bones = [('root', (0, 0, 0), (0, 0, .1), None),
             ('pelvis', (0, 0, .49), (0, 0, .565), 'root'),
             ('spine_01', (0, 0, .565), (0, 0, .64), 'pelvis'),
             ('spine_02', (0, 0, .64), (0, 0, .71), 'spine_01'),
             ('spine_03', (0, 0, .71), (0, 0, .79), 'spine_02'),
             ('neck', (0, 0, .79), (0, .015, .853), 'spine_03'),
             ('head', (0, .015, .853), (0, .010, .980), 'neck')]
    points = {}
    for side, sign in [('l', 1), ('r', -1)]:
        q = {'sh': (sign * shoulder, 0, .775), 'el': (sign * (shoulder + .08), .008, .615),
             'wrist': (sign * (shoulder + .13), .035, .455), 'hand': (sign * (shoulder + .135), .055, .405),
             'hip': (sign * .085, 0, .49), 'knee': (sign * .085, .006, .27), 'ankle': (sign * .085, 0, .07),
             'toe': (sign * .085, .12, .025)}
        points[side] = q
        bones.extend([(f'clavicle_{side}', (sign * .035, 0, .765), q['sh'], 'spine_03'),
                      (f'upperarm_{side}', q['sh'], q['el'], f'clavicle_{side}'),
                      (f'lowerarm_{side}', q['el'], q['wrist'], f'upperarm_{side}'),
                      (f'hand_{side}', q['wrist'], q['hand'], f'lowerarm_{side}'),
                      (f'thigh_{side}', q['hip'], q['knee'], 'pelvis'),
                      (f'calf_{side}', q['knee'], q['ankle'], f'thigh_{side}'),
                      (f'foot_{side}', q['ankle'], q['toe'], f'calf_{side}'),
                      (f'toe_{side}', q['toe'], (sign * .085, .16, .025), f'foot_{side}')])
    bones.extend([(f'weapon_{side}', points[side]['hand'], (points[side]['hand'][0], .12, .405), f'hand_{side}') for side in ('r', 'l')])
    bones.extend([('cast_origin', (0, .16, .72), (0, .25, .72), 'spine_03'),
                  ('head_ui', (0, 0, 1.025), (0, 0, 1.075), 'head')])
    if bpy.data.objects.get('Armature'):
        raise ValueError('A candidate scene already contains Armature; do not overwrite existing progress')
    data = bpy.data.armatures.new('WC_humanoid_draconic_candidate_v1')
    arm = bpy.data.objects.new('Armature', data)
    bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name, head, tail, parent in bones:
        bone = data.edit_bones.new(name)
        bone.head, bone.tail = V(head) * unit['height_m'], V(tail) * unit['height_m']
        bone.align_roll(V((0, 1, 0)))
        if parent:
            bone.parent = data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    for bone in arm.pose.bones:
        bone.rotation_mode = 'XYZ'
    return arm, points


def head_geometry(g, profile, unit_class):
    """One shaped skull surface includes the muzzle; no buried human head/nose."""
    width, front = profile['head_width'], profile['muzzle_front']
    g.loft([((0, -.003, .782), .057, .052), ((0, .007, .816), .053, .049),
            ((0, .015, .858), .049, .049)], 6, 'neck', 16)
    sections = [(.832, .50, .046, .063), (.850, .73, .055, front * .90),
                (.872, .98, .067, front), (.890, 1., .074, front * .97),
                (.908, 1.01, .078, .104), (.935, .98, .079, .080),
                (.965, .82, .068, .057), (.987, .52, .044, .032), (.998, .08, .010, .010)]
    vertices, faces = [], []
    sides = 24
    for z, radius, back, reach in sections:
        for j in range(sides):
            angle = j * 2 * math.pi / sides
            frontness = math.sin(angle)
            x = width * radius * math.cos(angle)
            y = reach * max(0, frontness) ** .62 if frontness > 0 else back * frontness
            vertices.append((x, y, z))
    faces.append(tuple(reversed(range(sides))))
    for section in range(len(sections) - 1):
        for j in range(sides):
            a = section * sides + j
            b = section * sides + (j + 1) % sides
            faces.append((a, b, b + sides, a + sides))
    faces.append(tuple((len(sections) - 1) * sides + j for j in range(sides)))
    g.add(vertices, faces, 6, 'head')
    # Narrow closed mouth seam follows the same broad muzzle; no visible teeth.
    g.tube([(-width * .53, front * .84, .858), (0, front * .928, .855), (width * .53, front * .84, .858)], [.0023] * 3, 14, 'head', 6)
    for sign in (-1, 1):
        x = sign * width * .61
        g.plate([(x - .017, .916), (x - .007, .923), (x + .011, .922),
                 (x + .019, .916), (x + .009, .910), (x - .010, .911)], .081, .008, 8, 'head')
        g.plate([(x - .006, .913), (x + .006, .913), (x + .006, .920), (x - .006, .920)], .087, .004, 9, 'head')
        g.plate([(x - .002, .913), (x + .002, .913), (x + .002, .920), (x - .002, .920)], .090, .003, 15, 'head')
        g.tube([(x - sign * .022, .082, .929), (x, .086, .931), (x + sign * .020, .073, .925)], [.006, .007, .004], 14, 'head', 7)
        g.ellipsoid((sign * .034, front * .971, .882), (.007, .0025, .004), 14, 'head', 4, 8)
        if unit_class == 'ranger':
            horn = [(sign * .069, -.011, .950), (sign * .096, -.022, .969), (sign * .119, -.054, .970)]
            radii = [.020, .021, .005]
        elif unit_class == 'priest':
            horn = [(sign * .061, -.018, .953), (sign * .080, -.029, .981), (sign * .082, -.065, .988), (sign * .069, -.097, .975)]
            radii = [.021, .019, .012, .006]
        else:
            length = .78 if unit_class == 'rogue' else 1
            horn = [(sign * .065, -.015, .946), (sign * .080, -.050, .966), (sign * .085, -.096 * length, .972)]
            radii = [.020, .014, .005]
        g.tube(horn, radii, 7, 'head', 10, depth=.75)
    if profile['crest']:
        # Short rounded crest sits on the neck; no accessory skeleton or tail.
        for offset, z in enumerate((.914, .883, .853)):
            g.tube([(0, -.057, z), (0, -.085 + offset * .005, z + .013), (0, -.095 + offset * .008, z - .009)],
                   [.012, .014 - offset * .002, .006], 7, 'neck' if offset == 2 else 'head', 8)


def build_geometry(unit, points):
    _, V, _, Geometry = _blender()
    g = Geometry()
    p = PROFILES[unit['id']]
    cls = unit['unit_class']
    waist, sh, radius = p['waist'], p['shoulder'], p['limb']
    g.loft([((0, 0, .476), waist, .080), ((0, 0, .545), waist * 1.05, .087),
            ((0, 0, .62), waist * .92, .082), ((0, -.005, .70), sh * .90, .103),
            ((0, -.005, .76), sh * .88, .108), ((0, 0, .795), .069, .065)], 0, 'spine_02', 20,
           weights=[{'pelvis': 1}, {'pelvis': .8, 'spine_01': .2}, {'spine_01': 1},
                    {'spine_02': 1}, {'spine_03': 1}, {'spine_03': 1}])
    for side, sign in [('l', 1), ('r', -1)]:
        q = points[side]
        g.tube([q['hip'], tuple(V(q['hip']).lerp(V(q['knee']), .5)), q['knee'],
                tuple(V(q['knee']).lerp(V(q['ankle']), .6)), q['ankle']],
               [radius, radius * .95, radius * .76, radius * .68, radius * .62], 3, 'thigh_' + side, 14,
               weights=[{'thigh_' + side: 1}, {'thigh_' + side: 1}, {'thigh_' + side: .5, 'calf_' + side: .5}, {'calf_' + side: 1}, {'calf_' + side: 1}])
        x = q['ankle'][0]
        g.loft([((x, .025, .001), radius * 1.05, .095), ((x, .035, .025), radius * 1.09, .108),
                ((x, .026, .068), radius, .094), ((x, .005, .106), radius * .80, .060),
                ((x, 0, .211), radius * .88, .064)], 0 if cls == 'guardian' else 5, 'calf_' + side, 14,
               weights=[{'foot_' + side: 1}, {'foot_' + side: 1}, {'foot_' + side: 1},
                        {'foot_' + side: .6, 'calf_' + side: .4}, {'calf_' + side: 1}])
        a, b, c = V(q['sh']), V(q['el']), V(q['wrist'])
        g.tube([tuple(a + V((-sign * .022, 0, .012))), tuple(a.lerp(b, .24)), tuple(a.lerp(b, .68)), q['el'], tuple(b.lerp(c, .5)), q['wrist']],
               [radius * .68, radius, radius * .86, radius * .68, radius * .76, radius * .51], 0, 'upperarm_' + side, 16,
               weights=[{'spine_03': .5, 'clavicle_' + side: .5}, {'upperarm_' + side: 1}, {'upperarm_' + side: 1},
                        {'upperarm_' + side: .5, 'lowerarm_' + side: .5}, {'lowerarm_' + side: 1}, {'lowerarm_' + side: 1}])
        palm = V(q['hand'])
        g.tube([q['wrist'], tuple(palm), tuple(palm + V((0, .015, -.020)))], [.026, .035, .028], 6, 'hand_' + side, 10, depth=.72)
        for finger in range(3):
            xx = palm.x + (finger - 1) * .012
            free = cls == 'priest' and side == 'l'
            g.tube([(xx, palm.y + .006, palm.z), (xx, palm.y + (.027 if free else .044), palm.z - (.034 if free else .003)),
                    (xx, palm.y + (.030 if free else .054), palm.z - (.059 if free else .018))], [.011, .009, .006], 6, 'hand_' + side, 7)
        g.tube([tuple(palm + V((-sign * .030, .007, .012))), tuple(palm + V((-sign * .035, .034, .015))), tuple(palm + V((-sign * .012, .046, .009)))], [.014, .011, .008], 6, 'hand_' + side, 7)
    # Tailored closed coat panels: short in front for melee, split ankle-clear robes for Oren.
    hem = .17 if cls == 'priest' else .36 if cls == 'ranger' else .415
    for sign in (-1, 1):
        g.plate([(sign * .014, .544), (sign * waist, .542), (sign * waist * 1.08, hem + .025), (sign * .032, hem)],
                .099, .015, 1 if cls in ('guardian', 'priest') else 0, 'pelvis', .08)
        g.plate([(sign * .014, .550), (sign * waist, .550), (sign * waist * 1.12, hem + .010), (sign * .031, hem)],
                -.097, .015, 1 if cls == 'priest' else 0, 'pelvis', .08)
    g.loft([((0, 0, .539), waist * 1.04, .102), ((0, 0, .563), waist * 1.03, .101)], 5, 'pelvis', 20)
    g.plate([(-.025, .538), (.025, .538), (.025, .565), (-.025, .565)], .108, .013, 10, 'pelvis')
    if cls == 'guardian':
        g.plate([(-.132, .74), (0, .78), (.132, .74), (.107, .62), (-.107, .62)], .11, .029, 0, 'spine_02', .13)
        for side, sign in [('l', 1), ('r', -1)]:
            x, _, z = points[side]['sh']
            g.loft([((x, 0, z - .022), .073, .075), ((x, 0, z + .020), .085, .082), ((x - sign * .008, 0, z + .047), .061, .064)], 0, 'clavicle_' + side, 12)
    elif cls == 'ranger':
        for sign in (-1, 1):
            g.plate([(sign * .044, .785), (sign * .169, .77), (sign * .161, .708), (sign * .076, .706)], -.054, .032, 1, 'spine_03', .13)
            g.plate([(sign * .025, .777), (sign * .142, .740), (sign * .184, .51), (sign * .052, .545)], -.126, .021, 0, 'spine_02', .10)
        g.plate([(-.037, .743), (.037, .743), (.037, .565), (-.037, .565)], -.156, .041, 5, 'spine_02')
    elif cls == 'rogue':
        g.tube([(-.112, .100, .768), (-.048, .120, .683), (.026, .113, .612), (.092, .101, .548)], [.024] * 4, 1, 'spine_02', 8, depth=.30,
               weights=[{'spine_03': 1}, {'spine_02': 1}, {'spine_01': 1}, {'pelvis': 1}])
    else:
        for sign in (-1, 1):
            g.plate([(sign * .047, .790), (sign * .18, .765), (sign * .165, .712), (sign * .065, .735)], -.011, .038, 1, 'spine_03', .13)
            g.tube([(sign * .056, .05, .793), (sign * .141, .034, .774), (sign * .178, .025, .754)], [.010] * 3, 10, 'spine_03', 8)
        g.plate([(.083, .535), (.145, .535), (.143, .444), (.087, .444)], -.016, .062, 5, 'pelvis')
        g.plate([(.096, .516), (.132, .516), (.132, .491), (.096, .491)], .020, .009, 10, 'pelvis')
    head_geometry(g, p, cls)
    equipment_start = len(g.faces)
    equipment_geometry(g, unit, points)
    return g, equipment_start


def equipment_geometry(g, unit, points):
    cls = unit['unit_class']
    if cls == 'guardian':
        x, y, z = points['l']['hand']
        oval = [(x + .133 * math.cos(i * math.tau / 28), z + .085 + .244 * math.sin(i * math.tau / 28)) for i in range(28)]
        g.plate(oval, y + .054, .040, 0, 'weapon_l', .10)
        rim = [(xx, y + .079, zz) for xx, zz in oval] + [(oval[0][0], y + .079, oval[0][1])]
        g.tube(rim, [.011] * len(rim), 10, 'weapon_l', 7)
        g.ellipsoid((x, y + .087, z + .112), (.036, .014, .047), 11, 'weapon_l', 6, 12)
        x, y, z = points['r']['hand']
        g.tube([(x, y, z - .047), (x, y, z + .204)], [.018, .018], 5, 'weapon_r', 10)
        g.loft([((x, y, z + .165), .035, .035), ((x, y, z + .198), .052, .048), ((x, y, z + .236), .039, .037)], 10, 'weapon_r', 10)
    elif cls == 'ranger':
        x, y, z = points['l']['hand']
        g.tube([(x - .055, y, z), (x + .055, y, z)], [.021, .021], 3, 'weapon_l', 10)
        for sign in (-1, 1):
            g.plate([(x + sign * .042, z - .025), (x + sign * .150, z + .012), (x + sign * .272, z + .088),
                     (x + sign * .305, z + .073), (x + sign * .192, z - .024), (x + sign * .070, z - .048)], y, .032, 11, 'weapon_l', .13)
            g.tube([(x + sign * .068, y + .020, z - .027), (x + sign * .178, y + .020, z - .006), (x + sign * .285, y + .020, z + .073)], [.006, .006, .003], 3, 'weapon_l', 7)
        g.tube([(x - .296, y, z + .070), (x, y - .090, z), (x + .296, y, z + .070)], [.003] * 3, 8, 'weapon_l', 6)
    elif cls == 'rogue':
        for side, sign in [('l', 1), ('r', -1)]:
            x, y, z = points[side]['hand']
            g.tube([(x, y, z - .05), (x, y, z + .080)], [.016, .016], 5, 'weapon_' + side, 10)
            outer = [(x + sign * (.075 + .104 * math.cos(a)), z + .146 + .140 * math.sin(a)) for a in [i * math.pi / 12 - math.pi / 2 for i in range(13)]]
            inner = [(x + sign * (.057 + .062 * math.cos(a)), z + .146 + .101 * math.sin(a)) for a in [i * math.pi / 12 - math.pi / 2 for i in range(12, -1, -1)]]
            g.plate(outer + inner, y, .023, 4, 'weapon_' + side, .065)
            g.ellipsoid((x + sign * .051, y + .015, z + .119), (.016, .006, .020), 11, 'weapon_' + side, 5, 10)
    else:
        x, y, z = points['r']['hand']
        g.tube([(x, y, z - .31), (x, y, z + .420)], [.017, .017], 5, 'weapon_r', 10)
        center = (x, y, z + .435)
        hexagon = [(center[0] + .080 * math.cos(i * math.tau / 6 + math.pi / 6), y, center[2] + .094 * math.sin(i * math.tau / 6 + math.pi / 6)) for i in range(7)]
        g.tube(hexagon, [.014] * 7, 10, 'weapon_r', 8)
        g.ellipsoid((x, y, center[2]), (.023, .019, .035), 11, 'weapon_r', 6, 10)


def smooth(value):
    value = max(0., min(1., value))
    return value * value * (3 - 2 * value)


def apply_pose(unit, arm, clip, frame, end, release):
    """One original in-place pose; returns actual analytic hand reach clamp in meters."""
    bpy, V, M, _ = _blender()
    from hand_contacts import place_hand
    cls, h = unit['unit_class'], unit['height_m']
    t = (frame - 1) / end
    wave, pulse = math.sin(t * math.tau), math.sin(t * math.pi)
    for bone in arm.pose.bones:
        bone.rotation_euler = (0, 0, 0)
        bone.location = (0, 0, 0)
        bone.scale = (1, 1, 1)

    def rot(name, x=0, y=0, z=0):
        arm.pose.bones[name].rotation_euler = tuple(math.radians(value) for value in (x, y, z))

    def envelope(values):
        times = [1, max(2, release // 2), release, min(end + 1, release + 9), end + 1]
        for index in range(1, len(times)):
            if frame <= times[index]:
                f = smooth((frame - times[index - 1]) / max(1, times[index] - times[index - 1]))
                return values[index - 1] * (1 - f) + values[index] * f
        return values[-1]

    active = envelope([0, 1, 1, .4, 0]) if clip == 'Active' else 0
    attack = envelope([0, 1, 1, .3, 0]) if clip == 'Attack' else 0
    kneel = smooth(t / .8) if clip == 'Defeat' else 0
    victory = pulse if clip == 'Victory' else 0
    if clip == 'Idle':
        rot('spine_02', .55 * wave)
        rot('head', 0, .8 * wave)
    if cls == 'rogue':
        rot('spine_02', 5 + 4 * active)
    if clip == 'Move':
        amplitude = 16 if cls == 'guardian' else 22 if cls == 'rogue' else 19
        for side, sign in [('l', 1), ('r', -1)]:
            swing = amplitude * sign * wave
            bend = max(0, -sign * wave) * 18
            rot('thigh_' + side, swing)
            rot('calf_' + side, -bend)
            rot('foot_' + side, -swing + bend)
        arm.pose.bones['pelvis'].location.y = -.42 * (1 - math.cos(math.radians(amplitude * wave))) * h
    if clip == 'Hit':
        rot('spine_02', -8 * pulse)
        rot('head', 6 * pulse)
    if kneel:
        rot('spine_01', 22 * kneel)
        rot('head', 14 * kneel)
        for side in ('l', 'r'):
            rot('thigh_' + side, 32 * kneel)
            rot('calf_' + side, -55 * kneel)
            rot('foot_' + side, 23 * kneel)
        arm.pose.bones['pelvis'].location.y = ((.49 - .27) * math.cos(math.radians(32 * kneel)) + (.27 - .07) * math.cos(math.radians(23 * kneel)) - .42) * h
    bpy.context.view_layer.update()
    spine = arm.pose.bones['spine_02']
    body = spine.matrix @ spine.bone.matrix_local.inverted()
    turn = body.to_3x3()

    def hand(side, point, angle=0, yaw=0):
        position = V(point) * h
        if kneel:
            position.z -= .07 * kneel * h
        return place_hand(arm, side, body @ position,
                          turn @ M.Rotation(math.radians(yaw), 3, 'Z') @ M.Rotation(math.radians(angle), 3, 'X'), h)

    if cls == 'guardian':
        return max(hand('l', (.24, .15 + .035 * active, .55 + .08 * active - .04 * kneel), -8 - 24 * active),
                   hand('r', (-.23, .14 + .08 * attack, .54 + .07 * attack + .09 * victory - .04 * kneel), -25 - 40 * attack))
    if cls == 'ranger':
        ready = max(active, attack)
        left = (.11, .16 + .055 * ready, .56 + .090 * ready - .08 * kneel)
        clamp = hand('l', left, -10 - 8 * active, -4 * active)
        # Right draw target is derived from the actual transformed bow hand.
        driver = arm.pose.bones['hand_l']
        pull = envelope([.030, .105, .032, .03, .03]) if clip in ('Attack', 'Active') else .030
        target = driver.matrix @ driver.bone.matrix_local.inverted() @ (driver.bone.tail_local + V((-.04, -pull, .005)) * h)
        return max(clamp, place_hand(arm, 'r', target, turn, h))
    if cls == 'rogue':
        draw = envelope([0, -.04, .07, .025, 0]) if clip in ('Attack', 'Active') else 0
        return max(hand('l', (.22 - .025 * attack, .12 - .03 * attack, .53 + .025 * attack - .05 * kneel), -24 + 16 * attack),
                   hand('r', (-.22 + .07 * active, .13 + draw, .53 + .045 * active + .04 * victory - .05 * kneel), -25 - 30 * active - 22 * attack))
    return max(hand('r', (-.225, .12 + .055 * active, .51 + .055 * active + .025 * attack - .055 * kneel), -4 - 10 * active),
               hand('l', (.20 - .035 * active, .10 + .14 * active, .48 + .17 * active + .045 * attack + .05 * victory - .04 * kneel), -12 - 32 * active))


def bake_actions(unit, arm):
    """Candidate actions only; no export or source save. Review every resulting frame."""
    bpy, _, _, _ = _blender()
    clips = clip_contract(unit)
    for clip, spec in clips.items():
        name = 'AN_' + unit['id'] + '_' + clip
        if bpy.data.actions.get(name):
            raise ValueError('Refusing to replace an existing action: ' + name)
        arm.animation_data_clear()
        previous, reach = {}, 0.
        for frame in range(1, spec['frames'][1] + 1):
            bpy.context.scene.frame_set(frame)
            reach = max(reach, apply_pose(unit, arm, clip, frame, spec['frames'][1] - 1, spec['release_frame'] or 1))
            for bone in arm.pose.bones:
                bone.rotation_euler = bone.rotation_euler.to_quaternion().to_euler('XYZ', previous.get(bone.name, bone.rotation_euler))
                previous[bone.name] = bone.rotation_euler.copy()
                bone.keyframe_insert(data_path='rotation_euler', frame=frame, group=bone.name)
                bone.keyframe_insert(data_path='location', frame=frame, group=bone.name)
        action = arm.animation_data.action
        action.name, action.use_fake_user = name, True
        spec['action'] = name
        spec['sampled_frames'] = spec['frames'][1]
        spec['maximum_reach_clamp_m'] = reach
        if reach > .025:
            raise RuntimeError(f'{clip} hand reach clamp {reach:.6f}m exceeds the measured helper tolerance')
    return clips


def inspect_family(unit, arm, mesh):
    """Structural measurements only; deliberately cannot declare visual acceptance."""
    bpy, V, _, _ = _blender()
    bpy.context.view_layer.update()
    required = {'root', 'pelvis', 'spine_01', 'spine_02', 'spine_03', 'neck', 'head',
                'weapon_l', 'weapon_r', 'cast_origin', 'head_ui'}
    missing = sorted(required - set(arm.data.bones.keys()))
    weights = [{group.group: group.weight for group in vertex.groups if group.weight > .00001} for vertex in mesh.data.vertices]
    bad_weights = [index for index, row in enumerate(weights) if not row or len(row) > 4 or abs(sum(row.values()) - 1) > .0001]
    mesh.data.calc_loop_triangles()
    bounds = [mesh.matrix_world @ vertex.co for vertex in mesh.data.vertices]
    axes = {'foot_to_toe_m': list(arm.data.bones['toe_l'].head_local - arm.data.bones['foot_l'].head_local),
            'root_head_m': list(arm.data.bones['root'].head_local)}
    result = {'status': 'MEASURED_STRUCTURE_ONLY', 'unit': unit['id'], 'bones': len(arm.data.bones),
              'missing_bones': missing, 'bad_weight_vertices': bad_weights, 'triangles': len(mesh.data.loop_triangles),
              'materials': len(mesh.data.materials), 'rest_bounds_m': {'minimum': [min(v[i] for v in bounds) for i in range(3)],
              'maximum': [max(v[i] for v in bounds) for i in range(3)]}, 'axes': axes,
              'object_scale': list(mesh.scale), 'armature_scale': list(arm.scale), 'fps': bpy.context.scene.render.fps,
              'visual_clearances': {item: 'NOT_REVIEWED' for item in PROFILES[unit['id']]['clearances']}}
    if missing or bad_weights or len(arm.data.bones) > 60 or len(mesh.data.loop_triangles) > 15000:
        raise RuntimeError(json.dumps(result))
    if any(abs(value - 1) > 1e-6 for value in (*arm.scale, *mesh.scale)) or V(axes['root_head_m']).length > 1e-6:
        raise RuntimeError('Unexpected root origin or source object scale')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--describe', action='store_true', required=True, help='Print preparation only; never create a scene or export')
    parser.parse_args()
    print(json.dumps(preparation_contract(), indent=2))
