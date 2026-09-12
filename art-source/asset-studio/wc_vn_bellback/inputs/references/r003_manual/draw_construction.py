"""Render newly authored vector construction proposals; never edits reference images."""
import hashlib
import html
import json
import math
from pathlib import Path

import fitz

HERE = Path(__file__).resolve().parent
G = json.loads((HERE / "construction_geometry.json").read_text())


class Drawing:
    def __init__(self, width, height, title, subtitle):
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                      f'<rect width="{width}" height="{height}" fill="#faf8f2"/>']
        self.text(42, 53, title, "title")
        self.text(42, 88, subtitle, "sub")

    def add(self, value):
        self.parts.append(value)

    def text(self, x, y, value, cls="note", anchor="start"):
        size={"title":30,"sub":17,"head":21,"note":16,"small":14,"dim":15,"label":15}[cls]
        weight="bold" if cls in ("title","head","label") else "normal"
        color="#8d6529" if cls=="dim" else "#526267" if cls=="sub" else "#27363c"
        self.add(f'<text x="{x:.2f}" y="{y:.2f}" font-family="sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{html.escape(str(value))}</text>')

    def line(self, x1, y1, x2, y2, color="#6c7b7b", width=1.5, dash=""):
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>')

    def ellipse(self, x, y, rx, ry, fill, stroke="#45675e", ident="", dash=""):
        self.add(f'<ellipse id="{ident}" cx="{x:.2f}" cy="{y:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-dasharray="{dash}"/>')

    def dim(self, x1, y1, x2, y2, label, tx, ty):
        self.line(x1,y1,x2,y2,"#8d6529",1.4)
        length=math.hypot(x2-x1,y2-y1);dx,dy=(x2-x1)/length,(y2-y1)/length
        for x,y,sign in ((x1,y1,1),(x2,y2,-1)):
            points=[(x+sign*8*dx+4*dy,y+sign*8*dy-4*dx),(x,y),(x+sign*8*dx-4*dy,y+sign*8*dy+4*dx)]
            self.add('<polyline points="'+" ".join(f"{a},{b}" for a,b in points)+'" fill="none" stroke="#8d6529" stroke-width="1.4"/>')
        self.text(tx, ty, label, "dim")

    def save(self, name):
        svg = HERE / (name + ".svg")
        svg.write_text("\n".join(self.parts + ["</svg>"]) + "\n", encoding="utf-8")
        document = fitz.open(stream=svg.read_bytes(), filetype="svg")
        page = document.convert_to_pdf()
        pdf = fitz.open(stream=page, filetype="pdf")
        pdf[0].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False).save(HERE / (name + ".png"))
        return svg


