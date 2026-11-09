"""Additional presentation sheets; release after primary direction approval."""
import math
import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.patches import Polygon as PatchPolygon
from shapely.geometry import Polygon
from drawing import page, save, plan, render_scene, FONTS, INK, MUTED, WOOD, STONE
from elevations import elevation, section


def comparison(g):
    fig=page(1600,1000,'A-02','EXISTING / OPTION B','RETAINED MECHANICAL FOOTPRINT  /  SAME NOMINAL ROOM BOUNDARY')
    for i,op in enumerate(['existing','B']):
        ax=fig.add_axes([.03+i*.49,.225,.455,.66]);ax.set_xlim(-82,187);ax.set_ylim(-40,239)
        render_scene(ax,plan(g,op,detail=False))
        fig.text(.065+i*.49,.185,'EXISTING INTERPRETATION' if i==0 else 'OPTION B / UTILITY UNCHANGED',fontproperties=FONTS['bold'],fontsize=9,color=INK)
        fig.text(.065+i*.49,.144,'Sketch dimensions + video features.\nFixture geometry is indicative, not a measured survey.' if i==0 else '50" x 40" tank closet / 50" x 60" shower.\nS-01, S-02 and S-04 retained; S-03 omitted.',fontproperties=FONTS['body'],fontsize=7,color=INK,linespacing=1.4)
    fig.text(.065,.085,'Both proposals retain the supplied coordinate envelope. Door / window / partition coordination holds remain applicable.',fontproperties=FONTS['body'],fontsize=7,color=INK)
    return save(fig,'cad_plan_existing_vs_option_b.png')


def elevations_sheet(g):
    fig=page(2400,1800,'A-03','INTERIOR ELEVATIONS / JOINERY','DIMENSIONS IN INCHES + CENTIMETRES  /  96" CEILING IS A MODELLING ASSUMPTION')
    placements=[('East',[.045,.575,.44,.30]),('West',[.53,.575,.44,.30]),('North',[.045,.255,.31,.28]),('South',[.365,.255,.31,.28])]
    for side,pos in placements:
        length=200 if side in ['East','West'] else 150
        ax=fig.add_axes(pos);ax.set_xlim(-6,length+23);ax.set_ylim(-30,122)
        render_scene(ax,elevation(g,side))
    for typ,pos in [('S-01 / GROOMING',[.70,.27,.12,.28]),('S-02 / LINEN',[.845,.27,.12,.28])]:
        ax=fig.add_axes(pos);ax.set_xlim(-4,104);ax.set_ylim(-22,118)
        render_scene(ax,section(g,typ))
    fig.text(.055,.194,'STORAGE IS SHOWN AS INTERNAL COMPARTMENTS',fontproperties=FONTS['bold'],fontsize=10,color=INK)
    a=g['storage']['option_A_estimate_ft3'];b=g['storage']['option_B_estimate_ft3']
    fig.text(.055,.16,f'Option A: {a:.2f} ft³ / {a*28.316846592:,.0f} L.  Option B: {b:.2f} ft³ / {b*28.316846592:,.0f} L.\nAssumed internal envelopes before shelves, runners and equipment; S-05 is undefined. The 142.4 ft³ brief target is unverified.',fontproperties=FONTS['body'],fontsize=9,color=INK,linespacing=1.5)
    fig.text(.055,.105,'C04  WC pocket travel needs redesign.   C06  Cabinet / WC window overlap.   C10  North vanity tower / WC partition termination.\nWest elevation is unfolded across the 50" room offset. Wall build-ups, window heights and service details require measured coordination.',fontproperties=FONTS['body'],fontsize=8,color=INK,linespacing=1.5)
    return save(fig,'cad_4_elevations.png')


