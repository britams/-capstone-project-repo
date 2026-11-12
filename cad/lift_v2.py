# -*- coding: utf-8 -*-
"""리프트 v2 — 기성품 + 나사만 (서현 11/12 14:34 "3D 프린트 절대 쓰지 마, 절단·재단도 못 해, 나사로 조이는 것만",
14:41 "마킹실 낮춰", 14:45 MiniSlide로, 15:10 "시제품 중 제일 싼 걸로"). 다른 부분과 아직 맞추지 않음 — 리프트부만.

좌표 (이 파일 혼자): 마킹실(PVC 크로스) 가운데 = 원점, z 위.
  마킹실  US Plastic 34567 (DuraClear 1" 투명 PVC 5방향 크로스, 소켓 깊이 1-1/4") — 구멍 ±x(입구·격리), ±z(위 망·아래 바닥 길), +y
          안지름 26.64 (1" 관 안) · 소켓 33.6 · 팔 끝까지 48 [추측 — 판매처가 소켓 깊이만 줌, 사서 잼] (11/12 15:54 3/4" → 1")
  리프트  Haydon Kerk MiniSlide MSA02S-C0039-805 (50 mm 행정, 리드 1 mm, 20 mm 캔스택 7.5°, 5 V 350 mA) — 세워서, 모터 아래
          캐리지 M3 인서트 4개 16.0 × 12.7 [확실 — 판매처 STEP]. STEP은 PC에만 (받은도면 step파일)
  연결    메카노 앵글 거더 1½" (구멍 3, 간격 12.7, 구멍 Ø4.1, 날개 12.7) — 캐리지 위 구멍 줄 2개에 M3 × 6
          두께 1.0, 구멍 줄은 날개 가운데 [추측 — 메카노 표준 간격 ½"만 확실]
  기둥    M3 육각 스페이서 암-암 40 + 수-암 30 (6각 5.5) — 거더 아래에서 M3 × 6
  바닥    M8 DIN 9021 와셔 (바깥 24, 안 8.4, 두께 2) + M3 DIN 9021 와셔 (바깥 9, 0.8) + M3 낮은 머리 나사 (머리 1.65)
  행정    말벌이 옆 구멍 바닥 높이로 걸어 들어옴 → 바닥 윗면 z −13.32. 위 망(z 16.25) − 눌린 말벌 5 → 11.25 → 24.57 mm
"""
import os
import glob
import math
import FreeCAD as App
import Part

