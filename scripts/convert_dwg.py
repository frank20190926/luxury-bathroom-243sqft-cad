"""LibreDWG compatibility conversion with entity-by-entity roundtrip evidence.

The authoritative DXF remains R2010. LibreDWG 0.14 has known metadata warnings;
the DWG is R2000 and its verification is a local roundtrip, not AutoCAD QA.
"""
import json
import logging
import math
import subprocess
from collections import Counter
from pathlib import Path
import ezdxf
from ezdxf.disassemble import recursive_decompose
from ezdxf.addons import text2path, MTextExplode
from ezdxf.layouts import VirtualLayout

ROOT=Path(__file__).resolve().parents[1]


def nums(v):
    if isinstance(v,(int,float)):return round(float(v),6)
    return tuple(round(float(x),6) for x in v)


def equivalent(a,b):
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):return abs(a-b)<=1e-5
    if isinstance(a,(list,tuple)) and isinstance(b,(list,tuple)):
        return len(a)==len(b) and all(equivalent(x,y) for x,y in zip(a,b))
    return a==b


def signature(e):
    t=e.dxftype();v=[t,e.dxf.get('layer','0')]
    attrs={'LINE':['start','end'],'TEXT':['text','insert','align_point','height','rotation','style'],
           'ARC':['center','radius','start_angle','end_angle'],'ELLIPSE':['center','major_axis','ratio','start_param','end_param'],
           'DIMENSION':['dimtype','defpoint','defpoint2','defpoint3','angle','text','geometry','dimstyle'],
           'POINT':['location'],'SOLID':['vtx0','vtx1','vtx2','vtx3'],
           'INSERT':['name','insert','rotation','xscale','yscale','zscale']}
    for a in attrs.get(t,[]):
        value=e.dxf.get(a)
        if value is None:
            # Optional rotations/scales omitted during serialization are defaults.
            value=0. if a in ['rotation','angle'] else 1. if a.endswith('scale') else '' if a=='text' else None
        if value is not None and not isinstance(value,str):value=nums(value)
        v.append((a,value))
    if t=='LWPOLYLINE':v.extend([bool(e.closed),tuple(nums(p) for p in e.get_points('xyb'))])
    elif t=='HATCH':
        v.extend([e.dxf.solid_fill,e.dxf.pattern_name,tuple(tuple(nums(p) for p in path.vertices) for path in e.paths if hasattr(path,'vertices'))])
        if not e.dxf.solid_fill:v.extend([nums(e.dxf.pattern_scale),nums(e.dxf.pattern_angle),tuple((nums(l.angle),nums(l.base_point),nums(l.offset),tuple(nums(x) for x in l.dash_length_items)) for l in e.pattern.lines)])
    elif t=='MTEXT':v.extend([e.text,nums(e.dxf.insert),nums(e.dxf.char_height),round(e.get_rotation()%360,5)])
    return v


