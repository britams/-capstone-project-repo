# -*- coding: utf-8 -*-
"""D5 개념 모델 5차 (D5e) — 이음부 보완 + 구매품 정밀 모델 + 관절 변수로 움직이는 모델 (서현 11/01, CAP-AI-20)

D5d(4차 보완)에서 바뀐 것 — D5d 이음부 검사(cad/D5e_이음부_검사.md)에서 찾은 문제를 고침
- 구동기 정밀 모델: 28BYJ-48 (몸통 Ø28×19, 귀 2개 Ø4.2 구멍 간격 35, 축 Ø5·D컷 3·길이 10, 축이 몸통 중심에서 8 mm 치우침,
  배선 상자 14.6 — 제조사 외형도), SG90 (22.2×11.8×22.7, 귀 32.2, 귀 윗면 16 — 외형도), MG90S (22.8×12.2, 문 3개, 승준 구매 목록 B2)
- 모터는 귀를 판에 나사로 고정 (D5d는 몸통 뒷면만 판에 닿음 = 고정 안 됨) / 축 → 커플링 끼움 깊이 6.5 mm 확보
- 커플링 Ø19.1×25.4 (5→8 mm, McMaster 4147N159와 같은 치수, 국내 D19L25) / T8 황동 플랜지 너트 (Ø22×3.5, 몸통 Ø10.2, 길이 15, 구멍 4×Ø3.5 PCD 16)
- 리드스크루가 블록 구멍에 그냥 끼어 있던 것 → 너트로 (바닥 캐리지·X 끝 블록 A·Y 캐리지), 지나가는 구멍은 틈 0.5
- Y 봉이 끝 블록 면에 맞대기만 → 블록에 10 mm 끼움. 바닥 가이드봉도 판·바닥판에 끼움
- 밀대(147)가 스프링(146)을 건너뛰고 로드셀에 바로 닿던 것 → 밀대 턱(칼라)이 스프링을 눌러 로드셀로 힘이 감
- 펜 들기: 홀더가 캐리지 면에 닿기만(안내 없음) → Ø3 안내 핀 2개 + 슬리브(길이 40). 혼 팔 16 mm, 탭을 혼 끝 너머까지 늘려 혼 끝이 평면을 밈
  (D5d: 혼 11.9 mm로는 들림 최대 7.9 mm < 캡 컵에서 빠지는 데 필요한 9.1 mm, 그리고 탭 모서리가 혼 면을 미는 쐐기 접촉)
- 문 3개: D5d는 문판이 슬롯 안에서 돌 자리가 없어 열리지 않음 → 서보 혼 핀이 문판 홈을 미는 '스카치 요크' 미닫이 (행정 15.6 mm)
- X 모터를 판(217)에 귀로 고정하고 판은 갠트리 레일 아래에 매닮. 빔 끝 블록 x 폭 24 → 28 (Y 모터 브래킷 팔 자리)
- 관절 변수 (스프레드시트 'Joints'): floor 바닥 승강 0~36.5 mm, xm·ym 마커 위치, horn 펜 들기 서보 각, support 팁 받침 높이,
  door_entry·door_iso·door_rel 문 서보 각. 셀 값을 바꾸고 다시 계산하면 부품이 움직인다 (Placement 식)

단위 mm, 원점 = 바닥 중심, z 위. 실측(★)은 design/2026-10-28_상용트랩_실측표.md, 나머지 잠정.
"""
import math
import FreeCAD as App
import Part

DOC_NAME = "D5e_module_kinematic"
SAVE_PATH = None
V = App.Vector

# ---------------- 치수 (D5d와 같음) ----------------
TRAP = dict(body_r=100, body_h=145, awning_top=180, awning_r=130, hole_r=27.5, ring_r=45, ring_h=10, dome_h=220, dome_r=100)
FR = dict(s=20, c=170, deck_z=180, top_z=590, cross_y=80, gantry_z=452, gantry_x=-18)   # 갠트리 받침 레일 x 25 → -18: 마커가 격자 -x 끝(xm 37.4)에 가면 레일과 겹침 (D5e 이동 검사), 격리 세로 통로(x ±8)도 피함
DECK = dict(t=5, x0=-130, x1=100, y=90)
TOP = dict(t=5, x=70, y=90)
CH = dict(cx=55, inner=32, wall=3, base_t=5, h=50, z_base=330)   # (11/12 서현) 안 40 → 32: 여왕벌 30 + 틈 1 × 2 (design/2026-11-12_마킹실_최소크기_계산)
GRID = dict(t=1.5, n=7, pitch=4.4, hole=3.0)   # (11/12) 안 32 → 7 × 7
FLOOR = dict(t=6, clear=0.5, stroke=36.5)
PORT_R, DUCT_R = 6, 8
BEND_R = 20.0                                # 통로 굽힘 중심 반지름 (안지름 12의 1.67배) — D5d는 관 두 개를 겹쳐 붙여 꺾인 곳이 막힘 덩어리였음
MK = dict(R=7.35, R_max=9.45, grip=60, body=60, cone=10, tip=4, rt=0.6)
BRG = dict(x=(7.5, 4.0, 24.0), y=(6.0, 3.0, 19.0))
CUP = dict(R=7, r=3, top=392.0, h=12)
XY = dict(rod_z=480, ya=-65, yb=57, x0=9, x1=172, yin0=-56, yin1=48, eb_t=18, eb_hw=14,   # X 봉 -x 끝 19 → 9 (받침이 옮긴 레일 위에)
          car_z0=400, car_z1=490, tab_z=462, eb_top=495, xscrew_z=425, yscrew_z=453, yrod_z=(438, 468))   # Y 봉 445/475 → 438/468: 봉을 끝 블록에 끼우면 LM8UU(z 472.5~)와 겹쳐서 내림
PARK = (65.0, -40.0)
CAM_D = 200
HORNET = dict(h=7.5)

# ---------------- 구매품 치수 (근거) ----------------
M28 = dict(D=28, L=19, off=8, ear_c=35, ear_w=7, ear_r=3.5, ear_hole=4.2, ear_t=1.0, shaft_d=5, shaft_l=10,
           flat_l=6, flat_t=3, boss_d=9, boss_h=1.5, box_w=14.6, box_r=17)          # 28BYJ-48 외형도 (components101 게시 도면)
SG90 = dict(L=22.2, W=11.8, H=22.7, tab_L=32.2, tab_top=16.0, tab_t=2.5, e=5.9, boss_r=5.9, boss_h=4.0,
            spl_r=2.4, spl_h=3.0, hole_r=1.0, hole_in=2.4)                          # TowerPro 외형도 (22.2·11.8·32.2·16·31) + 보스 높이 [가능성 높음]
MG90S = dict(L=22.8, W=12.2, H=22.7, tab_L=32.5, tab_top=16.0, tab_t=2.5, e=6.1, boss_r=6.1, boss_h=3.3,
             spl_r=2.4, spl_h=2.5, hole_r=1.0, hole_in=2.4)                         # 22.8×12.2×28.5 (판매처) — 귀 높이는 SG90과 같다고 봄 [추측]
NUT = dict(fl_r=11.0, fl_t=3.5, body_r=5.1, L=15.0, pcd=16.0, hole_r=1.75)          # T8 황동 플랜지 너트 (흔한 규격) [가능성 높음]
CPL = dict(R=9.55, L=25.4)                                                           # 5→8 mm 나선 커플링 (McMaster 4147N159: OD 19.1, 길이 25.4)
HORN = dict(Rt=14.0, rr=2.0, hub_r=3.5, t=1.5, gap=0.3)                             # 펜 들기 혼: 끝 원 중심 14 + 반지름 2 = 팔 16 (출력축–끝)
GATE = dict(ya=-20.0, rp=9.0, flap_y0=-27.0, flap_y1=-0.3, half_z=7.0, t=1.5)      # 문: 서보 축 y, 혼 핀 반지름, 문판 (φ=0 기준)
PIN = dict(r=1.5, dy=10.0, sleeve_r=3.5, sleeve_h=40.0)                             # 홀더 안내 핀 Ø3 ×2, 슬리브 길이 40