V = App.Vector
STEP_DIR = r"C:\Users\Seohyun_Lee\Desktop\capstone design\받은도면 step파일"
# (11/12 15:54 서현 '추천 방향') 마킹실 1" 로: US Plastic 34567 (DuraClear 1" 투명 PVC 5방향 크로스, C&S DCF1005WNSF, $10.12, 소켓 깊이 1-1/4")
#   안 = 1" 관 안지름 26.64 · 소켓 = 1" 관 바깥 33.4 + 0.2 · 바깥·팔 길이는 대표 [추측 — 판매처가 소켓 깊이만 줌, 사서 잼]
X = dict(bore=31.0, sock=33.6, sock_d=20.0, arm=27.0, od=40.0)
# (11/12 16:09 서현 '마킹실 상자 하나만 예외') PVC 크로스 → 마킹실 상자 300 (예외: 프린트 또는 판매처 가공 한 개)
#   크로스는 문(구멍 끝)에서 바닥까지 관이 약 36 mm라 벌이 바닥에 안 감 (서현 16:07) → 문 구멍이 바닥 바로 옆 벽에 뚫린 상자
#   안: 둥근 Ø31 × 높이 14 (z −7 ~ 7), 바닥 쪽은 뚫림(바닥 와셔가 올라옴). 입구 Ø13 (−x 벽) · 격리 Ø13 (+y 벽) — 구멍 아래 끝 = 바닥 윗면 z −7
#   위: 망 턱 z 7, 니플 소켓 Ø33.6 (z 7 ~ 27). 바깥 40 × 40, 뒤(−y) 날개 2개에 M4 구멍 → 위 2020 막대 T너트
#   행정 = 14 − 눌린 말벌 5 = 9 mm. 문은 벽 바깥에 바로 (벽 두께 4.5) [문 자리는 아직 안 그림]
BOXH = dict(z0=-7.0, z1=7.0, hole=13.0, bottom_t=3.0, wing=(20.0, 32.0), wing_z=(15.0, 25.0))
# 누르는 힘 = 위 망 + 강철 짧은 니플 무게 (망 위에 얹음, 묶지 않음 — 힘이 넘으면 통째로 들림)
#   니플 McMaster 44615K416 (1" NPT 짧은 니플, 길이 1-1/2", 강철 sch40, $3.13) — 바깥 33.4 · 안 26.64 [확실 — 판매처 표·관 규격]
#   무게 ≈ π/4 (33.4² − 26.64²) × 38.1 × 7.85 = 95 g (나사산만큼 덜함) → 약 0.93 N [가능성 높음 — 저울로 잼]
#   펜 (승준 11/02 실측: 팁 2.2·8.0, 앞코 7.2, 몸통 14.7은 팁 끝 15.6 뒤부터) 몸통이 니플 안(26.64)에 들어가 옆으로 ±5.97
#   홀 감지: 니플 바깥(−y) 소켓 위로 나온 곳에 원판 자석 6 × 3 (강철에 붙음) + 홀 모듈 KY-024 → UNO A1, 1 mm 들리면 멈춤
MESH = dict(d=33.0, t=0.5, hole=2.6, p=3.2)              # 스테인리스 타공 원판 [추측 — 상품 미정]. 펜 팁 2.2가 구멍 2.6을 지남
NIP = dict(od=33.4, id=26.64, L=38.1, rho=7.85)
MAG = dict(d=6.0, t=3.0)
HALL = dict(L=32.0, W=14.0, t=1.6, chip=(4.0, 1.6, 3.0))     # 모듈 판 대표 [추측]
PEN = dict(tip_d=2.2, tip_L=8.0, nose_d=7.2, body_d=14.7, body_from=15.6, L=134.6)
Z_SHELF = BOXH["z1"]                                     # 7 망 턱
H = dict(rest=BOXH["z0"], press=Z_SHELF - 5.0)          # 바닥 −7 → 2 (눌린 말벌 5)
STROKE = H["press"] - H["rest"]
W6 = dict(od=30.0, id=10.5, t=2.5)                      # 바닥 = M10 DIN 9021 (바깥 30 — 안 31과 틈 0.5)
W3 = dict(od=12.0, id=4.3, t=1.0)                       # 가운데 = M4 DIN 9021 (구멍 10.5를 덮음) + M3 나사
SO = (25.0,)                           # 스페이서 (캐리지가 레일 행정 안·거더가 상자 아래, 11/12 16:10 계산)
G = dict(L=38.1, w=12.7, t=1.0, hole=4.1, p=12.7, hole_from_out=6.6)
YC = -G["hole_from_out"]                # 캐리지 앞면 y (거더 구멍이 축 위에 오게)
ZR = -13.0                              # 레일 국부 x → 세계 z 더하는 값 (레일 위 블록 위 끝 −11.5 < 상자 아래 −10)
CAR_RANGE = (-85.69, -9.0)              # 캐리지가 움직일 수 있는 국부 x (두 블록 사이) [확실 — 판매처 STEP]


def cyl(r, h, p, d=V(0, 0, 1)):
    return Part.makeCylinder(r, h, p, d)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def marking_box():
    """마킹실 상자 300 (예외 부품 한 개)"""
    h = X["od"] / 2
    zb = BOXH["z0"] - BOXH["bottom_t"]
    b = box(-h, h, -h, h, zb, X["arm"])
    w0, w1 = BOXH["wing"]
    for sx in (-1, 1):
        b = b.fuse(box(min(sx * w0, sx * w1), max(sx * w0, sx * w1), -h, -h + 3.0, BOXH["wing_z"][0], BOXH["wing_z"][1]))
    b = b.cut(cyl(X["bore"] / 2, Z_SHELF - zb + 1, V(0, 0, zb - 1)))
    b = b.cut(cyl(X["sock"] / 2, X["arm"] - Z_SHELF + 1, V(0, 0, Z_SHELF)))
    zc = BOXH["z0"] + BOXH["hole"] / 2
    b = b.cut(cyl(BOXH["hole"] / 2, h + 1, V(0, 0, zc), V(-1, 0, 0)))          # 입구 (−x)
    b = b.cut(cyl(BOXH["hole"] / 2, h + 1, V(0, 0, zc), V(0, 1, 0)))           # 격리 (+y)
    for sx in (-1, 1):
        b = b.cut(cyl(2.25, 5, V(sx * (w0 + w1) / 2, -h - 1, sum(BOXH["wing_z"]) / 2), V(0, 1, 0)))
    return b.removeSplitter()


