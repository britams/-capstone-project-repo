# -*- coding: utf-8 -*-
"""리프트 v2 — 기성품 + 나사만, 마킹실 상자 하나만 예외 (CAP-AI-62, 서현 11/12)

서현 지시: 14:34 "3D 프린트 절대 쓰지 마, 절단·재단도 못 해, 나사로 조이는 것만" · 14:45 MiniSlide · 15:10 제일 싼 것
  16:09 "마킹실 상자 하나만 예외" · 16:22 "검정 원통(망 위 무게)이 있으면 말벌을 못 찍음, 파란 부품·나사·초록 이음 제대로"
다른 부분과 아직 안 맞춤 — 리프트부만. 좌표: 마킹실 가운데 축 = (0, 0), z 위.

  300 마킹실 상자 (예외: 3D 프린트 또는 판매처 가공 1개) 바깥 46 × 46 × 18.5 (z −10 ~ 8.5)
      안 Ø31 (바닥 쪽 뚫림 — 바닥이 올라옴), 망 턱 z 8.0 (윗면에서 0.5 파인 Ø33.4), 망 위는 비어 있음 → 펜이 위에서 바로
      입구 Ø13 (−x) · 격리 Ø13 (+y), 구멍 아래 끝 = 바닥 윗면 z −7 → 문을 열면 바로 바닥 (벽 7.5)
      뒤 날개 2개 (M4 구멍) → 상자 막대 T너트. 망은 M3 열압입 인서트 4 + M3 × 6 + M3 DIN 9021 와셔로 테두리를 누름
  301 Haydon Kerk MiniSlide MSA02S-C0039-805 (50 mm, 리드 1 mm, 20 mm 캔스택 7.5°, 5 V 350 mA) [확실 — 판매처 STEP, PC에만]
  302 메카노 앵글 거더 1½" (구멍 Ø4.1, 간격 12.7) — 캐리지 위 구멍 줄에 M3 × 6 두 개 [두께·구멍 자리 추측]
  303 기둥: M3 육각 스페이서 암-암 20 + 받침 (M6 DIN 9021 + M4 DIN 9021, M3 × 8)
  !! (11/12 16:30) 아래 304 '바닥 덩어리' 방식은 틀림 — 기둥이 덩어리를 밑에서 받쳐 밀면 덩어리가 멈출 수 없어 힘을 못 막음.
     바닥 ↔ 기둥 사이 스프링으로 바꿀 것 (스프링 상품 고르는 중, McMaster 로그인 대기). 이 판은 실행·검사 안 함.
  304 바닥 덩어리 (기둥 위에 얹혀 있을 뿐 — 누르는 힘 상한 = 이 무게):
      M10 DIN 9021 (바깥 30 · 안 10.5 · 2.5) + M10 DIN 125 10장 (바깥 20 · 안 10.5 · 2) + 원판 자석 6 × 3 (와셔 테에 붙음)
      → 계산 약 48.6 g = 0.48 N [가능성 높음 — 강철 7.85, 저울로 장수 맞춤]
      바닥이 말벌을 이보다 세게 밀면 덩어리는 멈추고 기둥만 더 올라감 → 홀 센서가 자석과 어긋남을 보고 멈춤
  306 홀 모듈 KY-024 (SS49E + LM393, DO → UNO A1): 판을 눕혀 거더 구멍 위 M3 스페이서 20에 M3 × 6, 칩은 자석 옆 0.5 [모듈 치수 추측]
  307 2020 100 mm 3개 (상자 · 레일 위 블록 · 레일 아래 블록), 레일은 M3 × 10 무두 볼트 + T너트
  행정 = 망 아래 z 8.0 − 눌린 말벌 5 − 바닥 −7 = 10 mm
"""
import os
import glob
import math
import FreeCAD as App
import Part

V = App.Vector
STEP_DIR = r"C:\Users\Seohyun_Lee\Desktop\capstone design\받은도면 step파일"

BOXD = dict(half=23.0, z_bot=-10.0, z_top=8.5, bore=31.0, mesh_rec=33.4, z_mesh=8.0, hole=13.0,
            wing=(23.0, 35.0), wing_t=4.0, ins=(13.0, 13.0), ins_d=4.0, ins_L=5.0)