def paws():
    p = G["paw"]
    d = Drawing(1560, 1030, "BELLBACK / FOUR-TOE PAW CONSTRUCTION",
                "New engineering proposal • millimeters • shared coordinates across projections • not matched to image cameras")
    for x in (30, 540, 1050):
        d.add(f'<rect x="{x}" y="125" width="480" height="590" rx="8" fill="#ffffff" stroke="#d8dfd9"/>')
    d.text(55, 165, "FRONT PROJECTION  X / Z", "head")
    d.text(565, 165, "SIDE PROJECTION  Y / Z", "head")
    d.text(1075, 165, "SOLE PROJECTION  X / Y", "head")
    s = .68
    x0, ground = 270, 625
    front = lambda x, z: (x0 + s*x, ground - s*z)
    # This shared envelope is a proposed primary paw shape, not traced raster anatomy.
    coords = [(-220,80),(-210,240),(-125,420),(125,420),(210,240),(220,80)]
    path = "M" + " L".join(f"{front(x,z)[0]},{front(x,z)[1]}" for x,z in coords) + " Z"
    d.add(f'<path d="{path}" fill="#c6d8cf" stroke="#45675e" stroke-width="2"/>')
    for toe in p["toes"]:
        x, z = front(toe["center_x"],p["toe_center_z"])
        d.ellipse(x,z,p["toe_radius_x"]*s,p["toe_radius_z"]*s,"#edf2e8",ident="front_"+toe["id"])
        d.text(x, 656, toe["id"], "label", "middle")
    d.line(74, ground, 467, ground, "#27363c",2)
    d.dim(*front(-220,-95),*front(220,-95),"440 target",210,710)
    d.dim(*front(-270,0),*front(-270,420),"420",64,487)
    d.text(90,205,"Four blunt digits; no opposable thumb.","note")
    d.text(90,232,"+X = anatomical right (diagram axis).","small")
    # Four toe records remain identifiable where projections overlap.
    x0, s = 780, .64
    side = lambda y,z: (x0+s*y,ground-s*z)
    outline=[(-275,0),(-245,200),(-150,420),(90,420),(170,235),(245,105),(245,0)]
    path="M"+" L".join(f"{side(y,z)[0]},{side(y,z)[1]}" for y,z in outline)+" Z"
    d.add(f'<path d="{path}" fill="#c6d8cf" stroke="#45675e" stroke-width="2"/>')
    for toe in p["toes"]:
        x,z=side(toe["center_y"],p["toe_center_z"])
        d.ellipse(x,z,p["toe_radius_y"]*s,p["toe_radius_z"]*s,"none",ident="side_"+toe["id"],dash="6 4")
    d.line(584,ground,986,ground,"#27363c",2)
    d.dim(*side(-275,-95),*side(275,-95),"550 target",729,710)
    d.text(583,205,"+Y forward →   +Z upward","small")
    d.text(583,234,"Toe contours overlap in projection.","note")
    d.text(583,262,"T1 / T4: Y 155   T2 / T3: Y 175","small")
    d.text(583,288,"Side view does not change toe count.","small")
    x0,y0,s=1290,449,.64
    sole=lambda x,y:(x0+s*x,y0-s*y)
    d.ellipse(x0,y0,220*s,275*s,"#c6d8cf",ident="sole_envelope")
    d.ellipse(*sole(*p["pad_center"]),p["pad_radii"][0]*s,p["pad_radii"][1]*s,"#7ca091",ident="sole_contact_pad")
    for toe in p["toes"]:
        x,y=sole(toe["center_x"],toe["center_y"])
        d.ellipse(x,y,p["toe_radius_x"]*s,p["toe_radius_y"]*s,"#edf2e8",ident="sole_"+toe["id"])
        d.text(x,y+5,toe["id"],"label","middle")
    d.text(1090,205,"+Y forward ↑    +X right →","small")
    d.text(1126,653,"One continuous central contact pad.","small")
    d.dim(*sole(-220,-330),*sole(220,-330),"440 target",1230,691)
    d.line(32,754,1528,754,"#bccbc3")
    d.text(48,797,"SHARED TOE CENTERS / PROPOSED GEOMETRY", "head")
    for i,toe in enumerate(p["toes"]):
        d.text(50+i*370,834,f'{toe["id"]}: X {toe["center_x"]}, Y {toe["center_y"]}, Z 85',"note")
    d.text(48,874,"Toe radii: X 43 / Y 70 / Z 85 mm. Hind paw: uniform 0.90 scale; retain exactly four named toes.","note")
    d.text(48,909,"Mirror complete paw assemblies for left/right. Gait, joint placement and body attachment need a separate pose review.","note")
    d.text(48,963,"PROPOSED CONSTRUCTION • HUMAN REFERENCE APPROVAL PENDING • NO 3D MODEL OR RASTER MEASUREMENT", "label")
    return d.save("paw_four_toe_proposal")


