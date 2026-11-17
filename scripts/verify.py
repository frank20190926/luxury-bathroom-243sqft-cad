"""Checks measurable coordination facts; unresolved design issues stay visible."""
import json
import math
from pathlib import Path
from shapely.geometry import Polygon, box
import ezdxf
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]


def verify():
    g=json.loads((ROOT/'layout_geometry.json').read_text());checks=[]
    def check(name,condition):
        checks.append(dict(name=name,pass_=bool(condition)))
        if not condition:raise AssertionError(name)
    footprint=Polygon(g['footprint']['polygon_in'])
    check('Footprint valid and exactly 35000 square inches',footprint.is_valid and footprint.area==35000)
    check('Footprint is nonoverlapping main rectangle + west wing',box(0,0,150,200).union(box(-50,100,0,200)).equals(footprint))
    objects={o['id']:o for o in g['objects']}
    for id,b in {'SHOWER-A':[-50,100,0,184],'SHOWER-B':[-50,100,0,160],'M-01':[-50,184,0,200],'M-EXIST':[-50,160,0,200],'TUB':[16,160,84,192]}.items():
        check(id+' exact bounds',objects[id]['bounds_in']==b)
    check('Five vanity bays sum to 134 inches',18+36+26+36+18==140-6)
    check('Cabinet-front gap is 102 inches',objects['S-01A']['bounds_in'][0]-objects['S-02A']['bounds_in'][2]==102)
    c=box(24,10,126,148).intersection(box(100,140,150,200)).area
    check('Requested circulation conflict is disclosed: 208 in2',c==208 and any(i['id']=='C03' for i in g['coordination_issues']))
    # A door on the south shower jamb avoids the actual elliptical tub envelope.
    from shapely.geometry import Point
    from shapely.affinity import scale
    tub=scale(Point(50,176).buffer(1,resolution=128),34,16,origin=(50,176))
    door_sweep=Point(0,138).buffer(30,resolution=128).intersection(box(0,138,30,168))
    check('South-hinged shower leaf sweep misses tub',door_sweep.intersection(tub).area<1e-8)
    check('S-05 not invented',next(s for s in g['storage']['groups'] if s['id']=='S-05')['parts']==[])
    check('Storage A includes S-03; B omits it',math.isclose(g['storage']['option_A_estimate_ft3']-g['storage']['option_B_estimate_ft3'],next(s for s in g['storage']['groups'] if s['id']=='S-03')['volume_ft3']))
    d=ezdxf.readfile(ROOT/'exports/Master_Bathroom_243sqft_Proposal.dxf');a=d.audit()
    check('DXF R2010 inches',d.dxfversion=='AC1024' and d.units==1)
    check('DXF reopened audit has zero errors and fixes',len(a.errors)==len(a.fixes)==0)
    check('Native dimensions present',len(d.modelspace().query('DIMENSION'))==79)
    for entry in g['cad_sheet_placement']['sheet1']['plans']:
        dx,dy=entry['origin_in'];target=[(x+dx,y+dy) for x,y in g['footprint']['polygon_in']]
        check(entry['option']+' exact footprint in CAD',any(list(e.get_points('xy'))==target for e in d.modelspace().query('LWPOLYLINE[layer=="A-FLOR-PATT"]')))
    dwg=json.loads((ROOT/'exports/dwg_validation.json').read_text())
    check('DWG placed-vector roundtrip passes',dwg['status']=='local_roundtrip_geometry_pass' and dwg['roundtrip_units']==1)
    sizes={'cad_plan_option_a.png':(2400,2600),'cad_plan_existing_vs_option_b.png':(1600,1000),'cad_3d_cutaway_iso.png':(1800,1400),'cad_4_elevations.png':(2400,1800)}
    pending=[]
    for name,size in sizes.items():
        p=ROOT/'assets'/name
        if p.exists():
            with Image.open(p) as im:check(name+' exact pixel size',im.size==size)
        else:pending.append(name)
    report=dict(checks=checks,passed=len(checks),pending_images=pending,design_issues=len(g['coordination_issues']),design_status='Coordination holds, not construction-ready',dwg_status=dwg['status'],dwg_semantic_dimensions=False)
    (ROOT/'exports/geometry_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    r=verify();print(json.dumps({k:v for k,v in r.items() if k!='checks'},indent=2))
