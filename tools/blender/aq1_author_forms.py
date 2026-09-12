"""Ada AQ1 semantic surface study on an isolated copy of the existing rig."""
import argparse, json, math, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/blender'))
from refine_update_ada import invariants,use_clip
from aq1_capture import setup,render_view
PI=math.pi
PARTS=[];ARM=None;COL=None;MATS={}

def rgb(h):
    values=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in values)

def make_material(key,h,rough=.5,metal=0):
    m=bpy.data.materials.new('AQ1_'+key);m.use_nodes=True;m.diffuse_color=(*rgb(h),1)
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb(h),1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    MATS[key]=m;return m

def mesh(name,verts,faces,mat,bone='head',smooth=True,weights=None):
    data=bpy.data.meshes.new(name+'_surface');data.from_pydata(verts,[],faces);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    ob=bpy.data.objects.new(name,data);COL.objects.link(ob);data.materials.append(MATS[mat]);ob['aq1_semantic_part']=name
    for poly in data.polygons:poly.use_smooth=smooth
    if weights:
        for i,ws in enumerate(weights):
            total=sum(ws.values())
            for key,w in ws.items():
                vg=ob.vertex_groups.get(key) or ob.vertex_groups.new(name=key);vg.add([i],w/total,'REPLACE')
    else:ob.vertex_groups.new(name=bone).add(list(range(len(verts))),1,'REPLACE')
    ob.modifiers.new('AQ1_Skin','ARMATURE').object=ARM
    uv=data.uv_layers.new(name='UVMap')
    # Semantic surfaces are unwrap/packed together by the later bake stage.
    for face in data.polygons:
        for li in face.loop_indices:
            co=data.vertices[data.loops[li].vertex_index].co;uv.data[li].uv=(co.x,co.z)
    PARTS.append(ob);return ob

def ellipsoid(name,center,radii,mat,bone='head',rings=10,segments=20):
    vs=[];fs=[]
    for j in range(rings+1):
        a=PI*(j+.001)/(rings+.002)
        for i in range(segments):
            t=2*PI*i/segments;vs.append((center[0]+radii[0]*math.sin(a)*math.sin(t),center[1]+radii[1]*math.sin(a)*math.cos(t),center[2]+radii[2]*math.cos(a)))
    for j in range(rings):
        for i in range(segments):a=j*segments+i;b=j*segments+(i+1)%segments;fs.append((a,b,b+segments,a+segments))
    return mesh(name,vs,fs,mat,bone)

def loft(name,sections,mat,bone='spine_02',segments=24,section_weights=None):
    vs=[];fs=[];ws=[]
    for j,(z,rx,ry,cy) in enumerate(sections):
        for i in range(segments):
            t=2*PI*i/segments;vs.append((rx*math.sin(t),cy+ry*math.cos(t),z));ws.append(section_weights[j] if section_weights else {bone:1})
    for j in range(len(sections)-1):
        for i in range(segments):a=j*segments+i;b=j*segments+(i+1)%segments;fs.append((a,b,b+segments,a+segments))
    fs.extend([tuple(range(segments-1,-1,-1)),tuple((len(sections)-1)*segments+i for i in range(segments))])
    return mesh(name,vs,fs,mat,bone,weights=ws)

def sweep(name,points,radii,mat,bone,segments=12,depth=1,weights=None):
    points=[Vector(p) for p in points];vs=[];fs=[];ws=[]
    for j,p in enumerate(points):
        tangent=(points[min(j+1,len(points)-1)]-points[max(0,j-1)]).normalized()
        ref=Vector((0,1,0)) if abs(tangent.y)<.9 else Vector((1,0,0))
        u=tangent.cross(ref).normalized();v=tangent.cross(u).normalized()
        for i in range(segments):
            a=2*PI*i/segments;vs.append(tuple(p+radii[j]*(math.cos(a)*u+math.sin(a)*v*depth)));ws.append(weights[j] if weights else {bone:1})
    for j in range(len(points)-1):
        for i in range(segments):a=j*segments+i;b=j*segments+(i+1)%segments;fs.append((a,b,b+segments,a+segments))
    fs.extend([tuple(range(segments-1,-1,-1)),tuple((len(points)-1)*segments+i for i in range(segments))])
    return mesh(name,vs,fs,mat,bone,weights=ws)

