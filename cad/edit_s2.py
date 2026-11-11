# -*- coding: utf-8 -*-
"""S2_마킹부만 고치기 — 따로 띄운 freecad.exe로: freecad.exe cad/edit_s2.py (CAP-AI-62)
지금 하는 일: 누름 장치 (D5g_feeder_uln.press_apply → press_check) — 걸쇠 혀·스위치를 +y 쪽으로.
둘레 부품(S1·S3)을 CTX_로 잠깐 넣어 겹침·올림 길을 보고 지움 → split/_edit_s2.json"""
import json, os, sys, time, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "split")
rep = dict(ok=False, t=time.strftime("%H:%M:%S"))
try:
    import FreeCAD as App
    import split3 as S
    d = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    rep["ctx"] = len(S.add_context(d, OUT))
    import D5g_feeder_uln as FU
    _o, pr = FU.press_apply(d)
    rep["press"] = FU.press_check(d, pr)
    S.remove_context(d)
    S.color_doc(d)
    d.recompute()
    d.save()
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
with open(os.path.join(OUT, "_edit_s2.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
