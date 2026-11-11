# -*- coding: utf-8 -*-
"""S2: 바닥 올리는 장치 다시 (lift_drive.py) — freecad.exe cad/s2_lift.py → split/_s2_lift.json (CAP-AI-62)"""
import json, os, sys, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "split")
rep = dict(ok=False)
try:
    import FreeCAD as App
    import split3 as S
    import lift_drive as LD
    d = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    S.add_context(d, OUT)
    made, rep["press"] = LD.apply(d)
    hits, sweep = LD.check(d, made)
    rep["overlaps"], rep["sweep"] = hits, sweep
    rep["bad"] = [h for h in hits if h[3] in ("문제", "확인")]
    S.remove_context(d)
    S.color_doc(d)
    d.recompute()
    if not rep["bad"] and not sweep and rep["press"].get("carriage_valid"):
        d.save()
        rep["saved"] = True
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
with open(os.path.join(OUT, "_s2_lift.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
