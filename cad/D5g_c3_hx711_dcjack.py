# -*- coding: utf-8 -*-
"""D5g C3 — HX711 모듈 + 패널 DC 잭 (서현, 2026-11-09, CAP-AI-55)

D5g_frame_detail.make() 끝에서 부른다. 다른 D5g 스크립트는 고치지 않는다 (194b 판은 여기서 −y로 늘림).

1) 198x HX711 모듈 (흔한 녹색 모듈) 34 × 21 × 1.6 [가능성 높음 — 판매처 표기, 실물 재기]
   - 작업 지시 자리 (66, 95, 210)는 급이 물길 143과 468 mm³ 겹치고 데크(y ±90) 밖 → 데크 위를 2 mm 간격으로 훑어
     (3 mm 틈, 높이 20) 빈 자리 3곳뿐 → 가장 가까운 (−44.5, 54), 긴 쪽을 y로 [확실 — c3 탐색, 고체 상자 기준]
   - 받침 198xc: 3D 프린트 받침 (바닥 3 + 긴 쪽 레일 1.5 + 둘레 턱 2), 기판 밑 바닥판 안 M3 × 8 접시머리 2개 → 데크 탭 구멍
     (승준 198n과 같은 데크 탭 방식. 귀를 밖으로 내면 빈 자리를 넘어서 안으로 넣음)
   - 핀: 한쪽 끝 4핀 (VCC·SCK·DT·GND → UNO 1 A1·A2), 다른 끝 6핀 (E+·E−·A−·A+·B−·B+ → 로드셀 148) — 2.54 간격, 위로 8.5
2) 194j 패널 DC 잭 5.5 × 2.1 (DC-099류: 판 구멍 Ø8, 바깥 테 Ø11 × 2, 안 너트 맞변 10 × 2, 뒤 몸통 Ø9 × 12 + 납땜 귀 3)
   [가능성 높음 — 판매처 대표 치수, 실물 재기]
   - 작업 지시 (−184, −22, 225)는 비상 정지 버섯 머리(Ø40, y −20~20)와 플러그(Ø약 10)가 겹침 → **y −35**
   - 194b 판을 −y로 22 mm 늘림 (퓨즈 쪽 +y 22 mm와 같은 방식, z 210~240), Ø8 구멍
"""
import FreeCAD as App
import Part

V = App.Vector
ZD = 205.0                                    # 데크 윗면
HX = dict(L=34.0, W=21.0, t=1.6, cx=-44.5, cy=54.0, base=3.0, lip=2.0, wall=1.5, gap=0.3, pin_h=8.5)
DC = dict(y=-35.0, z=225.0, hole=8.0, fl_d=11.0, fl_t=2.0, nut=10.0, nut_t=2.0, body_d=9.0, body_l=12.0, lug=3.0, ext=22.0)


def _hx711():
    h = HX
    # 긴 쪽(34)을 y로: 판 x 21, y 34
    bx, by = h["W"], h["L"]
    x0, y0 = h["cx"] - bx / 2, h["cy"] - by / 2
    w, g, rail = h["wall"], h["gap"], 1.5
    zb = ZD + h["base"] + rail                                          # 기판 아랫면 (레일 위 — 아래 납땜 1 mm 틈)
    cr = Part.makeBox(bx + 2 * (w + g), by + 2 * (w + g), h["base"] + rail + h["lip"], V(x0 - w - g, y0 - w - g, ZD))
    cr = cr.cut(Part.makeBox(bx + 2 * g, by + 2 * g, rail + h["lip"] + 1, V(x0 - g, y0 - g, ZD + h["base"])))
    for xr in (x0 - g, x0 + bx + g - 2.0):                              # 긴 쪽 두 레일 (폭 2)
        cr = cr.fuse(Part.makeBox(2.0, by + 2 * g, rail, V(xr, y0 - g, ZD + h["base"])))
    screws, cuts = [], []
    for sy in (h["cy"] - 8.0, h["cy"] + 8.0):                           # 기판 밑 바닥판 안 M3 접시머리 2 (기판 얹기 전에 조임)
        zt0 = ZD + h["base"]
        cuts += [Part.makeCone(1.6, 3.0, 1.4, V(h["cx"], sy, zt0 - 1.4)), Part.makeCylinder(1.7, h["base"] + 2, V(h["cx"], sy, ZD - 1))]
        screws.append(Part.makeCone(1.5, 2.8, 1.4, V(h["cx"], sy, zt0 - 1.4)).fuse(
            Part.makeCylinder(1.5, 8.0 - 1.4, V(h["cx"], sy, zt0 - 8.0))))
    cr = cr.cut(Part.makeCompound(cuts)).removeSplitter()
    pcb = Part.makeBox(bx, by, h["t"], V(x0, y0, zb))
    chip = Part.makeBox(4.0, 10.0, 1.6, V(h["cx"] - 2.0, h["cy"] - 5.0, zb + h["t"]))   # HX711 SOP-16
    pins = []
    zt = zb + h["t"]
    for n, yy in ((4, y0 + 2.0), (6, y0 + by - 2.0)):
        for i in range(n):
            xx = h["cx"] + (i - (n - 1) / 2) * 2.54
            pins.append(Part.makeBox(2.54, 2.54, 2.5, V(xx - 1.27, yy - 1.27, zt)))           # 플라스틱 받침
            pins.append(Part.makeBox(0.64, 0.64, h["pin_h"] + h["t"] + 1.0, V(xx - 0.32, yy - 0.32, zb - 1.0)))   # 아래 1 mm (레일 틈 1.5 안)
    board = Part.makeCompound([pcb, chip] + pins)
    return cr, board, Part.makeCompound(screws)