DECK_TOP = FR["deck_z"] + FR["s"] + DECK["t"]          # 205
TOP_BOT = FR["top_z"] + FR["s"]                         # 610
cx = CH["cx"]
zb = CH["z_base"]
zc0 = zb + CH["base_t"]                                 # 335 바닥판 윗면
z_floor_top_rest = zc0 + FLOOR["t"]                     # 341
z_grid_bot = zc0 + CH["h"]                              # 385
z_gt = z_grid_bot + GRID["t"]                           # 386.5
z_entry = z_floor_top_rest + 8                          # 349 입구 통로 중심
z_upper = z_grid_bot - 8                                # 377 격리·방생 통로 중심
s2 = math.sqrt(2.0)
XM0, YM0 = PARK                                         # 관절 0 자세 = 대기 자리
XB0 = XM0 + MK["R"] * s2 + 16                           # 빔·캐리지 중심 x (91.39)
h_rim = (CUP["r"] - MK["rt"]) / ((MK["R"] - MK["rt"]) / MK["cone"])
ZT0 = CUP["top"] - MK["tip"] - h_rim                    # 대기 때 팁 높이 384.44
SUPPORT_MARK = z_grid_bot - ZT0                         # 말벌 등 위에 앉을 때 홀더가 더 높은 양 0.56
HZ0 = ZT0 + MK["tip"] + MK["cone"] + 10                 # 홀더 아래 면 (대기) 408.44
HZ1 = HZ0 + 30
SERVO_Z = HZ0 + 9.5                                     # 펜 서보 축 높이 (혼 끝 윗점이 탭 아래 면에 θ = 0에서 닿음)
TAB_Z = SERVO_Z + HORN["Rt"] * 0 + HORN["rr"]           # 탭 아래 면 (대기)
LEAD = 8.0


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, h, p, d=V(0, 0, 1)):
    return Part.makeCylinder(r, h, p, d)


def tube(R, r, h, p, d=V(0, 0, 1)):
    return cyl(R, h, p, d).cut(cyl(r, h, p, d))


def bend(r, p0, t0, c, ang):
    """굽힘관(꽉 찬 원기둥 굽힘): 시작 단면 중심 p0, 시작 방향 t0, 굽힘 중심 c, ang도만큼 돌림"""
    face = Part.Face(Part.Wire(Part.makeCircle(r, V(p0), V(t0))))
    n = V(p0) - V(c)
    axis = n.cross(V(t0))                                   # 돌리는 축 (단면이 t0 방향으로 나아가게)
    return face.revolve(V(c), axis, ang)


def rot_to(zdir, xdir):
    """국부 좌표 (x, y, z) → 전역: 국부 z 축이 zdir, 국부 x 축이 xdir"""
    zd, xd = V(zdir).normalize(), V(xdir).normalize()
    yd = zd.cross(xd)
    return App.Rotation(xd, yd, zd, "ZXY")


def placed(shape, origin, zdir=V(0, 0, 1), xdir=V(1, 0, 0)):
    s = shape.copy()
    s.Placement = App.Placement(V(origin), rot_to(zdir, xdir)).multiply(s.Placement)
    return s


# ---------------- 구매품 (국부 좌표) ----------------
def m28byj48():
    """원점 = 출력축 중심의 설치면(귀 면), +z = 축 방향, 몸통 중심은 (0, -8), 귀는 x 방향"""
    d = M28
    yc = -d["off"]
    body = cyl(d["D"] / 2, d["L"], V(0, yc, -d["L"]))
    wire = box(-d["box_w"] / 2, d["box_w"] / 2, yc - d["box_r"], yc, -d["L"] + 1, -2)
    ear = box(-d["ear_c"] / 2, d["ear_c"] / 2, yc - d["ear_w"] / 2, yc + d["ear_w"] / 2, -d["ear_t"], 0)
    for sx in (-1, 1):
        ear = ear.fuse(cyl(d["ear_r"], d["ear_t"], V(sx * d["ear_c"] / 2, yc, -d["ear_t"])))
    for sx in (-1, 1):
        ear = ear.cut(cyl(d["ear_hole"] / 2, 3, V(sx * d["ear_c"] / 2, yc, -2)))
    boss = cyl(d["boss_d"] / 2, d["boss_h"], V(0, 0, 0))
    stator = body.fuse(wire).fuse(ear).fuse(boss).removeSplitter()
    sh = cyl(d["shaft_d"] / 2, d["shaft_l"] - d["boss_h"], V(0, 0, d["boss_h"]))
    z0 = d["shaft_l"] - d["flat_l"]
    for sy in (-1, 1):
        sh = sh.cut(box(-3, 3, sy * d["flat_t"] / 2, sy * 3, z0, d["shaft_l"] + 0.1) if sy > 0 else box(-3, 3, -3, -d["flat_t"] / 2, z0, d["shaft_l"] + 0.1))
    return stator, sh


def servo(d):
    """원점 = 출력축 중심의 케이스 윗면, +z = 출력 방향, 케이스 길이는 x (출력축이 +x 끝에서 e), 폭 y"""
    x0, x1 = -(d["L"] - d["e"]), d["e"]
    case = box(x0, x1, -d["W"] / 2, d["W"] / 2, -d["H"], 0)
    ext = (d["tab_L"] - d["L"]) / 2
    zt = -d["H"] + d["tab_top"]
    tab = box(x0 - ext, x1 + ext, -d["W"] / 2, d["W"] / 2, zt - d["tab_t"], zt)
    for xh in (x0 - ext + d["hole_in"], x1 + ext - d["hole_in"]):
        tab = tab.cut(cyl(d["hole_r"], 5, V(xh, 0, zt - 4)))
    boss = cyl(d["boss_r"], d["boss_h"], V(0, 0, 0)).fuse(cyl(2.6, d["boss_h"] * 0.6, V(-d["boss_r"] - 1.5, 0, 0)))
    stator = case.fuse(tab).fuse(boss).removeSplitter()
    spline = cyl(d["spl_r"], d["spl_h"], V(0, 0, d["boss_h"]))
    holes = [V(x0 - ext + d["hole_in"], 0, zt), V(x1 + ext - d["hole_in"], 0, zt)]
    return stator, spline, holes


def t8_nut():
    """원점 = 플랜지 바깥면 중심, +z = 몸통 쪽"""
    d = NUT
    n = cyl(d["fl_r"], d["fl_t"], V(0, 0, 0)).fuse(cyl(d["body_r"], d["L"] - d["fl_t"], V(0, 0, d["fl_t"])))
    for k in range(4):
        a = math.radians(45 + 90 * k)
        n = n.cut(cyl(d["hole_r"], d["fl_t"] + 1, V(d["pcd"] / 2 * math.cos(a), d["pcd"] / 2 * math.sin(a), -0.5)))
    return n.cut(cyl(4.0, d["L"] + 1, V(0, 0, -0.5))).removeSplitter()


def coupling():
    """원점 = 5 mm 쪽 끝면 중심, +z = 8 mm 쪽. 회전이 보이게 멈춤나사 구멍"""
    c = cyl(CPL["R"], CPL["L"], V(0, 0, 0))
    c = c.cut(cyl(2.5, CPL["L"] / 2, V(0, 0, 0))).cut(cyl(4.0, CPL["L"] / 2, V(0, 0, CPL["L"] / 2)))
    for z in (4.0, CPL["L"] - 4.0):
        c = c.cut(cyl(1.5, CPL["R"] + 1, V(0, 0, z), V(1, 0, 0)))
    for z in (9.5, 15.9):                                 # 나선 홈 대신 홈 2줄 (보이기용)
        c = c.cut(tube(CPL["R"] + 1, CPL["R"] - 1.2, 1.0, V(0, 0, z)))
    return c


def horn_arm(Rt, rr, hub_r, t, hub_h, bore_d):
    """원점 = 출력축, 회전축 = 국부 z, 팔은 국부 +x. 허브 아래 면 z=0"""
    hub = cyl(hub_r, hub_h, V(0, 0, 0))
    arm = box(0, Rt, -rr, rr, hub_h - t, hub_h).fuse(cyl(rr, t, V(Rt, 0, hub_h - t)))
    return hub.fuse(arm).cut(cyl(2.4, bore_d, V(0, 0, 0))).removeSplitter()


