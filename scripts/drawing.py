"""Shared vector primitives: the same plan feeds matplotlib and native DXF."""
import math
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPolygon, Ellipse, Arc
from matplotlib.font_manager import FontProperties
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
INK='#302c28'; MUTED='#625b52'; STONE='#eee7dc'; WOOD='#baa286'; GLASS='#dee7e4'
FONTS={k:FontProperties(fname=str(ROOT/'assets/fonts'/v)) for k,v in {
    'title':'SpaceGrotesk-600.ttf','body':'IBMPlexSans-400.ttf','bold':'IBMPlexSans-600.ttf','mono':'JetBrainsMono-400.ttf'}.items()}
LAYERS={'wall':'A-WALL-EXIST','new':'A-WALL-NEW','door':'A-DOOR','glass':'A-GLAZ','fixture':'A-FIXT-PLMB','wood':'A-MILLWORK-STOR','floor':'A-FLOR-PATT','sky':'A-CLNG-SKYLIGHT','dim':'A-DIMS-IMP','metric':'A-DIMS-MET','text':'A-ANNO-TEXT','elev':'A-ELEV-LINE','hold':'A-COORD-HOLD'}


def imperial(n):
    return f'{n:g}"'


def metric(n):
    return f'{n*2.54:.1f} cm'


class Scene:
    def __init__(self): self.items=[]
    def line(self,a,b,layer='elev',lw=.65,color=INK,dash=False):
        self.items.append(dict(kind='line',a=a,b=b,layer=layer,lw=lw,color=color,dash=dash))
    def poly(self,p,layer='elev',fill=None,lw=.7,hatch=None,color=INK,dash=False):
        self.items.append(dict(kind='poly',p=p,layer=layer,fill=fill,lw=lw,hatch=hatch,color=color,dash=dash))
    def rect(self,b,**kw):
        x,y,X,Y=b; self.poly([(x,y),(X,y),(X,Y),(x,Y)],**kw)
    def text(self,p,s,h=3,layer='text',align='center',font='body',rotation=0,color=INK):
        self.items.append(dict(kind='text',p=p,s=s,h=h,layer=layer,align=align,font=font,rotation=rotation,color=color))
    def ellipse(self,c,w,h,layer='fixture',fill='white',lw=.8):
        self.items.append(dict(kind='ellipse',c=c,w=w,h=h,layer=layer,fill=fill,lw=lw,color=INK))
    def arc(self,c,r,a,b,layer='door',lw=.6):
        self.items.append(dict(kind='arc',c=c,r=r,a=a,b=b,layer=layer,lw=lw,color=INK))
    def dim(self,a,b,offset,axis='x',h=2.7,dual=True):
        self.items.append(dict(kind='dim',a=a,b=b,offset=offset,axis=axis,h=h,dual=dual,layer='dim'))
    def leader(self,p,elbow,end,label,h=2.5,align='left'):
        self.line(p,elbow,lw=.45); self.line(elbow,end,lw=.45)
        self.text((end[0],end[1]+2.3),label,h=h,align=align)


