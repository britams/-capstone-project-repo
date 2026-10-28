# -*- coding: utf-8 -*-
"""S4 역학계산 1차 r2 — 말벌 자동 마킹 트랩 D5 4차(안 B) 기준 (r1 CAP-AI-18 → r2 CAP-AI-19, AI 계산값)

실행: python3 design/calc/s4_calc.py  →  화면 출력 + design/calc/s4_results.json
수기 풀이(서현)와 대조하는 'AI값'이다. 값의 근거와 상태는 PARAM의 주석과 design/2026-10-28_D6_설계변수표.md.
공용 식(나사 토크, 단순보 집중하중, 끼임 연립)은 s4_textbook_check.py가 교재 정답·해설집과 먼저 대조한다.
단위: N, mm, s (토크 N·mm = mN·m)

r2에서 바뀐 것 (교재·해설집 대조 뒤 재점검, CAP-AI-19)
- 질량·무게중심: FreeCAD D5d 모델에서 부품별 부피와 무게중심을 읽어 씀 (CAD_MARK / CAD_REST 표)
- M1: 모터 토크 34.3 mN·m는 120 Hz(약 1.8 rpm) 값 → 10~15 rpm에서의 토크는 모름을 결과에 표시
- M2: Y 캐리지 편심(홀더·마커가 Y 봉 면에서 -x로 약 25 mm) → 두 Y 봉(z 445·475)의 수평 짝힘을 마찰에 넣음
- M4: 홀더 레일 마찰을 홀더 편심 모멘트로 계산 (r1은 측압 0.2 N 가정)
- M5: 요(yaw)만 → 요 두 경계(B 부싱 혼자 / A·B 나눔) + 피치 + 둘을 합친 연립. 볼 부싱 유효 길이 감도
- M6: 봉 하중을 무게중심으로 나눔(봉 A가 약 70 %) + 최악(한 봉이 전부). Y 봉에 수평 짝힘 더함
"""
import json, math, os

g = 9.81
# ---------------- 입력값 (근거) ----------------
PARAM = dict(
    # T8 리드스크루 Tr8x8(P2): 바깥지름 8, 피치 2, 4줄 → 리드 8, 유효지름 d_m = d - p/2 = 7, 나사산 반각 15°
    d=8.0, p=2.0, lead=8.0, alpha_deg=15.0,
    mu_screw=0.15,          # 황동 너트–스테인리스 나사, 건조 (0.1~0.2) [가능성 높음]
    # 28BYJ-48 (datasheet): 견인 토크 > 34.3 mN·m (120 Hz), 감속비 1/64, 반 스텝 4096 스텝/회전, 공회전 최대 > 1000 Hz
    T_motor_Nmm=34.3, f_T_motor=120.0, f_idle_max=1000.0, steps_rev=4096,
    rpm=(10.0, 15.0),       # 회전수는 J6 실측 전 [가정] (공회전 최대 1000 Hz → 반 스텝 14.6 rpm)
    # SG90 정지 토크 1.8 kgf·cm (4.8 V) [가능성 높음]
    T_servo_Nmm=1.8 * 9.81 * 10, r_horn=11.9,   # 혼 길이 11.9 = 접촉 팔의 상한 (탭 접촉점은 혼 끝보다 안쪽)
    # 밀도 g/mm3 (PLA는 꽉 찬 값이라 상한) / 구매품은 사양 질량
    rho_pla=1.24e-3, rho_steel=7.85e-3, rho_al=2.7e-3,
    m_marker=13.0,          # 샤피 크리에이티브 불렛 13 g (JetPens 사양) [확실]
    m_sg90=9.0, m_28byj=37.0,   # [가능성 높음]
    m_lm8uu=15.0, m_lm6uu=8.0,  # LM8UU 15 g (판매처 사양) [확실] / LM6UU [가능성 높음]
    # 힘 조건 (R7 '말벌 손상 없음'의 힘 상한은 미정 → 가정)
    F_press=0.5,            # 바닥이 말벌 등을 격자에 붙이는 힘 상한 (하중 센서 정지값) [가정]
    F_ink_min=0.05,         # 펠트 팁이 잉크를 묻히는 최소 힘 [추측 — 마커 시험으로 정함]
    # 마찰
    mu_pla=0.30, mu_bronze=0.15, mu_ball=0.005,   # PLA 부싱–강봉 / 소결 청동 / 직선 볼 부싱 [가능성 높음] (볼 부싱 카탈로그 0.002~0.003보다 크게 잡음)
    # 기하 (cad/D5d_module_an1_B.py)
    stroke_floor=36.5, ya=-65.0, yb=57.0, L_block=24.0, L_lm8uu=24.0, L_lm8uu_eff=17.0,   # 유효 길이 17 = 볼 순환부 [추측]
    z_xrod=480.0, z_xscrew=425.0, yrod_z=(445.0, 475.0), h_rail=30.0,   # h_rail: 홀더가 캐리지 면을 무는 높이 (hz1 - hz0)
    park=(65.0, -40.0), xm_range=(37.0, 73.0), ym_range=(-18.0, 18.0),
    E_steel=200e3, L_xrod=153.0, d_xrod=8.0, L_yrod=104.0, d_yrod=6.0,   # L_xrod: 봉 전체 길이(받침 중심 간 141보다 김 → 보수적)
    a_start=0.02,           # 0.1 s에 2 mm/s 도달 [가정], m/s2
)
P = PARAM

