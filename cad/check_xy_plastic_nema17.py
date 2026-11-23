# -*- coding: utf-8 -*-
"""meviy 담당자 견적 6장(YA·YB·XN·YM·CP·SV)을 빼고 플라스틱 6장 + NEMA17 팬케이크로 조립을 다시 맞추고 부딪힘 검사. 승준 11/23, CAP-AI-SJ-63
  판 6장 (21시 최종): YA·YB·YM·XN·SV = PETG 3D 프린트, CP = 아크릴 3T 레이저, YB −x 혀 깎음 + 그 옆 M4 접시머리 Ø8.0 (cad/xy_plates_plastic_1123.py와 같은 구멍 수정 — 조립에서는 이름 치수 구멍)
  같이 바뀌는 것: X 모터 판 217을 +x 레일 바깥 면으로 (+23, x 180~183) · NEMA17 42 × 42 × 23 상자 · T8 나사 Ø8 (X 155, Y 132)
    · T8 너트 (플랜지 Ø22 × 3.5, 몸 Ø10.2, 길이 15) · XN M3 × 6 (2) · CP M3 + 너트 (2) · 217 M4 둥근머리 (2) · 모터 앞 M3 (X 아래 2, Y 3)
  빼는 옛 부품: LM-NK1134 모터·Tr5 나사·POM 너트와 그 나사, 판 212·211·206 (같은 자리에 PL_ 판), 217·217s
  검사: ① 정지 — 새 부품 하나씩 나머지 전부와 ② 움직임 (펜 12.1 mm 든 자세, REF_ 뺌) — 빔 x −38~+37, 캐리지 y 0~58 (대기 −40 기준), 모서리 2곳
  결과 (11/23, 승준 PC D5g_full_SJ1123): 정지에서 실제로 손볼 곳 2 — X 너트 플랜지 ↔ Y 원점 기판 2.5 mm³, Y 너트 플랜지 ↔ LMK8UU 나사 0.25 mm³ × 4
    (나머지는 탭·나사 구멍을 안 그려서 생기는 겹침) · 움직임: 캐리지 +58 (y +18)에서만 SP ↔ YB −x 혀 (x 88.4~90.4 · z 464~, 11/17 끝단 수정)
    — 0.1 mm로 보면 y +17.0부터. 원래 설계 그대로라 플라스틱과 무관, 펌웨어 한계 +18보다 1 mm 짧음 (서현 확인) → cad/_xy_plastic_nema17_check.json
    (21시) YB 혀 깎고 M4 접시머리 Ø8.0으로 다시: 움직임 전부 겹침 0 (캐리지 y 0~58 = 펌웨어 한계 +18까지), 정지는 위와 같음
실행: FreeCAD에서 D5g_full을 연 채로 매크로 실행 (문서에 PL_ 부품을 만들고 옛 부품은 숨김), 또는 freecad.exe cad/check_xy_plastic_nema17.py (cwd = cad)"""
import os, math, json, time
import FreeCAD as App, Part
V = App.Vector; X, Y = V(1, 0, 0), V(0, 1, 0)
T0 = time.time()

def doc():
    for d in App.listDocuments().values():
        if any(o.Label.startswith("217_x_motor_plate") for o in d.Objects): return d
    return App.openDocument(os.path.join(os.getcwd(), "D5g_full.FCStd"))
d = doc()
for o in [o for o in d.Objects if o.Name.startswith("PL_")]: d.removeObject(o.Name)
parts = [o for o in d.Objects if o.TypeId == "Part::Feature" and not o.Shape.isNull() and not o.Name.startswith(("PK_", "PL_"))]
OLD = ("215_x_stepper", "214_x_lead_screw", "225_x_nut", "217_x_motor_plate", "217s_x_motor_screws", "212_beam_plates",
       "209_y_stepper", "208_y_lead_screw", "224_y_nut", "211_y_motor_plate", "206_carriage_plates", "153b_stepper_bolts")