def _dc_jack(plate):
    d = DC
    pb = plate.Shape.BoundBox
    xo, xi = pb.XMin, pb.XMax                                             # 판 바깥 면 −184, 안 면 −180
    ext = Part.makeBox(pb.XLength, d["ext"], 30.0, V(xo, pb.YMin - d["ext"] + 0.01, 210.0))
    hole = Part.makeCylinder(d["hole"] / 2, 10, V(xo - 1, d["y"], d["z"]), V(1, 0, 0))
    plate.Shape = plate.Shape.fuse(ext).cut(hole).removeSplitter()
    plate.Label = "194b_estop_plate (3D 프린트 4 mm — 비상 정지 Ø22.5 + 퓨즈 Ø12 + DC 잭 Ø8, 레일에 M5 × 8 두 개)"
    P = lambda x: V(x, d["y"], d["z"])
    X = V(1, 0, 0)
    fl = Part.makeCylinder(d["fl_d"] / 2, d["fl_t"], P(xo), V(-1, 0, 0))
    thr = Part.makeCylinder(d["hole"] / 2 - 0.1, (xi - xo) + d["nut_t"] + 1.0, P(xo), X)
    nut = Part.makeCylinder(d["nut"] / 2 / 0.866, d["nut_t"], P(xi), X)   # 육각을 외접원으로 (겹침 검사에 넉넉히)
    body = Part.makeCylinder(d["body_d"] / 2, d["body_l"], P(xi + d["nut_t"]), X)
    lug = Part.makeBox(d["lug"], 1.0, 4.0, V(xi + d["nut_t"] + d["body_l"], d["y"] - 0.5, d["z"] - 2.0))
    return Part.makeCompound([fl, thr, nut, body, lug])


def apply(doc):
    rep = {}
    for o in [x for x in doc.Objects if x.Label.startswith(("198x_", "198xc_", "198xs_", "194j_"))]:
        doc.removeObject(o.Name)
    # (11/10 밤, CAP-AI-60) HX711 모듈·받침·나사·데크 탭 구멍 없앰 — 교수님 '로드셀은 과함' → 누름 스위치 (D5g_feeder_uln.press_apply)
    items = []
    pl = [o for o in doc.Objects if o.Label.startswith("194b_")]
    if pl:
        items.append(("194j_dc_jack_panel_5.5x2.1 (DC-099류, 판 구멍 Ø8 — 구동 레일 +5V_B 입력, 배터리 상자도 같은 플러그)", _dc_jack(pl[0]), (0.15, 0.15, 0.15)))
    for nm, shp, col in items:
        o = doc.addObject("Part::Feature", "C3_" + nm.split(" ")[0])
        o.Label = nm
        o.Shape = shp
        if App.GuiUp:
            o.ViewObject.ShapeColor = col
        grp = [g for g in doc.Objects if g.Name == ("GSJ_B" if nm.startswith(("198xc", "194b")) else "GSJ_A")]
        if grp:
            grp[0].addObject(o)
        rep[nm.split(" ")[0]] = [round(v, 1) for v in (shp.BoundBox.XMin, shp.BoundBox.XMax, shp.BoundBox.YMin, shp.BoundBox.YMax, shp.BoundBox.ZMin, shp.BoundBox.ZMax)]
    doc.recompute()
    return rep