def top_weight():
    """위 망 + 강철 니플 + 자석 + 홀 모듈 (망·니플·자석은 얹혀 있을 뿐 — 들릴 수 있음)"""
    zm = Z_SHELF
    mesh = cyl(MESH["d"] / 2, MESH["t"], V(0, 0, zm))
    holes = []
    n = int(MESH["d"] / 2 / MESH["p"]) + 1
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, y = i * MESH["p"], j * MESH["p"]
            if math.hypot(x, y) < MESH["d"] / 2 - 2:
                holes.append(cyl(MESH["hole"] / 2, 2, V(x, y, zm - 0.5)))
    mesh = mesh.cut(Part.makeCompound(holes))
    z0 = zm + MESH["t"]
    nip = cyl(NIP["od"] / 2, NIP["L"], V(0, 0, z0)).cut(cyl(NIP["id"] / 2, NIP["L"] + 2, V(0, 0, z0 - 1)))
    z_top = z0 + NIP["L"]
    zc = (X["arm"] + z_top) / 2                                               # 소켓 위로 나온 곳 가운데
    y_out = -NIP["od"] / 2
    mag = cyl(MAG["d"] / 2, MAG["t"], V(0, y_out, zc), V(0, -1, 0))
    y0 = y_out - MAG["t"] - 1.0                                               # 자석과 1 띄움
    cw, ct, ch = HALL["chip"]
    chip = box(-cw / 2, cw / 2, y0 - ct, y0, zc - ch / 2, zc + ch / 2)
    board = box(-HALL["W"] / 2, HALL["W"] / 2, y0 - ct - 1.0 - HALL["t"], y0 - ct - 1.0, zc - 6.0, zc - 6.0 + HALL["L"])
    return mesh, nip, mag, chip.fuse(board)


# (11/12 16:00) 리프트부 틀 — 기성품만, 나사로: 2020 프로파일 100 mm (정해진 길이 제품) 3개 (다른 틀에는 아직 안 붙임)
#   가운데·아래 막대: MiniSlide 끝 블록 바닥 M3 탭 2개 (28.5 간격) ↔ 막대 앞 홈 T너트 — M3 × 10 무두 볼트(양쪽 나사)로 [확실 — 판매처 STEP 구멍 자리]
#   위 막대 (z 22~42, 앞면 y −21 = 위 소켓 뒷면): 1-1/4" EMT 2구멍 새들 (바깥 41.6 관용 ≈ 소켓 바깥 42 [추측]) M4 × 8 두 개 + T너트
#     + 메카노 앵글 브래킷 #12 (½" × ½", 구멍 1씩)를 막대 윗면 홈에 M3, 다른 다리에 홀 모듈 KY-024를 M3 + 너트 (모듈 구멍 자리 [추측])
BAR = dict(L=100.0, a=20.0, slot=6.2, slot_d=6.0)
Z_BAR = (20.0, -2.5 + ZR, -89.69 + ZR)                  # 위 · 가운데(레일 위 블록 구멍 높이) · 아래(레일 아래 블록 구멍 높이)
Y_BAR_FRONT = (-X["od"] / 2, -24.0, -24.0)              # 레일 바닥면 y = 국부 −11 + YC − 6.35 = −23.95, 0.05 띄움 (모터와 0.04 mm³ 겹침, 11/12 검사)


def bar(zc, yf, slots=("front",)):
    x0 = 6.35 - BAR["L"] / 2
    b = box(x0, x0 + BAR["L"], yf - BAR["a"], yf, zc - BAR["a"] / 2, zc + BAR["a"] / 2)
    w, dpt = BAR["slot"], BAR["slot_d"]
    if "front" in slots:
        b = b.cut(box(x0 - 1, x0 + BAR["L"] + 1, yf - dpt, yf + 1, zc - w / 2, zc + w / 2))
    if "top" in slots:
        yc = yf - BAR["a"] / 2
        b = b.cut(box(x0 - 1, x0 + BAR["L"] + 1, yc - w / 2, yc + w / 2, zc + BAR["a"] / 2 - dpt, zc + BAR["a"] / 2 + 1))
    return b


