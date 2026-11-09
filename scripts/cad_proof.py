"""Render the actual DXF and DWG roundtrip, separately from presentation assets."""
import logging
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import ezdxf
from ezdxf.addons.drawing import RenderContext,Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration,ColorPolicy,BackgroundPolicy

ROOT=Path(__file__).resolve().parents[1]


def proof():
    logging.getLogger('ezdxf').setLevel(logging.ERROR)
    for key,file in [('dxf','exports/Master_Bathroom_243sqft_Proposal.dxf'),('dwg','review/dwg_roundtrip.dxf')]:
        d=ezdxf.readfile(ROOT/file)
        for style in d.styles:
            p=ROOT/'assets/fonts'/Path(style.dxf.font).name
            if p.is_file():style.dxf.font=str(p)
        fig=plt.figure(figsize=(6,7),dpi=150);ax=fig.add_axes([0,0,1,1])
        cfg=Configuration(color_policy=ColorPolicy.BLACK,background_policy=BackgroundPolicy.WHITE)
        Frontend(RenderContext(d),MatplotlibBackend(ax),config=cfg).draw_layout(d.modelspace(),finalize=True)
        ax.set_aspect('equal',adjustable='box');ax.set_xlim(0,250);ax.set_ylim(300,595);ax.axis('off')
        fig.savefig(ROOT/'review'/f'{key}_plan_proof.png',dpi=150,facecolor='white');plt.close(fig)


if __name__=='__main__':proof()
