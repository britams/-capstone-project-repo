# -*- coding: utf-8 -*-
"""리프트 v3 — 소형 액추에이터 하나로 (서현 11/14 16:34~16:42 "액추에이터로 단순하게, 운동만, 힘 제한은 나중에(거리로)", CAP-AI-62)

v2(MiniSlide + 거더 + 스페이서 + 스프링 + 홀)를 버리고 로드형 액추에이터를 바닥 가운데 밑에 세움.
  300 마킹실 상자 (예외 프린트 1개) 안 Ø33, 바깥 40 × 40, 윗면 z 8.0 + M3 태핑 밑구멍 Ø2.5 4 (±15, ±15) (11/15 인서트 없앰)
  300p 투명 아크릴 격자판 40 × 40 × 2 (예외 주문 제작, 11/14 17:25 서현) 네모 구멍 3.0 간격 4.4 — 카메라가 막대 너머도 봄
  301 mightyZAP D7-6PT-3 (아이알로봇, 디바이스마트 101,000원) 행정 26, 6 N, 7.4 V, PWM 900~2100 µs로 위치 지정
      [확실 — 판매처 도면 d12d7_xxxx_3 rev03]: 몸통 57.5 × 29.5 × 15, 로드 끝 M3 암나사 + M3 너트, 뒤 경첩 구멍 Ø3.5 (몸통 뒤 7.6)
      판매처 STEP은 PC 받은도면에만 (공개 레포에 안 올림). 없으면 대표 모양
  304 바닥: 로드 끝 M3 × 8 무두 볼트 + M3 너트(로드 잠금) + 아크릴 원판 Ø32 × 2T 구멍 Ø3.4 (격자판과 같이 주문 제작 — 너트 위에 얹힘, 볼트가 가운데를 잡음)
      (11/14 23:40) McMaster 90313A108 + M4 DIN 9021은 해외구매라 정산 불가 → 바꿈 (CAP-AI-62)
      볼트 끝은 바닥 구멍 안 (윗면보다 낮음). 바닥 바깥 31.75가 상자 안 Ø33에 끼워져 옆을 잡음
  309 경첩 고정: M3 × 20 냄비 + M3 원형 스페이서 Ø6 × 4 (경첩 8.6 ↔ 몸통 15 차이 메움) + 2020 M3 T너트 → 세운 2020 막대 옆 홈
  307 2020 막대 2개: 상자용(가로, v2와 같음) + 액추에이터용(세움, 100 mm). 프레임과는 아직 안 맞춤
  행정: 바닥 z −7 (쉼, 로드 8 mm 나옴) → z +3 (누름, 18 mm) — 액추에이터 행정 26 안. 멈춤은 거리(PWM)로
좌표: 마킹실 가운데 축 (0, 0), z 위 (lift_v2와 같음)
"""
import os
import glob
import math
import FreeCAD as App
import Part
import lift_v2 as L

V = App.Vector
STEP = glob.glob(os.path.join(L.STEP_DIR, "mightyZAP_D12D7-xxxx-3*.step"))
ROD_IDS = (28, 29)                         # STEP에서 움직이는 로드
DROP_IDS = (20, 30)                        # 판매처 끝 너트·볼 끝 (안 씀 — 바닥으로 바꿈)
ACT = dict(front=42.0, rear=-15.5, rod_face=45.8, hinge_back=7.6, hinge_d=3.5, half_t=7.63)   # STEP 좌표 (축 z, 로드 +z)
S_REST, STROKE = 8.0, L.STROKE              # 쉼 = 로드 8 mm 나옴, 누름까지 10
FLOOR_TOP = L.H["rest"]                     # −7
NUT_T, DISC = 2.4, (32.0, 3.4, 2.0)         # 바닥 = 아크릴 원판 (격자판과 같은 2T 판, DXF print/lift/300f_아크릴바닥원판.dxf)
STACK = NUT_T + DISC[2]                     # 로드 끝 → 바닥 윗면 4.4 (11/14 전 4.67)
Z0 = FLOOR_TOP - STACK - (ACT["rod_face"] + S_REST)
SPACER = (6.0, 3.2, 4.0)                    # M3 원형 스페이서 (나사 없음) Ø6 × 4 [상품 미정]
INFO = {}
WORLD = V(55, 0, 377)                       # 전체 좌표로 옮길 때 (마킹실 가운데 (55, 0), 격자 아래 385)
DECK_TOP = 205.0                             # 데크 윗면 (전체 좌표)
VBAR = dict(top=-16.0)                       # 전체 좌표 361 — +x 방생 문 하우징 아래 끝(362.5)보다 1.5 아래 (11/14 1단계 검사)
VBAR["L"] = VBAR["top"] - (DECK_TOP - WORLD.z)   # 161.5 — 데크까지 (2020 길이 주문 절단, 프레임 막대와 같은 방식) [가능성 높음]


