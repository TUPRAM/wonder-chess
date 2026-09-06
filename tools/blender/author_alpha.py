"""Original Wonder Chess authored mesh/rig/animation production, executed in Blender.

Constructs tailored lofts and beveled polygon equipment from the canonical alpha
briefs. Geometry and animation are editable in the saved source. Render and
structural evidence do not imply Unreal acceptance.
"""
from __future__ import annotations
import argparse
import array
import hashlib
import json
import math
from pathlib import Path
import re
import sys

import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUTHOR_SCRIPT_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
sys.path.insert(0,str(Path(__file__).resolve().parent))
PI = math.pi


def args():
    p = argparse.ArgumentParser()
    p.add_argument('--hero', default='wc_u_human_guardian')
    p.add_argument('--all', action='store_true')
    p.add_argument('--exclude', nargs='*', default=[])
    p.add_argument('--revision', type=int, default=1)
    p.add_argument('--skip-render', action='store_true')
    return p.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])


def rgb(value):
    return tuple(int(value[i:i+2], 16)/255 for i in (1,3,5))


class Geometry:
    def __init__(self):
        self.vertices, self.faces, self.colors, self.weights = [], [], [], []

    def add(self, vertices, faces, color, bone='spine_02', weights=None):
        start = len(self.vertices)
        self.vertices.extend(vertices)
        self.faces.extend(tuple(start+i for i in face) for face in faces)
        self.colors.extend([color]*len(faces))
        self.weights.extend(weights or [{bone: 1.0} for _ in vertices])

    def loft(self, sections, color, bone='spine_02', sides=12, weights=None):
        # Sections are sculpted elliptical cross-sections (center, width, depth).
        vs=[]
        for center, rx, ry in sections:
            for j in range(sides):
                a=2*PI*j/sides
                vs.append((center[0]+rx*math.cos(a), center[1]+ry*math.sin(a),center[2]))
        fs=[tuple(reversed(range(sides)))]
        for k in range(len(sections)-1):
            for j in range(sides):
                a=k*sides+j; b=k*sides+(j+1)%sides
                fs.append((a,b,b+sides,a+sides))
        fs.append(tuple((len(sections)-1)*sides+j for j in range(sides)))
        ws=[weights[k] for k in range(len(sections)) for _ in range(sides)] if weights else None
        self.add(vs,fs,color,bone,ws)

    def tube(self, points, radii, color, bone='spine_02', sides=8, weights=None, depth=1):
        vs=[]
        for k,p in enumerate(points):
            tangent=Vector(points[min(k+1,len(points)-1)])-Vector(points[max(k-1,0)])
            tangent.normalize()
            ref=Vector((0,1,0))
            if abs(tangent.dot(ref))>.9: ref=Vector((1,0,0))
            a=tangent.cross(ref).normalized(); b=tangent.cross(a).normalized()
            for j in range(sides):
                v=Vector(p)+radii[k]*(math.cos(j*2*PI/sides)*a+depth*math.sin(j*2*PI/sides)*b)
                vs.append(tuple(v))
        fs=[tuple(reversed(range(sides)))]
        for k in range(len(points)-1):
            for j in range(sides):
                q=k*sides+j; r=k*sides+(j+1)%sides
                fs.append((q,r,r+sides,q+sides))
        fs.append(tuple((len(points)-1)*sides+j for j in range(sides)))
        ws=[weights[k] for k in range(len(points)) for _ in range(sides)] if weights else None
        self.add(vs,fs,color,bone,ws)

    def ellipsoid(self, center, scale, color, bone='head', rings=8,sides=12):
        sections=[]
        for j in range(rings+1):
            a=-PI/2+PI*j/rings
            sections.append(((center[0],center[1],center[2]+scale[2]*math.sin(a)),max(.001,scale[0]*math.cos(a)),max(.001,scale[1]*math.cos(a))))
        self.loft(sections,color,bone,sides)

    def plate(self, polygon, y, depth, color,bone='spine_02',bevel=.08):
        # Polygon in X/Z plane; four boundary rings form bevels and a solid back.
        cx=sum(p[0] for p in polygon)/len(polygon); cz=sum(p[1] for p in polygon)/len(polygon)
        vs=[]
        for sy,f in [(y-depth/2,1-bevel),(y-depth/2+.007,1),(y+depth/2-.007,1),(y+depth/2,1-bevel)]:
            vs.extend((cx+(x-cx)*f,sy,cz+(z-cz)*f) for x,z in polygon)
        n=len(polygon); fs=[tuple(reversed(range(n))),tuple(3*n+i for i in range(n))]
        for k in range(3):
            for i in range(n): fs.append((k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i))
        self.add(vs,fs,color,bone)

    def ring(self, center, radius, thickness,color,bone='head',start=0,end=2*PI, steps=24):
        pts=[(center[0]+math.cos(start+(end-start)*i/steps)*radius,center[1],center[2]+math.sin(start+(end-start)*i/steps)*radius) for i in range(steps+1)]
        self.tube(pts,[thickness]*(steps+1),color,bone,6)


