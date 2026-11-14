# -*- coding: utf-8 -*-
"""(11/15 서현, CAP-AI-62) 비상 정지 22Φ → KGAUTO KGE-J4R1R 25Φ (국내 재고): 194b 판의 Ø22.5 구멍 → Ø25.5. S3 고쳐 씀 + 프린트 파일"""
import json, os, sys, traceback
HERE = os.getcwd()
rep = {}
try:
    import FreeCAD as App, Part, MeshPart
    V = App.Vector
    d = App.openDocument(os.path.join(HERE, "split", "S3_프레임회로.FCStd"))
    o = [x for x in d.Objects if x.Label.startswith("194b_estop_plate")][0]
    sh = o.Shape
    cy = [f for f in sh.Faces if isinstance(f.Surface, Part.Cylinder) and abs(f.Surface.Radius - 11.25) < 0.05]
    rep["found"] = len(cy)
    s = cy[0].Surface
    ax, c = s.Axis, s.Center
    bb = sh.BoundBox
    L = 50.0
    cut = Part.makeCylinder(12.75, L, c - ax * (L / 2), ax)
    new = sh.cut(cut).removeSplitter()
    rep["vol"] = (round(sh.Volume, 1), round(new.Volume, 1)); rep["valid"] = new.isValid()
    o.Shape = new
    o.Label = "194b_estop_plate (3D 프린트 4 mm — 비상 정지 Ø25.5 구멍 (KGE-J4R1R 25Φ, 11/15) + 퓨즈 Ø12 + DC 잭 Ø8, 레일에 M5 × 8 두 개)"
    d.save()
    out = os.path.join(HERE, "print", "all")
    MeshPart.meshFromShape(Shape=new, LinearDeflection=0.05, AngularDeflection=0.3).write(os.path.join(out, "194b_estop_plate.stl"))
    new.exportStep(os.path.join(out, "194b_estop_plate.step"))
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(HERE, "split", "_estop25.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
