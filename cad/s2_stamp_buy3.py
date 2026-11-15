# -*- coding: utf-8 -*-
"""스탬핑부 '전부 사는 것' (서현 11/15 15:02 "그 순서로 해", 펜 들기 방식 A "핀 + 판 구멍" → 안내는 판 홈 + 어깨 볼트, CAP-AI-62)
프린트 Y 캐리지 206 · 마커 홀더 202 · 조임 띠 203 · 스프링 204 · 안내 핀 223 → 알루미늄 3 mm 레이저 판 + 사는 것:
  CP 캐리지 판 (법선 y, y −47~−44): LMK8UU ×2 플랜지 (−y 면) + T8 너트 224 플랜지 (+y 면, 구멍 0·90°로 돌림)
  SP 안내 판 (법선 x, x 87.15~90.15): 세로 홈 2 (폭 4.2) — 홀더가 어깨 볼트 M3 (어깨 Ø4 × 6) 2개로 미끄러짐
  HV 홀더 판 (법선 x, x 84.15~87.15): P 클립 Ø15 ×2로 마커 잡음 (마커 축 x 75 = 옛 자리), 밑 모서리가 서보 혼에 얹힘 (옛 탭 높이 그대로)
  SV 서보 판 (법선 x, x 100.15~103.15): SG90 몸통 구멍 + 귀 M2 2 — SP와 M3 × 10 기둥 3
  CP ↔ SP: 작은 L 브래킷 2 (M3) — 위 z 486~496, 아래 z 395~405
  서보 205·혼·스플라인은 −x 2.35 (귀가 SV 면에 닿게)
펜 내림 힘 = 홀더 + 마커 무게만 (스프링 204 뺌) [추측: 말벌 등에 앉기 충분 — 실물로 확인]
P 클립 마커 축 거리 9.15 (반지름 7.35 + 고무·띠 1.8) [추측 — 판매처 치수로 확인]
순서: (buy2 뒤) → (이것, 한 번만 — 다시는 split/S2_마킹부_before_buy3.FCStd에서) → full_merge → s2_motion_v3_check (MOTION_ALL, PEN_LIFT 둘 다)
freecad.exe cad/s2_stamp_buy3.py (cwd = cad) → split/S2_마킹부.FCStd, split/_stamp_buy3.json"""
import json, os, sys, traceback, glob, time, math
HERE = os.getcwd(); OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
rep = dict(hits=[])


def _save(doc, path):
    try:
        doc.save(); App.closeDocument(doc.Name); return
    except OSError:
        pass
    App.closeDocument(doc.Name)
    tmp = sorted(glob.glob(path + ".*-*"), key=os.path.getmtime)[-1]
    for _ in range(60):
        try:
            os.replace(tmp, path); return
        except OSError:
            time.sleep(2)
    raise OSError("replace failed " + tmp)


