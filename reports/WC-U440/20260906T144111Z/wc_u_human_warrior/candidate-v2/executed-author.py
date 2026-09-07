"""Original dossier-specific Cass/Neris/Orla/Tala production; no old hero mesh copied."""
import argparse,copy,hashlib,json,math,runpy,shutil,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from author_alpha import Geometry,material_for,rig_for,make_mesh,preserve_source_parts,animate,setup_render,export_fbx_raw
from normalized_fbx import export_normalized_copy
from hand_contacts import place_hand
from refine_update_ada import invariants,action_curve_digest
PI=math.pi
ALLOWED={'wc_u_human_warrior','wc_u_elf_mage','wc_u_dwarf_priest','wc_u_orc_guardian'}
PALETTES={
 'wc_u_human_warrior':'#A4464D #E3D7BA #B2A17B #344155 #A6B5BF #574638 #956348 #302A28 #EEE6D2 #654735 #D3B56F #DDD9B8 #722F3F #C27A74 #875541 #292A30',
 'wc_u_elf_mage':'#7465A5 #B4CADD #C2CCD5 #3E4166 #BAC5D2 #5A5270 #8D695F #343A59 #E0E3D9 #BEADD6 #C1B696 #B8CEE0 #8C82B4 #9D91BA #805D56 #313044',
 'wc_u_dwarf_priest':'#AC6653 #DCCEAF #BDA061 #586B57 #AC955F #685343 #76533D #C0C4BA #F0E3CA #60402B #CFB877 #DFBD74 #864D43 #BE8970 #6B4835 #332E2A',
 'wc_u_orc_guardian':'#AC8658 #D1B576 #D2B681 #405E78 #9F845B #64513E #60765A #303D32 #E2DBC1 #765039 #D2B77B #C6BC84 #526C85 #C3A571 #52694C #29342E'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def curved_panel(g,points,y,depth,col,bone,bulge=.015,rows=4):
    # A closed tailored panel with curved relief, not a flat costume slab.
    left_top,right_top,right_bottom,left_bottom=[Vector(x) for x in points];verts=[]
    for face in (0,1):
        for j in range(rows+1):
            t=j/rows;a=left_top.lerp(left_bottom,t);b=right_top.lerp(right_bottom,t)
            for i in range(7):
                k=i/6;p=a.lerp(b,k);verts.append((p.x,y+bulge*math.sin(k*PI)*(1-.25*t)-face*depth,p.y))
    n=(rows+1)*7;faces=[]
    for j in range(rows):
        for i in range(6):
            a=j*7+i;faces += [(a,a+1,a+8,a+7),(n+a+7,n+a+8,n+a+1,n+a)]
    boundary=list(range(7))+[j*7+6 for j in range(1,rows+1)]+list(range(rows*7+5,rows*7-1,-1))+[j*7 for j in range(rows-1,0,-1)]
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.append((a,b,n+b,n+a))
    g.add(verts,faces,col,bone)
def shaped_hand(g,q,side,open_palm=False):
    h=Vector(q['hand']);s=1 if side=='l' else -1;bone='hand_'+side
    g.tube([q['wrist'],tuple(h+Vector((0,0,.014))),tuple(h+Vector((0,.013,-.018)))],[.025,.035,.030],6,bone,10,depth=.72)
    for finger in range(3):
        x=h.x+s*(finger-1)*.012
        pts=[(x,h.y+.004,h.z+.005),(x,h.y+.042,h.z+.002),(x,h.y+.055,h.z-.015)]
        if open_palm:pts=[(x,h.y+.008,h.z-.009),(x,h.y+.025,h.z-.041),(x,h.y+.032,h.z-.063)]
        g.tube(pts,[.012,.010,.007],6,bone,7)
    g.tube([tuple(h+Vector((-s*.027,.006,.012))),tuple(h+Vector((-s*.031,.035,.014))),tuple(h+Vector((-s*.011,.047,.008)))],[.014,.012,.009],6,bone,7)
def face_hair(g,u):
    uid=u['id'];stock=u['race']=='dwarf';broad=u['race']=='orc';elf=u['race']=='elf'
    width=.097 if stock else .102 if broad else .078 if elf else .081
    # Distinct jaw and cheek profiles retain readable adult facial planes.
    jaw=.73 if uid=='wc_u_human_warrior' else .57 if stock else .55 if elf else .70
    g.loft([((0,0,.788),.05,.045),((0,0,.84),.054,.052)],6,'neck',14)
    g.loft([((0,.015,.830),width*jaw,.043),((0,.015,.850),width*.82,.063),((0,.012,.885),width,.075),((0,.006,.920),width*.97,.079),((0,-.006,.955),width*.88,.073),((0,-.012,.983),width*.59,.051),((0,-.014,.993),.023,.024)],6,'head',20)
    g.add([(-.016,.079,.918),(.016,.079,.918),(-.018,.100,.883),(.018,.100,.883),(0,.112 if not stock else .117,.888)],[(0,1,4),(0,4,2),(1,3,4),(2,4,3),(0,2,3,1)],14,'head')
    for s in (-1,1):
        x=s*width*.44;y=.084
        g.plate([(x-.020,.908),(x-.010,.916),(x+.014,.915),(x+.020,.907),(x+.006,.900),(x-.012,.902)],y,.007,8,'head',.06)
        g.plate([(x-.006,.912),(x+.007,.912),(x+.007,.902),(x-.006,.902)],y+.004,.008,9,'head',.04)
        g.plate([(x-.002,.910),(x+.003,.910),(x+.003,.903),(x-.002,.903)],y+.009,.005,15,'head',.03)
        g.tube([(x-s*.021,.082,.929),(x,.090,.933),(x+s*.023,.077,.929)],[.006,.007,.004],7,'head',6)
        if uid=='wc_u_human_warrior' and s==1:g.tube([(x+.006,.088,.933),(x+.014,.083,.931)],[.0045,.0045],1,'head',6)
        if elf:g.plate([(s*width*.88,.929),(s*(width+.063),.954),(s*(width+.043),.894),(s*width,.884)],-.005,.029,6,'head',.06)
        else:g.ellipsoid((s*width,.002,.893),(.017,.026,.032),6,'head',5,10)
        if broad:g.tube([(s*.033,.086,.854),(s*.036,.111,.874),(s*.031,.115,.889)],[.012,.008,.001],8,'head',8)
    g.tube([(-.027,.083,.861),(0,.094,.857),(.027,.083,.861)],[.0025,.0035,.0025],14,'head',7)
    # Continuous scalp shell, shaped hairline, no sphere used as the face.
    vertices=[];faces=[];steps=28
    for k,(rad,z) in enumerate(((1,.925),(.99,.953),(.84,.978),(.49,.995),(.05,1.001))):
        for j in range(steps):
            a=j*2*PI/steps;vertices.append((width*rad*math.cos(a),-.014+.080*rad*math.sin(a),z+(.029*max(0,math.sin(a)) if k==0 else 0)))
    for k in range(4):
        for j in range(steps):faces.append((k*steps+j,k*steps+(j+1)%steps,(k+1)*steps+(j+1)%steps,(k+1)*steps+j))
    faces.append(tuple(4*steps+j for j in range(steps)));g.add(vertices,faces,7,'head')
    if elf:
        g.ellipsoid((0,-.091,.934),(.045,.037,.039),7,'head',7,14)
        for strand in range(3):
            pts=[(.038*math.cos(j*2*PI/24),-.114+.006*math.sin(j*1.7+strand),.933+.033*math.sin(j*2*PI/24)) for j in range(25)]
            g.tube(pts,[.006]*25,7,'head',6)
        g.ring((0,-.005,.969),.145,.015,2,'head',.20*PI,.80*PI,24)
        # Broken arc has an open center and thick ends against the sky.
        for s in (-1,1):g.tube([(s*.129,-.005,1.054),(s*.151,-.005,1.043)],[.019,.012],2,'head',8)
    if stock:
        for s in (-1,1):
            for strand in range(3):
                pts=[]
                for j in range(17):
                    a=j*.9+strand*2*PI/3;pts.append((s*.093+.009*math.cos(a),.013+.006*j+.009*math.sin(a),.918-.010*j))
                g.tube(pts,[.010-.003*j/16 for j in range(17)],7,'head',7)
            g.loft([((s*.093,.10,.754),.019,.018),((s*.093,.10,.771),.021,.020)],2,'head',10)
        # Soft padded hood arch, leaving the forehead and side braids exposed.
        pts=[(.122*math.cos(PI-i*PI/28),-.041,.920+.111*math.sin(PI-i*PI/28)) for i in range(29)]
        g.tube(pts,[.029]*29,0,'head',10,depth=1.20)
        g.tube([(s*.092,-.063,.82) for s in (-1,0,1)],[.028,.041,.028],0,'neck',10)
    if broad:
        for band in (-1,0,1):
            pts=[(band*.039+.006*math.sin(j*1.9),-.057-.003*j,.980-.004*j) for j in range(23)]
            g.tube(pts,[.011]*23,7,'head',7)
        g.ellipsoid((0,-.119,.888),(.048,.026,.034),7,'head',6,12)
def body(g,u,p):
    uid=u['id'];stock=u['race']=='dwarf';broad=u['race']=='orc';elf=u['race']=='elf';sh=abs(p['l']['sh'][0]);hip=p['l']['hip'][2]
    width=.175 if stock else .163 if broad else .108 if elf else .132
    torso=[((0,0,hip-.015),width,.11 if stock else .089),((0,0,hip+.045),width*1.07,.116 if stock else .095),((0,0,.61),width*.93,.106 if stock else .081),((0,0,.67),width*1.06,.115),((0,-.003,.732),sh*.89,.108),((0,-.003,.788),sh*.58,.070)]
    g.loft(torso,0,'spine_02',20,weights=[{'pelvis':1},{'pelvis':.8,'spine_01':.2},{'spine_01':1},{'spine_02':1},{'spine_03':1},{'spine_03':1}])
    for side in ('l','r'):
        q=p[side];s=1 if side=='l' else -1;leg=.076 if stock else .069 if broad else .045 if elf else .057
        g.tube([q['hip'],tuple(Vector(q['hip']).lerp(Vector(q['knee']),.45)),q['knee'],tuple(Vector(q['knee']).lerp(Vector(q['ankle']),.60)),q['ankle']],[leg,leg*.90,leg*.74,leg*.64,leg*.58],1 if uid=='wc_u_human_warrior' else 3,'thigh_'+side,14,weights=[{'thigh_'+side:1},{'thigh_'+side:1},{'thigh_'+side:.5,'calf_'+side:.5},{'calf_'+side:1},{'calf_'+side:1}])
        x=q['ankle'][0];br=leg*1.08
        g.loft([((x,.030,.008),br,.095),((x,.039,.034),br*1.03,.108),((x,.03,.073),br*.96,.095),((x,.005,.111),br*.80,.061),((x,0,.220 if not stock else .18),br*.92,.065)],5,'calf_'+side,14,weights=[{'foot_'+side:1},{'foot_'+side:1},{'foot_'+side:1},{'foot_'+side:.55,'calf_'+side:.45},{'calf_'+side:1}])
        g.tube([(x-br*.70,.070,.15),(x+br*.70,.070,.15)],[.009,.009],2,'calf_'+side,7)
        radius=.077 if stock else .071 if broad else .043 if elf else .053
        a=Vector(q['sh']);b=Vector(q['el']);c=Vector(q['wrist'])
        sleeve=[tuple(a.lerp(b,.13)),tuple(a.lerp(b,.25)),tuple(a.lerp(b,.65)),q['el'],tuple(b.lerp(c,.30)),tuple(b.lerp(c,.72)),q['wrist']]
        g.tube(sleeve,[radius*.49,radius*.99,radius*.86,radius*.69,radius*.81,radius*.65,radius*.50],0,'upperarm_'+side,16,weights=[{'clavicle_'+side:.4,'upperarm_'+side:.6},{'upperarm_'+side:1},{'upperarm_'+side:1},{'upperarm_'+side:.5,'lowerarm_'+side:.5},{'lowerarm_'+side:1},{'lowerarm_'+side:1},{'lowerarm_'+side:1}])
        g.tube([tuple(b.lerp(c,.73)),q['wrist']],[radius*.78,radius*.66],1 if uid in ('wc_u_elf_mage','wc_u_dwarf_priest') else 4,'lowerarm_'+side,12)
        # A fitted shoulder cap bridges the tailored sleeve into the torso.
        cap=[tuple(a+Vector((-s*.012,0,.006))),tuple(a.lerp(b,.12)),tuple(a.lerp(b,.29))]
        g.tube(cap,[radius*.58,radius*.88,radius*.98],0,'upperarm_'+side,14,weights=[{'spine_03':.6,'clavicle_'+side:.4},{'clavicle_'+side:.35,'upperarm_'+side:.65},{'upperarm_'+side:1}])
        shaped_hand(g,q,side,open_palm=uid=='wc_u_elf_mage' or(uid=='wc_u_dwarf_priest' and side=='l'))
    g.loft([((0,0,hip+.055),width*1.085,.112),((0,0,hip+.089),width*1.04,.108)],2 if uid=='wc_u_orc_guardian' else 5,'pelvis',20)
    g.plate([(-.027,hip+.055),(.027,hip+.055),(.027,hip+.089),(-.027,hip+.089)],.117,.016,10,'pelvis',.09)
    low=.295 if stock else .31 if elf else .37
    for s in (-1,1):
        curved_panel(g,[(s*.010,hip+.050),(s*(width+.006),hip+.052),(s*(width*.91),low),(s*.031,low-.018)],.107,.012,0,'pelvis',.021,5)
        curved_panel(g,[(s*.006,hip+.050),(s*(width+.005),hip+.052),(s*(width*1.13),low+.03),(s*.032,low-.015)],-.098,.014,0,'pelvis',-.015,5)
        g.tube([(s*.028,.124,hip+.025),(s*.033,.122,low+.008)],[.006,.005],13,'pelvis',6)
    if uid=='wc_u_human_warrior':
        curved_panel(g,[(-.046,.775),(.046,.775),(.042,.599),(-.042,.599)],.119,.009,1,'spine_02',.009)
        # One squared guard with rounded longitudinal contour.
        a=p['l']['sh'];g.loft([((a[0],0,a[2]-.020),.082,.078),((a[0],0,a[2]+.022),.103,.087),((a[0]-.015,0,a[2]+.049),.070,.069)],4,'clavicle_l',12)
        for s in (-1,1):g.tube([(s*.105,-.105,.753),(s*.10,-.11,.565)],[.014,.014],5,'spine_02',8)
        g.plate([(-.02,.74),(.135,.755),(.116,.645),(.013,.655)],.121,.025,4,'spine_02',.12)
    elif uid=='wc_u_elf_mage':
        for s in (-1,1):curved_panel(g,[(s*.024,.799),(s*.093,.778),(s*.070,.636),(s*.018,.640)],.113,.01,1,'spine_02',.014)
        g.tube([(-.058,.052,.800),(0,.078,.814),(.058,.052,.800)],[.014,.013,.014],2,'neck',8)
        curved_panel(g,[(-.070,.51),(.070,.51),(.050,.275),(-.052,.275)],.107,.01,1,'pelvis',.022)
    elif uid=='wc_u_dwarf_priest':
        curved_panel(g,[(-.11,.65),(.11,.65),(.15,.306),(-.15,.306)],.128,.015,1,'spine_01',.026,6)
        for z in (.35,.39,.43):g.tube([(-.128,.145,z),(.128,.145,z)],[.004,.004],2,'pelvis',6)
        # Hood drape joins the neck, with broad wool edging over shoulders.
        for s in (-1,1):g.tube([(s*.057,-.041,.81),(s*.16,-.015,.79),(s*.225,.0,.735)],[.037,.041,.024],0,'spine_03',10)
        g.plate([(-.047,.64),(0,.686),(.047,.64),(.036,.588),(-.036,.588)],-.126,.008,1,'spine_02',.10)
    else:
        for side in ('l','r'):
            s=1 if side=='l' else -1;a=p[side]['sh']
            g.loft([((a[0],0,a[2]-.020),.090,.085),((a[0],0,a[2]+.027),.101,.094),((a[0]-s*.010,0,a[2]+.054),.069,.074)],4,'clavicle_'+side,14)
        curved_panel(g,[(-.12,.742),(.12,.742),(.108,.612),(-.108,.612)],.113,.023,5,'spine_02',.020)
        for z in (.635,.685,.733):g.tube([(-.104,.139,z),(.104,.139,z)],[.009,.009],4,'spine_02',8)
        g.loft([((0,0,.530),width*1.09,.120),((0,0,.585),width*1.075,.116)],3,'pelvis',20)
        for s in (-1,1):g.tube([(s*.028,.127,.54),(s*.091,.125,.577)],[.005,.005],1,'pelvis',6)
        g.tube([(-.22,-.007,.784),(-.10,-.067,.814),(.10,-.067,.814),(.22,-.007,.784)],[.028,.031,.031,.028],1,'spine_03',10)
    face_hair(g,u)
def gear(g,u,p):
    uid=u['id']
    if uid=='wc_u_human_warrior':
        h=Vector(p['r']['hand']);x,y,z=h
        g.tube([(x,y,z-.075),(x,y,z+.105)],[.020,.020],5,'weapon_r',10)
        g.ellipsoid((x,y,z-.081),(.034,.025,.032),10,'weapon_r',5,10)
        g.tube([(x-.104,y,z+.102),(x-.051,y,z+.114),(x+.051,y,z+.114),(x+.104,y,z+.102)],[.015,.021,.021,.015],4,'weapon_r',9)
        g.plate([(x-.045,z+.122),(x+.045,z+.122),(x+.055,z+.43),(x,z+.565),(x-.055,z+.43)],y,.022,4,'weapon_r',.12)
        g.tube([(x,y+.016,z+.135),(x,y+.016,z+.52)],[.008,.003],8,'weapon_r',7)
        # Full physical back bracket and rigid folded banner, no implied gameplay aura.
        g.plate([(-.075,.64),(.075,.64),(.063,.76),(-.063,.76)],-.130,.038,5,'spine_03',.12)
        g.tube([(.075,-.158,.67),(.075,-.158,1.11)],[.012,.012],10,'spine_03',9)
        g.tube([(-.115,-.158,1.09),(.09,-.158,1.09)],[.012,.012],10,'spine_03',9)
        curved_panel(g,[(-.11,1.08),(.068,1.08),(.068,.854),(-.11,.870)],-.164,.012,0,'spine_03',-.015,6)
        g.tube([(-.094,-.184,.881),(.052,-.184,.866)],[.007,.007],1,'spine_03',7)
        g.plate([(-.065,1.036),(-.025,1.055),(.015,1.036),(-.025,.985)],-.186,.008,1,'spine_03',.07)
    elif uid=='wc_u_elf_mage':
        h=Vector(p['l']['hand']);cx,cy,cz=h+Vector((0,.015,.104))
        g.ring((cx,cy,cz),.083,.013,2,'weapon_l',steps=28)
        g.plate([(cx-.046,cz),(cx-.016,cz+.015),(cx,cz+.055),(cx+.016,cz+.015),(cx+.047,cz),(cx+.017,cz-.016),(cx,cz-.053),(cx-.017,cz-.016)],cy,.012,11,'weapon_l',.10)
        g.tube([tuple(h+Vector((0,.005,.016))),(cx,cy,cz-.081)],[.012,.014],2,'weapon_l',8)
        g.plate([(-.19,.46),(-.10,.46),(-.10,.595),(-.19,.585)],-.055,.042,3,'pelvis',.10)
        for z in (.49,.55):g.tube([(-.18,-.029,z),(-.114,-.029,z)],[.006,.006],2,'pelvis',6)
    elif uid=='wc_u_dwarf_priest':
        h=Vector(p['r']['hand']);x,y,z=h
        pts=[(x+.063*math.cos(PI-i*PI/16),y,z-.064+.076*math.sin(PI-i*PI/16)) for i in range(17)]
        g.tube(pts,[.012]*17,2,'weapon_r',8)
        g.loft([((x,y,z-.248),.100,.086),((x,y,z-.224),.112,.098),((x,y,z-.080),.102,.090),((x,y,z-.055),.065,.058)],2,'weapon_r',8)
        g.loft([((x,y,z-.214),.104,.090),((x,y,z-.094),.097,.085)],11,'weapon_r',8)
        for j in range(8):
            a=j*PI/4;g.tube([(x+.105*math.cos(a),y+.092*math.sin(a),z-.222),(x+.098*math.cos(a),y+.086*math.sin(a),z-.086)],[.008,.008],2,'weapon_r',6)
        g.plate([(.17,.42),(.24,.42),(.255,.50),(.17,.515)],-.02,.049,1,'pelvis',.13)
    else:
        h=Vector(p['l']['hand']);x,y,z=h;vertices=[];faces=[]
        outline=[(-.155,-.26),(.155,-.26),(.160,.20),(.133,.265),(.08,.305),(0,.318),(-.08,.305),(-.133,.265),(-.160,.20)]
        for back in (0,1):
            for dx,dz in outline:vertices.append((x+dx,y+.101-.035*(dx/.16)**2-back*.033,z+dz))
        n=len(outline);faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];g.add(vertices,faces,3,'weapon_l')
        pts=[tuple(Vector(vertices[i])+Vector((0,.008,0))) for i in range(n)];g.tube(pts+[pts[0]],[.012]*(n+1),4,'weapon_l',8)
        for s in (-1,1):g.tube([(x+s*.093,y+.104,z-.17),(x+s*.024,y+.117,z-.015),(x+s*.09,y+.103,z+.18)],[.012]*3,10,'weapon_l',8)
        g.tube([(x-.09,y+.102,z+.06),(x+.09,y+.102,z-.06)],[.012,.012],10,'weapon_l',8)
        g.tube([(x-.07,y+.010,z+.01),(x+.07,y+.010,z+.01)],[.014,.014],5,'weapon_l',8)
        for s in (-1,1):g.tube([(x+s*.07,y+.010,z+.01),(x+s*.07,y+.065,z+.01)],[.014,.014],4,'weapon_l',8)
        r=Vector(p['r']['hand']);g.tube([tuple(r+Vector((0,0,-.055))),tuple(r+Vector((0,0,.23)))],[.018,.022],5,'weapon_r',9)
        g.loft([((r.x,r.y,r.z+.20),.05,.045),((r.x,r.y,r.z+.26),.070,.064),((r.x,r.y,r.z+.31),.035,.033)],4,'weapon_r',10)
        g.plate([(-.135,.56),(.135,.56),(.12,.725),(-.12,.725)],-.143,.065,5,'spine_02',.14)
        for s in (-1,1):g.tube([(s*.08,-.183,.58),(s*.075,-.18,.716)],[.014,.014],1,'spine_02',8)

