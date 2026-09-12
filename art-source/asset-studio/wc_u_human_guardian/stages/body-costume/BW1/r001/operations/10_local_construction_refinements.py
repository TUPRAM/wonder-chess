import bpy,math,json
from mathutils import Vector
s=bpy.data.scenes['BW1_BODY_COSTUME']
# Explicitly reshape the breast cage into a sternum and paired side planes.
ob=bpy.data.objects['BW1_Breastplate'];rxs=[.166,.172,.195,.199,.19,.139];ys=[.129,.143,.19,.198,.174,.150]
for v in ob.data.vertices:
    j=v.index//13;i=v.index%13;u=-1+2*i/12
    v.co.x=rxs[j]*u
    v.co.y=ys[j]-.073*abs(u)+.008*(1-abs(u))**5
    if j==0:v.co.z=1.15-.052*(1-abs(u))
    if j==5:v.co.z=1.456-.018*(1-abs(u))
for p in ob.data.polygons:p.use_smooth=False
ob.data.update()
# Asymmetric shield-like lower shoulder edges and forward breadth replace straight cylindrical bands.
for name in ['BW1_Pauldron_R_Cap','BW1_Pauldron_R_Lame1','BW1_Pauldron_R_Lame2']:
    ob=bpy.data.objects[name];count=len(ob.data.vertices)//15
    a=Vector((.18185,-.04636,1.44498));axis=(Vector((.36106,-.04210,1.24891))-a).normalized()
    for v in ob.data.vertices:
        row=v.index//15;i=v.index%15;u=-1+2*i/14
        if row==count-1:v.co+=axis*(.017*(1-abs(u))-.008*abs(u))
        if 'Cap' in name and row in [1,2,3]:
            v.co.y+=.009*max(0,math.sin((u+1)*math.pi/2))
    ob.data.update()
# Thin cloth boundaries keep their authored hem shape under subdivision.
for ob in bpy.data.collections['BW1_CLOTH'].objects:
    if not ob.name.startswith(('BW1_Tabard','BW1_CoatPanel')):continue
    edge_use={}
    for p in ob.data.polygons:
        ids=list(p.vertices)
        for a,b in zip(ids,ids[1:]+ids[:1]):
            key=tuple(sorted((a,b)));edge_use[key]=edge_use.get(key,0)+1
    crease=ob.data.attributes.get('crease_edge') or ob.data.attributes.new('crease_edge','FLOAT','EDGE')
    for e,item in zip(ob.data.edges,crease.data):item.value=.9 if edge_use.get(tuple(sorted(e.vertices)))==1 else 0
    if ob.name.startswith('BW1_Tabard'):
        for v in ob.data.vertices:
            t=max(0,min(1,(1.105-v.co.z)/.43));v.co.y+=(-1 if 'Rear' in ob.name else 1)*.004*math.sin(v.co.x*40)*t
# Fit the original vamp strap onto the observed boot surface, maintaining a separate thickness layer.
strap=bpy.data.objects['BW1_BootVampStrap_R'];mod=strap.modifiers.new('Selected boot contact fit','SHRINKWRAP');mod.target=bpy.data.objects['BW1_Boot_Pair_SourceFit'];mod.wrap_method='NEAREST_SURFACEPOINT';mod.offset=.003
bpy.context.view_layer.objects.active=strap
for i in range(len(strap.modifiers)-1):bpy.ops.object.modifier_move_up(modifier=mod.name)
strap['fitting_note']='Whole narrow attachment strap fitted to boot; boot upper/crest retains independent volume.'
for name in ['BW1_BootSole_R','BW1_BootSole_L_Blockout']:
    ob=bpy.data.objects[name];n=len(ob.data.vertices)//2
    for v in ob.data.vertices:
        if v.index>=n:v.co.z=.009 if v.co.y<.07 else .012
    ob.data.update();ob['sole_thickness_m']='0.036-0.039';ob['adaptation']='Raised sole upper boundary to enclose the imported arch/instep gap; flat ground boundary retained'
# Add restrained elbow fullness on the continuous garment only.
ob=bpy.data.objects['BW1_CoatUpper_Continuous'];elbow=Vector((.36106,-.04210,1.24891))
for v in ob.data.vertices:
    delta=v.co-elbow
    if v.co.x>.27 and v.co.x<.43 and abs(delta.z)<.11:
        t=(v.co.x-.27)/.16
        amount=.0045*math.sin(t*math.pi*4)*math.sin(t*math.pi)
        radial=Vector((delta.x*.3,delta.y,delta.z*.3))
        if radial.length>.01:v.co+=radial.normalized()*amount
ob.data.update()
# A separate closeup camera covers the complete right shin and boot.
camdata=bpy.data.cameras.new('BW1_Camera_leg_proof');cam=bpy.data.objects.new('BW1_Camera_leg_proof',camdata);bpy.data.collections['BW1_PRESENTATION'].objects.link(cam)
cam.location=(1.25,1.8,.65);target=Vector((.19,.035,.29));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=.79
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
for view in ['front','profile','back','three_quarter']:
    s.camera=bpy.data.objects['BW1_Camera_'+view];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/blockout_r002_'+view+'.png';bpy.ops.render.render(write_still=True)
s.camera=cam;s.render.resolution_x=900;s.render.resolution_y=900;s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/leg_stance_r000.png';bpy.ops.render.render(write_still=True)
s.render.resolution_x=850;s.render.resolution_y=1100
print('Control-surface armor shaping, sharper cloth hems, boot strap contact and enclosed sole captured for review.')

