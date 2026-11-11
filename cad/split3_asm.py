# -*- coding: utf-8 -*-
"""S0_전체조립만 다시 만들기 (세 파일은 그대로) — 따로 띄운 freecad.exe로: freecad.exe cad/split3_asm.py (CAP-AI-62)"""
import os, sys, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "split")
try:
    import split3 as S
    msg = "S0 %s MB" % S.make_asm(OUT)
except Exception:
    msg = traceback.format_exc()
with open(os.path.join(OUT, "_asm.log"), "w", encoding="utf-8") as f:
    f.write(msg)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