CARR = ("201_", "202_", "202s", "203_", "204_", "205", "206_", "221_", "223_", "224_")          # 캐리지와 같이 (x·y)
BEAM = ("207_", "208_", "209", "210_", "211_", "212_", "222_", "225_", "227y", "153b_", "153n_")  # 빔과 같이 (x)
PEN = ("201_marker", "202_holder_plate", "202_holder_bolts", "203_marker_P_clips")              # 서보로 12.1 mm 듦
def lab(p): return [o for o in parts if o.Label.startswith(p)]
cyl = lambda r, h, p, a: Part.makeCylinder(r, h, p, a)

# ── 판: 문서의 판 고체를 그대로 쓰고 xy_plates_plastic_1123.py와 같은 구멍 수정 (두께 축 d, [t0, t1], 메울 구멍, 새 구멍)
a = math.radians
XN_TAP = [(-65 + 8 * math.cos(a(t)), 425 + 8 * math.sin(a(t))) for t in (150, 240)]
PL = [
 ("YA_PETG", "212_beam_plates", 1, -59.0, -56.0, [], [], "beam"),
 ("YB_PETG", "212_beam_plates", 1, 58.0, 61.0, [], [], "beam"),
 ("XN_PETG", "212_beam_plates", 0, 87.4, 90.4,
  [((-70.5, 421.8), 1.6), ((-59.5, 421.8), 1.6), ((-65.0, 431.35), 3.4)], [((-65.0, 425.0), 10.5)] + [(p, 2.5) for p in XN_TAP], "beam"),
 ("YM_PETG", "211_y_motor_plate", 1, -101.9, -98.9,
  [((89.9, 441.5), 3.0), ((89.9, 464.5), 3.0), ((112.9, 441.5), 3.0), ((112.9, 464.5), 3.0)],
  [((85.9, 437.5), 3.4), ((85.9, 468.5), 3.4), ((116.9, 468.5), 3.4)], "beam"),
 ("CP_acryl", "206_carriage_plates", 1, -47.0, -44.0,
  [((95.901, 456.175), 3.4), ((106.899, 456.175), 3.4), ((101.4, 446.65), 3.4)], [((93.4, 453.0), 3.4), ((109.4, 453.0), 3.4)], "carr"),
 ("SP_metal", "206_carriage_plates", 0, 87.15, 90.15, [], [], "carr"),     # SP는 meviy 금속 그대로 (6장에 안 듦)
 ("SV_PETG", "206_carriage_plates", 0, 100.15, 103.15, [], [], "carr"),
]
def hole(p, dd, r, t0, t1):
    b = [p[0], p[1]]; b.insert(dd, t0); return cyl(r, t1 - t0, V(*b), X if dd == 0 else Y)
def plate(src, dd, t0, t1):
    bb = lambda s: (s.BoundBox.XMin, s.BoundBox.XMax) if dd == 0 else (s.BoundBox.YMin, s.BoundBox.YMax)
    ss = [s for o in lab(src) for s in o.Shape.Solids if abs(bb(s)[0] - t0) < 0.01 and abs(bb(s)[1] - t1) < 0.01]
    assert len(ss) == 1, (src, t0, len(ss)); return ss[0]
NEW = []                                   # (이름, 모양, 무리)
for name, src, dd, t0, t1, fill, new, g in PL:
    s = plate(src, dd, t0, t1)
    for p, dia in fill: s = s.fuse(hole(p, dd, dia / 2 + 0.02, t0, t1))      # +0.02: 좌표 끝수 틈 없게
    for p, dia in new: s = s.cut(hole(p, dd, dia / 2, t0 - 1, t1 + 1))
    if name == "YB_PETG":      # (21시 최종) −x 혀 깎음 — SP가 y +17.0에서 닿던 곳 (xy_plates_plastic_1123.py와 같음)
        s = s.cut(Part.makeBox(2.1, 5, 35.1, V(88.3, 57, 463.9))); fill = True
    NEW.append((name, s.removeSplitter() if (fill or new) else s, g))