def torso():
    loft('body_base',[(.89,.175,.095,0),(.99,.15,.105,0),(1.13,.17,.115,0),(1.25,.218,.135,0),(1.35,.23,.115,0),(1.40,.16,.09,0)],'ivory',section_weights=[{'pelvis':1},{'pelvis':.8,'spine_01':.2},{'spine_01':1},{'spine_02':1},{'spine_03':1},{'spine_03':1}])
    loft('neck_surface',[(1.39,.079,.064,-.013),(1.45,.071,.064,-.01),(1.51,.066,.069,-.006),(1.56,.075,.074,-.007)],'skin','neck',24)
    # Breastplate wraps front and sides of the ribcage with a shaped central ridge.
    sections=[(1.09,.149,.119),(1.125,.17,.141),(1.22,.215,.153),(1.32,.224,.132),(1.365,.166,.105)]
    vs=[];fs=[];n=24
    for z,rx,ry in sections:
        for i in range(n+1):
            t=-1.75+3.5*i/n;c=math.cos(t);vs.append((rx*math.sin(t),ry*c+.014*max(0,c)**8,z+.026*max(0,c)**2 if z==1.32 else z))
    for j in range(len(sections)-1):
        for i in range(n):a=j*(n+1)+i;fs.append((a,a+1,a+n+2,a+n+1))
    ob=mesh('armor_chest',vs,fs,'steel','spine_02');solid=ob.modifiers.new('ForgedThickness','SOLIDIFY');solid.thickness=.009;bev=ob.modifiers.new('PlateEdge','BEVEL');bev.width=.005;bev.segments=2
    loft('armor_back',[(1.11,.157,.116,-.012),(1.22,.211,.124,-.018),(1.32,.209,.115,-.009),(1.375,.146,.079,-.006)],'steel_dark','spine_02',24)
    # High ivory collar and articulated waist keep the neck grounded in the coat.
    loft('coat_collar',[(1.375,.109,.081,0),(1.42,.095,.077,.003),(1.455,.086,.075,.001)],'ivory','spine_03',24)
    loft('belt',[(1.038,.159,.121,0),(1.065,.163,.124,0),(1.085,.159,.122,0)],'leather','spine_01',32)
    for s in (-1,1):
        ellipsoid('armor_fastener_'+('l' if s>0 else 'r'),(s*.119,.097,1.382),(.024,.009,.023),'gold','spine_03',8,14)
    # Distinct flared coat skirts, quiet volume under the split navy tabard.
    loft('coat_skirt',[(.71,.229,.142,0),(.75,.232,.15,.002),(.86,.208,.144,0),(1.0,.161,.113,0),(1.04,.158,.118,0)],'ivory','pelvis',32)
    for front in (True,False):
        vs=[];fs=[];rows=9;cols=12
        for j in range(rows):
            t=j/(rows-1);z=1.045-.40*t;width=.14+.017*t
            for i in range(cols+1):
                u=-1+2*i/cols;x=width*u;cy=(.131+.04*t+.012*math.sin(u*PI*3)*(t+.2))*(1 if front else -1)
                zz=z+(.055*abs(u) if j==rows-1 else 0);vs.append((x,cy,zz))
        for j in range(rows-1):
            for i in range(cols):
                # Lower split clears the legs; remaining web is one tailored panel.
                if j>4 and i in (5,6):continue
                a=j*(cols+1)+i;fs.append((a,a+1,a+cols+2,a+cols+1))
        ob=mesh('tabard_front' if front else 'tabard_back',vs,fs,'navy','pelvis');ob.modifiers.new('ClothThickness','SOLIDIFY').thickness=.004
    # Back straps support the costume without a cape.
    for s in (-1,1):sweep('back_strap_'+str(s),[(s*.18,-.119,1.32),(s*.08,-.145,1.21),(-s*.10,-.124,1.06)],[.018,.018,.018],'leather','spine_02',8,depth=.18)

