# -*- coding: utf-8 -*-
"""S2: 깔때기 111·173 → McMaster 9017T211 + 열수축 (funnels.py) — freecad.exe cad/s2_funnels.py → split/_s2_funnels.json (CAP-AI-62)"""
import json, os, sys, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "split")
rep = dict(ok=False)
try:
    import FreeCAD as App
    import split3 as S
    import funnels as FN
    d = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    S.add_context(d, OUT)
    made, rep["funnels"] = FN.apply(d)
    hits = FN.check(d, made)
    rep["overlaps"] = hits
    rep["bad"] = [h for h in hits if h[3] in ("문제", "확인")]
    S.remove_context(d)
    S.color_doc(d)
    d.recompute()
    if not rep["bad"]:
        d.save()
        rep["saved"] = True
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
with open(os.path.join(OUT, "_s2_funnels.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
