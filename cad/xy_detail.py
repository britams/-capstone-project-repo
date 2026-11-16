# -*- coding: utf-8 -*-
"""XY · 펜 그립 부품 실제 모양 + 구멍마다 나사 (서현 11/17 02:54 "직사각형들 제대로 그리고, 나사도 제대로 하나씩 … 조립해야 되는데", CAP-AI-62)
부품 파일 split/P2xy_XY플랫폼.FCStd에서 고침 (다시는 split/P2xy_XY플랫폼_before_detail.FCStd에서) → xy_platform.py attach로 S2에 붙임
  A. SC8UU 222: 민 상자 → 30 × 34 × 22 블록, 모서리 0.8, 봉 구멍 Ø8.4, 양 끝 베어링 자리 Ø15 × 1, 붙는 면 M4 탭 4 (18 × 24, 깊이 8) [Adafruit 1179 치수]
  B. LMK8UU 221: 플랜지 구멍 Ø3.5 4 (PCD 24) + M3 × 12 냄비 8 + 너트 8 (플랜지 −y → CP +y) → 새 물체 221_y_bearing_screws
  C. DCB 2025 (212 안): 민 상자 → L (두께 4 [추측]) + 다리마다 Ø5.5 / M5 × 12 냄비 2 + 6각 너트 2 (옛 M5 × 10은 판 3 + 다리 4 + 너트 4에 짧음)
  D. M4 12개 (212 안): 머리 없는 원기둥 → M4 × 10 접시머리 (ISO 10642) 12, YA·YB에 접시 자리 12 (봉 끝 4 · SC8UU 8 — 캐리지 쪽 면이 평평해야 LMK 나사 머리와 안 닿음)
  E. 211 기둥 3: 원기둥 → M3 × 40 암-암 6각 기둥 + M3 × 6 냄비 6 (양 끝)
  F. 206: SP–SV 기둥 3 → Ø6 × 10 스페이서 + M3 × 16 냄비 (SV 쪽에서, SP는 M3 탭 — 홀더 판 HV가 SP 바깥 면을 미끄러지므로 거기 머리·너트를 두면 안 됨)
         ETTINGER 브래킷 2: 나사 구멍 Ø3.2, M3 × 8 냄비 4 + 너트 4
  G. SG90 귀: M2 × 8 냄비 2 + M2 너트 2 (SV 쪽에서) → 새 물체 205_z_servo_screws
  H. 202: 네모 너트 4 → 6각, P-8 나사 2 → M3 × 10 접시머리 (HV +x 면이 SP에 닿아 미끄러짐 → 접시), HV 접시 자리 2
  I. POM 너트 224: M2 × 8 냄비 + M2 너트 2 (M3 너트는 너트 몸통 Ø7.9와 닿음), 아래 구멍은 LMK8UU 플랜지에 가려 비움
     225: XN +x 쪽에 너트 자리가 없어 XN M2 탭 2 + M2 × 6 (위 구멍은 Y 원점 스위치에 가려 비움). XN 윗모서리가 SC8UU와 겹치던 것 깎음
  E′. 211 기둥 나사 중 Y 모터판 쪽은 모터 앞면과 닿아 M3 × 8 접시머리 + 접시 자리
  G′. SV 아래 귀 구멍이 SG90 귀 구멍과 0.56 어긋나 있던 것 맞춤
GUI FreeCAD에서 exec 가능 (os._exit 없음) → split/_xy_detail.json"""
import json, os, sys, shutil, traceback, importlib, math
import FreeCAD as App, Part
HERE = r"C:\capstone\-capstone-project-repo\cad"; OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
V = App.Vector
rep = dict(hits=[])
EX, EY, EZ = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
NUT = {2.0: (4.0, 1.6), 3.0: (5.5, 2.4), 4.0: (7.0, 3.2), 5.0: (8.0, 4.0)}          # 맞변 · 두께 [확실 — ISO 4032]
CSK = {3.0: (6.72, 1.86), 4.0: (8.96, 2.48)}                                          # ISO 10642 머리 지름 · 높이


def rot(d):
    return App.Rotation(EZ, V(d).normalize())


def pan(p, d, size, L_):
    import lift_v2 as L
    return L.pan(V(p), V(d), size, L_)


