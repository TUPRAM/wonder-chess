"""Author original modular Seven-Lantern Courtyard and real Blender camera captures."""
import sys
from pathlib import Path
import json
import math
import hashlib
import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from author_alpha import Geometry, material_for, export_fbx, ROOT

OUT=ROOT/'exports/arena'
SOURCE=ROOT/'art-source/arena'
REPORT=ROOT/'reports/WC-330/arena'
for directory in (OUT,SOURCE,REPORT):directory.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.world=bpy.data.worlds.new('CourtyardSky');scene.world.color=(.36,.43,.56)
unit={'id':'wc_seven_lantern_courtyard','art':{'palette':'#C8B891 #E7DAB9 #375B86 #765A3E #A1AAB0 #685137 #637B4C #405B40 #EDE1C5 #283B50 #CBA65D #8FBDCD #EFAE63 #857592 #BCAA87 #B87B60'}}
material=material_for(unit,OUT)
kit=bpy.data.collections.new('WC_MODULAR_KIT');scene.collection.children.link(kit)
arrangement=bpy.data.collections.new('WC_COURTYARD');scene.collection.children.link(arrangement)
meshes={}

def box(g,center,size,color,bevel=.06):
    x,y,z=center;w,d,h=size
    polygon=[(x-w/2,z-h/2),(x+w/2,z-h/2),(x+w/2,z+h/2),(x-w/2,z+h/2)]
    g.plate(polygon,y,d,color,'root',bevel)

