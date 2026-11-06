# -*- coding: utf-8 -*-
"""스프링 146 (바닥 누르기 스프링) 강성 k 정하기 — S4 역학계산 방식 (서현, 2026-11-06, CAP-AI-24)

쌓임 순서 (D5e, cad/D5e_full_assembly.py): 캐리지(T8 너트) → 로드셀 148 → 스프링 146 → 밀대 147 → 바닥 140
바닥이 말벌 등에 닿은 뒤 캐리지가 더 올라가면 스프링이 줄어들며 힘이 생긴다 → 로드셀이 F_p에서 멈춤.

정하는 조건 (모두 이 파일에서 계산)
  C1 넘침: 멈춤 지연 동안 더 올라간 만큼 생기는 힘 ΔF = k_eff·v·t_d ≤ 0.2·F_p
  C2 도달: 가장 낮은 등(h_min)·단단한 접촉에서도 캐리지 한계(F_max) 1 mm 전에 F_p 도달 → F_p/k_eff ≤ h_min − 여유
  C2b 붙잡기: 가장 낮은 등·가장 무른 접촉이면 한계에서 멈출 수 있음 → 그때 힘 ≥ 0.8·F_p (말벌이 못 빠져나감)
  C3 고장 안전: 로드셀이 고장(0으로 읽음)이면 바닥은 F_max 한계까지 감 → 가장 큰 힘 k_s·h_max ≤ F_safe
  C4 진동: 바닥+밀대 질량의 고유진동수가 HX711 표본 주파수의 나이퀴스트보다 낮을 것
  C5 강도·좌굴: 전단응력 ≤ 0.45·Sut, 자유길이/평균지름 < 2.6 (안내 없이도 좌굴 안 함)

실행: python3 design/calc/spring146_calc.py  → design/calc/spring146_results.json, design/img/calc/spring146_*.png
"""
import json
import math
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "Noto Sans CJK JP", "axes.unicode_minus": False})
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "img", "calc")
g = 9.81

# ---------------------------------------------------------------- 입력 (근거)
IN = dict(
    F_p=0.5,              # N, 멈춤 힘 [확실 — D6 F_p, 단 F_harm 미정 R7]
    F_safe=1.0,           # N, 고장일 때 허용 최대 힘 [추측 — R7 표본 압축 전 임시, F_p의 2배]
    v=1.96e-3,            # m/s, 바닥 속도 [확실 — 펌웨어 반걸음 1000 µs, trap_sim PRM v_mm_s]
    f_hx=(10.0, 80.0),    # Hz, HX711 RATE 낮음/높음 [확실 — HX711 사양; 회로는 80 Hz로 묶음]
    t_stop=0.005,         # s, 판단 + 마지막 걸음 [가능성 높음]
    k_c=(300.0, 3000.0),  # N/m, 말벌 몸 + 격자 접촉 강성 범위 [추측 — R7 전]
    h_min=6.5e-3, h_max=8.5e-3,   # m, 말벌 등 높이 범위 (D6 hornet_h 7.5 ± 1) [가능성 높음]
    margin=1.0e-3,        # m, C2 여유
    m_floor=(9.0883 + 0.7677) * 1e-3,   # kg, 바닥 140 + 밀대 147 [가능성 높음 — CAD 질량, 승준 d5e_mass_cad_sj.json]
    G=79.3e9,             # Pa, 피아노선 전단탄성계수 [확실 — 교재 표]
    Sut_04=2.3e9,         # Pa, 피아노선 0.4 mm 인장강도 근사 (A=2211 MPa·mm^m, m=0.145 → 2.52 GPa; 보수적으로 2.3) [가능성 높음]
    env_OD=9.0e-3, env_ID_min=4.0e-3 + 1.0e-3,   # m, CAD 외경 9 mm 안, 밀대 Ø4 + 틈 1 mm
)


def t_delay(f):
    # 표본 한 개를 놓칠 수 있음 (최악: 표본 직후에 F_p를 넘음) + 판단·정지
    return 1.0 / f + 1.0 / f * 0.1 + IN["t_stop"]


def k_eff(ks, kc):
    return ks * kc / (ks + kc)


