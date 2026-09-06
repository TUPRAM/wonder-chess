"""Readable reaction poses on the frozen Wonder Chess family skeletons."""
import math
import bpy
from mathutils import Vector, Matrix
from hand_contacts import place_hand


def amount(frame,end):
    t=max(0,min(1,(frame-1)/end/.76))
    return t*t*(3-2*t)


def refine_body(unit,arm,clip,frame,end,release):
    t=(frame-1)/end
    def rot(name,x=0,y=0,z=0):
        if name.startswith(('upperarm','lowerarm','calf')):x=-x
        arm.pose.bones[name].rotation_euler=tuple(math.radians(v) for v in (x,y,z))
    if clip=='Hit':
        a=max(0,math.sin(math.pi*t))**.7
        rot('spine_01',-10*a,0,-8*a)
        rot('spine_02',-27*a,8*a,0)
        rot('head',18*a,-5*a,0)
        rot('upperarm_l',-7-20*a,0,-5-12*a)
        rot('upperarm_r',-7-12*a,0,5+9*a)
        rot('lowerarm_l',-10-18*a);rot('lowerarm_r',-10-12*a)
    elif clip=='Defeat':
        a=amount(frame,end)
        rot('spine_01',20*a);rot('spine_02',6*a);rot('head',24*a)
        rot('upperarm_l',14*a);rot('upperarm_r',19*a)
        rot('lowerarm_l',-10);rot('lowerarm_r',-10);rot('hand_l');rot('hand_r')
        thigh,calf=(46,96) if unit['id']=='wc_u_orc_mage' else (68,132)
        for side in ('l','r'):
            rot('thigh_'+side,thigh*a);rot('calf_'+side,calf*a)
            rot('foot_'+side,(calf-thigh)*a)
        arm.pose.bones['pelvis'].location=(0,0,0)
        bpy.context.view_layer.update()
        foot=arm.pose.bones['foot_l']
        delta=Vector((0,foot.bone.head_local.y-foot.head.y,foot.bone.head_local.z-foot.head.z))
        arm.pose.bones['pelvis'].location=arm.pose.bones['pelvis'].bone.matrix_local.to_3x3().inverted()@delta
        bpy.context.view_layer.update()
        for side in ('l','r'):
            foot=arm.pose.bones['foot_'+side]
            matrix=foot.bone.matrix_local.copy();matrix.translation=foot.head.copy();foot.matrix=matrix
        bpy.context.view_layer.update()
    elif clip=='Active' and unit['id'] in ('wc_u_human_priest','wc_u_human_mage','wc_u_orc_mage'):
        times=[1,max(2,release//2),release,min(end+1,release+9),end+1]
        def sample(values):
            for i in range(1,len(times)):
                if frame<=times[i]:
                    a=max(0,min(1,(frame-times[i-1])/max(1,times[i]-times[i-1])))
                    return values[i-1]*(1-a)+values[i]*a
            return values[-1]
        a=sample([0,1,1,.5,0])
        if unit['id']=='wc_u_human_mage':
            rot('upperarm_r',sample([-7,-65,-110,-55,-7]),0,10*a)
            rot('lowerarm_r',sample([-10,-75,-8,-25,-10]))
            rot('upperarm_l',sample([-7,-45,-102,-40,-7]),0,-24*a)
            rot('lowerarm_l',sample([-10,-65,-8,-20,-10]))
            rot('spine_02',sample([0,-9,12,4,0]))
        elif unit['id']=='wc_u_human_priest':
            rot('upperarm_r',sample([-7,-62,-112,-50,-7]),0,12*a)
            rot('lowerarm_r',sample([-10,-38,-8,-20,-10]))
            rot('upperarm_l',-65*a,0,-35*a);rot('lowerarm_l',-18*a)
            rot('spine_02',-7*a);rot('head',-8*a)
        else:
            rot('upperarm_r',sample([-7,-115,-20,-12,-7]),0,sample([5,-20,18,9,5]))
            rot('lowerarm_r',sample([-10,-18,-12,-10,-10]))
            rot('upperarm_l',-65*a,0,-40*a);rot('lowerarm_l',-12*a)
            rot('spine_02',sample([0,-8,12,4,0]))
    elif clip=='Victory' and unit['unit_class'] in ('priest','mage','ranger'):
        a=max(0,math.sin(math.pi*t))
        rot('upperarm_r',-7-123*a,0,24*a);rot('lowerarm_r',-10-22*a)
        rot('upperarm_l',-7-55*a,0,-30*a);rot('lowerarm_l',-10-15*a)
        rot('spine_02',-10*a);rot('head',-12*a)


def refine_contacts(unit,arm,clip,frame,end,release):
    if clip not in ('Defeat','Victory'):return 0
    if clip=='Victory' and unit['id'] not in ('wc_u_human_priest','wc_u_human_mage','wc_u_orc_mage'):return 0
    a=amount(frame,end) if clip=='Defeat' else max(0,math.sin(math.pi*(frame-1)/end))
    if a<=0:return 0
    height=unit['height_m'];uid=unit['id'];error=0
    def turn(x=0,y=0,z=0):
        return Matrix.Rotation(math.radians(z),3,'Z')@Matrix.Rotation(math.radians(y),3,'Y')@Matrix.Rotation(math.radians(x),3,'X')
    def lower(side,target,rotation):
        bone=arm.pose.bones['hand_'+side]
        current=bone.matrix.to_3x3()@bone.bone.matrix_local.to_3x3().inverted()
        blended=current.to_quaternion().slerp(rotation.to_quaternion(),a).to_matrix()
        return place_hand(arm,side,bone.tail.lerp(Vector(target)*height,a),blended,height)
    if clip=='Victory':
        error=lower('r',(-.36 if unit['race']=='orc' else -.31,.09,.94),turn(-12,0,0))
        return max(error,lower('l',(.27,.14,.71),turn(-35,0,-15)))
    if uid in ('wc_u_dwarf_guardian','wc_u_dwarf_warrior'):
        error=lower('r',(.02,-.12,.36),turn(-80,0,0))
        right=arm.pose.bones['hand_r'];grip=right.matrix@right.bone.matrix_local.inverted()@(right.bone.tail_local+Vector((0,0,.17))*height)
        error=max(error,place_hand(arm,'l',grip,turn(0,-35,0),height))
    elif uid=='wc_u_dwarf_ranger':
        error=lower('r',(-.05,0,.37),turn(-82,0,0))
        right=arm.pose.bones['hand_r'];grip=right.matrix@right.bone.matrix_local.inverted()@(right.bone.tail_local+Vector((.08,0,.11))*height)
        error=max(error,place_hand(arm,'l',grip,turn(0,-20,0),height))
    elif uid=='wc_u_elf_priest':
        error=lower('l',(.13,.08,.33),turn(-48,0,0))
        left=arm.pose.bones['hand_l'];grip=left.matrix@left.bone.matrix_local.inverted()@(left.bone.tail_local+Vector((-.08,.085,.13))*height)
        error=max(error,place_hand(arm,'r',grip,turn(0,0,20),height))
    else:
        right=(-.22,-.06,.39) if uid=='wc_u_orc_mage' else (-.22,.08 if uid=='wc_u_elf_ranger' else .19,.30)
        left=(.24,0,.40) if uid=='wc_u_orc_mage' else (.24,.10 if uid=='wc_u_elf_ranger' else .22,.33)
        error=lower('r',right,turn(-74,0,0))
        error=max(error,lower('l',left,turn(-70 if uid in ('wc_u_human_guardian','wc_u_elf_ranger') else -65,0,0)))
        if uid=='wc_u_elf_ranger':arm.pose.bones['weapon_l'].location=(0,0,0)
    return error
