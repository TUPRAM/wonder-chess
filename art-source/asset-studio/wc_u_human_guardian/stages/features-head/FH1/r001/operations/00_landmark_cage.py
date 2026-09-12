import math

# Original sparse anatomical scaffold. Front stations are placed at feature
# boundaries; the back has a separate cranium arc. Units: metres, +Y front.
FRONT_U = [-1,-.93,-.84,-.73,-.62,-.51,-.41,-.31,-.24,-.18,-.12,-.06,0,.06,.12,.18,.24,.31,.41,.51,.62,.73,.84,.93,1]
# z, half width, front depth, side depth, rear depth
HEAD_ROWS = [
 (1.563,.038,.010,-.030,-.061),
 (1.577,.045,.061,-.027,-.083),
 (1.590,.058,.065,-.025,-.096),
 (1.606,.068,.059,-.023,-.103),
 (1.617,.073,.059,-.022,-.107),
 (1.624,.075,.060,-.021,-.109),
 (1.632,.077,.059,-.020,-.111),
 (1.643,.079,.057,-.020,-.112),
 (1.650,.080,.058,-.020,-.112),
 (1.658,.081,.063,-.021,-.112),
 (1.668,.083,.066,-.021,-.112),
 (1.679,.084,.058,-.021,-.112),
 (1.689,.084,.056,-.021,-.111),
 (1.699,.083,.058,-.021,-.110),
 (1.709,.082,.061,-.021,-.108),
 (1.720,.081,.062,-.021,-.105),
 (1.733,.080,.058,-.022,-.101),
 (1.750,.077,.047,-.026,-.093),
 (1.768,.067,.024,-.033,-.081),
 (1.783,.047,.001,-.040,-.065),
 (1.794,.023,-.024,-.043,-.053),
]
NOSE_PORT=(8,16,7,15)
MOUTH_PORT=(6,18,2,7)
EYE_PORT_R=(16,21,10,15)
EYE_PORT_L=(3,8,10,15)

def grid_point(r,c):
    z,w,front,side,rear=HEAD_ROWS[r]
    u=FRONT_U[c]
    x=w*u
    y=front+(side-front)*u*u
    # Broad cheek plane, independent of the eyeball.
    if 7 <= r <= 11:
        y += .004*math.sin(math.pi*min(1,abs(u)/.85))
    # The cheek-to-jaw transition stays planar and softly angular.
    if 1 <= r <= 3:
        z += .005*abs(u)**1.6
    return (x,y,z)

def port_coords(port):
    c0,c1,r0,r1=port
    return ([(r0,c) for c in range(c0,c1)] +
            [(r,c1) for r in range(r0,r1)] +
            [(r1,c) for c in range(c1,c0,-1)] +
            [(r,c0) for r in range(r1,r0,-1)])

def build_nose():
    c0,c1,r0,r1=NOSE_PORT
    verts=[];faces=[];lookup={}
    # Explicit transverse sections: outer cheek, alar side, intermediate,
    # dorsum flank, midline. These are editable cage coordinates, not a
    # displacement or projection onto the rejected head.
    depths=[
      [.057,.060,.063,.065,.067],
      [.058,.074,.082,.080,.083],
      [.062,.086,.095,.101,.103],
      [.063,.079,.088,.093,.096],
      [.057,.066,.076,.082,.085],
      [.055,.061,.070,.075,.077],
      [.057,.060,.066,.070,.071],
      [.060,.062,.064,.065,.066],
      [.061,.062,.062,.062,.062],
    ]
    for r in range(r0,r1+1):
        for c in range(c0,c1+1):
            x,y,z=grid_point(r,c)
            j=c-c0;half=min(j,8-j)
            if c not in [c0,c1] and r not in [r0,r1]:
                y=depths[r-r0][half]
                if r==8:
                    z += [0,-.0005,.0005,-.0015,-.0035,-.0015,.0005,-.0005,0][j]
            lookup[(r,c)]=len(verts);verts.append((x,y,z))
    # Paired nostril apertures under the tip, each spans two meaningful cells.
    holes=[(9,11,8,9),(13,15,8,9)]
    for r in range(r0,r1):
        for c in range(c0,c1):
            omitted=False
            for a,b,d,e in holes:
                if a<=c<b and d<=r<e:omitted=True
            if not omitted:
                faces.append((lookup[(r,c)],lookup[(r,c+1)],lookup[(r+1,c+1)],lookup[(r+1,c)]))
    # Reshape the aperture itself, preserving the outer interface. Nostril
    # vaults turn inward behind the skin instead of painted black discs.
    nostril_groups=[]
    for sign,hole in [(-1,holes[0]),(1,holes[1])]:
        ids=[lookup[rc] for rc in port_coords(hole)]
        pts=[(.0055,.083,1.649),(.0105,.084,1.6475),(.016,.081,1.6485),(.0165,.086,1.651),(.011,.091,1.6535),(.006,.088,1.652)]
        if sign<0:pts=[pts[i] for i in [2,1,0,5,4,3]]
        for i,p in zip(ids,pts):verts[i]=(sign*p[0],p[1],p[2])
        previous=ids
        for k in [1,2]:
            current=[]
            for idx in ids:
                x,y,z=verts[idx]
                current.append(len(verts));verts.append((sign*.0108+(x-sign*.0108)*(.86 if k==1 else .60),y-.0025*k,z+.0015*k))
            for j in range(6):faces.append((previous[j],previous[(j+1)%6],current[(j+1)%6],current[j]))
            previous=current
        faces.append(tuple(reversed(previous)))
        nostril_groups+=ids
    return {'vertices':verts,'faces':faces,'root_loop':[lookup[rc] for rc in port_coords(NOSE_PORT)],'grid_keys':list(lookup),'named_vertex_groups':{'Nostril_Margins':nostril_groups,'Bridge_Midline':[lookup[(r,12)] for r in range(9,16)]},'design_notes':'Original nasal control cage with actual paired nostril vaults; exact 32-vertex planned head interface.'}
