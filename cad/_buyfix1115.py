# -*- coding: utf-8 -*-
"""(11/15 서현, CAP-AI-62) '자르기' 부품 → 출력 대행 파일, 데크·위판 → 레이저 DXF, 바닥 F 드라이버 자리(DRV8833, mightyZAP으로 필요 없음) 지움"""
import json, os, re, math, traceback
HERE = os.getcwd()
OUT = os.path.join(HERE, "print", "all2"); os.makedirs(OUT, exist_ok=True)
rep = dict(prints=[], dxf=[], removed=[])
def dxf_from_shape(sh, path):
    bb = sh.BoundBox
    zc = (bb.ZMin + bb.ZMax) / 2
    ws = sh.slice(App.Vector(0, 0, 1), zc)
    e = []; holes = []
    for w in ws:
        for ed in w.Edges:
            c = ed.Curve
            if isinstance(c, Part.Circle) or "Circle" in type(c).__name__:
                cc, r = c.Center, c.Radius
                if ed.isClosed():
                    e.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (cc.x - bb.XMin, cc.y - bb.YMin, r)); holes.append(round(2 * r, 2))
                else:
                    a0 = math.degrees(math.atan2(ed.Vertexes[0].Point.y - cc.y, ed.Vertexes[0].Point.x - cc.x))
                    a1 = math.degrees(math.atan2(ed.Vertexes[-1].Point.y - cc.y, ed.Vertexes[-1].Point.x - cc.x))
                    if c.Axis.z < 0: a0, a1 = a1, a0
                    e.append("0\nARC\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f\n50\n%.3f\n51\n%.3f" % (cc.x - bb.XMin, cc.y - bb.YMin, r, a0, a1))
            else:
                pts = ed.discretize(Deflection=0.02) if not isinstance(c, Part.Line) and "Line" not in type(c).__name__ else [ed.Vertexes[0].Point, ed.Vertexes[-1].Point]
                for p, q in zip(pts[:-1], pts[1:]):
                    e.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (p.x - bb.XMin, p.y - bb.YMin, q.x - bb.XMin, q.y - bb.YMin))
    open(path, "w", encoding="ascii").write("0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(e) + "\n0\nENDSEC\n0\nEOF\n")
    from collections import Counter
    return dict(size=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)], wires=len(ws), entities=len(e), holes=dict(Counter(holes)))
try:
    import FreeCAD as App, Part, MeshPart
    d = App.openDocument(os.path.join(HERE, "D5g_full.FCStd"), True)
    want = ("110_entry_duct", "172_isolation_duct", "111_entry_funnel", "173_isolation_funnel", "143_feed_trough", "143l_feed_trough_lid",
            "143p_post", "143a_angle", "143b_angle", "144b_feeder_holder")
    for o in d.Objects:
        if not o.TypeId.startswith("Part::"): continue
        code = o.Label.split(" ")[0]
        if code.startswith(want):
            sh = o.Shape
            if code.startswith("143_feed_trough") and len(sh.Solids) > 1:
                sh = sh.Solids[0].multiFuse(sh.Solids[1:]).removeSplitter()
            parts = sh.Solids if code.startswith("172_isolation_duct") else [sh]
            for k, s in enumerate(parts):
                nm = re.sub(r'[\\/:*?"<>|]', "_", code) + ("_%d" % (k + 1) if len(parts) > 1 else "")
                m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.3)
                m.write(os.path.join(OUT, nm + ".stl")); s.exportStep(os.path.join(OUT, nm + ".step"))
                bb = s.BoundBox
                rep["prints"].append(dict(file=nm, label=o.Label[:90], solids=len(s.Solids), valid=s.isValid(), mesh_solid=m.isSolid(),
                                          vol_cm3=round(s.Volume / 1000, 2), size=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)]))
        if code.startswith(("101_deck", "105_top_plate")):
            nm = code
            info = dxf_from_shape(o.Shape, os.path.join(HERE, "print", "lift", "..", "all2", nm + ".dxf"))
            info.update(file=nm, label=o.Label[:90]); rep["dxf"].append(info)
    App.closeDocument(d.Name)
    s3 = App.openDocument(os.path.join(HERE, "split", "S3_프레임회로.FCStd"))
    for o in list(s3.Objects):
        if o.Label.startswith(("195p_uln2003_F", "198_uln_standoff_F")):
            rep["removed"].append(o.Label[:60]); s3.removeObject(o.Name)
    s3.save()
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(HERE, "split", "_buyfix1115.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp: os._exit(0)
