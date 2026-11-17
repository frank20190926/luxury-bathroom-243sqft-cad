"""Orthogonal interior elevations and cabinet sections derived from JSON."""
from drawing import Scene, STONE, WOOD, INK, MUTED


def obj(g,id): return next(o for o in g['objects'] if o['id']==id)


def elevation(g,side):
    s=Scene(); H=g['assumptions']['ceiling_height_in']; length=200 if side in ['East','West'] else 150
    s.rect([0,0,length,H],layer='elev',fill='#fcfbf8',lw=.8)
    s.line((0,0),(length,0),'elev',1.3)
    s.line((0,H),(length,H),'elev',.8)
    s.dim((0,0),(length,0),-13,h=2.8)
    s.dim((length,0),(length,H),length+12,axis='y',h=2.5)
    s.text((length/2,H+10),side.upper()+' INTERIOR ELEVATION',3.8,font='title')
    def shelves(x0,x1,zs):
        for z in zs: s.line((x0+2,z),(x1-2,z),'wood',.45)
    def cabinet(b,label,zs):
        s.rect(b,layer='wood',fill=WOOD,lw=.7)
        x,y,X,Y=b
        s.rect([x+1.2,y+1.5,X-1.2,Y-1.5],layer='wood',fill=None,lw=.3)
        shelves(x,X,zs)
        s.text(((x+X)/2,Y+3.5),label,2.6,font='bold')
    if side=='East':
        s.rect([140,0,200,H],layer='elev',fill='#f1ede7',lw=.35)
        for id in ['S-01A','S-01B','S-01C']:
            o=obj(g,id); _,y,_,Y=o['bounds_in']; z,Z=o['z_in']
            cabinet([y,z,Y,Z],id,[12,28,44,60,76,90] if id!='S-01B' else [48,68,86])
        for id in ['V-01','V-02']:
            o=obj(g,id); _,y,_,Y=o['bounds_in']; z,Z=o['z_in']
            cabinet([y,z,Y,Z],'',[18,32]);s.line(((y+Y)/2-5,29),((y+Y)/2+5,29),'wood',1)
            s.line(((y+Y)/2-5,15),((y+Y)/2+5,15),'wood',1)
            s.rect([y,34.5,Y,36],layer='fixture',fill=STONE)
            s.rect([y+2,42,Y-2,90],layer='glass',fill='#e5e7df',lw=.6)
            s.line((y+4,44),(y+4,88),'elev',1,color='#9a805d')
            s.line((Y-4,44),(Y-4,88),'elev',1,color='#9a805d')
            s.line(((y+Y)/2,36),((y+Y)/2,42),'fixture',1)
        s.rect([64,0,82,20],layer='wood',fill='#d8ccbb',lw=.7)
        s.text((73,11),'STOOL',2.2)
        # Quad outlet within appliance tower, two duplex symbols.
        for x in [69,77]:
            s.rect([x-2,40,x+2,45],layer='elev',fill='white',lw=.5)
            for xx in [x-.7,x+.7]: s.line((xx,41.5),(xx,43.5),'elev',.5)
        s.text((73,56),'GFCI\n120 V',2.3)
        for x in [61,85]: s.line((x,38),(x,94),'wood',.45,MUTED,True)
        s.text((73,79),'POCKET\nFLIPPERS',2.2)
        s.line((140,0),(140,H),'new',1.4)
        s.rect([146,32,162,34],layer='fixture',fill=STONE)
        s.line((154,34),(154,40),'fixture',1)
        s.ellipse((177,14),28,12,fill='white')
        s.rect([190,0,200,48],layer='new',fill=STONE)
        s.rect([190,48,200,90],layer='wood',fill=WOOD,hatch='//')
        s.text((169,76),'WC ROOM\nINNER FACE',3)
        s.text((70,-25),'SOUTH  →  NORTH  |  134" JOINERY ON 140" WALL',2.7)
        for a,b in [(6,24),(24,60),(60,86),(86,122),(122,140),(140,200)]: s.dim((a,H),(b,H),H+19,h=2.3,dual=False)
    elif side=='West':
        # Unfolded elevation looking west: NORTH at left, SOUTH at right.
        s.rect([0,0,16,H],layer='new',fill='#d2ccc1',hatch='xx')
        s.text((8,50),'M-01',2.7,rotation=90)
        o=obj(g,'S-03'); b=o['bounds_in']; cabinet([200-b[3],0,200-b[1],84],'S-03',[18,36,54,72])
        s.rect([32,42,76,66],layer='fixture',fill='#d4c5b2',lw=.8)
        shelves(32,76,[54]);s.text((54,54),'6" NICHE',2.5)
        s.rect([82,0,100,18],layer='fixture',fill=STONE)
        for yy in [136,160]:
            x=200-yy;s.line((x,96),(x,90),'fixture',.6);s.line((x-6,90),(x+6,90),'fixture',1.5)
        s.ellipse((62,44),3,3,fill=None); s.ellipse((68,44),3,3,fill=None)
        s.line((32,0),(32,96),'glass',.6,MUTED,True);s.line((100,0),(100,96),'elev',1.1)
        cabinet([100,0,116,96],'S-02B',[18,36,60,84])
        s.rect([116,0,148,84],layer='door',fill='#f5f0e7',lw=.9)
        s.rect([116,84,148,96],layer='wood',fill=WOOD,lw=.5)
        s.text((132,44),'WIC\n32" CLEAR',3)
        cabinet([148,0,196,96],'S-02A',[6,36,54,72,90])
        s.line((166,6),(166,94),'wood',.6)
        s.text((157,57),'UTILITY',2.3,rotation=90)
        s.line((181,6),(181,36),'wood',.6)
        s.text((181,22),'DUAL\nHAMPERS',2.3)
        s.text((181,62),'LINEN',2.5)
        s.text((100,-25),'NORTH  →  SOUTH  |  UNFOLDED: X=-50 / X=0',2.7)
        for a,b in [(0,16),(16,100),(100,116),(116,148),(148,196)]: s.dim((a,H),(b,H),H+19,h=2.25,dual=False)
    elif side=='North':
        s.rect([0,28,100,30],layer='fixture',fill=STONE)
        s.ellipse((50,13),68,22,fill='#f1e9de',lw=1)
        s.line((16,18),(84,18),'fixture',.65)
        s.line((88,0),(88,34),'fixture',1.3);s.line((81,34),(88,34),'fixture',1.3)
        s.line((100,0),(100,H),'new',1.2)
        s.rect([110,42,140,90],layer='glass',fill='#e7ece9',lw=.6,dash=True)
        for z in [54,66,78]: s.line((110,z),(140,z),'glass',.4,MUTED,True)
        cabinet([102,48,148,90],'S-04',[62,76])
        s.rect([110,42,140,90],layer='hold',fill=None,lw=1,dash=True)
        s.text((125,70),'WINDOW\nCONFLICT\nC06',2.7,font='bold')
        s.rect([102,0,148,46],layer='new',fill=STONE,lw=.5)
        s.ellipse((125,15),18,14,fill='white')
        s.text((125,37),'CISTERN',2.5)
        s.line((25,H),(95,H),'sky',1.5,MUTED,True)
        s.text((60,84),'SKYLIGHT X 25..95"',2.6)
        s.text((50,45),'TUB 68" / 172.7 cm',2.8,font='mono')
        s.text((75,-25),'WEST  →  EAST  |  NORTH WALL',2.7)
        for a,b in [(0,100),(100,150)]:s.dim((a,H),(b,H),H+19,h=2.4)
    else:
        # Looking south, east corner at left.
        s.rect([45,0,105,84],layer='door',fill='#f3efe6',lw=.9)
        s.line((75,0),(75,84),'door',.8)
        for x in [45,75]:
            s.rect([x+3,8,x+27,78],layer='glass',fill='#e5e7df',lw=.5)
            for z in [30,54]:s.line((x+3,z),(x+27,z),'door',.5)
        s.ellipse((72,38),1.4,1.4,fill=INK);s.ellipse((78,38),1.4,1.4,fill=INK)
        s.rect([0,0,24,96],layer='wood',fill=WOOD,hatch='//',lw=.6)
        s.rect([126,0,150,96],layer='wood',fill=WOOD,hatch='//',lw=.6)
        s.text((12,50),'S-01A RETURN',2.7,rotation=90)
        s.text((138,50),'S-02A RETURN',2.7,rotation=90)
        s.text((75,90),'FRENCH ENTRY 60" / 152.4 cm',2.7)
        s.text((75,-25),'EAST  →  WEST  |  SOUTH WALL',2.7)
        for a,b in [(0,45),(45,105),(105,150)]: s.dim((a,H),(b,H),H+19,h=2.4)
    return s