def bell():
    b=G["bell_section"]
    d=Drawing(1560,1140,"BELLBACK / DORSAL BELL LONGITUDINAL SECTION",
              "New Y/Z engineering proposal • dimensions in millimeters • static section and limited visual swing only")
    origin_x,base,scale=470,945,.35
    project=lambda y,z:(origin_x+y*scale,base-z*scale)
    d.add('<rect x="32" y="122" width="952" height="885" rx="8" fill="#ffffff" stroke="#d8dfd9"/>')
    d.add('<rect x="1010" y="122" width="515" height="885" rx="8" fill="#f0f4ed" stroke="#d8dfd9"/>')
    # Body/legs are envelope drawings, not completed character anatomy.
    d.ellipse(*project(0,770),900*scale,400*scale,"#c6d8cf",ident="body_envelope")
    for y in (-550,550):
        x,z=project(y-160,600)
        d.add(f'<rect x="{x}" y="{z}" width="{320*scale}" height="{600*scale}" rx="35" fill="#c6d8cf" stroke="#45675e" stroke-width="2"/>')
    d.line(*project(-1080,0),*project(1380,0),"#27363c",2)
    outer=b["outer_profile_yz"]
    inner=[(-w,z) for z,w in b["inner_profile_width_by_z"]]+[(w,z) for z,w in reversed(b["inner_profile_width_by_z"])]
    path=lambda pts:"M"+" L".join(f"{project(y,z)[0]},{project(y,z)[1]}" for y,z in pts)+" Z"
    d.add(f'<path id="main_bell_shell" d="{path(outer)} {path(inner)}" fill="#c9aa64" fill-rule="evenodd" stroke="#8d6529" stroke-width="2.4"/>')
    for center in b["saddle_centers_y"]:
        left,right=center-b["saddle_half_length"],center+b["saddle_half_length"]
        bottom=[(y,770+400*math.sqrt(1-(y/900)**2)) for y in [right-(right-left)*i/12 for i in range(13)]]
        points=[(left,1270),(right,1270)]+bottom
        d.add(f'<path d="{path(points)}" fill="#bca584" stroke="#76604a" stroke-width="2"/>')
    x,z=project(-720,1320)
    d.add(f'<rect id="carrier_frame" x="{x}" y="{z}" width="{1440*scale}" height="{50*scale}" fill="#798b82" stroke="#40594d" stroke-width="2"/>')
    py,pz=b["pivot_y"],b["pivot_z"]
    # Draw the sweep outline, then each stop position and its rod.
    samples=[]
    for angle in range(-12,13):
        t=math.radians(angle)
        samples.append(project(py+b["clapper_length"]*math.sin(t),pz-b["clapper_length"]*math.cos(t)))
    d.add('<polyline points="'+" ".join(f"{x},{y}" for x,y in samples)+'" fill="none" stroke="#b6523b" stroke-width="3"/>')
    for angle in (-12,12):
        t=math.radians(angle);y=py+360*math.sin(t);z=pz-360*math.cos(t)
        d.line(*project(py,pz),*project(y,z),"#b6523b",2,"6 4")
        d.ellipse(*project(y,z),55*scale,55*scale,"none","#b6523b",dash="6 4")
    d.line(*project(0,2120),*project(py,pz),"#40594d",7)
    d.line(*project(py,pz),*project(py,pz-360),"#40594d",6)
    d.ellipse(*project(py,pz-360),55*scale,55*scale,"#40594d",ident="internal_striker")
    d.ellipse(*project(py,pz),12,12,"#fff6d6","#8d6529",ident="crown_suspension")
    d.line(*project(-980,1320),*project(-760,1320),"#8d6529",1.5,"5 4")
    d.dim(*project(-995,0),*project(-995,2200),"2200 target",52,400)
    d.dim(*project(350,1170),*project(350,1605),"435 body gap",600,464)
    d.dim(*project(-350,1320),*project(-350,1605),"285 carrier gap",198,424)
    d.line(*project(0,1605),*project(350,1605),"#8d6529",1,"5 4")
    d.line(*project(0,1170),*project(350,1170),"#8d6529",1,"5 4")
    d.line(*project(-720,1320),*project(-780,1320),"#8d6529")
    d.text(*project(-1150,1250),"Rim Z 1320", "dim")
    d.text(*project(-970,750),"Body envelope", "label")
    d.text(*project(-970,670),"not final anatomy", "small")
    d.text(*project(720,1280),"Carrier + saddles", "small")
    d.line(*project(730,1300),*project(620,1310),"#526267")
    d.text(*project(290,1990),"Pivot Z 2020", "label")
    d.text(*project(290,1900),"Internal rod 360", "small")
    d.text(*project(290,1810),"Striker radius 55", "small")
    d.text(*project(320,1640),"Stops ±12°", "label")
    d.text(71,982,"Section axis: +Y forward →    +Z upward ↑", "small")
    d.text(1034,167,"ASSEMBLY AND LIMITS", "head")
    entries=[("MAIN BELL",["Hollow arched shell reaches Z 2200.","Crown suspension supports an internal", "rod and striker; the small neck pendants", "are separate decorative parts."]),
             ("BODY AND MOUNT",["Body-top target: Z 1170 maximum.","Two contoured saddle pads support a", "new proposed carrier at Z 1270–1320.","Shell rim seats on the carrier top."]),
             ("CLEARANCE",["At rest: striker bottom Z 1605.","Body gap 435; carrier gap 285.","The full ±12° sweep is checked against", "the declared section cavity and body."]),
             ("WHAT THE SWING MEANS",["Small visual motion with hard stops.","No physical acoustics or shell strike is", "claimed by this engineering diagram.","Rod and striker never pass through bark."]),
             ("STILL TO RECONCILE",["Transverse bell/body clearance; gait and", "shoulder sweeps; mount fasteners; final", "front/side body proportions. This section", "does not clear the formal reference gate."])]
    y=212
    for heading,lines in entries:
        d.text(1034,y,heading,"label");y+=26
        for line in lines:d.text(1034,y,line,"note");y+=24
        y+=22
    d.text(42,1056,"CONTROL AUTHORITY: this proposed section replaces the r002 exterior-bell clapper inset only; selected creature identity remains the art anchor.","note")
    d.text(42,1096,"PROPOSED CONSTRUCTION • HUMAN REFERENCE APPROVAL PENDING • NO MEASUREMENTS RECOVERED FROM RASTER ART", "label")
    return d.save("bell_internal_clearance_proposal")