def window():
    v, Fp = IN["v"], IN["F_p"]
    td10 = t_delay(IN["f_hx"][0])
    dx10 = v * td10
    # C1 (10 Hz 최악, k_c 가장 큼): k_eff ≤ 0.2 F_p / dx
    keff_max = 0.2 * Fp / dx10
    kc = IN["k_c"][1]
    ks_C1 = keff_max * kc / (kc - keff_max) if kc > keff_max else float("inf")
    inv = (IN["h_min"] - IN["margin"]) / Fp - 1.0 / IN["k_c"][1]
    ks_C2 = 1.0 / inv
    ke_b = 0.8 * Fp / IN["h_min"]
    ks_C2b = ke_b * IN["k_c"][0] / (IN["k_c"][0] - ke_b)
    ks_C3 = IN["F_safe"] / IN["h_max"]
    return dict(td10_s=round(td10, 4), dx10_mm=round(dx10 * 1e3, 3), ks_C1_max=round(ks_C1, 1),
                ks_C2_min=round(ks_C2, 1), ks_C2b_min=round(ks_C2b, 1), ks_C3_max=round(ks_C3, 1))


def rigid_case():
    """스프링 없을 때 (로드셀이 바로 바닥을 밀 때) 넘치는 힘 — 왜 스프링이 필요한지"""
    out = []
    for f in IN["f_hx"]:
        dx = IN["v"] * t_delay(f)
        for kc in IN["k_c"]:
            out.append(dict(f_Hz=f, k_c=kc, dF_N=round(kc * dx, 3), pct_of_Fp=round(100 * kc * dx / IN["F_p"])))
    return out


def coil(d, D, n, L0):
    G = IN["G"]
    k = G * d ** 4 / (8 * D ** 3 * n)
    C = D / d
    Kw = (4 * C - 1) / (4 * C - 4) + 0.615 / C
    Ls = (n + 2) * d                         # 끝 2감김 닫고 연마
    x_pre = IN["m_floor"] * g / k            # 바닥 무게로 줄어든 길이
    x_run = x_pre + IN["h_max"]              # 고장 때 가장 많이 줄어든 길이
    F_run = k * x_run
    tau = Kw * 8 * F_run * D / (math.pi * d ** 3)
    fn = math.sqrt(k / IN["m_floor"]) / (2 * math.pi)
    return dict(d_mm=d * 1e3, D_mm=D * 1e3, OD_mm=round((D + d) * 1e3, 2), ID_mm=round((D - d) * 1e3, 2), n=n, L0_mm=L0 * 1e3,
                k_N_per_m=round(k, 1), k_N_per_mm=round(k / 1e3, 4), k_lbf_per_in=round(k * 0.0254 / 4.448, 3),
                C=round(C, 2), Kw=round(Kw, 3), Ls_mm=round(Ls * 1e3, 2), x_pre_mm=round(x_pre * 1e3, 2),
                x_Fp_mm=round(IN["F_p"] / k * 1e3, 2), x_run_mm=round(x_run * 1e3, 2), F_run_N=round(F_run, 3),
                L_run_mm=round((L0 - x_run) * 1e3, 2), solid_ok=(L0 - x_run) > 1.15 * Ls,
                tau_MPa=round(tau / 1e6), tau_allow_MPa=round(0.45 * IN["Sut_04"] / 1e6), tau_ok=tau < 0.45 * IN["Sut_04"],
                L0_over_D=round(L0 / D, 2), buckle_ok=L0 / D < 2.6, fn_Hz=round(fn, 1),
                fit_ok=(D + d) <= IN["env_OD"] and (D - d) >= IN["env_ID_min"])


def check_choice(k):
    rows = []
    for f in IN["f_hx"]:
        dx = IN["v"] * t_delay(f)
        for kc in IN["k_c"]:
            ke = k_eff(k, kc)
            rows.append(dict(f_Hz=f, k_c=kc, k_eff=round(ke, 1), dF_N=round(ke * dx, 4), pct_of_Fp=round(100 * ke * dx / IN["F_p"], 1)))
    t_press = IN["F_p"] / k_eff(k, IN["k_c"][1]) / IN["v"]   # 닿은 뒤 F_p까지 걸리는 시간 (단단한 접촉)
    F_lim_soft = k_eff(k, IN["k_c"][0]) * IN["h_min"]          # 낮은 등·무른 접촉: 한계에서의 힘
    return rows, round(t_press, 2), round(F_lim_soft, 3)


