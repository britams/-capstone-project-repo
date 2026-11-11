# -*- coding: utf-8 -*-
"""전체 도면 D5g_full.FCStd 에 진짜 모터 도면 넣기 (서현 '전체 수정' 때만) — freecad.exe cad/full_motors.py → split/_full_motors.json (CAP-AI-62)"""
import json, os, sys, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
rep = dict(ok=False)
try:
    import FreeCAD as App
    import real_motor as RM
    d = App.openDocument(os.path.join(HERE, "D5g_full.FCStd"))
    rep["motors"] = RM.replace(d)
    hits = RM.overlaps(d)
    rep["overlaps"] = hits
    rep["bad"] = [h for h in hits if h[3] in ("문제", "확인")]
    if not rep["bad"]:
        d.save()
        rep["saved"] = True
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
with open(os.path.join(HERE, "split", "_full_motors.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