def limbs():
    for side,s in [('l',1),('r',-1)]:
        sh=ARM.data.bones['upperarm_'+side].head_local.copy();el=ARM.data.bones['lowerarm_'+side].head_local.copy();wr=ARM.data.bones['hand_'+side].head_local.copy()
        direction=(el-sh);pts=[sh-direction*.09,sh+direction*.18,sh+direction*.50,sh+direction*.83,el,el+(wr-el)*.28,el+(wr-el)*.63,wr]
        radii=[.095,.101,.098,.08,.074,.079,.063,.047]
        weights=[{'upperarm_'+side:1}]*3+[{'upperarm_'+side:.7,'lowerarm_'+side:.3},{'upperarm_'+side:.45,'lowerarm_'+side:.55}]+[{'lowerarm_'+side:1}]*2+[{'lowerarm_'+side:.7,'hand_'+side:.3}]
        sweep('coat_sleeve_'+side,pts,radii,'ivory','upperarm_'+side,20,weights=weights)
        # Fitted domed pauldron surfaces, not cylindrical caps.
        vs=[];fs=[];segs=24;rings=8;center=sh+Vector((s*.012,0,.012))
        for j in range(rings+1):
            phi=.03+(PI*.58)*j/rings
            for i in range(segs):
                t=2*PI*i/segs;v=center+Vector((.145*math.sin(phi)*math.cos(t),.126*math.sin(phi)*math.sin(t),.113*math.cos(phi)))
                vs.append(tuple(v))
        for j in range(rings):
            for i in range(segs):a=j*segs+i;b=j*segs+(i+1)%segs;fs.append((a,b,b+segs,a+segs))
        ob=mesh('armor_pauldron_'+side,vs,fs,'steel','upperarm_'+side);ob.modifiers.new('PlateThickness','SOLIDIFY').thickness=.007
        rim=[]
        for i in range(25):
            t=2*PI*i/24;rim.append(tuple(center+Vector((.142*math.cos(t),.122*math.sin(t),-.022))))
        sweep('pauldron_rim_'+side,rim,[.006]*len(rim),'steel_dark','upperarm_'+side,6)
        mid=el+(wr-el)*.20;end=el+(wr-el)*.9
        sweep('bracer_'+side,[mid,mid+(end-mid)*.2,mid+(end-mid)*.73,end],[.083,.085,.063,.055],'steel','lowerarm_'+side,20,depth=.85)
        hip=ARM.data.bones['thigh_'+side].head_local.copy();knee=ARM.data.bones['calf_'+side].head_local.copy();ankle=ARM.data.bones['foot_'+side].head_local.copy()
        pts=[hip,hip+(knee-hip)*.22,hip+(knee-hip)*.56,knee,knee+(ankle-knee)*.25,knee+(ankle-knee)*.67,ankle]
        radii=[.119,.121,.100,.084,.089,.072,.056]
        weights=[{'thigh_'+side:1}]*3+[{'thigh_'+side:.35,'calf_'+side:.65}]+[{'calf_'+side:1}]*2+[{'foot_'+side:.5,'calf_'+side:.5}]
        sweep('leg_base_'+side,pts,radii,'leather','thigh_'+side,20,weights=weights)
        ellipsoid('knee_plate_'+side,tuple(knee+Vector((0,.072,.014))),(.088,.043,.103),'steel','calf_'+side,10,18)
        sweep('greave_'+side,[knee+Vector((0,.009,-.088)),knee+(ankle-knee)*.50+Vector((0,.024,0)),ankle+Vector((0,.015,.028))],[.085,.078,.06],'steel','calf_'+side,18,depth=.80)
        # Tailored boot: broad toe, defined ankle and sole, without bulbous feet.
        x=ankle.x
        ellipsoid('boot_'+side,(x,.071,.079),(.083,.163,.077),'leather','foot_'+side,10,20)
        ellipsoid('boot_sole_'+side,(x,.072,.021),(.088,.169,.025),'steel_dark','foot_'+side,6,20)
        ellipsoid('boot_toe_plate_'+side,(x,.151,.077),(.078,.087,.055),'steel','foot_'+side,8,16)

