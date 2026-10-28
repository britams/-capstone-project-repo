# -*- coding: utf-8 -*-
"""D5 개념 모델 4차 — 안 1 바닥 승강형 + 마커 XYZ (안 B, 서현 결정 10/28, CAP-AI-16)

3차(D5c)에서 바뀐 것
- 마커: 1자유도(격자 가운데 한 점) → X·Y·Z. 카메라가 찾은 흉부 좌표로 X·Y 이동, Z는 펜 들기 서보 + 홀더 스프링(찍는 힘 상한)
- 마커 캡: 실리콘 슬릿 → 캡 컵(대기 자리, 잉크젯 헤드 캡 원리). 마커는 V블록 + 조임 띠로 물려 다른 마커로 바꿔 끼움
- 카메라: 격자 위 57 mm → 200 mm (AI 카메라 초점 범위 20 cm~무한대, 제조사 사양). 그 아래 공간에 XYZ 이송부
- 프레임: 위 높이 520 → 590, 갠트리 레일 단(z 452) 추가

원칙 (3차와 같음)
- 모든 부품은 실제 부품 크기로 그리고, 다른 부품에 닿아 지지된다. 상용 트랩(REF_)에는 하중 0.
- 실행 끝에 겹침·지지·프레임 연결 검사 + 카메라 시야(REF_camera_view)를 가리는 부품 검사 (대기 상태에서 0이어야 함).
- 환경 요소(비·바람)는 다루지 않는다.

단위 mm. 원점 = 바닥 중심, z 위. 실측값은 design/2026-10-28_상용트랩_실측표.md (★, 줄자 ±1~2 mm). 나머지 잠정.
STATE = "rest" (바닥 내림, 마커는 캡 컵에 대기 — 카메라 시야 비움) / "mark" (바닥 올림, 마커가 흉부 좌표 위에서 찍음)
"""
import math
import FreeCAD as App
import Part

DOC_NAME = "D5d_module_an1_B"
SAVE_PATH = None
STATE = "rest"
RUN_CHECK = True

V = App.Vector
# ---------------- 치수 ----------------
TRAP = dict(body_r=100, body_h=145,          # body_r 잠정 / body_h ★H22
            awning_top=180, awning_r=130,    # ★H21, 제품 26 cm
            hole_r=27.5, ring_r=45, ring_h=10,  # ★D1 55, ★D2 90, h 잠정
            dome_h=220, dome_r=100)          # ★H1, dome_r 잠정
FR = dict(s=20, c=170, deck_z=180, top_z=590, cross_y=80, gantry_z=452, gantry_x=25)   # 2020 프로파일
DECK = dict(t=5, x0=-130, x1=100, y=90)     # 101 받침판 (아크릴 5 t)
TOP = dict(t=5, x=70, y=90)                 # 105 위 받침판
CH = dict(cx=55, inner=40, wall=3, base_t=5, h=50, z_base=330)   # 120 마킹실 (z_base: 캐리지 행정 + 로드셀·스프링 높이 확보)
GRID = dict(t=1.5, n=9, pitch=4.4, hole=3.0)
FLOOR = dict(t=6, clear=0.5, stroke=36)     # 140 승강 바닥
PORT_R = 6                                   # 통로 안 반지름 (지름 12)
DUCT_R = 8                                   # 통로 바깥 반지름
MK = dict(R=7.5, body=120, cone=10, tip=4, rt=0.6)   # 201 마커 (잠정 Ø15·길이 134 — 클램프 범위 Ø10~20, 샤피 크리에이티브 Ø14.7~18.9·134)
CUP = dict(R=7, r=3, top=392.0, h=12)       # 219 캡 컵 (실리콘): 마커 원뿔이 컵 안쪽 테두리에 앉음
XY = dict(rod_z=480, ya=-64, yb=54, x0=19, x1=172,   # 213 X 고정 봉 (Ø8): 높이·y 위치·양 끝
          yin0=-58, yin1=48,                 # 빔 끝 블록 안쪽 면 y (Y 행정 범위)
          car_z0=400, car_z1=490, tab_z=462,  # 206 Y 캐리지 높이, 스프링 멈춤 탭
          xscrew_z=425, yscrew_z=460, yrod_z=(445, 475))
