# -*- coding: utf-8 -*-
"""바닥 올리는 장치 → 산 리니어 모듈 하나 (서현 11/12 05:15 "리프팅 살 수 있으면 사도 돼", CAP-AI-62)

모듈: Keshuo 15BY25-77 (15 mm 2상 4선 스테핑 + M3×0.5 리드 + 구리 슬라이더, 행정 62)
  [확실 — 판매처 치수도 6af992a1….webp]: 전체 88 · 모터 Ø15 · 폭 14.5 · 바닥 2-M3 간격 48 · 슬라이더 2-M2.5 (가로 간격 10.0)
     · 슬라이더 길이 10.0 · 바닥 면 → 슬라이더 윗면 10.5 ± 0.05 · 리드 M3 × 0.5 · 선 120 ± 10
  [치수도에 없음 → 사서 잼]: 채널 판 두께 (1로 그림), 채널 옆벽 높이 (6), 슬라이더 폭 (12). 모터 축 높이 = Ø15 가운데 7.5 [가능성 높음]
없애는 것 (모듈 하나로): 모터판 152, 28BYJ 153·축 153r·귀 나사, 커플링 154, T8 리드 155·베어링 155b, 봉 157·부싱 157b·칼라 157c, T8 너트 159·나사 159s
놓는 자리: 모듈 바닥(채널 뒷면)을 옆판 151_R 안쪽 면 x 74에 M3 × 2, 모터가 아래 (z 241~254), 채널 z 254~329 (위판 121 아래 1 mm)
  y 가운데 −10 (스프링 칸 y −2부터를 비킴), 슬라이더 윗면 x 74 − 10.5 = 63.5
캐리지 158: 누름 받침 칸 쪽 몸통 (x 37~73, y −2~20) + 슬라이더로 가는 팔 (x 37~57.5, y −20~−2), z 262~274, M2.5 × 2로 슬라이더에.
  LM4UU는 누름 축 147 하나만 (봉 157이 없어짐)
"""
import FreeCAD as App
import Part

V = App.Vector
MOD = dict(L=88.0, motor_d=15.0, motor_t=13.0, ch_w=14.5, ch_h=15.0, wall=1.0, wall_h=6.0, hole_p=48.0, stroke=62.0,
           sl_L=10.0, sl_w=12.0, sl_top=10.5, axis_h=7.5, sl_hole_p=10.0)
X_BACK, Y_C, Z0 = 74.0, -10.0, 241.0          # 채널 뒷면 x, 가운데 y, 모터 아래 끝 z
REMOVE = ("152_", "153_", "153r", "154_", "155", "157", "159")


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def module():
    """반환 (모듈 고정부: 모터 + 채널(바닥판 + 옆벽 2) + 리드, 슬라이더 윗면 x)"""
    m = MOD
    xb = X_BACK                                            # 바닥 면 (옆판 151_R 안쪽 면에 닿음)
    y0, y1 = Y_C - m["ch_w"] / 2, Y_C + m["ch_w"] / 2
    zc0, zc1 = Z0 + m["motor_t"], Z0 + m["L"]
    xa = xb - m["axis_h"]                                  # 모터·리드 축
    motor = Part.makeCylinder(m["motor_d"] / 2, m["motor_t"], V(xa, Y_C, Z0))
    ch = box(xb - m["wall"], xb, y0, y1, zc0, zc1)                                                     # 바닥판
    for ya in (y0, y1 - m["wall"]):
        ch = ch.fuse(box(xb - m["wall_h"], xb, ya, ya + m["wall"], zc0, zc1))                           # 옆벽
    for ze in (zc0, zc1 - m["wall"]):
        ch = ch.fuse(box(xb - m["motor_d"], xb, y0, y1, ze, ze + m["wall"]))                            # 끝판 (리드 받침)
    for dz in (-m["hole_p"] / 2, m["hole_p"] / 2):
        ch = ch.cut(Part.makeCylinder(1.5, 5, V(xb - 2, Y_C, (zc0 + zc1) / 2 + dz), V(1, 0, 0)))          # 바닥 2-M3
    screw = Part.makeCylinder(1.5, zc1 - zc0 - 2 * m["wall"], V(xa, Y_C, zc0 + m["wall"]))
    return motor.fuse(ch).fuse(screw).removeSplitter(), xb - m["sl_top"]


