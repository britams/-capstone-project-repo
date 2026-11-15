# -*- coding: utf-8 -*-
"""마커 P 클립 → HellermannTyton P-8 (서현 11/15 22:03 "판홀더는 기구니까 건들고 싶으면", CAP-AI-62)
  규격 P 클립 15 mm는 M6 나사 (홀더 판 3 mm에 머리가 안 묻힘) → P-8: 묶음 Ø13.7~14.3 (마커 Ø14.7을 조금 늘려 잡음 [추측]), 폭 9.5, 벽 1.8, 구멍 3.2, 길이 28 [확실 — 제조사 페이지]
  마커 축 = 판 면 − (7.35 + 1.8) = 75 그대로. 귀는 −y 쪽 (구멍 y −54) → 홀더 판 HV를 y −58까지 늘림, 옛 M4 구멍(y −29) 메움, M3 접시 (HV +x 면이 SP에 미끄러짐)
한 번만 (다시는 split/S2_마킹부_before_p8.FCStd에서). freecad.exe cad/s2_clip_p8.py (cwd = cad) → split/S2, print/xy/HV_*.dxf, split/_clip_p8.json"""
import json, os, sys, traceback, glob
HERE = os.getcwd(); OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
rep = dict(hits=[])
try:
    import FreeCAD as App, Part
    import lift_v2 as L
    V = App.Vector
    box, cyl = L.box, L.cyl
    ex = V(1, 0, 0)
    XM, YM, HV0, HV1 = 75.0, -40.0, 84.15, 87.15
    CZ, W, T, YH = (412.0, 445.0), 9.5, 1.8, -54.0
    d = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]
    hv = ob("202_holder_plate_HV")[0]
    s = hv.Shape.fuse(box(HV0, HV1, -58.0, -45.0, 405.0, 455.0))
    for z in CZ:
        s = s.fuse(cyl(2.2, T + 3.2, V(HV0 - 0.1, -29.0, z), ex))      # 옛 M4 구멍 메움
    s = s.removeSplitter()
    s = s.common(box(HV0, HV1, -100, 100, 300, 500))
    for z in CZ:
        s = s.cut(cyl(1.7, 10, V(HV0 - 5, YH, z), ex))
    hv.Shape = s.removeSplitter()
    hv.Label = "202_holder_plate_HV (홀더 판 — 알루미늄 3 mm 레이저, 밑 모서리가 서보 혼에, P-8 M3 접시 2)"
    clips = []
    for z in CZ:
        ring = cyl(7.35 + T, W, V(XM, YM, z - W / 2)).cut(cyl(7.35, W + 2, V(XM, YM, z - W / 2 - 1)))
        tab = box(HV0 - T, HV0, -58.0, YM - 7.35, z - W / 2, z + W / 2).cut(cyl(1.6, 5, V(HV0 - 3, YH, z), ex))
        clips.append(ring.fuse(tab).removeSplitter())
    c = ob("203_marker_P_clips")[0]
    c.Shape = Part.makeCompound(clips)
    c.Label = "203_marker_P_clips (HellermannTyton P-8 ×2 — 묶음 Ø13.7~14.3, 폭 9.5, 구멍 3.2, 구매)"
    b = ob("202_holder_bolts")[0]
    keep = [x for x in b.Shape.Solids if abs(x.BoundBox.Center.y + 29.0) > 1.5]   # 어깨 볼트만 남김
    for z in CZ:
        keep.append(cyl(1.5, 10, V(HV1, YH, z), V(-1, 0, 0)))
        keep.append(box(HV0 - T - 2.4, HV0 - T, YH - 2.75, YH + 2.75, z - 2.75, z + 2.75))
    b.Shape = Part.makeCompound(keep)
    b.Label = "202_holder_bolts (어깨 볼트 M3 · 어깨 Ø4 × 6 2 + 너트, P-8용 M3 × 10 접시머리 2 + 너트 — 구매, 홀더와 같이 움직임)"
    rep["bolt_solids"] = len(keep)
    d.save()
    # DXF (HV)
    sl = hv.Shape.Solids[0]
    f = max([x for x in sl.Faces if x.Surface.TypeId == "Part::GeomPlane"], key=lambda x: x.Area); bb = sl.BoundBox
    uv = lambda p: (p.y - bb.YMin, p.z - bb.ZMin)
    ents = []
    for e in f.Edges:
        cv = e.Curve
        if "Circle" in cv.TypeId and e.isClosed():
            cc = uv(cv.Center); ents.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (cc[0], cc[1], cv.Radius)); continue
        pts = [uv(p) for p in e.discretize(Deflection=0.02)]
        for a, z in zip(pts[:-1], pts[1:]):
            ents.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (a[0], a[1], z[0], z[1]))
    XY = os.path.join(HERE, "print", "xy")
    for old in glob.glob(os.path.join(XY, "HV_*.dxf")):
        os.remove(old)
    fn = "HV_홀더판_알루미늄3T_M3접시2_%gx%g.dxf" % (round(bb.YLength, 1), round(bb.ZLength, 1))
    open(os.path.join(XY, fn), "w", encoding="ascii").write("0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(ents) + "\n0\nENDSEC\n0\nEOF\n")
    rep["dxf"] = fn
    App.closeDocument(d.Name)
    every = []
    for fdoc in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, fdoc + ".FCStd"), True)
        every += [(fdoc[:2] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    ok = (("202_holder_b", "202_holder_p"), ("202_holder_b", "203"), ("203", "201"), ("203", "202_holder_p"), ("202_holder_b", "206_carriage_p"), ("205h", "202_holder_p"))
    for la, sa in [(l, x) for l, x in every if l.split(" ", 1)[1].startswith(("202", "203"))]:
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
json.dump(rep, open(os.path.join(OUT, "_clip_p8.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
