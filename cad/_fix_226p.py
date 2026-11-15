# -*- coding: utf-8 -*-
"""s23_buy_batch2의 226p 팔 판 치수 고침만 지금 파일에 (11/15 움직임 검사: xm 37에서 Y 모터판·P 클립과 닿음) — 한 번만"""
import os, sys, json, traceback
HERE = os.getcwd(); OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
rep = {}
try:
    import FreeCAD as App
    import lift_v2 as L
    V = App.Vector
    d = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    o = [x for x in d.Objects if x.Label.startswith("226p_")][0]
    old = o.Shape.copy()
    cut = L.box(41.0, 50.0, -120, -40, 450, 470).fuse(L.box(0, 50, -51.0, -40, 450, 470))
    o.Shape = old.cut(cut).removeSplitter()
    rep["bb"] = [round(v, 2) for v in (o.Shape.BoundBox.XMax, o.Shape.BoundBox.YMax)]
    d.save(); rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_fix_226p.json"), "w"), indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