PROFILE=[(1.488,.030,.035,.025),(1.505,.063,.059,.010),(1.53,.088,.075,-.002),(1.56,.105,.083,-.007),(1.60,.114,.09,-.015),(1.64,.12,.092,-.016),(1.68,.118,.095,-.017),(1.72,.114,.092,-.014),(1.76,.103,.081,-.013),(1.79,.076,.056,-.012),(1.807,.015,.015,-.012)]
def head_dims(z):
    for a,b in zip(PROFILE,PROFILE[1:]):
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0]);return tuple(a[i]*(1-t)+b[i]*t for i in range(1,4))
    return PROFILE[0][1:] if z<PROFILE[0][0] else PROFILE[-1][1:]

def face_y(x,z):
    rx,ry,cy=head_dims(z);y=cy+ry*math.sqrt(max(.001,1-(x/rx)**2))
    g=lambda v,mu,s:math.exp(-((v-mu)/s)**2)
    y+=g(x,0,.019)*(.026*g(z,1.645,.047)+.025*g(z,1.613,.017))
    y-=.014*(g(x,-.045,.027)+g(x,.045,.027))*g(z,1.66,.012)
    y+=.009*(g(x,-.067,.035)+g(x,.067,.035))*g(z,1.617,.021)
    y+=.006*g(x,0,.034)*(g(z,1.565,.005)+g(z,1.553,.005))
    return y

def head():
    vs=[];fs=[];n=48;rows=33
    for j in range(rows):
        z=1.488+(1.807-1.488)*j/(rows-1);rx,ry,cy=head_dims(z)
        for i in range(n):
            t=2*PI*i/n;x=rx*math.sin(t);c=math.cos(t);y=face_y(x,z) if c>=0 else cy+ry*c
            vs.append((x,y,z))
    for j in range(rows-1):
        for i in range(n):a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
    fs.extend([tuple(range(n-1,-1,-1)),tuple((rows-1)*n+i for i in range(n))]);mesh('head_surface',vs,fs,'skin')
    for side,s in [('l',1),('r',-1)]:
        ellipsoid('ear_'+side,(s*.119,-.016,1.639),(.023,.016,.041),'skin',rings=10,segments=16)
        ellipsoid('ear_fold_'+side,(s*.134,-.001,1.641),(.007,.006,.023),'lip',rings=6,segments=10)
        cx=s*.045;cz=1.66
        # Almond eye opening supported by curved upper/lower eyelids.
        outline=[]
        for i in range(24):
            t=2*PI*i/24;x=cx+.024*math.cos(t);z=cz+.0087*math.sin(t)+s*.10*(x-cx);outline.append((x,face_y(x,z)+.004,z))
        verts=[(cx,face_y(cx,cz)+.007,cz)]+outline;faces=[(0,1+i,1+(i+1)%24) for i in range(24)];mesh('eye_white_'+side,verts,faces,'eye')
        sweep('eyelid_'+side,outline+[outline[0]],[.0024]*25,'lip','head',6)
        ellipsoid('iris_'+side,(cx,face_y(cx,cz)+.009,cz),(.0075,.0024,.0078),'iris',rings=8,segments=16)
        ellipsoid('pupil_'+side,(cx,face_y(cx,cz)+.011,cz),(.0036,.001,.0049),'hair',rings=6,segments=12)
        ellipsoid('eye_glint_'+side,(cx-.002,face_y(cx,cz)+.0125,cz+.003),(.0017,.0006,.0017),'eye',rings=4,segments=8)
        brow=[]
        for i in range(6):
            t=i/5;x=s*(.018+.061*t);z=1.686+.003*math.sin(t*PI)-.009*t;brow.append((x,face_y(x,z)+.0035,z))
        sweep('brow_'+side,brow,[.004,.005,.005,.0045,.003,.001],'hair','head',8,depth=.55)
    mouth=[]
    for i in range(13):
        x=-.027+.054*i/12;z=1.558-.0015*math.cos(x/.027*PI);mouth.append((x,face_y(x,z)+.001,z))
    sweep('mouth_line',mouth,[.0008]+[.0015]*11+[.0008],'lip','head',6,depth=.6)
    # Structured swept hair with a continuous cap, broad locks, and short braid.
    vs=[];fs=[];segs=40;rings=10
    for j in range(rings+1):
        t=j/rings
        for i in range(segs):
            a=2*PI*i/segs;front=max(0,math.cos(a));bottom=1.642+.092*front+.011*math.sin(a*2)
            phi=.04+(PI/2-.04)*t;z=1.835+(bottom-1.835)*(1-math.cos(phi));vs.append((.131*math.sin(phi)*math.sin(a),-.016+.108*math.sin(phi)*math.cos(a),z))
    for j in range(rings):
        for i in range(segs):a=j*segs+i;b=j*segs+(i+1)%segs;fs.append((a,b,b+segs,a+segs))
    mesh('hair_cap',vs,fs,'hair')
    locks=[([(-.035,.06,1.821),(-.064,.094,1.803),(-.099,.096,1.77),(-.123,.052,1.724),(-.126,.01,1.684)],[.008,.023,.026,.022,.006]),
           ([(-.018,.064,1.828),(.017,.099,1.814),(.066,.101,1.788),(.103,.071,1.754),(.123,.027,1.701)],[.012,.023,.027,.025,.008]),
           ([(-.020,.014,1.835),(.035,.024,1.828),(.09,.01,1.794),(.123,-.023,1.746),(.123,-.055,1.704)],[.012,.025,.026,.024,.007]),
           ([(-.04,-.023,1.825),(-.086,-.032,1.804),(-.115,-.052,1.761),(-.119,-.079,1.708),(-.078,-.109,1.673)],[.012,.026,.027,.024,.008])]
    for i,(pts,r) in enumerate(locks):sweep('hair_swept_lock_'+str(i),pts,r,'hair','head',12,depth=.52)
    for i in range(6):
        z=1.694-i*.039;ellipsoid('hair_braid_'+str(i),((-.018 if i%2 else .018),-.119-i*.002,z),(.039-i*.002,.026,.038),'hair','head',8,12)
    sweep('hair_tie',[(-.025,-.127,1.482),(0,-.153,1.482),(.025,-.127,1.482)],[.006]*3,'leather','head',8)