def tnut(p, n):
    """2020 T너트 대표 (10 × 6 × 4) — p = 홈 바닥 가운데, n = 바깥 방향"""
    if abs(n.y) > 0.5:
        return box(p.x - 5, p.x + 5, min(p.y, p.y - n.y * 4), max(p.y, p.y - n.y * 4), p.z - 3, p.z + 3)
    return box(p.x - 5, p.x + 5, p.y - 3, p.y + 3, min(p.z, p.z - n.z * 4), max(p.z, p.z - n.z * 4))


def frame():
    out = {}
    out["bars"] = Part.makeCompound([bar(Z_BAR[0], Y_BAR_FRONT[0], ("front", "top")), bar(Z_BAR[1], Y_BAR_FRONT[1]), bar(Z_BAR[2], Y_BAR_FRONT[2])])
    studs, nuts = [], []
    for zb in Z_BAR[1:]:
        for xh in (6.35 - 14.25, 6.35 + 14.25):
            yf = Y_BAR_FRONT[1]
            studs.append(cyl(1.5, 10.0, V(xh, yf - 6.0, zb), V(0, 1, 0)))                 # 블록 안 4, 홈 안 6
            nuts.append(tnut(V(xh, yf - BAR["slot_d"] + 4.0, zb), V(0, 1, 0)))
    out["rail_studs"] = Part.makeCompound(studs + nuts)
    yf = Y_BAR_FRONT[0]
    sc = []
    for sx in (-1, 1):
        x = sx * sum(BOXH["wing"]) / 2
        sc.append(cyl(3.5, 2.8, V(x, yf + 3.0, Z_BAR[0]), V(0, 1, 0)).fuse(cyl(2.0, 8.0, V(x, yf + 3.0 - 8.0, Z_BAR[0]), V(0, 1, 0))))
        sc.append(tnut(V(x, yf - BAR["slot_d"] + 4.0, Z_BAR[0]), V(0, 1, 0)))
    out["box_screws"] = Part.makeCompound(sc)
    # 홀 모듈 브래킷 (메카노 #12): 선 다리 = 모듈 판 뒤, 누운 다리 = 위 막대 윗면
    _m, _n, _g, hall = top_weight()
    hb = hall.BoundBox
    yb = hb.YMin                                                            # 모듈 판 뒷면
    ztop = Z_BAR[0] + BAR["a"] / 2
    br = box(-6.35, 6.35, yb - 1.0, yb, ztop, ztop + 12.7).fuse(box(-6.35, 6.35, yb - 12.7, yb, ztop, ztop + 1.0))
    zh_board = hb.ZMin + 3.5                                                # 모듈 구멍 [추측]
    yh = Y_BAR_FRONT[0] - BAR["a"] / 2                                      # 막대 윗면 홈 가운데
    br = br.cut(cyl(1.7, 5, V(0, yb - 2, zh_board), V(0, 1, 0))).cut(cyl(1.7, 5, V(0, yh, ztop - 1)))
    out["hall_bracket"] = br
    hs = [cyl(2.75, 1.65, V(0, yb - 1.0 - 1.65, zh_board), V(0, 1, 0)).fuse(cyl(1.5, 4.0, V(0, yb - 1.0, zh_board), V(0, 1, 0))),   # M3 × 4 + 너트 (8은 자석·크로스에 닿음, 11/12 검사)
          cyl(2.75, 1.65, V(0, yh, ztop + 1.0)).fuse(cyl(1.5, 8.0, V(0, yh, ztop + 1.0 - 8.0))),
          tnut(V(0, yh, ztop - BAR["slot_d"] + 4.0), V(0, 0, 1))]
    out["hall_screws"] = Part.makeCompound(hs)
    return out


def pen(dx, dy, z_tip):
    """샤피 크리에이티브 불렛 (승준 11/02 실측) — 팁 끝 z_tip, 축 (dx, dy)"""
    p = V(dx, dy, z_tip)
    s = cyl(PEN["tip_d"] / 2, PEN["tip_L"], p)
    s = s.fuse(cyl(PEN["nose_d"] / 2, PEN["body_from"] - PEN["tip_L"], p + V(0, 0, PEN["tip_L"])))
    return s.fuse(cyl(PEN["body_d"] / 2, PEN["L"] - PEN["body_from"], p + V(0, 0, PEN["body_from"])))


