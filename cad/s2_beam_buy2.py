# -*- coding: utf-8 -*-
"""XY 2단계 '전부 사는 것' — 빔 (X로 움직이는 쪽) (서현 11/15 "다음단계 계속해", CAP-AI-62)
프린트 212 빔 끝 블록 · 211 Y 모터 브래킷 · LM8UU 222 · Ø6 Y 봉 → 사는 것:
  SC8UU ×2 (X 봉, 면이 Y 판 바깥면에 붙음 — 면 = 봉 중심 ± 11, 폭 34 · 길이 30 · M4 구멍 [가능성 높음 — 흔한 표])
  Y 판 YA·YB (알루미늄 3 mm 레이저, 안쪽 면 −56 · 48 = 옛 끝 블록 안쪽 면 → Y 이동 범위 그대로)
  → SC8UU 면이 판 바깥면에 오도록 X 봉을 5 mm 바깥으로: ya −65 → −70, yb 57 → 62 (SK8도 같이)
  Y 봉 Ø8 × 104 양 끝 M4 암나사 (미스미 맞춤 길이), 판 바깥에서 M4 접시머리로 → 봉 끝이 판 안쪽 면에 맞닿음
  X 너트 판 XN (알루미늄 3 mm, 옛 끝 블록 −x 면 자리, Y 원점 스위치도 이 판에) — T8 너트 225 자리 그대로, YA와 L 브래킷 DCB 2025로
  Y 모터판 YM (알루미늄 3 mm) — YA와 M3 × 40 기둥 3개 (그래서 Y 모터·커플링·Y T8 +2 mm)
  Y 베어링 221: LM6UU → LMK8UU (사각 플랜지 25, 길이 24, PCD 24, 구멍 3.5 [확실 — 판매처 표]) — 캐리지 206은 3단계에서
순서: (s23_gantry_buy1·1b 뒤) → (이것, 한 번만 — 다시는 split/*_before_buy2.FCStd에서) → full_merge → s2_motion_v3_check
freecad.exe cad/s2_beam_buy2.py (cwd = cad) → split/S2_마킹부.FCStd, split/_beam_buy2.json"""
import json, os, sys, traceback, glob, time
HERE = os.getcwd(); OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
rep = dict(hits=[])


