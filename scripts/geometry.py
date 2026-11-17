"""Coordinate authority for the competition concept. All lengths are inches."""
import json
from pathlib import Path
from shapely.geometry import box, Polygon

ROOT = Path(__file__).resolve().parents[1]


def rect(id, bounds, name, z=(0, 0), **extra):
    x0, y0, x1, y1 = bounds
    return dict(id=id, name=name, bounds_in=bounds,
                bounds_cm=[round(n * 2.54, 4) for n in bounds],
                polygon_in=[[x0,y0],[x1,y0],[x1,y1],[x0,y1]],
                dimensions_in=[x1-x0,y1-y0,z[1]-z[0]],
                dimensions_cm=[round(n*2.54,4) for n in [x1-x0,y1-y0,z[1]-z[0]]],
                z_in=list(z), **extra)


def make_geometry():
    footprint = [[0,0],[150,0],[150,200],[-50,200],[-50,100],[0,100]]
    zones = [rect('MAIN',[0,0,150,200],'Main rectangle'),
             rect('WING',[-50,100,0,200],'West extension'),
             rect('WC',[100,140,150,200],'Private water closet'),
             rect('TUB-ZONE',[0,148,100,200],'Tub alcove'),
             rect('SKY',[25,125,95,175],'Existing skylight projection',(96,96),status='user-coordinate; height assumed'),
             rect('CIRC-REQUEST',[24,10,126,148],'Requested circulation rectangle')]
    objects = [
        rect('S-01A',[126,6,150,24],'Linen / tall cosmetics',(0,96),kind='cabinet',group='S-01'),
        rect('V-01',[126,24,150,60],'South basin drawer base',(6,34.5),kind='base',group='S-01'),
        rect('V-02',[126,86,150,122],'North basin drawer base',(6,34.5),kind='base',group='S-01'),
        rect('COUNTER',[126,24,150,122],'Honed stone counter',(34.5,36),kind='stone'),
        rect('S-01B',[136,60,150,86],'Powered grooming tower',(36,96),kind='cabinet',group='S-01'),
        rect('S-01C',[126,122,150,140],'Daily towel / skincare',(0,96),kind='cabinet',group='S-01'),
        rect('STOOL',[130,64,145,82],'Pull-out seated stool',(0,20),kind='stool'),
        rect('S-02A',[0,4,24,52],'Linen / hampers / utility',(0,96),kind='cabinet',group='S-02'),
        rect('S-02B',[0,84,20,100],'Robe / spa drawers',(0,96),kind='cabinet',group='S-02'),
        rect('S-03',[-22,168,0,184],'Heated towel / robe cabinet',(0,84),kind='cabinet',group='S-03',option='A'),
        rect('S-04',[102,190,148,200],'Over-cistern storage',(48,90),kind='cabinet',group='S-04'),
        rect('TUB',[16,160,84,192],'Freestanding soaking tub',(0,24),kind='tub'),
        rect('LEDGE',[0,192,100,200],'North stone display ledge',(28,30),kind='stone'),
        rect('WC-PAN',[116,162,134,190],'Wall-hung WC indicative envelope',(8,18),kind='toilet',stack_in=[125,182]),
        rect('RINSE',[140,146,150,162],'Hand rinse basin',(32,34),kind='basin'),
        rect('BASIN-1',[131,31,146,53],'South undermount basin',(33,36),kind='basin'),
        rect('BASIN-2',[131,93,146,115],'North undermount basin',(33,36),kind='basin'),
        rect('MIRROR-1',[149,26,150,58],'Recessed south mirror',(42,90),kind='mirror'),
        rect('MIRROR-2',[149,88,150,120],'Recessed north mirror',(42,90),kind='mirror'),
        rect('BENCH-A',[-50,100,0,118],'Heated stone bench',(0,18),kind='stone',option='A'),
        rect('M-01',[-50,184,0,200],'Tankless utility chase',(0,96),kind='mechanical',option='A'),
        rect('SHOWER-A',[-50,100,0,184],'Rain / steam shower zone',kind='zone',option='A'),
        rect('M-EXIST',[-50,160,0,200],'Retained tank mechanical closet',(0,96),kind='mechanical',option='B'),
        rect('SHOWER-B',[-50,100,0,160],'Retained shower zone',kind='zone',option='B'),
        rect('NICHE-A',[-56,124,-50,168],'Recessed shower niche',(42,66),kind='niche',option='A',status='recess beyond nominal footprint; wall build-up unverified'),
    ]
    objects.append(dict(id='BENCH-B',name='Corner stone bench',polygon_in=[[-50,100],[-32,100],[-50,118]],z_in=[0,18],kind='stone',option='B'))
    openings = [
        dict(id='D-01',name='French entry',axis='X',fixed=0,interval=[45,105],width_in=60,height_in=84,type='double swing',verified='position per user; height assumed'),
        dict(id='D-02',name='WIC portal',axis='Y',fixed=0,interval=[52,84],width_in=32,height_in=84,type='pocket proposed',pocket_interval=[20,52],verified='pocket wall structure unverified'),
        dict(id='D-03',name='WC entrance',axis='X',fixed=140,interval=[108,136],width_in=28,height_in=84,type='pocket requested; unresolved',verified='only 14 in east / 8 in west pocket run'),
        dict(id='D-04A',name='Shower pivot',axis='Y',fixed=0,interval=[138,168],width_in=30,height_in=96,type='pivot',option='A'),
        dict(id='D-04B',name='Shower pivot',axis='Y',fixed=0,interval=[128,158],width_in=30,height_in=96,type='pivot',option='B'),
        dict(id='W-01',name='West wet-zone opening',axis='Y',fixed=0,interval=[158,190],width_in=32,sill_in=42,head_in=90,type='window',verified='user coordinates; overlaps wing and proposed S-03 / M-01'),
        dict(id='W-02',name='WC north window',axis='X',fixed=200,interval=[110,140],width_in=30,sill_in=42,head_in=90,type='window',verified='sill/head assumed; overlaps S-04'),
    ]
    walls = [
        dict(id='WALL-S1',bounds_in=[0,-4,45,0],z_in=[0,96],status='existing',cutaway=True),
        dict(id='WALL-S2',bounds_in=[105,-4,154,0],z_in=[0,96],status='existing',cutaway=True),
        dict(id='WALL-E',bounds_in=[150,0,154,204],z_in=[0,96],status='existing'),
        dict(id='WALL-NW',bounds_in=[-54,200,110,204],z_in=[0,96],status='existing'),
        dict(id='WALL-NE',bounds_in=[140,200,150,204],z_in=[0,96],status='existing'),
        dict(id='WALL-N-SILL',bounds_in=[110,200,140,204],z_in=[0,42],status='existing'),
        dict(id='WALL-N-HEAD',bounds_in=[110,200,140,204],z_in=[90,96],status='existing'),
        dict(id='WALL-WING',bounds_in=[-54,96,-50,200],z_in=[0,96],status='existing',cutaway=True),
        dict(id='WALL-WING-S',bounds_in=[-50,96,0,100],z_in=[0,96],status='existing',cutaway=True),
        dict(id='WALL-W1',bounds_in=[-4,0,0,52],z_in=[0,96],status='existing',cutaway=True),
        dict(id='WALL-W2',bounds_in=[-4,84,0,100],z_in=[0,96],status='existing',cutaway=True),
        dict(id='PART-WC-W',bounds_in=[98,140,100,200],z_in=[0,96],status='new',note='2 in diagram thickness only; final partition outside WC'),
        dict(id='PART-WC-S1',bounds_in=[100,138,108,140],z_in=[0,96],status='new'),
        dict(id='PART-WC-S2',bounds_in=[136,138,150,140],z_in=[0,96],status='new',note='intersects S-01C; coordination hold'),
        dict(id='PART-WC-HEAD',bounds_in=[108,138,136,140],z_in=[84,96],status='new'),
    ]
    # Internal envelopes are explicit proposals, not manufacturer-rated capacities.
    storage = [
        dict(id='S-01',parts=[
            dict(name='S-01A internal tall space',size_in=[16,22,88],count=1),
            dict(name='S-01C internal tall space',size_in=[16,22,88],count=1),
            dict(name='Four U-drawer envelopes',size_in=[32,20,9],count=4,void_in=[12,10,9]),
            dict(name='S-01B grooming space',size_in=[24,12,56],count=1)]),
        dict(id='S-02',parts=[
            dict(name='S-02A utility locker',size_in=[16,22,88],count=1),
            dict(name='S-02A dual hamper compartment',size_in=[28,22,30],count=1),
            dict(name='S-02A upper linen compartment',size_in=[28,22,54],count=1),
            dict(name='S-02B robe internal space',size_in=[14,18,88],count=1)]),
        dict(id='S-03',parts=[dict(name='Heated towel internal space',size_in=[20,14,76],count=1)],option='A'),
        dict(id='S-04',parts=[dict(name='Over-cistern internal space',size_in=[44,8,38],count=1)],status='conflicts with north window'),
        dict(id='S-05',parts=[],status='undefined in supplied layout; no geometry or capacity invented'),
    ]
    for group in storage:
        total = 0
        for part in group['parts']:
            from math import prod
            part['size_cm']=[round(n*2.54,4) for n in part['size_in']]
            if 'void_in' in part:part['void_cm']=[round(n*2.54,4) for n in part['void_in']]
            v=(prod(part['size_in'])-prod(part.get('void_in',[0])))*part['count']
            part['volume_in3']=v; part['volume_ft3']=v/1728; part['volume_l']=v*0.016387064
            total+=v
        group['volume_in3']=total; group['volume_ft3']=total/1728; group['volume_l']=total*0.016387064
    issues = [
        dict(id='C01',subject='Skylight / tub',fact='Tub centre (50,176); skylight centre (60,150). Offset (-10,+26) inches.',resolution='Coordinates retained. Tub is partly beneath skylight, not centred.'),
        dict(id='C02',subject='North ledge',fact='Y 192..200 gives 8 in depth; narrative says 10 in. Tub touches ledge at Y192.',resolution='8 in drawn. Final cleaning / installation gap to be coordinated.'),
        dict(id='C03',subject='Circulation',fact='Requested 102 x 138 in rectangle intersects WC zone by 208 in2 and entry door sweeps.',resolution='102 in is cabinet-front separation, not a universally clear rectangle or code finding.'),
        dict(id='C04',subject='WC pocket door',fact='28 in opening has only 14 in east / 8 in west return; neither fits a conventional 28 in pocket.',resolution='Opening retained; pocket shown as unresolved design intent, no false pocket enclosure.'),
        dict(id='C05',subject='Wet-zone west window',fact='X=0,Y158..190 lies between main room and west wing; overlaps S-03, glass and chase.',resolution='Reference window drawn dashed. Exterior condition / proposed treatment must be resolved.'),
        dict(id='C06',subject='North WC window / S-04',fact='Window X110..140 overlaps cabinet X102..148; assumed vertical ranges also overlap.',resolution='Cabinet and window shown; no unobstructed daylight claim.'),
        dict(id='C07',subject='Storage target',fact='S-05 undefined; 142.4 ft3 cannot be established from supplied cabinet dimensions alone.',resolution='Report explicit internal-envelope estimate. Drawer runners, shelf thickness and equipment reduce usable capacity.'),
        dict(id='C08',subject='Tankless / steam systems',fact='Fuel, flow/temperature demand, vent, condensate, electrical service and steam generator not specified.',resolution='Option A conditional. Service access from east at Y184..200; equipment fit and steam generator remain unverified.'),
        dict(id='C09',subject='Shower niche',fact='6 in recess projects west beyond X=-50 boundary; wall thickness unknown.',resolution='Recess is design intent; no structural/exterior wall alteration approval inferred.'),
        dict(id='C10',subject='Partition / tall vanity',fact='Full S-01C reaches Y140; a finite WC south partition intrudes into cabinet at its north end.',resolution='2 in partition is diagrammatic; cabinet termination requires construction detailing.'),
        dict(id='C11',subject='Source reliability',fact='Employer brief lists approximate 36 x 60 WC and calls 243 sq ft preliminary; user specifies 50 x 60.',resolution='Use latest user coordinate schedule for model; do not describe as a completed measured survey.'),
        dict(id='C12',subject='Heights and floor area',fact='Ceiling, sill, head, wall build-ups and cabinet internals are not measured.',resolution='96 in ceiling, window heights and 4 in perimeter/2 in partition diagram thickness are explicit modelling assumptions; 243.06 sq ft is nominal coordinate area.'),
    ]
    changes = [
        dict(id='P01',system='Bath',option='A+B',action='Remove stepped deck; freestanding bath and floor filler near existing wet zone.',dependency='Trap/drain positions, slab recess and waterproofing survey.'),
        dict(id='P02',system='Shower',option='A',action='Extend nominal zone 50 x 60 to 50 x 84; two rain heads; thermostatic controls; level threshold.',dependency='Slope, linear drain, membrane continuity, hot-water delivery and steam enclosure design.'),
        dict(id='M01',system='Hot water',option='A',action='Tank-to-tankless conversion in 50 x 16 chase; PEX manifold.',dependency='Licensed sizing, vent/fuel or electrical supply, condensate, service clearances and access.'),
        dict(id='M02',system='Utility',option='B',action='Retain 50 x 40 mechanical closet and equipment footprint.',dependency='Existing service entrance and clearances unverified; no utility alteration proposed.'),
        dict(id='P03',system='WC',option='A+B',action='Wall-hung WC / concealed carrier; keep nominated stack point (125,182); small rinse basin.',dependency='Carrier anchorage, waste-offset connection and branch drain / vent. Stack point is not cistern position.'),
        dict(id='E01',system='Power',option='A+B',action='Grooming tower GFCI receptacles, heated floor/cabinets, mirror/task/accent lighting.',dependency='Local wet-zone and electrical design; appliance ratings, circuits, heat dissipation and switched isolation.'),
        dict(id='M03',system='Ventilation',option='A+B',action='Exhaust at WC / wet zone; steam feature in A.',dependency='Duct routes and equipment sizing; steam generator location not allocated.'),
        dict(id='A01',system='Millwork / openings',option='A+B',action='S-01/S-02/S-04; proposed WIC and WC pocket doors.',dependency='Pocket travel, wall structure, window conflicts and cabinet access coordination.'),
    ]
    g=dict(schema_version='1.0',project='Luxury Bathroom / Contest 2798513',status='COORDINATE CONCEPT — COORDINATION HOLDS',
           units=dict(model='inch',inch_to_cm=2.54,inch_to_mm=25.4,ft3_to_l=28.316846592),
           origin='Main rectangle south-west corner; +X east, +Y north, +Z up',
           design_read='Architectural competition drawing on white paper, thin black frame, bottom title strip; warm stone / walnut; shared-coordinate axonometric.',
           source_policy='Latest user coordinates govern geometry. Original sketches and video are contextual evidence, not a dimensioned as-built survey.',
           sources=['brief/20261001_165502.jpg','brief/20261001_171608.jpg','brief/bathroom_walkthrough_compressed.mp4','brief/contest_meta.json','user coordinate schedule 2026-11-10'],
           footprint=dict(polygon_in=footprint,polygon_cm=[[round(v*2.54,4) for v in p] for p in footprint],area_in2=35000,area_ft2=35000/144,area_m2=35000*0.00064516),
           assumptions=dict(ceiling_height_in=96,door_head_in=84,window_sill_in=42,window_head_in=90,external_wall_display_thickness_in=4,partition_display_thickness_in=2,wall_thickness_status='diagrammatic only'),
           zones=zones,objects=objects,walls=walls,openings=openings,
           glass=dict(A=[dict(p1=[0,100],p2=[0,138],z_in=[0,96]),dict(p1=[0,138],p2=[0,168],z_in=[0,96],type='pivot door')],B=[dict(p1=[0,100],p2=[0,128],z_in=[0,96]),dict(p1=[0,128],p2=[0,158],z_in=[0,96],type='pivot door'),dict(p1=[0,158],p2=[0,160],z_in=[0,96])]),
           storage=dict(basis='Assumed internal envelope before shelves/hardware/equipment; not certified net capacity',target_ft3=142.4,target_l_exact=142.4*28.316846592,target_l_user=4032,groups=storage,option_A_estimate_ft3=sum(s['volume_ft3'] for s in storage),option_B_estimate_ft3=sum(s['volume_ft3'] for s in storage if s['id']!='S-03')),
           coordination_issues=issues,change_schedule=changes,
           cad_sheet_placement=dict(sheet1=dict(x_range=[0,250],plans=[dict(option='existing',origin_in=[68,40]),dict(option='A',origin_in=[68,340]),dict(option='B',origin_in=[68,640])]),sheet2=dict(x_range=[300,700])),
           lighting=dict(sun_azimuth_deg=225,sun_altitude_deg=35,rain_heads_in=[[-27,136,93],[-27,160,93]],tub_filler_in=[88,173,34],floor_heat='wet-zone intent; no circuit design'))
    for o in openings:
        o['width_cm']=o['width_in']*2.54
        o['fixed_cm']=o['fixed']*2.54
        o['interval_cm']=[n*2.54 for n in o['interval']]
    for w in walls:
        w['bounds_cm']=[round(n*2.54,4) for n in w['bounds_in']]
        w['z_cm']=[round(n*2.54,4) for n in w['z_in']]
    for o in objects:
        o['z_cm']=[round(n*2.54,4) for n in o['z_in']]
        if 'dimensions_in' in o:o['dimensions_feet_inches']=[f'{int(n//12)} ft {n%12:g} in' for n in o['dimensions_in']]
    return g


def write_geometry():
    g=make_geometry()
    (ROOT/'layout_geometry.json').write_text(json.dumps(g,indent=2)+'\n')
    return g


if __name__=='__main__':
    g=write_geometry()
    print(json.dumps({'area_ft2':g['footprint']['area_ft2'],'storage_A_ft3':g['storage']['option_A_estimate_ft3'],'storage_B_ft3':g['storage']['option_B_estimate_ft3']},indent=2))