def slider(z_mid, x_front):
    m = MOD
    s = box(x_front, X_BACK - m["wall"], Y_C - m["sl_w"] / 2, Y_C + m["sl_w"] / 2, z_mid - m["sl_L"] / 2, z_mid + m["sl_L"] / 2)
    s = s.cut(Part.makeCylinder(1.5, 40, V(X_BACK - m["axis_h"], Y_C, z_mid - 20)))                     # 리드 M3 (너트 나사산은 단순화)
    for dy in (-m["sl_hole_p"] / 2, m["sl_hole_p"] / 2):
        s = s.cut(Part.makeCylinder(1.0, 6, V(x_front - 0.01, Y_C + dy, z_mid), V(1, 0, 0)))              # M2.5 탭 Ø2
    return s


def carriage_base(x_front):
    import lift_drive as LD
    c = LD.CAR
    body = box(c["x0"], c["x1"], -2.0, c["y1"], c["z0"], c["z1"])
    arm = box(c["x0"], x_front, c["y0"], -2.0 + 0.01, c["z0"], c["z1"])
    car = body.fuse(arm)
    car = car.cut(LD.cyl(LD.LM4["D"] / 2, c["z0"] - 1, c["z1"] + 1, LD.PSH))                                          # 누름 축 LM4UU
    zm = (c["z0"] + c["z1"]) / 2
    for dy in (-MOD["sl_hole_p"] / 2, MOD["sl_hole_p"] / 2):
        car = car.cut(Part.makeCylinder(1.4, 30, V(x_front - 30, Y_C + dy, zm), V(1, 0, 0)))                      # M2.5 지나는 구멍 Ø2.8
    r = car.removeSplitter()
    return r if r.isValid() else car


def slider_screws(x_front, zm):
    out = []
    for dy in (-MOD["sl_hole_p"] / 2, MOD["sl_hole_p"] / 2):
        p = V(x_front, Y_C + dy, zm)
        L = 12.0                                                    # 팔 길이 x 37 → 57.5 = 20.5 → 머리는 팔 −x 끝에서 [추측 — 길이는 사서 맞춤]
        out.append(Part.makeCylinder(1.25, L, p - V(L - 4, 0, 0), V(1, 0, 0)))
    return Part.makeCompound(out)


LABELS = {
    "153m": "153m_lift_module (리니어 모듈 Keshuo 15BY25-77 — 15 mm 2상 4선 + M3×0.5 리드, 행정 62, 151_R에 M3 × 2, 구매) [치수 대표값 — 사서 잼]",
    "153s": "153s_lift_slider (모듈 구리 슬라이더 — 캐리지에 M2.5 × 2, 모듈 일부)",
    "153ss": "153ss_slider_screws (M2.5 × 12 2 — 캐리지 팔 → 슬라이더, 구매)",
    "158": "158_carriage (바닥 캐리지 — 받침 칸 몸통 + 슬라이더 팔, LM4UU 1 (누름 축), 작은 3D 프린트 PETG)",
}


