# -*- coding: utf-8 -*-
"""스프링 146 역학계산 2차 (서현, 2026-11-06, CAP-AI-25) — 교재 유제 T8~T12의 방법을 우리 바닥에 적용

  A 정역학   (T8 Riley 9-6 방법)  밀대 안내 구멍의 두 접촉점 마찰 → 말벌이 가운데에서 벗어나면 로드셀이 얼마나 틀리나
  B 고체역학 (T9 Gere 2-1 방법)   힘 경로의 직렬 강성 (로드셀·스프링·밀대·바닥판·말벌) → k_eff, 로드셀 읽음 = 스프링 힘
  C 동역학   (T10 Meriam 8/1 방법) 닿을 때·멈출 때 진동 진폭 + 시간 적분으로 넘침 확인 (1차 계산 C1과 독립)
  D 기계요소 (T11·T12 Shigley 10-1·10-2 방법) 그림 10-3 흐름으로 선 지름별 표 → 권장 범위(4 ≤ C ≤ 12, 3 ≤ Na ≤ 15, ξ ≥ 0.15,
             ns ≥ 1.2) 안에서 고름 + 서지 주파수 (식 10-25) + 피로 (Zimmerli, Goodman)
확실도 표기는 '계산'과 '입력'을 나눈다: 계산은 교재 대조(52/52, ≤ 2 %)와 두 방법 교차로 확인, 입력 중 시험 전 값은 [추측]/[가능성 높음].
실행: python3 design/calc/spring146_calc2.py → spring146_calc2_results.json
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
g = 9.81
IN = dict(
    F_p=0.5, F_safe=1.0, v=1.96e-3, h_min=6.5e-3, h_max=8.5e-3, margin=1.0e-3,
    k_c=(300.0, 3000.0),                         # [추측] 말벌 + 접촉 강성, R7 전
    m_floor=(9.0883 + 0.7677) * 1e-3,            # [가능성 높음] CAD
    # A 정역학
    e_max=20e-3,                                 # [확실 — 모델] 바닥 39 × 39의 가운데에서 말벌 중심까지 최대 (모서리 몸통 중심)
    L_guide_now=5e-3, clear_now=1.0e-3,          # [확실 — D5e] 바닥판 121 구멍 Ø5 × 5 mm, 밀대 Ø4
    mu_pla=(0.2, 0.5),                           # [가능성 높음] PLA-PLA 마찰계수 범위
    L_lm4=12e-3, mu_lm=(0.002, 0.005),           # [가능성 높음] LM4UU 길이 12 mm, 볼 부싱 마찰계수 (제조사 일반값)
    floor_W=39e-3, floor_t=6e-3, wall_gap=0.5e-3,  # [확실 — D5e]
    # B 고체역학
    E_pla=3.5e9,                                 # [가능성 높음] PLA 탄성계수
    rod_d=4e-3, rod_L=46.5e-3,                   # [확실 — D5e] 칼라 위 ~ 바닥 윗면
    lc_defl_FS=0.15e-3, lc_FS=9.81,              # [추측] 1 kg 버튼 로드셀 정격 처짐 0.1~0.2 mm
    # C 동역학
    f_hx=(10.0, 80.0), t_stop=0.005, step_rate=1000.0, step_um=1.96,
    # D 기계요소 (Shigley Table 10-4, 10-5, 10-6, 10-1, 10-2)
    A=2211.0, mexp=0.145, gamma=76.5e3,          # MPa·mm^m, -, N/m³ (강 7.8 g/cm³)
    k_target=100.0, k_band=(94.0, 118.0),        # 1차 계산 범위 (C2·C3)
    rods=(1.5e-3, 2.0e-3, 3.0e-3), allows=(0.4e-3, 0.6e-3, 0.8e-3, 1.0e-3), OD_max=9.0e-3, nf_min=1.2,
    xi=0.15, ns_min=1.2,
    cycles_per_day=100 * 2, days=120,            # [추측] 하루 100마리 × 누르기 2번, 한 철 120일
)


def G_music(d_mm):
    return 82.7e9 if d_mm < 0.8 else 81.7e9 if d_mm <= 1.6 else 81.0e9 if d_mm <= 3 else 80.0e9


def KB(C):
    return (4 * C + 2) / (4 * C - 3)


# ---------------------------------------------------------------- A 정역학
def statics():
    """밀대가 안내 구멍에서 두 점(위·아래 끝)에 닿음. 말벌 힘 N_h가 e만큼 벗어나면
    ΣM: N_h·e = R·L  → 두 점 마찰 2μR = 2μ N_h e / L (올라가는 중, 아래로)
    ΣF_z: F_s = N_h + W + 2μ N_h e/L → 로드셀이 F_s − W = F_p에서 멈추면 N_h = F_p / (1 + 2μe/L)"""
    out = {}
    # 바닥판이 벽에 걸려 모멘트를 받을 수 있나: 기울어진 판의 폭 최대 √(W² + t²) < 벽 사이 40 mm면 못 받음
    span = math.hypot(IN["floor_W"], IN["floor_t"])
    out["floor_can_wedge_on_walls"] = span >= IN["floor_W"] + 2 * IN["wall_gap"]
    out["floor_tilted_span_mm"] = round(span * 1e3, 2)
    out["rod_tilt_free_deg"] = round(math.degrees(math.atan(IN["clear_now"] / IN["L_guide_now"])), 1)
    rows = []
    for name, L, mus in (("지금 (Ø5 구멍 5 mm, PLA)", IN["L_guide_now"], IN["mu_pla"]), ("LM4UU 12 mm (제안)", IN["L_lm4"], IN["mu_lm"])):
        for mu in mus:
            for e in (0.0, 5e-3, 10e-3, IN["e_max"]):
                r = 2 * mu * e / L
                rows.append(dict(guide=name, mu=mu, e_mm=e * 1e3, friction_ratio=round(r, 3),
                                 N_h_at_stop_N=round(IN["F_p"] / (1 + r), 3), pct_of_Fp=round(100 / (1 + r), 1)))
    out["rows"] = rows
    # 0.8 F_p 이상 (말벌을 붙잡는 힘) 이 되려면 2μe/L ≤ 0.25 → L ≥ 8μe
    out["L_needed_for_0.8Fp_mm"] = {str(mu): round(8 * mu * IN["e_max"] * 1e3, 1) for mu in IN["mu_pla"] + IN["mu_lm"]}
    return out


# ---------------------------------------------------------------- B 고체역학
def solids(k_s):
    k_lc = IN["lc_FS"] / IN["lc_defl_FS"]
    A = math.pi * IN["rod_d"] ** 2 / 4
    k_rod = IN["E_pla"] * A / IN["rod_L"]
    b = 2 * IN["e_max"]                                  # [추측] 판의 유효 폭 (가운데 지지, 점하중) — 보수적으로 2e
    I = b * IN["floor_t"] ** 3 / 12
    k_plate = 3 * IN["E_pla"] * I / IN["e_max"] ** 3     # 외팔보 끝 하중
    parts = dict(load_cell=k_lc, spring=k_s, rod=k_rod, floor_plate=k_plate)
    out = dict(k_parts=parts)
    for kc in IN["k_c"]:
        flex = sum(1 / v for v in parts.values()) + 1 / kc
        ideal = 1 / (1 / k_s + 1 / kc)
        out["k_total_kc%d" % kc] = round(1 / flex, 2)
        out["k_spring_only_kc%d" % kc] = round(ideal, 2)
        out["err_pct_kc%d" % kc] = round(100 * (ideal - 1 / flex) / ideal, 3)
    # 직렬이면 모든 요소에 같은 힘 → 로드셀 읽음 = 스프링 힘 (Gere 2-1의 F_CD처럼 상대 변위 × k)
    return out


# ---------------------------------------------------------------- C 동역학
def dynamics(k_s, surge_hz):
    m, v = IN["m_floor"], IN["v"]
    out = {}
    wn = math.sqrt(k_s / m)
    out["floor_fn_Hz"] = round(wn / 2 / math.pi, 2)
    out["static_defl_mm"] = round(m * g / k_s * 1e3, 3)
    rows = []
    for kc in IN["k_c"]:
        w2 = math.sqrt((k_s + kc) / m)
        amp_contact = v / w2                              # 닿는 순간: 바닥 속도 v, 두 스프링 사이 질량 (Meriam 8/1: 진폭 = ẋ0/ωn)
        F_contact = kc * amp_contact
        v_floor_press = v * k_s / (k_s + kc)              # 누르는 중 바닥 속도
        amp_stop = v_floor_press / w2                     # 캐리지가 갑자기 멈출 때
        F_stop = kc * amp_stop
        rows.append(dict(k_c=kc, f2_Hz=round(w2 / 2 / math.pi, 1), amp_contact_um=round(amp_contact * 1e6, 2),
                         dF_contact_N=round(F_contact, 4), amp_stop_um=round(amp_stop * 1e6, 3), dF_stop_N=round(F_stop, 5)))
    out["closed_form"] = rows
    out["step_force_ripple_N"] = round(k_s * IN["step_um"] * 1e-6, 5)      # 반걸음 하나가 스프링에 주는 힘 변화
    out["surge_vs_step"] = dict(surge_Hz=round(surge_hz), step_Hz=IN["step_rate"], ratio=round(surge_hz / IN["step_rate"], 2),
                                shigley_rule="서지 ≥ 15~20 × 가진 주파수")
    out["time_sim"] = [press_sim(k_s, kc, f, zeta) for kc in IN["k_c"] for f in IN["f_hx"] for zeta in (0.0, 0.1)]
    return out


def press_sim(k_s, kc, f_hx, zeta, dt=2e-6):
    """시간 적분 (반-암시 오일러): 캐리지 z_c = v t, 바닥 x, 말벌 접촉은 x ≥ gap 일 때 k_c (말벌 쪽 감쇠 ζ).
    로드셀은 스프링 힘 k_s (z_c − x) − W 를 1/f_hx 마다 읽음 → F_p 넘으면 t_stop 뒤 캐리지 멈춤. 최대 N_h 기록"""
    m, v, W = IN["m_floor"], IN["v"], IN["m_floor"] * g
    gap = 0.2e-3
    c = 2 * zeta * math.sqrt((k_s + kc) * m)
    x0 = -W / k_s                    # 정적 평형 (스프링 줄어든 만큼)
    x, xd, t = x0, v, 0.0
    t_next, t_halt, halted = 0.0, None, False
    Nmax, N_at_detect, zc = 0.0, None, 0.0
    t_contact = (gap - x0) / v
    T_end = t_contact + IN["F_p"] / (1 / (1 / k_s + 1 / kc)) / v + 1.5
    while t < T_end:
        zc = v * t if not halted else v * t_halt
        pen = x - gap
        N = kc * pen + c * xd if pen > 0 else 0.0
        N = max(N, 0.0)
        Fs = k_s * (zc - x)
        a = (Fs - W - N) / m
        xd += a * dt
        x += xd * dt
        t += dt
        Nmax = max(Nmax, N)
        if not halted and t >= t_next:
            t_next += 1.0 / f_hx
            reading = k_s * (zc - x) - W + 0.0     # 0점 맞춘 로드셀 읽음 ≈ N_h (+ 관성)
            if reading >= IN["F_p"] and t_halt is None:
                t_halt = t + IN["t_stop"]
                N_at_detect = N
        if t_halt is not None and t >= t_halt:
            halted = True
    return dict(k_c=kc, f_hx=f_hx, zeta=zeta, N_max_N=round(Nmax, 4), over_pct=round(100 * (Nmax / IN["F_p"] - 1), 2),
                N_at_detect=round(N_at_detect or 0, 4))


# ---------------------------------------------------------------- D 기계요소
MUSIC_IN = [0.006, 0.007, 0.008, 0.009, 0.010, 0.011, 0.012, 0.013, 0.014, 0.016, 0.018, 0.020, 0.022]   # Table A-28 음악선 게이지


def spring_row(d, D, Na=None, k_target=None, ends="squared_ground"):
    """d, D [m]. Na를 주면 그대로, 아니면 k_target에서 Na 계산 → 반 바퀴 단위로 맞춤"""
    dm = d * 1e3
    G = G_music(dm)
    if Na is None:
        Na = G * d ** 4 / (8 * D ** 3 * k_target)
        Na = round(Na * 2) / 2
    k = G * d ** 4 / (8 * D ** 3 * Na)
    C = D / d
    Sut = IN["A"] / dm ** IN["mexp"] * 1e6
    Ssy = 0.45 * Sut
    W = IN["m_floor"] * g
    x_pre = W / k
    y_max = x_pre + IN["h_max"]                    # 로드셀 고장 때 가장 많이 줄어듦
    Nt = Na + 2
    Ls = d * Nt                                     # squared & ground (Table 10-1)
    L0 = Ls + (1 + IN["xi"]) * y_max                # 그림 10-3
    Fs = k * (L0 - Ls)                              # 밀착 힘
    tau_s = KB(C) * 8 * Fs * D / (math.pi * d ** 3)
    ns = Ssy / tau_s
    L0cr = 2.63 * D / 0.5
    Wsp = math.pi ** 2 * d ** 2 * D * Na * IN["gamma"] / 4     # 식 10-27
    f_surge = 0.5 * math.sqrt(k * g / Wsp)                      # 식 10-25
    # 피로 (Zimmerli, 연마 안 함 unpeened: Ssa 241, Ssm 379 MPa; Ssu = 0.67 Sut; Goodman — Shigley 식 10-28a, 10-29a, 10-30)
    F_min, F_max = W, W + IN["F_p"] * 1.25         # 누르기 한 번: 바닥 무게 ~ F_p + 넘침 여유 25 %
    Fa, Fm = (F_max - F_min) / 2, (F_max + F_min) / 2
    ta = KB(C) * 8 * Fa * D / (math.pi * d ** 3)
    tm = KB(C) * 8 * Fm * D / (math.pi * d ** 3)
    Ssu = 0.67 * Sut
    Sse = 241e6 / (1 - 379e6 / Ssu)
    nf = 1 / (ta / Sse + tm / Ssu)
    rid = None
    return dict(d_mm=round(dm, 3), d_in=round(dm / 25.4, 4), D_mm=round(D * 1e3, 3), C=round(C, 2), Na=Na, k=round(k, 1),
                k_lbf_in=round(k * 0.0254 / 4.448, 3), OD_mm=round((D + d) * 1e3, 2), ID_mm=round((D - d) * 1e3, 2),
                Sut_MPa=round(Sut / 1e6), Ssy_MPa=round(Ssy / 1e6), x_pre_mm=round(x_pre * 1e3, 2), y_max_mm=round(y_max * 1e3, 2),
                Ls_mm=round(Ls * 1e3, 2), L0_mm=round(L0 * 1e3, 2), F_solid_N=round(Fs, 3), tau_solid_MPa=round(tau_s / 1e6),
                ns=round(ns, 2), L0cr_mm=round(L0cr * 1e3, 1), surge_Hz=round(f_surge), nf_goodman=round(nf, 2),
                ok_C=4 <= C <= 12, ok_Na=3 <= Na <= 15, ok_ns=ns >= IN["ns_min"], ok_k=IN["k_band"][0] <= k <= IN["k_band"][1],
                ok_OD=(D + d) <= IN["OD_max"], buckle_free=L0 <= L0cr, nf_ok=nf >= IN["nf_min"])


def machine_elements():
    table = []
    for rod in IN["rods"]:
        for al in IN["allows"]:
            for din in MUSIC_IN:
                d = din * 25.4e-3
                D = rod + d + al                              # 그림 10-3 '봉 위에서' D = d_rod + d + allow
                # Na는 반 바퀴 단위. k 범위 안에서 100 N/m에 가장 가까운 것 (없으면 계산값 그대로 → 불가로 표시)
                G = G_music(d * 1e3)
                cands = [n / 2 for n in range(6, 31)]
                ks = [(abs(G * d ** 4 / (8 * D ** 3 * n) - IN["k_target"]), n) for n in cands
                      if IN["k_band"][0] <= G * d ** 4 / (8 * D ** 3 * n) <= IN["k_band"][1]]
                r = spring_row(d, D, Na=min(ks)[1]) if ks else spring_row(d, D, k_target=IN["k_target"])
                r["rod_mm"] = rod * 1e3
                r["allow_mm"] = round(al * 1e3, 1)
                r["feasible"] = all(r[k] for k in ("ok_C", "ok_Na", "ok_ns", "ok_k", "ok_OD")) and r["nf_ok"]
                table.append(r)
    feas = [r for r in table if r["feasible"]]
    fom = lambda r: -(r["d_mm"] ** 2) * (r["Na"] + 2) * r["D_mm"]     # 식 10-22 (같은 재료라 상대값만)
    # 고르는 규칙: k가 100 N/m에 가장 가까운 것 (C3 고장 힘 여유) → 같으면 굵은 봉 (안내가 단단함) → fom
    best = min(feas, key=lambda r: (round(abs(r["k"] - IN["k_target"]) / 10), -r["rod_mm"], -fom(r))) if feas else None
    first = spring_row(0.4e-3, 7.5e-3, Na=6)             # 1차 계산에서 고른 스프링 — 교재 범위로 다시 봄
    first["note"] = "1차 선택 (d 0.4, D 7.5): C = 18.75 > 12 → Shigley 권장 범위 밖 (감기 어렵고 엉킴)"
    return dict(table=table, feasible=feas, choice=best, first_choice_recheck=first)


def window_with(k):
    """1차 계산의 조건 C1·C2·C2b·C3를 새 k로 다시"""
    v, Fp = IN["v"], IN["F_p"]
    kc_lo, kc_hi = IN["k_c"]
    keff = lambda kc: k * kc / (k + kc)
    td10 = 1 / 10 + 0.1 / 10 + IN["t_stop"]
    return dict(C1_over_pct_10Hz=round(100 * keff(kc_hi) * v * td10 / Fp, 2),
                C2_reach_before_limit_mm=round(Fp / keff(kc_hi) * 1e3, 2), C2_limit_mm=round((IN["h_min"] - IN["margin"]) * 1e3, 2),
                C2b_F_at_limit_soft_N=round(keff(kc_lo) * IN["h_min"], 3),
                C3_F_runaway_N=round(k * IN["h_max"], 3), F_safe=IN["F_safe"],
                t_press_after_contact_s=round(Fp / keff(kc_hi) / v, 2))


def main():
    me = machine_elements()
    ch = me["choice"]
    res = dict(inputs=IN, A_statics=statics(), D_machine=me, B_solids=solids(ch["k"]), C_dynamics=dynamics(ch["k"], ch["surge_Hz"]),
               window_new_k=window_with(ch["k"]))
    with open(os.path.join(HERE, "spring146_calc2_results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("== D 선택:", json.dumps(ch, ensure_ascii=False))
    print("== D 1차 다시:", json.dumps(me["first_choice_recheck"], ensure_ascii=False))
    print("== 가능한 것", len(me["feasible"]))
    for r in me["feasible"]:
        print("   rod %.1f al %.1f d %.3f D %.2f C %.1f Na %.1f k %.1f L0 %.1f ns %.2f surge %d nf %.2f" % (r["rod_mm"], r["allow_mm"], r["d_mm"], r["D_mm"], r["C"], r["Na"], r["k"], r["L0_mm"], r["ns"], r["surge_Hz"], r["nf_goodman"]))
    A = res["A_statics"]
    print("== A", {k: A[k] for k in A if k != "rows"})
    for r in A["rows"]:
        if r["e_mm"] in (0.0, 20.0):
            print("  ", r)
    print("== B", json.dumps(res["B_solids"], ensure_ascii=False))
    C = res["C_dynamics"]
    print("== C", json.dumps({k: C[k] for k in C if k != "time_sim"}, ensure_ascii=False))
    for r in C["time_sim"]:
        print("  ", r)
    print("== 창", res["window_new_k"])


if __name__ == "__main__":
    main()