# ---------------- 조립 (관절 0 자세 = 대기) ----------------
def build():
    """P: 이름 → 형상 (움직이는 부품은 MOTION의 기준 좌표에 놓인 형상). MOTION: 이름 → (종류, 회전 중심·축)"""
    P, M = {}, {}
    s, c = FR["s"], FR["c"]

    def fixed(name, shp):
        P[name] = shp
        M[name] = ("fixed",)

    # REF 상용 트랩
    fixed("REF_trap_body", cyl(TRAP["body_r"], TRAP["body_h"], V(0, 0, 0)))
    fixed("REF_trap_awning", Part.makeCone(TRAP["awning_r"], TRAP["ring_r"], TRAP["awning_top"] - TRAP["body_h"],
                                           V(0, 0, TRAP["body_h"])).cut(cyl(TRAP["hole_r"], 100, V(0, 0, 100))))
    fixed("REF_trap_ring", tube(TRAP["ring_r"], TRAP["hole_r"], TRAP["ring_h"], V(0, 0, TRAP["awning_top"])))

    # 100 프레임
    fr = []
    for x in (-c, c):
        for y in (-c, c):
            fr.append(box(x - s / 2, x + s / 2, y - s / 2, y + s / 2, 0, TOP_BOT))
    for z in (0, FR["deck_z"], FR["top_z"]):
        for y in (-c, c):
            fr.append(box(-c + s / 2, c - s / 2, y - s / 2, y + s / 2, z, z + s))
        for x in (-c, c):
            fr.append(box(x - s / 2, x + s / 2, -c + s / 2, c - s / 2, z, z + s))
    for z in (FR["deck_z"], FR["top_z"]):
        for y in (-FR["cross_y"], FR["cross_y"]):
            fr.append(box(-c + s / 2, c - s / 2, y - s / 2, y + s / 2, z, z + s))
    gz = FR["gantry_z"]
    for y in (-c, c):
        fr.append(box(-c + s / 2, c - s / 2, y - s / 2, y + s / 2, gz, gz + s))
    for x in (-c, c):
        fr.append(box(x - s / 2, x + s / 2, -c + s / 2, c - s / 2, gz, gz + s))
    gx = FR["gantry_x"]
    fr.append(box(gx - s / 2, gx + s / 2, -c + s / 2, c - s / 2, gz, gz + s))
    fixed("100_frame", fr[0].multiFuse(fr[1:]).removeSplitter())

    z0 = FR["deck_z"] + s
    fixed("101_deck", box(DECK["x0"], DECK["x1"], -DECK["y"], DECK["y"], z0, z0 + DECK["t"]).cut(cyl(TRAP["hole_r"], 20, V(0, 0, z0 - 5))))
    fixed("102_collar", tube(TRAP["ring_r"] + 5, TRAP["ring_r"] + 2, z0 - 185, V(0, 0, 185)))

    # 110~114 입구
    fixed("111_entry_funnel", Part.makeCone(TRAP["hole_r"] + 3, DUCT_R, 30, V(0, 0, DECK_TOP)).cut(
        Part.makeCone(TRAP["hole_r"], PORT_R, 30, V(0, 0, DECK_TOP))))
    W, w = CH["inner"], CH["wall"]
    x_wall_in = cx - W / 2 - w                              # 32
    hx0 = x_wall_in - 12                                    # 문 하우징 바깥면 20
    # 110 입구 통로: 세로관 → 굽힘(중심 반지름 BEND_R) → 문 하우징 면(x = hx0). 관을 겹쳐 붙이지 않고 굽힘관으로 이음
    zb0 = z_entry - BEND_R                                  # 굽힘 시작 높이 (세로관 끝)
    out_e = cyl(DUCT_R, zb0 - (DECK_TOP + 30), V(0, 0, DECK_TOP + 30)).fuse(
        bend(DUCT_R, V(0, 0, zb0), V(0, 0, 1), V(BEND_R, 0, zb0), 90.0))
    if hx0 > BEND_R + 1e-6:                                 # 굽힘 끝 ~ 문 하우징 사이 곧은 관 (지금은 0)
        out_e = out_e.fuse(cyl(DUCT_R, hx0 - BEND_R, V(BEND_R, 0, z_entry), V(1, 0, 0)))
    in_e = cyl(PORT_R, zb0 - (DECK_TOP + 30) + 1, V(0, 0, DECK_TOP + 29)).fuse(
        bend(PORT_R, V(0, 0, zb0), V(0, 0, 1), V(BEND_R, 0, zb0), 90.0)).fuse(
        cyl(PORT_R, hx0 - BEND_R + 1, V(BEND_R, 0, z_entry), V(1, 0, 0)))
    fixed("110_entry_duct", out_e.cut(in_e).removeSplitter())
    zs = DECK_TOP + 30 + 40                                 # 빛 게이트: 세로관 양옆 (굽힘·문 서보 자리를 피함)
    fixed("114_entry_sensor_tx", box(DUCT_R, DUCT_R + 4, -3, 3, zs - 3, zs + 3))
    fixed("114_entry_sensor_rx", box(-DUCT_R - 4, -DUCT_R, -3, 3, zs - 3, zs + 3))

    # 120 마킹실, 121 바닥판, 130 격자
    walls = box(cx - W / 2 - w, cx + W / 2 + w, -W / 2 - w, W / 2 + w, zc0, z_grid_bot).cut(
        box(cx - W / 2, cx + W / 2, -W / 2, W / 2, zc0, z_grid_bot))
    for zp in (z_entry, z_upper):
        walls = walls.cut(cyl(PORT_R, w + 2, V(cx - W / 2 - w - 1, 0, zp), V(1, 0, 0)))
    walls = walls.cut(cyl(PORT_R, w + 2, V(cx + W / 2 - 1, 0, z_upper), V(1, 0, 0)))
    walls = walls.cut(cyl(2, w + 2, V(cx - 5, W / 2 - 1, z_grid_bot - 4), V(0, 1, 0)))
    fixed("120_chamber_walls", walls)
    sy = -13.0                                              # 바닥 나사 축 y
    gy = 13.0                                               # 바닥 가이드봉 y
    Wb = max(W, 40)                                         # (11/12) 바닥판은 옛 46 그대로 — 바닥 구동 옆판 위에 얹히고 베어링 플랜지(y −22)가 들어감
    fixed("121_chamber_base", box(cx - Wb / 2 - w, cx + Wb / 2 + w, -Wb / 2 - w, Wb / 2 + w, zb, zc0).cut(
        cyl(2.5, 10, V(cx, 0, zb - 1))).cut(cyl(2.0, 3, V(cx, gy, zb))))
    g = box(cx - W / 2 - w, cx + W / 2 + w, -W / 2 - w, W / 2 + w, z_grid_bot, z_grid_bot + GRID["t"])
    k = GRID["n"] // 2
    holes = [box(cx + i * GRID["pitch"] - GRID["hole"] / 2, cx + i * GRID["pitch"] + GRID["hole"] / 2,
                 j * GRID["pitch"] - GRID["hole"] / 2, j * GRID["pitch"] + GRID["hole"] / 2, z_grid_bot - 1, z_grid_bot + GRID["t"] + 1)
             for i in range(-k, k + 1) for j in range(-k, k + 1)]
    fixed("130_grid", g.cut(Part.makeCompound(holes)))

    # 140~158 승강 바닥 + 구동부 (관절 floor)
    fw = W - 2 * FLOOR["clear"]
    zf = zc0
    floor = box(cx - fw / 2, cx + fw / 2, -fw / 2, fw / 2, zf, zf + FLOOR["t"]).cut(cyl(2.0, 3, V(cx, 0, zf)))
    zc = 262.0                                              # 캐리지 아래 면 (대기)
    carriage = box(cx - 18, cx + 18, -20, 20, zc, zc + 12)
    carriage = carriage.cut(cyl(NUT["body_r"] + 0.25, 14, V(cx, sy, zc - 1))).cut(cyl(2.2, 14, V(cx, gy, zc - 1)))
    for kk in range(4):
        a = math.radians(45 + 90 * kk)
        carriage = carriage.cut(cyl(1.5, 14, V(cx + 8 * math.cos(a), sy + 8 * math.sin(a), zc - 1)))
    for name, shp in (("140_lift_floor", floor), ("158_carriage", carriage),
                      ("159_floor_nut_T8", placed(t8_nut(), V(cx, sy, zc - NUT["fl_t"]), V(0, 0, 1))),
                      ("148_load_cell", cyl(6, 6, V(cx, 0, zc + 12))),
                      ("146_spring", tube(4.5, 3.0, 10, V(cx, 0, zc + 18))),
                      ("147_push_rod", cyl(4.5, 1.5, V(cx, 0, zc + 28)).fuse(cyl(2, (zf + 3) - (zc + 29.5), V(cx, 0, zc + 29.5))).fuse(
                          cyl(2, 7, V(cx, 0, zc + 21))))):
        P[name] = shp
        M[name] = ("floor",)
    # 159 너트: 플랜지가 캐리지 아래 면에 나사 4개로 붙고 몸통(Ø10.2)은 캐리지 구멍 안으로

    notch = lambda sx: box(cx + sx * 19 - 0.1 if sx > 0 else cx - 23 - 0.1, cx + 23 + 0.1 if sx > 0 else cx - 19 + 0.1,
                           sy + M28["off"] - 5, sy + M28["off"] + 5, 219, 225)     # 모터 귀·나사 머리 자리
    fixed("151_drive_side_L", box(cx - 23, cx - 19, -23, 23, DECK_TOP, zb).cut(notch(-1)))
    fixed("151_drive_side_R", box(cx + 19, cx + 23, -23, 23, DECK_TOP, zb).cut(notch(1)))
    plate = box(cx - 19, cx + 19, -23, 23, 225, 228).cut(cyl(5.0, 10, V(cx, sy, 220))).cut(cyl(2.0, 5, V(cx, gy, 224)))
    for sx in (-1, 1):
        plate = plate.cut(cyl(M28["ear_hole"] / 2, 10, V(cx + sx * M28["ear_c"] / 2, sy + M28["off"], 220)))
    fixed("152_motor_plate", plate)
    st, sh = m28byj48()
    # 몸통은 판 아래 (귀가 판 아래 면에 나사), 축은 위로. 몸통 중심이 축에서 +y로 8 → 국부 x를 전역 -x로 (국부 y=-8 → 전역 +y)
    fixed("153_floor_stepper_28BYJ48", placed(st, V(cx, sy, 225), V(0, 0, 1), V(-1, 0, 0)))
    P["153r_floor_motor_shaft"] = placed(sh, V(0, 0, 0), V(0, 0, 1), V(-1, 0, 0))
    M["153r_floor_motor_shaft"] = ("rot_floor", V(cx, sy, 225), V(0, 0, 1))
    P["154_coupling"] = coupling()                                           # 국부: 회전 중심 기준
    P["154_coupling"].Placement = App.Placement(V(0, 0, 228.5 - 225), App.Rotation())
    M["154_coupling"] = ("rot_floor", V(cx, sy, 225), V(0, 0, 1))
    P["155_lead_screw_T8"] = cyl(4, 80, V(0, 0, 242 - 225))
    M["155_lead_screw_T8"] = ("rot_floor", V(cx, sy, 225), V(0, 0, 1))
    fixed("157_guide_rod", cyl(2, (zb + 3) - 225, V(cx, gy, 225)))

    # 문 3개 — 스카치 요크 미닫이 (서보 혼 핀이 문판 세로 홈을 밀어 y로 15.6 mm)
    def gate(name, x_wall, side, zp, key):
        xa, xb = (x_wall - 12, x_wall) if side < 0 else (x_wall, x_wall + 12)
        x_face = xa if side < 0 else xb                    # 서보 쪽 바깥면
        slot0 = xa + 5 if side < 0 else xb - 7               # 문판 슬롯 (폭 2)
        ya = GATE["ya"]
        hb = box(xa, xb, -37, 10, zp - 14, zp + 9)
        hb = hb.cut(cyl(PORT_R, 14, V(xa - 1, 0, zp), V(1, 0, 0)))
        hb = hb.cut(box(slot0, slot0 + 2, -35.5, 8.5, zp - 7.5, zp + 7.5))                       # 문판 슬롯
        hb = hb.cut(box(slot0, slot0 + 2, -32.5, 0, zp - 12.8, zp))                              # 문판 아래 턱 자리
        if side < 0:
            pocket_x0, pocket_x1 = x_face - 0.1, slot0
        else:
            pocket_x0, pocket_x1 = slot0 + 2, x_face + 0.1
        hb = hb.cut(cyl(4.5, pocket_x1 - pocket_x0, V(pocket_x0, ya, zp), V(1, 0, 0)))          # 혼 허브 자리
        hb = hb.cut(box(pocket_x0, pocket_x1, ya - 11.5, ya + 11.5, zp - 11.5, zp))              # 혼 팔·핀 자리 (아래 반)
        P[name + "_housing"] = hb
        M[name + "_housing"] = ("fixed",)
        # 문판 (φ = 0 자세): y 몸체 + 아래 턱(핀 홈)
        f0, f1 = slot0 + 0.25, slot0 + 1.75
        flap = box(f0, f1, GATE["flap_y0"], GATE["flap_y1"], zp - 7.5, zp + 6.5)      # 슬롯 바닥에 얹힘 (위 0.5 틈)
        flap = flap.fuse(box(f0, f1, ya - 4, ya + 4, zp - 12.8, zp - 7.5))
        flap = flap.cut(box(f0 - 1, f1 + 1, ya - 1.1, ya + 1.1, zp - 10.6, zp - 3.4))         # 핀 홈 (세로)
        P[name + "_flap"] = flap.removeSplitter()
        M[name + "_flap"] = ("gate_flap", key)
        # MG90S: 축 = x 방향 (하우징 쪽), 몸통은 바깥으로, 케이스 길이는 y (-y 쪽으로)
        stt, spl, hl = servo(MG90S)
        zdir = V(1, 0, 0) if side < 0 else V(-1, 0, 0)
        gap = MG90S["boss_h"] + 0.5                         # 보스 윗면과 하우징 면 사이 0.5
        org = V(x_face - gap, ya, zp) if side < 0 else V(x_face + gap, ya, zp)
        P[name + "_servo_MG90S"] = placed(stt, org, zdir, V(0, 1, 0))
        M[name + "_servo_MG90S"] = ("fixed",)
        P[name + "_servo_spline"] = placed(spl, V(0, 0, 0), zdir, V(0, 1, 0))
        M[name + "_servo_spline"] = ("gate_horn", key, org, zdir)
        # 혼: 허브(하우징 허브 자리 안) + 팔(아래, 반지름 9) + 핀(문판 홈으로)
        hub_h = abs(pocket_x1 - pocket_x0) - 0.6
        hub = cyl(4.0, hub_h, V(0, 0, 0)).cut(cyl(MG90S["spl_r"], MG90S["spl_h"] - 0.3, V(0, 0, 0)))
        arm = box(-2, 2, -GATE["rp"], 0, hub_h - 1.5, hub_h).fuse(cyl(2, 1.5, V(0, -GATE["rp"], hub_h - 1.5)))
        pinr = cyl(1.0, 2.2, V(0, -GATE["rp"], hub_h))
        hrn = hub.fuse(arm).fuse(pinr).removeSplitter()
        # 국부: z = 서보 축(전역 zdir), y = 전역 +z 쪽이 위 → 국부 -y 가 아래(핀 방향)
        P[name + "_horn"] = placed(hrn, V(0, 0, 0), zdir, V(0, 1, 0) if side < 0 else V(0, -1, 0))
        M[name + "_horn"] = ("gate_horn", key, org + zdir * (MG90S["boss_h"] + 0.3), zdir)
        # 서보 고정 기둥 2개 (하우징 면 → 귀)
        for j, hp in enumerate(hl):
            gp = App.Placement(org, rot_to(zdir, V(0, 1, 0))).multVec(hp)
            L_post = abs(gp.x - x_face)
            p0 = V(min(gp.x, x_face), gp.y, gp.z)
            post = cyl(2.2, L_post, p0, V(1, 0, 0)).cut(cyl(0.8, L_post, p0, V(1, 0, 0)))
            P[name + "_post%d" % (j + 1)] = post
            M[name + "_post%d" % (j + 1)] = ("fixed",)

    gate("112_entry_gate", x_wall_in, -1, z_entry, "door_entry")
    gate("170_isolation_gate", x_wall_in, -1, z_upper, "door_iso")
    x_wall_out = cx + W / 2 + w                              # 78
    gate("176_release_gate", x_wall_out, +1, z_upper, "door_rel")

    # 172 격리 통로, 173 깔때기, 104·105, REF 포획통
    zfun = TOP_BOT - 25
    # 172 격리 통로: 문 하우징 면(x = hx0)에서 -x로 → 굽힘 → 세로관 → 깔때기 173
    zb1 = z_upper + BEND_R
    out_i = bend(DUCT_R, V(hx0, 0, z_upper), V(-1, 0, 0), V(hx0, 0, zb1), 90.0).fuse(
        cyl(DUCT_R, zfun - zb1, V(0, 0, zb1)))
    in_i = bend(PORT_R, V(hx0, 0, z_upper), V(-1, 0, 0), V(hx0, 0, zb1), 90.0).fuse(
        cyl(PORT_R, zfun - zb1 + 1, V(0, 0, zb1))).fuse(cyl(PORT_R, 1.0, V(hx0, 0, z_upper), V(1, 0, 0)))
    fixed("172_isolation_duct", out_i.cut(in_i).removeSplitter())
    fixed("173_isolation_funnel", Part.makeCone(DUCT_R, TRAP["hole_r"] + 3, 25, V(0, 0, zfun)).cut(
        Part.makeCone(PORT_R, TRAP["hole_r"], 25, V(0, 0, zfun))))
    fixed("105_top_plate", box(-TOP["x"], TOP["x"], -TOP["y"], TOP["y"], TOP_BOT, TOP_BOT + TOP["t"]).cut(cyl(TRAP["hole_r"], 20, V(0, 0, TOP_BOT - 5))))
    fixed("104_dome_coupling", tube(TRAP["ring_r"], TRAP["hole_r"], TRAP["ring_h"], V(0, 0, TOP_BOT + TOP["t"])))
    zd = TOP_BOT + TOP["t"] + TRAP["ring_h"]
    fixed("REF_trap_dome", Part.makeSphere(TRAP["dome_r"], V(0, 0, zd + TRAP["dome_r"] - 25)).common(cyl(TRAP["dome_r"] + 1, TRAP["dome_h"], V(0, 0, zd))))
    rx0 = x_wall_out + 12
    fixed("174_release_duct", tube(DUCT_R, PORT_R, 50, V(rx0, 0, z_upper), V(1, 0, 0)))
    fixed("175_release_oneway", Part.makeCone(DUCT_R, 3.5, 15, V(rx0 + 50, 0, z_upper), V(1, 0, 0)).cut(
        Part.makeCone(PORT_R, 1.5, 15, V(rx0 + 50, 0, z_upper), V(1, 0, 0))))
    fixed("142_feeder_wick", cyl(2, 5, V(cx - 5, W / 2 - 2, z_grid_bot - 4), V(0, 1, 0)))
    fixed("144_food_tank", box(cx - 20, cx + 10, W / 2 + w, W / 2 + w + 25, z_grid_bot - 30, z_grid_bot + 5))

    # ---------------- 200~ 마커 XYZ (관절 0 = 대기 xm 65, ym -40) ----------------
    R, rt = MK["R"], MK["rt"]
    xm, ym = XM0, YM0
    xa = xm + R * s2
    xhb = xa + 6
    xb = xhb + 10
    cz0, cz1 = XY["car_z0"], XY["car_z1"]
    ztab = XY["tab_z"]
    ex, ey, ez = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
    z_t = ZT0
    zg = z_t + MK["tip"] + MK["cone"]
    holder = {}
    holder["201_marker"] = cyl(rt, MK["tip"], V(xm, ym, z_t)).fuse(Part.makeCone(rt, R, MK["cone"], V(xm, ym, z_t + MK["tip"]))).fuse(
        cyl(R, MK["grip"], V(xm, ym, zg))).fuse(cyl(MK["R_max"], MK["body"], V(xm, ym, zg + MK["grip"])))
    hz0, hz1 = HZ0, HZ1
    hb = box(xm + 2, xhb, ym - 14, ym + 14, hz0, hz1)
    vtri = Part.Face(Part.makePolygon([V(xa, ym, hz0 - 1), V(xm - 5, ym - (xa - xm + 5), hz0 - 1),
                                       V(xm - 5, ym + (xa - xm + 5), hz0 - 1), V(xa, ym, hz0 - 1)]))
    hb = hb.cut(vtri.extrude(V(0, 0, hz1 - hz0 + 2)))
    xpin = xhb - 4.0                                        # 슬리브(r 3.5)가 캐리지 면(xhb) 안쪽 0.5
    for sgn in (-1, 1):                                     # 안내 슬리브 (길이 40) + 핀 구멍
        hb = hb.fuse(cyl(PIN["sleeve_r"], PIN["sleeve_h"], V(xpin, ym + sgn * PIN["dy"], hz0)))
    for sgn in (-1, 1):
        hb = hb.cut(cyl(PIN["r"] + 0.1, PIN["sleeve_h"] + 2, V(xpin, ym + sgn * PIN["dy"], hz0 - 1)))
    tab_x0, tab_x1 = xm + 9, xb - XY["eb_hw"] - 0.1          # 탭은 끝 블록 B의 x 범위 밖
    tab = box(tab_x0, tab_x1, ym + 14, ym + 26, SERVO_Z + 5, SERVO_Z + 8).fuse(box(tab_x0, tab_x1, ym + 26, ym + 40, TAB_Z, SERVO_Z + 8))
    holder["202_marker_holder_vblock"] = hb.fuse(tab).removeSplitter()
    bar = box(xm - R - 4, xm - R, ym - 14, ym + 14, hz0, hz1)
    holder["203_clamp_strap"] = bar.fuse(box(xm - R, xm + 2, ym + 10, ym + 14, hz0, hz1)).fuse(box(xm - R, xm + 2, ym - 14, ym - 10, hz0, hz1))
    for nme, shp in holder.items():
        P[nme] = shp
        M[nme] = ("holder",)
    # 204 스프링: 홀더 윗면 → 멈춤 탭 (길이가 변함 → pose에서 다시 만듦)
    xsp = xm + MK["R_max"] + 0.6 + 3.2
    P["204_holder_spring"] = tube(3, 2, ztab - hz1, V(xsp, ym, hz1))
    M["204_holder_spring"] = ("spring", V(xsp, ym, 0))

    # 206 Y 캐리지 + 안내 핀 받침(아래)·멈춤 탭(위, 핀 윗 끝) + 서보 기둥
    car = box(xhb, xhb + 20, ym - 15, ym + 15, cz0, cz1)
    rB, rS, LB = BRG["y"]
    for zr in XY["yrod_z"]:
        car = car.cut(cyl(rB, 32, V(xb, ym - 16, zr), ey))
    car = car.cut(cyl(4.5, 32, V(xb, ym - 16, XY["yscrew_z"]), ey))
    car = car.cut(cyl(NUT["body_r"] + 0.25, NUT["L"] - NUT["fl_t"] + 0.5, V(xb, ym + 15, XY["yscrew_z"]), V(0, -1, 0)))
    for kk in range(4):                                     # Y 너트는 +y 면 (대기 ym -40에서 -y 면 플랜지가 끝 블록 A에 걸려서)
        a = math.radians(45 + 90 * kk)
        car = car.cut(cyl(1.5, 8, V(xb + 8 * math.cos(a), ym + 15.5, XY["yscrew_z"] + 8 * math.sin(a)), V(0, -1, 0)))
    stop = box(xm + MK["R_max"] + 0.6, xhb, ym - 13, ym + 13, ztab, ztab + 8)
    pin_base = box(xhb - 6, xhb, ym - 13, ym + 13, cz0 + 1, cz0 + 5)
    car = car.fuse(stop).fuse(pin_base)
    for sgn in (-1, 1):
        car = car.cut(cyl(PIN["r"], 4, V(xpin, ym + sgn * PIN["dy"], cz0 + 1))).cut(cyl(PIN["r"], 8, V(xpin, ym + sgn * PIN["dy"], ztab)))
    # 펜 서보 SG90: 축 = -x (홀더 쪽), 케이스 길이 = z (출력축이 위쪽 끝), 폭 = y, 축 높이 SERVO_Z
    stt, spl, hl = servo(SG90)
    x_ct = tab_x0 + 1.0 + HORN["gap"] + 4.0 + SG90["boss_h"]  # 혼 팔이 탭 아래 (x: 탭 범위 안)
    org = V(x_ct, ym + 21.1, SERVO_Z)
    zdir = V(-1, 0, 0)
    P["205_z_servo_SG90"] = placed(stt, org, zdir, V(0, 0, 1))
    M["205_z_servo_SG90"] = ("carriage",)
    for j, hp in enumerate(hl):
        gp = App.Placement(org, rot_to(zdir, V(0, 0, 1))).multVec(hp)
        xt = gp.x + SG90["tab_t"]                            # 귀의 몸통 바닥 쪽 면
        car = car.fuse(box(xt, xhb + 20, ym + 15 - 0.01, ym + 15 + SG90["W"], gp.z - 2.5, gp.z + 2.5).cut(
            cyl(0.8, xhb + 20 - xt, V(xt, ym + 21.1, gp.z), V(1, 0, 0))))
    P["206_y_carriage"] = car.removeSplitter()
    M["206_y_carriage"] = ("carriage",)
    P["223_holder_guide_pins"] = cyl(PIN["r"], ztab + 8 - (cz0 + 1), V(xpin, ym - PIN["dy"], cz0 + 1)).fuse(
        cyl(PIN["r"], ztab + 8 - (cz0 + 1), V(xpin, ym + PIN["dy"], cz0 + 1)))
    M["223_holder_guide_pins"] = ("carriage",)
    P["205s_z_servo_spline"] = placed(spl, V(0, 0, 0), zdir, V(0, 0, 1))
    M["205s_z_servo_spline"] = ("pen_horn", org, zdir)
    hrn = horn_arm(HORN["Rt"], HORN["rr"], HORN["hub_r"], HORN["t"], 4.0, SG90["spl_h"] - HORN["gap"])
    # 국부 x(팔) = 전역 +y (horn = 0°일 때 수평, +y 쪽)
    P["205h_z_servo_horn"] = placed(hrn, V(0, 0, 0), zdir, V(0, 1, 0))
    M["205h_z_servo_horn"] = ("pen_horn", org + zdir * (SG90["boss_h"] + HORN["gap"]), zdir)
    P["221_y_bearings_LM6UU"] = Part.makeCompound([tube(rB, rS, LB, V(xb, ym - LB / 2, zr), ey) for zr in XY["yrod_z"]])
    M["221_y_bearings_LM6UU"] = ("carriage",)
    P["224_y_nut_T8"] = placed(t8_nut(), V(xb, ym + 15 + NUT["fl_t"], XY["yscrew_z"]), V(0, -1, 0), V(1, 0, 0))
    M["224_y_nut_T8"] = ("carriage",)

    # 207 Y 봉 (끝 블록에 10 mm 끼움), 208 Y 나사, 212 끝 블록, 222 LM8UU, 225 X 너트, 209~211 Y 모터
    y0, y1 = XY["yin0"], XY["yin1"]
    et, hw = XY["eb_t"], XY["eb_hw"]
    yo = y0 - et                                            # -74
    P["207_y_rods"] = cyl(3, y1 - y0 + 20, V(xb, y0 - 10, XY["yrod_z"][0]), ey).fuse(cyl(3, y1 - y0 + 20, V(xb, y0 - 10, XY["yrod_z"][1]), ey))
    M["207_y_rods"] = ("beam",)
    ya, yb = XY["ya"], XY["yb"]
    xR, xS, xL = BRG["x"]
    eb0 = box(xb - hw, xb + hw, yo, y0, cz0, XY["eb_top"])
    eb0 = eb0.cut(cyl(xR, xL + 0.01, V(xb - xL / 2, ya, XY["rod_z"]), ex)).cut(cyl(4.5, 2 * hw + 2, V(xb - hw - 1, ya, XY["xscrew_z"]), ex))
    eb0 = eb0.cut(cyl(NUT["body_r"] + 0.25, NUT["L"] - NUT["fl_t"] + 0.5, V(xb - hw, ya, XY["xscrew_z"]), ex))
    for kk in range(4):
        a = math.radians(45 + 90 * kk)
        eb0 = eb0.cut(cyl(1.5, 8, V(xb - hw - 0.5, ya + 8 * math.cos(a), XY["xscrew_z"] + 8 * math.sin(a)), ex))
    eb0 = eb0.cut(cyl(4.5, et + 2, V(xb, yo - 1, XY["yscrew_z"]), ey))
    eb1 = box(xb - hw, xb + hw, y1, y1 + et, cz0, XY["eb_top"]).cut(cyl(xR, xL + 0.01, V(xb - xL / 2, yb, XY["rod_z"]), ex))
    eb0 = eb0.cut(cyl(4.5, 2 * hw + 2, V(xb - hw - 1, ya, XY["rod_z"]), ex))
    eb1 = eb1.cut(cyl(4.5, 2 * hw + 2, V(xb - hw - 1, yb, XY["rod_z"]), ex))
    for zr in XY["yrod_z"]:
        eb0 = eb0.cut(cyl(3, 10, V(xb, y0 - 10, zr), ey))
        eb1 = eb1.cut(cyl(3, 10, V(xb, y1, zr), ey))
    P["212_beam_end_blocks"] = eb0.fuse(eb1)
    M["212_beam_end_blocks"] = ("beam",)
    P["222_x_bearings_LM8UU"] = Part.makeCompound([tube(xR, xS, xL, V(xb - xL / 2, yy, XY["rod_z"]), ex) for yy in (ya, yb)])
    M["222_x_bearings_LM8UU"] = ("beam",)
    P["225_x_nut_T8"] = placed(t8_nut(), V(xb - hw - NUT["fl_t"], ya, XY["xscrew_z"]), V(1, 0, 0), V(0, 1, 0))
    M["225_x_nut_T8"] = ("beam",)
    zy = XY["yscrew_z"]
    pl_y1 = yo - 26.9                                       # Y 모터판 +y 면 (커플링 쪽)
    plate_y = box(xb - 21.5, xb + 21.5, pl_y1 - 3, pl_y1, zy - 12, zy + 20).cut(cyl(5.0, 5, V(xb, pl_y1 - 4, zy), ey))
    for sx in (-1, 1):
        plate_y = plate_y.cut(cyl(M28["ear_hole"] / 2, 5, V(xb + sx * M28["ear_c"] / 2, pl_y1 - 4, zy + M28["off"]), ey))
    arms = box(xb - hw, xb - 11.0, pl_y1, yo, zy - 12, zy + 20).fuse(box(xb + 11.0, xb + hw, pl_y1, yo, zy - 12, zy + 20))
    P["211_y_motor_bracket"] = plate_y.fuse(arms).removeSplitter()
    M["211_y_motor_bracket"] = ("beam",)
    # Y 모터: 축 +y, 몸통 중심이 축보다 +z 8 → 국부 y=-8이 전역 +z → 국부 x = 전역 +x 이면 국부 y = z×x ... 확인용 placed
    P["209_y_stepper_28BYJ48"] = placed(st, V(xb, pl_y1 - 3, zy), V(0, 1, 0), V(1, 0, 0))
    M["209_y_stepper_28BYJ48"] = ("beam",)
    P["209r_y_motor_shaft"] = placed(sh, V(0, 0, 0), V(0, 1, 0), V(1, 0, 0))
    M["209r_y_motor_shaft"] = ("rot_y", V(xb, pl_y1 - 3, zy), V(0, 1, 0))
    P["210_y_coupling"] = placed(coupling(), V(0, 3.5, 0), V(0, 1, 0), V(1, 0, 0))
    M["210_y_coupling"] = ("rot_y", V(xb, pl_y1 - 3, zy), V(0, 1, 0))
    y_scr0 = (pl_y1 + 0.5 + CPL["L"]) - 11.7
    P["208_y_lead_screw_T8"] = cyl(4, (y1 - 2) - y_scr0, V(0, y_scr0 - (pl_y1 - 3), 0), ey)
    M["208_y_lead_screw_T8"] = ("rot_y", V(xb, pl_y1 - 3, zy), V(0, 1, 0))

    # 213 X 봉, 218 봉 받침, 214~217 X 나사·모터·판
    x0, x1 = XY["x0"], XY["x1"]
    rz = XY["rod_z"]
    fixed("213_x_rods", cyl(4, x1 - x0, V(x0, ya, rz), ex).fuse(cyl(4, x1 - x0, V(x0, yb, rz), ex)))
    rail_top = FR["gantry_z"] + FR["s"]
    sups = []
    for yy in (ya, yb):
        for (sx0, sx1) in ((FR["gantry_x"], x0 + 12), (x1 - 12, x1)):     # -x 받침은 옮긴 레일(x -28~-8) 위까지 늘림
            sups.append(box(sx0, sx1, yy - 8, yy + 8, rail_top, rz + 8).cut(cyl(4, 14, V(max(sx0, sx1 - 12) - 1, yy, rz), ex)))   # 봉 구멍은 봉이 있는 12 mm만
    fixed("218_rod_supports", sups[0].multiFuse(sups[1:]))
    zx = XY["xscrew_z"]
    xp0 = 142.0                                             # X 모터판 -x 면 (커플링 쪽)
    pl = box(xp0, xp0 + 3, ya - 22, ya + 22, 400, FR["gantry_z"]).cut(cyl(5.0, 5, V(xp0 - 1, ya, zx), ex))
    for sy_ in (-1, 1):
        pl = pl.cut(cyl(M28["ear_hole"] / 2, 5, V(xp0 - 1, ya + sy_ * M28["ear_c"] / 2, zx - M28["off"]), ex))
    pl = pl.fuse(box(xp0, 176, ya - 22, ya + 22, FR["gantry_z"] - 4, FR["gantry_z"]))
    fixed("217_x_motor_plate", pl.removeSplitter())
    fixed("215_x_stepper_28BYJ48", placed(st, V(xp0 + 3, ya, zx), V(-1, 0, 0), V(0, -1, 0)))
    P["215r_x_motor_shaft"] = placed(sh, V(0, 0, 0), V(-1, 0, 0), V(0, -1, 0))
    M["215r_x_motor_shaft"] = ("rot_x", V(xp0 + 3, ya, zx), V(-1, 0, 0))
    P["216_x_coupling"] = placed(coupling(), V(-3.5, 0, 0), V(-1, 0, 0), V(0, -1, 0))
    M["216_x_coupling"] = ("rot_x", V(xp0 + 3, ya, zx), V(-1, 0, 0))
    x_scr_end = (xp0 - 0.5 - CPL["L"]) + 11.7               # 커플링 8 mm 쪽에 11.7 끼움
    P["214_x_lead_screw_T8"] = cyl(4, x_scr_end - 35.0, V(-((xp0 + 3) - x_scr_end), 0, 0), V(-1, 0, 0))
    M["214_x_lead_screw_T8"] = ("rot_x", V(xp0 + 3, ya, zx), V(-1, 0, 0))

    # 219 캡 컵, 220 컵 받침
    wy = -CH["inner"] / 2 - CH["wall"]
    cup_z0 = CUP["top"] - CUP["h"]
    fixed("219_cap_cup", cyl(CUP["R"], CUP["h"], V(PARK[0], PARK[1], cup_z0)).cut(cyl(CUP["r"], CUP["h"] - 2 + 1, V(PARK[0], PARK[1], cup_z0 + 2))))
    fixed("220_cup_bracket", box(PARK[0] - 10, PARK[0] + 10, PARK[1] - 8, wy, cup_z0 - 5, cup_z0))

    # 180 카메라, 181 브래킷, 182 조명, 190·191 제어부
    zcam = z_gt + CAM_D
    fixed("180_camera", box(cx - 12.5, cx + 12.5, -12, 12, zcam + 4, zcam + 14).fuse(cyl(4, 4, V(cx, 0, zcam))))
    fixed("181_camera_bracket", box(cx - 10, cx + 10, -1.5, 1.5, zcam + 14, TOP_BOT))
    fixed("182_light_ring", tube(15, 6, 3, V(cx, 0, zcam + 1)))
    fixed("190_pi5_aihat", box(-125, -40, 15, 71, DECK_TOP, DECK_TOP + 35))
    fixed("191_arduino_uno", box(-125, -56.4, -75, -21.6, DECK_TOP, DECK_TOP + 15))
    sq = [V(cx - W / 2, -W / 2, z_gt), V(cx + W / 2, -W / 2, z_gt), V(cx + W / 2, W / 2, z_gt), V(cx - W / 2, W / 2, z_gt)]
    apex = V(cx, 0, zcam)
    fcs = [Part.Face(Part.makePolygon(sq + [sq[0]]))] + [Part.Face(Part.makePolygon([sq[i], sq[(i + 1) % 4], apex, sq[i]])) for i in range(4)]
    fixed("REF_camera_view", Part.makeSolid(Part.makeShell(fcs)))

    # REF 말벌 (국부: 가슴 중심 원점, +x 머리 쪽, 바닥 z = -h/2) + 노랑 점
    def ell(a, b, cc, p):
        sp = Part.makeSphere(1.0)
        m = App.Matrix()
        m.scale(a, b, cc)
        e = sp.transformGeometry(m)
        e.translate(p)
        return e
    hz = HORNET["h"] / 2
    wasp = ell(3.0, 2.6, hz, V(0, 0, 0)).fuse(ell(6.0, 3.0, hz - 0.4, V(-8.5, 0, -0.3))).fuse(ell(2.3, 2.6, 2.4, V(4.8, 0, 0.2)))
    P["REF_hornet"] = wasp
    M["REF_hornet"] = ("hornet",)
    P["REF_mark_dot"] = cyl(1.1, 0.3, V(0, 0, hz - 0.05))
    M["REF_mark_dot"] = ("hornet",)
    return P, M