def apply(doc):
    """lift_drive.apply 대신. 반환 (만든 것들, press 보고)"""
    import D5g_feeder_uln as FU
    import lift_drive as LD
    removed = []
    for o in [o for o in doc.Objects if o.TypeId == "Part::Feature" and o.Label.startswith(REMOVE)]:
        removed.append(o.Label.split(" ")[0])
        doc.removeObject(o.Name)
    for o in [o for o in doc.Objects if o.Label.startswith(("153b", "153n"))]:          # 바닥 모터 귀 나사만 뺌 (X·Y 모터 것은 남김)
        o.Shape = Part.makeCompound([s for s in o.Shape.Solids if s.BoundBox.ZMax >= 240])
    for o in [o for o in doc.Objects if o.Label.startswith(("148c_", "227p", "153m", "153s", "148_load_cell", "148b_", "148g_", "148s_", "148m"))]:   # 148_load_cell: D5e 옛 로드셀 자리 (press_apply가 지우던 것)
        doc.removeObject(o.Name)
    mod, x_front = module()
    zm = (LD.CAR["z0"] + LD.CAR["z1"]) / 2
    car, latch, sw, scr, rep = FU.press_parts(carriage_base(x_front))
    rep["carriage_valid"], rep["carriage_vol"], rep["removed"] = car.isValid(), round(car.Volume), removed
    made = [LD._set(doc, "158", car)]
    for key, shp in (("153m", mod), ("153s", slider(zm, x_front)), ("153ss", slider_screws(x_front, zm))):
        o = doc.addObject("Part::Feature", "LM_" + key)
        o.Label, o.Shape = LABELS[key], shp
        made.append(o)
    made[0].Label = LABELS["158"]
    for nm, shp in (("148c_spring_latch (걸쇠 — 축 147에 끼워 순간접착, +y 혀가 누름 스위치를 누름, 3D 프린트 PETG 작은 것)", latch),
                    ("227p_press_switch (KW11-3Z 누름 스위치 PSW — NC, 스프링 4.8 mm(0.5 N)에서 딸깍, UNO 1 A1)", sw),
                    ("227ps_press_switch_screws (M2 × 10 십자 냄비머리 2 — 받침판에 셀프 탭, 긴 구멍으로 힘 맞춤)", scr)):
        o = doc.addObject("Part::Feature", "P" + nm.split(" ")[0])
        o.Label, o.Shape = nm, shp
        made.append(o)
    made += columns(doc)
    for o in doc.Objects:                                                                # F 드라이버: ULN2003 → DRV8833 (자리 그대로)
        if o.Label.startswith("195p_uln2003_F"):
            b = o.Shape.BoundBox
            o.Shape = box(b.Center.x - 9, b.Center.x + 9, b.Center.y - 8, b.Center.y + 8, b.ZMin, b.ZMin + 5)
            o.Label = "195p_uln2003_F (→ DRV8833 모듈 18 × 16, 바닥 F 양극 — 11/12, 이름은 하네스와 같게 둠) [모양 대표값]"
    doc.recompute()
    return made, rep


def check(doc, made):
    import lift_drive as LD
    LD.MOVING = ("158_", "153s", "153ss", "149_", "146_", "147_", "148c_", "140_", "227p", "227ps")
    hits, sweep = LD.check(doc, made)
    ok = (("153s", "153m"), ("153ss", "153s"), ("153ss", "158_"), ("153m", "151_"), ("151s", "151"), ("151s", "101_"), ("151s", "121_"),
          ("151s", "153m"), ("227fs", "151_"))
    keep = lambda h: not any((h[0].startswith(p) and h[1].startswith(q)) or (h[1].startswith(p) and h[0].startswith(q)) for p, q in ok)
    hits = [h if keep(h) else (h[0], h[1], h[2], "허용") for h in hits]
    sweep = [s for s in sweep if keep((s[1], s[2]))]
    return hits, sweep