def nut(z0):
    R = 5.5 / 3 ** 0.5
    pg = Part.makePolygon([V(R * math.cos(math.radians(60 * k)), R * math.sin(math.radians(60 * k)), z0) for k in range(7)])
    return Part.Face(pg).extrude(V(0, 0, NUT_T)).cut(L.cyl(1.5, NUT_T + 2, V(0, 0, z0 - 1)))


def actuator():
    """반환 (몸통, 로드, 경첩 구멍 가운데 z(STEP), 경첩 x 범위, 출처) — STEP 좌표"""
    if STEP:
        sol = Part.read(STEP[0]).Solids
        body = Part.makeCompound([s for i, s in enumerate(sol) if i not in ROD_IDS + DROP_IDS])
        rod = Part.makeCompound([sol[i] for i in ROD_IDS])
        hinge = sol[21]
        vx = [(hinge.common(L.cyl(1.6, 20, V(-10, 0, z), V(1, 0, 0))).Volume, z) for z in [-24 + 0.1 * k for k in range(61)]]
        vy = [(hinge.common(L.cyl(1.6, 20, V(0, -10, z), V(0, 1, 0))).Volume, z) for z in [-24 + 0.1 * k for k in range(61)]]
        INFO.update(hole_x=min(vx), hole_y=min(vy), hinge_bb=[round(v, 2) for v in (hinge.BoundBox.XMin, hinge.BoundBox.XMax,
                    hinge.BoundBox.YMin, hinge.BoundBox.YMax, hinge.BoundBox.ZMin, hinge.BoundBox.ZMax)])
        zs = [z for v, z in vx if v < 0.05]
        zc = round(sum(zs) / len(zs), 2)
        x = hinge.common(L.box(-10, 10, 2.6, 3.0, zc - 0.2, zc + 0.2)).BoundBox
        INFO.update(eye_x=(round(x.XMin, 2), round(x.XMax, 2)), zc=zc)
        return body, rod, zc, (x.XMin, x.XMax), "STEP"
    zc = ACT["rear"] - ACT["hinge_back"]
    body = L.box(-7.5, 7.5, -20.1, 9.4, ACT["rear"], ACT["front"]).fuse(L.box(-2.5, 2.5, -3, 3, zc - 4, ACT["rear"]))
    body = body.cut(L.cyl(ACT["hinge_d"] / 2, 10, V(-5, 0, zc), V(1, 0, 0)))
    return body, L.cyl(3.25, ACT["rod_face"] - 2.6, V(0, 0, 2.6)), zc, (-2.5, 2.5), "대표"


def floor_stack(f):
    """로드 끝 면 f (세계 z)에서 위로: 무두 볼트 M3 × 8 (로드에 4.5), 잠금 너트, 아크릴 원판 (얹힘 — 볼트 끝 f + 3.5는 원판 구멍 안, 윗면 f + 4.4 아래)"""
    stud = L.cyl(1.5, 8.0, V(0, 0, f - 4.5))
    n1 = nut(f)
    return L.washer(*DISC, f + NUT_T), Part.makeCompound([stud, n1])


