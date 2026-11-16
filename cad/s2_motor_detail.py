# -*- coding: utf-8 -*-
"""LM-NK1134 모터 모양을 판매처 도면·사진대로 (서현 11/16 18:47 "캐드도 확실히 수정해", CAP-AI-62)
  몸 28 × 28 × 34, 긴 모서리 깎기 2.5 [추측 — NEMA11 보통 모양], 앞 턱 Ø22 × 2, 앞면 나사 구멍 4 × Ø2.6 깊이 4 (23 × 23),
  앞 덮개·뒤 덮개 (두께 4, 몸보다 0.3 작게) 사이 적층 몸, 뒤쪽 옆면 전선 단자 12 × 6 × 8 [추측 — 사진에 뒤 옆으로 선이 나옴]
  자리·크기는 그대로라 판·나사와 맞춤은 안 바뀜. X는 단자를 아래(−z, 레일 반대), Y는 +x 쪽.
한 번만 (다시는 split/S2_마킹부_before_md.FCStd에서). freecad.exe cad/s2_motor_detail.py (cwd = cad) → split/S2, split/_motor_detail.json"""
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

    def cbox(x0, x1, y0, y1, z0, z1, dirv, c):     # 축(dirv)과 나란한 모서리 4개를 c만큼 깎은 상자
        bx = box(x0, x1, y0, y1, z0, z1)
        es = [e for e in bx.Edges if abs(abs((e.Vertexes[1].Point - e.Vertexes[0].Point).normalize().dot(dirv)) - 1) < 1e-6]
        return bx.makeChamfer(c, es)

    def body(b0, b1, ax, other):          # ax = 'x' 또는 'y' (축), 앞·뒤 덮개 4 + 가운데 적층 (0.3 작게)
        lo, hi = min(b0, b1), max(b0, b1)
        if ax == "x":
            (y0, y1), (z0, z1) = other; dv = V(1, 0, 0)
            mk = lambda a0, a1, s, c: cbox(a0, a1, y0 + s, y1 - s, z0 + s, z1 - s, dv, c)
        else:
            (x0, x1), (z0, z1) = other; dv = V(0, 1, 0)
            mk = lambda a0, a1, s, c: cbox(x0 + s, x1 - s, a0, a1, z0 + s, z1 - s, dv, c)
        return mk(lo, lo + 4, 0, 2.5).fuse(mk(lo + 4, hi - 4, 0.3, 2.2)).fuse(mk(hi - 4, hi, 0, 2.5)).removeSplitter()

    # X: 몸 x 160~194, y −79~−51, z 411~439, 앞면 x 160 (나사 −x)
    bx = body(160.0, 194.0, "x", ((-79.0, -51.0), (411.0, 439.0)))
    bx = bx.fuse(cyl(11.0, 2.0, V(158.0, -65.0, 425.0), V(1, 0, 0)))
    for a in (-11.5, 11.5):
        for e in (-11.5, 11.5):
            bx = bx.cut(cyl(1.3, 4.0, V(160.0, -65.0 + a, 425.0 + e), V(1, 0, 0)))
    bx = bx.fuse(box(182.0, 194.0, -71.0, -59.0, 403.0, 411.0)).removeSplitter()
    # Y: 몸 y −135.9~−101.9, x 87.4~115.4, z 439~467, 앞면 y −101.9 (나사 +y)
    by = body(-135.9, -101.9, "y", ((87.4, 115.4), (439.0, 467.0)))
    by = by.fuse(cyl(11.0, 2.0, V(101.4, -101.9, 453.0), V(0, 1, 0)))
    for a in (-11.5, 11.5):
        for e in (-11.5, 11.5):
            by = by.cut(cyl(1.3, 4.0, V(101.4 + a, -105.9, 453.0 + e), V(0, 1, 0)))
    by = by.fuse(box(115.4, 123.4, -135.9, -123.9, 447.0, 459.0)).removeSplitter()
    ox = ob("215_x_stepper_LM-NK1134")[0]; ox.Shape = bx
    oy = ob("209_y_stepper_LM-NK1134")[0]; oy.Shape = by
    for o in (ox, oy):
        o.Label = o.Label.replace("몸 28 × 28 × 34,", "몸 28 × 28 × 34 (모서리 깎기·앞뒤 덮개·뒤 옆 전선 단자),")
    rep["x"] = [round(v, 1) for v in (bx.BoundBox.XMin, bx.BoundBox.XMax, bx.BoundBox.ZMin, bx.BoundBox.ZMax)]
    rep["y"] = [round(v, 1) for v in (by.BoundBox.XMin, by.BoundBox.XMax, by.BoundBox.YMin, by.BoundBox.YMax)]
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
    every = []
    for fdoc in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, fdoc + ".FCStd"), True)
        every += [(fdoc[:2] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    ok = (("215_x", "217_x"), ("209_y", "211_y"), ("153b", "215_x"), ("153b", "209_y"), ("214_x", "215_x"), ("208_y", "209_y"))
    for la, sa in [(l, x) for l, x in every if l.split(" ", 1)[1].startswith(("215_x_stepper", "209_y_stepper"))]:
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
json.dump(rep, open(os.path.join(OUT, "_motor_detail.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