def main():
    global ARM,COL
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True);p.add_argument('--equipment',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    out=Path(a.output).resolve();assert out.is_relative_to(ROOT/'art-source/heroes/wc_u_human_guardian/candidates/AQ1');assert not out.exists()
    report=Path(a.report);report.mkdir(parents=True,exist_ok=True)
    ARM=bpy.data.objects['Armature'];before=invariants(ARM);ARM.animation_data.action=None
    for pb in ARM.pose.bones:pb.location=(0,0,0);pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)
    for ob in bpy.context.scene.objects:
        if ob.type=='MESH':ob.hide_render=True;ob.hide_set(True)
    COL=bpy.data.collections.new('AQ1_EDITABLE');bpy.context.scene.collection.children.link(COL)
    for args in [('steel','9EAAB5',.34,.78),('steel_dark','505B66',.43,.72),('navy','25466B',.76,0),('ivory','E9E2CD',.83,0),('gold','C7A25B',.34,.73),('leather','4A3025',.66,0),('skin','A66645',.55,0),('hair','201916',.44,0),('lip','64352B',.59,0),('eye','E3D9C6',.32,0),('iris','493020',.4,0)]:make_material(*args)
    torso();limbs();head()
    if a.equipment:
        from aq1_equipment import build_equipment
        PARTS.extend(build_equipment(ARM,MATS,COL))
    use_clip(ARM,'Idle');assert invariants(ARM)==before
    count=0
    for ob in PARTS:ob.data.calc_loop_triangles();count+=len(ob.data.loop_triangles)
    bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False)
    (report/'forms.json').write_text(json.dumps({'candidate':str(out),'parts':[o.name for o in PARTS],'base_triangles':count,'invariants':before,'matches_existing_rig_curves':invariants(ARM)==before,'status':'FORM_CANDIDATE_REQUIRES_PIXEL_REVIEW'},indent=2))
    scene=setup()
    for view in ['front','three_quarter','face','side','board']:render_view(scene,report/('material_'+view+'.png'),view)
    scene.view_layers[0].material_override=make_material('clay','ADB1B5',.72,0)
    for view in ['front','three_quarter','face']:render_view(scene,report/('clay_'+view+'.png'),view)
    print('AQ1_FORMS_CANDIDATE',str(out),count,flush=True)

if __name__=='__main__':main()