# FreeCAD D5d_module_an1_B 에서 읽은 부품별 부피(cm3)와 무게중심 x, y, z (mm) — 2026-10-28, CAP-AI-19
#   mark: 흉부 좌표 예 xm 59.4, ym 0 (빔 중심 xb 85.79) / rest: 대기 xm 65, ym -40 (xb 91.39)
CAD_MARK = {"140": (9.126, 55.0, 0.0, 374.5), "146": (0.3534, 55.0, 0.0, 321.5), "147": (0.6912, 55.0, 0.0, 344.0),
            "148": (0.6786, 55.0, 0.0, 313.5), "158": (16.526, 55.0, 0.36, 304.5),
            "201": (27.6363, 59.4, 0.0, 464.81), "202": (10.3323, 69.62, 0.76, 423.91), "203": (5.604, 52.72, 0.0, 424.0),
            "204": (0.3613, 72.65, 0.0, 450.5), "205": (6.3638, 88.35, 21.15, 411.45), "206": (46.3153, 85.62, 0.0, 442.59),
            "207": (5.8811, 85.79, -4.0, 460.0), "208": (6.635, 85.79, -18.0, 460.0), "209": (12.0135, 85.79, -111.04, 467.79),
            "210": (2.3798, 85.79, -84.64, 460.0), "211": (6.5752, 85.79, -90.92, 468.1), "212": (71.4865, 85.79, -2.2, 443.87),
            "221": (3.2233, 85.79, 0.0, 460.0), "222": (6.0696, 85.79, -4.0, 480.0)}
CAD_REST = {"140": (9.126, 55.0, 0.0, 338.0), "146": (0.3534, 55.0, 0.0, 285.0), "147": (0.6912, 55.0, 0.0, 307.5),
            "148": (0.6786, 55.0, 0.0, 277.0), "158": (16.526, 55.0, 0.36, 268.0),
            "201": (27.6363, 65.0, -40.0, 464.25), "202": (10.3323, 75.22, -39.24, 423.36), "203": (5.604, 58.32, -40.0, 423.44),
            "204": (0.37, 78.25, -40.0, 450.22), "205": (6.3638, 93.95, -18.85, 411.45), "206": (46.3153, 91.22, -40.0, 442.59),
            "207": (5.8811, 91.39, -4.0, 460.0), "208": (6.635, 91.39, -18.0, 460.0), "209": (12.0135, 91.39, -111.04, 467.79),
            "210": (2.3798, 91.39, -84.64, 460.0), "211": (6.5752, 91.39, -90.92, 468.1), "212": (71.4865, 91.39, -2.2, 443.87),
            "221": (3.2233, 91.39, -40.0, 460.0), "222": (6.0696, 91.39, -4.0, 480.0)}
XB = {"mark": 85.79, "rest": 91.39}          # 빔·캐리지 중심 x = 볼 부싱 중심 = Y 봉 x
MAT = {"140": "pla", "146": "steel", "147": "steel", "148": "al", "158": "pla", "202": "pla", "203": "pla", "204": "steel",
       "206": "pla", "207": "steel", "208": "steel", "210": "al", "211": "pla", "212": "pla"}
SPEC = {"201": P["m_marker"], "205": P["m_sg90"], "209": P["m_28byj"], "221": 2 * P["m_lm6uu"], "222": 2 * P["m_lm8uu"]}
GROUP = {"floor": ["140", "146", "147", "148", "158"],
         "z": ["201", "202", "203"]}                                   # 홀더 + 조임 띠 + 마커