pl = plate("217_x_motor_plate", 0, 157.0, 160.0).copy(); pl.translate(V(23, 0, 0))
NEW.append(("217_moved", pl, "fixed"))     # +x 레일 바깥 면 (손 가공: 1:1 도안)

# ── 모터·나사·너트·체결 (치수: 내써팝 23 mm 팬케이크, T8 리드 8 [제조사 표 — 너트 4구멍 PCD 16은 추측])
def nut(p, ax):
    s = cyl(11, 3.5, p, ax).fuse(cyl(5.1, 11.5, p + ax * 3.5, ax))
    return s.cut(cyl(4.05, 25, p - ax * 5, ax)).removeSplitter()
def many(ss):
    return Part.makeCompound(ss)
NEW += [
 ("Xmotor_N17", Part.makeBox(23, 42, 42, V(183, -86, 404)), "fixed"),
 ("Ymotor_N17", Part.makeBox(42, 23, 42, V(80.4, -124.9, 432)), "beam"),
 ("Xscrew_T8", cyl(4, 155, V(28, -65, 425), X), "fixed"),
 ("Yscrew_T8", cyl(4, 132, V(101.4, -101.9, 453), Y), "beam"),
 ("Xnut_T8", nut(V(83.9, -65, 425), X), "beam"),          # 플랜지는 XN −x 면, 몸은 판을 지나 +x
 ("Ynut_T8", nut(V(101.4, -44, 453), Y), "carr"),         # 플랜지는 CP +y 면
 ("XN_M3x6", many([cyl(2.75, 2, V(81.9, y, z), X).fuse(cyl(1.5, 6, V(83.9, y, z), X)) for y, z in XN_TAP]), "beam"),
 ("CP_M3_nut", many([cyl(2.75, 2, V(x, -40.5, 453), Y).fuse(cyl(1.5, 10.9, V(x, -49.4, 453), Y)).fuse(cyl(3.2, 2.4, V(x, -49.4, 453), Y))
                     for x in (93.4, 109.4)]), "carr"),
 ("217_M4", many([cyl(3.8, 2.2, V(183, y, 450), X) for y in (-74, -56)]), "fixed"),           # ISO 7380 M4 dk 7.6
 ("Xmotor_M3low", many([cyl(2.75, 2, V(178, y, 409.5), X) for y in (-80.5, -49.5)]), "fixed"),  # 위 2개는 레일 (z 440~460)이라 못 씀
 ("Ymotor_M3", many([cyl(2.75, 2, V(x, -98.9, z), Y) for x, z in ((85.9, 437.5), (85.9, 468.5), (116.9, 468.5))]), "beam"),
]
COL = {"print": (0.95, 0.55, 0.95), "laser": (0.45, 0.65, 1.0)}
for name, s, g in NEW:
    o = d.addObject("Part::Feature", "PL_" + name); o.Label = "PL_" + name; o.Shape = s
    if App.GuiUp:
        o.ViewObject.ShapeColor = COL["print"] if "PETG" in name else COL["laser"] if "acryl" in name else (0.48, 0.62, 1.0) if "N17" in name else (0.6, 0.6, 0.6)
for o in parts:
    if o.Label.startswith(OLD) and App.GuiUp: o.ViewObject.Visibility = False
d.recompute()

# ── 고체 목록 (라벨, 고체, 무리) — REF_는 뺌 (보기용 원뿔·트랩 자리)
def grp(l):
    return "carr" if l.startswith(CARR) else "beam" if l.startswith(BEAM) else "fixed"
