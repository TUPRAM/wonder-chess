def build_mouth():
    outer=[grid_point(r,c) for r,c in port_coords(MOUTH_PORT)]
    count=len(outer);verts=[];faces=[]
    for layer in range(7):
        for ox,oy,oz in outer:
            theta=math.atan2((oz-1.617)/.026,ox/.041)
            q=math.cos(theta);s=math.sin(theta);upper=s>=0
            width=.026
            x=width*q
            fullness=max(0,1-q*q)
            line=1.621+.0008*fullness-.0004*math.exp(-(q/.16)**2)
            margin_y=.060+.011*fullness
            cupid=1+.24*math.exp(-((abs(q)-.27)/.18)**2)-.12*math.exp(-(q/.11)**2)
            height=(.0060*cupid if upper else .0076)*fullness**.70
            sign=1 if upper else -1
            if layer==0:
                y=margin_y-.004;z=line+sign*(.0004+.0003*abs(s));x*=.985
            elif layer==1:
                y=margin_y;z=line+sign*(.00015+.00020*abs(s))
            elif layer==2:
                y=margin_y+.0018*fullness;z=line+sign*(.00065+height*.58);x*=1.015
            elif layer==3:
                y=.058+.0095*fullness;z=line+sign*(.0012+height);x*=1.04
            elif layer==4:
                y=.057+.0066*fullness;z=line+sign*(.0028+height);x*=1.10
            elif layer==5:
                ix=width*1.10*q;iy=.057+.0066*fullness;iz=line+sign*(.0028+height)
                x=ix*.47+ox*.53;y=iy*.47+oy*.53;z=iz*.47+oz*.53
                # The paired philtrum columns end at the upper lip's bow.
                if upper:y+=.0012*math.exp(-((abs(x)-.006)/.0035)**2)
            else:x,y,z=ox,oy,oz
            verts.append((x,y,z))
    for k in range(6):
        for j in range(count):faces.append((k*count+j,k*count+(j+1)%count,(k+1)*count+(j+1)%count,(k+1)*count+j))
    return {'vertices':verts,'faces':faces,'root_loop':list(range(6*count,7*count)),'named_vertex_groups':{'Mouth_Opening':list(range(count,2*count)),'Vermilion_Border':list(range(3*count,4*count)),'Perioral_Transition':list(range(4*count,6*count))},'design_notes':'Closed calm expression study with shallow cupid bow, continuous upper/lower lips, recessed mouth cavity and matching 34-vertex surrounding face interface.'}