PARK = (65.0, -40.0)                          # 대기 자리 (캡 컵 중심) — 카메라 시야 밖
CAM_D = 200                                   # 카메라–격자 거리 (AI 카메라 최소 초점 20 cm)
HORNET = dict(h=7.5)                         # 말벌 몸 높이 (잠정)

DECK_TOP = FR["deck_z"] + FR["s"] + DECK["t"]          # 205
TOP_BOT = FR["top_z"] + FR["s"]                         # 540
cx = CH["cx"]
zb = CH["z_base"]
z_floor_top_rest = zb + CH["base_t"] + FLOOR["t"]      # 326
z_grid_bot = zb + CH["base_t"] + CH["h"]               # 385
z_gt = z_grid_bot + GRID["t"]                          # 격자 윗면 386.5
z_floor_top_mark = z_grid_bot - HORNET["h"]            # 362.5
lift = z_floor_top_mark - z_floor_top_rest if STATE == "mark" else 0.0
z_entry = z_floor_top_rest + 8                          # 입구 통로 중심
z_upper = z_grid_bot - 8                                # 격리·방생 통로 중심


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, h, p, d=V(0, 0, 1)):
    return Part.makeCylinder(r, h, p, d)


def tube(R, r, h, p, d=V(0, 0, 1)):
    return cyl(R, h, p, d).cut(cyl(r, h, p, d))


