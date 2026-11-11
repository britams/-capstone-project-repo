# -*- coding: utf-8 -*-
"""전체 도면 다시 (서현 '전체 수정' 때만): S1·S2·S3을 합쳐 cad/D5g_full.FCStd — freecad.exe cad/full_merge.py → split/_full_merge.json (CAP-AI-62)
D5g_full은 11/10에 만든 옛것이라 나눈 뒤 고친 것(급이부·누름·모터)이 없었음 → 이제 전체 도면 = 세 파일을 합친 것."""
import json, os, sys, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
rep = dict(ok=False)
try:
    import split3 as S
    rep["merge"] = S.merge_full(os.path.join(HERE, "split"), os.path.join(HERE, "D5g_full.FCStd"))
    # (11/12 02:24 서현) 최신 전체 CAD 파일 하나를 바탕화면 capstone design 폴더에도 — 전체 수정 때마다 덮어씀
    import shutil
    PC = r"C:\Users\Seohyun_Lee\Desktop\capstone design"
    if os.path.isdir(PC):
        shutil.copy2(os.path.join(HERE, "D5g_full.FCStd"), os.path.join(PC, "D5g_full.FCStd"))
        rep["pc_copy"] = os.path.join(PC, "D5g_full.FCStd")
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
with open(os.path.join(HERE, "split", "_full_merge.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