# (11/12 08:00 서현 '양옆 기둥 고쳐 — 산 재료로') 옆판 151 L/R (프린트 10.5 두께) → 알루미늄 평철 20 × 3 (125 자름·구멍)
#   + 아래·위 꺾쇠 = 알루미늄 앵글 20 × 20 × 2 (20 자름) 4개 + M3 나사·너트
#   L: 평철 x 33~36 (안쪽 면 x 36 — 바닥 원점 스위치 227f 자리 그대로), y 3.3~23.3 — 입구 깔때기 111·G1 센서(x ≤ 30)를 비킴 [확실 — 모델 빈 자리 검사]
#   R: 평철 x 74~77 (안쪽 면 x 74 — 리니어 모듈 바닥), y −20~0 — 모듈을 바깥에서 M3 × 2
#   꺾쇠: L은 안쪽(+x, 위 꺾쇠는 캐리지 최고 310.5 위 z 312부터), R은 바깥(+x) — 위 꺾쇠가 걸리게 바닥판 121에 x 78~97 혀를 붙임
COL = dict(t=3.0, w=20.0, z0=205.0, z1=330.0, L=(33.0, 3.3), R=(74.0, -20.0))
ANG = dict(a=20.0, t=2.0)


def _bracket(xw, y0, z_v0, z_v1, z_h, dirx):
    """앵글 꺾쇠: 세운 다리 (x xw ~ xw+2·dirx, z z_v0~z_v1), 누운 다리 (z z_h ~ +2, x 방향 dirx로 20), 길이 20 (y)"""
    a, t = ANG["a"], ANG["t"]
    xs = sorted((xw, xw + dirx * t))
    v = box(xs[0], xs[1], y0, y0 + 20.0, z_v0, z_v1)
    xh = sorted((xw, xw + dirx * a))
    h = box(xh[0], xh[1], y0, y0 + 20.0, z_h, z_h + t)
    return v.fuse(h).removeSplitter()


def _m3(p, d, L):
    """M3 냄비머리 (머리 Ø5.5 × 2.4) + 너트 (모서리 6.35 × 2.4) — p = 머리 밑, d = 몸 방향"""
    head = Part.makeCylinder(2.75, 2.4, p - d * 2.4, d)
    sh = Part.makeCylinder(1.5, L, p, d)
    nut = Part.makeCylinder(3.15, 2.4, p + d * (L - 3.2), d)
    return head.fuse(sh), nut