def pen_reach(doc, step=0.25):
    """팁 끝을 망 아랫면(말벌 등)까지 내렸을 때 니플·크로스·자석에 안 닿는 가장 큰 옆 거리 (x·y·대각)"""
    fx = [o.Shape for o in doc.Objects if o.Label.split(" ")[0] in ("300_marking_box", "305n_nipple", "305m_magnet")]
    out = {}
    for name, u in (("x", V(1, 0, 0)), ("y", V(0, 1, 0)), ("diag", V(0.7071, 0.7071, 0))):
        r = 0.0
        while r < 20:
            pn = pen(u.x * r, u.y * r, Z_SHELF)
            if any(pn.common(f).Volume > 0.001 for f in fx):
                break
            r += step
        out[name] = round(r - step, 2)
    return out


def floor_stack(dz):
    """움직이는 바닥 묶음 (dz = 쉬는 자리에서 올라간 양). 반환 {이름: 모양}"""
    top = H["rest"] + dz
    w6 = cyl(W6["od"] / 2, W6["t"], V(0, 0, top - W6["t"])).cut(cyl(W6["id"] / 2, 5, V(0, 0, top - 3)))
    w3 = cyl(W3["od"] / 2, W3["t"], V(0, 0, top)).cut(cyl(W3["id"] / 2, 3, V(0, 0, top - 1)))
    head_z = top + W3["t"]
    scr_top = cyl(2.75, 1.65, V(0, 0, head_z)).fuse(cyl(1.5, 6.0, V(0, 0, head_z - 6.0)))
    z_so1 = top - W6["t"]                                   # 스페이서 윗면
    so = None
    z = z_so1
    for L in SO:
        R = 5.5 / 3 ** 0.5
        hexp = Part.makePolygon([V(R * math.cos(math.radians(60 * k + 30)), R * math.sin(math.radians(60 * k + 30)), z - L) for k in range(7)])
        hx = Part.Face(hexp).extrude(V(0, 0, L)).cut(cyl(1.5, L + 2, V(0, 0, z - L - 1)))
        so = hx if so is None else so.fuse(hx)
        z -= L
    z_g = z                                                  # 거더 누운 날개 윗면
    t = G["t"]
    girder = box(-6.35, -6.35 + G["L"], YC, YC + G["w"], z_g - t, z_g)                                     # 누운 날개
    girder = girder.fuse(box(-6.35, -6.35 + G["L"], YC, YC + t, z_g - G["w"], z_g))                        # 선 날개 (캐리지에 붙음)
    for i in range(3):
        xh = i * G["p"]
        girder = girder.cut(cyl(G["hole"] / 2, 3, V(xh, 0, z_g - 2)))
        girder = girder.cut(cyl(G["hole"] / 2, 3, V(xh, YC - 1, z_g - G["w"] / 2), V(0, 1, 0)))
    scr_bot = cyl(2.75, 1.65, V(0, 0, z_g - t - 1.65)).fuse(cyl(1.5, 6.0, V(0, 0, z_g - t)))
    car_scr = []
    for xh in (0.0, G["p"]):
        c = V(xh, YC + t, z_g - G["w"] / 2)
        car_scr.append(cyl(2.75, 1.65, c, V(0, 1, 0)).fuse(cyl(1.5, 6.0, c - V(0, 6.0, 0), V(0, 1, 0))))
    return {"floor_w6": w6, "floor_w3": w3, "floor_screw": scr_top, "standoffs": so, "girder": girder,
            "girder_screw": scr_bot, "carriage_screws": Part.makeCompound(car_scr)}, z_g


