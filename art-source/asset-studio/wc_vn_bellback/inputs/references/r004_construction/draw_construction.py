"""Author new vector reference diagrams from explicit coordinates, never edit source art."""
import hashlib
import html
import json
import math
from pathlib import Path

import fitz

HERE = Path(__file__).resolve().parent
G = json.loads((HERE / "construction_spec.json").read_text())
SOURCE = (HERE / G["source_geometry"]).resolve()
R3 = json.loads(SOURCE.read_text())
B = R3["bell_section"]
P = R3["paw"]
COLORS = {"body": "#cadbd0", "bell": "#f2dbad", "mount": "#b38a66", "ink": "#28453d", "line": "#73958a", "motion": "#ae633e"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def body_top(x, y):
    inside = 1 - (x / 800) ** 2 - (y / 900) ** 2
    return 770 + 400 * math.sqrt(max(0, inside))


def inner_y(z):
    profile = B["inner_profile_width_by_z"]
    for (z0, w0), (z1, w1) in zip(profile, profile[1:]):
        if z0 <= z <= z1:
            return w0 + (w1 - w0) * (z - z0) / (z1 - z0)
    raise ValueError(f"Point outside authored inner shell height: {z}")


def foot_at(leg, phase):
    u = (phase + leg["phase_offset"]) % 1
    gait = G["gait"]
    if u < gait["stance_fraction"]:
        dy = gait["stride_half_y"] * (1 - 2 * u / gait["stance_fraction"])
        lift = 0
        contact = True
    else:
        v = (u - gait["stance_fraction"]) / (1 - gait["stance_fraction"])
        dy = -gait["stride_half_y"] + 2 * gait["stride_half_y"] * v
        lift = gait["swing_lift_z"] * math.sin(math.pi * v)
        contact = False
    return (leg["foot"][0], leg["foot"][1] + dy, lift), contact


def leg_points(leg, phase=None):
    foot = leg["foot"] if phase is None else foot_at(leg, phase)[0]
    root = leg["joint"]
    ankle = [foot[0], foot[1], foot[2] + P["height"] * leg["paw_scale"]]
    dy, dz = ankle[1] - root[1], ankle[2] - root[2]
    dist = math.hypot(dy, dz)
    upper, lower = leg["segment_lengths"]
    assert abs(upper - lower) < dist <= upper + lower
    along = (upper * upper - lower * lower + dist * dist) / (2 * dist)
    away = math.sqrt(max(0, upper * upper - along * along))
    bend = leg["bend_sign"]
    knee = [root[0], root[1] + along * dy / dist + bend * away * (-dz) / dist,
            root[2] + along * dz / dist + bend * away * dy / dist]
    return root, knee, ankle


class Drawing:
    def __init__(self, width, height, title, subtitle):
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                      f'<rect width="{width}" height="{height}" fill="#faf8f2"/>']
        self.text(36, 48, title, 27, True)
        self.text(36, 80, subtitle, 16)

    def text(self, x, y, value, size=15, bold=False, color="#28453d", anchor="start"):
        self.parts.append(f'<text x="{x:.3f}" y="{y:.3f}" font-family="sans-serif" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="{color}" text-anchor="{anchor}">{html.escape(str(value))}</text>')

    def line(self, a, b, color="#73958a", width=1.5, dash=""):
        self.parts.append(f'<line x1="{a[0]:.3f}" y1="{a[1]:.3f}" x2="{b[0]:.3f}" y2="{b[1]:.3f}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}" stroke-linecap="round"/>')

    def poly(self, points, fill="none", stroke="#28453d", width=2, close=True, dash=""):
        tag = "polygon" if close else "polyline"
        self.parts.append(f'<{tag} points="'+" ".join(f"{x:.3f},{y:.3f}" for x,y in points)+f'" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" stroke-dasharray="{dash}"/>')

    def ellipse(self, center, rx, ry, fill="none", stroke="#28453d", dash=""):
        self.parts.append(f'<ellipse cx="{center[0]:.3f}" cy="{center[1]:.3f}" rx="{rx:.3f}" ry="{ry:.3f}" fill="{fill}" stroke="{stroke}" stroke-width="1.6" stroke-dasharray="{dash}"/>')

    def rect(self, x, y, width, height, fill="#ffffff", stroke="#d7dfd8"):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="7" fill="{fill}" stroke="{stroke}"/>')

    def dim(self, a, b, label, at):
        self.line(a, b, "#9b7132")
        length = math.dist(a, b)
        dx, dy = (b[0]-a[0])/length, (b[1]-a[1])/length
        for p, sign in ((a, 1), (b, -1)):
            self.poly([(p[0]+sign*7*dx+3*dy,p[1]+sign*7*dy-3*dx), p,
                       (p[0]+sign*7*dx-3*dy,p[1]+sign*7*dy+3*dx)], stroke="#9b7132", close=False)
        self.text(*at, label, 14, color="#9b7132")

    def save(self, name):
        path = HERE / (name + ".svg")
        path.write_text("\n".join(self.parts+["</svg>"])+"\n", encoding="utf-8")
        svg = fitz.open(stream=path.read_bytes(), filetype="svg")
        pdf = fitz.open(stream=svg.convert_to_pdf(), filetype="pdf")
        pdf[0].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False).save(path.with_suffix(".png"))