def plan(g,option='A',detail=True):
    s=Scene(); existing=option=='existing'; op='B' if existing else option
    s.poly(g['footprint']['polygon_in'],layer='floor',fill='#faf8f4',lw=.7)
    for bounds in [[-50,100,0,184 if op=='A' else 160],[0,148,100,200]]:
        s.rect(bounds,layer='floor',fill=STONE,lw=.2)
        x,y,X,Y=bounds
        for xx in np.arange(x+12,X,24): s.line((xx,y),(xx,Y),'floor',.25,'#b8ad9d')
        for yy in np.arange(y+12,Y,24): s.line((x,yy),(X,yy),'floor',.25,'#b8ad9d')
    for w in g['walls']:
        if w['z_in'][0]>0: continue
        s.rect(w['bounds_in'],layer='wall' if w['status']=='existing' else 'new',fill='#635e55' if w['status']=='existing' else '#aaa091',lw=1.0)
    # North window uses the same opening coordinates as JSON.
    for yy in [200.5,202,203.5]: s.line((110,yy),(140,yy),'glass',.6)
    s.line((110,200),(110,204),'wall'); s.line((140,200),(140,204),'wall')
    # User-specified west window: dashed because its relation to the wing conflicts.
    s.line((1.5,158),(1.5,190),'hold',.7,MUTED,True)
    s.line((3,158),(3,190),'hold',.5,MUTED,True)
    if existing:
        s.rect([-50,160,0,200],layer='wall',fill='#d9d6cf',hatch='xx')
        s.ellipse((-25,181),25,25,fill='#eeeae3')
        s.text((-25,162),'TANK / UTILITY',2.2)
        s.rect([126,6,150,140],layer='wood',fill='#e2dbd1',hatch='//')
        for yy in [43,101]: s.ellipse((138,yy),15,23)
        for i in range(3): s.rect([0,140+i*5,100-i*3,200],layer='fixture',fill=None,lw=.5)
        s.ellipse((50,177),71,36)
        s.text((50,144),'EXISTING STEPPED DECK',2.6)
        s.ellipse((125,177),18,28)
        s.text((-25,130),'SHOWER\n50" x 60"',3)
    else:
        for o in g['objects']:
            if o.get('option') and o['option']!=option: continue
            k=o['kind']; b=o.get('bounds_in')
            if k in ['zone','mirror','niche']: continue
            if k in ['cabinet','base']:
                s.rect(b,layer='wood',fill=WOOD,hatch='////' if k=='cabinet' else None,lw=.8)
                x,y,X,Y=b
                for yy in np.arange(y+8,Y,10): s.line((x,yy),(x+2,yy),'wood',.5)
            elif k=='stone':
                s.poly(o['polygon_in'],layer='floor',fill='#e0d2bd',lw=.7)
            elif k=='mechanical':
                s.rect(b,layer='new',fill='#d9d5cd',hatch='xx')
                s.text(((b[0]+b[2])/2,(b[1]+b[3])/2),('M-01' if option=='A' else 'TANK\nRETAIN'),3)
            elif k=='tub':
                s.ellipse((50,176),68,32,fill='#fdfbf7',lw=1.2)
                s.ellipse((50,176),60,24,fill='#e8e7df',lw=.5)
                s.ellipse((75,176),1.3,1.3,fill=INK,lw=.3)
            elif k=='toilet':
                s.ellipse((125,176),18,28)
                s.ellipse((125,174),12,18,fill='#f1ede7',lw=.4)
            elif k=='basin':
                x,y,X,Y=b; s.ellipse(((x+X)/2,(y+Y)/2),X-x,Y-y,fill='white',lw=.7)
                s.ellipse(((x+X)/2,(y+Y)/2),1,1,fill=INK,lw=.3)
            elif k=='stool': s.rect(b,layer='wood',fill=None,lw=.45)
        # Counter is below tall grooming tower; restore tower plan after counter.
        s.rect([136,60,150,86],layer='wood',fill=WOOD,hatch='////',lw=.8)
        for p in [(-27,136),(-27,160)] if option=='A' else [(-27,140)]:
            s.ellipse(p,10,10,fill=None,lw=.55); s.line((p[0]-7,p[1]),(p[0]+7,p[1]),'fixture',.3)
        s.rect([-56,124,-50,168 if option=='A' else 154],layer='hold',fill=None,lw=.65,dash=True)
        s.line((-47,121 if option=='A' else 123),(-3,121 if option=='A' else 123),'fixture',1.2)
        s.line((-49,137),(-47,137),'fixture',1.2)
        s.ellipse((88,173),2.5,2.5,fill=None); s.line((88,173),(83,173),'fixture',1)
        for i,(id,p) in enumerate([('S-01A',(138,15)),('S-01B',(143,73)),('S-01C',(138,131)),('S-02A',(12,28)),('S-02B',(10,92))]):
            s.text(p,id,2.7,rotation=90 if id!='S-01B' else 90,font='bold')
        if option=='A': s.text((-11,176),'S-03',2.5,rotation=90,font='bold')
        s.text((125,195),'S-04 / C06',2.3,font='bold')
        s.text((-25,109 if option=='A' else 114),'BENCH',2.5)
        s.text((50,176),'68" x 32"',3,font='mono')
        s.text((50,168),'172.7 x 81.3 cm',2.2)
        s.text((117,151),'WC',3,font='bold')
        s.text((64,92),'102" BETWEEN CABINET FRONTS',3,font='bold')
        s.text((64,86),'259.1 cm  /  door sweeps excluded',2.5)
        s.dim((24,94),(126,94),101,h=2.8)
        s.text((75,117),'CIRCULATION',3.6,font='title')
        s.text((50,151),'TUB ALCOVE',2.6,font='bold')
        s.text((-27,127),'50" x '+('84"' if option=='A' else '60"'),2.8,font='mono')
        s.text((-27,132),'SHOWER',2.7,font='bold')
    # Proposed shower and WIC pockets; existing door graphics are contextual only.
    top=168 if option=='A' else 158; bottom=top-30
    s.line((0,100),(0,bottom),'glass',1.1)
    s.line((1,100),(1,bottom),'glass',.4)
    s.line((0,bottom),(30,bottom),'door',.8)
    s.arc((0,bottom),30,0,90)
    s.line((0,bottom),(0,top),'glass',.4,MUTED,True)
    s.line((-1,52),(-1,84),'door',.7)
    s.line((-2,20),(-2,52),'door',.6,MUTED,True)
    s.line((-4,52),(0,52),'door'); s.line((-4,84),(0,84),'door')
    s.text((7,68),'WIC',3,font='bold')
    # Double leaves open 90 degrees into bathroom.
    s.line((45,0),(45,30),'door',.8); s.arc((45,0),30,0,90)
    s.line((105,0),(105,30),'door',.8); s.arc((105,0),30,90,180)
    s.text((75,7),'ENTRY',3,font='bold')
    # WC opening retained, unresolved pocket travel is explicit.
    s.line((108,139),(136,139),'hold',.75,MUTED,True)
    s.text((122,135),'28" / C04',2.4)
    s.rect([25,125,95,175],layer='sky',fill=None,lw=.75,dash=True,color=MUTED)
    s.text((61,127),'SKYLIGHT ABOVE 70" x 50"',2.4,color=MUTED)
    s.line((60,145),(60,155),'sky',.4,MUTED,True); s.line((55,150),(65,150),'sky',.4,MUTED,True)
    # Dimensions: chains on all four sides; dual units use independent layers.
    s.dim((0,0),(150,0),-23,h=2.8)
    for a,b in [(0,45),(45,105),(105,150)]: s.dim((a,0),(b,0),-10,h=2.35,dual=False)
    s.dim((-50,200),(0,200),214,h=2.7)
    s.dim((0,200),(100,200),214,h=2.7)
    s.dim((100,200),(150,200),214,h=2.7)
    s.dim((-50,200),(150,200),228,h=2.8)
    for a,b in [(0,100),(100,184 if option=='A' else 160),(184 if option=='A' else 160,200)]:
        s.dim((-50 if a>=100 else 0,a),(-50,b),-62,axis='y',h=2.35)
    s.dim((150,0),(150,200),174,axis='y',h=3)
    if not existing:
        for a,b in [(6,24),(24,60),(60,86),(86,122),(122,140),(140,200)]:
            s.dim((150,a),(150,b),162,axis='y',h=2.1,dual=False)
        s.text((166,70),'VANITY 134" / 340.4 cm',2.4,rotation=90)
    s.text((10,-31),'0',2.4,font='mono'); s.line((10,-35),(58,-35),'dim',1)
    for n in [0,12,24,36,48]: s.line((10+n,-34),(10+n,-36),'dim',.6)
    s.text((58,-31),'4 ft',2.4,font='mono')
    s.line((-40,44),(-40,66),'text',.8); s.poly([(-40,69),(-42,63),(-38,63)],fill=INK)
    s.text((-40,75),'N',4,font='bold')
    return s


