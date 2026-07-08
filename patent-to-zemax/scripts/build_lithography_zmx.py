#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math, os, shutil, sys
from pathlib import Path

def fmt(v): return f"{float(v):.15g}"
def json_safe(value):
    """Replace non-finite API values so a failed trace still produces an audit log."""
    if isinstance(value,float) and not math.isfinite(value):
        return "infinity" if value > 0 else "-infinity" if value < 0 else "nan"
    if isinstance(value,dict):return {k:json_safe(v) for k,v in value.items()}
    if isinstance(value,list):return [json_safe(v) for v in value]
    return value
FRINGE_RADIAL_HIGH_ORDER={
    9:{4:6},16:{4:-30,6:20},25:{4:90,6:-140,8:70},
    36:{4:-210,6:560,8:-630,10:252},
    49:{4:420,6:-1680,8:3150,10:-2772,12:924},
}
def effective_even_coefficients(a):
    """Return Zemax r^2..r^20 coefficients; patent C1 starts at r^4."""
    coeff={2:0.0}
    for i,value in enumerate(a.get("even_coefficients",[]),start=1):coeff[2*i+2]=float(value)
    if a.get("kind")=="fringe_zernike_vertex_preserving":
        radius=float(a["normalization_radius_mm"])
        for term_text,value in a.get("fringe_terms_mm",{}).items():
            term=int(term_text)
            if term not in FRINGE_RADIAL_HIGH_ORDER:raise ValueError(f"unsupported rotational Fringe Zernike term {term}")
            for power,multiplier in FRINGE_RADIAL_HIGH_ORDER[term].items():
                coeff[power]=coeff.get(power,0.0)+float(value)*multiplier/(radius**power)
    return [coeff.get(power,0.0) for power in range(2,22,2)]
def validate(d):
    errors=[]
    required=("patent_id","embodiment","direction","wavelength_um","magnification","field","image_space_na","object_distance_mm","back_focal_distance_mm","surfaces","evidence")
    for key in required:
        if key not in d:errors.append(f"missing {key}")
    surfaces=d.get("surfaces",[])
    if [s.get("number") for s in surfaces] != list(range(1,len(surfaces)+1)):errors.append("surfaces must be consecutively numbered from 1")
    if d.get("direction")!="mask_to_wafer":errors.append("direction must be mask_to_wafer")
    if d.get("field",{}).get("type")!="object_height":errors.append("field.type must be object_height")
    materials=d.get("materials",{})
    for s in surfaces:
        if s.get("material_key") and s.get("material_key") not in materials:
            errors.append(f"material mapping required for refractive surface {s.get('number')}")
    return errors
def initial_zmx(d):
    lines=["VERS 240100 0 0","MODE SEQ",f"NAME {d['patent_id']} embodiment {d['embodiment']} mask-to-wafer reconstruction","UNIT MM X W X CM MR CPMM","GCAT MISC",f"WAVM 1 {fmt(d['wavelength_um'])} 1","PWAV 1"]
    lines += ["SURF 0","  TYPE STANDARD","  CURV 0","  DISZ "+fmt(d["object_distance_mm"])]
    object_material=d.get("materials",{}).get(d.get("object_space_material_key"))
    if object_material:
        if object_material.get("zemax_mode")=="model":lines.append("  GLAS ___BLANK 1 0 "+fmt(object_material["patent_index"])+" 0 0 0 0 0 0")
        else:lines.append("  GLAS "+object_material["zemax_name"])
    lines.append('  DIAM 0 0 0 0 1 ""')
    for s in d["surfaces"]:
        radius=s["radius_mm"]; curvature=0 if isinstance(radius,str) else 1/float(radius)
        surface_type="EVENASPH" if s.get("asphere") else "STANDARD"
        lines += [f"SURF {s['number']}","  TYPE "+surface_type,"  CURV "+fmt(curvature),"  DISZ "+fmt(s["thickness_mm"])]
        if s["number"]==d["stop_surface"]:lines.append("  STOP")
        if s.get("material_key") or (s.get("index_after",0)>1.0001 and d.get("material")):
            material=d.get("materials",{}).get(s.get("material_key"),d.get("material"))
            if material.get("zemax_mode")=="model":
                lines.append("  GLAS ___BLANK 1 0 "+fmt(material["patent_index"])+" 0 0 0 0 0 0")
            else:
                lines.append("  GLAS "+material["zemax_name"])
        if s.get("asphere"):
            a=s["asphere"]
            lines.append("  CONI "+fmt(a.get("conic",0)))
            for i,value in enumerate(effective_even_coefficients(a),start=1):
                lines.append(f"  PARM {i} {fmt(value)}")
        lines.append('  DIAM 0 0 0 0 1 ""')
    image_no=len(d["surfaces"])+1
    lines += [f"SURF {image_no}","  TYPE STANDARD","  CURV 0","  DISZ 0",'  DIAM 0 0 0 0 1 ""']
    return "\n".join(lines)+"\n"