# ---------------- 자세 (관절 → Placement) ----------------
JOINT0 = dict(floor=0.0, xm=XM0, ym=YM0, horn=-20.0, support=0.0, door_entry=60.0, door_iso=60.0, door_rel=60.0,
              hornet=(cx + GRID["pitch"], 0.0, z_floor_top_rest + HORNET["h"] / 2, 0.0), dot=0)   # (x, y, z, 들림각 pitch: 90 = 머리 위)
# door 각: +60 = 닫힘, -60 = 열림 (혼 핀이 문판을 y로 9 sin φ 만큼 옮김)


def pen_lift(horn_deg, support):
    """홀더가 대기 기준보다 높은 양: 혼 끝 윗점(14 sin θ + 2)이 탭 아래 면(대기 SERVO_Z + 2)을 밀거나, 팁이 받침(support)에 앉음"""
    lift_horn = HORN["Rt"] * math.sin(math.radians(horn_deg))
    return max(support, lift_horn)


def placement(name, kind, J, M):
    m = M[name]
    k = m[0]
    dx, dy = J["xm"] - XM0, J["ym"] - YM0
    if k == "fixed":
        return App.Placement()
    if k == "floor":
        return App.Placement(V(0, 0, J["floor"]), App.Rotation())
    if k == "rot_floor":
        c, ax = m[1], m[2]
        return App.Placement(c, App.Rotation(ax, J["floor"] / LEAD * 360.0))
    if k == "beam":
        return App.Placement(V(dx, 0, 0), App.Rotation())
    if k == "rot_x":
        c, ax = m[1], m[2]
        return App.Placement(c, App.Rotation(ax, -dx / LEAD * 360.0))
    if k == "rot_y":
        c, ax = m[1], m[2]
        return App.Placement(c + V(dx, 0, 0), App.Rotation(ax, dy / LEAD * 360.0))
    if k == "carriage":
        return App.Placement(V(dx, dy, 0), App.Rotation())
    if k == "holder":
        return App.Placement(V(dx, dy, pen_lift(J["horn"], J["support"])), App.Rotation())
    if k == "pen_horn":
        c, ax = m[1], m[2]
        return App.Placement(c + V(dx, dy, 0), App.Rotation(ax, -J["horn"]))
    if k == "gate_flap":
        return App.Placement(V(0, GATE["rp"] * math.sin(math.radians(J[m[1]])), 0), App.Rotation())
    if k == "gate_horn":
        c, ax = m[2], m[3]
        sgn = 1.0 if ax.x > 0 else -1.0
        return App.Placement(c, App.Rotation(ax, sgn * J[m[1]]))
    if k == "hornet":
        x, y, z, pitch = J["hornet"]
        return App.Placement(V(x, y, z), App.Rotation(V(0, 1, 0), -pitch))
    return App.Placement()


