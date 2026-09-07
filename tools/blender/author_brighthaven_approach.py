"""Author a compact original Brighthaven lobby approach, separate from the arena."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/blender'))
from author_alpha import Geometry,material_for,export_fbx_raw
from normalized_fbx import export_normalized_copy

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def box(g,c,size,color,bevel=.04):
    x,y,z=c;w,d,h=size
    g.plate([(x-w/2,z-h/2),(x+w/2,z-h/2),(x+w/2,z+h/2),(x-w/2,z+h/2)],y,d,color,'root',bevel)
def beam(g,a,b,r=.075,color=3):g.tube([a,b],[r,r],color,'root',8)
def leaf(g,origin,angle,length,color):
    x,y,z=origin;d=Vector((math.cos(angle)*length,math.sin(angle)*length,-length*.5));side=Vector((-math.sin(angle),math.cos(angle),0))*length*.26;c=Vector(origin)
    g.add([tuple(c),tuple(c+d*.42+side),tuple(c+d*.48+Vector((0,0,.045))),tuple(c+d),tuple(c+d*.42-side)],[(0,1,2),(1,3,2),(3,4,2),(4,0,2)],color,'root')
def flowers(g,x,y,z,hanging=False):
    if hanging:
        g.loft([((x,y,z-.20),.19,.16),((x,y,z),.26,.21),((x,y,z+.04),.27,.22)],3,'root',12)
        for s in (-1,1):beam(g,(x+s*.19,y,z),(x,y,z+.58),.017,10)
    else:g.loft([((x,y,z-.18),.22,.19),((x,y,z),.29,.24),((x,y,z+.035),.31,.26)],14,'root',12)
    for j in range(8):
        a=j*math.pi/4;length=.30+(j%3)*.07
        stem=[(x+.12*math.cos(a),y+.10*math.sin(a),z+.02),(x+.20*math.cos(a),y+.17*math.sin(a),z+.16),(x+length*math.cos(a),y+length*math.sin(a),z-(.30 if hanging else -.12))]
        g.tube(stem,[.016,.013,.006],6,'root',5)
        for k in (1,2):leaf(g,stem[k],a+.6*k,.19,6 if j%2 else 7)
        if j%2==0:
            tip=Vector(stem[1])+Vector((0,0,.07))
            for p in range(5):
                b=p*2*math.pi/5;g.ellipsoid(tuple(tip+Vector((.055*math.cos(b),.055*math.sin(b),0))),(.05,.05,.025),8 if j%4 else 9,'root',3,6)
            g.ellipsoid(tuple(tip),(.023,.023,.033),9,'root',3,6)
def arch(g,x,y,z,width,height,color):
    pts=[(x-width/2,y,z),(x-width/2,y,z+height-width/2)]
    pts += [(x+width/2*math.cos(math.pi-i*math.pi/12),y,z+height-width/2+width/2*math.sin(math.pi-i*math.pi/12)) for i in range(13)]
    pts.append((x+width/2,y,z));g.tube(pts,[.065]*len(pts),color,'root',6)
def house(g,x,y,w,h):
    box(g,(x,y,h/2),(w,1.45,h),0,.015)
    box(g,(x,y+.76,.20),(w+.16,.18,.32),14)
    for dx in (-w*.47,0,w*.47):box(g,(x+dx,y+.76,h*.52),(.11,.12,h*.96),3)
    for zz in (.48,h*.54,h-.06):box(g,(x,y+.77,zz),(w+.08,.13,.105),3)
    g.plate([(x-w/2,h),(x+w/2,h),(x,h+.91)],y,1.45,1,'root',.015)
    # Curved shingle surfaces with lifted eaves and a restrained ridge.
    for side in (-1,1):
        vertices=[]
        for j in range(4):
            yy=y-.94+j*1.89/3
            for i in range(9):
                t=i/8;vertices.append((x+side*(w/2+.19)*t,yy,h+.99-.92*t+.13*t*t))
        faces=[(j*9+i,j*9+i+1,(j+1)*9+i+1,(j+1)*9+i) for j in range(3) for i in range(8)]
        g.add(vertices,faces,2,'root')
        for i in (0,2,4,6,8):
            t=i/8;beam(g,(x+side*(w/2+.19)*t,y-.95,h+.995-.92*t+.13*t*t),(x+side*(w/2+.19)*t,y+.97,h+.995-.92*t+.13*t*t),.022,15)
        g.tube([(x,y+.99,h+1.01),(x+side*w*.25,y+.99,h+.54),(x+side*(w/2+.21),y+.99,h+.19)],[.055]*3,3,'root',7)
    for dx in (-w*.25,w*.25):
        px=x+dx;py=y+.84;pz=.72
        poly=[(px-.32,pz),(px+.32,pz),(px+.32,pz+.76),(px+.20,pz+.98),(px,pz+1.06),(px-.20,pz+.98),(px-.32,pz+.76)]
        g.plate(poly,py,.035,5,'root',.035);arch(g,px,py+.035,pz,.72,1.13,1)
        beam(g,(px,py+.08,pz+.04),(px,py+.08,pz+.98),.023,3)
        box(g,(px,py+.13,pz-.025),(.89,.32,.105),1)
    arch(g,x,y+.85,h*.59,.59,.78,3)
    g.plate([(x-.22,h*.59),(x+.22,h*.59),(x+.22,h*.59+.41),(x,h*.59+.67),(x-.22,h*.59+.41)],y+.87,.02,11,'root')
    flowers(g,x+w*.37,y+1.06,h-.17,True)

parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'exports/lobby');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);review=out/'review';review.mkdir();source=ROOT/'art-source/lobby/brighthaven_approach.blend';source.parent.mkdir(parents=True,exist_ok=True)
assert not source.exists(),'Refuse overwriting existing authored lobby'
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.world=bpy.data.worlds.new('BrighthavenSky');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.34,.52,.68,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
unit={'id':'wc_brighthaven_approach','art':{'palette':'#DCCBA9 #F1E5C9 #3F6E8D #76523D #B79154 #304958 #4F7858 #86A873 #CA7D80 #E1B46E #CFAC63 #8FBCC3 #608F9B #978BA4 #B3A58A #688FA7'}}
mat=material_for(unit,out);collection=bpy.data.collections.new('BRIGHTHAVEN_APPROACH');scene.collection.children.link(collection);modules=[]
def make(name,g):
    data=bpy.data.meshes.new(name);data.from_pydata(g.vertices,[],g.faces);data.update();uv=data.uv_layers.new(name='BrighthavenAtlas')
    for face,col in zip(data.polygons,g.colors):
        for li in face.loop_indices:
            v=data.vertices[data.loops[li].vertex_index].co;uv.data[li].uv=((col%4+.18+.64*((v.x+v.y)*.5%1))/4,(col//4+.18+.64*(v.z*.5%1))/4)
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    ob=bpy.data.objects.new(name,data);collection.objects.link(ob);data.materials.append(mat);modules.append(ob);return ob
g=Geometry();house(g,-3.4,-3.0,2.9,2.80);make('SM_WC_ApproachWestHouse',g)
g=Geometry();house(g,3.65,-3.6,2.7,3.35);make('SM_WC_ApproachEastHouse',g)
g=Geometry()
for s in (-1,1):
    x=s*1.32;box(g,(x,-4.1,1.05),(.24,.32,2.1),0);box(g,(x,-4.1,2.1),(.37,.43,.16),1)
    beam(g,(x,-4.1,2.12),(x,-4.1,2.67),.105)
g.tube([(-1.6,-4.1,2.58),(-.8,-4.1,2.80),(0,-4.1,2.87),(.8,-4.1,2.80),(1.6,-4.1,2.58)],[.14]*5,3,'root',8)
for i in range(7):beam(g,(-1.5+i*.5,-4.6,2.8),(-1.5+i*.5,-3.65,2.8),.045,3)
flowers(g,-1.38,-3.91,2.12,True);flowers(g,1.36,-3.91,2.12,True);make('SM_WC_ApproachGardenArch',g)
g=Geometry()
g.loft([((.25,-6.5,0),.72,.66),((.25,-6.5,.22),.79,.72),((.25,-6.5,.32),.49,.46),((.25,-6.5,3.7),.34,.33),((.25,-6.5,3.8),.49,.46),((.25,-6.5,3.94),.43,.40)],0,'root',12)
g.loft([((.25,-6.5,3.93),.30,.28),((.25,-6.5,4.54),.27,.25)],11,'root',8)
for j in range(8):
    a=j*math.pi/4;beam(g,(.25+.31*math.cos(a),-6.5+.29*math.sin(a),3.9),(.25+.29*math.cos(a),-6.5+.27*math.sin(a),4.57),.04,10)
g.loft([((.25,-6.5,4.53),.48,.44),((.25,-6.5,4.66),.42,.39),((.25,-6.5,5.08),.06,.06)],2,'root',12)
g.ellipsoid((.25,-6.5,5.12),(.09,.09,.10),10,'root',4,8);make('SM_WC_ApproachBeacon',g)
g=Geometry()
for x in (-4.65,-2.65,2.65,4.65):
    box(g,(x,-1.7,.38),(1.9,.30,.76),0);box(g,(x,-1.7,.78),(1.96,.43,.12),1)
    flowers(g,x,-1.72,.98)
for x in (-5.7,5.7):
    box(g,(x,-1.7,.44),(.43,.47,.88),14);box(g,(x,-1.7,.91),(.50,.54,.11),1)
    g.loft([((x,-1.7,.97),.16,.16),((x,-1.7,1.42),.16,.16),((x,-1.7,1.54),.24,.24),((x,-1.7,1.65),.025,.025)],10,'root',8)
    g.ellipsoid((x,-1.7,1.22),(.115,.115,.18),9,'root',4,8)
make('SM_WC_ApproachGardenWalls',g)
g=Geometry();box(g,(0,-1.5,-.16),(12.2,8.2,.30),0,.015)
for j in range(5):
    for i in range(8):
        x=-5.35+i*1.52;y=1.72-j*1.52
        box(g,(x,y,-.004),(1.49,1.49,.035),1 if (i+j)%4==0 else 0,.018)
make('SM_WC_ApproachPlatform',g)
for module in modules:export_normalized_copy(out/(module.name+'.fbx'),[module],False,export_fbx_raw)
# Joined copy provides a single predictable placement actor while retaining modules.
bpy.ops.object.select_all(action='DESELECT');copies=[]
for module in modules:
    copy=module.copy();copy.data=module.data.copy();scene.collection.objects.link(copy);copy.select_set(True);copies.append(copy)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();combined=bpy.context.object;combined.name='SM_WC_BrighthavenApproach';combined.data.name=combined.name
lods=[]
for level,ratio in ((0,1),(1,.50),(2,.25)):
    ob=combined if level==0 else combined.copy()
    if level:
        ob.data=combined.data.copy();scene.collection.objects.link(ob);ob.name=combined.name+'_LOD'+str(level);bpy.context.view_layer.objects.active=ob
        modifier=ob.modifiers.new('Measured_LOD','DECIMATE');modifier.ratio=ratio;bpy.ops.object.modifier_apply(modifier=modifier.name)
    ob.data.calc_loop_triangles();export_normalized_copy(out/(ob.name+'.fbx'),[ob],False,export_fbx_raw);lods.append({'level':level,'mesh':ob.name,'triangles':len(ob.data.loop_triangles)});ob.hide_render=True;ob.hide_set(True)
camera_data=bpy.data.cameras.new('ApproachReview');camera=bpy.data.objects.new('ApproachReview',camera_data);scene.collection.objects.link(camera);scene.camera=camera
sun_data=bpy.data.lights.new('AfternoonSun','SUN');sun_data.energy=2.2;sun_data.angle=.20;sun=bpy.data.objects.new('AfternoonSun',sun_data);scene.collection.objects.link(sun);sun.rotation_euler=(math.radians(25),math.radians(-20),math.radians(-30))
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.view_settings.view_transform='AgX';scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
camera_data.type='ORTHO';camera_data.ortho_scale=15.3
for label,location,target in [('approach-front',(0,15,7),(0,-2,1.2)),('approach-three-quarter',(11,15,10),(0,-2,1.0)),('approach-back',(0,-18,9),(0,-2,1.4))]:
    camera.location=location;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(review/(label+'.png'));bpy.ops.render.render(write_still=True)
camera.location=(0,15,7);camera.rotation_euler=(Vector((0,-2,1.2))-camera.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(source),check_existing=False)
points=[v.co for v in combined.data.vertices];bounds={'min_m':[min(v[i] for v in points) for i in range(3)],'max_m':[max(v[i] for v in points) for i in range(3)]}
manifest={'status':'AUTHORED_EXPORTED_RENDERED_CANDIDATE_NOT_ENGINE_ACCEPTED','source':str(source),'source_sha256':sha(source),'author_script_sha256':sha(Path(__file__)),'blender_version':bpy.app.version_string,'source_units':'meters','source_forward':'+Y','source_up':'+Z','bounds':bounds,'source_scale':[1,1,1],'combined_mesh':'SM_WC_BrighthavenApproach','modules':[o.name for o in modules],'material':'M_wc_brighthaven_approach','texture_channels':{'BaseColor':'sRGB','Normal':'linear tangent +Y; flat normal with modeled bevels','ORM':'linear R occlusion G roughness B metallic'},'lods':lods,'export_profile':'temporary centimeter copies via normalized_fbx.py and measured fbx_skeletal_cm_v1 operator settings; static Unreal import still unverified','placement':'Source origin0 at approach center, ground top about0m; view from+Y. Buildings atY-3..-3.6, beaconY-6.5. Clear central foreground. Combine meshes on Unreal import if needed; actor scale1 after centimeter import. Never stack combined mesh with individual modules.','files':{p.name:sha(p) for p in out.iterdir() if p.is_file()},'not_verified':['Unreal placement/import','LOD appearance in Unreal','gallery animation bounds','performance','final art acceptance']}
(out/'lobby_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('WC_BRIGHTHAVEN_APPROACH_RENDERED '+json.dumps(lods),flush=True)