# ---------------- 부품 ----------------
def build():
    P = {}
    s, c = FR["s"], FR["c"]

    # REF: 상용 트랩 (가상선 취급, 하중 없음)
    P["REF_trap_body"] = cyl(TRAP["body_r"], TRAP["body_h"], V(0, 0, 0))
    P["REF_trap_awning"] = Part.makeCone(TRAP["awning_r"], TRAP["ring_r"], TRAP["awning_top"] - TRAP["body_h"],
                                         V(0, 0, TRAP["body_h"])).cut(cyl(TRAP["hole_r"], 100, V(0, 0, 100)))
    P["REF_trap_ring"] = tube(TRAP["ring_r"], TRAP["hole_r"], TRAP["ring_h"], V(0, 0, TRAP["awning_top"]))

    # 100 프레임 (2020): 기둥 4, 바닥·받침·위 레일
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
    gz = FR["gantry_z"]                                  # 갠트리 단: 둘레 레일 + y 방향 받침 레일(x=25)
    for y in (-c, c):
        fr.append(box(-c + s / 2, c - s / 2, y - s / 2, y + s / 2, gz, gz + s))
    for x in (-c, c):
        fr.append(box(x - s / 2, x + s / 2, -c + s / 2, c - s / 2, gz, gz + s))
    gx = FR["gantry_x"]
    fr.append(box(gx - s / 2, gx + s / 2, -c + s / 2, c - s / 2, gz, gz + s))
    P["100_frame"] = fr[0].multiFuse(fr[1:]).removeSplitter()

    # 101 받침판, 102 칼라 (차양막 턱과 2 mm 틈, 접촉 없음)
    z0 = FR["deck_z"] + s
    P["101_deck"] = box(DECK["x0"], DECK["x1"], -DECK["y"], DECK["y"], z0, z0 + DECK["t"]).cut(
        cyl(TRAP["hole_r"], 20, V(0, 0, z0 - 5)))
    P["102_collar"] = tube(TRAP["ring_r"] + 5, TRAP["ring_r"] + 2, z0 - 185, V(0, 0, 185))

    # 110~114 입구: 깔때기 → 세로 통로 → 수평 통로 → 입구 문
    P["111_entry_funnel"] = Part.makeCone(TRAP["hole_r"] + 3, DUCT_R, 30, V(0, 0, DECK_TOP)).cut(
        Part.makeCone(TRAP["hole_r"], PORT_R, 30, V(0, 0, DECK_TOP)))
    v_duct = tube(DUCT_R, PORT_R, z_entry + DUCT_R - (DECK_TOP + 30), V(0, 0, DECK_TOP + 30))
    x_wall_in = cx - CH["inner"] / 2 - CH["wall"]          # 마킹실 -x 벽 바깥면 32
    hx0 = x_wall_in - 12                                    # 문 하우징 바깥면 20
    h_duct = tube(DUCT_R, PORT_R, hx0 + DUCT_R, V(-DUCT_R, 0, z_entry), V(1, 0, 0))
    inner_v = cyl(PORT_R, z_entry - (DECK_TOP + 30), V(0, 0, DECK_TOP + 30))
    inner_h = cyl(PORT_R, hx0 + DUCT_R + 1, V(0, 0, z_entry), V(1, 0, 0))
    P["110_entry_duct"] = v_duct.fuse(h_duct).cut(inner_v).cut(inner_h).cut(
        cyl(PORT_R, DUCT_R, V(0, 0, z_entry)))
    P["114_entry_sensor_tx"] = box(7, 13, DUCT_R, DUCT_R + 4, z_entry - 3, z_entry + 3)
    P["114_entry_sensor_rx"] = box(7, 13, -DUCT_R - 4, -DUCT_R, z_entry - 3, z_entry + 3)

    # 120 마킹실 (미끄러운 플라스틱 벽), 121 바닥판(고정), 130 격자망
    W, w = CH["inner"], CH["wall"]
    zc0 = zb + CH["base_t"]
    walls = box(cx - W / 2 - w, cx + W / 2 + w, -W / 2 - w, W / 2 + w, zc0, z_grid_bot).cut(
        box(cx - W / 2, cx + W / 2, -W / 2, W / 2, zc0, z_grid_bot))
    for zp in (z_entry, z_upper):
        walls = walls.cut(cyl(PORT_R, w + 2, V(cx - W / 2 - w - 1, 0, zp), V(1, 0, 0)))
    walls = walls.cut(cyl(PORT_R, w + 2, V(cx + W / 2 - 1, 0, z_upper), V(1, 0, 0)))
    walls = walls.cut(cyl(2, w + 2, V(cx - 5, W / 2 - 1, z_grid_bot - 4), V(0, 1, 0)))
    P["120_chamber_walls"] = walls
    P["121_chamber_base"] = box(cx - W / 2 - w, cx + W / 2 + w, -W / 2 - w, W / 2 + w, zb, zc0).cut(
        cyl(2.5, 10, V(cx, 0, zb - 1)))
    g = box(cx - W / 2 - w, cx + W / 2 + w, -W / 2 - w, W / 2 + w, z_grid_bot, z_grid_bot + GRID["t"])
    k = GRID["n"] // 2
    holes = [box(cx + i * GRID["pitch"] - GRID["hole"] / 2, cx + i * GRID["pitch"] + GRID["hole"] / 2,
                 j * GRID["pitch"] - GRID["hole"] / 2, j * GRID["pitch"] + GRID["hole"] / 2,
                 z_grid_bot - 1, z_grid_bot + GRID["t"] + 1)
             for i in range(-k, k + 1) for j in range(-k, k + 1)]
    P["130_grid"] = g.cut(Part.makeCompound(holes))

    # 140 승강 바닥 (피스톤)
    fw = W - 2 * FLOOR["clear"]
    zf = zc0 + lift
    P["140_lift_floor"] = box(cx - fw / 2, cx + fw / 2, -fw / 2, fw / 2, zf, zf + FLOOR["t"])

    # 150~158 승강 구동부: 옆판 2, 모터판, 28BYJ-48, 커플링, T8 리드스크루, 가이드봉, 캐리지
    P["151_drive_side_L"] = box(cx - 23, cx - 19, -23, 23, DECK_TOP, zb)
    P["151_drive_side_R"] = box(cx + 19, cx + 23, -23, 23, DECK_TOP, zb)
    P["152_motor_plate"] = box(cx - 19, cx + 19, -23, 23, 225, 230).cut(cyl(3, 10, V(cx, -13, 222)))
    sy = -13                                                      # 스크루 축 y
    stepper = cyl(14, 19, V(cx, sy + 8, 206)).fuse(cyl(2.5, 16, V(cx, sy, 225)))  # 몸통 + 축(Ø5)
    P["153_floor_stepper_28BYJ48"] = stepper
    P["154_coupling"] = cyl(7, 20, V(cx, sy, 231)).cut(cyl(2.5, 10, V(cx, sy, 231))).cut(cyl(4, 10, V(cx, sy, 241)))
    P["155_lead_screw_T8"] = cyl(4, (zb - 8) - 241, V(cx, sy, 241))      # 위 끝은 마킹실 바닥판 8 mm 아래
    P["157_guide_rod"] = cyl(2, zb - 230, V(cx, 13, 230))
    zc = 262 + lift
    carriage = box(cx - 18, cx + 18, -20, 20, zc, zc + 12)
    carriage = carriage.cut(cyl(4, 14, V(cx, sy, zc - 1))).cut(cyl(2, 14, V(cx, 13, zc - 1)))
    P["158_carriage"] = carriage
    P["148_load_cell"] = cyl(6, 6, V(cx, 0, zc + 12))
    P["146_spring"] = tube(4.5, 3.0, 10, V(cx, 0, zc + 18))
    P["147_push_rod"] = cyl(2, zf - (zc + 18), V(cx, 0, zc + 18))

    # 112/170/176 문 하우징 + 문판 + SG90 서보 (축은 x 방향, 문판은 y-z 평면에서 회전)
    def gate(name, x_wall, side, zp):
        # side = -1: 마킹실 -x 벽 바깥 / +1: +x 벽 바깥. 하우징 12 mm, 가운데 2 mm 슬롯에 문판.
        xa, xb = (x_wall - 12, x_wall) if side < 0 else (x_wall, x_wall + 12)
        x_face = xa if side < 0 else xb                     # 서보가 붙는 바깥면
        slot0 = xa + 5
        hb = box(xa, xb, -30, 12, zp - 8, zp + 8)
        hb = hb.cut(cyl(PORT_R, 14, V(xa - 1, 0, zp), V(1, 0, 0)))
        hb = hb.cut(box(slot0, slot0 + 2, -29, 10, zp - 7, zp + 7))
        if side < 0:
            hb = hb.cut(cyl(2.5, slot0 - xa + 1, V(xa - 0.5, -20, zp), V(1, 0, 0)))
        else:
            hb = hb.cut(cyl(2.5, xb - (slot0 + 2) + 1, V(slot0 + 1.5, -20, zp), V(1, 0, 0)))
        P[name + "_housing"] = hb
        f0, f1 = slot0 + 0.25, slot0 + 1.75
        P[name + "_flap"] = box(f0, f1, -24, 8, zp - 6.5, zp + 6.5)
        # SG90: 몸통 22.7(축 방향) x 12.2 x 22.5, 축 Ø4.8 — 축 끝이 문판 면에 닿음
        if side < 0:
            body = box(x_face - 22.7, x_face, -26.1, -13.9, zp - 6, zp + 16.5)
            shaft = cyl(2.4, f0 - x_face, V(x_face, -20, zp), V(1, 0, 0))
        else:
            body = box(x_face, x_face + 22.7, -26.1, -13.9, zp - 6, zp + 16.5)
            shaft = cyl(2.4, x_face - f1, V(f1, -20, zp), V(1, 0, 0))
        P[name + "_servo_SG90"] = body.fuse(shaft)

    gate("112_entry_gate", x_wall_in, -1, z_entry)
    gate("170_isolation_gate", x_wall_in, -1, z_upper)
    x_wall_out = cx + W / 2 + w                                    # 78
    gate("176_release_gate", x_wall_out, +1, z_upper)

    # 172 격리 통로 → 173 깔때기 → 위 받침판 구멍 → 104 포획통 결합부
    zfun = TOP_BOT - 25
    hx = tube(DUCT_R, PORT_R, hx0 + DUCT_R, V(-DUCT_R, 0, z_upper), V(1, 0, 0))
    vx = tube(DUCT_R, PORT_R, zfun - (z_upper - DUCT_R), V(0, 0, z_upper - DUCT_R))
    P["172_isolation_duct"] = hx.fuse(vx).cut(cyl(PORT_R, hx0 + DUCT_R + 1, V(0, 0, z_upper), V(1, 0, 0))).cut(
        cyl(PORT_R, zfun - z_upper + 1, V(0, 0, z_upper))).cut(cyl(PORT_R, DUCT_R, V(0, 0, z_upper)))
    P["173_isolation_funnel"] = Part.makeCone(DUCT_R, TRAP["hole_r"] + 3, 25, V(0, 0, zfun)).cut(
        Part.makeCone(PORT_R, TRAP["hole_r"], 25, V(0, 0, zfun)))
    P["105_top_plate"] = box(-TOP["x"], TOP["x"], -TOP["y"], TOP["y"], TOP_BOT, TOP_BOT + TOP["t"]).cut(
        cyl(TRAP["hole_r"], 20, V(0, 0, TOP_BOT - 5)))
    P["104_dome_coupling"] = tube(TRAP["ring_r"], TRAP["hole_r"], TRAP["ring_h"], V(0, 0, TOP_BOT + TOP["t"]))
    zd = TOP_BOT + TOP["t"] + TRAP["ring_h"]
    P["REF_trap_dome"] = Part.makeSphere(TRAP["dome_r"], V(0, 0, zd + TRAP["dome_r"] - 25)).common(
        cyl(TRAP["dome_r"] + 1, TRAP["dome_h"], V(0, 0, zd)))

    # 174 방생 통로 + 175 한 방향 실리콘 깔때기
    rx0 = x_wall_out + 12
    P["174_release_duct"] = tube(DUCT_R, PORT_R, 50, V(rx0, 0, z_upper), V(1, 0, 0))
    P["175_release_oneway"] = Part.makeCone(DUCT_R, 3.5, 15, V(rx0 + 50, 0, z_upper), V(1, 0, 0)).cut(
        Part.makeCone(PORT_R, 1.5, 15, V(rx0 + 50, 0, z_upper), V(1, 0, 0)))

    # 142 급이 심지 (+y 벽 관통), 144 먹이통 (+y 벽 바깥에 붙음)
    P["142_feeder_wick"] = cyl(2, 5, V(cx - 5, W / 2 - 2, z_grid_bot - 4), V(0, 1, 0))
    P["144_food_tank"] = box(cx - 20, cx + 10, W / 2 + w, W / 2 + w + 25, z_grid_bot - 30, z_grid_bot + 5)

    # 200~220 마커 XYZ 이송부 (안 B)
    # 위에서 보면: 마커(201) 축 (xm, ym) / +x 쪽에 V블록 홀더(202) → Y 캐리지(206) → Y 봉·나사(207·208, y 방향)
    #              Y 봉 양 끝은 빔 끝 블록(212) → X 고정 봉(213, x 방향)을 타고 움직임 → 봉 받침(218) → 프레임 갠트리 단
    R, rt = MK["R"], MK["rt"]
    if STATE == "mark":
        xm, ym = cx + GRID["pitch"], 0.0                    # 흉부 좌표 예: 격자 눈 하나 위 (i=1, j=0)
        z_t = z_grid_bot                                     # 팁이 격자 아랫면 = 눌린 말벌 등 높이
    else:
        xm, ym = PARK
        h_rim = (CUP["r"] - rt) / ((R - rt) / MK["cone"])     # 원뿔 반지름이 컵 안지름과 같아지는 높이
        z_t = CUP["top"] - MK["tip"] - h_rim                 # 원뿔이 컵 테두리에 앉은 팁 높이
    s2 = math.sqrt(2.0)
    xa = xm + R * s2                                         # V홈 꼭짓점 (90° V)
    xhb = xa + 6                                             # 홀더 뒷면 = 캐리지 앞면
    xb = xhb + 10                                            # 캐리지·빔 중심 x
    hz0 = z_t + MK["tip"] + MK["cone"] + 10                  # 홀더가 무는 구간 (원뿔 위 10 mm부터 30 mm)
    hz1 = hz0 + 30
    cz0, cz1 = XY["car_z0"], XY["car_z1"]
    ztab = XY["tab_z"]                                       # 캐리지 멈춤 탭 아랫면 (스프링 위 끝)
    ex, ey = V(1, 0, 0), V(0, 1, 0)

    # 201 마커: 팁(Ø1.2) + 원뿔 + 몸통
    P["201_marker"] = cyl(rt, MK["tip"], V(xm, ym, z_t)).fuse(
        Part.makeCone(rt, R, MK["cone"], V(xm, ym, z_t + MK["tip"]))).fuse(
        cyl(R, MK["body"], V(xm, ym, z_t + MK["tip"] + MK["cone"])))

    # 202 V블록 홀더 (+ 펜 들기 탭) — 마커 몸통이 V홈 두 면에 닿음
    hb = box(xm + 2, xhb, ym - 14, ym + 14, hz0, hz1)
    vtri = Part.Face(Part.makePolygon([V(xa, ym, hz0 - 1), V(xm - 5, ym - (xa - xm + 5), hz0 - 1),
                                       V(xm - 5, ym + (xa - xm + 5), hz0 - 1), V(xa, ym, hz0 - 1)]))
    hb = hb.cut(vtri.extrude(V(0, 0, hz1 - hz0 + 2)))
    lift_tab = box(xm + 9, xhb, ym + 14, ym + 30, hz0 + 11, hz0 + 14)
    P["202_marker_holder_vblock"] = hb.fuse(lift_tab)

    # 203 조임 띠: 마커 반대쪽 면을 눌러 V홈에 붙임 (나사 조임, 지름 Ø10~20 수용)
    bar = box(xm - R - 4, xm - R, ym - 14, ym + 14, hz0, hz1)
    arm1 = box(xm - R, xm + 2, ym + 10, ym + 14, hz0, hz1)
    arm2 = box(xm - R, xm + 2, ym - 14, ym - 10, hz0, hz1)
    P["203_clamp_strap"] = bar.fuse(arm1).fuse(arm2)

    # 204 홀더 스프링: 찍는 힘 상한 (홀더 윗면 ↔ 캐리지 탭)
    P["204_holder_spring"] = tube(3, 2, ztab - hz1, V(xm + 12.8, ym, hz1))

    # 205 Z 서보 (펜 들기, SG90): 캐리지 +y 면 아래쪽(Y 봉보다 낮게). 혼이 옆으로 누운 상태 = 놓음 (그림의 두 상태). 혼을 세우면 탭을 들어 올림
    sv_body = box(xm + 18, xm + 40.5, ym + 15, ym + 27.2, cz0, cz0 + 22.7)
    sv_shaft = cyl(2.4, 4, V(xm + 14, ym + 21.1, cz0 + 16), ex)
    sv_horn = box(xm + 12.5, xm + 14, ym + 19.6, ym + 33, cz0 + 14.5, cz0 + 17.5)
    P["205_z_servo_SG90"] = sv_body.fuse(sv_shaft).fuse(sv_horn)

    # 206 Y 캐리지 (+ 스프링 멈춤 탭): Y 봉 2개(Ø6)·Y 나사(T8) 너트
    car = box(xhb, xhb + 20, ym - 15, ym + 15, cz0, cz1)
    for zr in XY["yrod_z"]:
        car = car.cut(cyl(3, 32, V(xb, ym - 16, zr), ey))
    car = car.cut(cyl(4, 32, V(xb, ym - 16, XY["yscrew_z"]), ey))
    car = car.fuse(box(xm + 9, xhb, ym - 6, ym + 6, ztab, ztab + 8))
    P["206_y_carriage"] = car

    # 207 Y 봉 (Ø6, 2개), 208 Y 리드스크루 (T8)
    y0, y1 = XY["yin0"], XY["yin1"]
    P["207_y_rods"] = cyl(3, y1 - y0, V(xb, y0, XY["yrod_z"][0]), ey).fuse(cyl(3, y1 - y0, V(xb, y0, XY["yrod_z"][1]), ey))
    P["208_y_lead_screw_T8"] = cyl(4, y1 - (-80), V(xb, -80, XY["yscrew_z"]), ey)

    # 212 빔 끝 블록 2개: X 고정 봉 구멍, (-y 블록) X 나사 너트·Y 나사 구멍
    ya, yb = XY["ya"], XY["yb"]
    eb0 = box(xb - 10, xb + 10, y0 - 12, y0, cz0, XY["rod_z"] + 10)
    eb0 = eb0.cut(cyl(4, 22, V(xb - 11, ya, XY["rod_z"]), ex)).cut(cyl(4, 22, V(xb - 11, ya, XY["xscrew_z"]), ex))
    eb0 = eb0.cut(cyl(4, 14, V(xb, y0 - 13, XY["yscrew_z"]), ey))
    eb1 = box(xb - 10, xb + 10, y1, y1 + 12, cz0, XY["rod_z"] + 10).cut(cyl(4, 22, V(xb - 11, yb, XY["rod_z"]), ex))
    P["212_beam_end_blocks"] = eb0.fuse(eb1)

    # 209 Y 모터 28BYJ-48 (-y 끝 블록 바깥), 210 커플링, 211 모터 브래킷
    zy = XY["yscrew_z"]
    P["209_y_stepper_28BYJ48"] = cyl(14, 19, V(xb, -117, zy + 8), ey).fuse(cyl(2.5, 16, V(xb, -98, zy), ey))
    P["210_y_coupling"] = cyl(7, 20, V(xb, -90, zy), ey).cut(cyl(2.5, 10, V(xb, -90, zy), ey)).cut(cyl(4, 10, V(xb, -80, zy), ey))
    br = box(xb - 10, xb + 10, -98, -95, zy - 10, zy + 26).cut(cyl(3, 5, V(xb, -99, zy), ey))
    br = br.fuse(box(xb - 10, xb - 7.5, -95, y0 - 12, zy - 10, zy + 26)).fuse(box(xb + 7.5, xb + 10, -95, y0 - 12, zy - 10, zy + 26))
    P["211_y_motor_bracket"] = br

    # 213 X 고정 봉 (Ø8, 2개), 218 봉 받침 4개 (갠트리 단 레일 위)
    x0, x1 = XY["x0"], XY["x1"]
    rz = XY["rod_z"]
    P["213_x_rods"] = cyl(4, x1 - x0, V(x0, ya, rz), ex).fuse(cyl(4, x1 - x0, V(x0, yb, rz), ex))
    rail_top = FR["gantry_z"] + FR["s"]
    sups = []
    for yy in (ya, yb):
        for (sx0, sx1) in ((x0, x0 + 12), (x1 - 12, x1)):
            sups.append(box(sx0, sx1, yy - 8, yy + 8, rail_top, rz + 8).cut(cyl(4, 14, V(sx0 - 1, yy, rz), ex)))
    P["218_rod_supports"] = sups[0].multiFuse(sups[1:])

    # 214 X 리드스크루 (T8), 216 커플링, 215 X 모터 28BYJ-48, 217 X 모터 판 (+x 둘레 레일 안쪽 면에 붙음)
    zx = XY["xscrew_z"]
    P["214_x_lead_screw_T8"] = cyl(4, 127 - 35, V(35, ya, zx), ex)
    P["216_x_coupling"] = cyl(7, 20, V(117, ya, zx), ex).cut(cyl(4, 10, V(117, ya, zx), ex)).cut(cyl(2.5, 10, V(127, ya, zx), ex))
    P["215_x_stepper_28BYJ48"] = cyl(14, 19, V(137, ya, zx - 8), ex).fuse(cyl(2.5, 10, V(127, ya, zx), ex))
    xr_in = FR["c"] - FR["s"] / 2                            # +x 둘레 레일 안쪽 면 160
    P["217_x_motor_plate"] = box(xr_in - 4, xr_in, ya - 16, ya + 16, 400, rail_top)

    # 219 캡 컵 (실리콘, 대기 자리) + 220 컵 받침 (마킹실 -y 벽 바깥면에 붙음)
    wy = -CH["inner"] / 2 - CH["wall"]
    cup_z0 = CUP["top"] - CUP["h"]
    P["219_cap_cup"] = cyl(CUP["R"], CUP["h"], V(PARK[0], PARK[1], cup_z0)).cut(cyl(CUP["r"], CUP["h"] - 2 + 1, V(PARK[0], PARK[1], cup_z0 + 2)))
    P["220_cup_bracket"] = box(PARK[0] - 10, PARK[0] + 10, PARK[1] - 8, wy, cup_z0 - 5, cup_z0)

    # 180 카메라 (AI 카메라 25x24 기판), 181 브래킷, 182 조명 링
    zcam = z_gt + CAM_D                         # 렌즈 아랫면
    P["180_camera"] = box(cx - 12.5, cx + 12.5, -12, 12, zcam + 4, zcam + 14).fuse(cyl(4, 4, V(cx, 0, zcam)))
    P["181_camera_bracket"] = box(cx - 10, cx + 10, -1.5, 1.5, zcam + 14, TOP_BOT)
    P["182_light_ring"] = tube(15, 6, 3, V(cx, 0, zcam + 1))

    # 190 제어부: Pi 5 + AI HAT+ (85x56), 191 아두이노 UNO (68.6x53.4)
    P["190_pi5_aihat"] = box(-125, -40, 15, 71, DECK_TOP, DECK_TOP + 35)
    P["191_arduino_uno"] = box(-125, -56.4, -75, -21.6, DECK_TOP, DECK_TOP + 15)

    # 카메라 시야 (가상선): 렌즈 → 마킹실 안쪽 40x40 (격자 윗면)
    sq = [V(cx - CH["inner"] / 2, -CH["inner"] / 2, z_gt), V(cx + CH["inner"] / 2, -CH["inner"] / 2, z_gt),
          V(cx + CH["inner"] / 2, CH["inner"] / 2, z_gt), V(cx - CH["inner"] / 2, CH["inner"] / 2, z_gt)]
    apex = V(cx, 0, zcam)
    fcs = [Part.Face(Part.makePolygon(sq + [sq[0]]))] + [Part.Face(Part.makePolygon([sq[i], sq[(i + 1) % 4], apex, sq[i]])) for i in range(4)]
    P["REF_camera_view"] = Part.makeSolid(Part.makeShell(fcs))

    # 말벌 (가상선)
    P["REF_hornet"] = cyl(3.5, 20, V(cx - 10, 0, zf + FLOOR["t"] + 3.5), V(1, 0, 0))
    return P