MESH = dict(d=33.0, t=0.5, hole=2.6, p=3.2)                # 스테인리스 타공 원판 [상품 미정]. 펜 팁 2.2가 구멍 2.6을 지남
PEN = dict(tip_d=2.2, tip_L=8.0, nose_d=7.2, body_d=14.7, body_from=15.6, L=134.6)   # 승준 11/02 캘리퍼스
H = dict(rest=-7.0, press=BOXD["z_mesh"] - 5.0)
STROKE = H["press"] - H["rest"]                              # 10
FLOOR = dict(od=30.0, id=10.5, t=2.5)                        # M10 DIN 9021
WGT = dict(od=20.0, id=10.5, t=2.0, n=10)                    # M10 DIN 125
MAG = dict(d=6.0, t=3.0)
PAD = ((12.0, 4.3, 1.0), (18.0, 6.4, 1.6))                   # M4 DIN 9021 (위), M6 DIN 9021 (아래)
SO = 20.0                                                    # M3 스페이서 암-암 20
G = dict(L=38.1, w=12.7, t=1.0, hole=4.1, p=12.7, hole_from_out=6.6)
YC = -G["hole_from_out"]
ZR = -33.0                                                   # 레일 국부 x → 세계 z (레일 위 끝 −31.5 < 덩어리 아래 −29.5)
CAR_RANGE = (-85.69, -9.0)
HALLD = dict(L=32.0, W=14.0, t=1.6, x0=13.2, hole_x=25.4, chip=(1.6, 4.0, 3.0))
SCREW = {2.0: (4.0, 1.6), 2.5: (5.0, 2.0), 3.0: (5.6, 2.4), 4.0: (8.0, 3.1)}    # ISO 7045 머리 지름·높이 [확실 — 규격]
RHO = dict(steel=7.85, ndfeb=7.5)


def cyl(r, h, p, d=V(0, 0, 1)):
    return Part.makeCylinder(r, h, p, d)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def washer(od, idd, t, z0, xy=(0, 0)):
    return cyl(od / 2, t, V(xy[0], xy[1], z0)).cut(cyl(idd / 2, t + 2, V(xy[0], xy[1], z0 - 1)))


def pan(p, d, size, L):
    """ISO 7045 십자 냄비머리: p = 머리 밑면 가운데, d = 몸통 방향, L = 몸통 길이"""
    dk, k = SCREW[size]
    s = cyl(dk / 2, k, V(0, 0, -k)).fuse(cyl(size / 2, L, V(0, 0, 0)))
    w, ln = 0.18 * dk, 0.55 * dk
    s = s.cut(box(-ln / 2, ln / 2, -w / 2, w / 2, -k - 0.1, -0.4 * k)).cut(box(-w / 2, w / 2, -ln / 2, ln / 2, -k - 0.1, -0.4 * k))
    return s.removeSplitter().transformed(App.Placement(V(p), App.Rotation(V(0, 0, 1), V(d))).toMatrix())


def hexso(x, y, z0, L):
    """M3 육각 스페이서 (맞변 5.5)"""
    R = 5.5 / 3 ** 0.5
    pg = Part.makePolygon([V(x + R * math.cos(math.radians(60 * k + 30)), y + R * math.sin(math.radians(60 * k + 30)), z0) for k in range(7)])
    return Part.Face(pg).extrude(V(0, 0, L)).cut(cyl(1.5, L + 2, V(x, y, z0 - 1)))