def slide(dz, z_row):
    """MiniSlide: STEP이 있으면 그것 (PC), 없으면 대표 상자. 캐리지 위 구멍 줄이 z_row에 오게 캐리지만 옮김"""
    f = glob.glob(os.path.join(STEP_DIR, "Haydon_MSA02_50mm_*.stp"))
    m = App.Matrix(0, 0, -1, 6.35, 0, 1, 0, YC - 6.35, 1, 0, 0, ZR, 0, 0, 0, 1)   # 국부 (x,y,z) → 세계 (−z+6.35, y+YC−6.35, x+ZR)
    if f:
        s = Part.read(f[0])
        sol = s.Solids
        car = sol[6].copy()
        car.translate(V(z_row - (-11.33 + ZR), 0, 0))             # 국부 x로: 위 구멍 줄(−11.33) → z_row
        fixed = Part.makeCompound([x for i, x in enumerate(sol) if i != 6])
        return fixed.transformed(m), car.transformed(m), "STEP"
    rail = box(-116.12, 1.5, -11.0, 5.33, -18.0, 18.0).cut(box(-85.69, -9.0, -12, 7, -11, 11))
    car = box(-31.9, -6.5, -6.35, 6.35, -17.78, 17.78)
    car.translate(V(z_row - (-11.33 + ZR), 0, 0))
    return rail.transformed(m), car.transformed(m), "대표"


def make(doc=None, dz=0.0):
    doc = doc or App.newDocument("Lift_v2")
    parts, z_g = floor_stack(dz)
    z_row = z_g - G["w"] / 2
    rail, car, src = slide(dz, z_row)
    gray, dark = (0.75, 0.75, 0.77), (0.35, 0.35, 0.37)
    tw = top_weight()
    fr = frame()
    shapes = [("C_box", "300_marking_box (마킹실 상자 — 예외 부품: 3D 프린트 또는 판매처 가공 1개, 안 Ø31 × 14, 문 구멍 Ø13 바닥 높이)", marking_box(), (0.2, 0.7, 0.3), 60),
              ("L_rail", "301_minislide (Haydon Kerk MSA02S-C0039-805 — 레일·모터·블록, 구매) [%s]" % src, rail, gray, 0),
              ("L_car", "301c_minislide_carriage (MiniSlide 캐리지 — 움직임) [%s]" % src, car, gray, 0),
              ("L_gird", "302_meccano_angle_girder (메카노 앵글 거더 1½\" 구멍 3, 구매)", parts["girder"], gray, 0),
              ("L_gs", "302s_screws (M3 × 6 냄비머리 — 거더 → 캐리지 2, 구매)", parts["carriage_screws"], dark, 0),
              ("L_so", "303_standoffs (M3 육각 스페이서 암-암 25, 구매)", parts["standoffs"], gray, 0),
              ("L_bs", "303s_screw (M3 × 6 — 거더 아래에서 스페이서로, 구매)", parts["girder_screw"], dark, 0),
              ("L_w6", "304_floor_washer_M10_DIN9021 (바닥 — 바깥 30 × 2.5, 구매)", parts["floor_w6"], gray, 0),
              ("L_w3", "304a_washer_M4_DIN9021 (바깥 12 × 1.0, 구매)", parts["floor_w3"], gray, 0),
              ("L_ts", "304s_screw (M3 낮은 머리 × 6 — 바닥 → 스페이서, 구매)", parts["floor_screw"], dark, 0),
              ("T_mesh", "305_top_mesh (스테인리스 타공 원판 Ø33 × 0.5, 구멍 2.6 간격 3.2, 위 소켓 턱에 걸침, 구매) [상품 미정]", tw[0], gray, 0),
              ("T_nip", "305n_nipple (McMaster 44615K416 1\" 강철 짧은 니플 38.1 — 망 위 무게 약 95 g, 구매)", tw[1], dark, 0),
              ("T_mag", "305m_magnet (네오디뮴 원판 6 × 3 — 니플 바깥에 붙음, 구매) [상품 미정]", tw[2], (0.6, 0.6, 0.65), 0),
              ("T_hall", "306_hall_module_KY024 (SS49E + LM393, DO → UNO A1 — 메카노 브래킷에 M3, 구매)", tw[3], (0.2, 0.4, 0.8), 0),
              ("F_bar", "307_bar_2020_100 (2020 알루미늄 프로파일 100 mm 3개 — 정해진 길이 제품, 구매)", fr["bars"], (0.8, 0.8, 0.82), 0),
              ("F_rs", "307s_rail_studs (M3 × 10 무두 볼트 4 + 2020 M3 T너트 4 — 레일 블록 ↔ 막대, 구매)", fr["rail_studs"], dark, 0),
              ("F_ss", "308s_box_screws (M4 × 8 2 + 2020 M4 T너트 2 — 상자 날개 → 위 막대, 구매)", fr["box_screws"], dark, 0),
              ("F_hb", "309_hall_bracket (메카노 앵글 브래킷 #12 ½\" × ½\", 구매)", fr["hall_bracket"], gray, 0),
              ("F_hs", "309s_hall_screws (M3 × 4 + 너트 · M3 × 8 + 2020 M3 T너트, 구매)", fr["hall_screws"], dark, 0)]
    for name, lab, shp, col, tr in shapes:
        o = doc.addObject("Part::Feature", name)
        o.Shape, o.Label = shp, lab
        if App.GuiUp:
            o.ViewObject.ShapeColor = col
            o.ViewObject.Transparency = tr
    doc.recompute()
    return doc


