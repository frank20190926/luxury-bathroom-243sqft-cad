"""Rebuild reproducible local artifacts. No upload, deployment or account action."""
import argparse
from pathlib import Path
from geometry import write_geometry
from drawing import render_primary
from cad import build_cad
from convert_dwg import convert
from verify import verify


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--approved-direction',action='store_true',help='Use only after primary visual direction is approved; render the remaining three sheets.')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    for name in ['review','exports']: (root/name).mkdir(exist_ok=True)
    g=write_geometry();render_primary(g);build_cad(g);convert()
    if args.approved_direction:
        from views import comparison,elevations_sheet,cutaway
        comparison(g);elevations_sheet(g);cutaway(g)
    r=verify();print(f'{r["passed"]} checks passed; pending images: {r["pending_images"]}')


if __name__=='__main__':main()