def marking_box():
    b = BOXD
    h = b["half"]
    s = box(-h, h, -h, h, b["z_bot"], b["z_top"])
    w0, w1 = b["wing"]
    for sx in (-1, 1):
        s = s.fuse(box(min(sx * w0, sx * w1), max(sx * w0, sx * w1), -h, -h + b["wing_t"], b["z_bot"], b["z_top"]))
    s = s.cut(cyl(b["bore"] / 2, b["z_top"] - b["z_bot"] + 2, V(0, 0, b["z_bot"] - 1)))
    s = s.cut(cyl(b["mesh_rec"] / 2, b["z_top"] - b["z_mesh"] + 1, V(0, 0, b["z_mesh"])))
    zc = H["rest"] + b["hole"] / 2
    s = s.cut(cyl(b["hole"] / 2, h + 1, V(0, 0, zc), V(-1, 0, 0)))
    s = s.cut(cyl(b["hole"] / 2, h + 1, V(0, 0, zc), V(0, 1, 0)))
    for sx in (-1, 1):
        s = s.cut(cyl(2.25, b["wing_t"] + 2, V(sx * sum(b["wing"]) / 2, -h - 1, (b["z_bot"] + b["z_top"]) / 2), V(0, 1, 0)))
        for sy in (-1, 1):
            s = s.cut(cyl(b["ins_d"] / 2, b["ins_L"], V(sx * b["ins"][0], sy * b["ins"][1], b["z_top"] - b["ins_L"])))
    return s.removeSplitter()


def mesh_and_clamp():
    zm = BOXD["z_mesh"]
    m = cyl(MESH["d"] / 2, MESH["t"], V(0, 0, zm))
    holes = []
    n = int(MESH["d"] / 2 / MESH["p"]) + 1
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, y = i * MESH["p"], j * MESH["p"]
            if math.hypot(x, y) < MESH["d"] / 2 - 2:
                holes.append(cyl(MESH["hole"] / 2, 2, V(x, y, zm - 0.5)))
    m = m.cut(Part.makeCompound(holes))
    cl = []
    zt = BOXD["z_top"]
    for sx in (-1, 1):
        for sy in (-1, 1):
            xy = (sx * BOXD["ins"][0], sy * BOXD["ins"][1])
            cl.append(washer(9.0, 3.2, 0.8, zt, xy))                                       # M3 DIN 9021
            cl.append(pan(V(xy[0], xy[1], zt + 0.8), V(0, 0, -1), 3.0, 6.0))               # M3 × 6
            cl.append(washer(BOXD["ins_d"], 3.0, BOXD["ins_L"] - 0.7, zt - BOXD["ins_L"] + 0.7, xy))   # 인서트 (대표)
    return m, Part.makeCompound(cl)


def floor_lump():
    """바닥 덩어리 (받침 위에 얹힘): 바닥 와셔 + 무게 와셔 10 + 자석. 반환 (와셔들, 자석, 아랫면 z)"""
    top = H["rest"]
    parts = [washer(FLOOR["od"], FLOOR["id"], FLOOR["t"], top - FLOOR["t"])]
    z = top - FLOOR["t"]
    for k in range(WGT["n"]):
        parts.append(washer(WGT["od"], WGT["id"], WGT["t"], z - WGT["t"]))
        z -= WGT["t"]
    mag = cyl(MAG["d"] / 2, MAG["t"], V(WGT["od"] / 2, 0, z + WGT["t"] / 2), V(1, 0, 0))
    return Part.makeCompound(parts), mag, z


def column(zb):
    """받침 (M4 9021 위, M6 9021 아래) + M3 × 8 + 스페이서 20. 반환 (받침, 나사, 스페이서, 거더 윗면 z)"""
    (od1, id1, t1), (od2, id2, t2) = PAD
    pads = Part.makeCompound([washer(od1, id1, t1, zb - t1), washer(od2, id2, t2, zb - t1 - t2)])
    scr = pan(V(0, 0, zb), V(0, 0, -1), 3.0, 8.0)
    z_so = zb - t1 - t2
    return pads, scr, hexso(0, 0, z_so - SO, SO), z_so - SO


def girder(z_g):
    t = G["t"]
    g = box(-6.35, -6.35 + G["L"], YC, YC + G["w"], z_g - t, z_g).fuse(box(-6.35, -6.35 + G["L"], YC, YC + t, z_g - G["w"], z_g))
    for i in range(3):
        g = g.cut(cyl(G["hole"] / 2, 3, V(i * G["p"], 0, z_g - 2)))
        g = g.cut(cyl(G["hole"] / 2, 3, V(i * G["p"], YC - 1, z_g - G["w"] / 2), V(0, 1, 0)))
    return g.removeSplitter()