try:
    import FreeCAD as App, Part
    import lift_v2 as L
    V = App.Vector
    box, cyl = L.box, L.cyl
    ex, ey, ez = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
    XB, YM, XM = 101.4, -40.0, 75.0
    YRZ, YSZ = (435.0, 471.0), 453.0
    SZ, SY = 417.94, -18.9                    # 서보 축 높이·y (대기)
    DXS = -2.35
    T = 3.0

    def hy(sh, y0, pts, d):
        for x, z in pts:
            sh = sh.cut(cyl(d / 2, 20, V(x, y0 - 10, z), ey))
        return sh

    def hx(sh, x0, pts, d):
        for y, z in pts:
            sh = sh.cut(cyl(d / 2, 20, V(x0 - 10, y, z), ex))
        return sh

    def slot_x(sh, x0, y, z0, z1, w):         # 법선 x 판에 세로 홈
        r = w / 2
        s = box(x0 - 10, x0 + 10, y - r, y + r, z0, z1).fuse(cyl(r, 20, V(x0 - 10, y, z0), ex)).fuse(cyl(r, 20, V(x0 - 10, y, z1), ex))
        return sh.cut(s)

    s2 = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    ob = lambda p: [o for o in s2.Objects if o.Label.startswith(p)]
    for p in ("206_", "202_", "203_", "204_", "223_", "224_"):
        for o in ob(p):
            s2.removeObject(o.Name)
    for p in ("205",):
        for o in ob(p):
            o.Placement.Base = o.Placement.Base + V(DXS, 0, 0)
    add = []
    # ---- CP (x 88.9~113.9, y −47~−44, z 395~496)
    CP0, CP1 = -47.0, -44.0
    cp = box(88.9, 113.9, CP0, CP1, 395, 496)
    for z in YRZ:
        cp = hy(cp, CP0, [(XB, z)], 15.2)
        cp = hy(cp, CP0, [(XB + 8.485 * sx, z + 8.485 * sz) for sx in (-1, 1) for sz in (-1, 1)], 3.5)
    cp = hy(cp, CP0, [(XB, YSZ)], 10.5)
    nut_h = [(XB + 8, YSZ), (XB - 8, YSZ), (XB, YSZ + 8), (XB, YSZ - 8)]
    cp = hy(cp, CP0, nut_h, 3.4)
    BRK = [(398.0, 400.0), (493.0, 491.0)]    # (브래킷 가운데 z, 구멍 z)
    cp = hy(cp, CP0, [(98.0, zh) for _, zh in BRK], 3.4)
    # ---- SP (x 87.15~90.15, y −40~+1, z 388~496)
    SP0, SP1 = 87.15, 90.15
    sp = box(SP0, SP1, -40, 1, 388, 496)
    for y in (-32.0, -4.0):
        sp = slot_x(sp, SP0, y, 429.9, 446.2, 4.2)
    sp = sp.cut(box(SP0 - 1, SP1 + 1, -25.4, -12.4, 403.0, 425.0))           # 서보 보스·스플라인
    SO = [(-8.0, 398.0), (-12.0, 440.0), (-30.0, 392.0)]      # (−12, 440): 펜 올렸을 때 y −4 어깨 볼트 너트 피함
    sp = hx(sp, SP0, SO, 3.4)
    sp = hx(sp, SP0, [(-36.5, zh) for _, zh in BRK], 3.4)
    # ---- SV (x 100.15~103.15) — LMK 아래 몸통(y ≤ −28, z ≥ 427.5) 피해 L 모양
    SV0, SV1 = 100.15, 103.15
    sv = box(SV0, SV1, -33, -5, 388, 426).fuse(box(SV0, SV1, -27, -5, 426, 444))
    sv = sv.cut(box(SV0 - 1, SV1 + 1, -25.1, -12.7, 401.34, 424.14))         # SG90 몸통
    sv = hx(sv, SV0, [(SY, SZ - 18.9), (SY, SZ + 8.5)], 2.2)                  # 귀 M2
    sv = hx(sv, SV0, SO, 3.4)
    add.append(("206_carriage_plates (CP 캐리지 판 · SP 안내 판 · SV 서보 판 — 알루미늄 3 mm 레이저)",
                Part.makeCompound([cp.removeSplitter(), sp.removeSplitter(), sv.removeSplitter()]), (0.45, 0.6, 0.85)))
    # ---- 사는 것: 기둥·브래킷·나사·너트
    hw = [cyl(2.75, SV0 - SP1, V(SP1, y, z), ex) for y, z in SO]               # M3 × 10 육각 기둥 3
    for zc, zh in BRK:                                                       # 작은 L 브래킷 (CP +y 면 ↔ SP +x 면) 15 × 15 × 10 × 2 [추측]
        hw.append(box(SP1, SP1 + 15, CP1, CP1 + 2, zc - 5, zc + 5).fuse(box(SP1, SP1 + 2, CP1, CP1 + 15, zc - 5, zc + 5)))
        hw.append(cyl(1.5, 8, V(98.0, CP0 - 3, zh), ey)); hw.append(cyl(1.5, 8, V(SP0 - 3, -36.5, zh), ex))
    nut = cyl(11.0, 3.5, V(0, 0, 0)).fuse(cyl(5.1, 11.5, V(0, 0, 3.5)))
    for k in range(4):
        a = math.radians(90 * k)
        nut = nut.cut(cyl(1.75, 4.5, V(8 * math.cos(a), 8 * math.sin(a), -0.5)))
    nut = nut.cut(cyl(4.0, 16, V(0, 0, -0.5))).removeSplitter()
    nut.Placement = App.Placement(V(XB, CP1, YSZ), App.Rotation(ez, ey))
    add.append(("224_y_nut_T8 (T8 황동 플랜지 너트 — CP +y 면, 구멍 0·90°)", nut, (0.8, 0.65, 0.3)))
    add.append(("206_carriage_hardware (M3 × 10 기둥 3 · 작은 L 브래킷 2 · M3 나사·너트, M2 × 8 2 — 구매)", Part.makeCompound(hw), (0.35, 0.35, 0.37)))
    # ---- HV 홀더 판 (대기 = 펜 내림): 밑 모서리 y −46~−25.5 → z 405, −25.5~−12.4 → 424.3 (보스·허브 위), −12.4~0 → 419.94 (혼 끝 = 옛 탭)
    HV0, HV1 = 84.15, 87.15
    hv = box(HV0, HV1, -46, -25.5, 405, 455).fuse(box(HV0, HV1, -25.5, -12.4, 424.3, 455)).fuse(box(HV0, HV1, -12.4, 0, 419.94, 455))
    BOLT = [(-32.0, 432.0), (-4.0, 432.0)]
    hv = hx(hv, HV0, BOLT, 4.1)
    CLIP_Z = (412.0, 445.0)
    hv = hx(hv, HV0, [(YM, z) for z in CLIP_Z], 4.3)                           # P 클립 M4
    add.append(("202_holder_plate_HV (홀더 판 — 알루미늄 3 mm 레이저, 밑 모서리가 서보 혼에)", hv.removeSplitter(), (0.45, 0.6, 0.85)))
    # P 클립 Ø15 ×2 (고리 + 귀) — 마커 축 x 75
    clips = []
    for z in CLIP_Z:
        ring = cyl(9.15, 12, V(XM, YM, z - 6)).cut(cyl(7.35, 14, V(XM, YM, z - 7)))
        ear = box(XM + 7.35, HV0, YM - 6, YM + 6, z - 6, z + 6).cut(cyl(7.35, 14, V(XM, YM, z - 7)))
        clips.append(ring.fuse(ear).removeSplitter())
    add.append(("203_marker_P_clips (P 클립 Ø15 고무 ×2 + M4 × 10·너트 — 구매)", Part.makeCompound(clips), (0.3, 0.3, 0.3)))
    bolts = []
    for y, z in BOLT:                                                        # 어깨 볼트: 머리 −x, 어깨 Ø4 HV + SP
        bolts.append(cyl(3.5, 2.5, V(HV0 - 2.5, y, z), ex).fuse(cyl(2.0, SP1 + 0.2 - HV0, V(HV0, y, z), ex)).fuse(cyl(1.5, 4, V(SP1 + 0.2, y, z), ex)))
        bolts.append(box(SP1 + 0.2, SP1 + 2.6, y - 2.75, y + 2.75, z - 2.75, z + 2.75))     # 와셔 + 너트
    for z in CLIP_Z:
        bolts.append(cyl(2.0, 10, V(HV0 - 3, YM, z), ex))
    add.append(("202_holder_bolts (어깨 볼트 M3 · 어깨 Ø4 × 6 2 + 너트 — 구매, 홀더와 같이 움직임)", Part.makeCompound(bolts), (0.35, 0.35, 0.37)))
    for lab, shp, col in add:
        n = s2.addObject("Part::Feature", "B3_%d" % len(s2.Objects))
        n.Shape, n.Label = shp, lab
        if App.GuiUp:
            n.ViewObject.ShapeColor = col
    _save(s2, os.path.join(OUT, "S2_마킹부.FCStd"))
    # 정지 겹침 검사
    every = []
    for f in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        every += [(f[:2] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    CH = ("202", "203", "205", "206", "224")
    probe = [(l, s) for l, s in every if l.split(" ", 1)[1].startswith(CH)]
    ok_pairs = (("206_carriage_h", "206_carriage_p"), ("224", "206_carriage_p"), ("224", "208"), ("221", "206_carriage_p"),
                ("202_holder_b", "202_holder_p"), ("202_holder_b", "206_carriage_p"), ("202_holder_b", "203"), ("203", "201"), ("203", "202_holder_p"),
                ("205", "206_carriage_p"), ("205", "206_carriage_h"), ("205h", "202_holder_p"), ("205h", "205"), ("205s", "205"), ("205s", "205h"))
    seen = set()
    for la, sa in probe:
        for lb, sb in every:
            if la == lb or (lb, la) in seen:
                continue
            a, b = la.split(" ", 1)[1], lb.split(" ", 1)[1]
            if any(a.startswith(p) and b.startswith(q) or a.startswith(q) and b.startswith(p) for p, q in ok_pairs):
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
json.dump(rep, open(os.path.join(OUT, "_stamp_buy3.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
