"""Native R2010 DXF with audit and labelled modelspace offsets."""
import json
import math
from pathlib import Path
import ezdxf
from ezdxf.enums import TextEntityAlignment
from drawing import Scene, plan, LAYERS, INK
from elevations import elevation, section

ROOT=Path(__file__).resolve().parents[1]


def emit(msp,scene,dx=0,dy=0):
    def p(a):return(a[0]+dx,a[1]+dy)
    for i in scene.items:
        attr={'layer':LAYERS[i['layer']]}
        if i.get('dash'): attr['linetype']='DASHED'
        k=i['kind']
        if k=='line': msp.add_line(p(i['a']),p(i['b']),dxfattribs=attr)
        elif k=='poly':
            pts=[p(a) for a in i['p']];msp.add_lwpolyline(pts,close=True,dxfattribs=attr)
            if i['fill'] and (i['hatch'] or i['layer'] in ['wall','new']):
                hatch=msp.add_hatch(dxfattribs={'layer':attr['layer']})
                if i['hatch']:hatch.set_pattern_fill('ANSI31',scale=16,angle=0)
                elif i['layer'] in ['wall','new']:hatch.set_solid_fill(color=8)
                else:hatch.set_solid_fill(color=254)
                hatch.paths.add_polyline_path(pts,is_closed=True)
        elif k=='ellipse':
            if i['w']>=i['h']:major=(i['w']/2,0,0);ratio=i['h']/i['w']
            else:major=(0,i['h']/2,0);ratio=i['w']/i['h']
            msp.add_ellipse(p(i['c']),major_axis=major,ratio=ratio,dxfattribs=attr)
        elif k=='arc':msp.add_arc(p(i['c']),i['r'],i['a'],i['b'],dxfattribs=attr)
        elif k=='text':
            lines=i['s'].split('\n'); rot=i['rotation']
            for n,t in enumerate(lines):
                t=t.replace('→','to').replace('²','2').replace('³','3')
                anchor=list(p(i['p'])); anchor[1]+=(len(lines)-1)*i['h']*.65-n*i['h']*1.3
                ent=msp.add_text(t,dxfattribs={**attr,'height':i['h'],'rotation':rot,'style':'MONO' if i['font']=='mono' else 'TITLE' if i['font'] in ['title','bold'] else 'BODY'})
                ent.set_placement(anchor,align=TextEntityAlignment.MIDDLE_CENTER if i['align']=='center' else TextEntityAlignment.MIDDLE_LEFT)
        elif k=='dim':
            a,b=p(i['a']),p(i['b']);horizontal=i['axis']=='x'
            base=(a[0],i['offset']+dy) if horizontal else (i['offset']+dx,a[1])
            dim=msp.add_linear_dim(base=base,p1=a,p2=b,angle=0 if horizontal else 90,
                dimstyle='BATH-ARCH',override={'dimtxt':i['h'],'dimpost':'<>"','dimtad':1},dxfattribs=attr)
            dim.render()
            if i['dual']:
                val=abs(b[0]-a[0]) if horizontal else abs(b[1]-a[1])
                mp=((a[0]+b[0])/2,base[1]-3.3) if horizontal else (base[0]+3.4,(a[1]+b[1])/2)
                ent=msp.add_text(f'{val*2.54:.1f} cm',dxfattribs={'layer':LAYERS['metric'],'height':i['h']*.8,'rotation':0 if horizontal else 90,'style':'MONO'})
                ent.set_placement(mp,align=TextEntityAlignment.MIDDLE_CENTER)