def hall(z_g):
    """홀 모듈 판 (눕힘) + 칩, 판 스페이서, 나사 2 (판 → 스페이서, 거더 아래 → 스페이서)"""
    d = HALLD
    zt = z_g + SO
    board = box(d["x0"], d["x0"] + d["L"], -d["W"] / 2, d["W"] / 2, zt, zt + d["t"]).cut(cyl(1.6, 3, V(d["hole_x"], 0, zt - 1)))
    cx, cy, cz = d["chip"]
    chip = box(d["x0"] + 0.3, d["x0"] + 0.3 + cx, -cy / 2, cy / 2, zt + d["t"], zt + d["t"] + cz)
    scr = Part.makeCompound([pan(V(d["hole_x"], 0, zt + d["t"]), V(0, 0, -1), 3.0, 6.0),
                             pan(V(d["hole_x"], 0, z_g - G["t"]), V(0, 0, 1), 3.0, 6.0)])
    return board.fuse(chip), hexso(d["hole_x"], 0, z_g, SO), scr


def slide(z_row):
    """MiniSlide: STEP이 있으면 그것 (PC), 없으면 대표 상자. 캐리지 위 구멍 줄이 z_row에 오게"""
    f = glob.glob(os.path.join(STEP_DIR, "Haydon_MSA02_50mm_*.stp"))
    m = App.Matrix(0, 0, -1, 6.35, 0, 1, 0, YC - 6.35, 1, 0, 0, ZR, 0, 0, 0, 1)
    if f:
        sol = Part.read(f[0]).Solids
        car = sol[6].copy()
        car.translate(V(z_row - (-11.33 + ZR), 0, 0))
        return Part.makeCompound([x for i, x in enumerate(sol) if i != 6]).transformed(m), car.transformed(m), "STEP"
    rail = box(-116.12, 1.5, -11.0, 5.33, -18.0, 18.0).cut(box(-85.69, -9.0, -12, 7, -11, 11))
    car = box(-31.9, -6.5, -6.35, 6.35, -17.78, 17.78)
    car.translate(V(z_row - (-11.33 + ZR), 0, 0))
    return rail.transformed(m), car.transformed(m), "대표"


BAR = dict(L=100.0, a=20.0, slot=6.2, slot_d=6.0)
Z_BAR = ((BOXD["z_bot"] + BOXD["z_top"]) / 2, -2.5 + ZR, -89.69 + ZR)
Y_BAR_FRONT = (-BOXD["half"], -24.0, -24.0)


def bar(zc, yf):
    x0 = 6.35 - BAR["L"] / 2
    b = box(x0, x0 + BAR["L"], yf - BAR["a"], yf, zc - BAR["a"] / 2, zc + BAR["a"] / 2)
    return b.cut(box(x0 - 1, x0 + BAR["L"] + 1, yf - BAR["slot_d"], yf + 1, zc - BAR["slot"] / 2, zc + BAR["slot"] / 2))


def tnut(x, yf, z):
    return box(x - 5, x + 5, yf - BAR["slot_d"], yf - BAR["slot_d"] + 4, z - 3, z + 3)


def frame():
    bars = Part.makeCompound([bar(Z_BAR[i], Y_BAR_FRONT[i]) for i in range(3)])
    rs = []
    for zb in Z_BAR[1:]:
        for xh in (6.35 - 14.25, 6.35 + 14.25):
            rs.append(cyl(1.5, 10.0, V(xh, Y_BAR_FRONT[1] - 6.0, zb), V(0, 1, 0)))
            rs.append(tnut(xh, Y_BAR_FRONT[1], zb))
    bs = []
    for sx in (-1, 1):
        x = sx * sum(BOXD["wing"]) / 2
        bs.append(pan(V(x, -BOXD["half"] + BOXD["wing_t"], Z_BAR[0]), V(0, -1, 0), 4.0, 10.0))
        bs.append(tnut(x, Y_BAR_FRONT[0], Z_BAR[0]))
    return bars, Part.makeCompound(rs), Part.makeCompound(bs)


