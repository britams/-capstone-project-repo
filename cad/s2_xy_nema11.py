# -*- coding: utf-8 -*-
"""XY 모터 28BYJ-48 → 28각(NEMA11) 2상 스텝모터 모터뱅크 NK1140 2개 (서현 11/16 "제어 빠르고 정밀한 것으로", 예산 15만, 국내, CAP-AI-62)
  치수 [가능성 높음 — 모터뱅크 NK1140 도면]: 몸 28 × 28 × 40, 앞 턱 Ø22 × 2, 나사 구멍 23 × 23 (M2.6), 축 끝까지 12.
  축 지름 Ø5 [추측 — 도면 글씨가 흐림, NEMA11 보통 값] → 커플링 5→8 그대로.
  NEMA17(42각)은 X 모터 윗면이 +x 갠트리 레일(z 440)에 6 mm 겹쳐서 안 됨 (11/16 CAD).
  모터판 217·211: 옛 28BYJ 귀·축 구멍 메우고, 턱 구멍 Ø22.5 + M2.6 구멍 Ø2.9 4 — 알루미늄 3 mm 레이저 그대로.
한 번만 (다시는 split/S2_마킹부_before_n11.FCStd에서). freecad.exe cad/s2_xy_nema11.py (cwd = cad) → split/S2, print/xy/{YM,217}_*.dxf, split/_xy_nema11.json"""
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
    H, P, PT, SL, SD = 40.0, 22.0, 2.0, 12.0, 5.0      # 몸 길이, 턱 Ø, 턱 두께, 축 (몸 앞면부터), 축 Ø

    def motor(c, n, face):          # c = 축 중심, n = 축이 나가는 방향 (단위), face = 몸 앞면 위치 (축 방향 좌표)
        # 몸: 앞면에서 -n 쪽으로 40
        m = Part.makeBox(28, 28, H, V(-14, -14, -H))
        m = m.fuse(Part.makeCylinder(P / 2, PT, V(0, 0, 0))).fuse(Part.makeCylinder(SD / 2, SL, V(0, 0, 0)))
        rot = App.Rotation(V(0, 0, 1), n)
        m.Placement = App.Placement(c + n * (face - c.dot(n)), rot)
        return m.removeSplitter()

    def plate_holes(o, c, n, keep):          # 판 다시: 상자 + 남길 구멍 (keep: [(중심, 반지름)]) + 턱·M2.6
        b = o.Shape.BoundBox
        s = box(b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax)
        # 판 두께 방향 = n
        t0 = V(b.XMin, b.YMin, b.ZMin).dot(n) - 2 if n.dot(V(1, 1, 1)) > 0 else V(b.XMax, b.YMax, b.ZMax).dot(n) - 2
        def hole(p, r):
            q = p + n * (t0 - p.dot(n))
            return cyl(r, 10, q, n)
        for p, r in keep:
            s = s.cut(hole(p, r))
        s = s.cut(hole(c, 11.25))
        u = V(0, 1, 0) if abs(n.y) < 0.5 else V(1, 0, 0)
        w = n.cross(u)
        for a in (-11.5, 11.5):
            for e in (-11.5, 11.5):
                s = s.cut(hole(c + u * a + w * e, 1.45))
        return s.removeSplitter()

    def bolts(c, n, face, u):      # M2.6 × 6 냄비머리 4 — 판 반대쪽(커플링 쪽)에서
        w = n.cross(u); out = []
        for a in (-11.5, 11.5):
            for e in (-11.5, 11.5):
                p = c + u * a + w * e
                p = p + n * (face - p.dot(n))           # 몸 앞면 위치
                out.append(cyl(1.3, 6, p - n * 3, n))   # 몸 속 3 + 판 3
                out.append(cyl(2.25, 1.8, p - n * 4.8, n))  # 머리 (판 반대 면 위)
        return Part.makeCompound(out)

    # 지울 것: 28BYJ 몸·축 (STEP), 귀 볼트
    for p in ("209_y_stepper_28BYJ48", "209r_y_motor_shaft", "215_x_stepper_28BYJ48", "215r_x_motor_shaft", "153b_stepper_ear_bolts", "153n_stepper_ear_nuts"):
        for o in ob(p):
            d.removeObject(o.Name)
    # X: 축 y −65 · z 425, −x 쪽으로, 판 217 x 157~160 → 몸 앞면 x 160 (판 +x 면), 축은 −x
    cx, nx = V(0, -65.0, 425.0), V(-1, 0, 0)
    px = ob("217_x_motor_plate")[0]
    def old_holes(o, r):            # 판에 있던 구멍 (반지름 r) 가운데 — 앞뒤 면 원 2개는 하나로
        out = []
        for e in o.Shape.Edges:
            if "Circle" in e.Curve.TypeId and abs(e.Curve.Radius - r) < 0.05:
                c = V(e.Curve.Center.x, e.Curve.Center.y, e.Curve.Center.z)
                if not any((c - q).Length < 3.5 for q in out):
                    out.append(c)
        return out
    m5 = old_holes(ob("217_x_motor_plate")[0], 2.75)
    rep["x_m5"] = [[round(c.y, 1), round(c.z, 1)] for c in m5]
    px.Shape = plate_holes(px, V(158.5, -65.0, 425.0), V(1, 0, 0), [(V(158.5, c.y, c.z), 2.75) for c in m5])
    px.Label = "217_x_motor_plate (알루미늄 판 3 mm 레이저 — +x 레일 −x 옆면에 바로, NK1140 턱 Ø22.5 · M2.6 Ø2.9 4 · M5 Ø5.5 2)"
    mx = motor(V(160, -65.0, 425.0), V(-1, 0, 0), -160.0)
    # Y: 축 x 101.4 · z 453, +y 쪽으로, 판 211 y −101.9~−98.9 → 몸 앞면 y −101.9, 축 +y
    py = ob("211_y_motor_plate")[0]
    so = old_holes(py, 1.7)
    rep["y_standoffs"] = [[round(c.x, 1), round(c.z, 1)] for c in so]
    py.Shape = plate_holes(py, V(101.4, -100.4, 453.0), V(0, 1, 0), [(V(c.x, -100.4, c.z), 1.7) for c in so])
    py.Label = "211_y_motor_plate (알루미늄 3 mm 레이저 — NK1140 턱 Ø22.5 · M2.6 Ø2.9 4 · 기둥 Ø3.4 3)"
    my = motor(V(101.4, -101.9, 453.0), V(0, 1, 0), -101.9)
    add = [("215_x_stepper_NK1140 (모터뱅크 NK1140 28각 2상 1.8° 0.95 A — 몸 28 × 28 × 40, 축 Ø5 [추측] × 12, 구매)", mx),
           ("209_y_stepper_NK1140 (모터뱅크 NK1140 28각 2상 1.8° 0.95 A — 몸 28 × 28 × 40, 축 Ø5 [추측] × 12, 구매, X와 같이 움직임)", my),
           ("153b_stepper_bolts_M2.6 (NK1140 앞 나사 M2.6 × 6 냄비머리 4 — 판 반대쪽에서, 구매) [fixed]", bolts(V(160, -65.0, 425.0), V(1, 0, 0), 160.0, V(0, 1, 0))),
           ("153b_stepper_bolts_M2.6 (NK1140 앞 나사 M2.6 × 6 냄비머리 4 — 판 반대쪽에서, 구매) [marker]", bolts(V(101.4, -101.9, 453.0), V(0, -1, 0), 101.9, V(1, 0, 0)))]
    for lab, shp in add:
        n = d.addObject("Part::Feature", "N11_%d" % len(d.Objects)); n.Shape, n.Label = shp, lab
    rep["mx"] = [round(v, 1) for v in (mx.BoundBox.XMin, mx.BoundBox.XMax, mx.BoundBox.ZMin, mx.BoundBox.ZMax)]
    rep["my"] = [round(v, 1) for v in (my.BoundBox.YMin, my.BoundBox.YMax, my.BoundBox.ZMin, my.BoundBox.ZMax)]
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
    # DXF 2장
    XY = os.path.join(HERE, "print", "xy")
    for o, fn, ax in ((px, "217_X모터판_알루미늄3T.dxf", ("y", "z")), (py, "YM_Y모터판_알루미늄3T.dxf", ("x", "z"))):
        sl = o.Shape.Solids[0]; bb = sl.BoundBox
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
    CH = ("215_x_stepper", "209_y_stepper", "153b_stepper_bolts", "217_x_motor_plate", "211_y_motor_plate")
    ok = (("215_x", "217_x"), ("209_y", "211_y"), ("153b", "217_x"), ("153b", "211_y"), ("153b", "215_x"), ("153b", "209_y"),
          ("215_x", "216_x_coupling"), ("209_y", "210_y_coupling"), ("217_x", "217s"), ("211_y", "211_y_motor_standoffs"), ("217_x", "100"))
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
json.dump(rep, open(os.path.join(OUT, "_xy_nema11.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