def spring_shape(J, M):
    c = M["204_holder_spring"][1]
    dx, dy = J["xm"] - XM0, J["ym"] - YM0
    z0 = HZ1 + pen_lift(J["horn"], J["support"])
    L = XY["tab_z"] - z0
    return tube(3, 2, max(L, 1.0), V(c.x + dx, c.y + dy, z0))


def posed(P, M, J):
    out = {}
    for n, shp in P.items():
        if M[n][0] == "spring":
            out[n] = spring_shape(J, M)
            continue
        s = shp.copy()
        s.Placement = placement(n, None, J, M).multiply(s.Placement)
        out[n] = s
    return out


# ---------------- FreeCAD 문서: 스프레드시트 'Joints' 값으로 움직임 ----------------
JOINT_CELLS = [("floor", "바닥 승강 (mm, 0~36.5)"), ("xm", "마커 x (mm, 37.4~72.6, 대기 65)"), ("ym", "마커 y (mm, -40~17.6, 대기 -40)"),
               ("horn", "펜 서보 각 (°, -20 놓음 ~ 45.6 = 10 mm 들림)"), ("support", "팁 받침 높이 (mm, 컵 0 / 말벌 등 0.56)"),
               ("door_entry", "입구 문 서보 (°, 60 닫힘 / -60 열림)"), ("door_iso", "격리 문 서보 (°)"), ("door_rel", "방생 문 서보 (°)"),
               ("hx", "말벌 x"), ("hy", "말벌 y"), ("hz", "말벌 z"), ("hpitch", "말벌 머리 각 (°, 90 = 위)")]