def cutaway(g):
    # Orthographic projection, with every object extruded from JSON plan bounds.
    elev=math.radians(32); cs=math.cos(elev); sn=math.sin(elev); q=math.sqrt(.5)
    def project(p):x,y,z=p;return ((x-y)*q,(x+y)*q*sn+z*cs)
    def depth(p):x,y,z=p;return (x+y)*q*cs-z*sn
    sun=np.array([-math.cos(math.radians(35))*q,-math.cos(math.radians(35))*q,math.sin(math.radians(35))])
    faces=[]; lines=[]
    def face(vertices,color,alpha=1,lw=.3,shade=True):
        p=np.array(vertices,dtype=float);n=np.cross(p[1]-p[0],p[2]-p[0]);n=n/max(np.linalg.norm(n),1e-9)
        brightness=.72+.28*max(0,np.dot(n,sun)) if shade else 1
        rgb=np.clip(np.array(to_rgb(color))*brightness,0,1)
        faces.append((sum(depth(v) for v in vertices)/len(vertices),vertices,rgb,alpha,lw))
    def prism(poly,z0,z1,color,alpha=1):
        # CCW vertices yield outward side normals.
        for a,b in zip(poly,poly[1:]+poly[:1]):
            face([[*a,z0],[*b,z0],[*b,z1],[*a,z1]],color,alpha)
        face([[*p,z1] for p in poly],color,alpha)
    def box(b,z0,z1,color,alpha=1):
        x,y,X,Y=b;prism([[x,y],[X,y],[X,Y],[x,Y]],z0,z1,color,alpha)
    def ellipse(cx,cy,rx,ry,z,n=56):
        return [[cx+rx*math.cos(t),cy+ry*math.sin(t),z] for t in np.linspace(0,2*math.pi,n,endpoint=False)]
    fig=page(1800,1400,'A-04','COORDINATE CUTAWAY','OPTION A  /  ORTHOGRAPHIC MODEL FROM layout_geometry.json  /  SOUTH-WEST LIGHT AT 35°')
    ax=fig.add_axes([.045,.17,.91,.71]);ax.set_aspect('equal');ax.set_xlim(-208,142);ax.set_ylim(-20,241);ax.axis('off')
    floor=g['footprint']['polygon_in'];prism(floor,-3,0,'#e9dfcf')
    # Floor joints and actual height-projected shadows share the same sun vector.
    floorpoly=Polygon(floor)
    shadow_polys=[]
    for o in g['objects']:
        if o.get('option')=='B' or o['kind'] not in ['cabinet','mechanical']:continue
        b=o['bounds_in'];h=o['z_in'][1];shift=h/math.tan(math.radians(35))*q
        p=Polygon(o['polygon_in']);from shapely import affinity
        hull=p.union(affinity.translate(p,shift,shift)).convex_hull.intersection(floorpoly)
        if not hull.is_empty:shadow_polys.append(hull)
    # Floors first; shadows get rendered before freestanding objects.
    for _,v,c,al,lw in sorted(faces,key=lambda x:-x[0]):ax.add_patch(PatchPolygon([project(p) for p in v],fc=c,ec='#857b6e',lw=lw,alpha=al))
    faces.clear()
    for p in shadow_polys:
        polys=[p] if p.geom_type=='Polygon' else list(p.geoms)
        for pp in polys:ax.add_patch(PatchPolygon([project([x,y,.01]) for x,y in pp.exterior.coords],fc='#766956',ec='none',alpha=.065))
    for b in [[-50,100,0,184],[0,148,100,200]]:
        x,y,X,Y=b
        for xx in np.arange(x+12,X,24):lines.append(([[xx,y,.1],[xx,Y,.1]],'#c2b6a5',.4,False))
        for yy in np.arange(y+12,Y,24):lines.append(([[x,yy,.1],[X,yy,.1]],'#c2b6a5',.4,False))
    for pts,c,lw,dash in lines:
        pp=np.array([project(p) for p in pts]);ax.plot(pp[:,0],pp[:,1],color=c,lw=lw)
    lines.clear()
    for w in g['walls']:
        z0,z1=w['z_in'];z1=min(z1,12) if w.get('cutaway') else min(z1,52) if w['id'].startswith('PART-WC') else z1
        if z1>z0:box(w['bounds_in'],z0,z1,'#e7ddcb')
    for o in g['objects']:
        if o.get('option')=='B':continue
        kind=o['kind'];b=o.get('bounds_in');z0,z1=o['z_in']
        if kind=='cabinet' or kind=='base':
            box(b,z0,z1,'#b39876')
            x,y,X,Y=b
            front=X+.05 if o['id'].startswith('S-02') or o['id']=='S-03' else x-.05
            for z in ([18,32] if kind=='base' else [6,36,66,90]):
                if z0<z<z1: lines.append(([[front,y+1,z],[front,Y-1,z]],'#66523d',.45,False))
            for yy in np.arange(y+2,Y-1,2.5):
                lines.append(([[front,yy,z0+2],[front,yy,z1-2]],'#a48968',.18,False))
        elif kind in ['stone','stool']:
            prism(o['polygon_in'],z0,z1,'#e6d6bf' if kind=='stone' else '#a58b6d')
        elif kind=='mechanical':box(b,z0,z1,'#bcb3a2')
        elif kind=='tub':
            x,y,X,Y=b;cx=(x+X)/2;cy=(y+Y)/2
            lower=ellipse(cx,cy,(X-x)*.43,(Y-y)*.40,z0+2)
            upper=ellipse(cx,cy,(X-x)/2,(Y-y)/2,z1)
            inner=ellipse(cx,cy,(X-x)/2-3,(Y-y)/2-3,z1-.7)
            bottom=ellipse(cx,cy,(X-x)*.34,(Y-y)*.28,6)
            for j in range(len(upper)):
                n=(j+1)%len(upper)
                face([lower[j],lower[n],upper[n],upper[j]],'#f1e5d1')
                face([upper[j],upper[n],inner[n],inner[j]],'#fbf5e7')
                face([inner[j],inner[n],bottom[n],bottom[j]],'#c5b9a4')
            face(bottom,'#e8dec9',shade=False)
        elif kind=='basin':
            x,y,X,Y=b;face(ellipse((x+X)/2,(y+Y)/2,(X-x)/2,(Y-y)/2,z1+.2),'#f8f5ee',shade=False)
        elif kind=='toilet':
            x,y,X,Y=b;prism([[x+2,y+2],[X-2,y+2],[X-2,Y-2],[x+2,Y-2]],z0,z1-3,'#f3eee4')
            face(ellipse((x+X)/2,(y+Y)/2,(X-x)/2,(Y-y)/2,z1),'#f9f5ed',shade=False)
        elif kind=='mirror':
            x,y,X,Y=b;face([[x-.1,y,z0],[x-.1,Y,z0],[x-.1,Y,z1],[x-.1,y,z1]],'#dbe1d8',shade=False)
    # Glass is partially transparent and exactly on the JSON partition line.
    for seg in g['glass']['A']:
        a,b=seg['p1'],seg['p2'];z0,z1=seg['z_in']
        if seg.get('type')=='pivot door':b=[a[0]+30,a[1]]
        face([[*a,z0],[*b,z0],[*b,z1],[*a,z1]],'#bad0cb',alpha=.18,shade=False,lw=.5)
        lines.append(([[*a,z1],[*b,z1]],'#786a51',.8,False))
    for _,v,c,al,lw in sorted(faces,key=lambda x:-x[0]):ax.add_patch(PatchPolygon([project(p) for p in v],fc=c,ec='#746856',lw=lw,alpha=al))
    for pts,c,lw,dash in lines:
        pp=np.array([project(p) for p in pts]);ax.plot(pp[:,0],pp[:,1],color=c,lw=lw,ls='--' if dash else '-')
    sky=next(z for z in g['zones'] if z['id']=='SKY');x,y,X,Y=sky['bounds_in'];z=sky['z_in'][0]
    pp=np.array([project(p) for p in [[x,y,z],[X,y,z],[X,Y,z],[x,Y,z],[x,y,z]]]);ax.plot(pp[:,0],pp[:,1],ls=(0,(5,3)),lw=.7,color='#696253')
    for x,y,z in g['lighting']['rain_heads_in']:
        p=np.array([project(p) for p in ellipse(x,y,5,5,z)]);ax.add_patch(PatchPolygon(p,fc='#b5a07e',ec='#695d49',lw=.3))
    fx,fy,fz=g['lighting']['tub_filler_in'];pp=np.array([project(p) for p in [[fx,fy,0],[fx,fy,fz],[fx-6,fy,fz]]]);ax.plot(pp[:,0],pp[:,1],color='#9d8051',lw=1.2)
    def callout(anchor,end,txt,align='left'):
        a=project(anchor);el=(end[0]+(8 if align=='left' else -8),end[1]);ax.plot([a[0],el[0],end[0]],[a[1],el[1],end[1]],lw=.45,color=INK)
        ax.text(end[0],end[1]+3,txt,fontproperties=FONTS['body'],fontsize=6.5,ha=align,va='bottom',color=INK,linespacing=1.3)
    callout([-26,191,96],[-192,204],'M-01  /  TANKLESS CHASE\n50" x 16"; engineering dependency')
    callout([45,166,24],[-190,145],'STONE TUB  /  68" x 32"\nOffset from existing skylight centre')
    callout([0,28,96],[-186,66],'S-02  /  LINEN + HAMPERS\n48" vault + 16" robe column')
    callout([136,73,96],[128,190],'S-01  /  FIVE-BAY VANITY\n134" joinery on 140" wall','right')
    callout([126,170,18],[128,130],'PRIVATE WC  /  50" x 60"\nPartition cut at 52" for visibility','right')
    callout([-24,139,0],[-188,24],'SHOWER  /  50" x 84"\n30" pivot door; 18" stone bench')
    fig.text(.055,.12,'MODEL BASIS',fontproperties=FONTS['bold'],fontsize=9,color=INK)
    fig.text(.055,.087,'1:1 coordinate extrusion. South / west walls cut to 12"; WC partitions cut to 52". Cabinet heights remain as specified.\nCeiling height 96" assumed. Dashed frame = existing skylight. Window / cabinet conflicts are recorded, not concealed.',fontproperties=FONTS['body'],fontsize=8,color=INK,linespacing=1.4)
    return save(fig,'cad_3d_cutaway_iso.png')
