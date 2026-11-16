# -*- coding: utf-8 -*-
"""마킹실 프린트 3개 잇기 (서현 11/17 00:32 "너가 제안하는 데로 … 나사 사이즈 통일", CAP-AI-62)
  상자 300: y만 ±19 → ±24 (lift_v2 BOXD half_y), ±y 면 귀 나사 밑구멍 Ø2.5 깊이 6 4개 (x 39·71, z 376.5)
  112·176: 상자 ±y 면에 겹치는 귀 (두께 3, 13 높이) — 문판 도는 자리(문판 면 x 30·80, 경첩 둘레 반지름 27.5)를 피해 x 방향 나사 대신 y 방향
           176 −y 귀는 몸통(y −10)까지 다리로 이음
  나사: M3 × 8 냄비 태핑 4 (격자판 300s와 같은 나사)
한 번만 — 다시는 split/S2_마킹부_before_join.FCStd에서. GUI FreeCAD에서 exec 가능 (os._exit 없음) → split/_marking_join.json"""
import json, os, sys, shutil, traceback
import FreeCAD as App, Part
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else r"C:\capstone\-capstone-project-repo\cad"
OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
rep = dict(hits=[])
try:
    import importlib, lift_v2 as L, lift_v3 as L3
    importlib.reload(L)
    V = App.Vector
    box, cyl = L.box, L.cyl
    P = os.path.join(OUT, "S2_마킹부.FCStd")
    shutil.copy(P, os.path.join(OUT, "S2_마킹부_before_join.FCStd"))
    d = App.openDocument(P, True)
    ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]
    mw = App.Matrix(); mw.move(L3.WORLD)
    bx = ob("300_marking_box")[0]
    bx.Shape = L.marking_box().transformed(mw)
    Z0, Z1, ZC = 370.0, 383.0, 376.5
    HY = L.BOXD["half_y"]
    ears = {"112": [], "176": []}
    for x, y in L.BOXD["ear_holes"]:
        gx, sy = 55.0 + x, (1 if y > 0 else -1)
        e = box(gx - 3.5, gx + 3.5, min(sy * HY, sy * (HY + 3)), max(sy * HY, sy * (HY + 3)), Z0, Z1)
        if x < 0:                                   # 112: 귀가 112 면(x 36)까지
            e = e.fuse(box(36.0 - 0.5, gx + 3.5, min(sy * HY, sy * (HY + 3)), max(sy * HY, sy * (HY + 3)), Z0, Z1))
            k = "112"
        else:                                       # 176: 귀가 176 면(x 74)까지, −y는 몸통 y −10까지 다리
            e = e.fuse(box(gx - 3.5, 74.5, min(sy * HY, sy * (HY + 3)), max(sy * HY, sy * (HY + 3)), Z0, Z1))
            if sy < 0:
                e = e.fuse(box(74.0, 77.0, -(HY + 3), -9.5, Z0, Z1))
            k = "176"
        e = e.cut(cyl(1.7, 6, V(gx, sy * (HY + 4), ZC), V(0, -sy, 0)))
        ears[k].append(e)
    h2, h6 = ob("112_entry_iso_gate_housing")[0], ob("176_release_gate_housing")[0]
    s2 = h2.Shape
    for e in ears["112"]:
        s2 = s2.fuse(e)
    h2.Shape = s2.removeSplitter()
    s6 = h6.Shape
    for e in ears["176"]:
        s6 = s6.fuse(e)
    h6.Shape = s6.removeSplitter()
    scr = [L.pan(V(55.0 + x, (1 if y > 0 else -1) * (HY + 3), ZC), V(0, -(1 if y > 0 else -1), 0), 3.0, 8.0) for x, y in L.BOXD["ear_holes"]]
    for o in ob("300e_ear_screws"):
        d.removeObject(o.Name)
    n = d.addObject("Part::Feature", "EarScr"); n.Shape = Part.makeCompound(scr)
    n.Label = "300e_ear_screws (M3 × 8 냄비 태핑 4 — 112·176 귀 → 상자 ±y 면, 격자판 300s와 같은 나사, 구매)"
    bx.Label = bx.Label.split(" (")[0] + " (마킹실 상자 — 3D 프린트 (학교), 바깥 38 × 48 × 18 (11/17 y ±24로 넓힘: 112·176 귀 M3 태핑 4), Ø33 방, 옆 Ø13 3, 혀 → 세운 막대 M5 2, 윗면 격자판 M3 태핑 4)"
    d.recompute(); d.save()
    for o in (bx, h2, h6):
        rep[o.Label[:4]] = dict(valid=o.Shape.isValid(), solids=len(o.Shape.Solids), vol=round(o.Shape.Volume / 1000, 2),
                               bb=[round(v, 1) for v in (o.Shape.BoundBox.XMin, o.Shape.BoundBox.XMax, o.Shape.BoundBox.YMin, o.Shape.BoundBox.YMax, o.Shape.BoundBox.ZMin, o.Shape.BoundBox.ZMax)])
    App.closeDocument(d.Name)
    # 정지 겹침: 바뀐 것 ↔ S1·S2·S3
    every = []
    for f in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        every += [(f[:2] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    CH = ("300_marking_box", "112_entry_iso_gate_housing", "176_release_gate_housing", "300e_ear")
    ok = (("300_marking_box", "300"), ("300_marking_box", "301"), ("300_marking_box", "304"), ("300_marking_box", "307"), ("300_marking_box", "308"),
          ("300e", "300_marking_box"), ("300e", "112_entry_iso"), ("300e", "176_release_gate_housing"),
          ("112_entry_iso", "112"), ("112_entry_iso", "170"), ("112_entry_iso", "110"), ("112_entry_iso", "172"),
          ("176_release", "176"), ("176_release", "174_release"), ("176_release", "112s"))
    for la, sa in every:
        ta = la.split(" ", 1)[1]
        if not ta.startswith(CH):
            continue
        for lb, sb in every:
            tb = lb.split(" ", 1)[1]
            if la == lb or (tb.startswith(CH) and lb < la):
                continue
            if any(ta.startswith(p) and tb.startswith(q) or ta.startswith(q) and tb.startswith(p) for p, q in ok):
                continue
            if sa.BoundBox.intersect(sb.BoundBox):
                v = sa.common(sb).Volume
                if v > 0.05:
                    rep["hits"].append([ta[:40], tb[:40], round(v, 1)])
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_marking_join.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False))
