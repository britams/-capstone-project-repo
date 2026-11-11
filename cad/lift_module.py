# -*- coding: utf-8 -*-
"""바닥 올리는 장치 → 산 리니어 모듈 하나 (서현 11/12 05:15 "리프팅 살 수 있으면 사도 돼", CAP-AI-62)

모듈: Keshuo 15BY25-77 (15 mm 2상 4선 스테핑 + M3×0.5 리드 + 구리 슬라이더, 행정 62) [확실 — 판매처 치수도 값]
  전체 88 · 모터 Ø15 × 13 · 채널 단면 14.5 (폭) × 15 (높이) · 바닥 M3 구멍 2개 간격 48 · 슬라이더 M2.5 구멍 2개
  [추측 — 치수도에 없음]: 채널 판 두께 1, 슬라이더 10 × 10 × 13, 슬라이더 윗면이 채널 위로 1.5, 슬라이더 구멍 간격 10 → 사서 재고 고침
없애는 것 (모듈 하나로): 모터판 152, 28BYJ 153·축 153r·귀 나사, 커플링 154, T8 리드 155·베어링 155b, 봉 157·부싱 157b·칼라 157c, T8 너트 159·나사 159s
놓는 자리: 모듈 바닥(채널 뒷면)을 옆판 151_R 안쪽 면 x 74에 M3 × 2, 모터가 아래 (z 241~254), 채널 z 254~329 (위판 121 아래 1 mm)
  y 가운데 −10 (스프링 칸 y −2부터를 비킴), 슬라이더 앞면 x 57.5
캐리지 158: 누름 받침 칸 쪽 몸통 (x 37~73, y −2~20) + 슬라이더로 가는 팔 (x 37~57.5, y −20~−2), z 262~274, M2.5 × 2로 슬라이더에.
  LM4UU는 누름 축 147 하나만 (봉 157이 없어짐)
"""
import FreeCAD as App
import Part

V = App.Vector
MOD = dict(L=88.0, motor_d=15.0, motor_t=13.0, ch_w=14.5, ch_h=15.0, wall=1.0, hole_p=48.0, stroke=62.0,
           sl=(10.0, 10.0, 13.0), sl_out=1.5, sl_hole_p=10.0)
X_BACK, Y_C, Z0 = 74.0, -10.0, 241.0          # 채널 뒷면 x, 가운데 y, 모터 아래 끝 z
REMOVE = ("152_", "153_", "153r", "154_", "155", "157", "159")


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def module():
    """반환 (모듈 고정부: 모터 + 채널 + 리드, 슬라이더 (쉼 자리), 슬라이더 앞면 x)"""
    m = MOD
    x1, x0 = X_BACK, X_BACK - m["ch_h"]
    y0, y1 = Y_C - m["ch_w"] / 2, Y_C + m["ch_w"] / 2
    zc0, zc1 = Z0 + m["motor_t"], Z0 + m["L"]
    xc = (x0 + x1) / 2
    motor = Part.makeCylinder(m["motor_d"] / 2, m["motor_t"], V(xc, Y_C, Z0))
    ch = box(x0, x1, y0, y1, zc0, zc1)
    ch = ch.cut(box(x0 - 1, x1 - m["wall"], y0 + m["wall"], y1 - m["wall"], zc0 + m["wall"], zc1 - m["wall"]))   # U: 앞(−x)이 열림
    for dz in (-m["hole_p"] / 2, m["hole_p"] / 2):
        ch = ch.cut(Part.makeCylinder(1.5, 5, V(x1 - 2, Y_C, (zc0 + zc1) / 2 + dz), V(1, 0, 0)))                  # 바닥 M3
    screw = Part.makeCylinder(1.5, zc1 - zc0 - 2 * m["wall"], V(xc, Y_C, zc0 + m["wall"]))
    return motor.fuse(ch).fuse(screw).removeSplitter(), x0 - m["sl_out"]


def slider(z_mid, x_front):
    a, b, c = MOD["sl"]
    s = box(x_front, x_front + c, Y_C - b / 2, Y_C + b / 2, z_mid - a / 2, z_mid + a / 2)
    s = s.cut(Part.makeCylinder(1.5, 40, V(X_BACK - MOD["ch_h"] / 2, Y_C, z_mid - 20)))                            # 리드 M3 (너트 나사산은 단순화)
    for dy in (-MOD["sl_hole_p"] / 2, MOD["sl_hole_p"] / 2):
        s = s.cut(Part.makeCylinder(1.0, 6, V(x_front - 0.01, Y_C + dy, z_mid), V(1, 0, 0)))                      # M2.5 탭 Ø2
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
    ok = (("153s", "153m"), ("153ss", "153s"), ("153ss", "158_"), ("153m", "151_"))
    keep = lambda h: not any((h[0].startswith(p) and h[1].startswith(q)) or (h[1].startswith(p) and h[0].startswith(q)) for p, q in ok)
    hits = [h if keep(h) else (h[0], h[1], h[2], "허용") for h in hits]
    sweep = [s for s in sweep if keep((s[1], s[2]))]
    return hits, sweep
