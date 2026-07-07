#!/usr/bin/env python3
"""Block batch completion until every discovered numerical embodiment is resolved."""
import argparse,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument("inventory",type=Path);ap.add_argument("--output-root",required=True,type=Path);ns=ap.parse_args()
    data=json.loads(ns.inventory.read_text(encoding="utf-8"));errors=[]
    rows=data.get("embodiments",[])
    if not rows:errors.append("no embodiments inventoried")
    for row in rows:
        label=row.get("label","<missing>");status=row.get("status")
        if status not in ("modeled","unreconstructable"):errors.append(f"{label}: unresolved status {status!r}");continue
        artifact=row.get("artifact")
        if not artifact:errors.append(f"{label}: missing artifact path");continue
        path=(ns.output_root/artifact).resolve()
        if not path.is_file():errors.append(f"{label}: artifact not found: {path}")
        if status=="modeled" and path.suffix.lower()!=".zmx":errors.append(f"{label}: modeled artifact must be .zmx")
        if status=="unreconstructable" and path.suffix.lower()!=".md":errors.append(f"{label}: unreconstructable artifact must be a bilingual .md report")
    result={"patent_id":data.get("patent_id"),"inventoried":len(rows),"complete":not errors,"errors":errors}
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result["complete"] else 2
if __name__=="__main__":raise SystemExit(main())
