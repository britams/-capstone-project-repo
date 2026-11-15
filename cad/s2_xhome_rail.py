# -*- coding: utf-8 -*-
"""X 원점 스위치 팔: X 봉에 매단 SK8 → 프레임 갠트리 레일 y −170 위에 볼트로 (서현 11/15 22:44 "이건 왜 공중에 떠있냐", CAP-AI-62)
  SK8를 봉에 조여 매다는 방식은 봉에만 걸려 있어 떠 보이고, SK8 본래 쓰임(바닥에 놓고 봉을 잡음)과도 다름 → 뺌
  팔 판 (알루미늄 3 mm 레이저) x 25~41, y −178~−79, z 460~463 — 레일(y −180~−160) 위 M5 × 8 + 스프링너트 2, 스위치는 판 위 (z +3)
  x ≤ 41: 원점(xm 37)에서 Y 모터판 −x 면(41.9)까지 비킴 — 스위치 레버는 그대로 눌림
한 번만 (다시는 split/S2_마킹부_before_xh.FCStd에서). freecad.exe cad/s2_xhome_rail.py (cwd = cad) → split/S2, print/laser/226p_*.dxf, split/_xhome_rail.json"""
import json, os, sys, traceback, glob, time
HERE = os.getcwd(); OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
rep = dict(hits=[])
try:
    import FreeCAD as App, Part
    import lift_v2 as L
    V = App.Vector
    box, cyl = L.box, L.cyl
    d = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]
    for p in ("226_x_home_SK8", "226s_x_home_bolts", "226p_x_home_arm"):
        for o in ob(p):
            d.removeObject(o.Name)
    for o in ob("227x"):
        o.Placement.Base = o.Placement.Base + V(0, 0, 3.0)
    scr = [s.BoundBox.Center for o in ob("227xs") for s in o.Shape.Solids]
    Z0, BX = 460.0, (29.0, 37.0)
    ap = box(25.0, 41.0, -178.0, -79.0, Z0, Z0 + 3)
    for x in BX:
        ap = ap.cut(cyl(2.75, 5, V(x, -170.0, Z0 - 1)))
    for c in scr:
        ap = ap.cut(cyl(1.2, 5, V(c.x, c.y, Z0 - 1)))
    ap = ap.removeSplitter()
    n = d.addObject("Part::Feature", "XH_arm"); n.Shape = ap
    n.Label = "226p_x_home_arm (X 원점 스위치 팔 — 알루미늄 3 mm 레이저, 갠트리 레일 y −170 위 M5 × 8 2, 스위치 M2 2 + 너트)"
    hw = [cyl(2.5, 8, V(x, -170.0, Z0 - 5)) for x in BX] + [box(x - 5, x + 5, -173, -167, Z0 - 6, Z0 - 2) for x in BX]
    n = d.addObject("Part::Feature", "XH_bolts"); n.Shape = Part.makeCompound(hw)
    n.Label = "226s_x_home_bolts (20시리즈 M5 × 8 + 스프링너트 2, 구매)"
    path = os.path.join(OUT, "S2_마킹부.FCStd")
    try:
        d.save()
    except OSError:
        tmp = sorted(glob.glob(path + ".*-*"), key=os.path.getmtime)[-1]
        for _ in range(60):
            try:
                os.replace(tmp, path); break
            except OSError:
                time.sleep(2)
    App.closeDocument(d.Name)
    # DXF
    f = max([x for x in ap.Faces if x.Surface.TypeId == "Part::GeomPlane"], key=lambda x: x.Area); bb = ap.BoundBox
    uv = lambda p: (p.x - bb.XMin, p.y - bb.YMin)
    ents = []
    for e in f.Edges:
        cv = e.Curve
        if "Circle" in cv.TypeId and e.isClosed():
            cc = uv(cv.Center); ents.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (cc[0], cc[1], cv.Radius)); continue
        pts = [uv(p) for p in e.discretize(Deflection=0.02)]
        for a, z in zip(pts[:-1], pts[1:]):
            ents.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (a[0], a[1], z[0], z[1]))
    open(os.path.join(HERE, "print", "laser", "226p_X원점팔_알루미늄3T.dxf"), "w", encoding="ascii").write(
        "0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(ents) + "\n0\nENDSEC\n0\nEOF\n")
    rep["arm"] = [round(bb.XLength, 1), round(bb.YLength, 1)]
    every = []
    for fdoc in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, fdoc + ".FCStd"), True)
        every += [(fdoc[:2] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    ok = (("226s", "226p"), ("226s", "100"), ("226p", "227x"), ("227x", "227x"), ("226p", "100b"))
    for la, sa in [(l, x) for l, x in every if l.split(" ", 1)[1].startswith(("226", "227x"))]:
        for lb, sb in every:
            if la == lb:
                continue
            ta, tb = la.split(" ", 1)[1], lb.split(" ", 1)[1]
            if any(ta.startswith(p) and tb.startswith(q) or ta.startswith(q) and tb.startswith(p) for p, q in ok):
                continue
            if sa.BoundBox.intersect(sb.BoundBox):
                v = sa.common(sb).Volume
                if v > 0.05:
                    rep["hits"].append([la[:45], lb[:45], round(v, 1)])
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_xhome_rail.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
