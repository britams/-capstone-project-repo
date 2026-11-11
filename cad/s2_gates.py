# -*- coding: utf-8 -*-
"""S2: 빛 게이트 송수신기 Adafruit 2167 실제 치수 + 안장 받침 (gate2167.py) — freecad.exe cad/s2_gates.py → split/_s2_gates.json (CAP-AI-62)"""
import json, os, sys, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "split")
rep = dict(ok=False)
try:
    import FreeCAD as App
    import split3 as S
    import gate2167 as G
    d = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    S.add_context(d, OUT)
    made, rep["gates"] = G.apply(d)
    hits, touch = G.check(d, made)
    rep["overlaps"], rep["touch"] = hits, touch
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
with open(os.path.join(OUT, "_s2_gates.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