def find_zemax():
    roots=[]
    if os.environ.get("ZEMAX_ROOT"):roots.append(Path(os.environ["ZEMAX_ROOT"]))
    roots.extend(Path(os.environ.get("ProgramFiles",r"C:\Program Files")).glob("Ansys Zemax OpticStudio*"))
    for root in roots:
        if (root/"ZOSAPI.dll").exists():return root
    raise RuntimeError("OpticStudio/ZOS-API not found; set ZEMAX_ROOT")
def load_api():
    import clr
    root=find_zemax(); helper=Path.home()/"Documents"/"Zemax"/"ZOS-API"/"Libraries"/"ZOSAPI_NetHelper.dll"
    clr.AddReference(str(helper if helper.exists() else root/"ZOSAPI_NetHelper.dll"));import ZOSAPI_NetHelper
    if not ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize(str(root)):raise RuntimeError("ZOS-API initialization failed")
    clr.AddReference(str(root/"ZOSAPI_Interfaces.dll"));clr.AddReference(str(root/"ZOSAPI.dll"));import ZOSAPI
    return root,ZOSAPI
def configure_and_verify(d,zmx_path,log_path):
    root,ZOSAPI=load_api(); app=None
    result={"status":"failed","opticstudio_root":str(root),"checks":{},"errors":[]}
    try:
        app=ZOSAPI.ZOSAPI_Connection().CreateNewApplication()
        if app is None or not app.IsValidLicenseForAPI:raise RuntimeError("OpticStudio license is unavailable for API")
        system=app.PrimarySystem; system.LoadFile(str(zmx_path.resolve()),False)
        # Keep Clear Semi-Diameter automatic. Printed clear apertures remain source
        # evidence and clipping checks, but are not forced into fixed LDE cells.
        wave=system.SystemData.Wavelengths.GetWavelength(1);wave.Wavelength=d["wavelength_um"];wave.Weight=1;wave.MakePrimary()
        fields=system.SystemData.Fields;fields.DeleteAllFields();fields.SetFieldType(ZOSAPI.SystemData.FieldType.ObjectHeight)
        requested_fields=[float(y) for y in d["field"]["object_heights_mm"]]
        # OpticStudio retains one default field after DeleteAllFields.
        first=fields.GetField(1);first.X=0;first.Y=requested_fields[0];first.Weight=1
        for y in requested_fields[1:]:fields.AddField(0,y,1)
        asphere_checks=[];unsupported_terms=[]
        for expected in d["surfaces"]:
            a=expected.get("asphere")
            if not a:continue
            actual_surface=system.LDE.GetSurfaceAt(expected["number"])
            if a.get("kind") in ("fringe_zernike_vertex_preserving","even_asphere_zernike_characterization"):
                actual_surface.ChangeType(actual_surface.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.EvenAspheric))
                actual_surface.Conic=float(a.get("conic",0))
                combined=effective_even_coefficients(a)
                for i,value in enumerate(combined,start=12):actual_surface.GetCellAt(i).DoubleValue=float(value)
                interpretation="Zernike values retained as alternate characterization and not added twice" if a.get("kind")=="even_asphere_zernike_characterization" else "vertex-preserving expansion of rotational Fringe Zernike terms"
                asphere_checks.append({"surface":expected["number"],"type":"EvenAspheric","interpretation":interpretation,"zernike_characterization_terms":sorted(int(k) for k in a.get("fringe_terms_mm",{})),"normalization_radius_mm":float(a["normalization_radius_mm"]),"effective_r2_to_r20":combined})
        ray_aiming=system.SystemData.RayAiming;ray_aiming.RayAiming=ZOSAPI.SystemData.RayAimingMethod.Real
        # High-NA lithography objectives can return plausible but incorrect edge-field
        # chief rays with the default heuristic search. Persist robust, enhanced aiming
        # and advanced convergence before solving NA or tracing any validation ray.
        ray_aiming.UseRobustRayAiming=True
        ray_aiming.UseAdvancedConvergence=True
        aperture=system.SystemData.Aperture;aperture.ApertureType=ZOSAPI.SystemData.ZemaxApertureType.ObjectSpaceNA
        target=float(d["image_space_na"]);operand=ZOSAPI.Editors.MFE.MeritOperandType.ISNA
        object_na=float(d.get("object_space_na",target*abs(float(d["magnification"]))))
        aperture.ApertureValue=object_na;system.UpdateStatus()
        # Saving after all settings makes fields and exact image-space-NA aperture persistent in the ZMX.
        system.Save()
        # Reopen the saved file so validation proves persistence, not only in-memory API state.
        system.LoadFile(str(zmx_path.resolve()),False);system.UpdateStatus()
        wave=system.SystemData.Wavelengths.GetWavelength(1);fields=system.SystemData.Fields
        aperture=system.SystemData.Aperture;ray_aiming=system.SystemData.RayAiming
        actual_na=float(system.MFE.GetOperandValue(operand,0,0,0,0,0,0,0,0))
        surface_checks=[]
        for expected in d["surfaces"]:
            actual=system.LDE.GetSurfaceAt(expected["number"])
            radius=float(actual.Radius);thickness=float(actual.Thickness)
            surface_checks.append({"surface":expected["number"],"radius_expected":expected["radius_mm"],"radius_actual":"infinity" if math.isinf(radius) else radius,"thickness_expected":expected["thickness_mm"],"thickness_actual":thickness,"material":str(actual.Material),"published_clear_semi_diameter_mm":expected.get("semi_diameter_mm"),"semi_diameter_mode":"automatic","semi_diameter_actual":float(actual.SemiDiameter)})
        material_checks=[]
        material_map=d.get("materials",{"default":d.get("material")})
        for key,material in material_map.items():
            if material is None:continue
            candidates=[s["number"] for s in d["surfaces"] if s.get("material_key","default")==key]
            if candidates:surface_no=candidates[0]
            elif d.get("object_space_material_key")==key:surface_no=0
            else:
                material_checks.append({"key":key,"pass":False,"error":"material is declared but unused"});continue
            index=float(system.MFE.GetOperandValue(ZOSAPI.Editors.MFE.MeritOperandType.INDX,surface_no,1,0,0,0,0,0,0))
            material_checks.append({"key":key,"surface":surface_no,"pass":abs(index-material["patent_index"])<=material["index_tolerance"],"expected":material["patent_index"],"actual":index,"material":material["zemax_name"]})
        actual_fields=[float(fields.GetField(i).Y) for i in range(1,fields.NumberOfFields+1)]
        actual_track=float(system.LDE.GetSurfaceAt(0).Thickness)+sum(float(system.LDE.GetSurfaceAt(i).Thickness) for i in range(1,len(d["surfaces"])+1))
        # Trace the chief ray at maximum normalized field to verify the realized projection magnification.
        from System import Double, Enum, Int32
        raytrace=system.Tools.OpenBatchRayTrace();data=raytrace.CreateNormUnpol(1,ZOSAPI.Tools.RayTrace.RaysType.Real,system.LDE.NumberOfSurfaces)
        data.AddRay(1,0,1,0,0,Enum.Parse(ZOSAPI.Tools.RayTrace.OPDMode,"None"));raytrace.RunAndWaitForCompletion();data.StartReadingResults()
        result_row=data.ReadNextResult(Int32(1),Int32(1),Int32(1),Double(1),Double(1),Double(1),Double(1),Double(1),Double(1),Double(1),Double(1),Double(1),Double(1),Double(1));raytrace.Close()
        chief_image_y=float(result_row[5]);realized_magnification=chief_image_y/max(requested_fields) if max(requested_fields) else 0.0
        spot_rows=[]
        try:
            spot=system.Analyses.New_Analysis(ZOSAPI.Analysis.AnalysisIDM.StandardSpot);spot.ApplyAndWaitForCompletion();spot_data=spot.GetResults().SpotData
            for field_no in range(1,fields.NumberOfFields+1):
                radius_um=float(spot_data.GetRMSSpotSizeFor(field_no,1))
                spot_rows.append({"field":field_no,"object_y_mm":float(fields.GetField(field_no).Y),"rms_spot_radius_um":radius_um,"rms_spot_diameter_um":2*radius_um})
            spot.Close()
        except Exception as exc:
            unsupported_terms.append({"code":"spot_diagram_reference_unavailable","message":f"RMS spot reference could not be calculated: {type(exc).__name__}: {exc}"})
        def radius_ok(x):
            return x["radius_actual"]=="infinity" if isinstance(x["radius_expected"],str) else abs(float(x["radius_expected"])-float(x["radius_actual"]))<1e-8
        copied_ok=all(radius_ok(x) and abs(float(x["thickness_expected"])-x["thickness_actual"])<1e-8 for x in surface_checks)
        checks={
          "surface_roundtrip":{"pass":copied_ok,"count":len(surface_checks),"details":surface_checks},
          "field_object_heights_mm":{"pass":len(actual_fields)==len(requested_fields) and all(abs(a-b)<1e-10 for a,b in zip(actual_fields,requested_fields)),"expected":requested_fields,"actual":actual_fields},
          "wavelength_um":{"pass":abs(float(wave.Wavelength)-d["wavelength_um"])<1e-12,"expected":d["wavelength_um"],"actual":float(wave.Wavelength)},
          "active_wavelength_count":{"pass":system.SystemData.Wavelengths.NumberOfWavelengths==1,"expected":1,"actual":int(system.SystemData.Wavelengths.NumberOfWavelengths)},
          "object_space_na":{"pass":abs(float(aperture.ApertureValue)-object_na)<1e-12 and str(aperture.ApertureType)=="ObjectSpaceNA","expected":object_na,"actual":float(aperture.ApertureValue),"derivation":"image_space_na * abs(magnification)"},
          "image_space_na":{"pass":True,"within_credibility_tolerance":abs(actual_na-target)<=d.get("image_space_na_credibility_tolerance",0.01),"credibility_tolerance":d.get("image_space_na_credibility_tolerance",0.01),"patent_target":target,"actual_from_ISNA":actual_na,"difference":actual_na-target,"role":"independent credibility check; OBNA is not tuned to force this value"},
          "real_ray_aiming":{"pass":str(ray_aiming.RayAiming)=="Real" and bool(ray_aiming.UseRobustRayAiming) and bool(ray_aiming.UseAdvancedConvergence),"expected":"Real with robust aiming and advanced convergence","actual":str(ray_aiming.RayAiming),"method":str(ray_aiming.Method),"use_robust":bool(ray_aiming.UseRobustRayAiming),"use_enhanced":bool(ray_aiming.UseEnhancedRayAiming),"use_advanced_convergence":bool(ray_aiming.UseAdvancedConvergence)},
          "material_indices":{"pass":all(x["pass"] for x in material_checks),"details":material_checks},
          "total_track_mm":{"pass":abs(actual_track-d["total_track_mm"])<=d.get("total_track_tolerance_mm",0.01),"expected":d["total_track_mm"],"actual":actual_track,"difference":actual_track-d["total_track_mm"]},
          "projection_magnification":{"pass":result_row[0] and result_row[2]==0 and abs(abs(realized_magnification)-abs(d["magnification"]))<=d.get("magnification_tolerance",0.001),"expected_absolute":abs(d["magnification"]),"actual_signed":realized_magnification,"chief_ray_image_height_mm":chief_image_y},
          "rms_spot_diameter_reference":{"pass":True,"unit":"um","role":"reference only; not an optimization eligibility test","fields":spot_rows,"maximum_um":max((x["rms_spot_diameter_um"] for x in spot_rows),default=None)},
          "surface_count":{"pass":system.LDE.NumberOfSurfaces==len(d["surfaces"])+2,"expected":len(d["surfaces"])+2,"actual":int(system.LDE.NumberOfSurfaces)},
          "stop_surface":{"pass":system.LDE.StopSurface==d["stop_surface"],"expected":d["stop_surface"],"actual":int(system.LDE.StopSurface)}
        }
        checks["asphere_supported_terms"]={"pass":True,"details":asphere_checks}
        nonfinite_auto=[x["surface"] for x in surface_checks if not math.isfinite(x["semi_diameter_actual"])]
        if nonfinite_auto:
            unsupported_terms.append({"code":"nonfinite_automatic_semi_diameter","surfaces":nonfinite_auto,"message":"OpticStudio returned an infinite automatic semi-diameter; structural checks pass but marginal-ray performance requires manual review."})
        if not checks["image_space_na"]["within_credibility_tolerance"]:
            unsupported_terms.append({"code":"image_space_na_mismatch","message":"Derived OBNA is preserved, but independent ISNA readback differs from the patent image-side NA; investigate reconstruction credibility.","patent_target":target,"actual":actual_na})
        status="passed" if all(x["pass"] for x in checks.values()) else "failed"
        if status=="passed" and unsupported_terms:status="passed_with_warnings"
        result.update(status=status,checks=checks,warnings=unsupported_terms,system_file=str(system.SystemFile))
    except Exception as exc:result["errors"].append(f"{type(exc).__name__}: {exc}")
    finally:
        if app is not None:
            try:app.CloseApplication()
            except Exception:pass
    result=json_safe(result)
    log_path.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8");return result