def csk(p, d, size, L_):
    """접시머리: p = 머리 윗면 가운데 (판 면과 같은 높이), d = 몸통 방향, L_ = 전체 길이"""
    dk, k = CSK[size]
    s = Part.makeCone(dk / 2, size / 2, k, V(0, 0, 0), EZ).fuse(Part.makeCylinder(size / 2, L_, V(0, 0, 0), EZ))
    s = s.cut(Part.makeCylinder(dk * 0.22, k * 0.6, V(0, 0, -0.01), EZ))              # 6각 구멍 대신 둥근 홈
    s = s.removeSplitter()
    s.Placement = App.Placement(V(p), rot(d))
    return s


def csk_seat(p, d, size, hole_r):
    """판에 접시 자리 (p = 판 면 가운데, d = 판 안쪽으로)"""
    dk, k = CSK[size]
    c = Part.makeCone(dk / 2 + 0.1, hole_r, (dk / 2 + 0.1 - hole_r), V(0, 0, -0.01), EZ)
    c.Placement = App.Placement(V(p), rot(d))
    return c


def hexprism(p, d, af, t, bore):
    R = af / math.sqrt(3)
    pts = [V(R * math.cos(math.radians(60 * k)), R * math.sin(math.radians(60 * k)), 0) for k in range(7)]
    s = Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, t))
    if bore:
        s = s.cut(Part.makeCylinder(bore / 2, t + 2, V(0, 0, -1), EZ))
    s.Placement = App.Placement(V(p), rot(d))
    return s


def nut(p, d, size):
    af, t = NUT[size]
    return hexprism(p, d, af, t, size)


def tube(p, d, ro, ri, L_):
    s = Part.makeCylinder(ro, L_, V(0, 0, 0), EZ).cut(Part.makeCylinder(ri, L_ + 2, V(0, 0, -1), EZ))
    s.Placement = App.Placement(V(p), rot(d))
    return s


def cyl(p, d, r, L_):
    return Part.makeCylinder(r, L_, V(p), V(d))