def build_cad(g):
    doc=ezdxf.new('R2010',setup=True);doc.units=1
    doc.header['$MEASUREMENT']=0; doc.header['$LUNITS']=2;doc.header['$LUPREC']=3
    for key,name in LAYERS.items():
        doc.layers.new(name,dxfattribs={'color':7,'lineweight':40 if key in ['wall','new'] else 18 if key in ['wood','fixture'] else 13})
    for name,font in [('BODY','IBMPlexSans-400.ttf'),('TITLE','SpaceGrotesk-600.ttf'),('MONO','JetBrainsMono-400.ttf')]:doc.styles.new(name,dxfattribs={'font':font})
    doc.dimstyles.new('BATH-ARCH',dxfattribs={'dimtxsty':'MONO','dimtxt':2.6,'dimasz':1.4,'dimexo':1,'dimexe':1.5,'dimgap':1,'dimdec':0,'dimclrd':7,'dimclre':7,'dimclrt':7,'dimtad':1})
    m=doc.modelspace()
    frame=Scene();frame.rect([0,0,250,895],lw=1)
    frame.line((0,20),(250,20));frame.text((8,10),'A-01  /  PLANS  /  INCHES  /  MODEL 1:1',3,align='left',font='bold')
    for k,title in [(0,'EXISTING / SKETCH INTERPRETATION'),(1,'OPTION A / TANKLESS CONVERSION'),(2,'OPTION B / RETAIN MECHANICAL')]:
        frame.text((125,287+k*300),title,4,font='title')
        frame.text((125,279+k*300),'NOMINAL COORDINATES; FIELD DIMENSIONS / CONSTRUCTION HOLDS APPLY',2.2)
    emit(m,frame)
    for entry in g['cad_sheet_placement']['sheet1']['plans']:
        emit(m,plan(g,entry['option']),*entry['origin_in'])
    f=Scene(); f.rect([300,0,700,895],lw=1);f.line((300,20),(700,20))
    f.text((310,10),'A-02  /  INTERIOR ELEVATIONS & MILLWORK  /  MODEL 1:1',3,align='left',font='bold')
    f.text((500,878),'INTERIOR ARCHITECTURE',6,font='title')
    f.text((500,866),'96" HEIGHT ASSUMED / PARTITIONS DIAGRAMMATIC / REVIEW COORDINATION SCHEDULE',2.7)
    emit(m,f)
    for side,xy in [('East',(330,720)),('West',(330,525)),('North',(320,330)),('South',(520,330))]:
        emit(m,elevation(g,side),*xy)
    emit(m,section(g,'S-01 / GROOMING'),330,145)
    emit(m,section(g,'S-02 / LINEN'),520,145)
    note=Scene()
    note.text((315,113),'COORDINATION REGISTER',3.5,align='left',font='title')
    for j,txt in enumerate([
        'C01 Tub / skylight centres offset (-10,+26); C02 ledge depth 8 in by coordinates.',
        'C03 102 in cabinet-front separation is not an unobstructed 102 x 138 in rectangle.',
        'C04 WC pocket run insufficient; C05 west window / wing / chase conflict.',
        'C06 S-04 / north window conflict; C07 S-05 and 142.4 ft3 storage target unverified.',
        'C08 Tankless / steam sizing, venting, drainage and service access require design.',
        'C09 Niche wall recess unverified; C10 S-01C / finite WC partition conflict.',
        'C11 Source WC width differs; C12 heights and wall thicknesses are assumptions.',
        'See layout_geometry.json for exact bounds, volume formulas and plumbing schedule.'
    ]):note.text((315,103-j*9),txt,2.7,align='left')
    emit(m,note)
    doc.set_modelspace_vport(height=960,center=(350,450))
    auditor=doc.audit()
    if auditor.errors or auditor.fixes:raise RuntimeError(f'DXF audit: {len(auditor.errors)} errors / {len(auditor.fixes)} fixes')
    path=ROOT/'exports/Master_Bathroom_243sqft_Proposal.dxf';doc.saveas(path)
    reopened=ezdxf.readfile(path); a=reopened.audit()
    from collections import Counter
    report=dict(dxf_version=reopened.dxfversion,units=reopened.units,audit_errors=len(a.errors),audit_fixes=len(a.fixes),entities=dict(Counter(e.dxftype() for e in reopened.modelspace())),layers=[l.dxf.name for l in reopened.layers],modelspace_plans='1:1 in inches; placement offsets in JSON; no geometry scaling',native_dimension_count=len(reopened.modelspace().query('DIMENSION')))
    (ROOT/'exports/cad_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    print(json.dumps(build_cad(json.loads((ROOT/'layout_geometry.json').read_text())),indent=2))