def make(doc=None):
    doc = doc or App.newDocument("Lift_v3")
    body, rod, zc, (ex0, ex1), src = actuator()
    m = App.Matrix()
    m.move(V(0, 0, Z0))
    body, rod = body.transformed(m), rod.transformed(m)
    rod.translate(V(0, 0, S_REST))
    zh = zc + Z0
    fl, hw = floor_stack(ACT["rod_face"] + S_REST + Z0)
    # 경첩 → 세운 막대: 원형 스페이서 하나로 틈을 메움 (막대 면은 몸통 옆면 7.63보다 바깥)
    face = ex1 + SPACER[2]
    assert face > ACT["half_t"] + 0.2
    ws = [L.washer(*SPACER, 0).transformed(App.Placement(V(ex1, 0, zh), App.Rotation(V(0, 0, 1), V(1, 0, 0))).toMatrix())]
    scr = L.pan(V(ex0, 0, zh), V(1, 0, 0), 3.0, 20.0)
    tn = L.box(face + 1.5, face + 5.0, -3.0, 3.0, zh - 5, zh + 5)
    vb = L.box(face, face + 20, -10, 10, VBAR["top"] - VBAR["L"], VBAR["top"]).cut(
        L.box(face - 1, face + 6, -3.1, 3.1, VBAR["top"] - VBAR["L"] - 1, VBAR["top"] + 1)).cut(
        L.box(face + 10 - 3.1, face + 10 + 3.1, 4, 11, VBAR["top"] - VBAR["L"] - 1, VBAR["top"] + 1))      # +y 홈 (상자 혀)
    # (11/15) 세운 막대 밑을 데크에 고정 — 빠져 있던 것. −y 면에 L 브래킷 DCB 2025 (20 × 25, 두께 4 [추측 — 판매처 치수 없음]):
    #   세로 다리 → 막대 −y 홈 (M5 × 8 + 20시리즈 스프링너트), 가로 다리 → 데크 (M5 × 12 위에서 + 너트 데크 밑, 데크 구멍 Ø5.5)
    zb = VBAR["top"] - VBAR["L"]
    cx = face + 10
    brk = L.box(face, face + 20, -14, -10, zb, zb + 25).fuse(L.box(face, face + 20, -30, -10, zb, zb + 4))
    bs = [L.pan(V(cx, -14, zb + 16), V(0, 1, 0), 5.0, 8.0), L.box(cx - 5, cx + 5, -9.5, -5.0, zb + 13, zb + 19),
          L.pan(V(cx, -22, zb + 4), V(0, 0, -1), 5.0, 12.0), L.box(cx - 4, cx + 4, -26, -18, zb - 5 - 4, zb - 5)]
    INFO["deck_hole_world"] = (round(WORLD.x + cx, 2), round(WORLD.y - 22, 2), 5.5)
    tx, ty, tt, td = L.BOXD["tongue"]
    ts = []
    for z in L.BOXD["tongue_holes"]:
        ts.append(L.pan(V(tx, ty + tt, z), V(0, -1, 0), 5.0, 10.0))
        ts.append(L.box(tx - 5, tx + 5, 5.0, 9.0, z - 3, z + 3))                                       # 2020 M5 T너트

    gray, dark, green = (0.75, 0.75, 0.77), (0.35, 0.35, 0.37), (0.2, 0.7, 0.3)
    rows = [("300_marking_box (마킹실 상자 + 윗면 격자 Ø3 간격 4.4 — 예외 부품 1개, 프린트 파일 print/lift/300_마킹실상자)", L.marking_box(), green, 50),
            ("300p_acrylic_plate (투명 아크릴 격자판 40 × 40 × 2, 네모 구멍 3.0 간격 4.4 — 주문 제작, DXF print/lift/300p_아크릴격자판.dxf)", L.acrylic_plate(), (0.55, 0.75, 0.95), 60),
            ("300s_plate_screws (M3 × 8 냄비 태핑 4 + M3 DIN 125 4 — 상자 밑구멍 Ø2.5, 구매)", L.plate_screws(), dark, 0),
            ("301_mightyZAP_D7-6PT-3 (몸통 — 행정 26, 6 N, 7.4 V, PWM, 디바이스마트, 구매) [%s]" % src, body, gray, 0),
            ("301r_rod (로드 — 움직임) [%s]" % src, rod, gray, 0),
            ("304_floor (바닥 아크릴 원판 Ø32 × 2T 구멍 Ø3.4 — 격자판과 같이 주문 제작, 로드 끝 너트 위에 얹힘)", fl, (0.55, 0.75, 0.95), 0),
            ("304s_stud_nut (M3 × 8 무두 볼트 + M3 너트 — 로드 끝, 구매)", hw, dark, 0),
            ("307v_bar_act (2020 %.1f mm 세움 — 데크 → 상자 밑, 액추에이터 경첩·상자 혀, 구매)" % VBAR["L"], vb, (0.8, 0.8, 0.82), 0),
            ("308s_tongue_screws (M5 × 10 둥근머리 렌치 2 + 20시리즈 M5 스프링너트 2 — 상자 혀 → 세운 막대, 구매)", Part.makeCompound(ts), dark, 0),
            ("307b_bar_bracket (L 브래킷 DCB 2025 — 세운 막대 −y 면 → 데크, 디바이스마트 24022, 구매)", brk, gray, 0),
            ("307s_bar_bracket_screws (M5 × 8 + 스프링너트 — 막대, M5 × 12 + M5 너트 — 데크 구멍 Ø5.5, 구매)", Part.makeCompound(bs), dark, 0),
            ("309s_hinge_screw (M3 × 20 냄비 + 틈 4 = M3 너트 1 + M3 DIN 125 와셔 3 (Ø6 × 4 스페이서 대신 — 해외품) + 2020 홈 안 M3 너트, 구매)",
             Part.makeCompound([scr, tn] + ws), dark, 0)]
    for i, (lab, shp, col, tr) in enumerate(rows):
        o = doc.addObject("Part::Feature", "P%02d" % i)
        o.Shape, o.Label = shp, lab
        if App.GuiUp:
            o.ViewObject.ShapeColor = col
            o.ViewObject.Transparency = tr
    doc.recompute()
    return doc