def sensitivity():
    """F_safe를 모르니 R7 결과별 허용 범위"""
    w = window()
    out = []
    for Fs in (0.7, 0.8, 1.0, 1.5, 2.0):
        hi = min(w["ks_C1_max"], Fs / IN["h_max"])
        lo = max(w["ks_C2_min"], w["ks_C2b_min"])
        out.append(dict(F_safe_N=Fs, ks_min=lo, ks_max=round(hi, 1), ok=hi >= lo))
    return out


def fig(spec, w):
    os.makedirs(IMG, exist_ok=True)
    fig_, ax = plt.subplots(figsize=(8.6, 5.2), dpi=150)
    x = np.linspace(0, 9.5, 200)  # 닿은 뒤 캐리지가 더 올라간 거리 mm
    for ks, c, lab in ((w["ks_C2_min"], "#9aa5b1", "k = %.0f N/m (C2 아래 끝)" % w["ks_C2_min"]),
                       (spec["k_N_per_m"], "#1f4e9a", "선택 k = %.0f N/m" % spec["k_N_per_m"]),
                       (w["ks_C3_max"], "#d35400", "k = %.0f N/m (C3 위 끝)" % w["ks_C3_max"])):
        F = k_eff(ks, IN["k_c"][1]) * x * 1e-3
        ax.plot(x, F, color=c, lw=2.2 if c == "#1f4e9a" else 1.6, label=lab)
    ax.axhline(IN["F_p"], color="#c0392b", lw=1.2, ls="--")
    ax.text(0.2, IN["F_p"] + 0.02, "F_p = 0.5 N (로드셀이 멈추는 힘)", color="#c0392b", fontsize=9)
    ax.axhline(IN["F_safe"], color="#7d3c98", lw=1.2, ls="--")
    ax.text(7.4, IN["F_safe"] - 0.035, "F_safe = 1.0 N [추측] (고장일 때 넘으면 안 되는 힘)", color="#7d3c98", fontsize=9, ha="right", va="top")
    ax.axvline(IN["h_max"] * 1e3, color="#666666", lw=1, ls=":")
    ax.text(IN["h_max"] * 1e3 - 0.1, 0.05, "고장 때 끝까지\n(h_max 8.5 mm)", ha="right", fontsize=8.5, color="#444")
    ax.axvline((IN["h_min"] - IN["margin"]) * 1e3, color="#666666", lw=1, ls=":")
    ax.text((IN["h_min"] - IN["margin"]) * 1e3 - 0.1, 1.12, "F_max 1 mm 전\n(h_min − 1 mm)", ha="right", fontsize=8.5, color="#444")
    ax.set_xlabel("바닥이 말벌 등에 닿은 뒤 캐리지가 더 올라간 거리 (mm)")
    ax.set_ylabel("말벌을 누르는 힘 (N)")
    ax.set_title("스프링 146: 너무 단단하면 고장 때 세게 누르고, 너무 무르면 F_p에 못 닿는다")
    ax.set_xlim(0, 9.5)
    ax.set_ylim(0, 1.45)
    ax.grid(color="#e5e5e5", lw=0.6)
    ax.legend(loc="upper left", fontsize=9, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig_.tight_layout()
    p = os.path.join(IMG, "spring146_힘_거리.png")
    fig_.savefig(p)
    plt.close(fig_)
    return p


def main():
    w = window()
    spec = coil(d=0.4e-3, D=7.5e-3, n=6, L0=16e-3)
    rows, t_press, F_lim_soft = check_choice(spec["k_N_per_m"])
    res = dict(inputs=IN, rigid_no_spring=rigid_case(), window=w, choice=spec, overshoot=rows,
               t_press_after_contact_s=t_press, F_at_limit_soft_lowest_N=F_lim_soft, sensitivity_F_safe=sensitivity(), fig=os.path.relpath(fig(spec, w), HERE))
    with open(os.path.join(HERE, "spring146_results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: res[k] for k in ("window", "choice", "t_press_after_contact_s", "F_at_limit_soft_lowest_N", "sensitivity_F_safe")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
