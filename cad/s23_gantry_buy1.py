# -*- coding: utf-8 -*-
"""갠트리 '전부 사는 것' 1단계 (서현 11/15 12:51 "전부 사는것으로 바꿔. 시제품을 뽑지말고", CAP-AI-62)
  고정 쪽만: 218 X 봉 받침(프린트) → SK8 ×4 (삼익 표 [확실]: 중심 높이 h 20, 폭 42, 두께 14, 전체 32.8, 볼트 M5 간격 32),
            217 X 모터판(프린트) → 알루미늄 판 3 mm (레이저) + L 브래킷 DCB 2025,
            SK8 중심 20을 맞추려 갠트리 단(z 452~472의 레일·브래킷·나사) 전체를 12 mm 내림 → X 봉 z 480 그대로 (끝 블록·Y·마커 높이 안 바뀜)
            X 봉 Ø8 200: x −25 ~ 175 (양 끝 SK8 안), 11/15 s2_stdlen의 +x 늘림 대신
  순서: s2_doors_v3 → s2_stdlen → (이것) → full_merge → s2_motion_v3_check
  freecad.exe cad/s23_gantry_buy1.py (cwd = cad) → split/S2·S3 고쳐 씀, split/_gantry_buy1.json"""
import json, os, sys, traceback
HERE = os.getcwd(); OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
DZ = -12.0
rep = dict(moved=[], hits=[])
try:
    import FreeCAD as App, Part
    import lift_v2 as L
    V = App.Vector
    box, cyl = L.box, L.cyl
    # --- S3: 갠트리 단을 내림 (z 446~478 안에 다 들어가는 고체만)
    s3 = App.openDocument(os.path.join(OUT, "S3_프레임회로.FCStd"))
    for o in s3.Objects:
        if not o.TypeId.startswith("Part::") or o.Shape.isNull():
            continue
        sols = o.Shape.Solids
        if not sols:
            continue
        inside = [s for s in sols if s.BoundBox.ZMin >= 446 and s.BoundBox.ZMax <= 478]
        if not inside:
            continue
        keep = [s for s in sols if s not in inside]
        moved = []
        for s in inside:
            t = s.copy(); t.translate(V(0, 0, DZ)); moved.append(t)
        o.Shape = Part.makeCompound(keep + moved) if (keep or len(moved) > 1) else moved[0]
        rep["moved"].append([o.Label[:50], len(inside), len(sols)])
    s3.save()
    # --- S2: 218 → SK8, 217 → 판 + 브래킷, 213 다시
    s2 = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    ob = lambda p: [o for o in s2.Objects if o.Label.startswith(p)]
    for p in ("218_rod_supports", "217_x_motor_plate"):
        for o in ob(p):
            s2.removeObject(o.Name)
    RZ, YA, YB = 480.0, -65.0, 57.0
    rail_top = 472.0 + DZ
    def sk8(xc, yc):
        z0 = rail_top
        b = box(xc - 7, xc + 7, yc - 21, yc + 21, z0, z0 + 6).fuse(box(xc - 7, xc + 7, yc - 10.5, yc + 10.5, z0, z0 + 32.8))
        return b.cut(cyl(4.0, 16, V(xc - 8, yc, z0 + 20), V(1, 0, 0))).cut(cyl(2.75, 8, V(xc, yc - 16, z0 - 1))).cut(cyl(2.75, 8, V(xc, yc + 16, z0 - 1))).removeSplitter()
    sks, scr = [], []
    for xc in (-18.0, 170.0):
        for yc in (YA, YB):
            sks.append(sk8(xc, yc))
            for sy in (-16, 16):
                scr.append(L.pan(V(xc, yc + sy, rail_top + 6), V(0, 0, -1), 5.0, 10.0))
                scr.append(box(xc - 5, xc + 5, yc + sy - 3, yc + sy + 3, rail_top - 6, rail_top - 2))     # 20시리즈 스프링너트
    add = []
    add.append(("218_rod_supports_SK8 (SK8 샤프트 서포트 4 — 삼익 규격 h 20, 구매 / 갠트리 레일 위)", Part.makeCompound(sks), (0.55, 0.55, 0.6)))
    add.append(("218s_SK8_bolts (M5 × 10 둥근머리 8 + 20시리즈 스프링너트 8, 구매)", Part.makeCompound(scr), (0.35, 0.35, 0.37)))
    for o in ob("213_x_rods"):
        o.Shape = cyl(4, 200, V(-25, YA, RZ), V(1, 0, 0)).fuse(cyl(4, 200, V(-25, YB, RZ), V(1, 0, 0)))
        o.Label = "213_x_rods (Ø8 × 200 규격 그대로, x −25~175 — 양 끝 SK8, 11/15)"
    # X 모터: 판 (x 142~145, 법선 x) — 옛 217과 같은 구멍 + 위 끝을 L 브래킷으로 +x 레일(x 160~180) 밑면에
    zx, M28 = 425.0, dict(ear_c=35.0, off=8.0, ear_hole=4.2)
    rail_bot = 452.0 + DZ
    xp0 = 142.0
    pl = box(xp0, xp0 + 3, YA - 22, YA + 22, 400, rail_bot - 0.5).cut(cyl(5.0, 5, V(xp0 - 1, YA, zx), V(1, 0, 0)))
    for sy in (-1, 1):
        pl = pl.cut(cyl(M28["ear_hole"] / 2, 5, V(xp0 - 1, YA + sy * M28["ear_c"] / 2, zx - M28["off"]), V(1, 0, 0)))
    for sy in (-1, 1):
        pl = pl.cut(cyl(2.75, 5, V(xp0 - 1, YA + sy * 12, rail_bot - 10), V(1, 0, 0)))
    add.append(("217_x_motor_plate (알루미늄 판 3 mm — 레이저 주문, 28BYJ 귀 Ø4.2 2·축 Ø10·브래킷 Ø5.5 2)", pl.removeSplitter(), (0.45, 0.6, 0.85)))
    brk = []
    for sy in (-1, 1):
        yc = YA + sy * 12
        brk.append(box(xp0 + 3, xp0 + 7, yc - 10, yc + 10, rail_bot - 20, rail_bot).fuse(box(xp0 + 3, xp0 + 28, yc - 10, yc + 10, rail_bot - 4, rail_bot)))
    add.append(("217b_x_motor_brackets (L 브래킷 DCB 2025 ×2 — 판 → +x 레일 밑면, 구매, 두께 4 [추측])", Part.makeCompound(brk), (0.55, 0.55, 0.6)))
    hw = []
    for sy in (-1, 1):
        yc = YA + sy * 12
        hw.append(L.pan(V(xp0 - 0.0, yc, rail_bot - 10), V(1, 0, 0), 5.0, 8.0))
        hw.append(box(xp0 + 7, xp0 + 11, yc - 4, yc + 4, rail_bot - 14, rail_bot - 6))
        hw.append(L.pan(V(xp0 + 21, yc, rail_bot - 4), V(0, 0, 1), 5.0, 8.0))
        hw.append(box(xp0 + 16, xp0 + 26, yc - 3, yc + 3, rail_bot + 2, rail_bot + 6))
    add.append(("217s_x_motor_screws (M5 × 8 + 너트 2 — 판·브래킷, M5 × 8 + 스프링너트 2 — 레일, 구매)", Part.makeCompound(hw), (0.35, 0.35, 0.37)))
    for lab, shp, col in add:
        n = s2.addObject("Part::Feature", "B1_%d" % len(s2.Objects))
        n.Shape, n.Label = shp, lab
        if App.GuiUp:
            n.ViewObject.ShapeColor = col
    s2.save()
    # 고정 겹침 검사: 새것·내린 것 ↔ 전부
    every = []
    for f in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        every += [(f[:2] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    probe = [(l, s) for l, s in every if l.split(" ", 1)[1].startswith(("218", "217", "213")) or any(l.split(" ", 1)[1].startswith(m[0][:12]) for m in rep["moved"])]
    ok_pairs = (("213", "218_rod"), ("213", "222"), ("218s", "218_rod"), ("218s", "100"), ("217s", "217"), ("217s", "100"), ("217b", "217_"), ("217s", "217b"),
                ("215", "217_"), ("214", "217_"), ("216", "217_"), ("153", "217_"), ("153", "215"))
    seen = set()
    for la, sa in probe:
        for lb, sb in every:
            if la == lb or (lb, la) in seen:
                continue
            a, b = la.split(" ", 1)[1], lb.split(" ", 1)[1]
            if any(a.startswith(p) and b.startswith(q) or a.startswith(q) and b.startswith(p) for p, q in ok_pairs):
                continue
            if a.startswith("100") and b.startswith("100"):
                continue
            if sa.BoundBox.intersect(sb.BoundBox):
                try:
                    v = sa.common(sb).Volume
                except Exception:
                    v = 0.0
                if v > 0.05:
                    rep["hits"].append([la[:45], lb[:45], round(v, 1)]); seen.add((la, lb))
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_gantry_buy1.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