def _bake(shp):
    """형상의 Placement를 기하에 넣고 Placement를 0으로 (식으로 움직일 때 기준)"""
    s = shp.copy()
    m = s.Placement.toMatrix()
    s.Placement = App.Placement()
    s.transformShape(m, True)
    return s


def _vec(x, y, z):
    return "create(<<vector>>; %s; %s; %s)" % (x, y, z)


def _pl(base, axis=None, ang="0"):
    ax = _vec(*axis) if axis is not None else _vec(0, 0, 1)
    return "create(<<placement>>; %s; create(<<rotation>>; %s; %s))" % (base, ax, ang)


def placement_expr(n, M):
    m = M[n]
    k = m[0]
    dx, dy = "(Joints.xm - %g)" % XM0, "(Joints.ym - %g)" % YM0
    if k == "floor":
        return _pl(_vec(0, 0, "Joints.floor"))
    if k == "rot_floor":
        c, ax = m[1], m[2]
        return _pl(_vec(c.x, c.y, c.z), (ax.x, ax.y, ax.z), "Joints.floor / %g * 360" % LEAD)
    if k == "beam":
        return _pl(_vec(dx, 0, 0))
    if k == "rot_x":
        c, ax = m[1], m[2]
        return _pl(_vec("%g + %s" % (c.x, dx), c.y, c.z), (ax.x, ax.y, ax.z), "-%s / %g * 360" % (dx, LEAD))
    if k == "rot_y":
        c, ax = m[1], m[2]
        return _pl(_vec("%g + %s" % (c.x, dx), c.y, c.z), (ax.x, ax.y, ax.z), "%s / %g * 360" % (dy, LEAD))
    if k == "carriage":
        return _pl(_vec(dx, dy, 0))
    if k == "holder":
        lift = "(Joints.support > %g * sin(Joints.horn) ? Joints.support : %g * sin(Joints.horn))" % (HORN["Rt"], HORN["Rt"])
        return _pl(_vec(dx, dy, lift))
    if k == "pen_horn":
        c, ax = m[1], m[2]
        return _pl(_vec("%g + %s" % (c.x, dx), "%g + %s" % (c.y, dy), c.z), (ax.x, ax.y, ax.z), "-Joints.horn")
    if k == "gate_flap":
        return _pl(_vec(0, "%g * sin(Joints.%s)" % (GATE["rp"], m[1]), 0))
    if k == "gate_horn":
        c, ax = m[2], m[3]
        sgn = "" if ax.x > 0 else "-"
        return _pl(_vec(c.x, c.y, c.z), (ax.x, ax.y, ax.z), "%sJoints.%s" % (sgn, m[1]))
    if k == "hornet":
        return _pl(_vec("Joints.hx", "Joints.hy", "Joints.hz"), (0, 1, 0), "-Joints.hpitch")
    return None