def make(doc=None):
    doc = doc or App.newDocument("Lift_v2")
    lump, mag, zb = floor_lump()
    pads, pscr, so, z_g = column(zb)
    z_row = z_g - G["w"] / 2
    rail, car, src = slide(z_row)
    gs = Part.makeCompound([pan(V(xh, YC + G["t"], z_row), V(0, -1, 0), 3.0, 6.0) for xh in (0.0, G["p"])])
    hb, hso, hscr = hall(z_g)
    mesh, clamp = mesh_and_clamp()
    bars, rs, bs = frame()
    gray, dark, green, blue = (0.75, 0.75, 0.77), (0.35, 0.35, 0.37), (0.2, 0.7, 0.3), (0.2, 0.4, 0.8)
    rows = [("300_marking_box (마킹실 상자 — 예외 부품 1개: 3D 프린트 또는 판매처 가공. 안 Ø31 × 15, 문 구멍 Ø13 바닥 높이 −x·+y)", marking_box(), green, 50),
            ("300m_mesh (스테인리스 타공 원판 Ø33 × 0.5, 구멍 2.6 간격 3.2 — 상자 턱에, 구매) [상품 미정]", mesh, gray, 0),
            ("300c_mesh_clamp (M3 × 6 냄비 4 + M3 DIN 9021 와셔 4 + M3 열압입 인서트 4, 구매)", clamp, dark, 0),
            ("301_minislide (Haydon Kerk MSA02S-C0039-805 — 레일·모터·블록, 구매) [%s]" % src, rail, gray, 0),
            ("301c_minislide_carriage (MiniSlide 캐리지 — 움직임) [%s]" % src, car, gray, 0),
            ("302_meccano_angle_girder (메카노 앵글 거더 1½\" 구멍 3, 구매)", girder(z_g), gray, 0),
            ("302s_screws (M3 × 6 냄비 2 — 거더 → 캐리지 인서트, 구매)", gs, dark, 0),
            ("303_standoff (M3 육각 스페이서 암-암 20, 구매)", so, gray, 0),
            ("303p_pad (받침: M4 DIN 9021 + M6 DIN 9021, 구매)", pads, gray, 0),
            ("303s_screw (M3 × 8 냄비 — 받침 → 스페이서, 구매)", pscr, dark, 0),
            ("304_floor_lump (바닥 M10 DIN 9021 + 무게 M10 DIN 125 10장 — 받침 위에 얹힘, 구매)", lump, gray, 0),
            ("304m_magnet (네오디뮴 원판 6 × 3 — 아래 와셔 테에 붙음, 구매) [상품 미정]", mag, (0.6, 0.6, 0.65), 0),
            ("306_hall_module_KY024 (SS49E + LM393, DO → UNO A1 — 눕혀서 스페이서에, 구매) [판 치수 추측]", hb, blue, 0),
            ("306o_standoff (M3 육각 스페이서 암-암 20 — 홀 판, 구매)", hso, gray, 0),
            ("306s_screws (M3 × 6 냄비 2 — 판 → 스페이서 → 거더, 구매)", hscr, dark, 0),
            ("307_bar_2020_100 (2020 알루미늄 프로파일 100 mm 3개 — 정해진 길이 제품, 구매)", bars, (0.8, 0.8, 0.82), 0),
            ("307s_rail_studs (M3 × 10 무두 볼트 4 + 2020 M3 T너트 4, 구매)", rs, dark, 0),
            ("308s_box_screws (M4 × 10 냄비 2 + 2020 M4 T너트 2 — 상자 날개 → 막대, 구매)", bs, dark, 0)]
    for i, (lab, shp, col, tr) in enumerate(rows):
        o = doc.addObject("Part::Feature", "P%02d" % i)
        o.Shape, o.Label = shp, lab
        if App.GuiUp:
            o.ViewObject.ShapeColor = col
            o.ViewObject.Transparency = tr
    doc.recompute()
    return doc


MOVING = ("301c", "302", "303", "304", "306")
LUMP = ("304",)
ALLOW = (("300c", "300_"), ("300c", "300m"), ("301c", "301_"), ("302s", "301c"), ("302s", "302_"), ("303s", "303"),
         ("303s", "302_"), ("306s", "306"), ("306s", "302_"), ("306o", "302_"), ("307s", "307_"), ("307s", "301_"),
         ("308s", "307_"), ("308s", "300_"))


