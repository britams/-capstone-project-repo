# -*- coding: utf-8 -*-
"""색 규칙만 다시 칠하기 (초록 프린트 · 파랑 사서 고침 · 회색 그냥 삼) — freecad.exe cad/recolor.py → split/_recolor.json"""
import json, os, sys, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "split")
rep = {}
try:
    import FreeCAD as App
    import split3 as S
    import D5g_print_color as P
    for nm in S.NAMES + ("S2a_바닥구동",):
        d = App.openDocument(os.path.join(OUT, nm + ".FCStd"))
        S.color_doc(d)
        cnt = {}
        for o in S._solid_objects(d):
            k = P.color_of(o.Label)[1]
            cnt[k] = cnt.get(k, 0) + 1
        rep[nm] = cnt
        d.save()
        App.closeDocument(d.Name)
except Exception:
    rep["error"] = traceback.format_exc()
with open(os.path.join(OUT, "_recolor.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
