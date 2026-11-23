# -*- coding: utf-8 -*-
"""XY 모터를 NEMA17 팬케이크(42 × 42 × 23) + T8 리드 8로 바꾸면 부딪히나 — 검사만 (모델은 안 고침). 승준 11/23, CAP-AI-SJ-63
  배경: 모터뱅크 LM-NK1134가 12/4 이후 도착 → 12/2 시연용으로 내써팝 NEMA17 23 mm + TM 200 (절단). 판은 이미 주문 — 손 가공만.
  검사: ① X·Y 몸 지금 자리 ② Y 몸 x 움직임 (빔과 함께) ③ X 수정안 = 217 판을 +x 갠트리 레일 바깥 면으로 (+23) ④ 새 나사 머리·너트
  결과 (11/23, 승준 PC D5g_full_SJ1118): X 지금 자리 레일 2387 mm³ → 수정안 0 · Y 0 · 원점 쪽 여유 2.0 → 1.4 mm · 새 나사 0
  (M5 머리는 X 몸에 7 mm³ → M4). 판 수정 PDF: design/2026-11-23_XY모터_NEMA17/
실행: FreeCAD에서 D5g_full을 연 채로 매크로 실행, 또는 freecad.exe cad/check_xy_nema17_pancake.py (cwd = cad, D5g_full.FCStd를 엶)"""
import os, math, json
import FreeCAD as App, Part
V = App.Vector; X, Y = V(1, 0, 0), V(0, 1, 0)

def doc():
    for d in App.listDocuments().values():
        if any(o.Label.startswith("217_x_motor_plate") for o in d.Objects): return d
    return App.openDocument(os.path.join(os.getcwd(), "D5g_full.FCStd"))
d = doc()
parts = [o for o in d.Objects if o.TypeId == "Part::Feature" and not o.Shape.isNull() and not o.Name.startswith("PK_")]
def lab(p): return [o for o in parts if o.Label.startswith(p)]
def one(p): return lab(p)[0]
OLD = ("215_x_stepper", "209_y_stepper", "214_x_lead_screw", "208_y_lead_screw", "153b_stepper_bolts", "225_x_nut", "224_y_nut")
MOVE = ("212_", "211_", "206_", "221_", "222_", "224_", "225_", "209_", "208_", "227y", "227ym", "153b")   # 빔·캐리지와 같이 움직임
fixed = [o for o in parts if not o.Label.startswith(MOVE) and not o.Label.startswith(OLD)]
others = [o for o in parts if not o.Label.startswith(OLD)]

def hits(sh, objs, skip=()):
    return [(o.Label[:40], round(o.Shape.common(sh).Volume, 2)) for o in objs
            if not o.Label.startswith(skip) and o.Shape.BoundBox.intersect(sh.BoundBox) and o.Shape.common(sh).Volume > 0.01]
def first_hit(sh, objs, steps):
    for dx in steps:
        s = sh.copy(); s.translate(V(dx, 0, 0))
        h = hits(s, objs)
        if h: return dx, h
    return None
