#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

def fit(im, size):
    copy=im.convert("RGB"); copy.thumbnail(size,Image.Resampling.LANCZOS)
    canvas=Image.new("RGB",size,"white"); canvas.paste(copy,((size[0]-copy.width)//2,(size[1]-copy.height)//2)); return canvas
def main():
    p=argparse.ArgumentParser();p.add_argument("--patent",required=True,type=Path);p.add_argument("--zemax",required=True,type=Path);p.add_argument("--output",required=True,type=Path);p.add_argument("--patent-title");p.add_argument("--zemax-title");n=p.parse_args()
    size=(1100,720); left=fit(Image.open(n.patent),size); right=fit(Image.open(n.zemax),size)
    out=Image.new("RGB",(2220,820),"white");out.paste(left,(0,80));out.paste(right,(1120,80));d=ImageDraw.Draw(out)
    try:font=ImageFont.truetype("arial.ttf",24)
    except OSError:font=ImageFont.load_default()
    d.text((20,20),n.patent_title or f"Patent figure - {n.patent.stem}",fill="black",font=font);d.text((1140,20),n.zemax_title or f"Zemax reconstruction - {n.zemax.stem}",fill="black",font=font)
    d.line((1110,0,1110,820),fill=(120,120,120),width=2);n.output.parent.mkdir(parents=True,exist_ok=True);out.save(n.output)
if __name__=="__main__":main()