try:
    import lift_v2 as L
    importlib.reload(L)
    P = os.path.join(OUT, "P2xy_XY플랫폼.FCStd"); B = os.path.join(OUT, "P2xy_XY플랫폼_before_detail.FCStd")
    shutil.copy(B, P) if os.path.exists(B) else shutil.copy(P, B)
    d = App.openDocument(P, True)
    ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)][0]

    def add(lab, shapes, col=None):
        n = d.addObject("Part::Feature", "DT%d" % len(d.Objects)); n.Shape = Part.makeCompound(shapes); n.Label = lab
        return n

    # ---------- A. SC8UU ----------
    o = ob("222_x_bearings_SC8UU")
    out = []
    for s in o.Shape.Solids:
        b = s.BoundBox
        sg = 1 if b.Center.y < 0 else -1                    # 붙는 면: −y 쪽 블록은 YMax, +y 쪽은 YMin
        yf = b.YMax if sg > 0 else b.YMin
        blk = Part.makeBox(b.XLength, b.YLength, b.ZLength, V(b.XMin, b.YMin, b.ZMin))
        try:
            blk = blk.makeChamfer(0.8, blk.Edges)
        except Exception:
            pass
        ya, za = yf - sg * 11.0, 480.0
        blk = blk.cut(cyl(V(b.XMin - 1, ya, za), EX, 4.2, b.XLength + 2))
        for x in (b.XMin, b.XMax):
            dd = EX if x == b.XMin else -EX
            blk = blk.cut(cyl(V(x, ya, za) - dd * 0.01, dd, 7.5, 1.0))
        for x in (b.XMin + 6.0, b.XMin + 24.0):
            for z in (468.0, 492.0):
                blk = blk.cut(cyl(V(x, yf + sg * 0.01, z), V(0, -sg, 0), 1.65, 8.0))
        out.append(blk.removeSplitter())
    o.Shape = Part.makeCompound(out)
    o.Label = "222_x_bearings_SC8UU (SC8UU ×2 — 30 × 34 × 22, 봉 높이 11, 붙는 면 M4 탭 4 (18 × 24), LM8UU 든 알루미늄 블록, 구매 [Adafruit 1179])"
    # ---------- B. LMK8UU ----------
    o = ob("221_y_bearings_LMK8UU")
    out, scr = [], []
    for s in o.Shape.Solids:
        b = s.BoundBox
        xc, zc = 101.4, b.Center.z
        y0 = b.YMin                                          # 플랜지 −y 면 (−52), 두께 5
        for sx in (-1, 1):
            for sz in (-1, 1):
                x, z = xc + sx * 8.485, zc + sz * 8.485
                s = s.cut(cyl(V(x, y0 - 1, z), EY, 1.75, 7.0))
                scr.append(pan(V(x, y0, z), EY, 3.0, 12.0))
                scr.append(nut(V(x, -44.0, z), EY, 3.0))
        out.append(s.removeSplitter())
    o.Shape = Part.makeCompound(out)
    o.Label = "221_y_bearings_LMK8UU (사각 플랜지 LMK8UU ×2 — 플랜지 25 × 5, 구멍 Ø3.5 4 (PCD 24), 몸 Ø15 × 24, 구매)"
    add("221_y_bearing_screws (M3 × 12 냄비 8 + M3 6각 너트 8 — LMK8UU 플랜지(−y) → 캐리지 판 CP, 구매)", scr)
    # ---------- C · D. 212 hardware ----------
    o = ob("212_beam_hardware")
    sols = o.Shape.Solids
    legA = Part.makeBox(20, 4, 20, V(90.4, -63.0, 398.0)).cut(cyl(V(105.0, -64, 408.0), EY, 2.75, 6))
    legB = Part.makeBox(4, 25, 20, V(90.4, -84.0, 398.0)).cut(cyl(V(89.0, -76.0, 408.0), EX, 2.75, 7))
    dcb = legA.fuse(legB).removeSplitter()
    hw = [dcb, pan(V(87.4, -76.0, 408.0), EX, 5.0, 12.0), nut(V(94.4, -76.0, 408.0), EX, 5.0),
          pan(V(105.0, -56.0, 408.0), -EY, 5.0, 12.0), nut(V(105.0, -63.0, 408.0), -EY, 5.0)]
    bp = ob("212_beam_plates")
    plates = list(bp.Shape.Solids)
    iYA = [i for i, s in enumerate(plates) if s.BoundBox.YLength < 4 and s.BoundBox.Center.y < 0][0]
    iYB = [i for i, s in enumerate(plates) if s.BoundBox.YLength < 4 and s.BoundBox.Center.y > 0][0]
    seats = {iYA: [], iYB: []}
    for s in sols[5:17]:                                     # 원기둥 M4 12
        b = s.BoundBox
        x, z = b.Center.x, b.Center.z
        ya = b.Center.y < 0
        pl = plates[iYA if ya else iYB]; pb = pl.BoundBox
        rod = abs(z - 433.5) < 0.6 or abs(z - 472.5) < 0.6
        if ya:
            p, dd = (V(x, pb.YMin, z), EY) if rod else (V(x, pb.YMax, z), -EY)
        else:
            p, dd = (V(x, pb.YMax, z), -EY) if rod else (V(x, pb.YMin, z), EY)
        hw.append(csk(p, dd, 4.0, 10.0))
        seats[iYA if ya else iYB].append(csk_seat(p, dd, 4.0, 2.25))
    o.Shape = Part.makeCompound(hw)
    o.Label = "212_beam_hardware (DCB 2025 L 1 + M5 × 12 냄비·6각 너트 2 (XN·YA ↔ L), M4 × 10 접시머리 12 (봉 끝 4 · SC8UU 8) — 구매)"
    for i in (iYA, iYB):
        s = plates[i]
        for c in seats[i]:
            s = s.cut(c)
        plates[i] = s.removeSplitter()
    bp.Shape = Part.makeCompound(plates)
    bp.Label = "212_beam_plates (Y 판 YA·YB + X 너트 판 XN — 알루미늄 3 mm 레이저 주문, YA·YB M4 접시 자리 6씩 (meviy 접시 가공))"
    rep["csk"] = {k: len(v) for k, v in seats.items()}
    # ---------- E. 211 기둥 ----------
    o = ob("211_y_motor_standoffs")
    so, m211 = [], []
    for s in o.Shape.Solids:
        b = s.BoundBox
        x, z = b.Center.x, b.Center.z
        so.append(hexprism(V(x, b.YMin, z), EY, 5.5, b.YLength, 3.0))
        so.append(csk(V(x, b.YMin - 3.0, z), EY, 3.0, 8.0))      # Y 모터판 바깥 면 — 모터 앞면이 판에 붙으므로 접시 (머리가 모터와 닿음)
        m211.append(csk_seat(V(x, b.YMin - 3.0, z), EY, 3.0, 1.7))
        so.append(pan(V(x, b.YMax + 3.0, z), -EY, 3.0, 6.0))     # YA +y 면
    o.Shape = Part.makeCompound(so)
    o.Label = "211_y_motor_standoffs (M3 × 40 암-암 6각 기둥 3 + M3 × 8 접시머리 3 (Y 모터판 쪽) + M3 × 6 냄비 3 (YA 쪽), 구매)"
    ym = ob("211_y_motor_plate")
    t = ym.Shape
    for c in m211:
        t = t.cut(c)
    ym.Shape = t.removeSplitter()
    ym.Label = "211_y_motor_plate (알루미늄 3 mm 레이저 — 모터 턱 Ø22.5 · M2.5 Ø2.9 4 · 기둥 Ø3.4 3 + M3 접시 자리 3 (바깥 면, meviy 접시 가공))"
    # ---------- F. 206 ----------
    o = ob("206_carriage_hardware")
    sols = o.Shape.Solids
    cp = ob("206_carriage_plates")
    cps = list(cp.Shape.Solids)
    iSP = [i for i, s in enumerate(cps) if s.BoundBox.XLength < 4 and s.BoundBox.Center.x < 95][0]
    sp = cps[iSP]
    hw = []
    for s in sols[0:3]:                                      # SP–SV 기둥 → 스페이서 + M3 × 16 (SV 쪽), SP M3 탭
        b = s.BoundBox
        y, z = b.Center.y, b.Center.z
        hw.append(tube(V(90.15, y, z), EX, 3.0, 1.6, 10.0))
        hw.append(pan(V(103.15, y, z), -EX, 3.0, 16.0))
        sp = sp.fuse(cyl(V(87.15, y, z), EX, 1.72, 3.0)).cut(cyl(V(86.0, y, z), EX, 1.25, 5.0))
    cps[iSP] = sp.removeSplitter()
    cp.Shape = Part.makeCompound(cps)
    cp.Label = "206_carriage_plates (CP 캐리지 판 · SP 안내 판 · SV 서보 판 — 알루미늄 3 mm 레이저, SP M3 탭 3 (meviy 탭 가공))"
    for ib, (zb, sc, sp_) in enumerate(((400.0, sols[4], sols[5]), (491.0, sols[7], sols[8]))):
        br = sols[3] if ib == 0 else sols[6]
        br = br.cut(cyl(V(98.0, -45.0, zb), EY, 1.6, 4.0)).cut(cyl(V(89.0, -36.5, zb), EX, 1.6, 4.0)).removeSplitter()
        hw += [br, pan(V(98.0, -47.0, zb), EY, 3.0, 8.0), nut(V(98.0, -43.0, zb), EY, 3.0),
               pan(V(87.15, -36.5, zb), EX, 3.0, 8.0), nut(V(91.15, -36.5, zb), EX, 3.0)]
    o.Shape = Part.makeCompound(hw)
    o.Label = ("206_carriage_hardware (SP–SV: Ø6 × 10 스페이서 3 + M3 × 16 냄비 3 (SV 쪽에서 → SP 탭) · ETTINGER 014.86.153 직각 브래킷 2 "
               "(15 × 15 × 10, 두께 1 [가능성 높음], 구멍 Ø3.2) + M3 × 8 냄비 4 + 너트 4 — 구매)")
    # ---------- G. SG90 귀 ----------
    sg = []
    cps = list(cp.Shape.Solids)
    iSV = [i for i, s in enumerate(cps) if s.BoundBox.XLength < 4 and s.BoundBox.Center.x > 95][0]
    sv = cps[iSV]
    for zo, z in ((399.6, 399.04), (426.4, 426.44)):                       # SV 아래 구멍이 SG90 귀 구멍(간격 27.4)과 0.56 어긋나 있었음 → 귀 구멍에 맞춤
        sv = sv.fuse(cyl(V(100.15, -18.9, zo), EX, 1.12, 3.0)).cut(cyl(V(99.0, -18.9, z), EX, 1.1, 5.0))
        sg.append(pan(V(103.15, -18.9, z), -EX, 2.0, 8.0))
        sg.append(nut(V(97.65, -18.9, z), -EX, 2.0))
    cps[iSV] = sv.removeSplitter()
    cp.Shape = Part.makeCompound(cps)
    add("205_z_servo_screws (M2 × 8 냄비 2 + M2 6각 너트 2 — SV 판 +x 면에서 SG90 귀로, 구매)", sg)
    # ---------- H. 202 ----------
    o = ob("202_holder_bolts")
    sols = o.Shape.Solids
    hv = ob("202_holder_plate_HV")
    hvs = hv.Shape
    hw = [sols[0], sols[2]]
    for s in (sols[1], sols[3]):
        b = s.BoundBox; hw.append(nut(V(b.XMin, b.Center.y, b.Center.z), EX, 3.0))
    for s in (sols[5], sols[7]):
        b = s.BoundBox; hw.append(nut(V(b.XMax, b.Center.y, b.Center.z), -EX, 3.0))
    for s in (sols[4], sols[6]):
        b = s.BoundBox
        p = V(87.15, b.Center.y, b.Center.z)
        hw.append(csk(p, -EX, 3.0, 10.0))
        hvs = hvs.cut(csk_seat(p, -EX, 3.0, 1.7))
    o.Shape = Part.makeCompound(hw)
    o.Label = "202_holder_bolts (어깨 볼트 M3 · 어깨 Ø4 × 6 2 + 6각 너트, P-8용 M3 × 10 접시머리 2 + 6각 너트 — 구매, 홀더와 같이 움직임)"
    hv.Shape = hvs.removeSplitter()
    hv.Label = "202_holder_plate_HV (홀더 판 — 알루미늄 3 mm 레이저, 밑 모서리가 서보 혼에, P-8 M3 접시 자리 2 (+x 면, meviy 접시 가공))"
    # ---------- I. POM 너트 ----------
    pm = []
    plates = list(bp.Shape.Solids)
    iXN = [i for i, s in enumerate(plates) if s.BoundBox.XLength < 4][0]
    xn = plates[iXN]
    for y in (-59.5, -70.5):                                 # XN +x 쪽은 YA 모서리·DCB라 너트 자리가 없음 → XN에 M2 탭, 플랜지 쪽에서 M2 × 6 (끝이 XN 면과 같음)
        pm.append(pan(V(84.22, y, 421.8), EX, 2.0, 6.0))
        xn = xn.fuse(cyl(V(87.4, y, 421.8), EX, 1.72, 3.0)).cut(cyl(V(86.0, y, 421.8), EX, 0.8, 5.0))
    xn = xn.cut(Part.makeBox(4.0, 23.0, 5.0, V(86.9, -81.5, 462.5)))     # SC8UU 밑 모서리와 겹치던 XN 윗부분 (z 463~466) 깎음
    plates[iXN] = xn.removeSplitter()
    bp.Shape = Part.makeCompound(plates)
    add("225_x_nut_screws (M2 × 6 냄비 2 — POM 플랜지(−x) → XN M2 탭 (meviy 탭 가공), 위 구멍은 Y 원점 스위치와 닿아 비움, 구매)", pm)
    pm = []
    for x in (95.9, 106.9):
        pm.append(pan(V(x, -40.82, 456.2), -EY, 2.0, 8.0)); pm.append(nut(V(x, -47.0, 456.2), -EY, 2.0))
    add("224_y_nut_screws (M2 × 8 냄비 2 + M2 6각 너트 2 — POM 플랜지(+y) → CP, 아래 구멍은 LMK8UU 플랜지에 가려 비움, 구매)", pm)
    d.recompute(); d.save()
    # ---------- 겹침 검사 (부품 파일 안, 바뀐 것 ↔ 전부) ----------
    objs = [(o.Label, o.Shape) for o in d.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull()]
    CH = ("222_", "221_", "212_beam_hardware", "212_beam_plates", "211_y_motor_standoffs", "206_", "205_z_servo_screws", "202_", "225_x_nut_screws", "224_y_nut_screws")
    ok = (("212_beam_hardware", "222_"), ("212_beam_hardware", "207_"), ("206_carriage_hardware", "206_carriage_plates"),
          ("212_beam_hardware", "212_beam_hardware"), ("206_carriage_hardware", "206_carriage_hardware"), ("202_holder_bolts", "202_holder_bolts"),
          ("221_y_bearing_screws", "221_y_bearing_screws"), ("211_y_motor_standoffs", "211_y_motor_standoffs"))
    seen = set()
    for la, sa in objs:
        if not la.startswith(CH):
            continue
        for lb, sb in objs:
            if la == lb or (lb, la) in seen:
                continue
            if any(la.startswith(p) and lb.startswith(q) or la.startswith(q) and lb.startswith(p) for p, q in ok):
                continue
            if sa.BoundBox.intersect(sb.BoundBox):
                v = sa.common(sb).Volume
                if v > 0.05:
                    rep["hits"].append([la[:40], lb[:40], round(v, 2)]); seen.add((la, lb))
    App.closeDocument(d.Name)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_xy_detail.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False)[:4000])
