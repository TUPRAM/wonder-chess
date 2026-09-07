"""Author the seven original Wonder Chess neutral creatures in a real Blender process.

Uses the project's measured centimeter-copy FBX exporter and mesh construction
utilities read-only. Mechanical rigs, silhouettes and motion are creature-specific.
Outputs are authoring evidence; Unreal import and continuous acceptance remain separate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import runpy
import sys

import bpy
from mathutils import Euler, Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from author_alpha import Geometry, make_mesh, material_for, export_fbx, export_lods, setup_render

PALETTES = {
    'sprout': ['#58894D','#304F39','#99B865','#BC995B','#CDA768','#604C37','#B7C788','#283831','#F6E3AE','#172B27','#DFC07F','#D2F4B0','#7A613E','#E0C884','#42633E','#748F50'],
    'thorn': ['#7D8050','#3E5545','#A5A876','#957144','#C6AC74','#59462F','#A1B790','#333F35','#EFE2B8','#1B3029','#D7C086','#CDE4C1','#6D5E3F','#DA9C65','#5D7148','#A58A5A'],
    'wisp': ['#294F69','#142B42','#5D8290','#B4C5BA','#CCA55F','#515C66','#9DE1DC','#223B50','#E1F5D1','#12303C','#E3C778','#AAFAE0','#7194A0','#ACC8B9','#58717A','#D5E6D1'],
    'stoneback': ['#657A74','#324A4A','#93A096','#ADAF97','#B8A56E','#48514A','#8C9986','#3B4F47','#E8DDB6','#203835','#CBB87D','#A4DCC6','#79856D','#D4C7A1','#46645B','#B8BCAE'],
    'prowler': ['#397E88','#203D55','#679C9D','#ABC5BB','#C6AF78','#345064','#82C8C0','#253C4E','#DDF2D0','#132A39','#E0C891','#9DF0D6','#517480','#B2DAC4','#437D80','#B9E1D4'],
    'sentinel': ['#506980','#24384E','#8B9EAA','#A1A99C','#C9A761','#695746','#AEBDAE','#2F4154','#F0DDB0','#1E3045','#E1C783','#ADE5DC','#7E8B8F','#DCCDA8','#42596B','#BCC9BC'],
    'warden': ['#435F76','#203246','#8C9B9E','#A8B4A7','#CAB17D','#605A50','#B7DACA','#314755','#EAE7C7','#132B3F','#E3CB94','#B4F5DE','#768C99','#E4DBC0','#526B78','#BECEBD'],
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--creature', default='all')
    parser.add_argument('--report-dir', type=Path, required=True)
    parser.add_argument('--skip-motion-render', action='store_true')
    parser.add_argument('--revision', type=int, default=1)
    return parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])


def rig(bone_specs):
    data = bpy.data.armatures.new('WC_NeutralMechanical_v1')
    arm = bpy.data.objects.new('Armature', data)
    bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name, point, parent in [('root',(0,0,0),None)] + bone_specs:
        bone = data.edit_bones.new(name)
        bone.head = point
        bone.tail = Vector(point) + Vector((0,0,.10))
        if parent:
            bone.parent = data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    for bone in arm.pose.bones:
        bone.rotation_mode = 'QUATERNION'
    return arm


def leaf(g, origin, tip, width, color, bone):
    """Thick folded leaf blade with an actual raised central vein and back surface."""
    o, t = Vector(origin), Vector(tip)
    middle = o.lerp(t,.52)
    side = Vector((width,0,0))
    front = Vector((0,.045,0))
    vertices = [tuple(o),tuple(middle-side),tuple(t),tuple(middle+side),tuple(middle+front),tuple(middle-front*.35)]
    g.add(vertices,[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(1,0,5),(2,1,5),(3,2,5),(0,3,5)],color,bone)
    g.tube([o+front*.1,middle+front*1.04,t],[.012,.014,.002],3,bone,6)


def face(g, center, width, bone='head', metal=False):
    x,y,z = center
    for sign in (-1,1):
        eye = x + sign*width*.42
        g.plate([(eye-.055,z-.026),(eye+.052,z-.026),(eye+.06,z+.034),(eye-.045,z+.047)],y,.027,9,bone)
        g.plate([(eye-.023,z-.016),(eye+.024,z-.016),(eye+.024,z+.024),(eye-.023,z+.024)],y+.019,.009,11 if metal else 8,bone)
        g.tube([(eye-sign*.064,y+.01,z+.071),(eye,y+.033,z+.092),(eye+sign*.055,y+.018,z+.08)],[.018,.025,.014],4 if metal else 1,bone,6)
    g.tube([(x-width*.17,y+.028,z-.09),(x,y+.044,z-.104),(x+width*.17,y+.028,z-.09)],[.011,.012,.011],9,bone,6)


def root_feet(g, count=2, radius=.28, y=.02):
    specs=[]
    for i in range(count):
        x=(-1 if i%2==0 else 1)*radius
        yy=y if count==2 else (-.36 if i<2 else .37)
        bone=f'leg_{i}'
        specs.append((bone,(x,yy,.3),'root'))
        if count==4:
            g.tube([(x*.40,yy*.40,.43),(x*.75,yy*.78,.43),(x,yy,.38)],
                   [.12,.11,.105],5,bone,10)
        g.tube([(x,yy,.38),(x*1.10,yy+.035,.17),(x*1.15,yy+.12,.07)],[.105,.11,.10],5,bone,10)
        for offset in (-1,0,1):
            g.tube([(x*1.15,yy+.10,.075),(x*1.15+offset*.09,yy+.24,.025),
                    (x*1.15+offset*.10,yy+.30,.016)],[.055,.044,.018],3,bone,8)
    return specs


def plant(kind):
    g=Geometry()
    feet=root_feet(g,2 if kind=='sprout' else 4,.23 if kind=='sprout' else .30)
    top=.85 if kind=='sprout' else .68
    g.loft([((0,0,.23),.20,.18),((0,0,.35),.36,.28),((0,-.035,.56),.35,.29),
            ((0,-.02,top-.08),.24,.21),((0,0,top),.12,.11)],0,'body',20)
    # Raised seams and a broad face make the seed shell a deliberate character.
    g.tube([(-.18,.22,.30),(-.29,.25,.48),(-.20,.21,top-.04)],[.018,.020,.014],2,'body',7)
    g.tube([(.18,.22,.30),(.29,.25,.48),(.20,.21,top-.04)],[.018,.020,.014],2,'body',7)
    face(g,(0,.282,.58 if kind=='sprout' else .46),.29,'body')
    for side,sign in [('l',-1),('r',1)]:
        leaf(g,(sign*.13,-.03,.58),(sign*.56,-.04,.91 if kind=='sprout' else .64),.17,2,'petal_'+side)
        leaf(g,(sign*.10,-.18,.53),(sign*.34,-.35,.84 if kind=='sprout' else .69),.12,1,'body')
    specs=[('body',(0,0,.36),'root'),('head',(0,0,.57),'body'),
           ('petal_l',(-.17,0,.58),'body'),('petal_r',(.17,0,.58),'body')]+feet
    if kind=='sprout':
        leaf(g,(0,0,.77),(.06,.02,1.04),.12,2,'head')
        cast=(0,.38,.55); height=1.07
    else:
        g.tube([(0,-.19,.53),(0,-.30,.88),(0,-.20,1.13),(0,.08,1.25),(0,.44,1.12)],
               [.16,.145,.12,.11,.105],1,'launcher',16)
        g.tube([(0,.44,1.12),(0,.51,1.12)],[.14,.14],3,'launcher',14)
        g.ellipsoid((0,.526,1.12),(.088,.012,.088),9,'launcher',6,12)
        for sign in (-1,1):
            leaf(g,(sign*.055,-.18,.89),(sign*.31,-.16,1.2),.1,2,'launcher')
        specs.append(('launcher',(0,-.20,.53),'body'))
        cast=(0,.57,1.12);height=1.31
    specs += [('cast_origin',cast,'body' if kind=='sprout' else 'launcher'),('head_ui',(0,0,height),'root')]
    return g,specs,height


def lantern():
    g=Geometry()
    g.loft([((0,0,.34),.15,.15),((0,0,.48),.27,.24),((0,0,.89),.25,.23),((0,0,1.02),.16,.16)],
           11,'core',12)
    for z,rad in ((.37,.24),(.95,.26)):
        g.loft([((0,0,z-.045),rad*.9,rad*.9),((0,0,z),rad,rad),((0,0,z+.045),rad*.9,rad*.9)],4,'body',12)
    for i in range(6):
        a=i*math.tau/6
        x,y=.26*math.cos(a),.26*math.sin(a)
        g.tube([(x*.65,y*.65,.33),(x,y,.49),(x,y,.85),(x*.65,y*.65,1.0)], [.034]*4,0,'body',8)
    g.loft([((0,0,.99),.23,.23),((0,0,1.11),.08,.08),((0,0,1.15),.035,.035)],0,'crown',12)
    g.ring((0,0,1.15),.12,.027,4,'crown',steps=20)
    face(g,(0,.277,.72),.24,'core',True)
    for sign in (-1,1):
        g.ring((sign*.36,0,.72),.13,.019,4,'orbit_'+('l' if sign<0 else 'r'),steps=16)
        g.ellipsoid((sign*.40,.035,.8),(.05,.045,.055),11,'orbit_'+('l' if sign<0 else 'r'),5,10)
    for sign in (-1,1):
        g.tube([(sign*.11,0,.34),(sign*.08,.03,.23),(sign*.17,.08,.20)],[.025,.021,.006],4,'body',7)
    return g,[('body',(0,0,.64),'root'),('core',(0,0,.7),'body'),('head',(0,0,.9),'body'),
              ('crown',(0,0,1.0),'body'),('orbit_l',(-.22,0,.7),'body'),('orbit_r',(.22,0,.7),'body'),
              ('cast_origin',(0,.31,.72),'core'),('head_ui',(0,0,1.33),'root')],1.34


def stoneback():
    g=Geometry();specs=[('body',(0,0,.45),'root'),('head',(0,.49,.46),'body'),
                       ('shell_l',(-.17,0,.60),'body'),('shell_r',(.17,0,.60),'body')]
    g.loft([((0,-.06,.28),.47,.58),((0,-.06,.54),.58,.65),((0,-.08,.71),.46,.51)],1,'body',20)
    # Tessellated shell panels separated by dark recessed seams.
    for band in range(3):
        r0=band/3; r1=(band+1)/3
        sectors=12
        for i in range(sectors):
            a0=(i+.035)*math.tau/sectors;a1=(i+.965)*math.tau/sectors
            def point(r,a):return (math.cos(a)*.73*r, -.1+math.sin(a)*.82*r, .69+.43*math.sqrt(max(0,1-r*r)))
            verts=[point(r0+.018,a0),point(r1-.018,a0),point(r1-.018,a1),point(r0+.018,a1)]
            g.add(verts,[(0,1,2,3)],2 if (i+band)%3 else 3,'shell_l' if math.cos((a0+a1)/2)<0 else 'shell_r')
    g.loft([((0,-.1,.63),.76,.84),((0,-.1,.69),.76,.84),((0,-.1,.73),.72,.8)],4,'body',24)
    g.loft([((0,.63,.32),.22,.26),((0,.67,.45),.29,.31),((0,.65,.58),.24,.26),((0,.63,.65),.15,.15)],2,'head',16)
    face(g,(0,.946,.49),.31,'head')
    for i,(x,y) in enumerate([(-.51,-.51),(.51,-.51),(-.51,.43),(.51,.43)]):
        bone=f'leg_{i}';specs.append((bone,(x,y,.34),'root'))
        g.tube([(x*.87,y*.88,.43),(x,y,.26),(x,y+.06,.12)],[.14,.17,.15],2,bone,12)
        g.loft([((x,y+.09,.016),.17,.23),((x,y+.09,.065),.19,.24),((x,y+.04,.15),.15,.17)],1,bone,12)
        for dx in (-.075,0,.075):g.tube([(x+dx,y+.22,.08),(x+dx,y+.31,.025)],[.025,.012],3,bone,6)
    g.tube([(0,-.62,.4),(0,-.91,.29),(0,-1.01,.21)],[.12,.06,.009],2,'body',10)
    specs += [('cast_origin',(0,.35,1.07),'body'),('head_ui',(0,0,1.17),'root')]
    return g,specs,1.2


def prowler():
    g=Geometry();specs=[('body',(0,-.03,.65),'root'),('head',(0,.57,.83),'body'),('jaw',(0,.73,.76),'head'),
                       ('tail',(0,-.60,.73),'body')]
    # Continuous low feline torso, raised shoulder and tapered rump.
    g.tube([(0,-.64,.67),(0,-.37,.73),(0,.0,.68),(0,.35,.76),(0,.52,.84)],
           [.22,.30,.245,.31,.23],0,'body',20,depth=1.08)
    g.loft([((0,.59,.68),.17,.15),((0,.63,.81),.27,.23),((0,.58,.99),.23,.19),((0,.55,1.09),.13,.13)],2,'head',18)
    g.ellipsoid((0,.85,.78),(.18,.19,.11),6,'jaw',8,16)
    g.plate([(-.063,.83),(.063,.83),(.05,.77),(0,.75),(-.05,.77)],1.025,.025,9,'head')
    for sign in (-1,1):
        g.plate([(sign*.10,1.02),(sign*.20,1.29),(sign*.28,1.02)],.57,.10,1,'head')
        g.plate([(sign*.14,1.04),(sign*.20,1.21),(sign*.24,1.04)],.632,.018,11,'head')
    face(g,(0,.831,.94),.35,'head',True)
    for i,(x,y) in enumerate([(-.22,-.48),(.22,-.48),(-.23,.39),(.23,.39)]):
        bone=f'leg_{i}';specs.append((bone,(x,y,.61),'root'))
        g.tube([(x,y,.63),(x*1.25,y-.055,.37),(x*1.15,y+.025,.16),(x*1.15,y+.12,.08)],
               [.13,.10,.065,.095],0,bone,14)
        g.loft([((x*1.15,y+.15,.016),.105,.165),((x*1.15,y+.15,.07),.115,.17),((x*1.15,y+.10,.13),.08,.115)],6,bone,12)
        for dx in (-.057,0,.057):g.tube([(x*1.15+dx,y+.23,.064),(x*1.15+dx,y+.30,.025)],[.023,.009],8,bone,6)
        g.tube([(x*1.23,y,.46),(x*1.18,y+.061,.22)],[.018,.012],11,bone,6)
    g.tube([(0,-.59,.75),(.12,-.82,.81),(.20,-1.03,.96),(.12,-1.18,1.12),(-.02,-1.15,1.23)],
           [.095,.078,.052,.035,.005],1,'tail',12)
    for sign in (-1,1):
        g.tube([(sign*.20,.4,.91),(sign*.27,.05,.87),(sign*.20,-.40,.91)],[.022,.020,.013],11,'body',7)
    specs += [('cast_origin',(0,.98,.82),'head'),('head_ui',(0,.3,1.37),'root')]
    return g,specs,1.4


def sentinel():
    g=Geometry();specs=[('body',(0,0,.79),'root'),('head',(0,0,1.28),'body'),
                       ('bell',(0,0,1.28),'body'),('clapper',(0,0,.95),'bell')]
    # Standing carved bell, shoulder yoke and articulated supports are one designed construct.
    g.loft([((0,0,.62),.53,.36),((0,0,.69),.55,.38),((0,0,.8),.43,.30),
            ((0,0,1.12),.28,.22),((0,0,1.36),.21,.17)],4,'bell',20)
    for z,rad,depth in ((.65,.55,.38),(.85,.42,.30),(1.32,.24,.20)):
        g.loft([((0,0,z-.025),rad,depth),((0,0,z+.025),rad,depth)],10,'bell',20)
    for sign in (-1,1):
        g.tube([(sign*.47,-.05,.77),(sign*.51,-.03,1.32),(sign*.31,0,1.56),(0,0,1.62)],
               [.10,.105,.11,.085],0,'body',10)
        g.plate([(sign*.45,1.31),(sign*.63,1.43),(sign*.59,1.56),(sign*.38,1.5)],.07,.12,2,'body')
    g.tube([(0,0,1.61),(0,0,1.28)],[.05,.05],1,'body',12)
    g.ring((0,.065,1.37),.075,.025,10,'body',steps=16)
    g.tube([(0,0,.95),(0,0,.60)],[.037,.043],1,'clapper',10)
    g.ellipsoid((0,.02,.55),(.10,.10,.115),10,'clapper',8,12)
    face(g,(0,.30,1.03),.29,'bell',True)
    for sign in (-1,1):
        x=sign*.31;bone='leg_'+str(0 if sign<0 else 1);specs.append((bone,(x,0,.45),'root'))
        g.tube([(x,0,.63),(x,-.01,.35),(x,.025,.15)],[.105,.11,.083],2,bone,12)
        g.ring((x,.095,.36),.093,.025,4,bone,steps=16)
        g.loft([((x,.10,.016),.16,.23),((x,.10,.085),.175,.235),((x,.045,.17),.105,.14)],0,bone,12)
    specs += [('cast_origin',(0,0,.6),'bell'),('head_ui',(0,0,1.75),'root')]
    return g,specs,1.78


def warden():
    g=Geometry();specs=[('body',(0,0,.70),'root'),('head',(0,0,1.36),'body'),
                       ('crown',(0,0,1.56),'body'),('panel_l',(-.26,0,1.10),'body'),('panel_r',(.26,0,1.10),'body')]
    g.loft([((0,0,.35),.48,.43),((0,0,.54),.52,.46),((0,0,.84),.32,.29),
            ((0,0,1.16),.40,.34),((0,0,1.48),.31,.29),((0,0,1.57),.24,.22)],0,'body',12)
    for i,(x,y) in enumerate([(-.36,-.26),(.36,-.26),(-.36,.26),(.36,.26)]):
        bone=f'leg_{i}';specs.append((bone,(x,y,.35),'root'))
        g.tube([(x*.70,y*.70,.50),(x,y,.28),(x*1.22,y*1.28,.12)],[.12,.14,.16],2,bone,10)
        g.loft([((x*1.22,y*1.28+.06,.016),.16,.20),((x*1.22,y*1.28+.06,.10),.17,.20),((x*1.15,y*1.2,.18),.13,.13)],1,bone,10)
    for side,sign in [('l',-1),('r',1)]:
        polygon=[(sign*.16,.87),(sign*.48,.88),(sign*.57,1.22),(sign*.45,1.52),(sign*.20,1.43)]
        g.plate(polygon,.12,.28,2,'panel_'+side)
        g.tube([(sign*.26,.286,.95),(sign*.39,.286,1.20),(sign*.31,.286,1.43)],[.021,.023,.017],10,'panel_'+side,7)
    # Aperture: dark recess, thick hexagonal rim and opaque central energy lens.
    g.plate([(-.23,.96),(.23,.96),(.30,1.11),(.23,1.29),(-.23,1.29),(-.30,1.11)],.365,.055,9,'body')
    g.ring((0,.408,1.12),.235,.043,4,'body',steps=6)
    g.plate([(-.09,1.00),(.09,1.00),(.15,1.12),(.09,1.23),(-.09,1.23),(-.15,1.12)],.422,.055,11,'body')
    face(g,(0,.295,1.43),.26,'head',True)
    for i in range(5):
        angle=i*math.tau/5
        x,y=.25*math.cos(angle),.25*math.sin(angle)
        g.loft([((x,y,1.52),.083,.083),((x*1.13,y*1.13,1.74),.074,.074),((x*1.17,y*1.17,1.92),.005,.005)],
               4 if i%2 else 2,'crown',6)
    g.loft([((0,0,1.53),.12,.12),((0,0,1.73),.10,.10),((0,0,1.83),.007,.007)],11,'crown',6)
    specs += [('cast_origin',(0,.48,1.12),'body'),('head_ui',(0,0,2.03),'root')]
    return g,specs,2.06


def pose_rotation(bone, x=0, y=0, z=0):
    basis=bone.bone.matrix_local.to_quaternion()
    value=Euler(tuple(math.radians(a) for a in (x,y,z)),'XYZ').to_quaternion()
    bone.rotation_quaternion=basis.inverted() @ value @ basis


def pose_translation(bone, delta):
    bone.location=bone.bone.matrix_local.to_3x3().inverted() @ Vector(delta)


def animate(creature, kind, arm, out):
    clips={}
    lengths={'Idle':120,'Move':60,'Attack':max(42,round(creature['stats']['attack_windup_ms']*.06)+27),'Hit':24,'Defeat':60}
    if creature['ability']:
        lengths['Active']=max(36,round((creature['ability']['cast_ms']+creature['ability']['recovery_ms'])*.06))
    for clip,end in lengths.items():
        arm.animation_data_clear()
        release=1+round((creature['ability']['cast_ms'] if clip=='Active' else creature['stats']['attack_windup_ms'])*.06) if clip in ('Active','Attack') else 0
        frames=sorted(set(range(1,end+2,3))|{end+1}|({release} if release else set()))
        for frame in frames:
            t=(frame-1)/end;wave=math.sin(t*math.tau)
            for bone in arm.pose.bones:
                bone.rotation_quaternion=(1,0,0,0);bone.location=(0,0,0);bone.scale=(1,1,1)
            body=arm.pose.bones['body']
            def rotate(name,*angles):
                if name in arm.pose.bones:pose_rotation(arm.pose.bones[name],*angles)
            if clip=='Idle':
                pose_translation(body,(0,0,(.025 if kind=='wisp' else .007)*wave))
                rotate('head',0,0,wave*2)
                rotate('tail',0,wave*4,wave*4)
                rotate('petal_l',wave*2,0,wave*3);rotate('petal_r',-wave*2,0,-wave*3)
                rotate('orbit_l',0,wave*9,wave*4);rotate('orbit_r',0,-wave*9,-wave*4)
            elif clip=='Move':
                for i in range(4):
                    phase=t*math.tau+(math.pi if i in (1,2) else 0)
                    lift=max(0,math.sin(phase))
                    rotate('leg_'+str(i),lift*(17 if kind=='prowler' else 10),0,0)
                pose_translation(body,(0,0,abs(wave)*(.018 if kind!='wisp' else .04)))
                rotate('head',wave*2,0,0);rotate('tail',0,wave*10,0)
                rotate('petal_l',wave*7,0,0);rotate('petal_r',-wave*7,0,0)
            elif clip in ('Attack','Active'):
                progress=(frame-1)/max(1,release-1)
                anticip=frame<release
                strength=math.sin(min(1,progress)*math.pi/2) if anticip else max(0,1-(frame-release)/(end+1-release))
                signed=(-1 if anticip else 1)*strength
                if kind=='sprout':
                    rotate('petal_l',-signed*38,0,signed*18);rotate('petal_r',signed*26,0,-signed*15)
                    rotate('head',signed*8,0,0)
                elif kind=='thorn':rotate('launcher',signed*15,0,0)
                elif kind=='wisp':
                    rotate('crown',0,0,signed*20);rotate('orbit_l',0,signed*25,0);rotate('orbit_r',0,-signed*25,0)
                    pose_translation(arm.pose.bones['core'],(0,.035*max(0,signed),0))
                elif kind=='stoneback':
                    rotate('head',signed*12,0,0)
                    if clip=='Active':
                        rotate('shell_l',0,-strength*9,0);rotate('shell_r',0,strength*9,0)
                    else:pose_translation(arm.pose.bones['head'],(0,max(0,signed)*.10,0))
                elif kind=='prowler':
                    rotate('head',signed*13,0,0);rotate('jaw',strength*9,0,0)
                    rotate('tail',0,signed*13,0)
                    if clip=='Active':pose_translation(body,(0,0,-.13*strength))
                    else:pose_translation(body,(0,max(0,signed)*.06,0))
                elif kind=='sentinel':
                    rotate('bell',signed*(18 if clip=='Active' else 10),0,0)
                    rotate('clapper',-signed*26,0,0)
                elif kind=='warden':
                    rotate('crown',0,0,signed*18)
                    rotate('panel_l',0,-strength*10,0);rotate('panel_r',0,strength*10,0)
            elif clip=='Hit':
                bump=math.sin(t*math.pi);rotate('head',-bump*8,0,0)
                pose_translation(body,(0,-bump*.035,0))
            elif clip=='Defeat':
                amount=min(1,t*1.5)
                pose_translation(body,(0,0,-amount*(.18 if kind=='wisp' else .12)))
                rotate('head',amount*13,0,0);rotate('petal_l',amount*34,0,0);rotate('petal_r',amount*34,0,0)
                rotate('launcher',amount*22,0,0);rotate('bell',amount*8,0,0)
            for bone in arm.pose.bones:
                bone.keyframe_insert('rotation_quaternion',frame=frame,group=bone.name)
                bone.keyframe_insert('location',frame=frame,group=bone.name)
        action=arm.animation_data.action;action.name=f'AN_{creature["id"]}_{clip}';action.use_fake_user=True
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for key in curve.keyframe_points:key.interpolation='LINEAR'
        bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=end+1;bpy.context.scene.frame_set(1)
        export_fbx(out/f'{action.name}.fbx',[arm],True)
        clips[clip]={'action':action.name,'frames':[1,end+1],'release_frame':release,'fps':60,'loop':clip in ('Idle','Move')}
    return clips


def audit_motion(arm,mesh,clips,kind,report):
    records=[];errors=[]
    for clip,spec in clips.items():
        action=bpy.data.actions[spec['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
        minz=999;maxz=-999;root_drift=0;scale_error=0;minimum_height=999
        for frame in range(spec['frames'][0],spec['frames'][1]+1):
            bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
            evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());data=evaluated.to_mesh()
            values=[(evaluated.matrix_world@vertex.co).z for vertex in data.vertices]
            low=min(values);high=max(values);minz=min(minz,low);maxz=max(maxz,high);minimum_height=min(minimum_height,high-low)
            evaluated.to_mesh_clear()
            root_drift=max(root_drift,arm.pose.bones['root'].location.length)
            scale_error=max(scale_error,max(abs(v-1) for bone in arm.pose.bones for v in bone.scale))
        if minz<-.025:errors.append(f'{clip}: geometry penetrates floor {minz:.5f}m')
        if root_drift>1e-6 or scale_error>1e-6:errors.append(f'{clip}: root/scale invariant failed')
        records.append({'clip':clip,'frames_evaluated':spec['frames'][1],'minimum_z_m':minz,'maximum_z_m':maxz,
                        'minimum_height_m':minimum_height,'root_translation_max_m':root_drift,'scale_error_max':scale_error})
    payload={'status':'FAILED' if errors else 'PASS_ALL_FRAME_STRUCTURAL_MOTION','kind':kind,'clips':records,'errors':errors,
             'limits':['All-frame mesh evaluation is not continuous visual approval.','Floating Wisp has an intentionally airborne opaque lantern body.','Engine import/contact/FX synchronization remains unverified.']}
    (report/'motion-invariants.json').write_text(json.dumps(payload,indent=2)+'\n')
    if errors:raise RuntimeError('; '.join(errors))


def render_motion(arm,clips,report):
    scene=bpy.context.scene
    scene.render.engine='BLENDER_WORKBENCH'
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='TEXTURE'
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.render.resolution_x=384;scene.render.resolution_y=384
    scene.render.image_settings.media_type='VIDEO'
    scene.render.image_settings.file_format='FFMPEG';scene.render.image_settings.color_mode='RGB'
    scene.render.ffmpeg.format='MPEG4';scene.render.ffmpeg.codec='H264';scene.render.ffmpeg.constant_rate_factor='MEDIUM'
    for clip,spec in clips.items():
        action=bpy.data.actions[spec['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
        scene.frame_start=spec['frames'][0];scene.frame_end=spec['frames'][1]
        scene.render.filepath=str(report/f'continuous_{clip}.mp4')
        bpy.ops.render.render(animation=True)
    scene.render.image_settings.media_type='IMAGE'
    scene.render.image_settings.file_format='PNG';scene.render.engine='CYCLES'


def frame_camera(camera,mesh,height,location):
    """Fit the real creature bounds, including wide shells and long tails."""
    camera.location=location
    camera.rotation_euler=(Vector((0,0,height*.5))-camera.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()
    inverse=camera.matrix_world.inverted()
    projected=[inverse @ (mesh.matrix_world @ Vector(corner)) for corner in mesh.bound_box]
    camera.data.ortho_scale=max(abs(co[axis])*2 for co in projected for axis in (0,1))*1.10


def author(creature,opt):
    uid=creature['id'];kind=uid.removeprefix('wc_n_')
    out=ROOT/'exports/neutrals'/uid;source=ROOT/'art-source/neutrals'/uid;report=opt.report_dir.resolve()/uid
    for directory in (out,source,report):directory.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.fps=60
    for name in ('BODY','COSTUME','EQUIPMENT','RIG','PRESENTATION_HELPERS','EXPORT'):
        collection=bpy.data.collections.new(name);scene.collection.children.link(collection)
    g,specs,height=plant(kind) if kind in ('sprout','thorn') else {'wisp':lantern,'stoneback':stoneback,'prowler':prowler,'sentinel':sentinel,'warden':warden}[kind]()
    arm=rig(specs)
    texture_input={'id':uid,'art':{'palette':' '.join(PALETTES[kind])}}
    material=material_for(texture_input,out)
    for node in material.node_tree.nodes:
        if node.type=='TEX_IMAGE' and node.image and node.image.name.endswith('BaseColor'):
            material.node_tree.nodes.active=node
    mesh=make_mesh(g,{'id':uid,'height_m':1},arm,material)
    for ob in (arm,mesh):
        for collection in list(ob.users_collection):collection.objects.unlink(ob)
        bpy.data.collections['EXPORT'].objects.link(ob)
    bpy.data.collections['RIG'].objects.link(arm)
    export_fbx(out/f'SK_{uid}.fbx',[arm,mesh],False)
    lods=export_lods({'id':uid},mesh,arm,out)
    clips=animate(creature,kind,arm,out)
    audit_motion(arm,mesh,clips,kind,report)
    action=bpy.data.actions[clips['Idle']['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
    scene.frame_set(1);camera=setup_render(height)
    frame_camera(camera,mesh,height,tuple(camera.location))
    scene.render.resolution_x=640;scene.render.resolution_y=640;scene.cycles.samples=20
    scene.render.filepath=str(out/'portrait.png');bpy.ops.render.render(write_still=True)
    for label,location in [('front',(0,height*3.1,height*1.35)),('side',(height*3.1,0,height*1.35)),('back',(0,-height*3.1,height*1.35))]:
        frame_camera(camera,mesh,height,location)
        scene.render.resolution_x=448;scene.render.resolution_y=448;scene.render.filepath=str(report/f'{label}.png');bpy.ops.render.render(write_still=True)
    frame_camera(camera,mesh,height,(height*1.65,height*3.1,height*1.65))
    camera.data.ortho_scale*=1.10
    if not opt.skip_motion_render:render_motion(arm,clips,report)
    action=bpy.data.actions[clips['Idle']['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
    scene.frame_start=1;scene.frame_end=121;scene.frame_set(1);scene.render.resolution_x=640;scene.render.resolution_y=640
    bpy.ops.wm.save_as_mainfile(filepath=str(source/f'{uid}.blend'))
    mesh.data.calc_loop_triangles()
    manifest={'status':'AUTHORED_EXPORTED_BLENDER_EXECUTED_ENGINE_AND_VISUAL_ACCEPTANCE_OPEN','unit_id':uid,'name':creature['display_name'],
              'blender_version':bpy.app.version_string,'source_revision':opt.revision,'rig_family':'neutral_'+kind+'_mechanical_v1',
              'rig_bones':[bone.name for bone in arm.data.bones],'bones':len(arm.data.bones),'height_m':height,
              'measured_rest_dimensions_m':list(mesh.dimensions),'triangles':len(mesh.data.loop_triangles),'materials':1,'fps':60,
              'source_forward':'+Y','source_up':'+Z','source_unit_scale_m':1,'fbx_profile':'tools/blender/profiles/fbx_skeletal_cm_v1.json',
              'source_sha256':hashlib.sha256((source/f'{uid}.blend').read_bytes()).hexdigest(),
              'author_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'canonical_source_sha256':hashlib.sha256((ROOT/'data/neutrals.json').read_bytes()).hexdigest(),
              'textures':{'BaseColor':'sRGB','Normal':'linear tangent +Y flat normal; geometry provides bevels','ORM':'linear R=AO G=roughness B=metallic'},
              'clips':clips,'lods':lods,'continuous_recordings':not opt.skip_motion_render,
              'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.name!='export_manifest.json'},
              'review_path':str(report),'open_reviews':['Unreal scale/facing/import','normal-speed continuous visual acceptance','LOD silhouettes in game','effects/audio release alignment','actual crowded gameplay']}
    (out/'export_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    old=sys.argv
    try:
        sys.argv=['inspect_scene.py','--','--collection','EXPORT','--output',str(report/'structural.json'),'--require-skin']
        runpy.run_path(str(ROOT/'tools/blender/inspect_scene.py'),run_name='__main__')
    finally:sys.argv=old
    print('WC_NEUTRAL_AUTHORED '+uid+' '+json.dumps({'triangles':manifest['triangles'],'clips':len(clips),'report':str(report)}),flush=True)


if __name__=='__main__':
    options=parse_args()
    creatures=json.loads((ROOT/'data/neutrals.json').read_text(encoding='utf-8'))['creatures']
    chosen=[c for c in creatures if options.creature in ('all',c['id'],c['id'].removeprefix('wc_n_'))]
    if not chosen:raise ValueError('Unknown authored neutral')
    for creature in chosen:author(creature,options)
