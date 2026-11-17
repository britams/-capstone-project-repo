# -*- coding: utf-8 -*-
"""XY 판 끝단 거리 고침 (서현 11/17 17:27 '1번(탭·접시)은 제대로 해', CAP-AI-62)
xy_plates_step_meviy.py 구멍 표에서 접시·구멍이 판 끝에 1 mm보다 가까움 (meviy 가이드 p.12 '끝단 ↔ 구멍 1 mm 이상'):
  YA·YB  SC8UU M4 접시 Ø9.1 (구멍 x 94.4)이 판 −x 끝(x 90.4)을 0.57 mm 넘어 깎임, 위 구멍은 위 끝까지 0.43
         → −x 쪽에 SC8UU 발과 같은 x 88.4까지 혀(z 466.5~, XN 위 끝 466 위), 위 끝 +1.5
  YM     M3 접시 Ø6.9 (아래)가 아래 끝까지 0.55 → 아래 끝 −1.5
  HV     M3 접시 Ø6.9 (P 클립 위쪽)가 위 끝을 0.95 넘어 깎임 → 위 끝 +2.5
  SV     SG90 귀 M2 Ø2.2 · M3 구멍이 위·아래 끝까지 0~0.96 → 위·아래 끝 +1.5
판을 늘린 뒤 원래 접시 원뿔·구멍을 다시 깎음 (늘린 살이 구멍을 메우지 않게). 모양 말고는 안 바꿈.
한 번만 — 다시는 split/S2_마킹부_before_edge.FCStd에서. freecad.exe 따로 (cwd = cad) → split/_xy_edge.json"""
import json, os, shutil, traceback, glob, time
HERE = os.getcwd(); OUT = os.path.join(HERE, "split")
rep = {}
try:
    import FreeCAD as App, Part
    V = App.Vector
    box = lambda x0, x1, y0, y1, z0, z1: Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))

    def extend(s, boxes):
        cones, cyls = [], []
        for f in s.Faces:
            st = f.Surface.TypeId
            circ = [e for e in f.Edges if "Circle" in e.Curve.TypeId and e.isClosed()]
            if "Cone" in st and len(circ) == 2:
                big, small = sorted(circ, key=lambda e: -e.Curve.Radius)
                cones.append((big.Curve.Radius, small.Curve.Radius, big.Curve.Center, small.Curve.Center))
            elif "Cylinder" in st and circ and f.Surface.Radius < 6:
                cyls.append((f.Surface.Radius, circ[0].Curve.Center, f.Surface.Axis))
        n = s
        for b in boxes:
            n = n.fuse(b)
        for R, r, cR, cr in cones:
            dv = cr - cR; h = dv.Length; dv.normalize()
            n = n.cut(Part.makeCone(R, r, h, cR, dv)).cut(Part.makeCylinder(R, 3, cR - dv * 3, dv))
        for r, c, a in cyls:
            n = n.cut(Part.makeCylinder(r, 30, c - a * 15, a))
        n = n.removeSplitter()
        return Part.Solid(n.Solids[0]) if len(n.Solids) == 1 else n, len(cones), len(cyls)

    P, B = os.path.join(OUT, "S2_마킹부.FCStd"), os.path.join(OUT, "S2_마킹부_before_edge.FCStd")
    shutil.copy(B, P) if os.path.exists(B) else shutil.copy(P, B)
    d = App.openDocument(P, True)
    ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)][0]
    changed = {}
    # YA · YB (212 묶음)
    o = ob("212_beam_plates"); sols = list(o.Shape.Solids); new = []
    for s in sols:
        b = s.BoundBox
        if b.XLength < 4:                       # XN 그대로
            new.append(s); continue
        nm = "YA" if b.Center.y < 0 else "YB"
        s2, nc, ny = extend(s, [box(b.XMin - 2.0, b.XMin, b.YMin, b.YMax, 466.5, b.ZMax + 1.5), box(b.XMin, b.XMax, b.YMin, b.YMax, b.ZMax, b.ZMax + 1.5)])
        new.append(s2); changed[nm] = (s2, nc, ny)
    o.Shape = Part.makeCompound(new)
    # YM
    o = ob("211_y_motor_plate"); s = o.Shape.Solids[0]; b = s.BoundBox
    s2, nc, ny = extend(s, [box(b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin - 1.5, b.ZMin)])
    o.Shape = s2; changed["YM"] = (s2, nc, ny)
    # HV
    o = ob("202_holder_plate_HV"); s = o.Shape.Solids[0]; b = s.BoundBox
    s2, nc, ny = extend(s, [box(b.XMin, b.XMax, b.YMin, b.YMax, b.ZMax, b.ZMax + 2.5)])
    o.Shape = s2; changed["HV"] = (s2, nc, ny)
    # SV (206 묶음의 세 번째: x ≈ 101.6)
    o = ob("206_carriage_plates"); sols = list(o.Shape.Solids); new = []
    for s in sols:
        b = s.BoundBox
        if b.XLength < 4 and b.Center.x > 95:
            s2, nc, ny = extend(s, [box(b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin - 1.5, b.ZMin), box(b.XMin, b.XMax, b.YMin, b.YMax, b.ZMax, b.ZMax + 1.5)])
            new.append(s2); changed["SV"] = (s2, nc, ny)
        else:
            new.append(s)
    o.Shape = Part.makeCompound(new)
    d.recompute()
    for k, (s2, nc, ny) in changed.items():
        bb = s2.BoundBox
        rep[k] = dict(valid=s2.isValid(), solids=len(s2.Solids), cones=nc, holes=ny, bbox=[round(x, 2) for x in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)])
    d.save()
    # 정지 겹침: 고친 판 ↔ 전부 (같은 판 묶음·그 판에 박힌 나사는 0.5 mm³ 넘을 때만)
    every = []
    for ff in ("S1_급이부", "S2a_바닥구동", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, ff + ".FCStd"), True)
        every += [(o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull()]
        App.closeDocument(dd.Name)
    every += [(o.Label, o.Shape.copy()) for o in d.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull()]
    own = {"YA": "212_beam_plates", "YB": "212_beam_plates", "YM": "211_y_motor_plate", "HV": "202_holder_plate_HV", "SV": "206_carriage_plates"}
    hits = []
    for k, (s2, _, _) in changed.items():
        for lb, sb in every:
            if lb.startswith((own[k], "REF_", "190_")):
                continue
            try:
                if s2.BoundBox.intersect(sb.BoundBox):
                    v = s2.common(sb).Volume
                    if v > 0.05:
                        hits.append([k, lb[:50], round(v, 2)])
            except Exception:
                pass
    rep["hits"] = hits
    App.closeDocument(d.Name)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_xy_edge.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
