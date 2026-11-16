# -*- coding: utf-8 -*-
"""ULN2003 기판 2장 (X·Y) → DRV8825 2개를 꽂는 듀얼 확장보드 1장 (서현 11/16 "물품구매 정리 설계 다 완료", CAP-AI-62)
  보드: YwRobot 듀얼 42 스텝모터 드라이버 확장보드 ARD200928 (디바이스마트, DRV8825/A4988 꽂음, 68 × 54, 구동 12~24 V) — 납땜 없이 드라이버 꽂고 단자에 선
  치수 68 × 54 [확실 — 판매 페이지], 구멍 4 × Ø3 모서리 3.5 [추측 — 받은 뒤 확인], 높이 부품 포함 약 20 [추측]
  받침: 옛 197 Y 자리 (−x 갠트리 레일 위, 같은 M5 2 — y −146·−102)를 56 × 68 알루미늄 3 mm 레이저로 키움. 197 X 받침·ULN 기판·기둥·M5 2는 뺌
한 번만 (다시는 split/S3_프레임회로_before_drv.FCStd에서). freecad.exe cad/s3_drv_board.py (cwd = cad) → split/S3, print/laser/197_*.dxf, split/_drv_board.json"""
import json, os, sys, traceback, glob, time
HERE = os.getcwd(); OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
rep = dict(hits=[])
try:
    import FreeCAD as App, Part
    import lift_v2 as L
    V = App.Vector
    box, cyl = L.box, L.cyl
    d = App.openDocument(os.path.join(OUT, "S3_프레임회로.FCStd"))
    ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]
    xb = ob("197_uln_bracket_X")[0].Shape.BoundBox
    for p in ("197_uln_bracket_X", "197_uln_bracket_Y", "195p_uln2003_X", "195p_uln2003_Y", "198_uln_standoff_X", "198_uln_standoff_Y"):
        for o in ob(p):
            d.removeObject(o.Name)
    # X 받침 M5 (100h/100i 안 낱개 중 X 받침 자리) 뺌
    gone = 0
    for p in ("100h_bolt_M5x8_mounts", "100i_tnut_M5_mounts"):
        for o in ob(p):
            keep = [s for s in o.Shape.Solids if not (xb.XMin - 1 < s.BoundBox.Center.x < xb.XMax + 1 and xb.YMin - 1 < s.BoundBox.Center.y < xb.YMax + 1)]
            gone += len(o.Shape.Solids) - len(keep)
            o.Shape = Part.makeCompound(keep)
    rep["m5_removed"] = gone
    X0, X1, Y0, Y1, Z0 = -46.0, 10.0, -160.0, -92.0, 460.0
    br = box(X0, X1, Y0, Y1, Z0, Z0 + 3)
    for y in (-146.0, -102.0):
        br = br.cut(cyl(2.75, 5, V(-18.0, y, Z0 - 1)))
    BX0, BX1, BY0, BY1 = -45.0, 9.0, -160.0 + 0.0, -92.0      # 보드 54 (x) × 68 (y)
    holes = [(BX0 + 3.5, BY0 + 3.5), (BX1 - 3.5, BY0 + 3.5), (BX0 + 3.5, BY1 - 3.5), (BX1 - 3.5, BY1 - 3.5)]
    for x, y in holes:
        br = br.cut(cyl(1.7, 5, V(x, y, Z0 - 1)))
    br = br.removeSplitter()
    n = d.addObject("Part::Feature", "DRV_br"); n.Shape = br
    n.Label = "197_drv_bracket (드라이버 보드 받침 — 알루미늄 3 mm 레이저 56 × 68, −x 갠트리 레일 위 M5 2, 보드 기둥 M3 4)"
    ZB = Z0 + 3 + 8
    so = [cyl(2.75, 8, V(x, y, Z0 + 3)) for x, y in holes]
    n = d.addObject("Part::Feature", "DRV_so"); n.Shape = Part.makeCompound(so)
    n.Label = "198_drv_standoff (M3 × 8 암-암 육각 기둥 4 + M3 × 6 8, 구매)"
    pcb = box(BX0, BX1, BY0, BY1, ZB, ZB + 1.6)
    for x, y in holes:
        pcb = pcb.cut(cyl(1.6, 4, V(x, y, ZB - 1)))
    parts = [pcb]
    for yc in (-138.0, -114.0):                       # 드라이버 2개 (15 × 20, 방열판 포함 높이 12) [추측]
        parts.append(box(-26.0, -6.0, yc - 7.5, yc + 7.5, ZB + 1.6 + 8, ZB + 1.6 + 20))
        parts.append(box(-26.0, -6.0, yc - 7.5, yc + 7.5, ZB + 1.6, ZB + 1.6 + 8))   # 소켓
    parts.append(box(BX0 + 2, BX0 + 12, BY0 + 6, BY1 - 6, ZB + 1.6, ZB + 1.6 + 10))  # 단자대 (모터·전원) [추측]
    n = d.addObject("Part::Feature", "DRV_pcb"); n.Shape = Part.makeCompound(parts)
    n.Label = "195p_drv_dual_board (YwRobot ARD200928 듀얼 스텝 드라이버 확장보드 68 × 54 + DRV8825 2 — 판매 규격 상자, 구매)"
    path = os.path.join(OUT, "S3_프레임회로.FCStd")
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
    f = max([x for x in br.Faces if x.Surface.TypeId == "Part::GeomPlane"], key=lambda x: x.Area); bb = br.BoundBox
    ents = []
    for e in f.Edges:
        cv = e.Curve
        if "Circle" in cv.TypeId and e.isClosed():
            ents.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (cv.Center.x - bb.XMin, cv.Center.y - bb.YMin, cv.Radius)); continue
        pts = [(p.x - bb.XMin, p.y - bb.YMin) for p in e.discretize(Deflection=0.02)]
        for a, z in zip(pts[:-1], pts[1:]):
            ents.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (a[0], a[1], z[0], z[1]))
    LZ = os.path.join(HERE, "print", "laser")
    for old in glob.glob(os.path.join(LZ, "197*.dxf")):
        os.remove(old)
    open(os.path.join(LZ, "197_드라이버받침_알루미늄3T_56x68.dxf"), "w", encoding="ascii").write(
        "0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(ents) + "\n0\nENDSEC\n0\nEOF\n")
    every = []
    for fdoc in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, fdoc + ".FCStd"), True)
        every += [(fdoc[:2] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    ok = (("197_drv", "198_drv"), ("197_drv", "100"), ("198_drv", "195p_drv"))
    for la, sa in [(l, x) for l, x in every if l.split(" ", 1)[1].startswith(("197_drv", "198_drv", "195p_drv"))]:
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
json.dump(rep, open(os.path.join(OUT, "_drv_board.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