ALLOW = set()


def check(P):
    names = sorted(P)
    over, touch = [], {n: [] for n in names}
    bb = {n: P[n].BoundBox for n in names}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if a.startswith("REF") and b.startswith("REF"):
                continue
            if "REF_camera_view" in (a, b):
                continue
            A, B = bb[a], bb[b]
            if not A.intersect(B):
                continue
            d = P[a].distToShape(P[b])[0]
            if d < 1e-3:
                vol = P[a].common(P[b]).Volume
                if vol > 1e-2 and (a, b) not in ALLOW and (b, a) not in ALLOW:
                    over.append((a, b, round(vol, 2)))
                else:
                    touch[a].append(b)
                    touch[b].append(a)
    floating = [n for n in names if not n.startswith("REF") and not [m for m in touch[n] if not m.startswith("REF")]]
    on_trap = sorted({(n, m) for n in names if not n.startswith("REF") for m in touch[n] if m.startswith("REF") and m != "REF_hornet"})
    # 프레임에서 닿음으로 이어지는지 (REF 제외) — 덩어리째 떠 있는 부품 찾기
    seen, stack = {"100_frame"}, ["100_frame"]
    while stack:
        n = stack.pop()
        for m in touch[n]:
            if not m.startswith("REF") and m not in seen:
                seen.add(m)
                stack.append(m)
    not_connected = [n for n in names if not n.startswith("REF") and n not in seen]
    print("STATE", STATE, "parts", len(names))
    print("NOT_CONNECTED_TO_FRAME", not_connected)
    print("OVERLAP", over)
    print("FLOATING", floating)
    print("TOUCHING_TRAP", on_trap)
    vw = P["REF_camera_view"]
    ok_in_view = {"180_camera", "182_light_ring", "130_grid", "120_chamber_walls"}
    blockers = [n for n in names if not n.startswith("REF") and n not in ok_in_view
                and P[n].BoundBox.intersect(vw.BoundBox) and P[n].common(vw).Volume > 1e-2]
    print("CAMERA_VIEW_BLOCKED_BY", blockers)
    return over, floating, on_trap