GROUP["y"] = GROUP["z"] + ["204", "205", "206", "221"]                 # Y 캐리지 묶음
GROUP["x"] = GROUP["y"] + ["207", "208", "209", "210", "211", "212", "222"]   # X 빔 묶음 (X 나사·X 모터는 프레임 고정)


def parts(state="mark"):
    cad = CAD_MARK if state == "mark" else CAD_REST
    out = {}
    for k, (vol, x, y, z) in cad.items():
        m = SPEC[k] if k in SPEC else vol * P["rho_" + MAT[k]] * 1000   # g
        out[k] = (m, x, y, z)
    return out


def group(name, state="mark"):
    pts = parts(state)
    ks = GROUP[name]
    m = sum(pts[k][0] for k in ks)
    cg = tuple(sum(pts[k][0] * pts[k][i] for k in ks) / m for i in (1, 2, 3))
    return m, cg


def mass(state="mark"):
    return {k: group(k, state)[0] for k in ("floor", "z", "y", "x")}


def screw_torque(F, mu, lead=None, dm=None, alpha_deg=None):
    """나사 들어올림·내림 토크 (칼라 마찰 무시) — Shigley 식, sec α 포함 (α = 0이면 사각나사 = Riley 9-3.2 식)"""
    l = P["lead"] if lead is None else lead
    dm = P["d"] - P["p"] / 2 if dm is None else dm
    a = P["alpha_deg"] if alpha_deg is None else alpha_deg
    sec = 1 / math.cos(math.radians(a))
    T = F * dm / 2 * (l + math.pi * mu * dm * sec) / (math.pi * dm - mu * l * sec)
    TL = F * dm / 2 * (math.pi * mu * dm * sec - l) / (math.pi * dm + mu * l * sec)   # 내림 토크 (음수 = 저절로 내려감)
    eff = F * l / (2 * math.pi * T)
    selflock = math.pi * mu * dm * sec > l
    lead_angle = math.degrees(math.atan(l / (math.pi * dm)))
    fric_angle = math.degrees(math.atan(mu * sec))
    return dict(F=F, dm=dm, T_Nmm=T, TL_Nmm=TL, eff=eff, selflock=selflock,
                selflock_lhs=math.pi * mu * dm * sec, lead=l, lead_angle_deg=lead_angle, fric_angle_deg=fric_angle)


def M1_floor(m):
    W = m["floor"] / 1000 * g
    F = W + P["F_press"]
    r = screw_torque(F, P["mu_screw"])
    r.update(W_moving=W, SF=P["T_motor_Nmm"] / r["T_Nmm"])
    r["v_mm_s"] = [P["lead"] * n / 60 for n in P["rpm"]]
    r["t_stroke_s"] = [P["stroke_floor"] / v for v in r["v_mm_s"]]
    r["pps_halfstep"] = [n / 60 * P["steps_rev"] for n in P["rpm"]]
    r["rpm_at_T_motor"] = P["f_T_motor"] / P["steps_rev"] * 60
    r["note"] = "안전율은 120 Hz(약 1.8 rpm) 토크 기준 — 10~15 rpm(683~1024 Hz)의 토크는 사양서에 없음 → J6에서 부하 걸고 확인"
    return r


def beam_point_load(Pf, L, E, I, a=None):
    """단순보 집중하중 (Gere 예제 9-3 식). a = 왼쪽 받침에서 하중까지 (없으면 가운데)"""
    a = L / 2 if a is None else a
    b = L - a
    if abs(a - b) < 1e-9:
        dmax, x1 = Pf * L ** 3 / (48 * E * I), L / 2
    else:
        bb = min(a, b)                              # 식은 a ≥ b 기준
        dmax = Pf * bb * (L ** 2 - bb ** 2) ** 1.5 / (9 * math.sqrt(3) * L * E * I)
        x1 = math.sqrt((L ** 2 - bb ** 2) / 3)
    thetaA = Pf * a * b * (L + b) / (6 * L * E * I)
    return dict(delta_max=dmax, x_at_max=x1, theta_A=thetaA, M_max=Pf * a * b / L)