def validate_geometry():
    p,b=G["paw"],G["bell_section"]
    assert [toe["id"] for toe in p["toes"]]==["T1","T2","T3","T4"]
    assert len({toe["center_x"] for toe in p["toes"]})==4
    for toe in p["toes"]:
        assert abs(toe["center_x"])+p["toe_radius_x"]<=p["width"]/2
        assert abs(toe["center_y"])+p["toe_radius_y"]<=p["length"]/2
    def half_width(z):
        for (z1,w1),(z2,w2) in zip(b["inner_profile_width_by_z"],b["inner_profile_width_by_z"][1:]):
            if z1<=z<=z2:return w1+(w2-w1)*(z-z1)/(z2-z1)
        raise AssertionError(f"Clapper point outside cavity height: {z}")
    gaps={"striker_to_body_mm":float("inf"),"striker_to_carrier_mm":float("inf"),"striker_to_shell_horizontal_mm":float("inf"),"rod_to_shell_horizontal_mm":float("inf")}
    for i in range(97):
        theta=math.radians(-12+i*.25)
        y=b["pivot_y"]+b["clapper_length"]*math.sin(theta)
        z=b["pivot_z"]-b["clapper_length"]*math.cos(theta)
        for step in range(361):
            a=math.radians(step)
            by=y+b["clapper_striker_radius"]*math.cos(a)
            bz=z+b["clapper_striker_radius"]*math.sin(a)
            body_z=770+400*math.sqrt(max(0,1-(by/900)**2))
            gaps["striker_to_body_mm"]=min(gaps["striker_to_body_mm"],bz-body_z)
            gaps["striker_to_carrier_mm"]=min(gaps["striker_to_carrier_mm"],bz-b["carrier_frame_top_z"])
            gaps["striker_to_shell_horizontal_mm"]=min(gaps["striker_to_shell_horizontal_mm"],half_width(bz)-abs(by))
        for step in range(101):
            f=step/100
            ry=b["pivot_y"]+(y-b["pivot_y"])*f
            rz=b["pivot_z"]+(z-b["pivot_z"])*f
            gaps["rod_to_shell_horizontal_mm"]=min(gaps["rod_to_shell_horizontal_mm"],half_width(rz)-abs(ry)-b["clapper_rod_radius"])
    assert all(value>0 for value in gaps.values()), gaps
    return {"toe_count":4,"paw_dimensions_mm":[p["width"],p["length"],p["height"]],
            "sampled_swing_degrees":[-12,12],"swing_step_degrees":.25,"striker_perimeter_step_degrees":1,
            "minimum_sampled_clearances":{key:round(value,3) for key,value in gaps.items()},
            "scope":"Declared static 2D section and bounded clapper sweep only; not actual 3D geometry or motion acceptance."}


def main():
    checks=validate_geometry()
    paths=[paws(),bell()]
    import xml.etree.ElementTree as ET
    paw=ET.parse(paths[0]);ids=[item.attrib.get("id") for item in paw.iter()]
    for projection in ("front","side","sole"):
        assert all(ids.count(projection+"_T"+str(i))==1 for i in range(1,5))
    checks.update(schema="wonder_vnext.vector_construction_verification.1",renderer="PyMuPDF "+fitz.VersionBind,
                  vector_structure_pass=True,geometric_proposal_checks_pass=True,image_visual_review="not_recorded_by_script",
                  formal_reference_approval="not_received",artifacts_sha256={})
    for name in ("construction_geometry.json","draw_construction.py","paw_four_toe_proposal.svg","paw_four_toe_proposal.png","bell_internal_clearance_proposal.svg","bell_internal_clearance_proposal.png"):
        checks["artifacts_sha256"][name]=hashlib.sha256((HERE/name).read_bytes()).hexdigest()
    (HERE/"geometry_verification.json").write_text(json.dumps(checks,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(checks,indent=2))


if __name__=="__main__":main()