def make(name,g):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(g.vertices,[],g.faces);mesh.update()
    uv=mesh.uv_layers.new(name='CourtyardAtlas')
    for poly,col in zip(mesh.polygons,g.colors):
        for loop in poly.loop_indices:
            v=mesh.vertices[mesh.loops[loop].vertex_index].co
            uv.data[loop].uv=((col%4+.18+.64*((v.x+v.y)*.5%1))/4,(col//4+.18+.64*(v.z*.5%1))/4)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
    ob=bpy.data.objects.new(name,mesh);kit.objects.link(ob);ob.data.materials.append(material)
    export_fbx(OUT/(name+'.fbx'),[ob],False)
    ob.hide_render=True;ob.hide_set(True);meshes[name]=ob
    return ob

def place(name,loc,rotation=0,scale=(1,1,1)):
    ob=meshes[name].copy();ob.data=meshes[name].data;arrangement.objects.link(ob)
    ob.hide_render=False;ob.hide_set(False);ob.location=loc;ob.rotation_euler.z=rotation;ob.scale=scale
    return ob

for name,color in [('SM_WC_Tile',0),('SM_WC_TileAlt',1)]:
    g=Geometry();box(g,(0,0,-.105),(1.982,1.982,.21),color,.015)
    # Fine inset corner cuts define cells without loud graphic checkerboarding.
    for s in (-1,1):
        for t in (-1,1):box(g,(s*.88,t*.88,-.006),(.085,.085,.015),1 if color==0 else 0,.05)
    make(name,g)
g=Geometry();box(g,(0,0,-.16),(2,.44,.4),0);box(g,(0,0,.065),(2,.49,.05),1);make('SM_WC_BoardEdge',g)
g=Geometry();box(g,(0,0,-.13),(.55,.55,.46),0);box(g,(0,0,.12),(.64,.64,.07),1);make('SM_WC_BoardCorner',g)
g=Geometry();box(g,(0,0,.38),(2,.32,.76),0);box(g,(0,0,.79),(2.07,.42,.12),1)
for s in (-1,1):box(g,(s*.9,0,.45),(.17,.45,.89),1)
make('SM_WC_LowWall',g)
g=Geometry();box(g,(0,0,.16),(1.34,.84,.32),0);box(g,(0,0,.35),(1.44,.94,.1),1);box(g,(0,0,.421),(1.19,.68,.043),2);make('SM_WC_BenchPlinth',g)
g=Geometry();g.loft([((0,0,0),.23,.23),((0,0,.14),.26,.26),((0,0,.19),.16,.16),((0,0,.26),.08,.08),((0,0,3.8),.065,.065)],3,'root',12)
g.ellipsoid((0,0,3.87),(.13,.13,.17),10,'root',6,10);make('SM_WC_Flagpole',g)
g=Geometry();g.add([(0,0,3.53),(.47,.06,3.56),(.98,-.035,3.52),(.94,-.03,2.26),(.45,.06,2.10),(0,0,2.28)],[(0,1,4,5),(1,2,3,4)],2,'root')
g.tube([(.09,.006,3.5),(.10,.005,2.33)],[.019,.019],10,'root',6)
g.ring((.47,.075,2.90),.18,.028,10,'root',steps=20)
make('SM_WC_Banner',g)
g=Geometry();box(g,(0,0,.07),(.58,.58,.14),0);g.loft([((0,0,.13),.2,.2),((0,0,.85),.32,.32),((0,0,.94),.35,.35)],0,'root',12)
g.loft([((0,0,.89),.36,.36),((0,0,.98),.36,.36)],1,'root',12)
g.ellipsoid((0,0,1.12),(.42,.42,.33),6,'root',6,10)
for i in range(7):
    a=i*2*math.pi/7;x=math.cos(a)*.30;y=math.sin(a)*.30
    g.ellipsoid((x,y,1.27+(i%3)*.05),(.15,.14,.19),6 if i%2 else 7,'root',5,8)
make('SM_WC_Planter',g)
g=Geometry();box(g,(0,0,.055),(.48,.48,.11),3)
g.loft([((0,0,.10),.19,.19),((0,0,.14),.17,.17),((0,0,.64),.17,.17),((0,0,.73),.23,.23),((0,0,.81),.04,.04)],10,'root',8)
box(g,(0,0,.42),(.23,.23,.43),12,.12)
for s in (-1,1):
    for t in (-1,1):g.tube([(s*.13,t*.13,.16),(s*.13,t*.13,.69)],[.024,.024],3,'root',6)
make('SM_WC_Lantern',g)
g=Geometry()
for i in range(4):box(g,(0,-i*.28,(i+1)*.12),(3.5,.30,(i+1)*.24),0)
make('SM_WC_Stairs',g)
g=Geometry();box(g,(0,0,2.1),(4.8,.32,4.2),1,.012)
for x in (-2.33,0,2.33):box(g,(x,.21,2.13),(.16,.14,4.26),3)
for z in (.2,2.3,4.16):box(g,(0,.21,z),(4.8,.16,.15),3)
for x in (-1.18,1.18):
    g.plate([(x-.43,.65),(x+.43,.65),(x+.43,1.64),(x+.29,1.91),(x,2.06),(x-.29,1.91),(x-.43,1.64)],.181,.04,2,'root')
    for dx in (-.45,.45):box(g,(x+dx,.24,1.16),(.09,.11,1.10),0)
    g.ring((x,.23,1.62),.43,.06,0,'root',0,math.pi,18)
    box(g,(x,.25,.62),(1.07,.3,.10),0)
g.add([(-2.66,-.25,4.17),(2.66,-.25,4.17),(0,-.25,5.25),(-2.66,1.42,4.17),(2.66,1.42,4.17),(0,1.42,5.25)],[(0,1,2),(5,4,3),(0,3,4,1),(0,2,5,3),(1,4,5,2)],2,'root')
g.tube([(-2.7,1.44,4.17),(0,1.44,5.26),(2.7,1.44,4.17)],[.07]*3,3,'root',6)
make('SM_WC_DistantFacade',g)
# Lay out the actual authored board and restrained background modules.
for x in range(8):
    for y in range(8):place('SM_WC_Tile' if (x+y)%2==0 else 'SM_WC_TileAlt',((x-3.5)*2,(y-3.5)*2,0))
for i in range(8):
    a=(i-3.5)*2
    for side in (-1,1):
        place('SM_WC_BoardEdge',(a,side*8.19,0));place('SM_WC_BoardEdge',(side*8.19,a,0),math.pi/2)
for x in (-1,1):
    for y in (-1,1):place('SM_WC_BoardCorner',(x*8.20,y*8.20,0))
for i in range(9):place('SM_WC_BenchPlinth',((i-4)*1.74,10.5,0))
for i in range(11):
    a=(i-5)*2
    place('SM_WC_LowWall',(a,-10.3,0))
    if i not in (4,5,6):place('SM_WC_LowWall',(a,12,0))
for side in (-1,1):
    for i in range(10):place('SM_WC_LowWall',(side*10.7,(i-4.5)*2,0),math.pi/2)
for x,y in [(-10,-10),(10,-10),(-10,10),(10,10)]:
    place('SM_WC_Flagpole',(x,y,0));place('SM_WC_Banner',(x,y,0),.15 if x<0 else math.pi)
for x,y in [(-9.2,-8),(9.2,-8),(-9.2,8),(9.2,8),(-5,-9.1),(5,-9.1)]:place('SM_WC_Planter',(x,y,0))
for i in range(7):place('SM_WC_Lantern',((i-3)*2.8,-10.25,.89))
for i in range(5):place('SM_WC_DistantFacade',((i-2)*5,-13,0))
place('SM_WC_Stairs',(0,13,-.9),math.pi)
boxgeo=Geometry();box(boxgeo,(0,0,-.4),(27,31,.3),0);make('SM_WC_CourtyardFoundation',boxgeo);place('SM_WC_CourtyardFoundation',(0,0,0))
sun_data=bpy.data.lights.new('WarmAfternoon','SUN');sun_data.energy=2.0;sun_data.angle=.13
sun=bpy.data.objects.new('WarmAfternoon',sun_data);scene.collection.objects.link(sun);sun.rotation_euler=(math.radians(26),math.radians(-23),math.radians(-28))
fill_data=bpy.data.lights.new('SkyBounce','AREA');fill_data.energy=1800;fill_data.size=25
fill=bpy.data.objects.new('SkyBounce',fill_data);scene.collection.objects.link(fill);fill.location=(0,4,13)
camera_data=bpy.data.cameras.new('WC_GameplayCameraCandidate');camera=bpy.data.objects.new('WC_GameplayCameraCandidate',camera_data);scene.collection.objects.link(camera)
camera.location=(0,22,25.5);target=Vector((0,1.5,0));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO';camera_data.ortho_scale=34;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.view_settings.view_transform='AgX'
for w,h in [(1920,1080),(1280,720)]:
    scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.resolution_percentage=100;scene.render.filepath=str(REPORT/f'courtyard_{w}x{h}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'WC_SevenLanternCourtyard.blend'))
record={'status':'authored_exported_rendered_not_engine_accepted','blender_version':bpy.app.version_string,'source_unit':'meter','source_forward':'+Y','module_origin':'center at floor; tile top at Z 0',
        'board_tile_pitch_m':2,'board_extent_m':16,'module_meshes':list(meshes),'camera':{'type':'orthographic','location_m':list(camera.location),'target_m':[0,1.5,0],'ortho_width_m':34,'state':'candidate requiring in-engine HUD and crowd review'},
        'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file()},'not_verified':['Unreal import','gameplay camera safe area','crowded combat readability','performance']}
(OUT/'arena_manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('WC_COURTYARD_COMPLETE '+json.dumps(list(meshes)),flush=True)
