"""Bake reachable support-hand poses into the existing humanoid bones."""
import math
import bpy
from mathutils import Vector,Matrix


def oriented_matrix(head,direction):
    y=direction.normalized();z=Vector((0,1,0))
    z=(z-y*z.dot(y)).normalized()
    if z.length<.01:z=Vector((0,0,1))
    x=y.cross(z).normalized();z=x.cross(y).normalized()
    matrix=Matrix((x,y,z)).transposed().to_4x4();matrix.translation=head
    return matrix


def place_hand(arm,side,palm,rotation,height):
    upper=arm.pose.bones['upperarm_'+side];lower=arm.pose.bones['lowerarm_'+side];hand=arm.pose.bones['hand_'+side]
    bpy.context.view_layer.update();shoulder=upper.head.copy()
    target=Vector(palm)-rotation@(hand.bone.tail_local-hand.bone.head_local);line=target-shoulder
    distance=line.length;direction=line.normalized();a=upper.bone.length;b=lower.bone.length
    reach=min(max(distance,abs(a-b)+.001),a+b-.001)
    target=shoulder+direction*reach
    along=(a*a-b*b+reach*reach)/(2*reach);across=math.sqrt(max(0,a*a-along*along))
    side_vector=Vector((.8 if side=='l' else -.8,.12,-1))
    bend=(side_vector-direction*side_vector.dot(direction)).normalized()
    elbow=shoulder+direction*along+bend*across
    upper.matrix=oriented_matrix(shoulder,elbow-shoulder);upper.scale=(1,1,1);bpy.context.view_layer.update()
    lower.matrix=oriented_matrix(elbow,target-elbow);lower.scale=(1,1,1);bpy.context.view_layer.update()
    hand_matrix=(rotation@hand.bone.matrix_local.to_3x3()).to_4x4();hand_matrix.translation=target
    hand.matrix=hand_matrix;hand.scale=(1,1,1);bpy.context.view_layer.update()
    return max(0,distance-reach)


def contact_pose(unit,arm,clip,frame,end,release):
    uid=unit['id'];height=unit['height_m'];error=0
    bpy.context.view_layer.update()
    spine=arm.pose.bones['spine_02'];body=spine.matrix@spine.bone.matrix_local.inverted();bodyrot=body.to_3x3()
    def position(xyz):return body@(Vector(xyz)*height)
    def rotation(x=0,y=0,z=0):
        return bodyrot@Matrix.Rotation(math.radians(z),3,'Z')@Matrix.Rotation(math.radians(y),3,'Y')@Matrix.Rotation(math.radians(x),3,'X')
    def follow(source_offset,driver,side,turn):
        hand=arm.pose.bones['hand_'+driver]
        source=hand.bone.tail_local+Vector(source_offset)*height
        grip=hand.matrix@hand.bone.matrix_local.inverted()@source
        return place_hand(arm,side,grip,turn,height)
    def sampled(values):
        times=[1,max(2,release//2),release,min(end+1,release+9),end+1]
        for i in range(1,len(times)):
            if frame<=times[i]:
                t=max(0,min(1,(frame-times[i-1])/max(1,times[i]-times[i-1])))
                return values[i-1]*(1-t)+values[i]*t
        return values[-1]
    envelope=sampled([0,1,1,.5,0])
    anticipate=frame<release
    celebrate=math.sin((frame-1)/end*math.pi) if clip=='Victory' else 0
    if uid in ('wc_u_dwarf_guardian','wc_u_dwarf_warrior','wc_u_dwarf_ranger'):
        if uid=='wc_u_dwarf_ranger':
            active=clip=='Active'
            turn=rotation(-76-(9*envelope if clip in ('Attack','Active') else 0),0,0)
            pull=sampled([0,-.075,.075,.035,0]) if active else 0
            error=place_hand(arm,'r',position((-.05,.10+pull,.58+(.055*envelope if active else 0)+.16*celebrate)),turn,height)
            error=max(error,follow((.08,0,.11),'r','l',rotation(0,-20,0)))
        else:
            strike=clip in ('Attack','Active') and not(clip=='Active' and uid=='wc_u_dwarf_guardian')
            rise=sampled([0,.14,.13,.06,0]) if strike else 0
            swing=sampled([0,-30,-62,-31,0]) if strike else 0
            offset_x=sampled([0,.02,.07,.03,0]) if strike else 0
            offset_y=sampled([0,-.03,-.09,-.045,0]) if strike else 0
            if clip=='Victory':rise=.15*math.sin((frame-1)/end*math.pi)
            turn=rotation(swing,65,0)
            error=place_hand(arm,'r',position((-.09+offset_x,.16+offset_y,.47+rise)),turn,height)
            error=max(error,follow((0,0,.17),'r','l',rotation(0,-35,0)))
    elif uid=='wc_u_elf_ranger':
        turn=rotation(0,0,-8)
        ready=envelope if clip in ('Attack','Active') else 0
        pull=sampled([.012,.13,.012,.012,.012]) if clip=='Attack' else .012
        arm.pose.bones['weapon_l'].location.y=-(pull-.012)*height
        error=place_hand(arm,'l',position((.20-.11*ready,.13+.07*ready,.58+.055*ready+.08*celebrate)),turn,height)
        hand=arm.pose.bones['hand_l'];source=hand.bone.tail_local+Vector((-.01,-pull,.015))*height
        grip=hand.matrix@hand.bone.matrix_local.inverted()@source
        target=position((-.24,.10,.42+.50*celebrate)).lerp(grip,ready)
        error=max(error,place_hand(arm,'r',target,rotation(0,0,20*ready),height))
    elif uid=='wc_u_elf_priest':
        chord=envelope if clip=='Active' else 0
        error=place_hand(arm,'l',position((.12+.08*chord+.04*celebrate,.12,.51+.07*chord+.09*celebrate)),rotation(0,35*celebrate,0),height)
        pluck=sampled([-.08,-.20,-.32,-.18,-.08]) if clip=='Active' else -.08
        pluck-=.12*celebrate
        error=max(error,follow((pluck,.085+.010*math.sin((frame-1)/end*2*math.pi),.13),'l','r',rotation(0,0,20)))
    return error
