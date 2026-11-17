# -*- coding: utf-8 -*-
"""작은 ㄱ자 브래킷 4개 → 미스미 FALCS (L형 판금, 치수 지정) (서현 11/17 21~23시 '치수 제대로 있는 부품을 넣어', CAP-AI-62)
  ETTINGER 014.86.153 (15 × 15 × 폭 10, 해외)는 국내에 같은 크기가 없음. FALCS는 한쪽 다리 ≥ 20, 다른 쪽 ≥ 15, 폭 ≥ 10이라
  20 × 15 × 폭 10, SUS 1.0, 구멍 N3 (Ø3.5)로 하고 구멍은 지금 판에 뚫린 자리 그대로 → CP·SP·199a 판은 안 바꿈.
  캐리지 CP ↔ SP 2 (206_carriage_hardware 안): 옛 모델은 브래킷이 판 구멍(z 400·491)에서 4·2 mm 어긋나 있었음 → 구멍 가운데로 맞춤.
  캐리지 아래 브래킷은 구멍 가운데 z 400이면 폭 10이 z 395까지 내려와 움직일 때 G5 게이트(위 z 396.5)에 닿음 (움직임 검사 21 mm³)
  → CP·SP 판의 그 구멍을 z 403으로 올림 (브래킷 z 398~408, 게이트와 1.5), 나사·너트도 +3.
  그러면 SP 쪽 냄비머리(Ø5.6)가 z 405.8까지 올라와 SP −x 면을 미끄러지는 홀더 판 HV (밑 z 405)에 닿음
  → 그 1개만 M3 × 8 접시머리, SP −x 면에 접시 Ø6.9 90° (머리가 면과 같은 높이).
  접시가 SP 끝(y −40)에서 0.05 mm라 SP 쪽 구멍은 두 브래킷 다 y −36.5 → −34.5 (SP 끝에서 5.5, 접시 끝단 2.05) — 브래킷 15 다리 구멍 9.5.
  Pi 선반 PB ↔ PV 2 (199ab): 옛 모델 두께 2 → 1.
  20 mm로 늘릴 다리는 두 쪽을 다 해 보고 다른 부품에 안 닿는 쪽 (앞 순서 먼저).
한 번만 — 다시는 split/*_before_falcs.FCStd에서. freecad.exe 따로 (cwd = cad) → split/_falcs.json"""
import json, os, shutil, traceback
HERE = os.getcwd(); OUT = os.path.join(HERE, "split")
rep = {}
T, W, R = 1.0, 10.0, 1.75                                   # 두께, 폭, 구멍 반지름 (N3 = Ø3.5)
try:
    import FreeCAD as App, Part
    V = App.Vector
    box = lambda x0, x1, y0, y1, z0, z1: Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
    cyl = lambda c, a: Part.makeCylinder(R, 6, c - a * 3, a)
    docs = {}
    for f in ("S2_마킹부", "S3_프레임회로"):
        P, B = os.path.join(OUT, f + ".FCStd"), os.path.join(OUT, f + "_before_falcs.FCStd")
        shutil.copy(B, P) if os.path.exists(B) else shutil.copy(P, B)
        docs[f] = App.openDocument(P, True)
    ob = lambda d, p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)][0]
    s2, s3 = docs["S2_마킹부"], docs["S3_프레임회로"]

    SY = -34.5                                              # SP 쪽 구멍 y (옛 −36.5)
    # 캐리지: 꺾인 바깥 모서리 (x 90.15 = SP +x 면, y −44 = CP +y 면), CP 다리 +x 쪽 구멍 x 98, SP 다리 +y 쪽 구멍 y SY
    def carriage(zc, lcp, lsp):
        x0, y0, z0, z1 = 90.15, -44.0, zc - W / 2, zc + W / 2
        s = box(x0, x0 + lcp, y0, y0 + T, z0, z1).fuse(box(x0, x0 + T, y0, y0 + lsp, z0, z1))
        s = s.cut(cyl(V(98.0, y0, zc), V(0, 1, 0))).cut(cyl(V(x0, SY, zc), V(1, 0, 0)))
        return Part.Solid(s.removeSplitter().Solids[0])

    # Pi 선반: 바깥 모서리 (y 67 = PV 안쪽 면, z 562 = PB 밑면), 가로 다리 −y 쪽 구멍 y 59.5, 세로 다리 −z 쪽 구멍 z 554
    def shelf(xc, lh, lv):
        x0, x1 = xc - W / 2, xc + W / 2
        s = box(x0, x1, 67.0 - lh, 67.0, 562.0 - T, 562.0).fuse(box(x0, x1, 67.0 - T, 67.0, 562.0 - lv, 562.0))
        s = s.cut(cyl(V(xc, 59.5, 562.0), V(0, 0, 1))).cut(cyl(V(xc, 67.0, 554.0), V(0, 1, 0)))
        return Part.Solid(s.removeSplitter().Solids[0])

    # 캐리지 아래 구멍 z 400 → 403: CP (y −47~−44)·SP (x 87.15~90.15) 판 구멍을 메우고 다시 뚫음, 그 나사·너트 +3
    ZB = 403.0
    o = ob(s2, "206_carriage_plates"); new = []
    for s in o.Shape.Solids:
        b = s.BoundBox
        if b.YLength < 4:                                   # CP
            s = s.fuse(Part.makeCylinder(1.7, b.YLength, V(98, b.YMin, 400), V(0, 1, 0))).cut(Part.makeCylinder(1.7, 10, V(98, b.YMin - 3, ZB), V(0, 1, 0)))
            s = Part.Solid(s.removeSplitter().Solids[0])
        elif b.XLength < 4 and b.Center.x < 95:             # SP (+ −x 면 접시)
            for zz in (400.0, 491.0):
                s = s.fuse(Part.makeCylinder(1.7, b.XLength, V(b.XMin, -36.5, zz), V(1, 0, 0)))
            for zz in (ZB, 491.0):
                s = s.cut(Part.makeCylinder(1.7, 10, V(b.XMin - 3, SY, zz), V(1, 0, 0)))
            s = s.cut(Part.makeCone(3.45, 1.7, 1.75, V(b.XMin, SY, ZB), V(1, 0, 0))).cut(Part.makeCylinder(3.45, 1, V(b.XMin - 1, SY, ZB), V(1, 0, 0)))
            s = Part.Solid(s.removeSplitter().Solids[0]); spx = b.XMin
        new.append(s)
    o.Shape = Part.makeCompound(new)
    o = ob(s2, "206_carriage_hardware"); hw = []; moved = 0
    for s in o.Shape.Solids:
        c = s.BoundBox.Center
        sp_side = abs(c.y + 36.5) < 1 and c.x < 96
        bottom = abs(c.z - 400) < 1.5
        if (bottom and abs(c.x - 98) < 1 and c.y < -39) or (sp_side and (bottom or abs(c.z - 491) < 1.5)):
            s = s.copy(); s.translate(V(0, SY + 36.5 if sp_side else 0, ZB - 400 if bottom else 0)); moved += 1
            if bottom and s.BoundBox.XMin < spx - 1:        # 아래 SP 쪽 냄비 나사 → 접시 M3 × 8 (머리 Ø6, 90°)
                s = Part.makeCone(3.0, 1.5, 1.5, V(spx, SY, ZB), V(1, 0, 0)).fuse(Part.makeCylinder(1.5, 8, V(spx, SY, ZB), V(1, 0, 0)))
                s = Part.Solid(s.removeSplitter().Solids[0]); rep["sp_flat_screw"] = True
        hw.append(s)
    o.Shape = Part.makeCompound(hw); rep["bottom_screws_moved"] = moved

    # 판에 그 구멍이 정말 있는지 (구멍 속 점이 판 밖이어야 함)
    cp_sp = ob(s2, "206_carriage_plates").Shape
    rep["old_hole_filled"] = cp_sp.isInside(V(98, -45.5, 400), 0.01, True) and cp_sp.isInside(V(88.65, -36.5, 400), 0.01, True) and cp_sp.isInside(V(88.65, -36.5, 491), 0.01, True)
    pi_pl = ob(s3, "199a_pi_shelf_plates").Shape
    probe = {"CP z403": (cp_sp, V(98, -45.5, 403)), "CP z491": (cp_sp, V(98, -45.5, 491)),
             "SP z403": (cp_sp, V(88.65, SY, 403)), "SP z491": (cp_sp, V(88.65, SY, 491)),
             "PB x-110": (pi_pl, V(-110, 59.5, 563.5)), "PB x-55": (pi_pl, V(-55, 59.5, 563.5)),
             "PV x-110": (pi_pl, V(-110, 68.5, 554)), "PV x-55": (pi_pl, V(-55, 68.5, 554))}
    rep["plate_hole_ok"] = {k: not sh.isInside(p, 0.01, True) for k, (sh, p) in probe.items()}

    o = ob(s2, "206_carriage_hardware")
    keep = [s for s in o.Shape.Solids if not (abs(s.BoundBox.XLength - 15) < 0.5 and abs(s.BoundBox.YLength - 15) < 0.5)]
    rep["carriage_old_removed"] = len(o.Shape.Solids) - len(keep)
    every = [("206_hw_keep (기둥·나사)", Part.makeCompound(keep))]     # 옛 브래킷 뺀 나머지 하드웨어도 검사
    for f in ("S1_급이부", "S2a_바닥구동"):
        dd = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        every += [(o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull()]
        App.closeDocument(dd.Name)
    for d in (s2, s3):
        every += [(o.Label, o.Shape.copy()) for o in d.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull()
                  and not o.Label.startswith(("206_carriage_hardware", "199ab"))]

    def hits(sols, own):
        out = []
        for s in sols:
            for lb, sb in every:
                if lb.startswith(own + ("REF_", "190_")):
                    continue
                try:
                    if s.BoundBox.intersect(sb.BoundBox):
                        v = s.common(sb).Volume
                        if v > 0.05:
                            out.append([lb[:50], round(v, 2)])
                except Exception:
                    pass
        return out

    # 캐리지: SP 다리 20 먼저, 아니면 CP 다리 20
    rep["carriage"] = {}
    for name, lcp, lsp in (("SP다리20", 15.0, 20.0), ("CP다리20", 20.0, 15.0)):
        new = [carriage(ZB, lcp, lsp), carriage(491.0, lcp, lsp)]
        h = hits(new, ())                    # 판 CP·SP·SV·기둥·나사와는 면만 닿아야 함 (겹침 0)
        rep["carriage"][name] = h
        if not h:
            break
    o.Shape = Part.makeCompound(keep + new)
    o.Label = ("206_carriage_hardware (SP–SV: M3 × 10 암-암 기둥 3 + M3 × 6 냄비 3 (SV 쪽) + M3 × 6 무두 3 (SP 탭 쪽, 면과 같은 높이) · "
               "미스미 FALCS L형 판금 브래킷 2 (%s — 20 × 15 × 폭 10, SUS 1.0, 구멍 N3 Ø3.5, 치수 지정) + M3 × 8 냄비 3 + 접시 1 (아래 브래킷 SP 쪽 — HV 밑) + 너트 4 — 구매)" % name)
    rep["carriage_pick"] = name
    # Pi 선반: 가로 다리 20 먼저, 아니면 세로 다리 20
    o = ob(s3, "199ab_pi_shelf_brackets")
    rep["shelf"] = {}
    for name, lh, lv in (("가로다리20", 20.0, 15.0), ("세로다리20", 15.0, 20.0)):
        new = [shelf(-110.0, lh, lv), shelf(-55.0, lh, lv)]
        h = hits(new, ())                    # 판 PB·PV와는 면만 닿아야 함
        rep["shelf"][name] = h
        if not h:
            break
    o.Shape = Part.makeCompound(new)
    o.Label = ("199ab_pi_shelf_brackets (미스미 FALCS L형 판금 브래킷 2 (%s — 20 × 15 × 폭 10, SUS 1.0, 구멍 N3 Ø3.5, 치수 지정) "
               "+ M3 × 8·너트 4 — PB 밑 ↔ PV, 구매)" % name)
    rep["shelf_pick"] = name
    for d in (s2, s3):
        d.recompute(); d.save(); App.closeDocument(d.Name)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_falcs.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