def transverse():
    d = Drawing(1500, 1130, "BELLBACK / TRANSVERSE CAVITY AND MOUNT", "r004 construction proposal • millimeters • sections derive from the same r003 dimensions • no model measurement")
    d.rect(28, 110, 815, 730)
    d.rect(864, 110, 608, 430)
    d.rect(864, 557, 608, 283)
    d.text(50, 147, "CENTER SECTION  Y = 0", 21, True)
    s, ox, floor = .275, 434, 796
    xy = lambda x,z: (ox+s*x, floor-s*z)
    d.line(xy(-1300, 0), xy(1300, 0), width=2)
    d.line(xy(0, 0), xy(0, 2280), dash="5 5")
    d.ellipse(xy(0, 770), 800*s, 400*s, COLORS["body"])
    ratio = G["bell"]["x_to_y_radius_ratio"]
    outer = [(y*ratio,z) for y,z in B["outer_profile_yz"]]
    inner = [(-w*ratio,z) for z,w in B["inner_profile_width_by_z"]]
    inner += [(w*ratio,z) for z,w in reversed(B["inner_profile_width_by_z"])]
    d.poly([xy(x,z) for x,z in outer], COLORS["bell"])
    d.poly([xy(x,z) for x,z in inner], "#ffffff")
    d.line(xy(0,2160),xy(0,2020),"#9e855f",36*s)
    d.ellipse(xy(0,1660),55*s,55*s,"#be9250")
    d.line(xy(0,2020),xy(0,1660),"#8f673b",16*s)
    d.ellipse(xy(0,2020),12*s,12*s,"#8f673b")
    d.poly([xy(-45,1270),xy(45,1270),xy(45,1320),xy(-45,1320)],COLORS["mount"])
    # Only the perimeter ring and spine cross this actual section; pads live at Y +/-450.
    for sign in (-1,1):
        d.poly([xy(sign*612.4,1270),xy(sign*662.4,1270),xy(sign*662.4,1320),xy(sign*612.4,1320)],COLORS["mount"])
    d.dim(xy(-800,250),xy(800,250),"1600 body envelope",(343,756))
    d.dim(xy(875,1170),xy(875,1270),"100 minimum static gap",(531,484))
    d.line(xy(0,1660),(605,313),"#9b7132")
    d.text(593,290,"Internal striker",15,True)
    d.text(593,315,"110 diameter",14)
    d.text(56,177,"X / Z coordinates",14)
    d.text(67,692,"Body envelope below hollow bell.",15)
    d.text(67,716,"No saddle pads are cut by Y = 0.",15)
    d.text(886,147,"SADDLE SECTION  Y = +450",19,True)
    t, cx, zz = .26, 1168, 635
    q = lambda x,z:(cx+t*x,zz-t*z)
    radius_x=800*math.sqrt(1-(450/900)**2)
    radius_z=400*math.sqrt(1-(450/900)**2)
    d.ellipse(q(0,770),radius_x*t,radius_z*t,COLORS["body"])
    pts=[(-350+700*i/40,body_top(-350+700*i/40,450)) for i in range(41)]
    d.poly([q(-350,1270),q(350,1270)]+[q(x,z) for x,z in reversed(pts)],COLORS["mount"])
    edge=662.4*math.sqrt(1-(450/720)**2)
    d.poly([q(-edge,1270),q(edge,1270),q(edge,1320),q(-edge,1320)],"#9f7752")
    d.dim(q(-350,1390),q(350,1390),"700 saddle width",(1085,265))
    d.text(886,192,"Actual conforming pad, body and crossbeam cut.",14)
    d.text(886,214,"Second identical pad at Y = -450.",14)
    d.text(886,239,"Pad height: 154 mm at center; 201 mm at edges.",14)
    d.text(886,535,"Bell above Z = 1320 omitted from inset.",14)
    d.text(886,589,"OPEN CARRIER / PLAN  X-Y",19,True)
    c, scale = (1160,720),.115
    plan=lambda x,y:(c[0]+scale*x,c[1]-scale*y)
    d.ellipse(c,662.4*scale,720*scale,COLORS["mount"])
    d.ellipse(c,612.4*scale,670*scale,"#ffffff")
    d.poly([plan(-45,-720),plan(45,-720),plan(45,720),plan(-45,720)],COLORS["mount"])
    for y in (-450,450):
        d.poly([plan(-350,y-90),plan(350,y-90),plan(350,y+90),plan(-350,y+90)],"#d1b394")
        ex=662.4*math.sqrt(1-(y/720)**2)
        d.poly([plan(-ex,y-45),plan(ex,y-45),plan(ex,y+45),plan(-ex,y+45)],COLORS["mount"])
    d.text(888,626,"Ring + spine + 2 crossbeams",14)
    d.text(1280,713,"Front",14)
    d.text(1280,736,"+Y up",14)
    d.text(50,882,"CONSTRUCTION DECISIONS",20,True)
    notes=["Bell is an elliptical shell: X half-width = 0.92 x Y half-width at every height; crown target Z = 2200.",
           "Carrier spine matches the r003 longitudinal section. Saddles contact the back at Y = +/-450; they do not fill the central cavity.",
           "Crown hanger anchors at Z 2160; hinge at Z 2020. Clapper rod 360, striker radius 55, bounded +/-12 degree Y/Z swing.",
           "The clapper remains inside a hollow volume. Optional neck bells are separate decorations. No physical striking or acoustic claim.",
           "The proposed 3D shell sample and mount clearances are recorded in geometry_verification.json; real mesh/deformation review is later."]
    for i,line in enumerate(notes):d.text(50,917+i*31,line,16)
    d.save("transverse_mount_sections")


