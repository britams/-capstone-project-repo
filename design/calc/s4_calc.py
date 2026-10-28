# -*- coding: utf-8 -*-
"""S4 역학계산 1차 — 말벌 자동 마킹 트랩 D5 4차(안 B) 기준 (CAP-AI-18, AI 계산값)

실행: python3 design/calc/s4_calc.py  →  화면 출력 + design/calc/s4_results.json
수기 풀이(서현)와 대조하는 'AI값'이다. 값의 근거와 상태는 PARAM의 주석과 design/2026-10-28_D6_설계변수표.md.
단위: N, mm, s (토크는 N·mm로 계산하고 mN·m도 함께 표시)
"""
import json, math, os

g = 9.81
# ---------------- 입력값 (근거) ----------------
PARAM = dict(
    # T8 리드스크루 Tr8x8(P2): 바깥지름 8, 피치 2, 4줄 → 리드 8, 유효지름 d_m = d - p/2 = 7, 나사산 반각 15°
    d=8.0, p=2.0, lead=8.0, alpha_deg=15.0,
    mu_screw=0.15,          # 황동 너트–스테인리스 나사, 건조 (0.1~0.2) [가능성 높음]
    # 28BYJ-48 (datasheet): 견인 토크 > 34.3 mN·m (120 Hz), 감속비 1/64, 반 스텝 4096 스텝/회전
    T_motor_Nmm=34.3, rpm=(10.0, 15.0),   # 회전수는 J6 실측 전 [가정] (풀아웃 1000 Hz → 반 스텝 14.6 rpm)
    # SG90 정지 토크 1.8 kgf·cm (4.8 V) [가능성 높음]
    T_servo_Nmm=1.8 * 9.81 * 10, r_horn=11.9,
    # 질량 (FreeCAD 4차 모델 부피 × 밀도: PLA 1.24 상한, 강 7.85, 알루미늄 2.7) / 구매품은 사양
    rho_pla=1.24e-3, rho_steel=7.85e-3, rho_al=2.7e-3,   # g/mm3
    m_marker=13.0,          # 샤피 크리에이티브 불렛 13 g (JetPens 사양) [확실]
    m_sg90=9.0, m_28byj=37.0,   # [가능성 높음]
    m_lm8uu=15.0, m_lm6uu=8.0,  # LM8UU 15 g (판매처 사양) [확실] / LM6UU [가능성 높음]
    # 힘 조건 (R7 '말벌 손상 없음'의 힘 상한은 미정 → 가정)
    F_press=0.5,            # 바닥이 말벌 등을 격자에 붙이는 힘 상한 (하중 센서 정지값) [가정]
    F_ink_min=0.05,         # 펠트 팁이 잉크를 묻히는 최소 힘 [추측 — 마커 시험으로 정함]
    # 마찰
    mu_pla=0.30, mu_bronze=0.15, mu_ball=0.005,           # PLA 부싱–강봉 / 소결 청동 / 직선 볼 부싱 [가능성 높음]
    # 기하 (cad/D5d_module_an1_B.py)
    stroke_floor=36.5, ya=-65.0, yb=57.0, L_block=24.0, L_lm8uu=24.0,
    z_xrod=480.0, z_xscrew=425.0,
    park=(65.0, -40.0), xm_range=(37.0, 73.0), ym_range=(-18.0, 18.0),
    E_steel=200e3, L_xrod=153.0, d_xrod=8.0, L_yrod=104.0, d_yrod=6.0,
)
P = PARAM
# 모델 부피 (cm3, FreeCAD D5d_mark에서 읽음)
VOL = {"140": 9.126, "147": 0.691, "146": 0.353, "148": 0.679, "158": 16.526,
       "206": 46.315, "202": 10.332, "203": 5.604, "204": 0.361,
       "212": 71.487, "207": 5.881, "208": 6.635, "210": 2.38, "211": 6.575}   # D5d 4차 보완 (LM 부싱) 모델