ALL = [(o.Label, s, grp(o.Label)) for o in parts if not o.Label.startswith(OLD + ("REF_",)) for s in (o.Shape.Solids or [o.Shape])]
ALL += [(n, s, g) for n, sh, g in NEW for s in sh.Solids]
# (21시 최종) 혀 옆 M4 접시머리 2개 (YB −y 면, x 94.4 · z 468/492): 모델은 ISO 10642 머리 Ø8.96 → 십자 접시 Ø8.0 (키트 SMG NT-KIT-LS008, 받으면 재 볼 것 ≤ 8.4)
HEAD = [i for i, (l, s, g) in enumerate(ALL) if l.startswith("212_beam_hardware") and s.BoundBox.XMin < 90.5 and s.BoundBox.ZMin > 460 and abs(s.BoundBox.YMin - 58) < 0.1]
for i in reversed(HEAD): ALL.pop(i)
ALL += [("YB_M4접시_머리Ø8", Part.makeCone(4.0, 2.0, 2.2, V(94.4, 58.0, z), Y), "beam") for z in (468, 492)]
def common(s1, s2):
    return s1.common(s2).Volume if s1.BoundBox.intersect(s2.BoundBox) else 0.0

# ① 정지 (펜 내린 자세): 새 부품 고체마다 나머지 전부
R = {"고체 수": len(ALL), "바꾼 M4 머리 고체": len(HEAD), "정지": []}
newn = {n for n, _, _ in NEW}
for i, (l1, s1, _) in enumerate(ALL):
    if l1 not in newn: continue
    for j, (l2, s2, _) in enumerate(ALL):
        if j == i or (l2 in newn and j < i) or l2 == l1: continue
        v = common(s1, s2)
        if v > 0.01: R["정지"].append((l1, l2[:34], round(v, 2)))

# ② 움직임 (펜 든 자세): 1 mm씩, 처음 닿는 곳
A2 = []
for l, s, g in ALL:
    if l.startswith(PEN): s = s.copy(); s.translate(V(0, 0, 12.1))
    A2.append((l, s, g))
def scan(movers, others, path):
    """movers를 path [(dx, dy), …] 따라 옮기며 others와 처음 닿는 곳 → (위치, [(움직이는, 고정, mm³)]) 또는 None"""
    xs = [p[0] for p in path]; ys = [p[1] for p in path]
    near = []
    for l, s, _ in movers:
        b = s.BoundBox
        sw = App.BoundBox(b.XMin + min(xs), b.YMin + min(ys), b.ZMin, b.XMax + max(xs), b.YMax + max(ys), b.ZMax)
        near.append((l, s, [(l2, s2) for l2, s2, _ in others if s2.BoundBox.intersect(sw)]))
    for dx, dy in path:
        h = []
        for l, s, cand in near:
            if not cand: continue
            m = s.copy(); m.translate(V(dx, dy, 0))
            for l2, s2 in cand:
                v = common(m, s2)
                if v > 0.01: h.append((l[:34], l2[:34], round(v, 2)))
        if h: return (dx if dy == 0 else dy, h)
    return None
fx = [t for t in A2 if t[2] == "fixed"]; bm = [t for t in A2 if t[2] == "beam"]; cr = [t for t in A2 if t[2] == "carr"]
M = {}
M["빔_+x (0~+37)"] = scan(bm + cr, fx, [(x, 0) for x in range(0, 38)])
M["빔_-x (0~-38)"] = scan(bm + cr, fx, [(-x, 0) for x in range(0, 39)])
M["캐리지_+y (0~58)"] = scan(cr, fx + bm, [(0, y) for y in range(0, 59)])
def moved(lst, dy):
    out = []
    for l, s, g in lst:
        s = s.copy(); s.translate(V(0, dy, 0)); out.append((l, s, g))
    return out
M["캐리지+57 · 빔_+x"] = scan(bm + moved(cr, 57), fx, [(x, 0) for x in range(0, 38)])
M["캐리지+57 · 빔_-x"] = scan(bm + moved(cr, 57), fx, [(-x, 0) for x in range(0, 39)])
R["움직임"] = M
R["초"] = round(time.time() - T0, 1)
for k, v in R.items(): print(k, v)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd(), "_xy_plastic_nema17_check.json")
try: json.dump(R, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("→", out)
except Exception as e: print("json 못 씀", e)