def material_for(unit,out):
    palette=re.findall(r'#[0-9A-Fa-f]{6}',unit['art']['palette'])
    skin={'wc_u_human_guardian':'#96644B','wc_u_human_priest':'#B8946A','wc_u_human_mage':'#AD7955',
          'wc_u_elf_ranger':'#B58C5E','wc_u_elf_priest':'#694535','wc_u_elf_rogue':'#BB936D',
          'wc_u_dwarf_guardian':'#BA8869','wc_u_dwarf_ranger':'#A27254','wc_u_dwarf_warrior':'#704834',
          'wc_u_orc_warrior':'#6E8260','wc_u_orc_mage':'#859C81','wc_u_orc_rogue':'#708D72'}.get(unit['id'],'#96644B')
    hair={'wc_u_human_priest':'#613C31','wc_u_elf_ranger':'#907858','wc_u_elf_priest':'#D3D6D8',
          'wc_u_dwarf_guardian':'#76533A','wc_u_dwarf_ranger':'#AD613B'}.get(unit['id'],'#302E33')
    colors=(palette+['#B6C3CC','#72533C',skin,hair,'#F4EBDD','#272C38','#DFB557','#7ECEE1','#E9A463','#625A64','#AA7C60','#E5D5B8'])[:16]
    while len(colors)<16: colors.append('#808080')
    if unit['id']=='wc_u_human_mage':colors[10]='#A98451'
    size=1024
    buffers=[array.array('f',[0.0])*(size*size*4) for _ in range(3)]
    for y in range(size):
        for x in range(size):
            idx=(y//256)*4+x//256; c=rgb(colors[idx]); k=(y*size+x)*4
            # Sparse broad weave and gentle tonal shaping; atlas UVs stay in swatches.
            shade=.91+.09*(y%256)/255 + (.006 if (x+y)%9<3 else 0)
            buffers[0][k:k+4]=array.array('f',[c[0]*shade,c[1]*shade,c[2]*shade,1])
            buffers[1][k:k+4]=array.array('f',[.5,.5,1,1])
            metal=1 if idx in (4,10) else 0
            buffers[2][k:k+4]=array.array('f',[1,.36 if metal else .72,metal,1])
    images=[]
    for suffix,pixels in zip(('BaseColor','Normal','ORM'),buffers):
        canonical_name=f'T_{unit["id"]}_{suffix}'
        im=bpy.data.images.new(canonical_name,width=size,height=size)
        if suffix!='BaseColor': im.colorspace_settings.name='Non-Color'
        im.pixels.foreach_set(pixels); im.filepath_raw=str(out/f'{canonical_name}.png');im.file_format='PNG';im.save()
        # Load the written PNG as a file texture so Blender renders the same sRGB
        # decoding as Unreal, instead of retaining generated-image pixel semantics.
        file_path=im.filepath_raw;image_name=im.name;bpy.data.images.remove(im)
        loaded=bpy.data.images.load(file_path,check_existing=False);loaded.name=image_name
        loaded.colorspace_settings.name='sRGB' if suffix=='BaseColor' else 'Non-Color'
        images.append(loaded)
    mat=bpy.data.materials.new(f'M_{unit["id"]}');mat.use_nodes=True
    nodes=mat.node_tree.nodes; links=mat.node_tree.links; bsdf=nodes.get('Principled BSDF')
    for im in images:
        node=nodes.new('ShaderNodeTexImage');node.image=im
        if im==images[0]: links.new(node.outputs['Color'],bsdf.inputs['Base Color'])
        elif im==images[1]:
            normal=nodes.new('ShaderNodeNormalMap');links.new(node.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bsdf.inputs['Normal'])
        else:
            split=nodes.new('ShaderNodeSeparateColor');links.new(node.outputs['Color'],split.inputs['Color'])
            links.new(split.outputs['Green'],bsdf.inputs['Roughness']);links.new(split.outputs['Blue'],bsdf.inputs['Metallic'])
    return mat


def rig_for(unit):
    race=unit['race']; cls=unit['unit_class']; dwarf=race=='dwarf'; broad=race=='orc'
    shoulder=.235 if broad else (.235 if dwarf else .185)
    if cls=='rogue': shoulder*=.89
    if race=='elf': shoulder=.16
    hip=.43 if dwarf else .49; knee=.235 if dwarf else .27
    zshoulder=.755 if dwarf else .775
    bones=[('root',(0,0,0),(0,0,.1),None),('pelvis',(0,0,hip),(0,0,hip+.075),'root'),
           ('spine_01',(0,0,hip+.075),(0,0,.64),'pelvis'),('spine_02',(0,0,.64),(0,0,.71),'spine_01'),
           ('spine_03',(0,0,.71),(0,0,.79),'spine_02'),('neck',(0,0,.79),(0,0,.85),'spine_03'),
           ('head',(0,0,.85),(0,0,.985),'neck')]
    points={}
    for side,s in [('l',1),('r',-1)]:
        sh=(s*shoulder,0,zshoulder); el=(s*(shoulder+.08),.008,.615 if not dwarf else .58)
        wrist=(s*(shoulder+.13),.035,.455 if not dwarf else .43)
        hand=(s*(shoulder+.135),.055,.405 if not dwarf else .375)
        hip_p=(s*(.11 if dwarf else .085),0,hip); knee_p=(hip_p[0],.006,knee);ankle=(hip_p[0],0,.07);toe=(hip_p[0],.12,.025)
        bones.extend([(f'clavicle_{side}',(s*.035,0,.765),sh,'spine_03'),(f'upperarm_{side}',sh,el,f'clavicle_{side}'),
                      (f'lowerarm_{side}',el,wrist,f'upperarm_{side}'),(f'hand_{side}',wrist,hand,f'lowerarm_{side}'),
                      (f'thigh_{side}',hip_p,knee_p,'pelvis'),(f'calf_{side}',knee_p,ankle,f'thigh_{side}'),
                      (f'foot_{side}',ankle,toe,f'calf_{side}'),(f'toe_{side}',toe,(toe[0],.16,.025),f'foot_{side}')])
        points[side]={'sh':sh,'el':el,'wrist':wrist,'hand':hand,'hip':hip_p,'knee':knee_p,'ankle':ankle}
    bones.extend([('weapon_r',points['r']['hand'],(points['r']['hand'][0],.12,points['r']['hand'][2]),'hand_r'),
                  ('weapon_l',points['l']['hand'],(points['l']['hand'][0],.12,points['l']['hand'][2]),'hand_l'),
                  ('cast_origin',(0,.16,.72),(0,.25,.72),'spine_03'),('head_ui',(0,0,1.025),(0,0,1.075),'head')])
    arm_data=bpy.data.armatures.new('WC_'+unit['rig_family']+'_v1');arm=bpy.data.objects.new('Armature',arm_data)
    bpy.context.collection.objects.link(arm);bpy.context.view_layer.objects.active=arm;arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    h=unit['height_m']
    for name,a,b,parent in bones:
        eb=arm_data.edit_bones.new(name);eb.head=Vector(a)*h;eb.tail=Vector(b)*h
        eb.align_roll(Vector((0,1,0)))
        if parent: eb.parent=arm_data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    for b in arm.pose.bones: b.rotation_mode='XYZ'
    return arm,points


def body_geometry(unit,p,revision):
    g=Geometry(); race=unit['race'];cls=unit['unit_class'];uid=unit['id'];dwarf=race=='dwarf';orc=race=='orc'
    sh=abs(p['l']['sh'][0]);hip=p['l']['hip'][2]
    width=.155 if dwarf else (.155 if orc else .125)
    if race=='elf':width=.108
    if cls=='rogue': width*=.82
    # Smoothly changing tailored torso and continuous flexible trousers.
    torso=[((0,0,hip-.025),width,.09),((0,0,hip+.035),width*1.05,.095),((0,0,.60),width*.85,.078),
           ((0,0,.67),width*1.10,.11),((0,0,.735),sh*.84,.105),((0,0,.785),sh*.63,.075)]
    cloth=0 if uid!='wc_u_human_guardian' else 1
    g.loft(torso,cloth,'spine_02',16,weights=[{'pelvis':1},{'pelvis':.8,'spine_01':.2},{'spine_01':1},{'spine_02':1},{'spine_03':1},{'spine_03':1}])
    for side in ('l','r'):
        s=1 if side=='l' else -1; q=p[side]
        leg_r=.075 if dwarf else (.068 if orc else (.046 if race=='elf' else .055))
        g.tube([q['hip'],(q['hip'][0],0,(hip+q['knee'][2])/2),q['knee'],(q['ankle'][0],0,.14),q['ankle']],
               [leg_r,leg_r*.9,leg_r*.75,leg_r*.66,leg_r*.6],1 if uid=='wc_u_human_guardian' else 3,f'thigh_{side}',12,
               weights=[{f'thigh_{side}':1},{f'thigh_{side}':1},{f'thigh_{side}':.5,f'calf_{side}':.5},{f'calf_{side}':1},{f'calf_{side}':1}])
        # Sculpted boot toe, ankle, flared cuff; base exactly on ground.
        x=q['ankle'][0]; br=leg_r*1.12
        g.loft([((x,.035,.009),br,.10),((x,.038,.035),br,.108),((x,.028,.075),br*.94,.095),
                ((x,0,.115),br*.78,.06),((x,0,.205),br*.90,.065),((x,0,.22),br,.068)],5,f'calf_{side}',12,
                weights=[{f'foot_{side}':1},{f'foot_{side}':1},{f'foot_{side}':1},{f'foot_{side}':.5,f'calf_{side}':.5},{f'calf_{side}':1},{f'calf_{side}':1}])
        g.loft([((x,0,.206),br*1.02,.07),((x,0,.225),br*1.02,.07)],2,f'calf_{side}')
        arm_r=.074 if dwarf else (.075 if orc else (.044 if race=='elf' else .052))
        g.tube([q['sh'],tuple(Vector(q['sh']).lerp(Vector(q['el']),.25)),tuple(Vector(q['sh']).lerp(Vector(q['el']),.65)),q['el'],
                tuple(Vector(q['el']).lerp(Vector(q['wrist']),.25)),tuple(Vector(q['el']).lerp(Vector(q['wrist']),.7)),q['wrist']],
               [arm_r*.92,arm_r,arm_r*.83,arm_r*.67,arm_r*.82,arm_r*.67,arm_r*.51],cloth,f'upperarm_{side}',16,
               weights=[{f'upperarm_{side}':1},{f'upperarm_{side}':1},{f'upperarm_{side}':1},{f'upperarm_{side}':.5,f'lowerarm_{side}':.5},{f'lowerarm_{side}':1},{f'lowerarm_{side}':1},{f'lowerarm_{side}':1}])
        seam_a=Vector(q['sh']).lerp(Vector(q['el']),.22)+Vector((0,arm_r*.88,0))
        seam_b=Vector(q['sh']).lerp(Vector(q['el']),.65)+Vector((0,arm_r*.73,0))
        g.tube([seam_a,seam_b],[.003,.003],cloth,f'upperarm_{side}',5)
        g.tube([tuple(Vector(q['el']).lerp(Vector(q['wrist']),.45)),tuple(Vector(q['el']).lerp(Vector(q['wrist']),.7)),q['wrist']],
               [arm_r*.91,arm_r*.88,arm_r*.72],4 if cls in ('guardian','warrior') else 2,f'lowerarm_{side}',10)
        hc=Vector(q['hand']);hc.z+=.013
        g.ellipsoid(hc,(arm_r*.69,.039,.046),6,f'hand_{side}',6,10)
        g.ellipsoid((hc.x-s*.027,hc.y+.018,hc.z+.012),(.018,.027,.023),6,f'hand_{side}',4,8)
    # Belt wraps around torso as one purpose-built ring.
    g.loft([((0,0,hip+.053),width*1.05,.099),((0,0,hip+.085),width*1.01,.101)],5,'pelvis',16)
    g.plate([(-.033,hip+.052),(.033,hip+.052),(.033,hip+.086),(-.033,hip+.086)],.11,.017,4 if uid=='wc_u_human_guardian' else 10,'pelvis')
    # Anatomical neck and deliberately shaped jaw/cheek/brow planes.
    g.loft([((0,0,.785),.051,.047),((0,0,.84),.054,.05)],6,'neck')
    headwidth=.101 if dwarf else (.10 if orc else .079)
    g.loft([((0,.018,.828),headwidth*.53,.040),((0,.018,.846),headwidth*.76,.058),
            ((0,.015,.875),headwidth,.071),((0,.006,.913),headwidth,.076),((0,-.002,.95),headwidth*.92,.071),
            ((0,-.006,.982),headwidth*.58,.052),((0,-.008,.99),.025,.025)],6,'head',16)
    # Nose is a small shaped wedge, eyes are inset dark planes with warm whites.
    g.add([(-.017,.077,.906),(.017,.077,.906),(-.020,.104,.876),(.020,.104,.876),(0,.112,.886)],[(0,1,4),(0,4,2),(1,3,4),(2,4,3),(0,2,3,1)],14,'head')
    for s in (-1,1):
        ex=s*headwidth*.45
        def eye_surface(x,z,offset):
            return (x,.008+.075*math.sqrt(max(.01,1-(x/headwidth)**2))+offset,z)
        g.add([eye_surface(ex-.015,.908,.0012),eye_surface(ex-.006,.914,.0012),
               eye_surface(ex+.011,.913,.0012),eye_surface(ex+.016,.908,.0012),eye_surface(ex+.004,.903,.0012),eye_surface(ex-.008,.904,.0012)],
              [(0,1,2,3,4,5)],8,'head')
        g.add([eye_surface(ex-.004,.913,.0021),eye_surface(ex+.005,.913,.0021),eye_surface(ex+.005,.904,.0021),eye_surface(ex-.004,.904,.0021)],
              [(0,1,2,3)],9,'head')
        g.tube([(ex-s*.021,.08,.926),(ex,.085,.931),(ex+s*.021,.076,.927)],[.006,.007,.004],7,'head',5)
        if race=='elf':
            g.plate([(s*headwidth*.86,.928),(s*(headwidth+.075),.955),(s*(headwidth+.042),.886),(s*headwidth,.883)],-.004,.022,6,'head')
        else: g.ellipsoid((s*headwidth,.007,.892),(.018,.024,.031),6,'head',5,8)
        if orc:
            g.tube([(s*.032,.085,.85),(s*.034,.105,.874),(s*.030,.108,.890)],[.014,.009,.001],8,'head',7)
    g.tube([(-.029,.079,.855),(0,.088,.852),(.029,.079,.855)],[.003,.004,.003],14,'head',5)
    # Hair is formed from broad swept locks, distinct for each brief.
    hair_vertices=[];hair_faces=[];hair_sides=24
    for k,(radius,z) in enumerate(((1,.925),(.97,.958),(.77,.982),(.43,.997),(.04,1.004))):
        for j in range(hair_sides):
            angle=j*2*PI/hair_sides
            hz=z+(.025*max(0,math.sin(angle))+.005*math.cos(angle) if k==0 else 0)
            hair_vertices.append((headwidth*radius*math.cos(angle),-.014+.078*radius*math.sin(angle),hz))
    for k in range(4):
        for j in range(hair_sides):hair_faces.append((k*hair_sides+j,k*hair_sides+(j+1)%hair_sides,(k+1)*hair_sides+(j+1)%hair_sides,(k+1)*hair_sides+j))
    hair_faces.append(tuple(4*hair_sides+j for j in range(hair_sides)))
    g.add(hair_vertices,hair_faces,7,'head')
    if uid in ('wc_u_human_mage','wc_u_elf_rogue','wc_u_orc_rogue','wc_u_dwarf_ranger'):
        for j in range(4):
            x=(j-1.5)*headwidth*.43
            g.tube([(x,.025,.972),(x-.008,.055,.965),(x-.025,.064,.943)],[.014,.012,.002],7,'head',8)
    if uid in ('wc_u_human_guardian','wc_u_dwarf_warrior','wc_u_orc_mage'):
        count=3 if uid=='wc_u_orc_mage' else 1
        for i in range(count):
            x=(i-(count-1)/2)*.043
            for strand in range(3):
                pts=[]
                for j in range(17):
                    a=j*.9+strand*2*PI/3
                    if uid=='wc_u_dwarf_warrior':
                        around=j*2*PI/16;radius=.044+.006*math.cos(a)
                        pts.append((radius*math.cos(around),-.088+.006*math.sin(a),.934+radius*math.sin(around)))
                    else:pts.append((x+.010*math.cos(a),-.079-.0018*j+.010*math.sin(a),.934-.008*j))
                g.tube(pts,[.008-(.003*j/16) for j in range(17)],7,'head',7)
        g.ring((0,-.114,.835),.015,.005,2,'head',steps=10)
    if uid=='wc_u_human_priest':
        g.ellipsoid((0,-.085,.963),(.052,.04,.039),7,'head',7,12)
        g.tube([(-.078,.018,.943),(0,.075,.965),(.078,.018,.943)],[.012,.012,.012],2,'head',6)
    if uid=='wc_u_orc_warrior':
        g.tube([(0,-.025,.986),(0,-.028,1.035),(0,-.064,1.043)],[.028,.023,.012],7,'head',8)
    if uid=='wc_u_elf_priest':
        for strand in range(2):
            pts=[]
            for j in range(49):
                a=j*2*PI/48;wave=a*9+strand*PI
                pts.append(((.082+.005*math.sin(wave))*math.cos(a),(.068+.005*math.sin(wave))*math.sin(a),.96+.006*math.cos(wave)))
            g.tube(pts,[.0068]*49,7,'head',7)
    if uid=='wc_u_elf_ranger':
        for j in range(3):g.tube([(0,-.07,.952),((j-1)*.039,-.12,.943),((j-1)*.055,-.16,.959)],[.025,.02,.004],7,'head',7)
    if uid=='wc_u_dwarf_guardian':
        for s in (-1,1):
            g.tube([(s*.04,.049,.87),(s*.046,.084,.80),(s*.054,.055,.72)],[.045,.035,.014],7,'head',10)
            g.loft([((s*.052,.06,.735),.017,.021),((s*.052,.06,.75),.018,.022)],2,'head',8)
        g.loft([((0,-.012,.936),.109,.082),((0,-.012,.965),.104,.08),((0,-.02,.996),.071,.06),((0,-.02,1.011),.02,.02)],0,'head',16)
        g.tube([(-.11,.005,.937),(0,.08,.952),(.11,.005,.937)],[.011,.011,.011],2,'head',8)
    if uid=='wc_u_human_mage':
        for s in (-1,1):g.ring((s*.039,.091,.909),.025,.006,10,'head',steps=20)
        g.tube([(-.01,.091,.909),(.01,.091,.909)],[.005,.005],10,'head',6)
    if uid=='wc_u_dwarf_ranger':
        rim=[(.065*math.cos(i*2*PI/28),.092,.966+.032*math.sin(i*2*PI/28)) for i in range(29)]
        g.tube(rim,[.008]*len(rim),2,'head',8)
        g.plate([(.056*math.cos(i*2*PI/20),.966+.024*math.sin(i*2*PI/20)) for i in range(20)],.09,.01,9,'head')
        g.tube([(-.09,.014,.95),(-.075,.075,.966),(.075,.075,.966),(.09,.014,.95)],[.007]*4,5,'head',6)
    # Tailored skirt/tabard panels, short and separated to preserve readable legs.
    skirtlow=(.18 if uid=='wc_u_orc_mage' else .37) if not dwarf else .31
    for s in (-1,1):
        col=0 if uid!='wc_u_human_guardian' else 0
        if uid=='wc_u_dwarf_warrior': col=2
        lower_width=width+(.076 if cls=='priest' else .042)
        polygon=[(s*.012,hip+.047),(s*(width+.012),hip+.05),(s*lower_width,skirtlow+.04),(s*(lower_width-.016),skirtlow+.004),(s*.03,skirtlow),(s*.018,skirtlow+.025)]
        if uid=='wc_u_orc_mage':polygon=[(s*.018,hip+.047),(s*(width+.012),hip+.05),(s*(width+.055),.24),(s*.12,skirtlow),(s*.055,.29)]
        g.plate(polygon,.10,.025,col,'pelvis')
        if cls in ('priest','mage') or uid=='wc_u_elf_ranger':
            low=.18 if uid=='wc_u_orc_mage' else skirtlow
            g.plate([(s*.008,hip+.04),(s*(width+.02),hip+.06),(s*(width+.07),low+.02),(s*.015,low-.025)],-.089,.018,0,'pelvis')
    if cls in ('guardian','warrior'):
        for side in ('l','r'):
            s=1 if side=='l' else -1; q=p[side]['sh']
            if uid=='wc_u_dwarf_warrior' and s==-1: continue
            g.loft([((q[0],q[1],q[2]-.035),.083,.078),((q[0],q[1],q[2]+.019),.095,.086),((q[0],q[1],q[2]+.043),.058,.064)],4 if uid!='wc_u_dwarf_guardian' else 0,f'clavicle_{side}',8)
    if uid=='wc_u_human_guardian':
        g.plate([(-.13,.73),(0,.768),(.13,.73),(.10,.62),(0,.603),(-.10,.62)],.112,.035,4)
        # Two restrained gold fasteners, source revision raises their spacing.
        for s in (-1,1):g.ellipsoid((s*.104,.139,.723),(.01,.007,.01),10,'spine_03',4,8)
        for s in (-1,1):g.tube([(s*.1,-.105,.76),(-s*.1,-.098,.57)],[.014,.014],0,'spine_02',5)
    if uid in ('wc_u_human_priest','wc_u_orc_warrior','wc_u_orc_mage','wc_u_elf_priest'):
        mantlecol=1 if uid in ('wc_u_human_priest','wc_u_orc_mage','wc_u_elf_priest') else 0
        for s in (-1,1):
            g.plate([(s*.032,.79),(s*sh,.81),(s*(sh+.075),.701),(s*(sh+.036),.67),(s*.045,.738)],.008,.18,mantlecol,'spine_03')
    if cls=='rogue':
        g.plate([(.035,.803),(.18,.80),(.26,.66),(.12,.61),(.035,.73)],-.001,.17,0,'spine_03')
        g.tube([(-.08,.033,.798),(0,.065,.812),(.08,.02,.802),(.055,-.065,.788),(-.06,-.065,.79)], [.028]*5,1,'neck',8)
        g.plate([(-.04,.77),(-.13,.85),(-.20,.81),(-.09,.72)],-.09,.025,1,'spine_03')
    if uid=='wc_u_human_mage':
        for s in (-1,1):g.plate([(s*.035,.758),(s*.055,.85),(s*.138,.828),(s*.13,.71)],.025,.145,0,'spine_03')
        g.plate([(-.06,.77),(.06,.77),(.05,.58),(-.05,.58)],.118,.012,1)
    if uid=='wc_u_elf_ranger':
        for i in range(3):
            x=(i-1)*.085;g.plate([(x-.049,.75),(x+.049,.75),(x+.063,.51),(x,.405),(x-.064,.51)],-.10,.02,0,'spine_02')
        g.tube([(-.05,.06,.79),(.025,.077,.80),(.13,-.07,.77)],[.025,.025,.025],1,'neck',7)
    # Broad diagonal straps and flat purposeful cases in dossier positions.
    if uid in ('wc_u_human_priest','wc_u_dwarf_ranger','wc_u_elf_rogue','wc_u_orc_rogue'):
        g.tube([(-.1,.12,.755),(.12,.12,.53)],[.017,.017],2,'spine_02',5)
        x=.17 if uid=='wc_u_human_priest' else 0;y=.022 if uid=='wc_u_human_priest' else -.132
        z=.49 if uid=='wc_u_human_priest' else (.54 if uid=='wc_u_orc_rogue' else .65)
        g.plate([(x-.065,z-.064),(x+.065,z-.064),(x+.065,z+.055),(x-.065,z+.055)],y,.054,5,'pelvis' if uid=='wc_u_human_priest' else 'spine_02')
        for s in (-1,1):g.plate([(x+s*.037-.01,z+.001),(x+s*.037+.01,z+.001),(x+s*.037+.01,z+.023),(x+s*.037-.01,z+.023)],y+.035,.01,10,'pelvis' if uid=='wc_u_human_priest' else 'spine_02')
    return g


def equipment(g,u,p):
    uid=u['id'];cls=u['unit_class'];r=p['r']['hand'];l=p['l']['hand']
    def blade(hand,bone,curved=False):
        x,y,z=hand
        g.tube([(x,y,z-.055),(x,y,z+.06)],[.018,.018],5,bone,8)
        g.plate([(x-.06,z+.04),(x+.06,z+.04),(x+.063,z+.067),(x-.063,z+.067)],y,.036,4 if uid=='wc_u_human_guardian' else 10,bone)
        poly=[(x-.032,z+.068),(x+.03,z+.068),(x+.027,z+.29),(x,z+.365),(x-.028,z+.28)]
        if curved:poly=[(x-.027,z+.065),(x+.025,z+.065),(x+.06,z+.205),(x+.03,z+.295),(x-.025,z+.23),(x-.045,z+.16)]
        g.plate(poly,y,.024,4,bone)
    if uid=='wc_u_human_guardian':
        blade(r,'hand_r');x,y,z=l
        shield=[(x-.16,z+.26),(x-.09,z+.34),(x+.085,z+.33),(x+.17,z+.24),(x+.135,z-.08),(x,z-.24),(x-.14,z-.08)]
        g.plate(shield,y+.12,.065,4,'hand_l')
        g.tube([(x-.04,y+.09,z+.04),(x-.06,y+.05,z),(x+.03,y+.05,z),(x+.05,y+.09,z+.04)],[.013]*4,5,'hand_l',8)
        cx=sum(v[0] for v in shield)/len(shield);cz=sum(v[1] for v in shield)/len(shield)
        g.plate([(cx+(vx-cx)*.86,cz+(vz-cz)*.88) for vx,vz in shield],y+.158,.017,0,'hand_l')
        g.ring((x,y+.174,z+.16),.058,.009,10,'hand_l',steps=24)
        g.ellipsoid((x,y+.172,z+.16),(.048,.012,.048),10,'hand_l',6,16)
        for j in range(7):
            a=j*PI/6;g.tube([(x+.075*math.cos(a),y+.174,z+.16+.075*math.sin(a)),(x+.096*math.cos(a),y+.174,z+.16+.096*math.sin(a))],[.008,.003],10,'hand_l',5)
    elif cls=='rogue':
        blade(r,'hand_r',True);blade(l,'hand_l',True)
    elif uid=='wc_u_human_priest':
        x,y,z=r
        g.tube([(x,y,.06),(x+.015,y,.66),(x,y,.93)],[.017,.019,.017],5,'hand_r',10)
        g.ring((x,y,.995),.073,.013,10,'hand_r',steps=28)
        g.ellipsoid((x,y,.99),(.025,.023,.036),12,'hand_r',6,10)
    elif uid=='wc_u_human_mage':
        x,y,z=r
        g.tube([(x,y,z),(x-.05,y,z+.14),(x-.025,y,z+.29),(x+.05,y,z+.32)],[.014,.013,.014,.009],10,'hand_r',8)
        g.ring((x+.04,y,z+.225),.092,.012,10,'hand_r',-PI*.82,PI*.65,22)
        g.ellipsoid((x+.04,y,z+.225),(.052,.052,.052),1,'hand_r',8,14)
        g.plate([(.125,.49),(.215,.49),(.215,.61),(.125,.61)],.013,.064,2,'pelvis')
    elif uid=='wc_u_elf_ranger':
        x,y,z=l
        g.tube([(x-.025,y,z-.30),(x+.06,y,z-.22),(x+.105,y,z-.10),(x+.045,y,z),(x+.105,y,z+.10),(x+.06,y,z+.22),(x-.025,y,z+.30)], [.008,.019,.021,.022,.021,.019,.008],5,'hand_l',8,depth=.6)
        g.tube([(x-.025,y,z-.30),(x-.01,y,z),(x-.025,y,z+.30)],[.003]*3,8,'hand_l',5,
               weights=[{'hand_l':1},{'weapon_l':1},{'hand_l':1}])
        g.tube([(-.05,-.17,.53),(.08,-.17,.79)],[.039,.041],5,'spine_02',10)
        for j in range(3):g.tube([(.055+j*.018,-.17,.77),(.075+j*.018,-.17,.89)],[.005,.005],2,'spine_02',5)
    elif uid=='wc_u_elf_priest':
        x,y,z=l;cx=x-.055;cy=y+.085;cz=z+.12
        g.ring((cx,cy,cz),.162,.022,3,'hand_l',-.45*PI,.92*PI,30)
        g.tube([(cx-.158,cy,cz+.041),(cx+.035,cy,cz+.155)],[.018,.019],3,'hand_l',8)
        g.tube([(cx-.105,cy,cz-.132),(cx+.027,cy,cz-.120)],[.012,.012],3,'hand_l',8)
        for j in range(4):
            xx=cx-.097+j*.035;g.tube([(xx,cy,cz-.13+j*.003),(xx,cy,cz+.092+j*.018)],[.0035,.0035],8,'hand_l',5)
    elif uid in ('wc_u_dwarf_guardian','wc_u_dwarf_warrior'):
        x,y,z=r
        g.tube([(x,y,z-.095),(x,y,z+.36)],[.022,.022],5,'hand_r',10)
        if cls=='guardian':
            g.loft([((x,y,z+.25),.135,.086),((x,y,z+.28),.14,.09),((x,y,z+.33),.10,.075),((x,y,z+.40),.075,.06),((x,y,z+.425),.041,.04)],2,'hand_r',12)
        else:
            g.plate([(x-.175,z+.255),(x+.16,z+.255),(x+.18,z+.39),(x-.16,z+.425)],y,.16,4,'hand_r')
            g.plate([(x-.12,z+.28),(x+.12,z+.28),(x+.12,z+.32),(x-.12,z+.32)],y+.09,.012,2,'hand_r')
    elif uid=='wc_u_dwarf_ranger':
        x,y,z=r
        g.plate([(x-.055,z-.005),(x+.055,z-.005),(x+.045,z+.25),(x-.04,z+.29)],y,.075,5,'hand_r')
        g.tube([(x-.24,y,z+.18),(x-.14,y+.025,z+.24),(x,y+.045,z+.23),(x+.14,y+.025,z+.24),(x+.24,y,z+.18)],[.013,.026,.034,.026,.013],2,'hand_r',8)
        g.tube([(x-.24,y,z+.18),(x,y,z+.10),(x+.24,y,z+.18)],[.0035]*3,8,'hand_r',5)
        g.ring((x+.065,y+.016,z+.07),.043,.012,2,'hand_r',steps=18)
    elif uid=='wc_u_orc_warrior':
        x,y,z=r;g.tube([(x,y,z-.08),(x,y,z+.36)],[.022,.022],5,'hand_r',10)
        g.plate([(x-.01,z+.25),(x-.19,z+.22),(x-.21,z+.34),(x-.14,z+.42),(x-.015,z+.385),(x+.025,z+.34)],y,.054,4,'hand_r')
    elif uid=='wc_u_orc_mage':
        x,y,z=r;g.tube([(x,y,.045),(x+.015,y,.62),(x,y,.91)],[.021,.024,.026],5,'hand_r',10)
        for s in (-1,1):g.tube([(x,y,.83),(x+s*.063,y,.95),(x+s*.082,y,1.06)],[.023,.021,.009],5,'hand_r',9)
        g.ellipsoid((x,y,1.006),(.041,.034,.06),11,'hand_r',6,8)


def make_mesh(g,u,arm,mat):
    mesh=bpy.data.meshes.new('WC_TailoredGeometry');h=u['height_m']
    mesh.from_pydata([tuple(Vector(v)*h) for v in g.vertices],[],g.faces);mesh.update()
    obj=bpy.data.objects.new('SK_'+u['id'],mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat)
    uv=mesh.uv_layers.new(name='WC_PaletteAtlas')
    for poly,col in zip(mesh.polygons,g.colors):
        for li in poly.loop_indices:
            co=mesh.vertices[mesh.loops[li].vertex_index].co/h
            uv.data[li].uv=((col%4+.20+.60*((co.x+.7)%1))/4,(col//4+.20+.60*(co.z%1))/4)
        poly.use_smooth=col in (6,7,8,9,14)
    for bone in arm.data.bones:obj.vertex_groups.new(name=bone.name)
    for i,ws in enumerate(g.weights):
        for name,w in ws.items():obj.vertex_groups[name].add([i],w,'REPLACE')
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
    mod=obj.modifiers.new('WC_Skin','ARMATURE');mod.object=arm;obj.parent=arm
    return obj


def animate(u,arm,out,export_animation=True,selected_clips=None):
    from hand_contacts import contact_pose
    from refine_animation_poses import refine_body,refine_contacts
    clips={};cls=u['unit_class'];race=u['race']
    lengths={'Idle':120,'Move':60,'Attack':max(36,int(u['stats']['attack_windup_ms']*.06)+24),
             'Active':int((u['ability']['cast_ms']+u['ability'].get('recovery_ms',300))*.06),
             'Hit':24,'Defeat':60,'Victory':90}
    lengths['Active']=max(30,lengths['Active'])
    for clip,end in lengths.items():
        if selected_clips is not None and clip not in selected_clips:continue
        arm.animation_data_clear()
        old=bpy.data.actions.get(f'AN_{u["id"]}_{clip}')
        if old:bpy.data.actions.remove(old)
        for b in arm.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
        frames=sorted(set([1,1+end//4,1+end//2,1+3*end//4,end+1]))
        release=int((u['ability']['cast_ms'] if clip=='Active' else u['stats']['attack_windup_ms'])*.06)+1
        if clip in ('Attack','Active'):frames=sorted(set([1,max(2,release//2),release,min(end+1,release+9),end+1]))
        for frame in frames:
            t=(frame-1)/end;wave=math.sin(t*2*PI)
            for b in arm.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0)
            def rot(n,x=0,y=0,z=0):
                # Positive rotation around the rolled arm X is a forward reach.
                if n.startswith(('upperarm','lowerarm')):x=-x
                if n.startswith('calf'):x=-x
                arm.pose.bones[n].rotation_euler=tuple(math.radians(a) for a in (x,y,z))
            # Settled guard, with arms turned slightly forwards from the editable A-pose.
            rot('upperarm_l',-7,0,-5);rot('upperarm_r',-7,0,5)
            rot('lowerarm_l',-10);rot('lowerarm_r',-10)
            if clip=='Idle':
                rot('spine_02',wave*.8);rot('head',0,wave*2,0)
                rot('lowerarm_l',-11+wave*1.5);rot('lowerarm_r',-12-wave*1.5)
            elif clip=='Move':
                amp=17 if race=='dwarf' else (27 if cls=='rogue' else 22)
                rot('thigh_l',amp*wave);rot('thigh_r',-amp*wave)
                rot('calf_l',max(0,-wave)*19);rot('calf_r',max(0,wave)*19)
                rot('foot_l',-amp*wave+max(0,-wave)*19);rot('foot_r',amp*wave+max(0,wave)*19)
                leg_length=(.43 if race=='dwarf' else .49)-.07
                arm.pose.bones['pelvis'].location.y=-leg_length*(1-math.cos(math.radians(amp*wave)))*u['height_m']
                rot('upperarm_l',-10-wave*11,0,-5);rot('upperarm_r',-10+wave*11,0,5)
                rot('spine_02',4 if cls=='rogue' else 1)
            elif clip in ('Attack','Active'):
                envelope=0 if frame in (1,end+1) else (1 if frame<=release else .5)
                anticipate=frame<release
                if cls in ('guardian','warrior','rogue'):
                    rot('upperarm_r',(30 if anticipate else -55)*envelope,0,(-18 if anticipate else 15)*envelope)
                    rot('lowerarm_r',(-50 if anticipate else -9)*envelope)
                    rot('hand_r',-(20 if anticipate else 64)*envelope)
                    rot('spine_02',3*envelope,(-12 if anticipate else 16)*envelope)
                    if clip=='Active' and cls=='guardian' and race=='human':
                        rot('upperarm_r',-7,0,5);rot('lowerarm_r',-10);rot('hand_r',0)
                        rot('upperarm_l',-65*envelope,0,15*envelope);rot('lowerarm_l',-16*envelope)
                        rot('hand_l',-81*envelope)
                    elif clip=='Active' and race=='dwarf' and cls=='guardian':
                        rot('upperarm_r',-7,0,5);rot('lowerarm_r',-10);rot('hand_r',0)
                        rot('thigh_l',-24*envelope if anticipate else 0);rot('calf_l',35*envelope if anticipate else 0)
                        rot('foot_l',59*envelope if anticipate else 0)
                    elif clip=='Active' and cls=='rogue':
                        rot('spine_02',26*envelope);rot('thigh_l',-20*envelope);rot('calf_l',30*envelope);rot('upperarm_l',15*envelope)
                        rot('upperarm_r',15*envelope);rot('lowerarm_r',0);rot('hand_r',0)
                        rot('foot_l',50*envelope)
                    elif clip=='Active' and race=='orc' and cls=='warrior':
                        rot('spine_02',-7*envelope);rot('upperarm_l',-35*envelope,0,-22*envelope)
                        rot('upperarm_r',-20*envelope);rot('lowerarm_r',-20*envelope);rot('hand_r',0)
                else:
                    rot('upperarm_r',(-48 if anticipate else -67)*envelope,0,7*envelope)
                    rot('lowerarm_r',(-30 if anticipate else -5)*envelope)
                    rot('upperarm_l',(-31 if clip=='Attack' else -58)*envelope,0,-15*envelope)
                    rot('lowerarm_l',-22*envelope)
                    rot('spine_02',(-4 if anticipate else 6)*envelope)
                    if u['id']=='wc_u_elf_priest':rot('upperarm_l',-16*envelope,0,-18*envelope);rot('upperarm_r',-20*envelope,0,22*envelope)
                    if clip=='Active' and u['id']=='wc_u_elf_ranger':
                        rot('spine_02',23*envelope);rot('thigh_l',-18*envelope);rot('calf_l',28*envelope);rot('foot_l',46*envelope)
            elif clip=='Hit':
                a=math.sin(t*PI);rot('spine_02',-12*a);rot('head',9*a)
            elif clip=='Defeat':
                a=min(1,t*1.5);rot('spine_01',30*a);rot('head',19*a)
                rot('thigh_l',42*a);rot('thigh_r',42*a);rot('calf_l',70*a);rot('calf_r',70*a)
                rot('foot_l',28*a);rot('foot_r',28*a)
                hip=.43 if race=='dwarf' else .49;knee=.235 if race=='dwarf' else .27
                drop=(hip-knee)*math.cos(math.radians(42*a))+(knee-.07)*math.cos(math.radians(28*a))-(hip-.07)
                arm.pose.bones['pelvis'].location.y=drop*u['height_m']
                rot('upperarm_l',14*a);rot('upperarm_r',19*a)
            elif clip=='Victory':
                a=math.sin(t*PI);rot('upperarm_r',-88*a,0,15*a);rot('lowerarm_r',-18*a);rot('head',-7*a);rot('spine_02',-4*a)
            refine_body(u,arm,clip,frame,end,release)
            contact_pose(u,arm,'Idle' if clip=='Defeat' else clip,frame,end,release)
            refine_contacts(u,arm,clip,frame,end,release)
            for b in arm.pose.bones:
                b.keyframe_insert(data_path='rotation_euler',frame=frame,group=b.name)
                b.keyframe_insert(data_path='location',frame=frame,group=b.name)
        action=arm.animation_data.action;action.name=f'AN_{u["id"]}_{clip}';action.use_fake_user=True
        contact_maximum=0;contact_samples=0
        if clip in ('Hit','Defeat','Active','Victory') or u['id'] in ('wc_u_dwarf_guardian','wc_u_dwarf_warrior','wc_u_dwarf_ranger','wc_u_elf_ranger','wc_u_elf_priest'):
            previous={}
            for sample in sorted(set(range(1,end+2,3))|{end+1}):
                bpy.context.scene.frame_set(sample);bpy.context.view_layer.update()
                refine_body(u,arm,clip,sample,end,release)
                support_error=contact_pose(u,arm,'Idle' if clip=='Defeat' else clip,sample,end,release)
                if clip!='Defeat':contact_maximum=max(contact_maximum,support_error)
                contact_samples+=1
                contact_maximum=max(contact_maximum,refine_contacts(u,arm,clip,sample,end,release))
                for bone in arm.pose.bones:
                    if u['id']=='wc_u_elf_ranger' and bone.name=='weapon_l':bone.keyframe_insert(data_path='location',frame=sample,group=bone.name)
                    if clip in ('Hit','Defeat','Active','Victory') or bone.name.startswith(('upperarm_','lowerarm_','hand_')):
                        rotation=bone.rotation_euler.to_quaternion().to_euler('XYZ',previous.get(bone.name,bone.rotation_euler))
                        bone.rotation_euler=rotation;previous[bone.name]=rotation.copy()
                        bone.keyframe_insert(data_path='rotation_euler',frame=sample,group=bone.name)
                        if clip=='Defeat':bone.keyframe_insert(data_path='location',frame=sample,group=bone.name)
            if contact_maximum>.025:raise RuntimeError(f'{u["id"]} {clip}: support grip unreachable by {contact_maximum:.4f}m')
        bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=end+1;bpy.context.scene.frame_set(1)
        if export_animation:export_fbx(out/f'{action.name}.fbx',[arm],True)
        clips[clip]={'action':action.name,'frames':[1,end+1],'release_frame':release if clip in ('Attack','Active') else None,
                     'support_hand_bake_samples':contact_samples,'maximum_support_reach_clamp_m':contact_maximum}
    return clips


def export_fbx_raw(path,objects,animation):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH','ARMATURE'},
        global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Y',axis_up='Z',
        use_mesh_modifiers=True,mesh_smooth_type='FACE',use_tspace=False,add_leaf_bones=False,
        use_armature_deform_only=True,bake_anim=animation,bake_anim_use_all_bones=True,bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,bake_anim_force_startend_keying=True,bake_anim_step=1,bake_anim_simplify_factor=0,
        path_mode='COPY',embed_textures=False)


def export_fbx(path,objects,animation):
    if any(ob.type=='ARMATURE' for ob in objects):
        profile=json.loads((ROOT/'tools/blender/profiles/fbx_skeletal_cm_v1.json').read_text())
        if profile['calibration_status']!='measured_pass':raise RuntimeError('Skeletal export requires the measured centimeter profile')
        from normalized_fbx import export_normalized_copy
        export_normalized_copy(path,objects,animation,export_fbx_raw)
    else:export_fbx_raw(path,objects,animation)


def export_lods(unit,mesh,arm,out):
    collection=bpy.data.collections.new('LOD_SOURCE');bpy.context.scene.collection.children.link(collection)
    records=[]
    for index,ratio in ((1,.5),(2,.25)):
        lod=mesh.copy();lod.data=mesh.data.copy();lod.name=f'SK_{unit["id"]}_LOD{index}';collection.objects.link(lod)
        bpy.ops.object.select_all(action='DESELECT');lod.select_set(True);bpy.context.view_layer.objects.active=lod
        modifier=lod.modifiers.new('WC_SilhouetteReduction','DECIMATE');modifier.ratio=ratio
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        lod.data.calc_loop_triangles();records.append({'lod':index,'triangles':len(lod.data.loop_triangles),'ratio_target':ratio,'visual_acceptance':'pending'})
        export_fbx(out/f'{lod.name}.fbx',[arm,lod],False)
        lod.hide_render=True;lod.hide_set(True)
    return records


def preserve_source_parts(mesh,geometry,equipment_face_start):
    for name in ('BODY','COSTUME','EQUIPMENT'):
        part=mesh.copy();part.data=mesh.data.copy();part.name=f'{name}_{mesh.name}'
        bpy.data.collections[name].objects.link(part)
        bm=bmesh.new();bm.from_mesh(part.data);bm.faces.ensure_lookup_table()
        remove=[]
        for index,face in enumerate(bm.faces):
            category='EQUIPMENT' if index>=equipment_face_start else ('BODY' if geometry.colors[index] in (6,7,8,9,14) else 'COSTUME')
            if category!=name:remove.append(face)
        bmesh.ops.delete(bm,geom=remove,context='FACES')
        loose=[v for v in bm.verts if not v.link_faces]
        if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
        bm.to_mesh(part.data);bm.free();part.hide_render=True;part.hide_set(True)


def setup_render(height):
    sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True
    sc.render.resolution_x=768;sc.render.resolution_y=768;sc.render.resolution_percentage=100
    if sc.world is None:sc.world=bpy.data.worlds.new('WC_Studio')
    sc.world.color=(.14,.17,.22);sc.view_settings.view_transform='AgX'
    for name,loc,power,size,color in [('Key',(3,4,5),650,4,(1,.87,.72)),('Fill',(-3,1,3),400,3,(.71,.85,1)),('Rim',(0,-3,4),850,3,(.76,.88,1))]:
        d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
        ob=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(ob);ob.location=loc
        ob.rotation_euler=(Vector((0,0,height*.5))-ob.location).to_track_quat('-Z','Y').to_euler()
    camdata=bpy.data.cameras.new('WC_Portrait');cam=bpy.data.objects.new('WC_Portrait',camdata);bpy.context.collection.objects.link(cam)
    sc.camera=cam;camdata.type='ORTHO';camdata.ortho_scale=height*1.35
    cam.location=(height*1.65,height*3.1,height*1.65);cam.rotation_euler=(Vector((0,0,height*.51))-cam.location).to_track_quat('-Z','Y').to_euler()
    # Ground is presentation-only, excluded from FBX exports.
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.009));ground=bpy.context.object;ground.name='PRESENTATION_Ground'
    mat=bpy.data.materials.new('PRESENTATION_DeepBlue');mat.diffuse_color=(.045,.065,.10,1);mat.use_nodes=True
    mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.045,.065,.10,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.8
    ground.data.materials.append(mat)
    return cam


def author(unit,opt):
    uid=unit['id'];out=ROOT/'exports/heroes'/uid;source=ROOT/'art-source/heroes'/uid;report=ROOT/'reports/WC-330'/uid
    for folder in (out,source,report):folder.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.fps=60
    for n in ('BODY','COSTUME','EQUIPMENT','RIG','PRESENTATION_HELPERS','EXPORT'):
        c=bpy.data.collections.new(n);sc.collection.children.link(c)
    mat=material_for(unit,out);arm,points=rig_for(unit);geo=body_geometry(unit,points,opt.revision)
    equipment_face_start=len(geo.faces);equipment(geo,unit,points)
    mesh=make_mesh(geo,unit,arm,mat)
    for ob in (mesh,arm):
        for c in list(ob.users_collection):c.objects.unlink(ob)
        bpy.data.collections['EXPORT'].objects.link(ob)
    bpy.data.collections['RIG'].objects.link(arm);preserve_source_parts(mesh,geo,equipment_face_start)
    # Mesh export uses explicit reference pose with no assigned action.
    export_fbx(out/f'SK_{uid}.fbx',[arm,mesh],False)
    lods=export_lods(unit,mesh,arm,out)
    clips=animate(unit,arm,out)
    action=bpy.data.actions[clips['Idle']['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
    sc.frame_start=1;sc.frame_end=121;sc.frame_set(1)
    camera=setup_render(unit['height_m'])
    if not opt.skip_render:
        sc.render.filepath=str(out/'portrait.png');bpy.ops.render.render(write_still=True)
        sc.render.resolution_x=512;sc.render.resolution_y=512
        for label,loc in [('front',(0,4,1.7)),('side',(4,0,1.7)),('back',(0,-4,1.7))]:
            camera.location=loc;camera.rotation_euler=(Vector((0,0,unit['height_m']*.51))-camera.location).to_track_quat('-Z','Y').to_euler()
            sc.render.filepath=str(report/f'{label}.png');bpy.ops.render.render(write_still=True)
        camera.location=(unit['height_m']*1.65,unit['height_m']*3.1,unit['height_m']*1.65)
        camera.rotation_euler=(Vector((0,0,unit['height_m']*.51))-camera.location).to_track_quat('-Z','Y').to_euler()
        sc.render.resolution_x=320;sc.render.resolution_y=320;sc.cycles.samples=12
        for clip,spec in clips.items():
            action=bpy.data.actions[spec['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0]
            sample=spec['release_frame'] or (spec['frames'][1]//4 if clip in ('Idle','Move') else spec['frames'][1] if clip=='Defeat' else spec['frames'][1]//2)
            sc.frame_set(sample)
            sc.render.filepath=str(report/f'clip_{clip}.png');bpy.ops.render.render(write_still=True)
    action=bpy.data.actions[clips['Idle']['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0];sc.frame_set(1)
    sc.render.resolution_x=768;sc.render.resolution_y=768
    bpy.ops.wm.save_as_mainfile(filepath=str(source/f'{uid}.blend'))
    mesh.data.calc_loop_triangles()
    manifest={'status':'authored_exported_rendered_pending_engine_and_visual_acceptance','unit_id':uid,'name':unit['name'],
        'blender_version':bpy.app.version_string,'source_revision':opt.revision,'height_m':unit['height_m'],
        'source_sha256':hashlib.sha256((source/f'{uid}.blend').read_bytes()).hexdigest(),
        'author_script_sha256':AUTHOR_SCRIPT_SHA256,
        'units_source_sha256':hashlib.sha256((ROOT/'data/units.json').read_bytes()).hexdigest(),
        'rig_family':unit['rig_family'],'rig_revision':'WC_family_v1','bones':len(arm.data.bones),'triangles':len(mesh.data.loop_triangles),
        'materials':1,'fps':60,'source_forward':'+Y','source_up':'+Z','unit_scale_m':1,
        'fbx_profile':'tools/blender/profiles/fbx_skeletal_cm_v1.json','normalized_export_revision':1,
        'normalized_exporter_sha256':hashlib.sha256((ROOT/'tools/blender/normalized_fbx.py').read_bytes()).hexdigest(),
        'exported_coordinate_units':'centimeters in temporary independent copies; authoring source remains meters',
        'engine_calibration':['reports/WC-330/import-probe/forward_cm-results.json','reports/WC-330/import-probe/all7-comparison.json'],
        'textures':{'BaseColor':'sRGB','Normal':'linear, tangent +Y, flat normal surface; geometric bevels','ORM':'linear R=occlusion G=roughness B=metallic'},
        'equipment':'weighted within the skeletal mesh; socket bones also available','clips':clips,'lods':lods,
        'source_brief':unit['art'],'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file() and p.name!='export_manifest.json'},
        'open_reviews':['Unreal scale and facing','all continuous animation deformation','source revision reimport','crowded-board readability','LOD1/LOD2','effects and sound integration']}
    (out/'export_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    # Execute the supplied inspector in the actual authoring process, not plain Python.
    import runpy
    saved_argv=sys.argv
    try:
        sys.argv=['inspect_scene.py','--','--collection','EXPORT','--output',str(report/'structural.json'),'--require-skin']
        runpy.run_path(str(ROOT/'tools/blender/inspect_scene.py'),run_name='__main__')
        sys.argv=['audit_motion.py','--','--unit',uid,'--output',str(report/'motion-invariants.json')]
        runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
    finally:sys.argv=saved_argv
    print('WC_HERO_COMPLETE '+uid+' '+json.dumps({'triangles':manifest['triangles'],'bones':manifest['bones']}),flush=True)


if __name__=='__main__':
    opt=args();units=json.loads((ROOT/'data/units.json').read_text(encoding='utf-8'))['units']
    selected=[u for u in units if u['production_phase']=='alpha' and (opt.all or u['id']==opt.hero) and u['id'] not in opt.exclude]
    if not selected:raise ValueError('Hero must be an authored alpha ID')
    for unit in selected:author(unit,opt)
