# -*- coding: utf-8 -*-
"""마지막 조립 검사: 서로 다른 부분끼리 겹침 (상자 겹치는 쌍만) — freecad.exe cad/split3_boundary.py → split/_boundary.json (CAP-AI-62)"""
import json, os, sys, time, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "split")
rep = dict(ok=False)
t0 = time.time()
try:
    import split3 as S
    rep["hits"] = S.boundary_check(OUT)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
rep["seconds"] = round(time.time() - t0)
with open(os.path.join(OUT, "_boundary.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