def make_doc(P, M, J=None, gui_colors=True):
    J = dict(JOINT0 if J is None else J)
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    sh = doc.addObject("Spreadsheet::Sheet", "Joints")
    sh.set("A1", "관절 변수 — 값을 바꾸고 다시 계산(Ctrl+R)하면 부품이 움직임 (CAP-AI-20)")
    hx, hy, hz, hpitch = J["hornet"]
    vals = dict(J, hx=hx, hy=hy, hz=hz, hpitch=hpitch)
    for i, (k, desc) in enumerate(JOINT_CELLS):
        r = i + 3
        sh.set("A%d" % r, k)
        sh.set("B%d" % r, "%g" % vals[k])
        sh.set("C%d" % r, desc)
        sh.setAlias("B%d" % r, k)
    doc.recompute()
    objs = {}
    for n, shp in P.items():
        k = M[n][0]
        if k == "spring":
            continue
        o = doc.addObject("Part::Feature", "P" + n.replace("-", "_"))    # 이름은 숫자로 시작 못 함 → 'P' + 도면부호, 라벨은 도면부호
        o.Label = n
        o.Shape = _bake(shp)
        e = placement_expr(n, M)
        if e:
            o.setExpression("Placement", e)
        objs[n] = o
    # 204 스프링: Part::Tube (길이 = 멈춤 탭 - 홀더 윗면)
    c = M["204_holder_spring"][1]
    lift = "(Joints.support > %g * sin(Joints.horn) ? Joints.support : %g * sin(Joints.horn))" % (HORN["Rt"], HORN["Rt"])
    cyls = []
    for nm, r, dz in (("P204a", 3.0, 0.0), ("P204b", 2.0, -0.5)):
        cy = doc.addObject("Part::Cylinder", nm)
        cy.Radius = r
        cy.setExpression("Height", "(%g - %g - %s + %g) * 1 mm" % (XY["tab_z"], HZ1, lift, -2 * dz))
        cy.setExpression("Placement", _pl(_vec("%g + Joints.xm - %g" % (c.x, XM0), "%g + Joints.ym - %g" % (c.y, YM0), "%g + %s + %g" % (HZ1, lift, dz))))
        cyls.append(cy)
    sp = doc.addObject("Part::Cut", "P204_holder_spring")
    sp.Label = "204_holder_spring"
    sp.Base, sp.Tool = cyls
    objs["204_holder_spring"] = sp
    doc.recompute()
    if gui_colors and App.GuiUp:
        color_doc(doc)
    return doc


