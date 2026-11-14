# -*- coding: utf-8 -*-
"""리프트 v2 — 기성품 + 나사만, 마킹실 상자 하나만 예외 (CAP-AI-62, 서현 11/12)

서현 지시: 14:34 "3D 프린트 절대 쓰지 마, 절단·재단도 못 해, 나사로 조이는 것만" · 14:45 MiniSlide · 15:10 제일 싼 것
  16:09 "마킹실 상자 하나만 예외" · 16:22 "검정 원통(망 위 무게)이 있으면 말벌을 못 찍음, 파란 부품·나사·초록 이음 제대로"
다른 부분과 아직 안 맞춤 — 리프트부만. 좌표: 마킹실 가운데 축 = (0, 0), z 위.

  300 마킹실 상자 (예외: 3D 프린트 또는 판매처 가공 1개) 바깥 38 × 38 × 18.5 (z −10 ~ 8.5) — 11/14 46에서 줄임 (안 Ø31은 그대로)
      안 Ø31 (바닥 쪽 뚫림 — 바닥이 올라옴), 망 턱 z 8.0 (윗면에서 0.5 파인 Ø33.4), 망 위는 비어 있음 → 펜이 위에서 바로
      입구 Ø13 (−x) · 격리 Ø13 (+y), 구멍 아래 끝 = 바닥 윗면 z −7 → 문을 열면 바로 바닥 (벽 7.5)
      뒤 날개 2개 (M4 구멍) → 상자 막대 T너트. 망은 M3 열압입 인서트 4 + M3 × 6 + M3 DIN 9021 와셔로 테두리를 누름
  301 Haydon Kerk MiniSlide MSA02S-C0039-805 (50 mm, 리드 1 mm, 20 mm 캔스택 7.5°, 5 V 350 mA) [확실 — 판매처 STEP, PC에만]
  302 메카노 앵글 거더 1½" (구멍 Ø4.1, 간격 12.7) — 캐리지 위 구멍 줄에 M3 × 6 두 개 [두께·구멍 자리 추측]
  303 기둥: M3 육각 스페이서 암-암 20 (거더 아래에서 M3 × 6) + 스프링 받침 M4 DIN 9021 + M3 스페이서 수-암 20 (스프링 안내)
      — 위 스페이서 수나사가 받침 구멍을 지나 아래 스페이서에 물려 받침을 끼워 조임
  304 바닥 (스프링 위에 얹힘): M10 DIN 9021 (밟는 면, 바깥 30 → 상자 안 Ø31이 옆을 잡음) + M5 DIN 9021 (스프링 받는 판)
      + 막대 자석 Ø6 × 10 (바닥 아래 x 12에 붙음 — 자석 힘으로만 붙음, 나사 없음)
  305 압축 스프링 McMaster 9657K33 (바깥 9.53 · 안 8.26 · 선 0.64 · 자유 38.1 · 1.1 lbf/in = 0.193 N/mm) [확실 — 판매처 표]
      (11/12 16:30 고침: 예전 '바닥 덩어리'는 기둥이 밑에서 밀어 올리니 힘을 못 막음 → 바닥 ↔ 기둥 사이 스프링)
      바닥이 말벌에 막히면 기둥만 더 올라가 스프링이 줄어듦 → 누르는 힘 = 0.193 N/mm × 줄어든 길이
      홀 칩이 자석 쪽으로 다가감 → 홀 모듈 DO가 바뀌면 멈춤. 2.5 mm에서 멈추면 0.48 N [문턱은 모듈 가변저항으로 실험해 맞춤 — 추측]
  306 홀 모듈 KY-024 (SS49E + LM393, DO → UNO A1): 판을 눕혀 거더 구멍 위 M3 스페이서 30에 M3 × 6, SS49E는 다리를 세워 자석 바로 아래 (가변저항이 높아 판은 낮게) [모듈 치수 추측]
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

# 11/14 17:20 서현: 망은 상자 윗면 격자로 같이 프린트, 안 Ø31 → Ø33 (여왕벌 30 + 틈 2 ≥ 32). 바깥 40, 윗면 z 9.5
# 11/14 17:25 서현: 격자는 투명 아크릴 주문 제작 (두 번째 예외) — 상자 윗면 z 8.0에 얹고 M3 × 8 + 와셔 4개로 인서트에 조임
BOXD = dict(half=19.0, z_bot=-10.0, z_top=8.0, bore=33.0, mesh_rec=33.4, z_mesh=8.0, hole=13.0,
            wing=None, wing_t=4.0, ins=(15.0, 15.0), ins_d=2.5, ins_L=6.0,   # (11/15) ins_d 4.0 → 2.5: 열압입 인서트(인두 필요) 대신 M3 태핑 나사 밑구멍 — 서현 "나사로 조이기만"
            r=1.0, grid=False, plate=True,
            doors4=True, feed_d=11.2, feed_tip=(0.0, 17.4, 1.0), feed_end=(0.0, 54.28, -8.15),   # 솜 축 (D5g_feeder_uln FD − (55, 0, 377))
            tongue=(18.3, 10.0, 3.0, 24.0), tongue_holes=(-21.0, -29.0))   # (11/14 17:55) 바깥 38 = 옛 벽 바깥, 세운 막대 위 끝 −16 (방생 문 하우징 아래)
# (11/14 17:40 서현 "새 상자 넣고 문 3개 다시", "격리 −y") 전체 좌표 = 이 좌표 + (55, 0, 377): 격자 아래 385·바닥 쉼 370
#   −x 입구 Ø13 · +x 방생 Ø13 · −y 격리 Ø13 (아래 끝 = 바닥 쉼) · +y 급이 Ø11.2 (솜 142n 축 따라 기울게, 끝 z 378)
#   날개 없앰 → 바닥 밑 혀(+y, x 13.3~23.3, 두께 3, 깊이 14)를 세운 2020 +y 홈에 M5 × 10 두 개 (lift_v3)
MESH = dict(d=38.0, t=2.0, hole=3.0, p=4.4, corner=1.0, screw_hole=3.4)   # 아크릴 2T, 네모 구멍 3.0 × 3.0 간격 4.4 (열린 면적 46 % — 비전 자 D6)
GRID_R = BOXD["bore"] / 2 - MESH["hole"] / 2 * 2 ** 0.5   # 네모 구멍 모서리까지 안 Ø33 안


def grid_centers():
    n = int(GRID_R / MESH["p"]) + 1
    return [(i * MESH["p"], j * MESH["p"]) for i in range(-n, n + 1) for j in range(-n, n + 1) if math.hypot(i, j) * MESH["p"] <= GRID_R + 1e-9]


def acrylic_plate():
    """300p 투명 아크릴 격자판 40 × 40 × 2 (주문 제작) — z_mesh 위에"""
    m, z = MESH, BOXD["z_mesh"]
    h = m["d"] / 2
    s = box(-h, h, -h, h, z, z + m["t"])
    try:
        s = s.makeFillet(m["corner"], [e for e in s.Edges if e.Curve.TypeId == "Part::GeomLine" and abs(e.Length - m["t"]) < 1e-6])
    except Exception:
        pass
    a = m["hole"] / 2
    s = s.cut(Part.makeCompound([box(x - a, x + a, y - a, y + a, z - 1, z + m["t"] + 1) for x, y in grid_centers()]))
    for sx in (-1, 1):
        for sy in (-1, 1):
            s = s.cut(cyl(m["screw_hole"] / 2, m["t"] + 2, V(sx * BOXD["ins"][0], sy * BOXD["ins"][1], z - 1)))
    return s


def plate_screws():
    """M3 × 8 냄비 태핑(셀프 탭) 4 + M3 DIN 125 와셔 4 (아크릴 깨짐 막음) — 상자 밑구멍 Ø2.5에 바로 (11/15, 인서트 없앰)"""
    zt = BOXD["z_mesh"] + MESH["t"]
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            xy = (sx * BOXD["ins"][0], sy * BOXD["ins"][1])
            out.append(washer(7.0, 3.2, 0.5, zt, xy))
            out.append(pan(V(xy[0], xy[1], zt + 0.5), V(0, 0, -1), 3.0, 8.0))
    return Part.makeCompound(out)
PEN = dict(tip_d=2.2, tip_L=8.0, nose_d=7.2, body_d=14.7, body_from=15.6, L=134.6)   # 승준 11/02 캘리퍼스
H = dict(rest=-7.0, press=BOXD["z_mesh"] - 5.0)
STROKE = H["press"] - H["rest"]                              # 10
FLOOR = dict(od=30.0, id=10.5, t=2.5)                        # M10 DIN 9021
BEAR = dict(od=15.0, id=5.3, t=1.2)                          # M5 DIN 9021
SEAT = dict(od=12.0, id=4.3, t=1.0)                          # M4 DIN 9021 (구멍 4.3 — M3 수나사는 지나고 육각 5.5는 걸림)
SPR = dict(od=9.525, wire=0.635, L0=38.1, Ls=13.97, k=1.1 * 4.448 / 25.4)   # McMaster 9657K33
MAG = dict(d=6.0, L=10.0, x=12.0)                            # 네오디뮴 막대 Ø6 × 10 [상품 미정]
TRIP = 2.5                                                   # 멈추는 줄어듦 (mm) [추측 — 실험]
SO = 20.0                                                    # M3 스페이서 20 (아래 암-암, 위 수-암)
HSO = 30.0                                                   # 홀 판 스페이서 M3 암-암 30
G = dict(L=38.1, w=12.7, t=1.0, hole=4.1, p=12.7, hole_from_out=6.6)
YC = -G["hole_from_out"]
ZR = -33.0                                                   # 레일 국부 x → 세계 z (레일 위 끝 −31.5 < 덩어리 아래 −29.5)
CAR_RANGE = (-85.69, -9.0)
HALLD = dict(L=32.0, W=14.0, t=1.6, x0=10.0, hole_x=25.4, gap=5.5,       # KY-024 판 [치수 추측 — 사서 잼]
             ss49e=(3.0, 4.0, 1.52), lead=0.45, pot=(4.5, 9.5, 10.0), ic=(4.9, 3.9, 1.5), hdr=(2.5, 10.2, 2.5))
BR = 1.2                                                     # N35 잔류 자속 밀도 (T) [추측]
SCREW = {2.0: (4.0, 1.6), 2.5: (5.0, 2.0), 3.0: (5.6, 2.4), 4.0: (8.0, 3.1), 5.0: (9.5, 3.7)}    # ISO 7045 머리 지름·높이 [확실 — 규격]
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
    if b.get("wing"):
        w0, w1 = b["wing"]
        for sx in (-1, 1):
            s = s.fuse(box(min(sx * w0, sx * w1), max(sx * w0, sx * w1), -h, -h + b["wing_t"], b["z_bot"], b["z_top"]))
    if b.get("tongue"):
        tx, ty, tt, td = b["tongue"]
        s = s.fuse(box(tx - 5, tx + 5, ty, ty + tt, b["z_bot"] - td, b["z_bot"] + 0.01))
        s = s.cut(box(18.6, tx + 6, ty - 0.1, ty + tt + 0.1, b["z_bot"] - 5.6, b["z_bot"] + 0.02))   # (11/14) 혀 위 모서리: 방생 문 하우징(전체 x 74~, z 362.5~) 자리
    if b.get("grid"):
        s = s.cut(cyl(b["bore"] / 2, b["z_mesh"] - b["z_bot"] + 1, V(0, 0, b["z_bot"] - 1)))
        n = int(GRID_R / MESH["p"]) + 1
        s = s.cut(Part.makeCompound([cyl(MESH["hole"] / 2, b["z_top"] - b["z_mesh"] + 2, V(i * MESH["p"], j * MESH["p"], b["z_mesh"] - 1))
                                     for i in range(-n, n + 1) for j in range(-n, n + 1) if math.hypot(i, j) * MESH["p"] <= GRID_R]))
    else:
        s = s.cut(cyl(b["bore"] / 2, b["z_top"] - b["z_bot"] + 2, V(0, 0, b["z_bot"] - 1)))
        if not b.get("plate"):
            s = s.cut(cyl(b["mesh_rec"] / 2, b["z_top"] - b["z_mesh"] + 1, V(0, 0, b["z_mesh"])))
    zc = H["rest"] + b["hole"] / 2
    if b.get("doors4"):
        for d in (V(-1, 0, 0), V(1, 0, 0), V(0, -1, 0)):
            s = s.cut(cyl(b["hole"] / 2, h + 1, V(0, 0, zc), d))
        t0, t1 = V(*b["feed_tip"]), V(*b["feed_end"])
        u = (t1 - t0).normalize()
        s = s.cut(cyl(b["feed_d"] / 2, 16.0, t0 - u * 6.0, u))                    # 솜 축 따라 Ø11.2 (옛 벽 120과 같은 방식)
        tx, ty, tt, td = b["tongue"]
        for z in b["tongue_holes"]:
            s = s.cut(cyl(2.75, tt + 2, V(tx, ty - 1, z), V(0, 1, 0)))
    else:
        s = s.cut(cyl(b["hole"] / 2, h + 1, V(0, 0, zc), V(-1, 0, 0)))
        s = s.cut(cyl(b["hole"] / 2, h + 1, V(0, 0, zc), V(0, 1, 0)))
    for sx in (-1, 1):
        if b.get("wing"):
            s = s.cut(cyl(2.25, b["wing_t"] + 2, V(sx * sum(b["wing"]) / 2, -h - 1, (b["z_bot"] + b["z_top"]) / 2), V(0, 1, 0)))
        for sy in (-1, 1):
            if not b.get("grid"):
                s = s.cut(cyl(b["ins_d"] / 2, b["ins_L"], V(sx * b["ins"][0], sy * b["ins"][1], b["z_top"] - b["ins_L"])))
    s = s.removeSplitter()
    try:                                                   # 세로 모서리 R1 (날개 뿌리 안쪽 모서리 포함 → 날개가 덜 부러짐)
        ed = [e for e in s.Edges if e.Curve.TypeId == "Part::GeomLine" and abs(e.Length - (b["z_top"] - b["z_bot"])) < 1e-3
              and max(abs(e.Vertexes[0].X), abs(e.Vertexes[0].Y)) > h - 0.1]
        s = s.makeFillet(b["r"], ed)
    except Exception:
        pass
    return s


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


def ring_g(od, idd, t, rho=RHO["steel"]):
    return math.pi / 4 * (od ** 2 - idd ** 2) * t * rho / 1000


FLOAT_G = ring_g(FLOOR["od"], FLOOR["id"], FLOOR["t"]) + ring_g(BEAR["od"], BEAR["id"], BEAR["t"]) + \
    ring_g(MAG["d"], 0, MAG["L"], RHO["ndfeb"])
L_REST = SPR["L0"] - FLOAT_G * 9.81e-3 / SPR["k"]            # 바닥 무게로 눌린 길이


def floor():
    """바닥 (스프링 위): 와셔 2 + 자석. 반환 (와셔들, 자석, M5 와셔 아랫면 z)"""
    z = H["rest"] - FLOOR["t"]
    w = Part.makeCompound([washer(FLOOR["od"], FLOOR["id"], FLOOR["t"], z), washer(BEAR["od"], BEAR["id"], BEAR["t"], z - BEAR["t"])])
    mag = cyl(MAG["d"] / 2, MAG["L"], V(MAG["x"], 0, z - MAG["L"]))
    return w, mag, z - BEAR["t"]


def spring(z0, L):
    """압축 스프링 (선 가운데가 양 끝에서 선 반지름만큼 안) — 감김 수는 닫힌 길이 / 선 지름"""
    r, w = (SPR["od"] - SPR["wire"]) / 2, SPR["wire"]
    n = SPR["Ls"] / w
    h = L - w
    try:
        hx = Part.makeHelix(h / n, h, r)
        hx.translate(V(0, 0, z0 + w / 2))
        p0 = hx.Edges[0].valueAt(hx.Edges[0].FirstParameter)
        t0 = hx.Edges[0].tangentAt(hx.Edges[0].FirstParameter)
        c = Part.Wire(Part.makeCircle(w / 2, p0, t0))
        return Part.Wire(hx.Edges).makePipeShell([c], True, True)
    except Exception:
        return cyl(SPR["od"] / 2, L, V(0, 0, z0)).cut(cyl(SPR["od"] / 2 - w, L + 2, V(0, 0, z0 - 1)))


def column(z_bear):
    """스프링 받침 + 안내 스페이서 + 나사. 반환 (받침, 나사, 스페이서, 스프링, 거더 윗면 z)"""
    z_seat = z_bear - L_REST
    z_g = z_seat - SEAT["t"] - SO
    seat = washer(SEAT["od"], SEAT["id"], SEAT["t"], z_g + SO)
    scr = pan(V(0, 0, z_g - G["t"]), V(0, 0, 1), 3.0, 6.0)
    so = Part.makeCompound([hexso(0, 0, z_g, SO), hexso(0, 0, z_seat, SO)])
    return seat, scr, so, spring(z_seat, L_REST), z_g


def girder(z_g):
    t = G["t"]
    g = box(-6.35, -6.35 + G["L"], YC, YC + G["w"], z_g - t, z_g).fuse(box(-6.35, -6.35 + G["L"], YC, YC + t, z_g - G["w"], z_g))
    for i in range(3):
        g = g.cut(cyl(G["hole"] / 2, 3, V(i * G["p"], 0, z_g - 2)))
        g = g.cut(cyl(G["hole"] / 2, 3, V(i * G["p"], YC - 1, z_g - G["w"] / 2), V(0, 1, 0)))
    return g.removeSplitter()


def hall(z_g):
    """KY-024: 판 (스페이서 HSO 위, M3 × 6) + LM393 + 가변저항 3296 + 핀 4 (직각) + SS49E (다리를 세워 자석 바로 아래, 얼굴 위)
    가변저항 높이 10 때문에 판은 낮게 (올라가도 상자 밑 z −10 아래), 센서만 다리로 올림. 반환 (판·부품, 스페이서, 나사)"""
    d = HALLD
    zb = z_g + HSO
    zt = zb + d["t"]
    x0, x1 = d["x0"], d["x0"] + d["L"]
    board = box(x0, x1, -d["W"] / 2, d["W"] / 2, zb, zt).cut(cyl(1.6, 3, V(d["hole_x"], 0, zb - 1)))
    ix, iy, iz = d["ic"]
    ic = box(17.0, 17.0 + ix, -iy / 2, iy / 2, zt, zt + iz)
    px, py, pz = d["pot"]
    pot = box(30.0, 30.0 + px, -py / 2, py / 2, zt, zt + pz).cut(cyl(1.0, 1.0, V(32.25, 2.5, zt + pz - 0.8)))
    hx, hy, hz = d["hdr"]
    hdr = box(x1 - 3.0, x1 - 3.0 + hx, -hy / 2, hy / 2, zt, zt + hz)
    pins = [box(x1 - 1.75 - 0.32, x1 + 6.0, y - 0.32, y + 0.32, zt + hz / 2 - 0.32, zt + hz / 2 + 0.32) for y in (-3.81, -1.27, 1.27, 3.81)]
    return Part.makeCompound([board, ic, pot, hdr] + pins), hexso(d["hole_x"], 0, z_g, HSO), \
        Part.makeCompound([pan(V(d["hole_x"], 0, zt), V(0, 0, -1), 3.0, 6.0), pan(V(d["hole_x"], 0, z_g - G["t"]), V(0, 0, 1), 3.0, 6.0)])


def ss49e(z_mag_bottom, zt):
    """SS49E (TO-92S 4.0 × 3.0 × 1.52) 얼굴 위로 눕혀 자석 축 아래 + 다리 3 (옆으로 1 → 판으로 내려감)"""
    d = HALLD
    sx, sy, sz = d["ss49e"]
    top = z_mag_bottom - d["gap"]
    body = box(MAG["x"] - sx / 2, MAG["x"] + sx / 2, -sy / 2, sy / 2, top - sz, top)
    xl = MAG["x"] + sx / 2 + 1.0
    zm = top - sz / 2
    legs = []
    for y in (-1.27, 0.0, 1.27):
        legs.append(cyl(d["lead"] / 2, xl - (MAG["x"] + sx / 2), V(MAG["x"] + sx / 2, y, zm), V(1, 0, 0)))
        legs.append(cyl(d["lead"] / 2, zm - zt + d["lead"] / 2, V(xl, y, zt)))
    return body, Part.makeCompound(legs)


def b_mT(z):
    """막대 자석 축 위 자속 밀도 (mT), 끝면에서 z mm"""
    R, Lm = MAG["d"] / 2, MAG["L"]
    return BR / 2 * ((Lm + z) / math.hypot(R, Lm + z) - z / math.hypot(R, z)) * 1000


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
    flo, mag, zb = floor()
    seat, pscr, so, spr, z_g = column(zb)
    z_row = z_g - G["w"] / 2
    rail, car, src = slide(z_row)
    gs = Part.makeCompound([pan(V(xh, YC + G["t"], z_row), V(0, -1, 0), 3.0, 6.0) for xh in (0.0, G["p"])])
    hb, hso, hscr = hall(z_g)
    sb, sl = ss49e(mag.BoundBox.ZMin, z_g + HSO + HALLD["t"])
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
            ("303_standoffs (M3 육각 스페이서 암-암 20 + 수-암 20 — 기둥·스프링 안내, 구매)", so, gray, 0),
            ("303p_spring_seat (스프링 받침 M4 DIN 9021 — 스페이서 사이에 끼움, 구매)", seat, gray, 0),
            ("303s_screw (M3 × 6 냄비 — 거더 아래 → 스페이서, 구매)", pscr, dark, 0),
            ("304_floor (바닥 M10 DIN 9021 + 스프링 받는 판 M5 DIN 9021 — 스프링 위에 얹힘, 구매)", flo, gray, 0),
            ("304m_magnet (네오디뮴 막대 Ø6 × 10 — 바닥 아래에 자석 힘으로 붙음, 구매) [상품 미정]", mag, (0.6, 0.6, 0.65), 0),
            ("305_spring (압축 스프링 McMaster 9657K33 — 0.193 N/mm, 구매)", spr, gray, 0),
            ("306_hall_module_KY024 (판 + LM393 + 가변저항 + 핀 4, DO → UNO A1 — 눕혀서 스페이서에, 구매) [판 치수 추측]", hb, blue, 0),
            ("306h_SS49E (홀 소자 — 다리를 세워 얼굴이 자석을 봄, KY-024에 딸림)", sb, (0.15, 0.15, 0.15), 0),
            ("306l_SS49E_legs (다리 3 — 판에 납땜된 그대로 구부림)", sl, (0.8, 0.7, 0.3), 0),
            ("306o_standoff (M3 육각 스페이서 암-암 30 — 홀 판, 구매)", hso, gray, 0),
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


MOVING = ("301c", "302", "303", "304", "305", "306")
LUMP = ("304",)
ALLOW = (("300c", "300_"), ("300c", "300m"), ("301c", "301_"), ("302s", "301c"), ("302s", "302_"), ("303s", "303"),
         ("303s", "302_"), ("306s", "306"), ("306l", "306"), ("306s", "302_"), ("306o", "302_"), ("307s", "307_"), ("307s", "301_"),
         ("308s", "307_"), ("308s", "300_"))


def pen(dx, dy, z_tip):
    p = V(dx, dy, z_tip)
    s = cyl(PEN["tip_d"] / 2, PEN["tip_L"], p)
    s = s.fuse(cyl(PEN["nose_d"] / 2, PEN["body_from"] - PEN["tip_L"], p + V(0, 0, PEN["tip_L"])))
    return s.fuse(cyl(PEN["body_d"] / 2, PEN["L"] - PEN["body_from"], p + V(0, 0, PEN["body_from"])))


def check(doc):
    """(1) 0 → 행정 3 mm씩 움직이는 것 ↔ 고정 (2) 덩어리가 멈춘 뒤 기둥 쪽만 1~3 mm 더 (3) 고정끼리 (4) 움직이는 것끼리
    (5) 캐리지가 레일 안 (6) 펜이 닿는 망 구멍 수 (7) 스프링 힘·자석 ↔ 칩 틈"""
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
    rest = [o for o in mv if o not in lump and not key(o).startswith("305")]
    over = [(e, key(a), key(b), round(v, 2)) for e in (1.0, 2.0, TRIP + 1.0) for a in rest for b in lump + fx
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
    mb = [o for o in obs if key(o) == "304m_magnet"][0].Shape.BoundBox.ZMin
    ct = [o for o in obs if key(o).startswith("306h")][0].Shape.BoundBox.ZMax
    return dict(stroke=STROKE, sweep=sweep, over=over, static=static, inner=inner,
                carriage_local=(round(lo, 2), round(hi, 2)), carriage_in_rail=(lo >= CAR_RANGE[0] and hi <= CAR_RANGE[1]),
                pen_holes=(n_ok, n_all), float_g=round(FLOAT_G, 1), spring_rest=round(L_REST, 2),
                gap_rest=round(mb - ct, 2), gap_trip=round(mb - ct - TRIP, 2), B_rest_mT=round(b_mT(mb - ct), 1), B_trip_mT=round(b_mT(mb - ct - TRIP), 1), N_trip=round(SPR["k"] * TRIP, 3),
                N_lift=round(FLOAT_G * 9.81e-3, 3), standoff_gap=round(zb_gap(obs, key), 2))


def zb_gap(obs, key):
    """안내 스페이서 윗면 ↔ M5 와셔 아랫면 (줄어들 수 있는 최대)"""
    so = [o for o in obs if key(o) == "303_standoffs"][0].Shape.BoundBox.ZMax
    fl = [o for o in obs if key(o) == "304_floor"][0].Shape.BoundBox.ZMin
    return fl - so