def show(doc, P):
    gray = {"100_frame": (0.62, 0.64, 0.68)}
    tr = {"REF_trap_body": 80, "REF_trap_awning": 75, "REF_trap_ring": 60, "REF_trap_dome": 88,
          "101_deck": 65, "105_top_plate": 65, "120_chamber_walls": 55, "REF_hornet": 30, "REF_camera_view": 85}
    for n, shp in P.items():
        o = doc.addObject("Part::Feature", n.replace("-", "_"))
        o.Label = n
        o.Shape = shp
        if App.GuiUp:
            vo = o.ViewObject
            vo.ShapeColor = gray.get(n, (0.9, 0.9, 0.9) if n.startswith("REF") else (0.72, 0.72, 0.72))
            if n == "REF_hornet":
                vo.ShapeColor = (0.95, 0.75, 0.2)
            if n == "REF_camera_view":
                vo.ShapeColor = (0.3, 0.6, 1.0)
            if n.startswith("2"):
                vo.ShapeColor = (0.55, 0.62, 0.78)      # XYZ 마킹부
            if n == "201_marker":
                vo.ShapeColor = (0.95, 0.95, 0.95)
            vo.LineColor = (0.05, 0.05, 0.05)
            vo.Transparency = tr.get(n, 0)


if __name__ == "__main__":
    P = build()
    if RUN_CHECK:
        check(P)
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    show(doc, P)
    doc.recompute()
    if SAVE_PATH:
        doc.saveAs(SAVE_PATH)