def columns(doc):
    c = COL
    xL, yL = c["L"]
    xR, yR = c["R"]
    barL = box(xL, xL + c["t"], yL, yL + c["w"], c["z0"], c["z1"])
    barR = box(xR, xR + c["t"], yR, yR + c["w"], c["z0"], c["z1"])
    xi = xL + c["t"]                                                     # L 안쪽 면 36
    xo = xR + c["t"]                                                     # R 바깥 면 77
    br = [_bracket(xi, yL, c["z0"], c["z0"] + 20, c["z0"], +1),          # L 아래 (안쪽)
          _bracket(xi, yL, 312.0, c["z1"], c["z1"] - 2, +1),               # L 위 (안쪽, 캐리지 최고 310.5 위)
          _bracket(xo, yR, c["z0"], c["z0"] + 20, c["z0"], +1),          # R 아래 (바깥)
          _bracket(xo, yR, c["z1"] - 20, c["z1"], c["z1"] - 2, +1)]      # R 위 (바깥)
    bolts, nuts, deck_h, base_h = [], [], [], []
    for xb, y0, zv, zh, up in ((xi, yL, c["z0"] + 10, c["z0"], True), (xi, yL, 321.0, c["z1"] - 2, False),
                               (xo, yR, c["z0"] + 10, c["z0"], True), (xo, yR, c["z1"] - 10, c["z1"] - 2, False)):
        ym = y0 + 10.0
        # 세운 다리 ↔ 평철: 평철 바깥(머리) → 꺾쇠 쪽 너트
        bar_out = xb - c["t"] if xb == xi else xb - c["t"]
        b_, n_ = _m3(V(bar_out, ym, zv), V(1, 0, 0), 8.0)
        bolts.append(b_); nuts.append(n_)
        # 누운 다리 ↔ 데크(아래에서) / 바닥판(위에서)
        xm = xb + 12.0
        if up:
            b_, n_ = _m3(V(xm, ym, c["z0"] - 5.0), V(0, 0, 1), 10.0)       # 데크 아래 z 200에서 위로
            deck_h.append(Part.makeCylinder(1.7, 10, V(xm, ym, c["z0"] - 8)))
        else:
            b_, n_ = _m3(V(xm, ym, c["z1"] + 5.0), V(0, 0, -1), 10.0)      # 바닥판 위 z 335에서 아래로
            base_h.append(Part.makeCylinder(1.7, 10, V(xm, ym, c["z1"] - 3)))
        bolts.append(b_); nuts.append(n_)
    # 모듈 → R 평철 (바깥에서 M3 × 6, 모듈 바닥 탭)
    zc = Z0 + MOD["motor_t"] + (MOD["L"] - MOD["motor_t"]) / 2
    for dz in (-MOD["hole_p"] / 2, MOD["hole_p"] / 2):
        b_, _n = _m3(V(xo, Y_C, zc + dz), V(-1, 0, 0), 6.0)
        bolts.append(b_)
        barR = barR.cut(Part.makeCylinder(1.7, 10, V(xo + 1, Y_C, zc + dz), V(-1, 0, 0)))
    for (xb, y0, zv) in ((xi, yL, c["z0"] + 10), (xi, yL, 321.0), (xo, yR, c["z0"] + 10), (xo, yR, c["z1"] - 10)):
        hole = Part.makeCylinder(1.7, 20, V(xb - 10, y0 + 10, zv), V(1, 0, 0))
        if xb == xi:
            barL = barL.cut(hole)
        else:
            barR = barR.cut(hole)
    br = [b.cut(Part.makeCompound([Part.makeCylinder(1.7, 30, V(x0 - 15, y0 + 10, zv), V(1, 0, 0)) for x0, y0, zv in
                                   ((xi, yL, c["z0"] + 10), (xi, yL, 321.0), (xo, yR, c["z0"] + 10), (xo, yR, c["z1"] - 10))]))
          .cut(Part.makeCompound(deck_h + base_h)) for b in br]
    out = []
    for key, shp, lab in (("151_drive_side_L", barL, "151_drive_side_L (알루미늄 평철 20 × 3 — 125 자름·구멍 4, 원점 스위치 227f M2 탭, 구매)"),
                          ("151_drive_side_R", barR, "151_drive_side_R (알루미늄 평철 20 × 3 — 125 자름·구멍 4, 리니어 모듈 M3 × 2, 구매)")):
        o = [x for x in doc.Objects if x.Label.startswith(key)]
        o = o[0] if o else doc.addObject("Part::Feature", "LM_" + key[:4])
        o.Placement = App.Placement()
        o.Shape, o.Label = shp, lab
        out.append(o)
    for key, shp, lab in (("151k", Part.makeCompound(br), "151k_column_brackets (꺾쇠 4 — 알루미늄 앵글 20 × 20 × 2를 20씩 자름·구멍, 구매)"),
                          ("151s", Part.makeCompound(bolts + nuts), "151s_column_screws (M3 냄비머리 + 너트 — 평철·꺾쇠·데크·바닥판, 모듈 M3 × 6 2, 구매)")):
        for x in [x for x in doc.Objects if x.Label.startswith(key)]:
            doc.removeObject(x.Name)
        o = doc.addObject("Part::Feature", "LM_" + key)
        o.Shape, o.Label = shp, lab
        out.append(o)
    for pre, holes, tab in (("101_deck", deck_h, None), ("121_", base_h, box(78.0 - 0.01, 97.0, yR, yR + 20.0, c["z1"], c["z1"] + 5.0))):
        o = [x for x in doc.Objects if x.Label.startswith(pre)]
        if o:
            s = o[0].Shape
            if tab is not None:
                s = s.fuse(tab)
            o[0].Shape = s.cut(Part.makeCompound(holes)).removeSplitter()
    return out