def project(point, view, ox, floor, s):
    x,y,z=point
    u={"front":-x,"back":x,"right":y,"left":-y}[view]
    return ox+s*u,floor-s*z


def fullbody():
    d=Drawing(1240,1500,"BELLBACK / SHARED CONSTRUCTION LANDMARKS","r004 proposal • four orthogonal projections of one dimension set • aesthetic master remains the selected creature")
    panels=[("front",35,112,"FRONT / looking from +Y"),("right",640,112,"RIGHT SIDE / looking from +X"),
            ("back",35,687,"BACK / looking from -Y"),("left",640,687,"LEFT SIDE / looking from -X")]
    scale=.215
    for view,x,y,title in panels:
        d.rect(x,y,565,555)
        d.text(x+18,y+30,title,19,True)
        ox,floor=x+281,y+507
        q=lambda p:project(p,view,ox,floor,scale)
        horiz=0 if view in ("front","back") else 1
        d.line((x+25,floor),(x+540,floor),width=2)
        d.line(q([0,0,0]),q([0,0,2250]),dash="4 5")
        for level in (420,770,1170,1320,2200):
            d.line((x+22,floor-scale*level),(x+544,floor-scale*level),"#dbe4dd",1,"4 4")
        depth_axis=1 if horiz==0 else 0
        depth_sign=1 if view in ("front","right") else -1
        for leg in sorted(G["legs"],key=lambda a:depth_sign*a["foot"][depth_axis]):
            hidden=depth_sign*leg["foot"][depth_axis]<0
            roots=leg_points(leg)
            d.poly([q(p) for p in roots],stroke="#769386",width=2 if hidden else 27*leg["paw_scale"],close=False,dash="4 4" if hidden else "")
            d.poly([q(p) for p in roots],stroke="#375b4c",width=1.5,close=False)
            foot=leg["foot"]; sc=leg["paw_scale"]
            if horiz==0:
                coords=[[-220,80],[-210,240],[-125,420],[125,420],[210,240],[220,80]]
                points=[[foot[0]+xx*sc,foot[1],zz*sc] for xx,zz in coords]
            else:
                coords=[[-275,0],[-245,200],[-150,420],[90,420],[170,235],[245,105],[245,0]]
                points=[[foot[0],foot[1]+yy*sc,zz*sc] for yy,zz in coords]
            d.poly([q(p) for p in points],"none" if hidden else COLORS["body"],stroke="#8da79a" if hidden else "#28453d",dash="4 4" if hidden else "")
            for toe in ([] if hidden else P["toes"]):
                toe_center=[foot[0]+toe["center_x"]*sc,foot[1]+toe["center_y"]*sc,85*sc]
                d.ellipse(q(toe_center),(43 if horiz==0 else 70)*sc*scale,85*sc*scale,"#e6ede1")
        body=G["body"];d.ellipse(q(body["center"]),body["radii"][horiz]*scale,400*scale,COLORS["body"])
        d.line(q(G["tail"]["base"]),q(G["tail"]["tip"]),"#74927c",20)
        h=G["head"]
        # Rear view deliberately draws the hidden head as an outline, not a second visible face.
        if view=="back":
            d.ellipse(q(h["center"]),h["radii"][0]*scale,h["radii"][2]*scale,"none","#8aafa0","4 4")
        else:
            d.ellipse(q(h["center"]),h["radii"][horiz]*scale,h["radii"][2]*scale,"#b8cbb7")
            d.ellipse(q(h["muzzle_center"]),h["muzzle_radii"][horiz]*scale,100*scale,"#adc0a7")
            eyes=h["eye_centers"] if view=="front" else [h["eye_centers"][1 if view=="right" else 0]]
            for e in eyes:d.ellipse(q(e),5,4,"#3b493b")
        if horiz==1:
            for yy in (-450,450):
                d.poly([q([0,yy-90,body_top(0,yy-90)]),q([0,yy+90,body_top(0,yy+90)]),q([0,yy+90,1270]),q([0,yy-90,1270])],COLORS["mount"])
        d.poly([q([0,-720,1270]),q([0,720,1270]),q([0,720,1320]),q([0,-720,1320])] if horiz==1 else [q([-662.4,0,1270]),q([662.4,0,1270]),q([662.4,0,1320]),q([-662.4,0,1320])],COLORS["mount"])
        profile=[]
        for v,z in B["outer_profile_yz"]:
            profile.append([v*.92,0,z] if horiz==0 else [0,v,z])
        d.poly([q(p) for p in profile],COLORS["bell"])
        # Right branch is always the same +X object; hidden in left-side projection.
        branch=G["branch"]
        d.poly([q(branch[k]) for k in ("base","elbow","tip")],stroke="#a78659" if view!="left" else "#a3ada2",width=7,close=False,dash="4 4" if view=="left" else "")
        d.ellipse(q([0,0,2200]),3,3,"#9b7132")
        if view=="front":
            d.text(x+15,y+549,"Anatomical RIGHT is viewer left; branch is +X.",14)
            d.dim((x+30,floor),(x+30,floor-2200*scale),"2200",(x+36,y+293))
        elif view=="back":
            d.text(x+15,y+549,"Anatomical RIGHT is viewer right; head hidden.",14)
        else:
            direction="right" if view=="right" else "left"
            d.text(x+15,y+549,f"Nose faces {direction}; paired limbs overlap in projection.",14)
    d.text(44,1303,"ONE COORDINATE SOURCE / PROPOSED DIMENSION TARGETS",20,True)
    lines=["Body: 1800 long x 1600 wide; center Z 770, back top Z 1170. Bell top Z 2200, rim Z 1320.",
           "Head: 660 wide x 500 long x 460 high; nose envelope ends Y +1150. Tail tip Y -1060; root stub radius 55.",
           "Neutral feet: fore X +/-550, Y +550; hind X +/-490, Y -550. Four toes on every paw; hind scale 0.90.",
           "Dashed marks are hidden geometry or datums. Contours express mass envelopes; r001 controls face, bark and moss character.",
           "2 m logical cell is unchanged. Head/tail may visually overhang; crowding and camera readability must be tested in the actual blockout."]
    for i,line in enumerate(lines):d.text(44,1336+i*29,line,15)
    d.save("full_body_landmarks")


