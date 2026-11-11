# -*- coding: utf-8 -*-
"""S1_급이부만 고치기 — 따로 띄운 freecad.exe로: freecad.exe cad/edit_s1.py (CAP-AI-62)
1) S1 열기  2) 둘레 40 mm 안의 마킹부·프레임 부품을 CTX_로 넣기  3) D5g_feeder_pump.apply (병·펌프·관·버림통)
4) CTX 지우기  5) 색 규칙  6) 저장 → split/_edit_s1.json"""
import json, os, sys, time, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "split")
rep = dict(ok=False, t=time.strftime("%H:%M:%S"))
try:
    import FreeCAD as App
    import split3 as S
    d = App.openDocument(os.path.join(OUT, "S1_급이부.FCStd"))
    rep["ctx"] = len(S.add_context(d, OUT))
    import D5g_feeder_pump as FPMP
    r = FPMP.apply(d)
    rep["feeder_pump"] = {k: r[k] for k in ("drain_tube", "feed_tube_z", "feed_tube_len_mm", "drain_tube_len_mm", "bad", "bottle_lift_blockers", "cap_hand_blockers", "holder_on_rail_mm") if k in r}
    rep["overlaps"] = r.get("overlaps")
    S.remove_context(d)
    S.color_doc(d)
    d.recompute()
    d.save()
    rep["objects"] = len([o for o in d.Objects if o.TypeId == "Part::Feature"])
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
with open(os.path.join(OUT, "_edit_s1.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