def section(g,type):
    s=Scene(); H=g['assumptions']['ceiling_height_in']
    s.line((-2,0),(30,0),'elev',1.2)
    s.rect([24,0,26,H],layer='wall',fill='#71695c')
    s.dim((0,0),(24,0),-12,h=2.6)
    s.dim((24,0),(24,H),36,axis='y',h=2.6)
    s.text((12,H+10),type,3.4,font='title')
    if type=='S-01 / GROOMING':
        s.rect([0,34.5,24,36],layer='fixture',fill=STONE)
        s.rect([10,36,24,96],layer='wood',fill=WOOD)
        s.rect([11,38,23,94],layer='wood',fill='white',lw=.5)
        for z in [48,68,86]: s.rect([11,z,23,z+.75],layer='wood',fill=WOOD,lw=.3)
        s.rect([21.5,40,23,45],layer='elev',fill='white')
        s.line((23,42),(25,42),'elev',.4,MUTED,True)
        s.rect([4,0,19,20],layer='wood',fill=WOOD)
        s.leader((22,43),(43,45),(49,45),'GFCI / 120 V',2.5)
        s.leader((11,70),(43,74),(49,74),'14" TOWER DEPTH',2.5)
        s.leader((11,15),(43,17),(49,17),'PULL-OUT STOOL',2.5)
        s.dim((10,96),(24,96),105,h=2.4)
    else:
        s.rect([0,0,24,96],layer='wood',fill=WOOD)
        s.rect([1,6,23,94],layer='wood',fill='white',lw=.5)
        for z in [36,54,72,90]:s.rect([1,z,23,z+.75],layer='wood',fill=WOOD,lw=.4)
        s.rect([3,8,21,33],layer='wood',fill='#ddd2c2',lw=.6)
        for z in [12,18,24,30]: s.line((4,z),(20,z),'wood',.35)
        s.leader((13,22),(43,22),(49,22),'VENTILATED HAMPER',2.5)
        s.leader((12,63),(43,65),(49,65),'ADJUSTABLE SHELVES',2.5)
        s.leader((12,3),(43,4),(49,4),'6" SERVICE PLINTH',2.5)
    return s