def _save(doc, path):          # buy1과 같음
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
    ex, ey = V(1, 0, 0), V(0, 1, 0)
    XB, YM0 = 101.4, -40.0                    # 대기 자세의 빔 x · 캐리지 y
    YA, YB = -70.0, 62.0                      # 새 X 봉 y
    RZ, YRZ, YSZ = 480.0, (433.5, 472.5), 453.0   # Y 봉 간격 30 → 39: LMK8UU 몸통(Ø15) 사이에 T8 너트 플랜지(Ø22)가 들어감 (36이면 플랜지(25) 사이로 T8만 지나가고 너트가 몸통에 0.5 걸림)
    XS = XB + 2.0                             # SC8UU 가운데 x (+2: YA −x 끝 90.4 안에 M4 구멍)
    A_IN, B_IN, T = -56.0, 48.0, 3.0
    DY_MOT = 2.0

    def holes_y(sh, y0, pts, d):              # 판(법선 y)에 구멍
        for x, z in pts:
            sh = sh.cut(cyl(d / 2, 20, V(x, y0 - 10, z), ey))
        return sh

    def holes_x(sh, x0, pts, d):
        for y, z in pts:
            sh = sh.cut(cyl(d / 2, 20, V(x0 - 10, y, z), ex))
        return sh

    s2 = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    ob = lambda p: [o for o in s2.Objects if o.Label.startswith(p)]
    for p in ("212_", "211_", "222_", "207_", "221_"):
        for o in ob(p):
            s2.removeObject(o.Name)
    # X 봉·SK8 5 mm 바깥으로
    for o in ob("213_x_rods"):
        o.Shape = cyl(4, 200, V(-25, YA, RZ), ex).fuse(cyl(4, 200, V(-25, YB, RZ), ex))
        o.Label = "213_x_rods (Ø8 × 200, x −25~175, y −70 · 62 — 11/15 SC8UU 면 맞춤)"
    for p in ("218_rod_supports_SK8", "218s_SK8_bolts"):
        for o in ob(p):
            out = []
            for s in o.Shape.Solids:
                t = s.copy(); t.translate(V(0, -5 if s.BoundBox.Center.y < 0 else 5, 0)); out.append(t)
            o.Shape = Part.makeCompound(out)
    for p in ("226_", "227x"):                # X 원점 집게·스위치도 X 봉 따라 −y 5 (4단계에서 사는 것으로)
        for o in ob(p):
            o.Placement.Base = o.Placement.Base + V(0, -5, 0)
    # Y 모터 쪽 +2
    for p in ("209_", "209r_", "210_", "208_"):
        for o in ob(p):
            o.Placement.Base = o.Placement.Base + V(0, DY_MOT, 0)
    for p in ("153b_", "153n_"):
        for o in ob(p):
            if o.Shape.BoundBox.XMax < 130:          # Y 모터 귀 것만
                o.Placement.Base = o.Placement.Base + V(0, DY_MOT, 0)

    add = []
    # SC8UU ×2 (단순 모양: 몸통 + 봉 구멍 + LM8UU 테)
    def sc8(yr, face_y, sgn):                  # sgn: 면에서 몸통 쪽 (+1 = +y)
        y0, y1 = sorted((face_y, face_y + sgn * 22))
        b = box(XS - 15, XS + 15, y0, y1, RZ - 17, RZ + 17).cut(cyl(4.05, 32, V(XS - 16, yr, RZ), ex))
        return b
    add.append(("222_x_bearings_SC8UU (SC8UU ×2 — LM8UU 든 알루미늄 블록, 구매, M4 구멍 면이 Y 판에)",
                Part.makeCompound([sc8(YA, A_IN - T, -1), sc8(YB, B_IN + T, 1)]), (0.6, 0.6, 0.65)))
    # Y 판 YA (x 90.4~116.4, z 388~497) · YB (x 87.4~116.4, z 425~497)
    rod_pts = [(XB, z) for z in YRZ]
    sc_pts = [(XS + sx * 9, RZ + sz * 12) for sx in (-1, 1) for sz in (-1, 1)]
    so_pts = [(115.5, 433.0), (115.5, 458.0), (100.0, 392.0)]                 # M3 기둥 (YA ↔ YM)
    ya = box(90.4, 118.4, A_IN - T, A_IN, 400, 497).fuse(box(95, 105, A_IN - T, A_IN, 388, 400))   # 밑 혀: 기둥 3 (홀더 202는 x 91.4 밑으로 내려옴)
    ya = holes_y(ya, A_IN - T, rod_pts + sc_pts, 4.5)
    ya = holes_y(ya, A_IN - T, [(XB, YSZ)], 9.0)
    ya = holes_y(ya, A_IN - T, so_pts, 3.4)
    ya = holes_y(ya, A_IN - T, [(105.0, 408.0)], 5.5)                       # L 브래킷
    yb = box(90.4, 118.4, B_IN, B_IN + T, 425, 497)
    yb = holes_y(yb, B_IN, rod_pts + sc_pts, 4.5)
    # X 너트 판 XN (법선 x, x 87.4~90.4 = 옛 끝 블록 −x 면, y −84~−56, z 398~466) — T8 너트 225·Y 원점 스위치 227y 자리 그대로, 스위치 M2 나사는 판 관통 + 너트
    xn = box(87.4, 90.4, -84, -56, 398, 466).cut(cyl(5.25, 5, V(86, -65, 425), ex))
    for o in ob("227ys_"):
        for sol in o.Shape.Solids:
            c = sol.BoundBox.Center
            xn = xn.cut(cyl(1.2, 5, V(86, c.y, c.z), ex))
    import math
    xn = holes_x(xn, 87.4, [(-65 + 8 * math.cos(math.radians(45 + 90 * k)), 425 + 8 * math.sin(math.radians(45 + 90 * k))) for k in range(4)], 3.4)
    xn = holes_x(xn, 87.4, [(-76.0, 408.0)], 5.5)
    add.append(("212_beam_plates (Y 판 YA·YB + X 너트 판 XN — 알루미늄 3 mm 레이저 주문)", Part.makeCompound([ya.removeSplitter(), yb.removeSplitter(), xn.removeSplitter()]), (0.45, 0.6, 0.85)))
    # L 브래킷 DCB 2025 (XN +x 면 ↔ YA 바깥면), z 398~418. M5: XN은 −x에서 냄비 + 너트, YA는 안쪽에서 접시머리(판 면과 같은 높이) + 바깥 너트
    brk = box(90.4, 94.4, -84, -59, 398, 418).fuse(box(90.4, 110.4, -63, -59, 398, 418))
    hw = [cyl(2.5, 12, V(85.4, -76, 408), ex), box(94.4, 98.4, -80, -72, 404, 412),
          cyl(2.5, 12, V(105, -56, 408), V(0, -1, 0)), box(101, 109, -67, -63, 404, 412)]
    # Y 봉 끝 M4 접시머리 4 (판 바깥 → 봉 끝), SC8UU M4 접시머리 8 (판 안쪽 → SC8UU)
    for x, z in rod_pts:
        hw += [cyl(2, 10, V(x, A_IN - T, z), ey), cyl(2, 10, V(x, B_IN + T, z), V(0, -1, 0))]
    for x, z in sc_pts:
        hw += [cyl(2, 10, V(x, A_IN, z), V(0, -1, 0)), cyl(2, 10, V(x, B_IN, z), ey)]
    add.append(("212_beam_hardware (DCB 2025 1 + M5 × 10·너트 2 + M4 × 10 냄비 10 + 접시머리 2 (위 Y 봉 끝 — SC8UU 밑), 구매)", Part.makeCompound([brk] + hw), (0.35, 0.35, 0.37)))
    # Y 봉 Ø8 × 104
    add.append(("207_y_rods (Ø8 × 104 양 끝 M4 암나사 — 미스미 맞춤 길이, 판 안쪽 면 사이)",
                cyl(4, B_IN - A_IN, V(XB, A_IN, YRZ[0]), ey).fuse(cyl(4, B_IN - A_IN, V(XB, A_IN, YRZ[1]), ey)), (0.75, 0.75, 0.78)))
    # Y 모터판 YM (옛 211 판 자리 +2 → y −101.9~−98.9), 기둥 쪽으로 아래 늘림
    ym1 = -100.9 + DY_MOT
    ymp = box(XB - 21.5, XB + 21.5, ym1 - T, ym1, YSZ - 12, YSZ + 20).fuse(box(95.0, 118.4, ym1 - T, ym1, 388, YSZ - 12))
    ymp = holes_y(ymp, ym1 - T, [(XB, YSZ)], 10.0)
    ymp = holes_y(ymp, ym1 - T, [(XB + sx * 17.5, YSZ + 8) for sx in (-1, 1)], 4.2)
    ymp = holes_y(ymp, ym1 - T, so_pts, 3.4)
    add.append(("211_y_motor_plate (알루미늄 3 mm 레이저 — 28BYJ 귀 Ø4.2 2·축 Ø10·기둥 Ø3.4 3)", ymp.removeSplitter(), (0.45, 0.6, 0.85)))
    sos = [cyl(2.75, (A_IN - T) - ym1, V(x, ym1, z), ey) for x, z in so_pts]
    add.append(("211_y_motor_standoffs (M3 × 40 암-암 육각 기둥 3 + M3 × 6 6, 구매)", Part.makeCompound(sos), (0.7, 0.6, 0.3)))
    # LMK8UU ×2 (대기 ym −40, 플랜지 −y 끝)
    lmk = []
    for z in YRZ:
        lmk.append(cyl(7.5, 24, V(XB, YM0 - 12, z), ey).fuse(box(XB - 12.5, XB + 12.5, YM0 - 12, YM0 - 7, z - 12.5, z + 12.5)).cut(cyl(4.05, 26, V(XB, YM0 - 13, z), ey)))
    add.append(("221_y_bearings_LMK8UU (사각 플랜지 LMK8UU ×2, 구매 — 캐리지 판은 3단계)", Part.makeCompound(lmk), (0.6, 0.6, 0.65)))
    for lab, shp, col in add:
        n = s2.addObject("Part::Feature", "B2_%d" % len(s2.Objects))
        n.Shape, n.Label = shp, lab
        if App.GuiUp:
            n.ViewObject.ShapeColor = col
    _save(s2, os.path.join(OUT, "S2_마킹부.FCStd"))
    # 정지 겹침 검사 (바뀐 것 ↔ 전부)
    every = []
    for f in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        every += [(f[:2] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    CH = ("207", "208", "209", "210", "211", "212", "213", "218", "221", "222", "153b", "153n")
    probe = [(l, s) for l, s in every if l.split(" ", 1)[1].startswith(CH)]
    ok_pairs = (("213", "218_rod"), ("213", "222"), ("218s", "218_rod"), ("218s", "100"), ("217s", "218s"),
                ("207", "212"), ("207", "221"), ("221", "206"), ("221", "202"), ("227ys", "212"), ("207", "206"), ("222", "212"), ("212_beam_h", "212"), ("212_beam_h", "222"),
                ("211_y_motor_s", "211"), ("211_y_motor_s", "212"), ("209", "211"), ("153", "211"), ("153", "209"), ("210", "209"), ("208", "210"),
                ("208", "212"), ("208", "206"), ("208", "224"), ("225", "212"), ("214", "225"), ("214", "212"))
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
json.dump(rep, open(os.path.join(OUT, "_beam_buy2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