def gait():
    d=Drawing(1560,1270,"BELLBACK / GAIT CONTACTS AND SHOULDER SWEEP","r004 animation intent • four-beat walk proposal • one grounded leg system • sampled geometry is not an animation review")
    for i,phase in enumerate((.125,.375,.625,.875)):
        x=28+i*384
        d.rect(x,112,364,485)
        d.text(x+17,147,f"CYCLE {phase:.3f}",19,True)
        scale=.14; cx,cy=x+182,340
        xy=lambda a,b:(cx+scale*a,cy-scale*b)
        d.ellipse((cx,cy),800*scale,900*scale,"#edf2eb")
        poses=[(leg,*foot_at(leg,phase)) for leg in G["legs"]]
        contacts=[foot for _,foot,contact in poses if contact]
        centroid=[sum(p[j] for p in contacts)/len(contacts) for j in (0,1)]
        angles=sorted(contacts,key=lambda p:math.atan2(p[1]-centroid[1],p[0]-centroid[0]))
        d.poly([xy(p[0],p[1]) for p in angles],"#e5ece0",stroke="#73958a",dash="5 4")
        for leg,foot,contact in poses:
            col="#567f69" if contact else "#bb714b"
            d.ellipse(xy(foot[0],foot[1]),220*scale*leg["paw_scale"],275*scale*leg["paw_scale"],col)
            d.text(*xy(foot[0],foot[1]+20),leg["id"],13,True,"#ffffff","middle")
        d.ellipse(xy(*centroid),4,4,"#4a5850")
        airborne=[leg["id"] for leg,_,contact in poses if not contact][0]
        d.text(x+18,531,f"Swing: {airborne}   /   three stance feet",15,True)
        d.text(x+18,557,"Dot: support planning centroid, not COM.",13)
        d.text(x+18,580,"+Y forward is up; +X right is right.",13)
    d.rect(28,620,848,452)
    d.rect(895,620,637,452)
    d.text(50,656,"FORELEG / BOUNDED SIDE SWEEP",20,True)
    s,ox,ground=.22,185,1008
    q=lambda y,z:(ox+s*y,ground-s*z)
    d.line((56,ground),(846,ground),width=2)
    d.line((56,ground-s*1270),(420,ground-s*1270),"#9b7132",2,"5 4")
    d.text(53,685,"Frame underside Z 1270; joint capsule top <= 970.",15)
    leg=next(a for a in G["legs"] if a["id"]=="FR")
    for j in range(17):
        phase=j/16
        points=leg_points(leg,phase)
        d.poly([q(p[1],p[2]) for p in points],stroke="#9bb5a5",width=1.5,close=False)
    points=leg_points(leg,.875)
    d.poly([q(p[1],p[2]) for p in points],stroke="#446c57",width=7,close=False)
    for p in points:d.ellipse(q(p[1],p[2]),5,5,"#446c57")
    d.ellipse(q(580,900),70*s,70*s,"none","#ae633e","4 3")
    foot,contact=foot_at(leg,.875)
    paw_points=[(-275,0),(-245,200),(-150,420),(90,420),(170,235),(245,105),(245,0)]
    d.poly([q(foot[1]+y,foot[2]+z) for y,z in paw_points],COLORS["body"])
    d.text(460,736,"Shoulder Y 580 / Z 900",15,True)
    d.text(460,766,"Upper + lower lengths: 260 + 260",15)
    d.text(460,796,"Fore wrist: Z 420 + swing lift",15)
    d.text(460,826,"Foot reaches Y 430 .. 670",15)
    d.text(460,856,"Swing lift 0 .. 70; body bob 0",15)
    d.text(460,886,"Hind lengths: 250 + 240",15)
    d.text(460,916,"Hind ankle: Z 378 + swing lift",15)
    d.text(50,1043,"Capsules bound proposed joints. Actual flesh, skinning and contacts require later mesh/rig tests.",14)
    d.text(915,656,"CONTACT AND ATTACHMENT CONTRACT",19,True)
    lines=["1.6 s cycle; 75% stance; one swing leg at a time.",
           "Relative stance travel: +120 to -120 mm.",
           "Root travel: +320 mm / cycle balances stance drift.",
           "Swing order: HL, FR, HR, FL in this phase convention.",
           "Stance pads and all four toe bottoms stay at Z = 0.",
           "Feet stay within a proposed 2 m X/Y animation cell.",
           "Bell and frame follow the body root as rigid objects.",
           "Clapper owns only its bounded +/-12 degree swing.",
           "No bob, tilt, physics or contact solver is proved here.",
           "Turning, attack braces, hits and defeat need rig review."]
    for i,line in enumerate(lines):d.text(915,695+i*32,line,15)
    d.text(48,1120,"WHAT THIS CLOSES FOR REFERENCE REVIEW",20,True)
    d.text(48,1154,"A four-leg skeleton route, neutral contacts, a continuous proposed foot path and explicit mount separation can be built without guessing.",16)
    d.text(48,1187,"What it does not close: believable weight, planted paws on an actual mesh, motion transitions, bell acoustics, or normal-speed play quality.",16)
    d.text(48,1220,"Geometry checks sample 193 gait phases and 97 clapper angles; see the verification report for scope and measured values from these equations.",16)
    d.save("gait_contacts_and_sweep")


