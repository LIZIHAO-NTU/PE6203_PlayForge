import math, sys, os, random
import pygame

# ---------- math helpers ----------
def vadd(a,b): return (a[0]+b[0],a[1]+b[1],a[2]+b[2])
def vsub(a,b): return (a[0]-b[0],a[1]-b[1],a[2]-b[2])
def vmul(a,s): return (a[0]*s,a[1]*s,a[2]*s)
def vdot(a,b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def vcross(a,b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def vlen(a): return math.sqrt(vdot(a,a))
def vnorm(a):
    l=vlen(a)
    return (0,0,0) if l<1e-12 else (a[0]/l,a[1]/l,a[2]/l)

WIDTH, HEIGHT = 960, 640
FOV = math.radians(60)
NEAR = 0.1
LIGHT = vnorm((-2,4,1))

# ---------- camera ----------
class Camera:
    def __init__(self):
        self.reset()
    def reset(self):
        self.dist=math.sqrt(10*10+14*14)
        self.yaw=math.atan2(10,14)
        self.height=4.0
        self.pitch=math.radians(22)
        self.target=(0,2.5,0)
    def eye(self):
        x=self.dist*math.sin(self.yaw)
        z=self.dist*math.cos(self.yaw)
        return (x,self.height,z)
    def dir(self):
        e=self.eye(); t=self.target
        # pitch applied on vertical
        horiz=vnorm((t[0]-e[0],0,t[2]-e[2]))
        d=(horiz[0]*math.cos(self.pitch), math.sin(self.pitch)*-1, horiz[2]*math.cos(self.pitch))
        # look down by pitch amount but target above -> aim direction
        return vnorm((t[0]-e[0], t[1]-e[1], t[2]-e[2]))
    def basis(self):
        e=self.eye(); f=vnorm(vsub(self.target,e))
        r=vnorm(vcross(f,(0,1,0)))
        u=vcross(r,f)
        return e,f,r,u
    def project(self,p):
        e,f,r,u=self.basis()
        d=vsub(p,e)
        z=vdot(d,f)
        if z<NEAR: return None
        x=vdot(d,r)
        y=vdot(d,u)
        s=(HEIGHT/2)/math.tan(FOV/2)
        sx=WIDTH/2 + x*s/z
        sy=HEIGHT/2 - y*s/z
        return (sx,sy,z)

# ---------- physics bodies ----------
GRAV=20.0
class Body:
    def __init__(self,kind,pos,half=None,radius=None,mass=1.0):
        self.kind=kind
        self.pos=list(pos)
        self.vel=[0.0,0.0,0.0]
        self.half=half
        self.radius=radius
        self.mass=mass
        self.inv_mass=0 if mass<=0 else 1.0/mass
        self.rest=0.2 if kind=='box' else 0.4
        self.sleep=0
    def aabb(self):
        if self.kind=='box':
            h=self.half
            return (self.pos[0]-h[0],self.pos[1]-h[1],self.pos[2]-h[2],
                    self.pos[0]+h[0],self.pos[1]+h[1],self.pos[2]+h[2])
        r=self.radius
        return (self.pos[0]-r,self.pos[1]-r,self.pos[2]-r,
                self.pos[0]+r,self.pos[1]+r,self.pos[2]+r)

def aabb_overlap(a,b):
    return (a[0]<b[3] and a[3]>b[0] and a[1]<b[4] and a[4]>b[1] and a[2]<b[5] and a[5]>b[2])

class World:
    def __init__(self):
        self.bodies=[]
        self.table_surface=1.0
        self.table_half=4.0
        self.build()
    def build(self):
        self.bodies=[]
        # stack 4x4x1 blocks centered on table, bottom on table surface
        rnd=random.Random(7)
        base_y=1.0+0.5
        for iy in range(4):
            for ix in range(4):
                x=(ix-1.5)*1.0
                y=base_y+iy*1.0
                b=Body('box',(x,y,0),(0.5,0.5,0.5),mass=1.0)
                b.color=(0.88+rnd.uniform(-0.05,0.05),0.84+rnd.uniform(-0.05,0.05),0.78+rnd.uniform(-0.05,0.05))
                self.bodies.append(b)
        self.ball=None
    def remaining_blocks(self):
        cnt=0
        for b in self.bodies:
            if b.kind=='box' and abs(b.pos[0])<=self.table_half and abs(b.pos[2])<=self.table_half \
               and b.pos[1] >= self.table_surface-0.01:
                cnt+=1
        return cnt
    def step(self,dt):
        # gravity
        for b in self.bodies:
            b.vel[1]-=GRAV*dt
            # simple ground friction when resting near ground
        if self.ball:
            self.ball.vel[1]-=GRAV*dt
        # integrate with substeps to avoid tunneling
        n=4
        sdt=dt/n
        for _ in range(n):
            self.substep(sdt)
    def substep(self,sdt):
        allb=list(self.bodies)
        if self.ball: allb.append(self.ball)
        for b in allb:
            # move with swept check against ground (no tunneling)
            b.pos[0]+=b.vel[0]*sdt
            b.pos[1]+=b.vel[1]*sdt
            b.pos[2]+=b.vel[2]*sdt
        # ground
        for b in allb:
            bb=b.aabb()
            if bb[1]<0:
                pen=-bb[1]
                b.pos[1]+=pen
                if b.vel[1]<0:
                    b.vel[1]=-b.vel[1]*b.rest
                    if abs(b.vel[1])<0.6: b.vel[1]=0
                # friction
                b.vel[0]*= (1.0-4.0*sdt)
                b.vel[2]*= (1.0-4.0*sdt)
        # table collision (table top slab + legs treated as block under surface)
        for b in allb:
            if b is self.ball: continue
            bb=b.aabb()
            # table top: y range 0.7..1.0, x/z within +-4
            if bb[0]<4 and bb[3]>-4 and bb[2]<4 and bb[5]>-4:
                # top face
                if bb[1]<1.0 and b.pos[1]>0.5 and b.vel[1]<0:
                    if bb[1]>0.6:
                        b.pos[1]=1.0+b.half[1]
                        b.vel[1]=-b.vel[1]*b.rest
                        if abs(b.vel[1])<0.6: b.vel[1]=0
        # ball vs table top
        if self.ball:
            bb=self.ball.aabb()
            if bb[1]<1.0 and bb[4]>0.7 and abs(bb[0])<4.2 and abs(bb[2])<4.2:
                if bb[1]>0.6:
                    self.ball.pos[1]=1.0+self.ball.radius
                    if self.ball.vel[1]<0:
                        self.ball.vel[1]=-self.ball.vel[1]*self.ball.rest
                        if abs(self.ball.vel[1])<0.6: self.ball.vel[1]=0
                    self.ball.vel[0]*=0.97
                    self.ball.vel[2]*=0.97
        # body-body collisions (box-box, box-ball) - simple AABB MTV
        allb=list(self.bodies)
        if self.ball: allb.append(self.ball)
        for i in range(len(allb)):
            for j in range(i+1,len(allb)):
                a,b=allb[i],allb[j]
                ba=a.aabb(); bb=b.aabb()
                if not aabb_overlap(ba,bb): continue
                # compute MTV
                ox=min(ba[3],bb[3])-max(ba[0],bb[0])
                oy=min(ba[4],bb[4])-max(ba[1],bb[1])
                oz=min(ba[5],bb[5])-max(ba[2],bb[2])
                if ox<=0 or oy<=0 or oz<=0: continue
                if ox<oy and ox<oz:
                    n=(1,0,0) if a.pos[0]<b.pos[0] else (-1,0,0)
                    pen=ox
                elif oy<oz:
                    n=(0,1,0) if a.pos[1]<b.pos[1] else (0,-1,0)
                    pen=oy
                else:
                    n=(0,0,1) if a.pos[2]<b.pos[2] else (0,0,-1)
                    pen=oz
                tot=a.inv_mass+b.inv_mass
                if tot<=0: continue
                a.pos[0]-=n[0]*pen*(a.inv_mass/tot)
                a.pos[1]-=n[1]*pen*(a.inv_mass/tot)
                a.pos[2]-=n[2]*pen*(a.inv_mass/tot)
                b.pos[0]+=n[0]*pen*(b.inv_mass/tot)
                b.pos[1]+=n[1]*pen*(b.inv_mass/tot)
                b.pos[2]+=n[2]*pen*(b.inv_mass/tot)
                rel=(b.vel[0]-a.vel[0],b.vel[1]-a.vel[1],b.vel[2]-a.vel[2])
                vn=vdot(rel,n)
                if vn<0:
                    e=min(a.rest,b.rest)
                    jimp=-(1+e)*vn/tot
                    a.vel[0]-=n[0]*jimp*a.inv_mass
                    a.vel[1]-=n[1]*jimp*a.inv_mass
                    a.vel[2]-=n[2]*jimp*a.inv_mass
                    b.vel[0]+=n[0]*jimp*b.inv_mass
                    b.vel[1]+=n[1]*jimp*b.inv_mass
                    b.vel[2]+=n[2]*jimp*b.inv_mass
                    # friction
                    t=(rel[0]-vn*n[0],rel[1]-vn*n[1],rel[2]-vn*n[2])
                    tl=vlen(t)
                    if tl>1e-4:
                        td=(t[0]/tl,t[1]/tl,t[2]/tl)
                        jt=-vdot(rel,td)/tot*0.4
                        a.vel[0]-=td[0]*jt*a.inv_mass
                        a.vel[1]-=td[1]*jt*a.inv_mass
                        a.vel[2]-=td[2]*jt*a.inv_mass
                        b.vel[0]+=td[0]*jt*b.inv_mass
                        b.vel[1]+=td[1]*jt*b.inv_mass
                        b.vel[2]+=td[2]*jt*b.inv_mass
        # damping
        for b in allb:
            if b.pos[1]<0.01:
                b.vel[0]*=0.98
                b.vel[2]*=0.98

# ---------- geometry builders ----------
def box_faces(pos,half,color):
    x,y,z=pos; hx,hy,hz=half
    v=[(x-hx,y-hy,z-hz),(x+hx,y-hy,z-hz),(x+hx,y-hy,z+hz),(x-hx,y-hy,z+hz),
       (x-hx,y+hy,z-hz),(x+hx,y+hy,z-hz),(x+hx,y+hy,z+hz),(x-hx,y+hy,z+hz)]
    faces=[((0,1,2,3),(0,-1,0)),((4,5,6,7),(0,1,0)),
           ((0,1,5,4),(0,0,-1)),((3,2,6,7),(0,0,1)),
           ((0,3,7,4),(-1,0,0)),((1,2,6,5),(1,0,0))]
    out=[]
    for idx,n in faces:
        out.append(([v[i] for i in idx],n,color))
    return out

def sphere_faces(center,radius,color,sides=16,rings=10):
    faces=[]
    for i in range(rings):
        phi0=math.pi*i/rings; phi1=math.pi*(i+1)/rings
        for j in range(sides):
            th0=2*math.pi*j/sides; th1=2*math.pi*(j+1)/sides
            def pt(phi,th):
                return (center[0]+radius*math.sin(phi)*math.cos(th),
                        center[1]+radius*math.cos(phi),
                        center[2]+radius*math.sin(phi)*math.sin(th))
            a=pt(phi0,th0); b=pt(phi0,th1); c=pt(phi1,th1); d=pt(phi1,th0)
            cen=((a[0]+b[0]+c[0]+d[0])/4,(a[1]+b[1]+c[1]+d[1])/4,(a[2]+b[2]+c[2]+d[2])/4)
            n=vnorm(vsub(cen,center))
            faces.append(([a,b,c,d],n,color))
    return faces

def cylinder_faces(base,top,r0,r1,color,sides=16):
    faces=[]
    bx,by,bz=base; tx,ty,tz=top
    for i in range(sides):
        a0=2*math.pi*i/sides; a1=2*math.pi*(i+1)/sides
        p0=(bx+r0*math.cos(a0),by,bz+r0*math.sin(a0))
        p1=(bx+r0*math.cos(a1),by,bz+r0*math.sin(a1))
        p2=(tx+r1*math.cos(a1),ty,tz+r1*math.sin(a1))
        p3=(tx+r1*math.cos(a0),ty,tz+r1*math.sin(a0))
        cen=((p0[0]+p2[0])/2,(p0[1]+p2[1])/2,(p0[2]+p2[2])/2)
        n=vnorm((cen[0]-(bx+tx)/2,0,cen[2]-(bz+tz)/2))
        faces.append(([p0,p1,p2,p3],n,color))
    # caps
    topcap=[(tx+r1*math.cos(2*math.pi*i/sides),ty,tz+r1*math.sin(2*math.pi*i/sides)) for i in range(sides)]
    faces.append((topcap,(0,1,0),color))
    return faces

def cone_faces(base,apex,radius,color,sides=16):
    faces=[]
    bx,by,bz=base
    for i in range(sides):
        a0=2*math.pi*i/sides; a1=2*math.pi*(i+1)/sides
        p0=(bx+radius*math.cos(a0),by,bz+radius*math.sin(a0))
        p1=(bx+radius*math.cos(a1),by,bz+radius*math.sin(a1))
        cen=((p0[0]+p1[0]+apex[0])/3,(p0[1]+p1[1]+apex[1])/3,(p0[2]+p1[2]+apex[2])/3)
        n=vnorm(vsub(cen,(bx,by,bz)))
        faces.append(([p0,p1,apex],n,color))
    basecol=[(bx+radius*math.cos(2*math.pi*i/sides),by,bz+radius*math.sin(2*math.pi*i/sides)) for i in range(sides)]
    faces.append((basecol,(0,-1,0),color))
    return faces

# ---------- scene ----------
def build_scene(world):
    faces=[]
    # ground patches
    rnd=random.Random(1)
    for gx in range(-10,10):
        for gz in range(-10,10):
            g=0.32+0.06*rnd.random()
            col=(g*0.55,g,g*0.45)
            faces+=box_faces((gx+0.5,0,gz+0.5),(0.5,0.02,0.5),col)
    # table
    wood=(0.42,0.26,0.14)
    faces+=box_faces((0,0.85,0),(4,0.15,4),wood)
    legc=(0.32,0.2,0.1)
    for sx in (-3.5,3.5):
        for sz in (-3.5,3.5):
            faces+=box_faces((sx,0.35,sz),(0.2,0.35,0.2),legc)
    # blocks
    for b in world.bodies:
        c=b.color
        faces+=box_faces(b.pos,b.half,c)
    # trees
    tree_pos=[(-16,-16),(16,-16),(-16,16),(16,16)]
    rnd=random.Random(3)
    for i,(tx,tz) in enumerate(tree_pos):
        hscale=1.0+rnd.uniform(-0.15,0.15)
        bark=(0.30+rnd.uniform(-0.03,0.03),0.2+rnd.uniform(-0.03,0.03),0.1)
        faces+=cylinder_faces((tx,0,tz),(tx,4*hscale,tz),0.45,0.3,bark,16)
        layers=[(2.0,1.0,3.0),(1.6,2.6,4.4),(1.1,4.0,5.8)]
        for r,y0,y1 in layers:
            col=(0.12+rnd.uniform(-0.03,0.03),0.4+rnd.uniform(-0.05,0.05),0.15)
            faces+=cone_faces((tx,y0*hscale,tz),(tx,(y1)*hscale,tz),r,col,14)
    # rocks
    rock_data=[((-6,9),0.35),((7,-8),0.5),((11,3),0.7)]
    rnd=random.Random(9)
    for (rx,rz),rad in rock_data:
        col=(0.42+rnd.uniform(-0.05,0.05),)*3
        faces+=sphere_faces((rx,rad*0.7,rz),rad,col,16,8)
    return faces

# ---------- render ----------
def render(screen,cam,cam_face_list,ball,charged,cleared):
    # sky
    for y in range(0,HEIGHT,4):
        t=y/HEIGHT
        c=(int(120+80*t),int(160+60*t),int(220-20*t))
        pygame.draw.rect(screen,c,(0,y,WIDTH,4))
    faces=list(cam_face_list)
    if ball:
        faces+=sphere_faces(ball.pos,ball.radius,(0.5,0.05,0.05),16,10)
    # shading with distance
    eye=cam.eye()
    shaded=[]
    for verts,n,col in faces:
        cen=(sum(v[0] for v in verts)/len(verts),sum(v[1] for v in verts)/len(verts),sum(v[2] for v in verts)/len(verts))
        # backface cull relative to camera
        if vdot(n,vsub(eye,cen))<=0: continue
        lam=max(0,vdot(n,LIGHT))
        sh=0.25+0.75*lam
        d=vlen(vsub(eye,cen))
        dist_sh=max(0.4,1.0-d/60.0)
        c=(max(0,min(1,col[0]*sh*dist_sh)),max(0,min(1,col[1]*sh*dist_sh)),max(0,min(1,col[2]*sh*dist_sh)))
        pts=[]; zsum=0; ok=True
        for v in verts:
            p=cam.project(v)
            if p is None: ok=False; break
            pts.append((p[0],p[1])); zsum+=p[2]
        if not ok: continue
        shaded.append((zsum/len(pts),pts,c))
    # shadow under table and ball as simple dark ellipse on ground
    def shadow(x,z,r):
        p=cam.project((x,0.011,z))
        if p:
            rw=int(r*(HEIGHT/2)/max(0.1,p[2])*0.5)
            if rw>0:
                s=pygame.Surface((rw*2,rw//2*2),pygame.SRCALPHA)
                pygame.draw.ellipse(s,(0,0,0,80),(0,0,rw*2,rw))
                screen.blit(s,(int(p[0]-rw),int(p[1]-rw//4)))
    shadow(0,0,6)
    if ball: shadow(ball.pos[0],ball.pos[2],1.5)
    shaded.sort(key=lambda t:-t[0])
    for z,pts,c in shaded:
        cc=(int(c[0]*255),int(c[1]*255),int(c[2]*255))
        try:
            pygame.draw.polygon(screen,cc,pts)
        except Exception:
            pass
    # HUD
    font=pygame.font.SysFont(None,28)
    if cleared:
        surf=font.render("TABLE CLEAR! Press R to reset",True,(255,255,255))
        screen.blit(surf,(WIDTH//2-surf.get_width()//2,20))
    if charged>0:
        w=int(200*charged)
        pygame.draw.rect(screen,(40,40,40),(20,HEIGHT-50,204,24))
        pygame.draw.rect(screen,(220,120,40),(22,HEIGHT-48,w,20))
        surf=font.render("Power %d%%"%int(charged*100),True,(255,255,255))
        screen.blit(surf,(20,HEIGHT-80))
    else:
        surf=font.render("Hold SPACE to charge",True,(255,255,255))
        screen.blit(surf,(20,HEIGHT-40))

# ---------- main ----------
def main():
    pygame.init()
    screen=pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("Knockdown")
    clock=pygame.time.Clock()
    world=World()
    cam=Camera()
    scene=build_scene(world)
    charge=0.0
    charging=False
    cleared=False
    ready=False
    acc=0.0; DT=1/120.0
    running=True
    while running:
        dt=clock.tick(60)/1000.0
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: running=False
            elif ev.type==pygame.KEYDOWN:
                if ev.key in (pygame.K_q,pygame.K_ESCAPE): running=False
                elif ev.key==pygame.K_r:
                    world.build(); cam.reset(); charge=0; charging=False; cleared=False
                    scene=build_scene(world)
                elif ev.key==pygame.K_SPACE and not charging and world.ball is None:
                    charging=True; charge=0.0
            elif ev.type==pygame.KEYUP:
                if ev.key==pygame.K_SPACE and charging:
                    charging=False
                    e=cam.eye(); d=cam.dir()
                    speed=30.0*charge
                    b=Body('ball',(e[0]+d[0]*0.8,e[1]+d[1]*0.8,e[2]+d[2]*0.8),radius=0.5,mass=5.0)
                    b.vel=[d[0]*speed,d[1]*speed,d[2]*speed]
                    world.ball=b
                    charge=0.0
        keys=pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: cam.yaw-=1.6*dt
        if keys[pygame.K_RIGHT]: cam.yaw+=1.6*dt
        if keys[pygame.K_UP]:
            cam.pitch=min(math.radians(50),cam.pitch+dt*1.0)
            cam.target=(0,cam.target[1]+dt*2.0,0)
        if keys[pygame.K_DOWN]:
            cam.pitch=max(math.radians(5),cam.pitch-dt*1.0)
            cam.target=(0,max(1.0,cam.target[1]-dt*2.0),0)
        if charging:
            charge=min(1.0,charge+dt)
        # fixed step simulation
        acc+=dt
        steps=0
        while acc>=DT and steps<8:
            world.step(DT); acc-=DT; steps+=1
        # check cleared
        if not cleared and world.remaining_blocks()==0:
            cleared=True
        render(screen,cam,scene,world.ball,charge,cleared)
        pygame.display.flip()
        if not ready:
            ready=True
            print("READY: Knockdown playable",file=sys.stderr,flush=True)
    pygame.quit()

if __name__=="__main__":
    main()
