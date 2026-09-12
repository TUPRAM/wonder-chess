import bpy,bmesh,json,math
from mathutils import Vector

def build_head_scaffold():
    verts=[];faces=[]
    for r,row in enumerate(HEAD_ROWS):
        z,w,front,side,rear=row
        for c in range(25):verts.append(grid_point(r,c))
        for j in range(1,16):
            a=math.pi*j/16
            verts.append((w*math.cos(a),side+(rear-side)*math.sin(a),z))
    for r in range(len(HEAD_ROWS)-1):
        for c in range(40):faces.append((r*40+c,r*40+(c+1)%40,(r+1)*40+(c+1)%40,(r+1)*40+c))
    cap=len(verts);verts.append((0,-.043,1.798))
    for c in range(40):faces.append(((len(HEAD_ROWS)-1)*40+c,(len(HEAD_ROWS)-1)*40+(c+1)%40,cap))
    return {'vertices':verts,'faces':faces,'root_loop':list(range(40)),'named_vertex_groups':{'Jaw_Chin':list(range(40,160)),'Cheek_Planes':list(range(280,440)),'Forehead':list(range(560,680)),'Cranium':list(range(680,841))},'design_notes':'Original sparse landmark head cage. Shaped chin, tapered jaw, high cheek planes and independent cranium; deliberate front stations reserve matching component connections. No old Ada head used.'}

assert bpy.data.scenes.get('FH1_HEAD_SHAPE_STUDY') is None
scene,col=fh_scene('FH1_HEAD_SHAPE_STUDY',(0,-.012,1.682),.290)
head=fh_mesh('FH1_Head_Shape_Control_Cage',build_head_scaffold(),col)
bpy.context.view_layer.objects.active=head;head.select_set(True)
scene['render_allowlist']=json.dumps([o.name for o in col.objects]);scene['status']='New jaw/skull/face envelope study before feature integration'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for label in ['front','profile','three_quarter']:
    scene.camera=bpy.data.objects[scene.name+'_'+label];scene.render.filepath=ROOT+'/captures/head_shape_initial_'+label+'.png';bpy.ops.render.render(write_still=True)
print('Original head cage created: 841 control vertices, 840 faces. Featureless envelope intentionally shown for shape review.')
