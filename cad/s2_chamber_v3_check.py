# -*- coding: utf-8 -*-
"""전체 수정 1단계 검사: 새 마킹실 + 리프트 v3를 전체 좌표에 놓고 S1·S2·S3와 겹침 (서현 11/14 17:37 "계속해봐", CAP-AI-62)
  freecad.exe cad/s2_chamber_v3_check.py  (cwd = cad) → split/_chamber_v3.json, split/S2v3_미리보기.FCStd (레포에 안 올림), img/parts/lift/S2v3_*.png
v3가 바꾸는 것(옛 마킹실·바닥 구동)은 빼고 본다. 문·통로·게이트는 그대로 두어 2단계에서 옮길 목록을 얻는다.
"""
import json, os, sys, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "split")
REPLACED = ("120_", "121_", "130_", "140_", "146_", "147_", "148", "149_", "151", "152_", "153", "154_", "155", "157", "158_", "159",
            "227f", "227p", "REF_hornet", "REF_mark_dot", "102_collar")
rep = dict(ok=False)
try:
    import FreeCAD as App
    import Part
    import lift_v3 as L3
    V = App.Vector
    d = App.newDocument("S2v3_preview")
    L3.make(d)
    rep["v3"] = L3.check(d)                       # 리프트 혼자 (움직임·펜·고정끼리)
    m = App.Matrix()
    m.move(L3.WORLD)
    new = []
    for o in d.Objects:
        o.Shape = o.Shape.transformed(m)
        o.Label = "NEW " + o.Label
        new.append(o)
    bb = Part.makeCompound([o.Shape for o in new]).BoundBox
    bb.enlarge(30)
    rep["new_bb"] = [round(v) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)]
    hits, ctx = [], 0
    for f in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        s = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        for o in s.Objects:
            if not o.TypeId.startswith("Part::") or o.Label.startswith(REPLACED):
                continue
            try:
                sh = o.Shape
                if sh.isNull() or sh.Volume <= 0 or not sh.BoundBox.intersect(bb):
                    continue
            except Exception:
                continue
            c = d.addObject("Part::Feature", "C%03d" % ctx)
            c.Shape, c.Label = sh.copy(), "CTX %s %s" % (f[:2], o.Label[:60])
            ctx += 1
            for n in new:
                if n.Shape.BoundBox.intersect(sh.BoundBox):
                    v = n.Shape.common(sh).Volume
                    if v > 0.05 and not o.Label.startswith("REF_camera"):
                        hits.append((n.Label.split(" ")[1], f[:2], o.Label[:50], round(v, 1)))
        App.closeDocument(s.Name)
    rep["context"] = ctx
    rep["hits"] = hits
    if App.GuiUp:
        import FreeCADGui as Gui
        for o in d.Objects:
            if o.Label.startswith("CTX"):
                o.ViewObject.Transparency = 75
                o.ViewObject.ShapeColor = (0.85, 0.85, 0.85)
            elif o.Label.startswith("NEW 300_"):
                o.ViewObject.ShapeColor = (0.2, 0.7, 0.3)
            elif o.Label.startswith("NEW 300p"):
                o.ViewObject.ShapeColor = (0.55, 0.75, 0.95)
        v = Gui.getDocument(d.Name).activeView()
        v.setCameraType("Orthographic")
        img = os.path.join(HERE, "img", "parts", "lift")
        for nm, fn in (("등각", v.viewIsometric), ("정면", v.viewFront), ("위", v.viewTop)):
            fn(); v.fitAll()
            v.saveImage(os.path.join(img, "S2v3_%s.png" % nm), 1600, 1200, "White")
    d.saveAs(os.path.join(OUT, "S2v3_미리보기.FCStd"))
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
with open(os.path.join(OUT, "_chamber_v3.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
