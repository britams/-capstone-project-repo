# -*- coding: utf-8 -*-
"""따로 띄운 FreeCAD 창에서 전체를 한 번 만들고 3부분 파일로 나눠 저장 (CAP-AI-62)

  freecad.exe cad/split3_build.py     → cad/split/ 에 S0~S3 .FCStd, cad/split/_build.json, _build.log
쓰는 FreeCAD 창과 다른 프로세스라 무거운 다시 만들기가 멈춰도 그 창은 안전하다.
freecadcmd(GUI 없음)는 못 씀 — D5f 등 옛 스크립트가 ViewObject를 바로 써서 오류 (11/11 확인).
"""
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "split")
os.makedirs(OUT, exist_ok=True)
LOG = os.path.join(OUT, "_build.log")


def log(*a):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a) + "\n")


open(LOG, "w").close()
sys.stdout = open(os.path.join(OUT, "_build_stdout.txt"), "w", encoding="utf-8")   # GUI 창에서는 print가 안 보여서 (RP 실패 이유 등)
rep = dict(ok=False)
try:
    t0 = time.time()
    log("make 시작")
    import D5g_frame_detail as G
    doc = G.make()
    log("make 끝 %.0f s" % (time.time() - t0))
    rep["fix"] = getattr(G, "FIX_REPORT", {})
    import split3 as S
    rep["split"] = S.export(doc, OUT)
    log("나눠 저장 끝", rep["split"]["count"], rep["split"]["files"])
    rep["ok"] = True
    rep["seconds"] = round(time.time() - t0)
except Exception:
    rep["error"] = traceback.format_exc()
    log("오류", rep["error"])
with open(os.path.join(OUT, "_build.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
log("끝")
import FreeCAD as App
if App.GuiUp:          # 따로 띄운 freecad.exe 창은 스스로 닫는다
    os._exit(0)