def convert():
    logging.getLogger('ezdxf').setLevel(logging.ERROR)
    src=ROOT/'exports/Master_Bathroom_243sqft_Proposal.dxf'
    conv=ROOT/'review/dwg_conversion_input.dxf'; dwg=src.with_suffix('.dwg');back=ROOT/'review/dwg_roundtrip.dxf'
    d=ezdxf.readfile(src)
    # LibreDWG loses TEXT alignment points, MTEXT height and rotated dimension
    # angles. Preserve appearance as editable vectors in the companion DWG;
    # the R2010 master retains semantic text and native dimension entities.
    for style in d.styles:
        font=ROOT/'assets/fonts'/style.dxf.font
        if font.is_file():style.dxf.font=str(font)
    flat=list(recursive_decompose(d.modelspace()))
    normalized=[]
    for e in flat:
        if e.dxftype()=='MTEXT':
            layout=VirtualLayout()
            with MTextExplode(layout,doc=d) as exploder:exploder.explode(e,destroy=False)
            normalized.extend(list(layout))
        else:normalized.append(e)
    flat=normalized
    m=d.modelspace()
    originals=list(m)
    for e in originals:m.unlink_entity(e)
    outlined=0
    for e in flat:
        if e.dxftype() in ['TEXT','MTEXT']:
            paths=text2path.make_paths_from_entity(e)
            hatch=m.add_hatch(color=7,dxfattribs={'layer':e.dxf.layer})
            for path in paths:
                for part in path.sub_paths():
                    points=[(p.x,p.y) for p in part.flattening(.002)]
                    if len(points)>=3:hatch.paths.add_polyline_path(points,is_closed=True)
            if not hatch.paths:m.delete_entity(hatch)
            outlined+=1
        else:
            m.add_entity(e.copy())
    for block in d.blocks:
        for e in block.query('MTEXT'):
            if e.dxf.hasattr('rotation'):
                a=math.radians(e.dxf.rotation);e.dxf.text_direction=(math.cos(a),math.sin(a),0);e.dxf.discard('rotation')
    d.header['$DIMBLK']='';d.saveas(conv)
    logs={}
    for name,args in [('dxf2dwg',['dxf2dwg','--as','r2000','-y','-o',str(dwg),str(conv)]),('dwg2dxf',['dwg2dxf','-y','-o',str(back),str(dwg)])]:
        r=subprocess.run(args,capture_output=True,text=True,timeout=60);logs[name]=r.stdout+r.stderr
        (ROOT/'review'/f'{name}.log').write_text(logs[name])
        if r.returncode:raise RuntimeError(f'{name} returned {r.returncode}')
    a=ezdxf.readfile(conv);b=ezdxf.readfile(back);differences=[]
    if len(a.modelspace())!=len(b.modelspace()):differences.append('modelspace entity count')
    for j,(x,y) in enumerate(zip(a.modelspace(),b.modelspace())):
        if not equivalent(signature(x),signature(y)):differences.append(dict(space='modelspace',index=j,type=x.dxftype()))
    block_differences=[]
    # All placed dimensions/inserts were decomposed. Unreferenced source blocks
    # remain only to avoid LibreDWG handle-map defects and do not draw anything.
    used_blocks={e.dxf.name for e in a.modelspace().query('INSERT')}
    for block in a.blocks:
        if block.name.startswith('*Model') or block.name.startswith('*Paper'):continue
        if block.name not in used_blocks:continue
        if block.name not in b.blocks:block_differences.append(dict(block=block.name,reason='missing'));continue
        other=b.blocks[block.name]
        if len(block)!=len(other):block_differences.append(dict(block=block.name,reason='entity count'));continue
        for j,(x,y) in enumerate(zip(block,other)):
            if not equivalent(signature(x),signature(y)):block_differences.append(dict(block=block.name,index=j,type=x.dxftype()))
    au=b.audit()
    report=dict(dwg_header=dwg.read_bytes()[:6].decode(),dwg_version='AutoCAD 2000',
        source_dxf_version='R2010 / AC1024',modelspace_entities=len(b.modelspace()),blocks=len(b.blocks),
        modelspace_differences=differences,block_differences=block_differences,
        roundtrip_audit_errors=len(au.errors),roundtrip_audit_fixes=len(au.fixes),
        converter_warnings={k:len([l for l in txt.splitlines() if 'Warning:' in l or 'ERROR:' in l]) for k,txt in logs.items()},
        text_entities_outlined=outlined,dimensions_flattened_for_dwg=True,outline_tolerance_in=0.002,comparison_tolerance_in=0.00001,roundtrip_units=b.units,placed_block_references=len(used_blocks),comparison_scope='All placed modelspace entities and referenced blocks; unused library blocks excluded',
        limitations=['DWG text and dimensions are vector outlines / primitives for LibreDWG compatibility; edit semantic annotations in the R2010 DXF.',
                      'LibreDWG emits metadata/handle/HATCH warnings; local geometry comparison does not certify AutoCAD interoperability.',
                      'DWG has not been opened in Autodesk AutoCAD. Use the audited R2010 DXF as authority.'],
        status='local_roundtrip_geometry_pass' if not differences and not block_differences and not au.errors else 'roundtrip_differences_require_review')
    (ROOT/'exports/dwg_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    r=convert();print(json.dumps({k:v for k,v in r.items() if k not in ['modelspace_differences','block_differences']},indent=2));print('modelspace differences:',len(r['modelspace_differences']),'block differences:',len(r['block_differences']))
