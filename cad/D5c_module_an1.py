# -*- coding: utf-8 -*-
"""D5 개념 모델 3차 — 안 1 바닥 승강형, 다시 그림 (CAP-AI-14)

원칙
- 모든 부품은 실제 부품 크기(보유품: 28BYJ-48 스테핑, SG90 서보 / 구매 예정: T8 리드스크루 등)로 그린다.
- 모든 부품은 다른 부품에 닿아 지지된다 (공중에 뜬 부품 없음). 상용 트랩(REF_)에는 하중 0.
- 실행 끝에 겹침 검사(부품 쌍 공통 부피)와 지지 검사(다른 부품과 최소 거리 0)를 출력한다.
- 환경 요소(비·바람)는 다루지 않는다 (서현 10/28).

단위 mm. 원점 = 바닥 중심, z 위. 실측값은 design/2026-10-28_상용트랩_실측표.md (★, 줄자 ±1~2 mm). 나머지 잠정.
STATE = "rest" (바닥 내림·마커 후퇴: 대기·진입) / "mark" (바닥 올림·마커 전진: 자세 고정·마킹)
"""
import math
import FreeCAD as App
import Part

DOC_NAME = "D5c_module_an1"
SAVE_PATH = None
STATE = "rest"
RUN_CHECK = True

V = App.Vector
# ---------------- 치수 ----------------
TRAP = dict(body_r=100, body_h=145,          # body_r 잠정 / body_h ★H22
            awning_top=180, awning_r=130,    # ★H21, 제품 26 cm
            hole_r=27.5, ring_r=45, ring_h=10,  # ★D1 55, ★D2 90, h 잠정
            dome_h=220, dome_r=100)          # ★H1, dome_r 잠정
FR = dict(s=20, c=170, deck_z=180, top_z=520, cross_y=80)   # 2020 프로파일
DECK = dict(t=5, x0=-130, x1=100, y=90)     # 101 받침판 (아크릴 5 t)
TOP = dict(t=5, x=70, y=90)                 # 105 위 받침판
CH = dict(cx=55, inner=40, wall=3, base_t=5, h=50, z_base=330)   # 120 마킹실 (z_base: 캐리지 행정 + 로드셀·스프링 높이 확보)
GRID = dict(t=1.5, n=9, pitch=4.4, hole=3.0)
FLOOR = dict(t=6, clear=0.5, stroke=36)     # 140 승강 바닥
PORT_R = 6                                   # 통로 안 반지름 (지름 12)
DUCT_R = 8                                   # 통로 바깥 반지름
MK = dict(tilt=25, retract=25)               # 마커 기울기(연직에서), 후퇴 거리
HORNET = dict(h=7.5)                         # 말벌 몸 높이 (잠정)