def jam_solve(mu, W, W_B, m_kg, acc, L, d, h, M_w=0.0, e_y=0.0, k=1.0, s=None):
    """한쪽 구동 빔의 추력과 부싱 짝힘 (요 + 피치 연립, 마찰 크기는 더해서 보수적으로)
       (1) P = μ(W + 2Qp + 2Qy) + m a        (봉 방향 힘 평형)
       (2) Qp·L = h·P + |M_w|                 (피치: 나사가 봉보다 h 아래 + 무게 편심 모멘트)
       (3) Qy·L = d·μ(W_B + 2k·Qy + 2s·Qp) + m a·e_y   (요: 구동점 A 기준, 먼 봉 B의 마찰 + 관성력)
       k = 요 짝힘 접점 중 B에 있는 비율 (1: B 부싱 혼자 = 보수적, 0.5: A·B가 나눔 = Riley 9-43 서랍처럼 대각 접촉)
       s = 피치 짝힘 접점 중 B에 있는 비율 (기본 k와 같음)
       반환 jam=True 이면 어떤 추력으로도 안 움직임 (행렬식 ≤ 0). 한계 μ_c = L / (2(k d + h))  (s = k일 때)"""
    s = k if s is None else s
    ma = m_kg * acc
    det = (L - 2 * mu * h) * (L - 2 * k * d * mu) - 4 * s * d * mu ** 2 * h
    mu_c = L / (2 * (k * d + h)) if abs(s - k) < 1e-12 else None
    if det <= 0 or L - 2 * mu * h <= 0 or L - 2 * k * d * mu <= 0:
        return dict(jam=True, det=det, mu_crit=mu_c)
    # 3x3 연립을 크라메르 공식으로 풂
    A =[[1, -2 * mu, -2 * mu], [-h, L, 0], [0, -2 * s * d * mu, L - 2 * k * d * mu]]
    bvec = [mu * W + ma, abs(M_w), d * mu * W_B + ma * e_y]

    def det3(M):
        return (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
    D = det3(A)
    sol = []
    for j in range(3):
        Aj = [row[:] for row in A]
        for i in range(3):
            Aj[i][j] = bvec[i]
        sol.append(det3(Aj) / D)
    Pt, Qp, Qy = sol
    return dict(jam=False, det=det, mu_crit=mu_c, P=Pt, Qp=Qp, Qy=Qy)


def eccentric(state="mark"):
    """Y 캐리지 묶음의 x 편심 (봉·부싱 중심 xb 기준) → Y 봉 수평 짝힘, X 부싱 피치 모멘트 (같은 크기)"""
    my, cg = group("y", state)
    e = cg[0] - XB[state]
    M = my / 1000 * g * abs(e)                       # N·mm
    s_y = P["yrod_z"][1] - P["yrod_z"][0]
    return dict(m_y=my, cg_x_minus_xb=e, M=M, H=M / s_y, s_y=s_y)


def M2_axes(m, state="mark"):
    out = {}
    ec = eccentric(state)
    # Y: 나사가 두 봉 가운데(z 460, 같은 x) → 끼임 팔 0. 봉 반력 = 무게 + 수평 짝힘 2H (마찰 크기 합, 보수적)
    for name, mu in (("Y (볼 부싱)", P["mu_ball"]), ("Y (PLA 부싱, 참고)", P["mu_pla"])):
        W = m["y"] / 1000 * g
        N_sum = W + 2 * ec["H"]
        Fi = m["y"] / 1000 * P["a_start"]
        F = mu * N_sum + Fi
        r = screw_torque(F, P["mu_screw"])
        r.update(W=W, H=ec["H"], N_sum=N_sum, F_fric=mu * N_sum, F_inertia=Fi, SF=P["T_motor_Nmm"] / r["T_Nmm"])
        out[name] = r
    # X: 끼임 연립(M5와 같은 식, 보수적 k = 1)으로 추력
    mx, cgx = group("x", state)
    W = mx / 1000 * g
    W_B = W * (cgx[1] - P["ya"]) / (P["yb"] - P["ya"])
    for name, mu in (("X (볼 부싱)", P["mu_ball"]), ("X (PLA 부싱, 참고)", P["mu_pla"])):
        js = jam_solve(mu, W, W_B, mx / 1000, P["a_start"], P["L_lm8uu"], P["yb"] - P["ya"], P["z_xrod"] - P["z_xscrew"],
                       M_w=ec["M"], e_y=cgx[1] - P["ya"], k=1.0)
        if js["jam"]:
            out[name] = dict(jam=True, note="끼임 — 어떤 추력으로도 안 움직임 (M5)")
            continue
        r = screw_torque(js["P"], P["mu_screw"])
        r.update(W=W, W_B=W_B, Qp=js["Qp"], Qy=js["Qy"], SF=P["T_motor_Nmm"] / r["T_Nmm"], jam=False)
        out[name] = r
    dx = max(abs(P["park"][0] - P["xm_range"][0]), abs(P["park"][0] - P["xm_range"][1]))
    dy = max(abs(P["park"][1] - P["ym_range"][0]), abs(P["park"][1] - P["ym_range"][1]))
    out["dx_max"], out["dy_max"] = dx, dy
    out["eccentric"] = ec
    return out


def time_budget(v_floor, v_xy, t_feed, retries=0, retract=10.0):
    """한 마리 처리 시간 R6. 마커 복귀·바닥 급이 위치 이동은 급이와 병렬"""
    dx = max(abs(P["park"][0] - P["xm_range"][0]), abs(P["park"][0] - P["xm_range"][1]))
    dy = max(abs(P["park"][1] - P["ym_range"][0]), abs(P["park"][1] - P["ym_range"][1]))
    steps = [
        ("진입 감지·입구 문 닫힘", 1.0),
        ("판별 (촬영·추론)", 2.0),
        ("바닥 상승 36.5 mm", P["stroke_floor"] / v_floor),
        ("자세·흉부 좌표 확인", 1.0),
        ("재시도 (바닥 %.0f mm 내렸다 올림 + 재확인)" % retract, retries * (2 * retract / v_floor + 1.0)),
        ("마커 이동 (X·Y 동시, 최악)", max(dx, dy) / v_xy),
        ("찍기 2회 + 펜 들기·놓기", 2 * 0.5 + 2 * 0.3),
        ("점 확인", 1.0),
        ("급이 (= 잉크 건조) — 마커 복귀와 병렬", t_feed),
        ("방생 문 열림·말벌 나감 (가정)", 10.0),
    ]
    return steps, sum(t for _, t in steps)


def holder_rail(state="mark"):
    """홀더(201~203)가 캐리지 면(xhb = xb - 10)에 매달린 편심 → 레일 법선 짝힘"""
    mz, cg = group("z", state)
    W_h = mz / 1000 * g
    x_face = XB[state] - 10.0
    e_h = x_face - cg[0]
    N_rail = 2 * W_h * e_h / P["h_rail"]
    return dict(W_h=W_h, cg_x=cg[0], x_face=x_face, e_h=e_h, N_rail=N_rail, f_max=P["mu_pla"] * N_rail)


def M3_dab(m):
    hr = holder_rail("mark")
    W_h = hr["W_h"]
    # 말벌이 격자에 붙어 있으려면 N_tip ≤ F_press (넘으면 말벌이 격자에서 밀려 내려감)
    # 홀더가 내려와 멈춘 뒤 레일 마찰 f는 위쪽(0 ~ f_max) → N_tip = W_h + F_s - f
    Fs_max = P["F_press"] - W_h                 # f = 0 (가장 큰 N_tip) 기준
    return dict(W_h=W_h, F_press=P["F_press"], Fs_max=Fs_max, f_max=hr["f_max"],
                N_tip_range_Fs0=(W_h - hr["f_max"], W_h),
                tip_by_weight_ok=W_h < P["F_press"], tip_ink_ok=W_h - hr["f_max"] >= P["F_ink_min"])


def M4_servo(m, F_s=0.0):
    hr = holder_rail("mark")
    F_lift = hr["W_h"] + F_s + hr["f_max"]      # 들어 올릴 때 마찰은 아래로
    T = F_lift * P["r_horn"]                    # 혼 길이 = 팔의 상한 → T 상한
    return dict(F_lift=F_lift, f_rail=hr["f_max"], N_rail=hr["N_rail"], e_h=hr["e_h"], T_Nmm=T, SF=P["T_servo_Nmm"] / T)


def M5_jam(state="mark"):
    """한쪽 구동 X 빔의 끼임. 한계 μ_c = L / (2 (k d + h)) — 요만: h = 0, 피치만: d = 0"""
    d = P["yb"] - P["ya"]                       # 구동점(봉 A 선)–먼 봉 B 거리 122
    h = P["z_xrod"] - P["z_xscrew"]             # 나사 추력이 봉보다 아래 55
    res = {}
    for name, mu in (("PLA 부싱", P["mu_pla"]), ("소결 청동", P["mu_bronze"]), ("볼 부싱 LM8UU", P["mu_ball"]),
                     ("볼 부싱 LM8UU (유효 길이 17, 감도)", P["mu_ball"])):
        L = P["L_lm8uu_eff"] if "유효" in name else (P["L_lm8uu"] if "LM8UU" in name else P["L_block"])
        c = dict(mu=mu, L=L,
                 yaw_B=2 * mu * d / L, yaw_AB=mu * d / L, pitch=2 * mu * h / L,
                 comb_B=2 * mu * (d + h) / L, comb_AB=2 * mu * (0.5 * d + h) / L,
                 mu_c_yaw_B=L / (2 * d), mu_c_yaw_AB=L / d, mu_c_pitch=L / (2 * h),
                 mu_c_comb_B=L / (2 * (d + h)), mu_c_comb_AB=L / (2 * (0.5 * d + h)))
        c["verdict"] = ("끼임" if c["comb_AB"] >= 1 else ("경계 (접촉 배분에 따라 끼임)" if c["comb_B"] >= 1 else "안전"))
        c["SF_mu"] = c["mu_c_comb_B"] / mu
        res[name] = c
    return dict(d=d, h=h, cases=res)


def M6_rods(state):
    out = {}
    mx, cgx = group("x", state)
    Wx = mx / 1000 * g
    R_A = Wx * (P["yb"] - cgx[1]) / (P["yb"] - P["ya"])
    R_B = Wx - R_A
    I8 = math.pi * P["d_xrod"] ** 4 / 64
    S8 = math.pi * P["d_xrod"] ** 3 / 32
    for name, F in (("X 봉 A (무게중심 배분)", R_A), ("X 봉 B (무게중심 배분)", R_B), ("X 봉 한 개가 전부 (최악)", Wx)):
        b = beam_point_load(F, P["L_xrod"], P["E_steel"], I8)
        out[name] = dict(F=F, delta=b["delta_max"], M=b["M_max"], sigma=b["M_max"] / S8)
    ec = eccentric(state)
    Wy = ec["m_y"] / 1000 * g
    I6 = math.pi * P["d_yrod"] ** 4 / 64
    S6 = math.pi * P["d_yrod"] ** 3 / 32
    for name, Fv in (("Y 봉 (세로 하중 반씩 + 수평 짝힘)", Wy / 2), ("Y 봉 한 개가 세로 하중 전부 + 수평 짝힘 (최악)", Wy)):
        F = math.hypot(Fv, ec["H"])
        b = beam_point_load(F, P["L_yrod"], P["E_steel"], I6)
        out[name] = dict(F=F, F_vert=Fv, H=ec["H"], delta=b["delta_max"], M=b["M_max"], sigma=b["M_max"] / S6)
    out["_cg_x_beam"] = dict(m_g=mx, cg=cgx, R_A_share=R_A / Wx)
    return out


if __name__ == "__main__":
    m = mass()
    R = dict(mass_g=m, cg={k: group(k)[1] for k in ("floor", "z", "y", "x")},
             M1=M1_floor(m), M2=M2_axes(m), M3=M3_dab(m), M4=M4_servo(m), M4_spring_max=None,
             M5=M5_jam(), M6={"mark": M6_rods("mark"), "rest": M6_rods("rest")})
    R["M4_spring_max"] = M4_servo(m, F_s=R["M3"]["Fs_max"])
    tb = {}
    for label, vf, vxy in (("28BYJ-48+T8 (10 rpm)", 8 * 10 / 60, 8 * 10 / 60), ("28BYJ-48+T8 (15 rpm)", 8 * 15 / 60, 8 * 15 / 60),
                           ("바닥 28BYJ-48 + XY 벨트(20T, 15 rpm)", 8 * 15 / 60, 40 * 15 / 60)):
        for tf in (60, 90, 120, 180):
            for rt in (0, 1):
                steps, tot = time_budget(vf, vxy, tf, rt)
                tb["%s | 급이 %d s | 재시도 %d" % (label, tf, rt)] = round(tot, 1)
    R["R6_time"] = tb
    steps, tot = time_budget(2.0, 2.0, 90, 0)
    R["R6_steps_example"] = [(s, round(t, 1)) for s, t in steps]
    for label, vf, vxy in (("28BYJ+T8 15rpm", 2.0, 2.0), ("28BYJ+T8 10rpm", 4 / 3, 4 / 3), ("XY 벨트", 2.0, 10.0)):
        for rt in (0, 1):
            _, base = time_budget(vf, vxy, 0, rt)
            R.setdefault("t_feed_max", {})["%s, 재시도 %d" % (label, rt)] = round(180 - base, 1)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s4_results.json")
    json.dump(R, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
    print(json.dumps(R, ensure_ascii=False, indent=1, default=lambda o: round(o, 4) if isinstance(o, float) else str(o)))
