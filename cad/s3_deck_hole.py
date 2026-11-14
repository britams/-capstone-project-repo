# -*- coding: utf-8 -*-
"""(11/15 서현, CAP-AI-62) 세운 막대 L 브래킷 → 데크 구멍 Ø5.5 (lift_v3 INFO deck_hole_world) + 데크·위판 레이저 DXF 다시 (탭 구멍 → 관통: M2 Ø1.6 → 2.4, M3 Ø2.5·2.7 → 3.4, 아래 너트)
  freecad.exe cad/s3_deck_hole.py (cwd = cad) → split/S3_프레임회로.FCStd 고쳐 씀, print/all2/101_deck_레이저_5T.dxf·105_top_plate_레이저_5T.dxf, split/_deck_hole.json"""
import json, os, sys, math, traceback
from collections import Counter
HERE = os.getcwd(); sys.path.insert(0, HERE)
rep = {}
MAP = {0.8: 1.2, 1.25: 1.7, 1.35: 1.7}


def dxf(sh, path):
    bb = sh.BoundBox
    ws = sh.slice(App.Vector(0, 0, 1), (bb.ZMin + bb.ZMax) / 2)
    e, holes = [], []
    for w in ws:
        for ed in w.Edges:
            c = ed.Curve
            if "Circle" in type(c).__name__ and ed.isClosed():
                r = c.Radius
                for k, v in MAP.items():
                    if abs(r - k) < 0.02:
                        r = v
                e.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (c.Center.x - bb.XMin, c.Center.y - bb.YMin, r)); holes.append(round(2 * r, 2))
            else:
                pts = ed.discretize(Deflection=0.02)
                for p, q in zip(pts[:-1], pts[1:]):
                    e.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (p.x - bb.XMin, p.y - bb.YMin, q.x - bb.XMin, q.y - bb.YMin))
    open(path, "w", encoding="ascii").write("0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(e) + "\n0\nENDSEC\n0\nEOF\n")
    return dict(size=[round(bb.XLength, 1), round(bb.YLength, 1)], entities=len(e), holes=dict(Counter(holes)))


try:
    import FreeCAD as App, Part
    import lift_v3 as L3
    t = App.newDocument("tmp"); L3.make(t); App.closeDocument(t.Name)
    x, y, d = L3.INFO["deck_hole_world"]
    rep["hole"] = (x, y, d)
    s3 = App.openDocument(os.path.join(HERE, "split", "S3_프레임회로.FCStd"))
    deck = [o for o in s3.Objects if o.Label.startswith("101_deck")][0]
    sh = deck.Shape
    bb = sh.BoundBox
    if not sh.isInside(App.Vector(x, y, (bb.ZMin + bb.ZMax) / 2), 0.01, True):
        rep["note"] = "hole already or not on deck"
    deck.Shape = sh.cut(Part.makeCylinder(d / 2, bb.ZLength + 2, App.Vector(x, y, bb.ZMin - 1)))
    if "세운 막대" not in deck.Label:
        deck.Label = deck.Label.rstrip(")") + ", 세운 막대 L 브래킷 Ø5.5 (11/15))"
    s3.save()
    out = os.path.join(HERE, "print", "all2"); os.makedirs(out, exist_ok=True)
    rep["deck"] = dxf(deck.Shape, os.path.join(out, "101_deck_레이저_5T.dxf"))
    top = [o for o in s3.Objects if o.Label.startswith("105_top_plate")][0]
    rep["top"] = dxf(top.Shape, os.path.join(out, "105_top_plate_레이저_5T.dxf"))
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(HERE, "split", "_deck_hole.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