DECK_TOP = FR["deck_z"] + FR["s"] + DECK["t"]          # 205
TOP_BOT = FR["top_z"] + FR["s"]                         # 540
cx = CH["cx"]
zb = CH["z_base"]
z_floor_top_rest = zb + CH["base_t"] + FLOOR["t"]      # 326
z_grid_bot = zb + CH["base_t"] + CH["h"]               # 370
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

    # 160~168 마커부: 기울기 25°, 격자 중심을 겨냥
    t = math.radians(MK["tilt"])
    u = V(0, math.sin(t), math.cos(t))           # 마커 축 (후퇴 방향)
    vv = V(0, math.cos(t), -math.sin(t))         # 축에 수직 (y-z 평면)
    ex = V(1, 0, 0)
    T = V(cx, 0, z_grid_bot)                     # 겨냥점 = 격자 아랫면 중심 (흉부 윗면)

    def L(a, sp, tt):
        return T + ex * a + u * sp + vv * tt

    def lbox(a0, a1, s0, s1, t0, t1):
        b = Part.makeBox(a1 - a0, s1 - s0, t1 - t0)
        m = App.Matrix(ex.x, u.x, vv.x, 0, ex.y, u.y, vv.y, 0, ex.z, u.z, vv.z, 0, 0, 0, 0, 1)
        b = b.transformGeometry(m)
        b.translate(L(a0, s0, t0))
        return b

    def lcyl(r, s0, s1, a=0, tt=0):
        return Part.makeCylinder(r, s1 - s0, L(a, s0, tt), u)

    sh = MK["retract"] if STATE == "rest" else 0.0
    pen = lcyl(0.4, 0 + sh, 4 + sh).fuse(Part.makeCone(0.4, 4, 6, L(0, 4 + sh, 0), u)).fuse(lcyl(6, 10 + sh, 110 + sh))
    P["160_marker"] = pen
    rail = lbox(10, 18, 20, 130, -4, 4)
    P["164_marker_rail"] = rail
    P["167_marker_screw_M5"] = lcyl(2.5, 40, 130, a=24)
    P["168_marker_stepper_28BYJ48"] = lcyl(14, 130, 149, a=24, tt=8)
    clamp = lbox(-9, 9.5, 60 + sh, 75 + sh, -9, 9).cut(lcyl(6, 59 + sh, 76 + sh))
    slider = lbox(10, 30, 60 + sh, 75 + sh, -4, 9).cut(lbox(10, 18, 59 + sh, 76 + sh, -4, 4)).cut(
        lcyl(2.5, 59 + sh, 76 + sh, a=24))
    P["165_marker_carriage"] = clamp.fuse(slider).fuse(lbox(9.5, 10, 60 + sh, 75 + sh, 4, 9))
    sleeve = lcyl(8, 18, 32).cut(lcyl(6.5, 17, 33))
    membrane = lcyl(6.5, 18, 19).cut(lbox(-0.25, 0.25, 17, 20, -7, 7)).cut(lbox(-7, 7, 17, 20, -0.25, 0.25))
    arm = lbox(7, 10, 24, 30, -3, 3)
    P["166_marker_cap_slit"] = sleeve.fuse(membrane).fuse(arm)
    post = box(cx + 10, cx + 18, W / 2, W / 2 + w, z_grid_bot + GRID["t"], z_grid_bot + 80)
    post = post.cut(lbox(-50, 50, -100, 300, -100, 4))   # 레일 아랫면(t=+4, vv는 -z 성분) 아래쪽만 남김 → 레일과 면 접촉
    P["163_marker_post"] = post

    # 180 카메라 (AI 카메라 25x24 기판), 181 브래킷, 182 조명 링
    zcam = z_grid_bot + 57
    P["180_camera"] = box(cx - 12.5, cx + 12.5, -12, 12, zcam + 4, zcam + 14).fuse(cyl(4, 4, V(cx, 0, zcam)))
    P["181_camera_bracket"] = box(cx - 10, cx + 10, -1.5, 1.5, zcam + 14, TOP_BOT)
    P["182_light_ring"] = tube(15, 6, 3, V(cx, 0, zcam + 1))

    # 190 제어부: Pi 5 + AI HAT+ (85x56), 191 아두이노 UNO (68.6x53.4)
    P["190_pi5_aihat"] = box(-125, -40, 15, 71, DECK_TOP, DECK_TOP + 35)
    P["191_arduino_uno"] = box(-125, -56.4, -75, -21.6, DECK_TOP, DECK_TOP + 15)

    # 말벌 (가상선)
    P["REF_hornet"] = cyl(3.5, 20, V(cx - 10, 0, zf + FLOOR["t"] + 3.5), V(1, 0, 0))
    return P


ALLOW = {("160_marker", "166_marker_cap_slit")}   # 마킹 때 마커가 실리콘 슬릿을 벌리고 지나감 (의도)


def check(P):
    names = sorted(P)
    over, touch = [], {n: [] for n in names}
    bb = {n: P[n].BoundBox for n in names}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if a.startswith("REF") and b.startswith("REF"):
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
    return over, floating, on_trap


def show(doc, P):
    gray = {"100_frame": (0.62, 0.64, 0.68)}
    tr = {"REF_trap_body": 80, "REF_trap_awning": 75, "REF_trap_ring": 60, "REF_trap_dome": 88,
          "101_deck": 65, "105_top_plate": 65, "120_chamber_walls": 55, "REF_hornet": 30}
    for n, shp in P.items():
        o = doc.addObject("Part::Feature", n.replace("-", "_"))
        o.Label = n
        o.Shape = shp
        if App.GuiUp:
            vo = o.ViewObject
            vo.ShapeColor = gray.get(n, (0.9, 0.9, 0.9) if n.startswith("REF") else (0.72, 0.72, 0.72))
            if n == "REF_hornet":
                vo.ShapeColor = (0.95, 0.75, 0.2)
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
