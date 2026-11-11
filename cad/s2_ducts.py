# -*- coding: utf-8 -*-
"""S2: 통로 관 → PVC 13A + 꺾임 조각 (ducts_pvc.py), 그 뒤 게이트 받침 다시 (gate2167, 관 Ø18) — freecad.exe cad/s2_ducts.py → split/_s2_ducts.json (CAP-AI-62)"""
import json, os, sys, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "split")
rep = dict(ok=False)
try:
    import FreeCAD as App
    import split3 as S
    import ducts_pvc as DP
    import gate2167 as G
    d = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    S.add_context(d, OUT)
    made, rep["ducts"] = DP.apply(d)
    gm, rep["gates"] = G.apply(d)
    hits = DP.check(d, made)
    gh, touch = G.check(d, gm)
    rep["overlaps"], rep["gate_overlaps"], rep["touch"] = hits, gh, touch
    rep["bad"] = [h for h in hits + gh if h[3] in ("문제", "확인")]
    S.remove_context(d)
    S.color_doc(d)
    d.recompute()
    if not rep["bad"]:
        d.save()
        rep["saved"] = True
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
with open(os.path.join(OUT, "_s2_ducts.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
