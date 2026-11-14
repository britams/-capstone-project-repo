# -*- coding: utf-8 -*-
"""리프트 v3 — 소형 액추에이터 하나로 (서현 11/14 16:34~16:42 "액추에이터로 단순하게, 운동만, 힘 제한은 나중에(거리로)", CAP-AI-62)

v2(MiniSlide + 거더 + 스페이서 + 스프링 + 홀)를 버리고 로드형 액추에이터를 바닥 가운데 밑에 세움.
  300 마킹실 상자 (예외 프린트 1개) · 망 · 망 나사 — lift_v2 그대로
  301 mightyZAP D7-6PT-3 (아이알로봇, 디바이스마트 101,000원) 행정 26, 6 N, 7.4 V, PWM 900~2100 µs로 위치 지정
      [확실 — 판매처 도면 d12d7_xxxx_3 rev03]: 몸통 57.5 × 29.5 × 15, 로드 끝 M3 암나사 + M3 너트, 뒤 경첩 구멍 Ø3.5 (몸통 뒤 7.6)
      판매처 STEP은 PC 받은도면에만 (공개 레포에 안 올림). 없으면 대표 모양
  304 바닥: 로드 끝 M3 × 10 무두 볼트 + M3 너트(아래, 로드 잠금) + M4 DIN 9021 + M10 DIN 9021(밟는 면) + M3 너트(위, 바닥 구멍 안 — 윗면보다 낮음)
      바닥 바깥 30이 상자 안 Ø31에 끼워져 로드를 똑바로 잡음
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
NUT_T, M4W, M10W = 2.4, (12.0, 4.3, 1.0), (30.0, 10.5, 2.5)
STACK = NUT_T + M4W[2] + M10W[2]           # 로드 끝 → 바닥 윗면 5.9
Z0 = FLOOR_TOP - STACK - (ACT["rod_face"] + S_REST)
SPACER = (6.0, 3.2, 4.0)                    # M3 원형 스페이서 (나사 없음) Ø6 × 4 [상품 미정]
INFO = {}
VBAR = dict(L=100.0, top=L.BOXD["z_bot"] - 0.5)


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
    """로드 끝 면 f (세계 z)에서 위로: 무두 볼트, 아래 너트, M4 와셔, M10 와셔, 위 너트"""
    stud = L.cyl(1.5, 10.0, V(0, 0, f - 4.5))
    n1 = nut(f)
    w4 = L.washer(*M4W, f + NUT_T)
    w10 = L.washer(*M10W, f + NUT_T + M4W[2])
    n2 = nut(f + NUT_T + M4W[2])
    return Part.makeCompound([w4, w10]), Part.makeCompound([stud, n1, n2])


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
        L.box(face - 1, face + 6, -3.1, 3.1, VBAR["top"] - VBAR["L"] - 1, VBAR["top"] + 1))
    mesh, clamp = L.mesh_and_clamp()
    bars, rs, bs = L.frame()
    gray, dark, green = (0.75, 0.75, 0.77), (0.35, 0.35, 0.37), (0.2, 0.7, 0.3)
    rows = [("300_marking_box (마킹실 상자 — 예외 부품 1개, 프린트 파일 print/lift/300_마킹실상자)", L.marking_box(), green, 50),
            ("300m_mesh (스테인리스 타공 원판 Ø33 × 0.5, 구매) [상품 미정]", mesh, gray, 0),
            ("300c_mesh_clamp (M3 × 6 냄비 4 + M3 DIN 9021 4 + M3 열압입 인서트 4, 구매)", clamp, dark, 0),
            ("301_mightyZAP_D7-6PT-3 (몸통 — 행정 26, 6 N, 7.4 V, PWM, 디바이스마트, 구매) [%s]" % src, body, gray, 0),
            ("301r_rod (로드 — 움직임) [%s]" % src, rod, gray, 0),
            ("304_floor (바닥 M10 DIN 9021 + M4 DIN 9021 — 로드 끝, 구매)", fl, gray, 0),
            ("304s_stud_nuts (M3 × 10 무두 볼트 + M3 너트 2 — 로드 끝, 구매)", hw, dark, 0),
            ("307_bar_box (2020 100 mm — 상자 날개, 구매)", Part.makeCompound([L.bar(L.Z_BAR[0], L.Y_BAR_FRONT[0])]), (0.8, 0.8, 0.82), 0),
            ("307v_bar_act (2020 100 mm 세움 — 액추에이터 경첩, 구매)", vb, (0.8, 0.8, 0.82), 0),
            ("308s_box_screws (M4 × 10 냄비 2 + 2020 M4 T너트 2, 구매)", bs, dark, 0),
            ("309s_hinge_screw (M3 × 20 냄비 + M3 원형 스페이서 Ø6 × 4 + 2020 M3 T너트, 구매)",
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
ALLOW = (("300c", "300_"), ("300c", "300m"), ("301r", "301_"), ("304s", "301r"), ("304s", "304_"),
         ("308s", "307_"), ("308s", "300_"), ("309s", "301_"), ("309s", "307v"))


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
    fixed_pen = [o.Shape for o in obs if key(o) in ("300_marking_box", "300c_mesh_clamp")]
    n_ok = n_all = 0
    n = int(L.MESH["d"] / 2 / L.MESH["p"]) + 1
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, y = i * L.MESH["p"], j * L.MESH["p"]
            if math.hypot(x, y) >= L.BOXD["bore"] / 2 - 1.1:
                continue
            n_all += 1
            if not any(L.pen(x, y, L.BOXD["z_mesh"]).common(f).Volume > 0.001 for f in fixed_pen):
                n_ok += 1
    fl = [o for o in obs if key(o) == "304_floor"][0].Shape.BoundBox
    body = [o for o in obs if key(o).startswith("301_")][0].Shape.BoundBox
    return dict(sweep=sweep, static=static, pen_holes=(n_ok, n_all), floor_top=(round(fl.ZMax, 2), round(fl.ZMax + STROKE, 2)),
                rod_out=(S_REST, S_REST + STROKE, 26.0), body_z=(round(body.ZMin, 2), round(body.ZMax, 2)),
                info=INFO, gap_mesh_press=round(L.BOXD["z_mesh"] - (fl.ZMax + STROKE), 2))