def color_doc(doc):
    tr = {"REF_trap_body": 80, "REF_trap_awning": 75, "REF_trap_ring": 60, "REF_trap_dome": 88, "101_deck": 65, "105_top_plate": 70,
          "120_chamber_walls": 55, "REF_camera_view": 90, "100_frame": 40, "102_collar": 50}
    for o in doc.Objects:
        if not hasattr(o, "ViewObject") or o.ViewObject is None or o.TypeId == "Spreadsheet::Sheet":
            continue
        n = o.Label
        vo = o.ViewObject
        col = (0.75, 0.75, 0.75)
        if n.startswith("REF"):
            col = (0.92, 0.92, 0.92)
        if n.startswith("2"):
            col = (0.55, 0.62, 0.78)
        if "stepper" in n or "servo" in n:
            col = (0.25, 0.25, 0.28) if "stepper" in n else (0.15, 0.35, 0.75)
        if "28BYJ48" in n:
            col = (0.55, 0.58, 0.62)
        if "MG90S" in n or "SG90" in n:
            col = (0.12, 0.30, 0.70)
        if "nut" in n:
            col = (0.85, 0.65, 0.20)
        if "coupling" in n:
            col = (0.80, 0.80, 0.85)
        if "lead_screw" in n or "rods" in n or "guide" in n or "shaft" in n:
            col = (0.62, 0.64, 0.68)
        if "horn" in n or "spline" in n:
            col = (0.95, 0.95, 0.95)
        if "flap" in n:
            col = (0.95, 0.55, 0.15)
        if n == "201_marker":
            col = (0.98, 0.85, 0.10)
        if n == "REF_hornet":
            col = (0.30, 0.22, 0.10)
        if n == "REF_mark_dot":
            col = (1.0, 0.92, 0.0)
        if n == "100_frame":
            col = (0.62, 0.64, 0.68)
        if n == "140_lift_floor":
            col = (0.35, 0.65, 0.40)
        if n == "REF_camera_view":
            col = (0.30, 0.60, 1.00)
        vo.ShapeColor = col
        vo.LineColor = (0.1, 0.1, 0.1)
        vo.Transparency = tr.get(n, 0)


if __name__ == "__main__":
    P, M = build()
    doc = make_doc(P, M)
    if SAVE_PATH:
        doc.saveAs(SAVE_PATH)