def contacts(u,arm,clip,frame,end,release):
    h=u['height_m'];uid=u['id'];t=(frame-1)/end;wave=math.sin(t*2*PI);victory=max(0,math.sin(t*PI)) if clip=='Victory' else 0
    times=[1,max(2,release//2),release,min(end+1,release+9),end+1]
    def sample(values):
        for i in range(1,len(times)):
            if frame<=times[i]:return values[i-1]+(values[i]-values[i-1])*smooth((frame-times[i-1])/max(1,times[i]-times[i-1]))
        return values[-1]
    active=clip=='Active';attack=clip=='Attack';defeat=clip=='Defeat'
    kneel=smooth(t/.76) if defeat else 0
    def settle(start,end):return tuple(Vector(start).lerp(Vector(end),kneel))
    spine=arm.pose.bones['spine_02'];body=spine.matrix@spine.bone.matrix_local.inverted();bodyrot=body.to_3x3()
    def pos(v):return Vector(v)*h if defeat else body@(Vector(v)*h)
    def turn(x=0,y=0,z=0):return (Matrix.Identity(3) if defeat else bodyrot)@Matrix.Rotation(math.radians(z),3,'Z')@Matrix.Rotation(math.radians(y),3,'Y')@Matrix.Rotation(math.radians(x),3,'X')
    def hand(side,v,rotation):return place_hand(arm,side,pos(v),rotation,h)
    errors=[]
    if uid=='wc_u_human_warrior':
        rise=sample([0,.045,.06,.03,0]) if attack else sample([0,.085,.065,.03,0]) if active else .035*victory
        angle=sample([-142,-90,-130,-150,-142]) if attack else sample([-142,-55,-120,-145,-142]) if active else -142+52*victory
        point=(-.025,.115,.665+rise+.003*wave);rotation=turn(angle,0,-10)
        if defeat:point=settle((-.025,.115,.665),(.015,.10,.33));rotation=turn(-142+56*kneel,0,-10+10*kneel)
        errors.append(hand('r',point,rotation));r=arm.pose.bones['hand_r'];target=r.matrix@r.bone.matrix_local.inverted()@(r.bone.tail_local+Vector((0,0,.074))*h)
        errors.append(place_hand(arm,'l',target,rotation,h))
    elif uid=='wc_u_elf_mage':
        a=sample([0,1,1,.4,0]) if active else 0;f=sample([0,1,.3,0,0]) if attack else 0
        errors.append(hand('l',(.19-.045*a,.16+.08*a,.56+.18*a+.04*victory+.003*wave),turn(-8-18*a,0,0)))
        errors.append(hand('r',(-.22+.13*a,.10+.22*a+.03*f,.48+.26*a+.06*f+.12*victory),turn(-12-45*a-18*f,0,12*a)))
        if defeat:
            errors=[hand('l',settle((.19,.16,.56),(.20,.20,.32)),turn(-8-32*kneel)),hand('r',settle((-.22,.10,.48),(-.20,.20,.28)),turn(-12-23*kneel))]
    elif uid=='wc_u_dwarf_priest':
        a=sample([0,1,1,.4,0]) if active else 0;f=sample([0,.4,1,.3,0]) if attack else 0
        errors.append(hand('r',(-.11,.21+.045*a,.585+.14*a+.03*f+.055*victory+.004*wave),turn(-8+5*a,0,0)))
        errors.append(hand('l',(.29+.005*a,.10+.05*a,.49+.18*a+.07*victory),turn(-20-27*a,0,-12*a)))
        if defeat:errors=[hand('r',settle((-.11,.21,.585),(-.10,.26,.30)),turn(-8-57*kneel)),hand('l',settle((.29,.10,.49),(.24,.12,.28)),turn(-20-15*kneel))]
    else:
        a=sample([0,1,1,.4,0]) if active else 0;f=sample([0,1,1,.4,0]) if attack else 0
        errors.append(hand('l',(.26,.14+.035*a,.51-.025*a+.045*victory),turn(-5-9*a,0,-8)))
        errors.append(hand('r',(-.29-.015*a,.11+.065*a+.09*f,.50+.12*a+.09*f),turn(-30-38*f-38*a,0,14*f)))
        if defeat:errors=[hand('l',settle((.26,.14,.51),(.24,.23,.31)),turn(-5-72*kneel,0,-8+8*kneel)),hand('r',settle((-.29,.11,.50),(-.25,.17,.27)),turn(-30-40*kneel))]
    return max(errors)

def bake_actions(u,arm,out):
    clips=animate(u,arm,out,export_animation=False);maximum={}
    for clip,spec in clips.items():
        action=bpy.data.actions[spec['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0];end=spec['frames'][1]-1;release=spec['release_frame'] or 1;limit=0;previous={}
        for frame in range(1,end+2):
            bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();limit=max(limit,contacts(u,arm,clip,frame,end,release))
            for bone in arm.pose.bones:
                if not bone.name.startswith(('upperarm_','lowerarm_','hand_')):continue
                bone.rotation_euler=bone.rotation_euler.to_quaternion().to_euler('XYZ',previous.get(bone.name,bone.rotation_euler));previous[bone.name]=bone.rotation_euler.copy();bone.keyframe_insert(data_path='rotation_euler',frame=frame,group=bone.name)
        spec['support_hand_bake_samples']=end+1;spec['maximum_support_reach_clamp_m']=limit;maximum[clip]=limit
        if limit>.025:raise RuntimeError('Reach clamp '+clip+' '+str(limit))
        bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=end+1;bpy.context.scene.frame_set(1);export_normalized_copy(out/(spec['action']+'.fbx'),[arm],True,export_fbx_raw)
    return clips,maximum
def explicit_triangles(ob):
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.calc_loop_triangles()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--unit',required=True,choices=sorted(ALLOWED));parser.add_argument('--report',type=Path,required=True);parser.add_argument('--resume-partial',action='store_true');a=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);uid=a.unit;report=a.report.resolve();report.mkdir(parents=True,exist_ok=False)
    (report/'executed-author.py').write_bytes(Path(__file__).read_bytes());units=json.loads((ROOT/'data/units.json').read_text());u=next(x for x in units['units'] if x['id']==uid);out=ROOT/'exports/heroes'/uid;source=ROOT/'art-source/heroes'/uid/(uid+'.blend')
    assert not source.exists(),'Existing source requires incremental refinement, never regeneration'
    if out.exists():
        assert a.resume_partial and not (out/'export_manifest.json').exists(),'Existing published progress must be preserved'
        shutil.copytree(out,report/'retained-partial-export')
    out.mkdir(parents=True,exist_ok=a.resume_partial);source.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.fps=60
    for name in ('BODY','COSTUME','EQUIPMENT','RIG','PRESENTATION_HELPERS','EXPORT'):scene.collection.children.link(bpy.data.collections.new(name))
    visual=copy.deepcopy(u);visual['art']['palette']=PALETTES[uid];mat=material_for(visual,out);arm,p=rig_for(u);g=Geometry();body(g,u,p);equipment_start=len(g.faces);gear(g,u,p);mesh=make_mesh(g,u,arm,mat)
    for ob in (mesh,arm):
        for col in list(ob.users_collection):col.objects.unlink(ob)
        bpy.data.collections['EXPORT'].objects.link(ob)
    bpy.data.collections['RIG'].objects.link(arm);preserve_source_parts(mesh,g,equipment_start)
    explicit_triangles(mesh);export_normalized_copy(out/('SK_'+uid+'.fbx'),[arm,mesh],False,export_fbx_raw)
    lod_collection=bpy.data.collections.new('LOD_SOURCE');scene.collection.children.link(lod_collection);lods=[]
    for index,ratio in ((1,.5),(2,.25)):
        lod=mesh.copy();lod.data=mesh.data.copy();lod.name=f'SK_{uid}_LOD{index}';lod_collection.objects.link(lod);bpy.context.view_layer.objects.active=lod;mod=lod.modifiers.new('WC_SilhouetteReduction','DECIMATE');mod.ratio=ratio;bpy.ops.object.modifier_apply(modifier=mod.name);explicit_triangles(lod)
        export_normalized_copy(out/(lod.name+'.fbx'),[arm,lod],False,export_fbx_raw);lods.append({'lod':index,'triangles':len(lod.data.loop_triangles),'ratio_target':ratio,'visual_acceptance':'pending'});lod.hide_render=True;lod.hide_set(True)
    bpy.ops.wm.save_as_mainfile(filepath=str(report/'unanimated-source.blend'),check_existing=False)
    clips,reach=bake_actions(u,arm,out);action=bpy.data.actions[clips['Idle']['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0];scene.frame_set(1);camera=setup_render(u['height_m']);scene.cycles.samples=12;camera.data.ortho_scale=u['height_m']*1.45
    for label,loc in [('front',(0,4,1.8)),('side',(4,0,1.8)),('back',(0,-4,1.8)),('three-quarter',(3,5,2.7))]:
        camera.location=loc;camera.rotation_euler=(Vector((0,0,u['height_m']*.54))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(report/(label+'.png'));bpy.ops.render.render(write_still=True)
    scene.render.filepath=str(out/'portrait.png');bpy.ops.render.render(write_still=True)
    for clip,spec in clips.items():
        action=bpy.data.actions[spec['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0];scene.frame_set(spec['release_frame'] or (spec['frames'][1] if clip=='Defeat' else spec['frames'][1]//2));scene.render.resolution_x=scene.render.resolution_y=384;scene.cycles.samples=4;scene.render.filepath=str(report/('clip_'+clip+'.png'));bpy.ops.render.render(write_still=True)
    action=bpy.data.actions[clips['Idle']['action']];arm.animation_data.action=action;arm.animation_data.action_slot=action.slots[0];scene.frame_set(1);scene.frame_start=1;scene.frame_end=121;scene.render.resolution_x=scene.render.resolution_y=768;bpy.ops.wm.save_as_mainfile(filepath=str(source),check_existing=False)
    manifest={'status':'authored_exported_rendered_candidate_not_engine_accepted','unit_id':uid,'name':u['name'],'blender_version':bpy.app.version_string,'source_revision':1,'geometry_source_revision':1,'animation_revision':1,'height_m':u['height_m'],'source_sha256':sha(source),'author_script_sha256':sha(report/'executed-author.py'),'units_source_sha256':sha(ROOT/'data/units.json'),'rig_family':u['rig_family'],'rig_revision':'WC_family_v1','bones':len(arm.data.bones),'triangles':len(mesh.data.loop_triangles),'materials':1,'fps':60,'source_forward':'+Y','source_up':'+Z','unit_scale_m':1,'fbx_profile':'tools/blender/profiles/fbx_skeletal_cm_v1.json','normalized_export_revision':1,'normalized_exporter_sha256':sha(ROOT/'tools/blender/normalized_fbx.py'),'exported_coordinate_units':'centimeters in temporary independent copies; source meters','engine_calibration':['reports/WC-330/import-probe/forward_cm-results.json','reports/WC-330/import-probe/all7-comparison.json'],'textures':{'BaseColor':'sRGB','Normal':'linear tangent +Y flat normal with modeled bevels','ORM':'linear R occlusion G roughness B metallic'},'equipment':'weighted within skeletal mesh; visual only','clips':clips,'lods':lods,'source_brief':u['art'],'files':{x.name:sha(x) for x in out.iterdir() if x.is_file()},'open_reviews':['Unreal import/reimport','continuous clip quality','crowded board','LOD appearance','effects and audio'],'report':str(report)}
    (out/'export_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(report/'authoring-result.json').write_text(json.dumps({'unit_id':uid,'source':str(source),'source_sha256':sha(source),'invariants':invariants(arm),'actions':{c:action_curve_digest(bpy.data.actions[s['action']]) for c,s in clips.items()},'reach_clamp_m':reach,'manifest_sha256':sha(out/'export_manifest.json')},indent=2)+'\n')
    saved=sys.argv
    try:
        for collection in ('EXPORT','LOD_SOURCE'):
            sys.argv=['inspect_scene.py','--','--collection',collection,'--require-skin','--output',str(report/(collection+'-inspection.json'))];runpy.run_path(str(ROOT/'tools/blender/inspect_scene.py'),run_name='__main__')
        sys.argv=['audit_motion.py','--','--unit',uid,'--output',str(report/'motion-invariants.json')];runpy.run_path(str(ROOT/'tools/blender/audit_motion.py'),run_name='__main__')
    finally:sys.argv=saved
    print('WC_NEW_FAMILY_HERO_CANDIDATE '+uid+' '+str(len(mesh.data.loop_triangles)),flush=True)
if __name__=='__main__':main()