def mass():
    pla, st, al = P["rho_pla"] * 1000, P["rho_steel"] * 1000, P["rho_al"] * 1000   # g/cm3
    m_floor = VOL["140"] * pla + VOL["147"] * st + VOL["146"] * st + VOL["148"] * al + VOL["158"] * pla
    m_z = VOL["202"] * pla + VOL["203"] * pla + P["m_marker"]
    m_y = m_z + VOL["206"] * pla + VOL["204"] * st + P["m_sg90"] + 2 * P["m_lm6uu"]
    m_x = m_y + VOL["212"] * pla + VOL["207"] * st + VOL["208"] * st + P["m_28byj"] + VOL["210"] * al + VOL["211"] * pla + 2 * P["m_lm8uu"]
    return dict(floor=m_floor, z=m_z, y=m_y, x=m_x)


def screw_torque(F, mu, lead=None):
    """사다리꼴 나사 들어올림 토크 (칼라 마찰 무시) — Shigley 식, sec α 포함"""
    l = P["lead"] if lead is None else lead
    dm = P["d"] - P["p"] / 2
    sec = 1 / math.cos(math.radians(P["alpha_deg"]))
    T = F * dm / 2 * (l + math.pi * mu * dm * sec) / (math.pi * dm - mu * l * sec)
    TL = F * dm / 2 * (math.pi * mu * dm * sec - l) / (math.pi * dm + mu * l * sec)   # 내림 토크 (음수 = 저절로 내려감)
    eff = F * l / (2 * math.pi * T)
    selflock = math.pi * mu * dm * sec > l
    return dict(F=F, dm=dm, T_Nmm=T, T_mNm=T, TL_Nmm=TL, eff=eff, selflock=selflock,
                selflock_lhs=math.pi * mu * dm * sec, lead=l)


def M1_floor(m):
    W = m["floor"] / 1000 * g
    F = W + P["F_press"]
    r = screw_torque(F, P["mu_screw"])
    r.update(W_moving=W, SF=P["T_motor_Nmm"] / r["T_Nmm"])
    r["v_mm_s"] = [P["lead"] * n / 60 for n in P["rpm"]]
    r["t_stroke_s"] = [P["stroke_floor"] / v for v in r["v_mm_s"]]
    return r


def M2_axes(m):
    out = {}
    for ax, mm, mu in (("Y (볼 부싱)", m["y"], P["mu_ball"]), ("X (볼 부싱)", m["x"], P["mu_ball"]),
                       ("Y (PLA 부싱, 참고)", m["y"], P["mu_pla"]), ("X (PLA 부싱, 참고)", m["x"], P["mu_pla"])):
        W = mm / 1000 * g
        F_inertia = mm / 1000 * 0.02          # 가속 0.02 m/s2 (0.1 s에 2 mm/s 도달) → N
        F = mu * W + F_inertia
        r = screw_torque(F, P["mu_screw"])
        r.update(W=W, F_fric=mu * W, F_inertia=F_inertia, SF=P["T_motor_Nmm"] / r["T_Nmm"])
        out[ax] = r
    # 이송 거리 (대기 → 흉부 최악)
    dx = max(abs(P["park"][0] - P["xm_range"][0]), abs(P["park"][0] - P["xm_range"][1]))
    dy = max(abs(P["park"][1] - P["ym_range"][0]), abs(P["park"][1] - P["ym_range"][1]))
    out["dx_max"], out["dy_max"] = dx, dy
    return out


def time_budget(v_floor, v_xy, t_feed, retries=0, retract=10.0):
    """한 마리 처리 시간 R6. 마커 복귀·바닥 급이 위치 이동은 급이와 병렬"""
    dx, dy = M2_axes(mass())["dx_max"], M2_axes(mass())["dy_max"]
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


