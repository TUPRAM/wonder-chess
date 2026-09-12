"""Offline weak-perspective camera fit; no mesh or image modification."""
import math,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
anchor=(0,.04,1.67)
landmarks=[
 ('near_pupil',(.034,.0597,1.690),(123,89),1.5),
 ('far_pupil',(-.034,.0597,1.690),(159,95),2),
 ('tip',(0,.087,1.662),(153,112),2),
 ('columella',(0,.077,1.651),(150,119),2.5),
 ('mouth',(0,.073,1.6244),(141,131),1.5),
 ('chin',(0,.061,1.582),(137,161),3),
 ('tragus',(.075,-.002,1.674),(76,110),5),
]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def camera_fit(yaw,pitch):
    t=math.radians(yaw);p=math.radians(pitch)
    right=(-math.cos(t),math.sin(t),0)
    up=(-math.sin(t)*math.sin(p),-math.cos(t)*math.sin(p),math.cos(p))
    view=(math.sin(t)*math.cos(p),math.cos(t)*math.cos(p),math.sin(p))
    pairs=[]
    for label,v,xy,sigma in landmarks:
        v=tuple(x-y for x,y in zip(v,anchor));pairs.append((dot(right,v),-dot(up,v),xy[0],xy[1],1/sigma**2))
    sw=sum(a[4] for a in pairs);means=[sum(a[k]*a[4] for a in pairs)/sw for k in range(4)]
    aa=bb=den=0
    for x,y,X,Y,w in pairs:
        x-=means[0];y-=means[1];X-=means[2];Y-=means[3]
        aa+=w*(x*X+y*Y);bb+=w*(x*Y-y*X);den+=w*(x*x+y*y)
    A=aa/den;B=bb/den;scale=math.hypot(A,B);roll=math.atan2(B,A)
    tx=means[2]-A*means[0]+B*means[1];ty=means[3]-B*means[0]-A*means[1]
    err=sum(w*((A*x-B*y+tx-X)**2+(B*x+A*y+ty-Y)**2) for x,y,X,Y,w in pairs)
    return err,dict(yaw_degrees=yaw,pitch_degrees=pitch,image_rotation_degrees=math.degrees(roll),pixels_per_metre=scale,tx=tx,ty=ty,right=right,up=up,view=view,A=A,B=B)
best=(float('inf'),None)
for yaw in range(15,66):
    for pitch in range(-30,21):
        candidate=camera_fit(yaw,pitch)
        if candidate[0]<best[0]:best=candidate
for step in [.2,.04]:
    yaw=best[1]['yaw_degrees'];pitch=best[1]['pitch_degrees']
    for i in range(-5,6):
        for j in range(-5,6):
            candidate=camera_fit(yaw+i*step,pitch+j*step)
            if candidate[0]<best[0]:best=candidate
r=best[1];ang=math.radians(r['image_rotation_degrees']);c=math.cos(ang);ss=math.sin(ang)
right=tuple(c*x+ss*y for x,y in zip(r['right'],r['up']))
up=tuple(-ss*x+c*y for x,y in zip(r['right'],r['up']))
target=tuple(anchor[k]+right[k]*(105-r['tx'])/r['pixels_per_metre']+up[k]*(r['ty']-98.5)/r['pixels_per_metre'] for k in range(3))
r.update(camera_right=right,camera_up=up,camera_target=target,ortho_scale=210/r['pixels_per_metre'],weighted_error=best[0])
residuals=[]
for label,v,xy,sigma in landmarks:
    v=tuple(x-y for x,y in zip(v,anchor));x=dot(r['right'],v);y=-dot(r['up'],v)
    pred=(r['A']*x-r['B']*y+r['tx'],r['B']*x+r['A']*y+r['ty'])
    residuals.append(dict(label=label,observed=xy,predicted=pred,uncertainty_pixels=sigma,error_pixels=math.dist(xy,pred)))
r['landmarks']=residuals
r['limitations']='Approximate hand-read illustrated landmarks and approximate cage locations. Weak-perspective pose aid only, not measured silhouette agreement or artistic approval. Neutral baseline cameras unchanged.'
(ROOT/'reviews/portrait_camera_fit.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
