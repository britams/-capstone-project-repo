# -*- coding: utf-8 -*-
"""XY 구동을 '나사 일체형 모터' 모터뱅크 LM-NK1134 (28각, 외부 스크류형, 스크류 150) 2개로 (서현 11/16 18:02 "물품구매 정리 설계 다 완료", CAP-AI-62)
  NK1140 + 커플링 5→8 + T8 리드 나사·황동 너트는 커플링·T8을 파는 국내 판매처를 못 찾음 (디바이스마트·아이씨뱅큐·모터뱅크·11번가 11/16) →
  모터 축이 곧 나사인 LM-NK1134 하나로 (모터뱅크, 국내) — 커플링·T8 4개가 빠지고 축 맞춤도 없어짐.
  치수 [가능성 높음 — 모터뱅크 LM-NK1134 도면 그림]: 몸 28각 × 34, 턱 Ø22 × 2, 스크류 Tr5 × 2 (지름 5, 리드 2, 한 스텝 0.01 mm), 길이 132 옵션 (150은 Y 끝이 빔 판 YB에 닿음 — 11/16 검사),
    POM 너트: 플랜지 Ø19.05 × 3.18, 몸 Ø7.94, 전체 9.53, 구멍 3 × Ø3.175 PCD 12.7. 앞 나사 구멍은 NK1140과 같은 23 × 23 M2.6 [추측 — 같은 28각 계열].
  모터판 217·211은 그대로 (턱 Ø22.5·M2.6 구멍 같음). 너트 판 XN·캐리지 판 CP: 옛 T8 너트 구멍 메우고 Ø8.5 + M3 Ø3.4 3 (PCD 12.7).
한 번만 (다시는 split/S2_마킹부_before_lm.FCStd에서). freecad.exe cad/s2_xy_lm1134.py (cwd = cad) → split/S2, print/xy/{XN,CP}_*.dxf, split/_xy_lm1134.json"""
import json, os, sys, traceback, glob, time, math
HERE = os.getcwd(); OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
rep = dict(hits=[])
try:
    import FreeCAD as App, Part
    import lift_v2 as L
    V = App.Vector
    box, cyl = L.box, L.cyl
    d = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]
    BODY, PIL, PT, SCR, SD = 34.0, 22.0, 2.0, 132.0, 5.0

    def along(c, n, a, b, r):          # 축 c, 방향 n 위 [a, b] 구간 원기둥 (a, b = 축 방향 좌표)
        p = c + n * (a - c.dot(n))
        return cyl(r, b - a, p, n)

    def motor(c, n, face):            # n = 나사가 나가는 방향, face = 몸 앞면 (n 방향 좌표)
        p0 = c + n * (face - c.dot(n))
        m = Part.makeBox(28, 28, BODY, V(-14, -14, -BODY))
        m.Placement = App.Placement(p0, App.Rotation(V(0, 0, 1), n))
        m = m.fuse(along(c, n, face, face + PT, PIL / 2)).removeSplitter()
        return m, along(c, n, face, face + SCR, SD / 2)

    def new_nut(o, c, n, f0, f1, b0, b1):   # 플랜지 [f0, f1], 몸 [b0, b1] (n 방향 좌표)
        u = V(0, 1, 0) if abs(n.y) < 0.5 else V(1, 0, 0); w = n.cross(u)
        fl = along(c, n, f0, f1, 19.05 / 2)
        for k in range(3):
            a = math.radians(90 + 120 * k)
            q = c + (u * math.cos(a) + w * math.sin(a)) * 6.35
            fl = fl.cut(along(q, n, f0 - 1, f1 + 1, 3.175 / 2))
        lo, hi = min(f0, b0), max(f1, b1)
        nut = fl.fuse(along(c, n, b0, b1, 7.94 / 2)).cut(along(c, n, lo - 1, hi + 1, SD / 2)).removeSplitter()
        o.Shape = nut
        return u, w

    def replate(sol, c, n, u, w):          # 판 한 장: 축 근처(10.6 안) 옛 구멍 메움 → Ø8.5 + Ø3.4 3
        bb = sol.BoundBox
        t0 = min(V(bb.XMin, bb.YMin, bb.ZMin).dot(n), V(bb.XMax, bb.YMax, bb.ZMax).dot(n)) - 1
        t1 = max(V(bb.XMin, bb.YMin, bb.ZMin).dot(n), V(bb.XMax, bb.YMax, bb.ZMax).dot(n)) + 1
        s = sol
        for e in sol.Edges:
            if "Circle" in e.Curve.TypeId:
                q = e.Curve.Center; q = V(q.x, q.y, q.z)
                dq = q - c; dq = dq - n * dq.dot(n)
                if dq.Length + e.Curve.Radius < 10.6:
                    s = s.fuse(along(c + dq, n, t0 + 1, t1 - 1, e.Curve.Radius + 0.01))
        s = s.removeSplitter()
        s = s.cut(along(c, n, t0, t1, 4.25))
        for k in range(3):
            a = math.radians(90 + 120 * k)
            s = s.cut(along(c + (u * math.cos(a) + w * math.sin(a)) * 6.35, n, t0, t1, 1.7))
        return s.removeSplitter()

    for p in ("215_x_stepper_NK1140", "209_y_stepper_NK1140", "210_y_coupling", "216_x_coupling", "208_y_lead_screw_T8", "214_x_lead_screw_T8"):
        for o in ob(p):
            d.removeObject(o.Name)
    # X: 축 y −65 · z 425, 나사 −x, 몸 앞면 x 160 / Y: 축 x 101.4 · z 453, 나사 +y, 몸 앞면 y −101.9
    CX, NX = V(0, -65.0, 425.0), V(-1, 0, 0)
    CY, NY = V(101.4, 0, 453.0), V(0, 1, 0)
    mx, sx = motor(CX, NX, -160.0)
    my, sy = motor(CY, NY, -101.9)
    # 너트: 옛 T8 너트가 판에 닿은 면·몸 방향을 그대로
    plates = ob("212_beam_plates")[0]; cplates = ob("206_carriage_plates")[0]
    xn = [s for s in plates.Shape.Solids if s.BoundBox.XLength < 4][0]
    cp = [s for s in cplates.Shape.Solids if s.BoundBox.YLength < 4 and abs(s.BoundBox.Center.y + 45.5) < 1][0]
    on = ob("225_x_nut_T8")[0]; nb = on.Shape.BoundBox
    # XN x 87.4~90.4: 옛 너트 x 83.9~98.9 → 플랜지는 −x 쪽 (x 87.4 면), 몸은 판을 지나 +x
    x0 = xn.BoundBox.XMin
    ux, wx = new_nut(on, CX, V(1, 0, 0), x0 - 3.18, x0, x0, x0 + 6.35)
    on.Label = "225_x_nut_POM (LM-NK1134 POM 플랜지 너트 Ø19.05 — 같이 옴, XN −x 면, M3 × 8 3 + 너트)"
    oy = ob("224_y_nut_T8")[0]
    y0 = cp.BoundBox.YMax
    uy, wy = new_nut(oy, CY, V(0, 1, 0), y0, y0 + 3.18, y0 + 3.18, y0 + 9.53)
    oy.Label = "224_y_nut_POM (LM-NK1134 POM 플랜지 너트 Ø19.05 — 같이 옴, CP +y 면, M3 × 8 3 + 너트)"
    rep["old_nut_x"] = [round(nb.XMin, 1), round(nb.XMax, 1)]
    # 판 구멍
    newx = replate(xn, CX, V(1, 0, 0), ux, wx)
    plates.Shape = Part.makeCompound([newx if s.isSame(xn) else s for s in plates.Shape.Solids])
    newc = replate(cp, CY, V(0, 1, 0), uy, wy)
    cplates.Shape = Part.makeCompound([newc if s.isSame(cp) else s for s in cplates.Shape.Solids])
    add = [("215_x_stepper_LM-NK1134 (모터뱅크 LM-NK1134 28각 외부 스크류형 2상 1.8° 0.75 A — 몸 28 × 28 × 34, 스크류 Tr5 × 2 132 일체, 구매)", mx),
           ("214_x_lead_screw_Tr5 (LM-NK1134 축 = 나사 Ø5 리드 2 × 132 — 모터와 한 몸)", sx),
           ("209_y_stepper_LM-NK1134 (모터뱅크 LM-NK1134 28각 외부 스크류형 2상 1.8° 0.75 A — 몸 28 × 28 × 34, 스크류 132 일체, 구매, X와 같이 움직임)", my),
           ("208_y_lead_screw_Tr5 (LM-NK1134 축 = 나사 Ø5 리드 2 × 132 — 모터와 한 몸)", sy)]
    for lab, shp in add:
        n = d.addObject("Part::Feature", "LM_%d" % len(d.Objects)); n.Shape, n.Label = shp, lab
    for o in ob("153b_stepper_bolts_M2.6"):
        o.Label = o.Label.replace("NK1140", "LM-NK1134").replace("M2.6 × 6", "M2.6 × 6 [추측 — 같은 28각]")
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
    XY = os.path.join(HERE, "print", "xy")
    for sl, fn, ax in ((newx, "XN_X너트판_알루미늄3T.dxf", ("y", "z")), (newc, "CP_캐리지판_알루미늄3T.dxf", ("x", "z"))):
        bb = sl.BoundBox
        f = max([x for x in sl.Faces if x.Surface.TypeId == "Part::GeomPlane"], key=lambda x: x.Area)
        g = lambda p: (getattr(p, ax[0]) - getattr(bb, ax[0].upper() + "Min"), getattr(p, ax[1]) - getattr(bb, ax[1].upper() + "Min"))
        ents = []
        for e in f.Edges:
            cv = e.Curve
            if "Circle" in cv.TypeId and e.isClosed():
                cc = g(cv.Center); ents.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (cc[0], cc[1], cv.Radius)); continue
            pts = [g(p) for p in e.discretize(Deflection=0.02)]
            for a, z in zip(pts[:-1], pts[1:]):
                ents.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (a[0], a[1], z[0], z[1]))
        open(os.path.join(XY, fn), "w", encoding="ascii").write(
            "0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(ents) + "\n0\nENDSEC\n0\nEOF\n")
        rep[fn] = len(ents)
    App.closeDocument(d.Name)
    every = []
    for fdoc in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, fdoc + ".FCStd"), True)
        every += [(fdoc[:2] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    CH = ("215_x_stepper", "209_y_stepper", "214_x_lead", "208_y_lead", "224_y_nut", "225_x_nut", "212_beam_plates", "206_carriage_plates")
    ok = (("215_x", "217_x"), ("209_y", "211_y"), ("153b", "215_x"), ("153b", "209_y"), ("214_x", "215_x"), ("208_y", "209_y"),
          ("214_x", "225_x"), ("208_y", "224_y"), ("225_x", "212_beam_plates"), ("224_y", "206_carriage_plates"),
          ("214_x", "217_x"), ("208_y", "211_y"), ("214_x", "212_beam_plates"), ("208_y", "206_carriage_plates"),
          ("212_beam", "212_beam"), ("206_carriage", "206_carriage"), ("212_beam_plates", "222"), ("212_beam_plates", "207"),
          ("206_carriage_plates", "221"), ("206_carriage_plates", "205"), ("206_carriage_plates", "202"), ("212_beam_plates", "211_y_motor_st"),
          ("212_beam_plates", "227y"), ("206_carriage_plates", "203"))
    seen = set()
    for la, sa in [(l, x) for l, x in every if l.split(" ", 1)[1].startswith(CH)]:
        for lb, sb in every:
            if la == lb or (lb, la) in seen:
                continue
            ta, tb = la.split(" ", 1)[1], lb.split(" ", 1)[1]
            if any(ta.startswith(p) and tb.startswith(q) or ta.startswith(q) and tb.startswith(p) for p, q in ok):
                continue
            if sa.BoundBox.intersect(sb.BoundBox):
                v = sa.common(sb).Volume
                if v > 0.05:
                    rep["hits"].append([la[:45], lb[:45], round(v, 1)]); seen.add((la, lb))
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_xy_lm1134.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