def M3_dab(m):
    W_h = m["z"] / 1000 * g        # 홀더 + 조임 띠 + 마커 자중
    # 말벌이 격자에 붙어 있으려면 F_tip < F_press (넘으면 말벌이 격자에서 밀려 내려감)
    Fs_max = P["F_press"] - W_h     # 스프링이 더 밀 수 있는 최대 (마찰 0일 때)
    return dict(W_h=W_h, F_press=P["F_press"], Fs_max=Fs_max,
                tip_by_weight_ok=W_h < P["F_press"], tip_ink_ok=W_h >= P["F_ink_min"])


def M4_servo(m, F_s=0.0):
    W_h = m["z"] / 1000 * g
    F_lift = W_h + F_s + P["mu_pla"] * 0.2   # 레일 마찰 (측압 0.2 N 가정)
    T = F_lift * P["r_horn"]
    return dict(F_lift=F_lift, T_Nmm=T, SF=P["T_servo_Nmm"] / T)


def M5_jam():
    """한쪽 구동 빔의 끼임 (서랍 끼임 모델): 먼 쪽 블록 B의 마찰이 만든 요 모멘트를 B 부싱 짝힘이 받을 때
       Q_B (L - 2 μ d) = μ W_B d → 2 μ d / L ≥ 1 이면 끼임"""
    d_yaw = P["yb"] - P["ya"]                 # 구동점(A)–먼 봉(B) 거리 118
    d_pitch = P["z_xrod"] - P["z_xscrew"]     # 구동력(나사) 높이와 봉 높이 차 55
    res = {}
    for name, mu in (("PLA 부싱", P["mu_pla"]), ("소결 청동", P["mu_bronze"]), ("볼 부싱 LM8UU", P["mu_ball"])):
        L = P["L_lm8uu"] if "LM8UU" in name else P["L_block"]
        res[name] = dict(mu=mu, L=L, yaw_ratio=2 * mu * d_yaw / L, pitch_ratio=2 * mu * d_pitch / L,
                         mu_crit_yaw=L / (2 * d_yaw), mu_crit_pitch=L / (2 * d_pitch))
    return dict(d_yaw=d_yaw, d_pitch=d_pitch, cases=res)


def M6_rod_deflection(m):
    out = {}
    for name, F_tot, L, dd in (("X 고정 봉 Ø8 (빔 전체 하중)", m["x"] / 1000 * g, P["L_xrod"], P["d_xrod"]),
                               ("Y 봉 Ø6 (캐리지 하중)", m["y"] / 1000 * g, P["L_yrod"], P["d_yrod"])):
        F = F_tot / 2                          # 봉 2개가 나눠 받음
        I = math.pi * dd ** 4 / 64
        delta = F * L ** 3 / (48 * P["E_steel"] * I)   # 단순지지 중앙 집중하중 (보수적)
        M = F * L / 4
        sigma = M / (math.pi * dd ** 3 / 32)
        out[name] = dict(F=F, I=I, L=L, delta=delta, M=M, sigma=sigma)
    return out


if __name__ == "__main__":
    m = mass()
    R = dict(mass_g=m, M1=M1_floor(m), M2=M2_axes(m), M3=M3_dab(m), M4=M4_servo(m), M5=M5_jam(), M6=M6_rod_deflection(m))
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
    # 급이 시간 상한 (R6 180 s 안)
    for label, vf, vxy in (("28BYJ+T8 15rpm", 2.0, 2.0), ("28BYJ+T8 10rpm", 4 / 3, 4 / 3), ("XY 벨트", 2.0, 10.0)):
        for rt in (0, 1):
            _, base = time_budget(vf, vxy, 0, rt)
            R.setdefault("t_feed_max", {})["%s, 재시도 %d" % (label, rt)] = round(180 - base, 1)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s4_results.json")
    json.dump(R, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
    print(json.dumps(R, ensure_ascii=False, indent=1, default=lambda o: round(o, 4) if isinstance(o, float) else str(o)))