cyl = lambda r, h, p, a: Part.makeCylinder(r, h, p, a)
R = {}
# 모터 자리 (LM-NK1134 축 그대로): X 축 y −65 z 425, 몸 앞면 x 160, 나사 −x / Y 축 x 101.4 z 453, 몸 앞면 y −101.9, 나사 +y
Xb = Part.makeBox(23, 42, 42, V(160, -86, 404)); Yb = Part.makeBox(42, 23, 42, V(80.4, -124.9, 432))
R["X_지금자리"] = hits(Xb, others, ("217_x_motor_plate",))
R["Y_지금자리"] = hits(Yb, others, ("211_y_motor_plate",))
R["X_T8_d8"] = hits(cyl(4, 132, V(28, -65, 425), X), others)
R["Y_T8_d8"] = hits(cyl(4, 132, V(101.4, -101.9, 453), Y), others)
# Y 몸은 빔과 같이 x로 움직임 — 고정 부품과 처음 닿는 곳 (판 211과 비교)
yp = one("211_y_motor_plate").Shape
R["Y_몸_-x"] = first_hit(Yb, fixed, [-i * 0.1 for i in range(0, 600)])
R["Y_판_-x"] = first_hit(yp, fixed, [-i * 0.1 for i in range(0, 600)])
R["Y_몸_+x"] = first_hit(Yb, fixed, [i * 0.5 for i in range(0, 200)])
R["Y_판_+x"] = first_hit(yp, fixed, [i * 0.5 for i in range(0, 200)])
# X 수정안: 217 판 +23 (레일 바깥 면 x 180~183), 몸 x 183~206, T8 Ø8 × 155 (끝 x 28 그대로)
pl = one("217_x_motor_plate").Shape.copy(); pl.translate(V(23, 0, 0))
R["X안_판"] = hits(pl, others, ("217_x_motor_plate", "217s_x_motor_screws"))
R["X안_몸"] = hits(Part.makeBox(23, 42, 42, V(183, -86, 404)), others)
R["X안_T8"] = hits(cyl(4, 155, V(28, -65, 425), X), others)
xm = Part.makeBox(23, 42, 42, V(183, -86, 404))
for yy in (-74, -56):
    R["X안_M5머리%d_몸" % yy] = round(cyl(4.75, 2.75, V(183, yy, 450), X).common(xm).Volume, 2)   # ISO 7380 M5 dk 9.5
    R["X안_M4머리%d_몸" % yy] = round(cyl(3.8, 2.2, V(183, yy, 450), X).common(xm).Volume, 2)    # ISO 7380 M4 dk 7.6
for yy in (-80.5, -49.5):
    for zz in (409.5, 440.5):                       # 모터 앞 M3 (31 간격) 머리는 레일 쪽 판 면 (x 180)
        R["X안_M3냄비(%g,%g)" % (yy, zz)] = hits(cyl(2.75, 2.0, V(178, yy, zz), X), others)
for x in (85.9, 116.9):
    for zz in (437.5, 468.5):                       # Y 모터 앞 M3 머리는 판 +y 면 (y −98.9)
        R["Y_M3냄비(%g,%g)" % (x, zz)] = hits(cyl(2.75, 2.0, V(x, -98.9, zz), Y), others)
# T8 너트 (플랜지 Φ22 × 3.5, 4구멍 PCD 16 [추측], 몸 Φ10.2) — XN: 플랜지 −x 면, 몸 +x로 판 통과 / CP: 플랜지 +y 면
R["XN_플랜지"] = hits(cyl(11, 3.5, V(83.9, -65, 425), X), others, ("212_beam_plates",))
for ang in (150, 240):                              # +y에서 +z 쪽으로 잰 각도 — 2개만 (스위치·옛 M2·판 끝 피함), M3 탭
    a = math.radians(ang); yy, zz = -65 + 8 * math.cos(a), 425 + 8 * math.sin(a)
    R["XN_M3(%d°)머리" % ang] = hits(cyl(2.75, 2.0, V(81.9, yy, zz), X), others)
    R["XN_M3x6(%d°)끝" % ang] = hits(cyl(1.5, 6.0, V(83.9, yy, zz), X), others, ("212_beam_plates",))
R["CP_플랜지"] = hits(cyl(11, 3.5, V(101.4, -44, 453), Y), others, ("206_carriage_plates",))
for x in (93.4, 109.4):                             # 가로 2개 + 뒤 너트 (세로는 너트가 LMK8UU 플랜지에 닿음)
    R["CP_M3(%g)머리" % x] = hits(cyl(2.75, 2.0, V(x, -40.5, 453), Y), others)
    R["CP_M3(%g)너트" % x] = hits(cyl(3.2, 2.4, V(x, -49.4, 453), Y), others)
for k, v in R.items(): print(k, v)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd(), "_xy_nema17_check.json")
try: json.dump(R, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("→", out)
except Exception as e: print("json 못 씀", e)