def pen(dx, dy, z_tip):
    p = V(dx, dy, z_tip)
    s = cyl(PEN["tip_d"] / 2, PEN["tip_L"], p)
    s = s.fuse(cyl(PEN["nose_d"] / 2, PEN["body_from"] - PEN["tip_L"], p + V(0, 0, PEN["tip_L"])))
    return s.fuse(cyl(PEN["body_d"] / 2, PEN["L"] - PEN["body_from"], p + V(0, 0, PEN["body_from"])))


def check(doc):
    """(1) 0 → 행정 3 mm씩 움직이는 것 ↔ 고정 (2) 덩어리가 멈춘 뒤 기둥 쪽만 1~3 mm 더 (3) 고정끼리 (4) 움직이는 것끼리
    (5) 캐리지가 레일 안 (6) 펜이 닿는 망 구멍 수 (7) 덩어리 무게"""
    key = lambda o: o.Label.split(" ")[0]
    ok = lambda a, b: any(a.startswith(p) and b.startswith(q) or b.startswith(p) and a.startswith(q) for p, q in ALLOW)
    obs = [o for o in doc.Objects if hasattr(o, "Shape")]
    mv = [o for o in obs if key(o).startswith(MOVING)]
    fx = [o for o in obs if o not in mv]

    def vol(a, sa, b, sb):
        if ok(key(a), key(b)) or not sa.BoundBox.intersect(sb.BoundBox):
            return 0.0
        return sa.common(sb).Volume

    def moved(o, dz):
        s = o.Shape.copy()
        s.translate(V(0, 0, dz))
        return s
    steps = sorted({min(STROKE, 3.0 * k) for k in range(int(STROKE // 3) + 2)})
    sweep = [(dz, key(a), key(b), round(v, 2)) for dz in steps for a in mv for b in fx
             for v in [vol(a, moved(a, dz), b, b.Shape)] if v > 0.01]
    lump = [o for o in mv if key(o).startswith(LUMP)]
    rest = [o for o in mv if o not in lump]
    over = [(e, key(a), key(b), round(v, 2)) for e in (1.0, 2.0, 3.0) for a in rest for b in lump + fx
            for v in [vol(a, moved(a, STROKE + e), b, moved(b, STROKE) if b in lump else b.Shape)] if v > 0.01]
    static = [(key(a), key(b), round(v, 2)) for i, a in enumerate(fx) for b in fx[i + 1:]
              for v in [vol(a, a.Shape, b, b.Shape)] if v > 0.01]
    inner = [(key(a), key(b), round(v, 2)) for i, a in enumerate(mv) for b in mv[i + 1:]
             for v in [vol(a, a.Shape, b, b.Shape)] if v > 0.01]
    car = [o for o in obs if key(o).startswith("301c")][0].Shape.BoundBox
    lo, hi = car.ZMin - ZR, car.ZMax - ZR + STROKE + 3.0
    fixed_pen = [o.Shape for o in obs if key(o) in ("300_marking_box", "300c_mesh_clamp")]
    n_ok = n_all = 0
    n = int(MESH["d"] / 2 / MESH["p"]) + 1
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, y = i * MESH["p"], j * MESH["p"]
            if math.hypot(x, y) >= BOXD["bore"] / 2 - 1.1:
                continue
            n_all += 1
            pn = pen(x, y, BOXD["z_mesh"])
            if not any(pn.common(f).Volume > 0.001 for f in fixed_pen):
                n_ok += 1
    g = sum(o.Shape.Volume for o in lump if key(o) == "304_floor_lump") * RHO["steel"] / 1000 + \
        sum(o.Shape.Volume for o in lump if key(o) == "304m_magnet") * RHO["ndfeb"] / 1000
    return dict(stroke=STROKE, sweep=sweep, over=over, static=static, inner=inner,
                carriage_local=(round(lo, 2), round(hi, 2)), carriage_in_rail=(lo >= CAR_RANGE[0] and hi <= CAR_RANGE[1]),
                pen_holes=(n_ok, n_all), lump_g=round(g, 1), lump_N=round(g * 9.81 / 1000, 3))