MOVING = ("301c", "302", "303", "304")
ALLOW = (("305", "300_"), ("305", "305"), ("306", "305m"), ("301c", "301_"), ("302s", "301c"),     # 301c↔301_: 판매처 STEP 자체가 캐리지 부싱과 안내 봉을 1.97 mm³씩 겹쳐 그림 (11/12 확인)
          ("307s", "307_"), ("307s", "301_"), ("308s", "307_"), ("308s", "300_"), ("309s", "307_"), ("309s", "309_"),
          ("309s", "306_"), ("309_", "306_"), ("302s", "302_"), ("303s", "302_"), ("303s", "303_"), ("304s", "303_"), ("304s", "304"), ("304_", "304a"))


def check(doc, steps=(0.0, 4.0, 8.0, 12.0, STROKE)):
    """쉬는 자리 → 누른 자리까지 움직이는 묶음 ↔ 고정 (마킹실·레일) 겹침, 그리고 움직이는 것끼리 (나사 물림 허용)"""
    obs = [o for o in doc.Objects if hasattr(o, "Shape")]
    mv = [o for o in obs if o.Label.startswith(MOVING)]
    fx = [o for o in obs if o not in mv]
    ok = lambda a, b: any(a.startswith(p) and b.startswith(q) or b.startswith(p) and a.startswith(q) for p, q in ALLOW)
    hits = []
    for dz in steps:
        for a in mv:
            s = a.Shape.copy()
            s.translate(V(0, 0, dz))
            for b in fx:
                if ok(a.Label.split(" ")[0], b.Label.split(" ")[0]):
                    continue
                if s.BoundBox.intersect(b.Shape.BoundBox):
                    v = s.common(b.Shape).Volume
                    if v > 0.01:
                        hits.append((dz, a.Label.split(" ")[0], b.Label.split(" ")[0], round(v, 2)))
    inner = []
    for i, a in enumerate(mv):
        for b in mv[i + 1:]:
            ka, kb = a.Label.split(" ")[0], b.Label.split(" ")[0]
            if a.Shape.BoundBox.intersect(b.Shape.BoundBox) and not ok(ka, kb):
                v = a.Shape.common(b.Shape).Volume
                if v > 0.01:
                    inner.append((ka, kb, round(v, 2)))
    static = []                                                               # 틀·센서 (고정) ↔ 모두
    fix_new = [o for o in obs if o.Label.startswith(("306", "307", "308", "309"))]
    for a in fix_new:
        for b in obs:
            if b is a or (b in fix_new and b.Name < a.Name):
                continue
            ka, kb = a.Label.split(" ")[0], b.Label.split(" ")[0]
            if ok(ka, kb) or not a.Shape.BoundBox.intersect(b.Shape.BoundBox):
                continue
            v = a.Shape.common(b.Shape).Volume
            if v > 0.01:
                static.append((ka, kb, round(v, 2)))
    car = [o for o in obs if o.Label.startswith("301c")][0].Shape.BoundBox
    lo, hi = car.ZMin - ZR, car.ZMax - ZR + STROKE                            # 국부 x (쉴 때 아래 끝, 누를 때 위 끝)
    return dict(stroke=round(STROKE, 2), sweep=hits, inner=inner, static=static, carriage_local=(round(lo, 2), round(hi, 2)),
                carriage_in_rail=(lo >= CAR_RANGE[0] and hi <= CAR_RANGE[1]), pen=pen_reach(doc),
                nipple_g=round(NIP["rho"] * math.pi / 4 * (NIP["od"] ** 2 - NIP["id"] ** 2) * NIP["L"] / 1000, 1))
