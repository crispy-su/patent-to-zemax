#!/usr/bin/env python3
from __future__ import annotations
import argparse,math,sys
from pathlib import Path
from PIL import Image,ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_lithography_zmx import load_api

def sag(radius,y,conic=0.0,coeff=()):
    if math.isinf(radius):base=0.0
    else:
        c=1.0/radius;q=max(0.0,1.0-(1.0+conic)*c*c*y*y)
        base=c*y*y/(1.0+math.sqrt(q))
    return base+sum(float(a)*y**(2*i) for i,a in enumerate(coeff,start=1))

def main():
    ap=argparse.ArgumentParser();ap.add_argument("zmx",type=Path);ap.add_argument("--output",required=True,type=Path);ns=ap.parse_args()
    root,ZOSAPI=load_api();app=None
    try:
        app=ZOSAPI.ZOSAPI_Connection().CreateNewApplication();system=app.PrimarySystem
        system.LoadFile(str(ns.zmx.resolve()),False);system.UpdateStatus()
        count=system.LDE.NumberOfSurfaces;rows=[];z=0.0
        for i in range(count):
            s=system.LDE.GetSurfaceAt(i);radius=float(s.Radius);thickness=float(s.Thickness);semi=float(s.SemiDiameter)
            index=float(system.MFE.GetOperandValue(ZOSAPI.Editors.MFE.MeritOperandType.INDX,i,1,0,0,0,0,0,0))
            coeff=[]
            for cell_no in range(12,20):
                cell=s.GetCellAt(cell_no)
                coeff.append(float(cell.DoubleValue) if cell.IsActive else 0.0)
            rows.append({"number":i,"z":z,"radius":radius,"thickness":thickness,"semi":semi,"index":index,"conic":float(s.Conic),"coeff":coeff})
            z+=thickness
        image_z=rows[-1]["z"];W,H,S=2200,850,2;padx,pady=90,55;maxy=max(r["semi"] for r in rows)*1.08
        def px(x):return int((padx+(x/image_z)*(W-2*padx))*S)
        def py(y):return int((H/2-y/maxy*(H/2-pady))*S)
        im=Image.new("RGB",(W*S,H*S),"white");draw=ImageDraw.Draw(im);draw.line((px(0),py(0),px(image_z),py(0)),fill=(90,90,90),width=2*S)
        for i,s in enumerate(rows[:-1]):
            if s["index"]<=1.05:continue
            e=rows[i+1];radius=min(s["semi"],e["semi"]);ys=[-radius+2*radius*j/80 for j in range(81)]
            left=[(px(s["z"]+sag(s["radius"],y,s["conic"],s["coeff"])),py(y)) for y in ys]
            right=[(px(e["z"]+sag(e["radius"],y,e["conic"],e["coeff"])),py(y)) for y in reversed(ys)]
            color=(224,245,225) if 1.48<s["index"]<1.53 else (205,226,255)
            draw.polygon(left+right,fill=color,outline=(20,45,75))
        envelope=[(px(r["z"]),py(r["semi"])) for r in rows];draw.line(envelope,fill=(70,120,170),width=S);draw.line([(x,2*py(0)-y) for x,y in envelope],fill=(70,120,170),width=S)
        stop=int(system.LDE.StopSurface);st=rows[stop];draw.line((px(st["z"]),py(st["semi"]),px(st["z"]),py(-st["semi"])),fill=(210,40,40),width=2*S)
        wavelength=float(system.SystemData.Wavelengths.GetWavelength(1).Wavelength);na=float(system.MFE.GetOperandValue(ZOSAPI.Editors.MFE.MeritOperandType.ISNA,0,0,0,0,0,0,0,0))
        aperture_type=str(system.SystemData.Aperture.ApertureType);ray_aiming=str(system.SystemData.RayAiming.RayAiming)
        if aperture_type!="ObjectSpaceNA" or ray_aiming!="Real":raise RuntimeError(f"layout export requires ObjectSpaceNA and Real Ray Aiming; got {aperture_type}, {ray_aiming}")
        draw.text((px(0),18*S),f"{ns.zmx.stem} - ZOS-API LDE export",fill=(0,0,0));draw.text((px(0),40*S),f"{aperture_type} | image NA {na:.6f} | Real Ray Aiming | wavelength {wavelength*1000:.3f} nm | surfaces {count} | track {image_z:.6f} mm",fill=(50,50,50))
        ns.output.parent.mkdir(parents=True,exist_ok=True);im.resize((W,H),Image.Resampling.LANCZOS).save(ns.output);print(ns.output)
    finally:
        if app is not None:
            try:app.CloseApplication()
            except Exception:pass
if __name__=="__main__":main()
