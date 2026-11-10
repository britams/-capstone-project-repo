# -*- coding: utf-8 -*-
"""전기 계통 계산 (서현, 2026-11-02, CAP-AI-22) — D5e 기준

하는 일
  1) 부품 전류표 (근거 표시)            → LOADS
  2) 상태별 구동 레일(5 V) 전류·Pi 레일 전력 → STATE_TABLE
  3) 최대 전류 2가지 (규칙 지킬 때 / 켤 때 서보 동시)  → 퓨즈 고르기
  4) 전선 굵기와 전압 강하
  5) 배선 길이 (D5e 좌표에서 직각 경로 × 1.2 + 끝 여유, 움직이는 부품은 휨 고리)
  6) 하루 에너지·배터리 시나리오
  7) 바닥 모터 HOLD F 유지 전류가 필요한가 (기어 마찰 vs 역구동 토크)

실행:  python design/control_sim/elec_budget.py   →  design/control_sim/out/elec_results.json + 표 출력
표기: [확실] 사양·계산 / [가능성 높음] 근거 있는 값, 실측 전 / [추측] 실측 필요
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

V_A = 5.1     # Pi 공식 27 W 어댑터 (5.1 V 5 A) [확실 — 보유품 사양]
V_B = 5.0     # 구동 레일 5 V 3 A 어댑터 [확실 — 보유품 사양]
PSU_B_MAX = 3.0
ETA_ADAPTER = 0.85   # 벽 어댑터 효율 [가능성 높음]

# ---------------------------------------------------------------------------
# 1) 부품 전류표  (A, 구동 레일 B 5 V) / (W, Pi 레일 A)
# ---------------------------------------------------------------------------
R_COIL = 50.0                  # 28BYJ-48 상 저항 50 Ω [확실 — 제조사 사양]
VCE_ULN = 0.9                  # ULN2003 달링턴 포화 전압 (100 mA에서 약 0.9 V) [가능성 높음 — TI 데이터시트 대표값]
I_PHASE = (V_B - VCE_ULN) / R_COIL          # 0.082 A
I_STEP_AVG = 1.5 * I_PHASE                   # 반걸음: 1상·2상이 번갈아 → 평균 1.5상
I_STEP_PEAK = 2.0 * I_PHASE
I_ULN_LED = 0.003 * 1.5                      # ULN2003 보드 상 표시 LED (상당 약 3 mA) [추측]

LOADS = {
    # 구동 레일 B
    "stepper":      dict(rail="B", off=0.0, move=I_STEP_AVG + I_ULN_LED, hold=I_STEP_AVG + I_ULN_LED, peak=I_STEP_PEAK + 0.006,
                         src="28BYJ-48 50 Ω, ULN2003 0.9 V 강하 → 상당 %.0f mA, 반걸음 평균 1.5상 [확실 계산 / 강하값 가능성 높음]" % (I_PHASE * 1000)),
    "sg90_pen":     dict(rail="B", detached=0.004, idle=0.010, move=0.25, stall=0.65,
                         src="SG90 움직일 때 약 0.25 A, 막힘 약 0.65 A [가능성 높음 — 흔한 측정값, 실측 필요]"),
    "mg90s_door":   dict(rail="B", detached=0.004, idle=0.010, move=0.20, stall=0.75,
                         src="MG90S 무부하 90 mA, 막힘 750 mA @4.8 V [확실 — 판매처 사양] / 미닫이 이동 평균 0.2 A [추측]"),
    "ir_emitter":   dict(rail="B", on=0.020, src="Adafruit 2167 송신 20 mA @5 V [확실 — 제조사]; 문 빔 낱개 LED는 220 Ω → 17 mA (11/06 21시) — 20 mA로 보수적으로 둠"),
    "ir_receiver":  dict(rail="B", on=0.002, src="수신부 자체 전류 (공개값 없음) [추측]"),
    "pullup":       dict(rail="B", on=V_B / 10e3, src="10 kΩ 풀업, 빔이 끊겼을 때(LOW)만 0.5 mA [확실 계산]"),
    "light_top":    dict(rail="B", on=0.20, src="위 링 조명 182 [추측 — 보유 조명 실측 필요]"),
    "light_bot":    dict(rail="B", on=0.10, src="아래 조명 [추측]"),
    "light_exit":   dict(rail="B", on=0.0, src="출구 조명 — 없앰 (승준 SJ-45 11/06: 굴뚝 위 하늘빛, 밤 LED는 벌레를 부름)"),
    "mosfet_led":   dict(rail="B", on=0.003, src="MOSFET 모듈 표시 LED [추측]"),
    "pump":         dict(rail="B", on=0.5, stall=0.8, src="급이 펌프 Adafruit 3910 0.5 A [확실 — Adafruit 페이지] / 막힘 0.8 A [추측] (CAP-AI-59)"),
    # Pi 레일 A (W)
    "pi5":          dict(rail="A", halt=0.01, idle=3.0, active=4.5, peak=8.8,
                         src="Pi 5 대기 약 3.0 W, CPU 4코어 최대 약 8.8 W (raspberry.tips 측정), 꺼짐 0.01 W (POWER_OFF_ON_HALT=1, Jeff Geerling) [가능성 높음]. 'active' 4.5 W는 [추측]"),
    "ai_camera":    dict(rail="A", off=0.0, standby=0.3, run=1.87,
                         src="AI 카메라 모델 실행 중 약 1.87 W (Hackster 측정) [가능성 높음] / 대기 0.3 W [추측]"),
    "ai_hat":       dict(rail="A", off=0.0, idle=0.3, run=1.5,
                         src="Hailo-8L 보통 1.5 W (CNX) [가능성 높음] / 쉴 때 0.3 W [추측]"),
    "uno":          dict(rail="A", on=0.25, src="UNO R3 약 50 mA (16U2 + 328P + LED) [가능성 높음], Pi USB에서 받음"),
    "hx711":        dict(rail="A", on=0.03, src="HX711 1.5 mA + 1 kΩ 브리지 약 4 mA [가능성 높음], UNO 1 5V 핀에서 받음"),
}


N_GATE = 9   # G1, 문마다 2개(G2·G2b, G3·G3b, G5·G5b), G4, G6 — 서현 11/02 결정 (원래 6)


def rail_b(stepper_move=0, stepper_hold=0, pen="idle", doors=("idle", "idle", "idle"), emit=N_GATE, rx=N_GATE, blocked=0,
           top=0, bot=0, exit_=0, pump=0, peak=False):
    """구동 레일 B 전류 (A). peak=True면 스테핑은 2상, 서보 move는 막힘값으로 본다."""
    st = LOADS["stepper"]
    i = stepper_move * (st["peak"] if peak else st["move"]) + stepper_hold * (st["peak"] if peak else st["hold"])
    sg = LOADS["sg90_pen"]
    i += sg["stall"] if (peak and pen == "move") else sg[pen]
    mg = LOADS["mg90s_door"]
    for d in doors:
        i += mg["stall"] if (peak and d == "move") else mg[d]
    i += emit * LOADS["ir_emitter"]["on"] + rx * LOADS["ir_receiver"]["on"] + blocked * LOADS["pullup"]["on"]
    i += top * LOADS["light_top"]["on"] + bot * LOADS["light_bot"]["on"] + exit_ * LOADS["light_exit"]["on"]
    i += (top + bot + exit_ + (1 if emit else 0) + pump) * LOADS["mosfet_led"]["on"]
    i += pump * (LOADS["pump"]["stall"] if peak else LOADS["pump"]["on"])
    return i


def rail_a(pi="idle", cam="run", hat="idle"):
    """Pi 레일 A 전력 (W). UNO 2개 + HX711 포함."""
    return (LOADS["pi5"][pi] + LOADS["ai_camera"][cam] + LOADS["ai_hat"][hat]
            + 2 * LOADS["uno"]["on"] + LOADS["hx711"]["on"])


# ---------------------------------------------------------------------------
# 2) 상태별 표 (제어 순서 0~8단계와 같은 이름)
# ---------------------------------------------------------------------------
def state_table(hold_f):
    hf = 1 if hold_f else 0
    rows = [
        ("0 켤 때 원점 찾기 (F → X·Y)", dict(stepper_move=2, stepper_hold=hf), dict(pi="active", cam="standby", hat="idle")),
        ("대기 (아래 조명 켬)", dict(stepper_hold=hf, bot=1), dict(pi="idle", cam="run", hat="idle")),
        ("1 진입 → 입구 문 닫기 (0.2 s)", dict(stepper_hold=hf, bot=1, doors=("move", "idle", "idle"), blocked=1), dict(pi="active", cam="run", hat="idle")),
        ("2 판별 (위 조명)", dict(stepper_hold=hf, top=1), dict(pi="active", cam="run", hat="run")),
        ("3 누르기 + X·Y 미리 이동", dict(stepper_move=3, bot=1), dict(pi="active", cam="run", hat="idle")),
        ("4 자세·흉부 촬영", dict(stepper_hold=hf, top=1), dict(pi="active", cam="run", hat="run")),
        ("5 찍기 (펜 서보)", dict(stepper_hold=hf, top=1, pen="move"), dict(pi="active", cam="run", hat="idle")),
        ("6 급이·건조", dict(stepper_hold=hf, bot=1), dict(pi="idle", cam="run", hat="idle")),
        ("7 방생 문 열고 기다림 (마킹실 불 끔, 굴뚝 하늘빛)", dict(stepper_hold=hf, doors=("idle", "idle", "move")), dict(pi="active", cam="run", hat="idle")),
        ("8 격리 문 열고 기다림", dict(stepper_hold=hf, doors=("idle", "move", "idle")), dict(pi="active", cam="run", hat="idle")),
        ("밤 (Pi 꺼짐, UNO 꺼짐)", dict(emit=0, rx=N_GATE, pen="detached", doors=("detached",) * 3), dict(pi="halt", cam="off", hat="off")),
    ]
    out = []
    for name, b, a in rows:
        night = name.startswith("밤")
        ib = rail_b(**b)
        ipk = rail_b(peak=True, **b)
        pa = rail_a(**a) if not night else LOADS["pi5"]["halt"]
        out.append(dict(state=name, iB_typ=round(ib, 3), iB_peak=round(ipk, 3), pB_W=round(ib * V_B, 2), pA_W=round(pa, 2)))
    return out


# ---------------------------------------------------------------------------
# 3) 최대 전류
# ---------------------------------------------------------------------------
def worst_cases():
    rule = rail_b(stepper_move=3, doors=("move", "idle", "idle"), pen="idle", top=1, bot=1, exit_=1, blocked=N_GATE, peak=True)
    boot_all = rail_b(stepper_hold=1, pen="move", doors=("move", "move", "move"), blocked=0, peak=True)
    boot_seq = rail_b(stepper_hold=1, pen="idle", doors=("move", "idle", "idle"), peak=True)
    feed = rail_b(stepper_hold=3, pen="idle", top=0, bot=1, blocked=N_GATE, pump=1, peak=True)   # 펌프는 문과 같이 안 돎 (펌웨어 ERR BUSY)
    return dict(
        rule_kept_A=round(rule, 2),
        boot_all_servos_A=round(boot_all, 2),
        boot_staggered_A=round(boot_seq, 2),
        feed_pump_A=round(feed, 2),
        note="규칙: 서보는 한 번에 하나 (문 3개·펜). 지금 펌웨어 setup()은 서보 4개를 한꺼번에 attach·write → 켤 때 위치가 다르면 4개가 동시에 움직임",
    )


# 퓨즈: 어댑터가 3 A에서 스스로 전류를 묶으므로 3 A 퓨즈는 거의 끊어지지 않음 → 정상 최대의 약 1.4배인 2.5 A 지연형
FUSE = dict(rating_A=2.5, kind="T (지연형) 5×20 유리관 또는 2.5 A 폴리퓨즈",
            why="정상 최대 약 1.8 A × 1.4 ≈ 2.5 A. 3 A 어댑터는 과전류 때 스스로 전압을 떨어뜨리므로 3 A 퓨즈는 단락에서도 늦다 [가능성 높음]")

# ---------------------------------------------------------------------------
# 4) 전선 굵기 (구리, 20 °C) [확실 — AWG 표]
# ---------------------------------------------------------------------------
AWG_MOHM_PER_M = {18: 20.9, 20: 33.3, 22: 52.9, 24: 84.2, 26: 133.9, 28: 212.9}
AWG_MAX_A_CHASSIS = {18: 16, 20: 11, 22: 7, 24: 3.5, 26: 2.2, 28: 1.4}   # 섀시 배선 허용 [가능성 높음 — 흔한 표, 보수적으로 절반만 씀]


def drop(awg, length_m, amps):
    """왕복 전압 강하 (V)."""
    return 2 * length_m * AWG_MOHM_PER_M[awg] / 1000 * amps


# ---------------------------------------------------------------------------
# 5) 배선 길이 — D5e 좌표 (mm, 원점 = 트랩 축, z = 바닥에서 위)
#    근거: cad/D5e_module_kinematic.py (cx 55, 입구 통로 z 349, 격리·방생 z 377, 데크 윗면 205, 위판 아래 610,
#          X 모터판 x 142, X 봉 y -65/57, Y 나사 z 453, 펜 서보 z 417.9, 카메라 z 586.5, Pi 상자, UNO 상자)
# ---------------------------------------------------------------------------
P = {
    "UNO1": (-94, -48, 212),            # D5g (승준 SJ-49): x −131.5~−56.4, y −75~−21.7, 기판 z 207
    "UNO2": (-94, -48, 229),            # D5g: UNO 1 위, 기판 z 223.6
    "PI_A": (-82, 43, 222),             # 190 상자 (D5e, 데크 위)
    "PI_B": (-81, 32, 578),             # D5g: 선반 199a 위 x −125.5~−36.9, y 3.4~61, z 568.5~587.5
    "TB":   (-5, -67, 211),             # D5g: 와고 221-415 ×5 받침 193h (단자대 대신)
    "DCIN": (-184, -35, 225),           # D5g 194j (CAP-AI-55): 194b −y로 늘린 판, 비상 정지 머리 비킴
    "M_F":  (55, -13, 215), "ULN_F": (55, -50, 208),
    "LC":   (66.5, 77.5, 236), "HX711": (-44.5, 54, 214),   # D5g 막대 로드셀 4540 +y 끝 / HX711 198x (CAP-AI-55, 제안 자리는 급이 물길과 겹침)
    "SW_F": (39, 13, 255),              # D5g 227f (CAP-AI-55): 151_L 안쪽 면
    "M_X":  (145, -65, 425), "ULN_X": (170, -30, 478), "SW_X": (35, -88, 471),   # 227x 집게 226 밑 (CAP-AI-55)
    "M_Y":  (91, -77, 453), "ULN_Y": (170, 22, 478), "SW_Y": (74, -61, 450),   # 227y 212A −x 면, 빔과 같이 (CAP-AI-55)
    "PEN":  (97, -19, 418),             # 펜 서보: 캐리지 위 (대기 자리 기준)
    "D_IN": (26, -20, 349), "D_CAP": (26, -20, 377), "D_REL": (84, -20, 377),
    "G1": (0, 0, 275), "G4": (0, 0, 570), "G6": (108, 0, 377),   # G6 방생 목 위 (승준 SJ-44, 11/06: x 120 → 108)
    # 문 빔 2개: 문판 평면(입구·격리 x ≈ 26, 방생 x ≈ 84) 앞뒤 각 2 mm
    "G2": (23, 0, 349), "G2b": (29, 0, 349), "G3": (29, 0, 377), "G3b": (23, 0, 377), "G5": (81, 0, 377), "G5b": (87, 0, 377),
    "CAM": (55, 0, 551), "L_TOP": (55, 0, 540),   # CAP-AI-54: CM3 기판·렌즈 끝 (승준 SJ-53 D5g_fix_sj53 CAM tip_z 540, 렌즈 10.5)
    "L_BOT": (55, 15, 333), "L_EXIT": (115, 0, 395),
}
MOVE = {   # 움직이는 끝: 움직임 길이 (mm) → 휨 고리 = 1.5 × 움직임 + 40
    "LC": 36.5,          # 바닥 승강 행정
    "M_Y": 36.0,         # X 이동 (xm 37~73)
    "SW_Y": 36.0,
    "PEN": 36.0 + 58.0,  # X 36 + Y 58 (ym -40~18)
}
STOCK = {"stepper": 240, "servo": 250, "ir": 230}   # 기본 선 길이 mm (28BYJ-48·서보 [가능성 높음], Adafruit 2167 230 [확실])

HARNESS = [
    # (이름, 시작, 끝, 선 수, 굵기 AWG, 최대 전류 A, 기본 선 종류 또는 None)
    ("구동 전원 입력 → 단자대 (+5 V, GND)", "DCIN", "TB", 2, 20, 2.5, None),
    ("단자대 → ULN2003 F (+5 V, GND)", "TB", "ULN_F", 2, 22, I_STEP_PEAK, None),
    ("단자대 → ULN2003 X·Y (+5 V, GND, 둘이 함께)", "TB", "ULN_X", 2, 22, 2 * I_STEP_PEAK, None),
    ("UNO 1 → ULN2003 F (IN1~4)", "UNO1", "ULN_F", 4, 26, 0.002, None),
    ("UNO 1 → ULN2003 X (IN1~4)", "UNO1", "ULN_X", 4, 26, 0.002, None),
    ("UNO 1 → ULN2003 Y (IN1~4)", "UNO1", "ULN_Y", 4, 26, 0.002, None),
    ("ULN2003 F → 바닥 모터 153", "ULN_F", "M_F", 5, 26, I_STEP_PEAK, "stepper"),
    ("ULN2003 X → X 모터 215", "ULN_X", "M_X", 5, 26, I_STEP_PEAK, "stepper"),
    ("ULN2003 Y → Y 모터 209 (X로 움직임)", "ULN_Y", "M_Y", 5, 26, I_STEP_PEAK, "stepper"),
    ("UNO 1 → 펜 서보 205 (신호 + 레일 전원, X·Y로 움직임)", "UNO1", "PEN", 3, 26, 0.65, "servo"),
    ("HX711 → 로드셀 148 (바닥과 함께 움직임)", "HX711", "LC", 4, 28, 0.005, None),
    ("UNO 1 → HX711 (5V, GND, DT, SCK)", "UNO1", "HX711", 4, 26, 0.01, None),
    ("UNO 1 → 원점 F", "UNO1", "SW_F", 2, 28, 0.001, None),
    ("UNO 1 → 원점 X", "UNO1", "SW_X", 2, 28, 0.001, None),
    ("UNO 1 → 원점 Y (빔과 함께 움직임)", "UNO1", "SW_Y", 2, 28, 0.001, None),
    ("UNO 2 → 입구 문 서보 112", "UNO2", "D_IN", 3, 26, 0.75, "servo"),
    ("UNO 2 → 격리 문 서보 170", "UNO2", "D_CAP", 3, 26, 0.75, "servo"),
    ("UNO 2 → 방생 문 서보 176", "UNO2", "D_REL", 3, 26, 0.75, "servo"),
] + [("UNO 2 → 빛 게이트 %s (송신 2선 + 수신 3선)" % g, "UNO2", g, 5, 28, 0.02, "ir")
      for g in ("G1", "G2", "G2b", "G3", "G3b", "G4", "G5", "G5b", "G6")] + [
    ("UNO 2 → MOSFET → 위 조명 182", "UNO2", "L_TOP", 2, 24, 0.20, None),
    ("UNO 2 → MOSFET → 아래 조명", "UNO2", "L_BOT", 2, 24, 0.10, None),
]


def manhattan(a, b):
    return sum(abs(p - q) for p, q in zip(P[a], P[b]))


def route_len(a, b):
    L = 1.2 * manhattan(a, b) + 60       # 프레임·벽을 따라 돎 1.2배 + 양 끝 커넥터 여유 30씩 [추측 — 시제품에서 고침]
    for end in (a, b):
        if end in MOVE:
            L += 1.5 * MOVE[end] + 40
    return L


def harness_table():
    rows = []
    for name, a, b, n, awg, amps, stock in HARNESS:
        L = route_len(a, b)
        ext = max(0.0, L - STOCK[stock]) if stock else L
        rows.append(dict(name=name, frm=a, to=b, wires=n, awg=awg, len_mm=round(L), stock_mm=STOCK.get(stock),
                         extension_mm=round(ext), moving=(a in MOVE or b in MOVE),
                         drop_V=round(drop(awg, L / 1000, amps), 3) if amps > 0.05 else None))
    return rows


def csi_options():
    out = {}
    for k in ("PI_A", "PI_B"):
        L = 1.15 * manhattan("CAM", k) + 40
        out[k] = dict(len_mm=round(L), cable=next((c for c in (200, 300, 500, 1000) if c >= L), ">1000"))
    return out


# ---------------------------------------------------------------------------
# 6) 하루 에너지
# ---------------------------------------------------------------------------
def daily(visits, hours_on=9.0, hold_f=False, cam_always=True, bot_idle=True, per_visit_Wh=None):
    """하루 에너지 (Wh, 부하 쪽). per_visit_Wh = 한 마리 처리 중 '대기보다 더 쓰는' 에너지 (trap_sim 결과)."""
    idle_A = rail_a(pi="idle", cam="run" if cam_always else "standby", hat="idle")
    idle_B = rail_b(stepper_hold=1 if hold_f else 0, bot=1 if bot_idle else 0) * V_B
    night_A = LOADS["pi5"]["halt"]
    night_B = rail_b(emit=0, rx=N_GATE, pen="detached", doors=("detached",) * 3) * V_B + 0.1   # 어댑터 무부하 0.1 W [추측]
    extra = visits * (per_visit_Wh if per_visit_Wh is not None else 0.0)
    load = hours_on * (idle_A + idle_B) + (24 - hours_on) * (night_A + night_B) + extra
    return dict(visits=visits, hours_on=hours_on, hold_f=hold_f, cam_always=cam_always, bot_idle=bot_idle,
                idle_W=round(idle_A + idle_B, 2), load_Wh=round(load, 1), wall_Wh=round(load / ETA_ADAPTER, 1))


# ---------------------------------------------------------------------------
# 6-1) 콘센트 기본 + 배터리 겸용 (서현 11/02: "콘센트로 하는데 배터리도 가능하게")
#   본체 입력은 그대로 2개: Pi = USB-C (27 W 어댑터), 구동 레일 = DC 5.5×2.1 배럴 5 V (3 A 어댑터).
#   배터리 상자 = LiFePO4 12.8 V + 강압 2개(5.1 V 5 A → USB-C, 5 V 3 A → 배럴) + INA226(I2C → Pi). 같은 플러그로 꽂음.
# ---------------------------------------------------------------------------
ETA_BUCK = 0.90            # 강압 효율 [가능성 높음 — 동기 정류형 1~2 A]
BUCK_IQ_W = 0.05           # 강압 2개 무부하 (밤) [추측]
LFP_USABLE = 0.90          # LiFePO4 쓸 수 있는 몫 (BMS 차단 전) [가능성 높음]


def battery_days(load_day_Wh, night_W, hours_on, Ah, V=12.8):
    """load_day_Wh: 하루 부하(낮 운용 + 밤) Wh. 배터리 쪽 에너지 = 부하/강압 효율 + 강압 무부하."""
    need = load_day_Wh / ETA_BUCK + BUCK_IQ_W * 24
    cap = Ah * V * LFP_USABLE
    return round(cap / need, 2), round(need, 1)


def battery_table(per_visit_Wh=0.047, visits=20):
    rows = []
    for mode, cam, bot in (("보통 (카메라 늘 켬, 대기 조명)", True, True), ("절약 (카메라 G1 때만, 대기 조명 끔)", False, False)):
        d = daily(visits, 9.0, False, cam, bot, per_visit_Wh=per_visit_Wh)
        for Ah in (6, 12, 15, 20):
            days, need = battery_days(d["load_Wh"], 0, 9.0, Ah)
            rows.append(dict(mode=mode, Ah=Ah, Wh=round(Ah * 12.8), need_Wh_day=need, days=days))
    return rows


BATTERY = dict(name="보조배터리 20,000 mAh (3.7 V 셀)", Wh_cell=74.0, eff=0.85,
               note="5 V 출력 쪽 쓸 수 있는 양 ≈ 74 × 0.85 = 63 Wh [가능성 높음]. Pi 5는 5 V 3 A 전원이면 USB 전류를 600 mA로 묶고 경고를 띄움 — UNO 2개(0.1 A)는 괜찮음 [가능성 높음]")


# ---------------------------------------------------------------------------
# 7) HOLD F — 바닥 모터를 멈춘 뒤 코일 전류를 계속 흘려야 하나
# ---------------------------------------------------------------------------
def hold_check(F_N=0.5, lead_mm=8.0):
    T_back = F_N * lead_mm / (2 * math.pi)          # 역구동 효율 1로 본 최악 (N·mm, 출력축)
    T_fric = (600 * 0.0980665, 1200 * 0.0980665)    # 28BYJ-48 마찰 토크 600~1200 gf·cm → N·mm [확실 — 제조사 사양]
    T_self = 34.3                                   # 자기 위치 유지 토크 > 34.3 mN·m [확실 — 제조사 사양]
    p_hold = (I_PHASE ** 2 * R_COIL, 2 * I_PHASE ** 2 * R_COIL)   # 1상·2상 코일 발열 W
    return dict(F_N=F_N, T_back_Nmm=round(T_back, 3), T_friction_Nmm=[round(t, 1) for t in T_fric], T_self_Nmm=T_self,
                margin_friction=[round(t / T_back) for t in T_fric], margin_self=round(T_self / T_back),
                coil_heat_W=[round(p, 2) for p in p_hold], rail_W=[round(I_PHASE * V_B, 2), round(2 * I_PHASE * V_B, 2)],
                wasted_Wh_per_9h=[round(I_PHASE * V_B * 9, 1), round(2 * I_PHASE * V_B * 9, 1)])


def main():
    res = dict(
        loads={k: v for k, v in LOADS.items()},
        I_phase_A=round(I_PHASE, 4),
        states_holdF0=state_table(False),
        states_holdF1=state_table(True),
        worst=worst_cases(),
        fuse=FUSE,
        harness=harness_table(),
        csi=csi_options(),
        hold=hold_check(),
        daily=[daily(v, h, hf, ca, bi) for (v, h, hf, ca, bi) in (
            (20, 24, True, True, True), (20, 9, True, True, True), (20, 9, False, True, True),
            (20, 9, False, False, False), (100, 9, False, True, True))],
        battery=BATTERY,
        battery_box=battery_table(),
    )
    with open(os.path.join(OUT, "elec_results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)

    print("상 전류 %.0f mA" % (I_PHASE * 1000))
    print("\n상태별 (HOLD F=0)")
    for r in res["states_holdF0"]:
        print("  %-28s B %.3f A (최대 %.3f)  B %.2f W  A %.2f W" % (r["state"], r["iB_typ"], r["iB_peak"], r["pB_W"], r["pA_W"]))
    print("\n최대:", res["worst"])
    print("\n배선")
    tot = 0
    for r in res["harness"]:
        tot += r["len_mm"] * r["wires"]
        print("  %-48s %4d mm  선%d AWG%d 기본%s 연장%4d  강하%s" % (r["name"], r["len_mm"], r["wires"], r["awg"], r["stock_mm"], r["extension_mm"], r["drop_V"]))
    print("  전선 총 길이 (가닥 합) %.1f m" % (tot / 1000))
    res["harness_total_m"] = round(tot / 1000, 1)
    print("\nCSI:", res["csi"])
    print("\nHOLD:", res["hold"])
    print("\n배터리 상자:")
    for r in res["battery_box"]:
        print("  ", r)
    print("\n하루:")
    for d in res["daily"]:
        print("  ", d)
    with open(os.path.join(OUT, "elec_results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    return res


if __name__ == "__main__":
    main()