def render_scene(ax,s):
    ax.set_aspect('equal'); ax.axis('off')
    # Convert inch-based annotation height to point size at the current viewport.
    scale=ax.get_position().width*ax.figure.get_figwidth()*72/(ax.get_xlim()[1]-ax.get_xlim()[0])
    def ln(a,b,lw=.5,color=INK,dash=False):
        ax.plot([a[0],b[0]],[a[1],b[1]],lw=lw,color=color,ls=(0,(5,3)) if dash else '-',solid_capstyle='butt')
    def tx(p,t,h=3,rotation=0,align='center',font='body',color=INK):
        ax.text(*p,t,fontproperties=FONTS[font],fontsize=h*scale,ha=align,va='center',rotation=rotation,color=color,linespacing=1.35)
    for i in s.items:
        k=i['kind']
        if k=='line': ln(i['a'],i['b'],i['lw'],i['color'],i['dash'])
        elif k=='poly':
            ax.add_patch(MPolygon(i['p'],closed=True,facecolor=i['fill'] or 'none',edgecolor=i['color'],lw=i['lw'],hatch=i['hatch'],linestyle=(0,(5,3)) if i['dash'] else '-'))
        elif k=='text': tx(i['p'],i['s'],i['h'],i['rotation'],i['align'],i['font'],i['color'])
        elif k=='ellipse': ax.add_patch(Ellipse(i['c'],i['w'],i['h'],facecolor=i['fill'] or 'none',edgecolor=i['color'],lw=i['lw']))
        elif k=='arc': ax.add_patch(Arc(i['c'],2*i['r'],2*i['r'],theta1=i['a'],theta2=i['b'],lw=i['lw'],color=i['color']))
        elif k=='dim':
            a,b=i['a'],i['b']; o=i['offset']; h=i['h']; horizontal=i['axis']=='x'
            if horizontal:
                p=(a[0],o); q=(b[0],o); n=b[0]-a[0]; tp=((a[0]+b[0])/2,o+2.7); mp=(tp[0],o-3.3)
            else:
                p=(o,a[1]); q=(o,b[1]); n=b[1]-a[1]; tp=(o-3,(a[1]+b[1])/2); mp=(o+3.4,tp[1])
            ln(a,p,.3,MUTED);ln(b,q,.3,MUTED);ln(p,q,.4,MUTED)
            for r in [p,q]: ln((r[0]-1,r[1]-1),(r[0]+1,r[1]+1),.7)
            tx(tp,imperial(n),h,0 if horizontal else 90,font='mono')
            if i['dual']: tx(mp,metric(n),h*.8,0 if horizontal else 90,font='mono',color=MUTED)