MOVING = ("301r", "304")
ALLOW = (("300s", "300_"), ("300s", "300p"), ("301r", "301_"), ("304s", "301r"), ("304s", "304_"),
         ("308s", "307v"), ("308s", "300_"), ("307s", "307b"), ("307s", "307v"), ("307b", "307v"), ("309s", "301_"), ("309s", "307v"))


def check(doc):
    """(1) 쉼 → 누름 2 mm씩 움직이는 것 ↔ 고정 (2) 고정끼리 (3) 펜이 닿는 망 구멍 수 (4) 로드 행정 안"""
    key = lambda o: o.Label.split(" ")[0]
    ok = lambda a, b: any(a.startswith(p) and b.startswith(q) or b.startswith(p) and a.startswith(q) for p, q in ALLOW)
    obs = [o for o in doc.Objects if hasattr(o, "Shape")]
    mv = [o for o in obs if key(o).startswith(MOVING)]
    fx = [o for o in obs if o not in mv]

    def vol(a, sa, b, sb):
        if ok(key(a), key(b)) or not sa.BoundBox.intersect(sb.BoundBox):
            return 0.0
        return sa.common(sb).Volume
    sweep = []
    for dz in [2.0 * k for k in range(int(STROKE / 2) + 1)]:
        for a in mv:
            sa = a.Shape.copy()
            sa.translate(V(0, 0, dz))
            for b in fx:
                v = vol(a, sa, b, b.Shape)
                if v > 0.01:
                    sweep.append((dz, key(a), key(b), round(v, 2)))
    static = [(key(a), key(b), round(v, 2)) for i, a in enumerate(fx) for b in fx[i + 1:]
              for v in [vol(a, a.Shape, b, b.Shape)] if v > 0.01]
    fixed_pen = [o.Shape for o in obs if key(o) in ("300_marking_box", "300p_acrylic_plate", "300s_plate_screws")]
    n_ok = n_all = 0
    for x, y in L.grid_centers():
        n_all += 1
        if not any(L.pen(x, y, L.BOXD["z_mesh"]).common(f).Volume > 0.001 for f in fixed_pen):
            n_ok += 1
    fl = [o for o in obs if key(o) == "304_floor"][0].Shape.BoundBox
    body = [o for o in obs if key(o).startswith("301_")][0].Shape.BoundBox
    return dict(sweep=sweep, static=static, pen_holes=(n_ok, n_all), floor_top=(round(fl.ZMax, 2), round(fl.ZMax + STROKE, 2)),
                rod_out=(S_REST, S_REST + STROKE, 26.0), body_z=(round(body.ZMin, 2), round(body.ZMax, 2)),
                info=INFO, gap_mesh_press=round(L.BOXD["z_mesh"] - (fl.ZMax + STROKE), 2))