def verify():
    assert sha(SOURCE)==G["source_geometry_sha256"], "r003 source changed"
    assert G["body"]["radii"]==[800,900,400]
    assert G["body"]["center"]==[0,B["body_ellipse_center_y"],B["body_ellipse_center_z"]]
    assert G["mount"]["bottom_z"]==B["carrier_frame_bottom_z"]
    assert G["mount"]["top_z"]==B["carrier_frame_top_z"]
    assert G["mount"]["crossbeam_centers_y"]==B["saddle_centers_y"]
    assert len(P["toes"])==4 and len({t["id"] for t in P["toes"]})==4
    min_shell=1.;max_ik=0.;max_capsule_z=0.;min_stance=max_stance=3
    min_floor=1e9;foot_extents=[1e9,-1e9,1e9,-1e9];max_stance_world_error=0.
    for angle_index in range(97):
        angle=math.radians(-12+angle_index*.25)
        cy=360*math.sin(angle);cz=2020-360*math.cos(angle)
        for lat in range(-90,91,6):
            latitude=math.radians(lat)
            for lon in range(0,360,6):
                longitude=math.radians(lon)
                x=55*math.cos(latitude)*math.cos(longitude)
                y=cy+55*math.cos(latitude)*math.sin(longitude)
                z=cz+55*math.sin(latitude)
                wy=inner_y(z);wx=.92*wy
                normalized=(x/wx)**2+(y/wy)**2
                min_shell=min(min_shell,1-normalized)
                assert normalized<1
        for i in range(101):
            y=cy*i/100;z=2020+(cz-2020)*i/100
            wy=inner_y(z);wx=.92*wy
            normalized=(8/wx)**2+((abs(y)+8)/wy)**2
            assert normalized<1
    neutral=[1e9,-1e9,1e9,-1e9]
    for leg in G["legs"]:
        sc=leg["paw_scale"];x,y,_=leg["foot"]
        neutral=[min(neutral[0],x-220*sc),max(neutral[1],x+220*sc),min(neutral[2],y-275*sc),max(neutral[3],y+275*sc)]
    for n in range(193):
        phase=n/192;stance=0
        for leg in G["legs"]:
            foot,contact=foot_at(leg,phase);stance+=int(contact)
            sc=leg["paw_scale"]
            foot_extents=[min(foot_extents[0],foot[0]-220*sc),max(foot_extents[1],foot[0]+220*sc),min(foot_extents[2],foot[1]-275*sc),max(foot_extents[3],foot[1]+275*sc)]
            min_floor=min(min_floor,foot[2])
            root,knee,ankle=leg_points(leg,phase)
            for (a,b),target in zip(((root,knee),(knee,ankle)),leg["segment_lengths"]):
                max_ik=max(max_ik,abs(math.dist(a,b)-target))
            max_capsule_z=max(max_capsule_z,max(root[2],knee[2])+70,max(knee[2],ankle[2])+55)
            if contact:
                assert abs(foot[2])<1e-9
                epsilon=1e-6
                later,later_contact=foot_at(leg,phase+epsilon)
                if later_contact and abs(later[1]-foot[1])<1:
                    max_stance_world_error=max(max_stance_world_error,abs(later[1]-foot[1]+320*epsilon))
        min_stance=min(min_stance,stance);max_stance=max(max_stance,stance)
        assert stance==3
    assert min_shell>0 and max_ik<1e-8
    assert min_floor>=-1e-8 and max_capsule_z<1270
    assert max_stance_world_error<1e-8
    assert neutral[1]-neutral[0]<=1700 and neutral[3]-neutral[2]<=1700
    assert all(abs(v)<=1000 for v in foot_extents)
    return {"schema":"wonder_vnext.bellback_geometry_check.2","status":"pass_proposed_geometry_only",
            "source_geometry_sha256":sha(SOURCE),"construction_spec_sha256":sha(HERE/"construction_spec.json"),
            "checks":{"four_unique_toes":True,"r003_dimension_consistency":True,"clapper_inside_elliptical_cavity":True,
                      "leg_lengths_reconstructed":True,"three_stance_feet_each_sample":True,"contact_floor_nonnegative":True,
                      "root_travel_cancels_stance_sliding_in_declared_equations":True,"neutral_contact_envelope_within_1700":True,"stride_envelope_within_2000":True},
            "sample_counts":{"gait_phases":193,"clapper_angles":97,"striker_sphere_latitude_step_degrees":6,"striker_sphere_longitude_step_degrees":6,"rod_samples_per_angle":101},
            "results":{"minimum_striker_elliptical_shell_implicit_margin":min_shell,"max_ik_length_error_mm":max_ik,"max_stance_world_drift_error_mm":max_stance_world_error,
                       "max_limb_capsule_z_mm":max_capsule_z,"minimum_limb_to_carrier_vertical_gap_mm":1270-max_capsule_z,"minimum_body_to_carrier_vertical_gap_mm":100,
                       "neutral_foot_envelope_xy_mm":[neutral[1]-neutral[0],neutral[3]-neutral[2]],"stride_foot_bounds_xxyy_mm":foot_extents,"stance_count_range":[min_stance,max_stance]},
            "limits":["Authored mathematical envelopes and kinematics only; not measurements of a mesh, rig, mass, physical joint, or game engine.","Finite sampling is not a formal continuous collision proof. Capsule ranges and frame gap are separate analytic bounds for the stated no-bob pose.","Anatomy, actual contact deformation, turning/attack/hit/defeat, camera visibility and animation quality remain later stage tests.","No human reference approval has been issued."],
            "renderer":"PyMuPDF "+fitz.VersionBind,"artifacts":{}}


if __name__=="__main__":
    transverse();fullbody();gait()
    result=verify()
    result["artifacts"]={p.name:sha(p) for pattern in ("*.svg","*.png") for p in sorted(HERE.glob(pattern))}
    (HERE/"geometry_verification.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"results":result["results"],"rendered_images":len(list(HERE.glob("*.png")))},indent=2))