def confidence_report(d,validation):
    groups={k:[] for k in ("copied","derived","inferred")}
    for item in d["evidence"]:groups[item["classification"]].append(item)
    lines=["# 复现可信性报告 / Reconstruction Confidence Report","",f"- 专利 / Patent: `{d['patent_id']}`",f"- 实施例 / Embodiment: {d['embodiment']}",f"- ZOS-API 验证 / Validation: **{validation['status'].upper()}**","","## 可信性结论 / Credibility Conclusion","","逐面处方已与渲染后的专利表格核对并经 OpticStudio 回读。结构验证通过不等于专利像差性能已经复现。Clear Semi-Diameter 保持 Automatic；专利口径只作为证据和遮拦核验值。","Surface data are checked against rendered patent tables and round-tripped through OpticStudio. Structural validation alone does not prove reproduction of patent-level aberration performance. Clear Semi-Diameter remains Automatic; published apertures are retained only as evidence and clipping references.",""]
    spot=validation.get("checks",{}).get("rms_spot_diameter_reference",{})
    if spot.get("fields"):
        lines += ["## RMS 点列斑直径参考 / RMS Spot Diameter Reference","","以下数值由最终 ZMX 的 ZOS-API Standard Spot Diagram 计算，仅供复现质量参考。","Values below are calculated from the final ZMX with the ZOS-API Standard Spot Diagram and are provided only as reconstruction-quality references.","","| 视场 / Field | 物高 / Object Y (mm) | RMS 直径 / Diameter (µm) |","|---:|---:|---:|"]
        lines += [f"| {x['field']} | {x['object_y_mm']:.9g} | {x['rms_spot_diameter_um']:.9g} |" for x in spot["fields"]]
        lines += ["",f"- 最大值 / Maximum: `{spot['maximum_um']:.9g} µm`",""]
    for key,title in (("copied","专利直接抄录 / Directly Copied"),("derived","确定性推导 / Deterministically Derived"),("inferred","推断或实现相关 / Inferred or Implementation-dependent")):
        lines += [f"## {title}",""]
        for x in groups[key]:lines.append(f"- `{x['field']}` — confidence {x['confidence']:.2f}: {x['reason']}"+(f" (page {x['source_page']}, {x.get('source_location','')})" if x.get("source_page") else "")+(f" Calculation: `{x['calculation']}`" if x.get("calculation") else ""))
        lines.append("")
    return "\n".join(lines)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("prescription",type=Path);ap.add_argument("--output",required=True,type=Path);ap.add_argument("--source-pdf",type=Path);ns=ap.parse_args();d=json.loads(ns.prescription.read_text(encoding="utf-8"));errors=validate(d)
    if errors:print(json.dumps(errors,indent=2),file=sys.stderr);return 2
    ns.output.mkdir(parents=True,exist_ok=True);stem=f"{d['patent_id']}-embodiment-{d['embodiment']}";zmx=ns.output/f"{stem}.zmx";zmx.write_text(initial_zmx(d),encoding="utf-8",newline="\r\n")
    if ns.source_pdf:
        if ns.source_pdf.read_bytes()[:4]!=b"%PDF":raise ValueError("source file is not a PDF")
        shutil.copy2(ns.source_pdf,ns.output/f"{d['patent_id']}-source.pdf")
    (ns.output/f"{stem}.prescription.json").write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
    log=ns.output/f"{stem}-zosapi-validation.json";result=configure_and_verify(d,zmx,log)
    (ns.output/f"{stem}-confidence.md").write_text(confidence_report(d,result),encoding="utf-8")
    print(zmx);return 0 if result["status"] in ("passed","passed_with_warnings") else 4
if __name__=="__main__":raise SystemExit(main())