def page(w,h,number,title,subtitle):
    fig=plt.figure(figsize=(w/200,h/200),dpi=200,facecolor='white')
    border=plt.Rectangle((.018,.018),.964,.964,fill=False,lw=.75,ec=INK,transform=fig.transFigure); fig.add_artist(border)
    fig.text(.045,.949,title,fontproperties=FONTS['title'],fontsize=25,color=INK)
    fig.text(.046,.927,subtitle,fontproperties=FONTS['body'],fontsize=9,color=MUTED)
    fig.add_artist(plt.Line2D([.018,.982],[.061,.061],transform=fig.transFigure,lw=.6,color=INK))
    fig.text(.038,.036,'LUXURY BATHROOM  /  2798513',fontproperties=FONTS['bold'],fontsize=8,color=INK)
    fig.text(.50,.036,'CONCEPT COORDINATION  ·  DIMENSIONS GOVERN',fontproperties=FONTS['body'],fontsize=7,color=INK)
    fig.text(.945,.034,number,fontproperties=FONTS['title'],fontsize=17,ha='right',color=INK)
    return fig


def save(fig,name):
    p=ROOT/'assets'/name; fig.savefig(p,dpi=200,facecolor='white'); plt.close(fig)
    with Image.open(p) as im:
        im.thumbnail((1200,1200)); im.convert('RGB').save(ROOT/'review'/(p.stem+'_1200.jpg'),quality=90)
    return p


def render_primary(g):
    fig=page(2400,2600,'A-01','WET-ZONE SANCTUARY','OPTION A  /  150" x 200" MAIN ROOM + 50" x 100" WEST WING  /  INCHES + CENTIMETRES')
    ax=fig.add_axes([.067,.203,.866,.696]); ax.set_xlim(-80,190); ax.set_ylim(-40,239)
    render_scene(ax,plan(g,'A'))
    fig.text(.065,.166,'243.06 ft²',fontproperties=FONTS['title'],fontsize=23,color=INK)
    fig.text(.065,.145,'22.5806 m²  /  nominal coordinate footprint',fontproperties=FONTS['body'],fontsize=9,color=MUTED)
    fig.text(.39,.168,'01  UTILITY CONVERSION',fontproperties=FONTS['bold'],fontsize=9,color=INK)
    fig.text(.39,.148,'50" x 16" chase; tankless sizing / service access pending.\n50" x 84" shower zone; 18"-deep bench at south.',fontproperties=FONTS['body'],fontsize=8,color=INK,linespacing=1.5)
    fig.text(.70,.168,'02  JOINERY / MATERIALS',fontproperties=FONTS['bold'],fontsize=9,color=INK)
    fig.text(.70,.148,'134" five-bay vanity; walnut storage wall.\nHoned travertine / low-iron glass / bronze.',fontproperties=FONTS['body'],fontsize=8,color=INK,linespacing=1.5)
    fig.text(.065,.113,'COORDINATION HOLDS',fontproperties=FONTS['bold'],fontsize=8,color=INK)
    fig.text(.065,.091,'C01  Tub is offset from skylight centre.   C02  North ledge is 8" by coordinates.   C04  WC pocket travel unresolved.\nC05  West window overlaps wing.   C06  WC window / S-04 conflict.   Refer to README and geometry issue schedule.',fontproperties=FONTS['body'],fontsize=8,color=INK,linespacing=1.5)
    return save(fig,'cad_plan_option_a.png')


if __name__=='__main__':
    import json
    g=json.loads((ROOT/'layout_geometry.json').read_text())
    print(render_primary(g))
