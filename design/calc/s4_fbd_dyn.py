# -*- coding: utf-8 -*-
"""S4 동역학 M7~M10 그림 (교재 유제 그림 + 우리 자유물체도·운동 그림 + 결과 그래프) — CAP-AI-21
실행: python3 design/calc/s4_fbd_dyn.py (먼저 s4_dyn_calc.py) → design/img/fbd/M7~M10_D5e_*.jpg
교재 그림은 베끼지 않고 주어진 수치로 새로 그림.
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fbd_lib import (plt, GIVEN, UNK, FRIC, INER, MOM, DIM, arrow, label, force, dim, angle, moment, triad, ground,  # noqa: E402
                     point, cg, body, rect, note, legend, setup, save, Circle)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "img", "fbd")
R = json.load(open(os.path.join(HERE, "s4_dyn_results.json"), encoding="utf-8"))
D = R["D"]
g = 9.81


def kd_eq(ax, x, y):
    label(ax, (x, y), "=", fs=26, box=False)


# ---------------- M7 문 미닫이 ----------------
def m7():
    fig = plt.figure(figsize=(19, 13))
    gs = fig.add_gridspec(2, 3, width_ratios=[0.8, 1.2, 1.0], height_ratios=[1, 1], hspace=0.22, wspace=0.12)
    # (a) 교재 5/26
    ax = fig.add_subplot(gs[0, 0])
    ax.add_patch(Circle((0, 0), 3.2, fc="#eef1f6", ec="#333", lw=1.4))
    th = math.radians(55)
    A = np.array([2.4 * math.cos(th), 2.4 * math.sin(th)])
    ax.plot([0, A[0]], [0, A[1]], color="#555", lw=2.5)
    point(ax, (0, 0), "O", off=(-0.4, -0.4))
    point(ax, A, "A", off=(0.35, 0.35))
    body(ax, [(A[0] - 0.25, -3.6), (A[0] + 0.25, -3.6), (A[0] + 0.25, 3.6), (A[0] - 0.25, 3.6)], fc="#c9ced6")
    body(ax, [(A[0] + 0.25, -0.2), (6.5, -0.2), (6.5, 0.2), (A[0] + 0.25, 0.2)], fc="#c9ced6")
    point(ax, (6.5, 0), "P", off=(0.35, 0.35))
    angle(ax, (0, 0), 0.9, 0, 55, "θ", tr=1.45)
    moment(ax, (0, 0), 1.6, 120, 200)
    label(ax, (-2.1, 1.6), "ω, α", c=MOM, fs=11)
    dim(ax, (0, -4.3), (6.5, -4.3), "s = r cos θ + d", off=0, fs=10)
    note(ax, (0.0, 0.16), "주어진 것: r, d, θ, ω, α (문자)\n해설집: v = −rω sin θ\n           a = −rα sin θ − rω² cos θ\nAI: 수치 미분과 대조 (차이 10^-7 이하)", fs=10)
    setup(ax, (-4, 7.4), (-7.8, 4.2), "(a) 교재 Meriam 5/26 스카치 요크")
    # (b) 우리 문판 자유물체도 + 운동 그림
    ax = fig.add_subplot(gs[0, 1:])
    ph = math.radians(25)
    O = np.array([0.0, 2.6])
    Pn = O + 3.0 * np.array([math.sin(ph), -math.cos(ph)])
    ax.add_patch(Circle(tuple(O), 0.45, fc="#3b6fd8", ec="#1d3f8a", lw=1, alpha=0.5))
    label(ax, (-1.9, 2.6), "MG90S 축 O\n(문 서보, 떼어 냄)", fs=9, box=False)
    ax.plot([O[0], Pn[0]], [O[1], Pn[1]], color="#999", lw=3, alpha=0.6)
    ax.plot([0, 0], [2.6, -0.5], color=DIM, lw=0.8, ls=":")
    angle(ax, O, 1.3, -90, -90 + 25, "φ", tr=1.35)
    label(ax, (Pn[0] + 0.5, Pn[1] + 1.2), "혼 (r = 9)", fs=9, c="#777777", box=False)
    body(ax, [(0.4, -1.9), (6.4, -1.9), (6.4, 0.7), (Pn[0] + 0.25, 0.7), (Pn[0] + 0.25, -1.1), (Pn[0] - 0.25, -1.1), (Pn[0] - 0.25, 0.7), (0.4, 0.7)], fc="#f2a65a", alpha=0.85)
    ax.add_patch(Circle(tuple(Pn), 0.18, fc="white", ec="#333", zorder=8))
    label(ax, (4.6, 0.3), "문판 0.78 g", fs=10, box=False)
    G = np.array([4.3, -0.7])
    force(ax, (Pn[0] + 0.25, Pn[1]), (1.5, 0), UNK, "F_pin (핀이 홈 벽을 밂)", push=False, off=(0.9, -0.45), fs=10)
    force(ax, G, (0, -1.6), GIVEN, "mg", push=False, off=(0.3, -0.1), ha="left", fs=10)
    force(ax, (5.6, -1.9), (0, 1.3), UNK, "N", push=True, off=(0.25, -0.2), ha="left", fs=10)
    force(ax, (2.6, -1.9), (-1.6, 0), FRIC, "μN (운동 반대)", push=False, off=(-0.2, -0.4), fs=10)
    force(ax, (6.4, -0.6), (-1.4, 0), "#888888", "F_h (말벌이 끼면,\n닫힘 반대)", push=True, off=(0.6, 0.75), fs=9, ls="--")
    arrow(ax, (1.0, 1.5), (3.6, 1.5), "#2e8b57", lw=1.4, ls="--")
    label(ax, (2.3, 1.9), "닫힘 방향 +y (v, a)", c="#2e8b57", fs=9)
    triad(ax, (-3.6, -3.4), 1.0, names=("y", "z"))
    kd_eq(ax, 8.9, -0.6)
    body(ax, [(9.8, -1.9), (12.8, -1.9), (12.8, 0.7), (9.8, 0.7)], fc="#f2a65a", alpha=0.3, ls="--")
    force(ax, (11.3, -0.6), (1.6, 0), INER, "m a_y", push=False, off=(-0.6, 0.6), ls="--", fs=10)
    label(ax, (5.0, -3.6), "핀이 세로 홈 안에서 미끄러짐 → 핀은 y 방향 힘만 전함.  문판 y = r sin φ (+60° 닫힘 ~ −60° 열림)\n교재 θ = 90° − φ 로 놓으면 5/26과 같은 식", fs=9.5)
    setup(ax, (-4.2, 13.4), (-4.4, 3.4), "(b) 문판 자유물체도 = 운동 그림")
    # (c) 식과 결과
    ax = fig.add_subplot(gs[1, 2])
    m7 = R["M7"]
    note(ax, (0.0, 0.98), "ΣF_y = m a_y:  F_pin − μN − F_h = m a_y\nv = rω cos φ,  a = −rω² sin φ  (서보 정속 ω, α = 0)\n\nMG90S 0.1 s/60° → ω = %.2f rad/s, r = 9 mm\n최대 속도 %.0f mm/s (φ = 0), 최대 가속도 %.3f m/s² (φ = ±60°)\n닫힘 시간 %.2f s, 행정 %.1f mm\n\n필요 토크 (관성 + 슬롯 마찰): %.3f N·mm\n→ MG90S %.0f N·mm의 1/%.0f — 토크는 문제 없음\n\n대신 말벌이 문틈에 있으면:\n서보가 낼 수 있는 닫힘 힘 F = T / (r cos φ)\n= %.0f N (가운데) ~ %.0f N (닫힘 끝)\n→ 찍는 힘 기준 0.5 N의 40~90배: 말벌이 눌림\n\n판정: 운동·토크 만족 / 끼임 위험\n환류 ① 닫기 전·닫는 0.2 s 동안 빛 게이트로 문틈 확인\n② 문판–혼 사이 약한 스프링(힘 상한) 또는 닫힘 끝 10° 느리게\n③ F_harm(말벌이 다치는 힘) 시험 — 미측정\n안 풀었다면: '토크가 남는다'만 보고 닫힘 힘을 놓침" % (
        D["w_mg90s"], m7["v_max_mms"], m7["a_max_ms2"], m7["t_close_s"], m7["stroke_mm"], m7["T_need_max_Nmm"],
        D["T_mg90s"], m7["SF_torque"], m7["F_close_mid_N"], m7["F_close_end_N"]), fs=10.5)
    setup(ax, (0, 1), (0, 1), "(c) 식·결과·판정·환류")
    # (d) 그래프
    ax = fig.add_subplot(gs[1, :2])
    phs = np.linspace(-60, 60, 241)
    r = D["r_gate"]
    w = D["w_mg90s"]
    ax.plot(phs, r * np.sin(np.radians(phs)), color="#555", lw=2, label="문판 위치 y (mm)")
    ax.plot(phs, r * w * np.cos(np.radians(phs)) / 10, color=UNK, lw=2, label="속도 v (10 mm/s 단위)")
    ax.plot(phs, -r * w ** 2 * np.sin(np.radians(phs)) / 100, color=INER, lw=2, ls="--", label="가속도 a (0.1 m/s² 단위)")
    ax.axhline(0, color="#999", lw=0.8)
    ax.set_xlabel("혼 각 φ (°)  ← 열림 −60 · 닫힘 +60 →")
    ax.legend(loc="upper left", fontsize=10)
    ax2 = ax.twinx()
    ax2.plot(phs, D["T_mg90s"] / (r * np.cos(np.radians(phs))), color=GIVEN, lw=2.2, label="서보가 낼 수 있는 닫힘 힘 (N)")
    ax2.axhline(0.5, color=GIVEN, lw=1, ls=":")
    ax2.text(-58, 2.5, "0.5 N (찍는 힘 기준, 참고)", color=GIVEN, fontsize=9)
    ax2.set_ylabel("닫힘 힘 (N)", color=GIVEN)
    ax2.set_ylim(0, 50)
    ax2.legend(loc="upper right", fontsize=10)
    ax.set_title("(d) 문판 운동과 닫힘 힘 (MG90S 4.8 V, 정속 회전 가정)", loc="left", fontsize=12, fontweight="bold")
    legend(fig.axes[1], ("given", "unk", "fric", "iner"), loc=(0.82, 0.62))
    fig.suptitle("M7  문 미닫이(스카치 요크)의 운동과 닫힘 힘 — 동역학(강체 평면 운동학 + 질점 운동방정식) ↔ Meriam 5/26", fontsize=15, x=0.01, ha="left", fontweight="bold")
    save(fig, os.path.join(OUT, "M7_D5e_문_스카치요크.jpg"))


# ---------------- M8 펜 내려찍기 충격 ----------------
def m8():
    fig = plt.figure(figsize=(19, 12))
    gs = fig.add_gridspec(2, 3, width_ratios=[0.85, 1.3, 1.05], height_ratios=[1, 0.9], hspace=0.25, wspace=0.15)
    ax = fig.add_subplot(gs[0, 0])
    ground(ax, (-2.5, 0), (2.5, 0), n=10, h=0.3)
    xs = np.linspace(0, 3.0, 200)
    ax.plot(0.6 * np.sin(xs * 2 * math.pi * 4 / 3.0), xs, color="#555", lw=1.5)
    body(ax, [(-1.2, 3.0), (1.2, 3.0), (1.2, 3.2), (-1.2, 3.2)], fc="#c9ced6")
    label(ax, (1.9, 2.2), "k = 4 kN/m\n50 mm 미리 눌림\n(끈으로)", fs=9)
    rect(ax, -0.9, 5.2, 1.8, 1.6, fc="#d9c7a3")
    label(ax, (0, 6.0), "6 kg", fs=10, box=False)
    dim(ax, (-1.6, 3.2), (-1.6, 5.2), "h = 100 mm", off=0, fs=9)
    note(ax, (0.0, 0.2), "정지에서 놓음 → 스프링을 δ 더 누름\nm g (h + δ) = ∫ k x dx (x: 50 → 50 + δ mm)\n해설집 δ = 29.4 mm, AI 29.43 mm", fs=10)
    setup(ax, (-3, 3.2), (-3.2, 7.4), "(a) 교재 Meriam 3/108")
    # (b) 우리
    ax = fig.add_subplot(gs[0, 1])
    rect(ax, -0.8, 1.0, 1.6, 5.0, fc="#ffe26a")
    label(ax, (0, 5.2), "홀더 + 마커\n33.0 g", fs=9.5, box=False)
    ax.plot([-0.25, 0.25, 0], [1.0, 1.0, 0.4], color="#333")
    body(ax, [(-0.25, 1.0), (0.25, 1.0), (0, 0.45)], fc="#333")
    ax.add_patch(plt.matplotlib.patches.Ellipse((0, -0.2), 3.2, 1.2, fc="#d98b3a", ec="#7a4a12", alpha=0.6))
    label(ax, (2.4, -0.3), "말벌 흉부\n(접촉 강성 k_c)", fs=9)
    cg(ax, (0, 3.6), name="G", off=(0.55, 0.3))
    force(ax, (-0.3, 3.0), (0, -1.6), GIVEN, "W = 0.324 N", push=False, off=(-0.3, -0.2), ha="right", fs=10)
    force(ax, (0, 6.0), (0, -1.0), GIVEN, "F_s (스프링 204, 0 ~ 0.144 N)", push=True, off=(0.3, 0.2), ha="left", fs=10)
    force(ax, (0.8, 4.6), (0, 1.2), FRIC, "f ≤ 0.0125 N\n(핀 마찰)", push=False, off=(0.35, 0.3), ha="left", fs=9)
    force(ax, (0, 0.45), (0, 1.8), UNK, None, push=True)
    label(ax, (-1.7, 0.2), "N_c = k_c δ", c=UNK, fs=11)
    label(ax, (-3.3, 5.6), "혼은 탭에서 떨어짐\n(N_c ≥ W이 된 뒤)", fs=9, c="#777777")
    arrow(ax, (-2.2, 4.4), (-2.2, 2.6), "#2e8b57", lw=1.4, ls="--")
    label(ax, (-2.9, 3.5), "v_0 =\n혼 끝 속도", c="#2e8b57", fs=9)
    triad(ax, (-3.6, -0.6), 0.9, names=("y", "z"))
    kd_eq(ax, 4.2, 3.4)
    rect(ax, 5.2, 1.0, 1.6, 5.0, fc="#ffe26a", alpha=0.35, ls="--")
    force(ax, (6.0, 3.6), (0, 1.6), INER, "m a (위로: 감속)", push=False, off=(0.4, 0.4), ha="left", ls="--", fs=10)
    setup(ax, (-4.2, 9.0), (-1.2, 8.0), "(b) 홀더 자유물체도 = 운동 그림 (가장 깊이 눌린 순간)")
    # (c) 식
    ax = fig.add_subplot(gs[0, 2])
    m8 = R["M8"]
    rows = m8["rows"]
    txt = "일-에너지 (닿는 순간 → 가장 깊이):\n혼이 W'까지 받쳐 주다 떨어진 뒤\n½ m v_0² = ½ k_c (δ − δ_s)²,  δ_s = W'/k_c\n→ F_max = W' + v_0 √(k_c m),  W' = W + F_s\n\nSG90 최고 속도 0.1 s/60°: v_0 = 14 mm × ω cos %.1f°\n= %.0f mm/s\n\nk_c (N/m)   F_s 0      F_s 0.144 N\n" % (m8["theta_contact_deg"], rows[0]["v_full_mms"])
    for k in D["k_c"]:
        a_ = [x for x in rows if x["k"] == k]
        txt += "  %5.0f    %.2f N (×%.1f)   %.2f N (×%.1f)\n" % (k, a_[0]["F_max_full_N"], a_[0]["ratio"], a_[1]["F_max_full_N"], a_[1]["ratio"])
    txt += "\n→ 모두 F_p 0.5 N 초과: 말벌이 격자에서 밀리거나 다침\n\nF_max ≤ 0.5 N 이 되는 혼 속도 (F_s 0):\n  %.0f ~ %.0f °/s  (F_s 0.144 N이면 %.0f ~ %.0f °/s)" % (
        min(x["w_allow_dps"] for x in rows if x["F_s"] == 0), max(x["w_allow_dps"] for x in rows if x["F_s"] == 0),
        min(x["w_allow_dps"] for x in rows if x["F_s"] > 0), max(x["w_allow_dps"] for x in rows if x["F_s"] > 0))
    note(ax, (0.0, 0.98), txt, fs=10.3)
    setup(ax, (0, 1), (0, 1), "(c) 식과 결과 (k_c는 추측 범위)")
    # (d) 그래프
    ax = fig.add_subplot(gs[1, :2])
    m = D["m_holder"] * 1e-3
    W = m * g
    wd = np.linspace(0, 620, 300)
    v = D["Rt"] * 1e-3 * np.radians(wd) * math.cos(math.radians(m8["theta_contact_deg"]))
    cols = {300.0: "#7fb3e6", 1000.0: "#2f6db3", 3000.0: "#123a6b"}
    for k in D["k_c"]:
        ax.plot(wd, W + v * math.sqrt(k * m), color=cols[k], lw=2, label="k_c %.0f N/m, F_s 0" % k)
        ax.plot(wd, W + D["F_s_max"] + v * math.sqrt(k * m), color=cols[k], lw=1.6, ls="--", label="k_c %.0f, F_s 0.144" % k)
    ax.axhline(D["F_p"], color=GIVEN, lw=1.5, ls=":")
    ax.text(330, D["F_p"] - 0.09, "F_p = 0.5 N (말벌이 격자에 붙어 있는 한계, M3)", color=GIVEN, fontsize=10)
    ax.axvline(600, color="#999", lw=1)
    ax.text(470, 1.85, "SG90 최고 속도\n600 °/s", fontsize=9, color="#555")
    ax.axvspan(0, 60, color="#2e8b57", alpha=0.12)
    ax.text(8, 1.6, "권장: 마지막 2 mm\n≤ 60 °/s (F_s 0)", fontsize=9, color="#2e8b57")
    ax.set_xlabel("혼을 내리는 각속도 (°/s)")
    ax.set_ylabel("찍는 순간 최대 힘 F_max (N)")
    ax.set_xlim(0, 620)
    ax.set_ylim(0, 2.1)
    ax.legend(ncol=3, fontsize=9, loc="upper left", bbox_to_anchor=(0.12, 1.0))
    ax.set_title("(d) 내리는 속도와 찍는 순간 힘", loc="left", fontsize=12, fontweight="bold")
    ax = fig.add_subplot(gs[1, 2])
    note(ax, (0.0, 0.97), "판정: 서보를 최고 속도로 내리면 불만족\n(정적 0.32 N → 순간 0.8 ~ 1.8 N)\n\n환류 (제어)\n① 두 단계로 내림: 팁 위 2 mm까지 빠르게,\n   마지막 2 mm는 60 °/s 이하 (+%.2f s)\n② 스프링 204를 넣으면 ≤ 15 °/s 이거나 빼기\n③ k_c 측정: 저울 위 펠트 팁 눌림 (F_ink 시험과\n   같이) → 허용 속도 확정\n\n교재와 다른 점: 낙하 높이 대신 '혼이 내려 주는\n속도'가 v_0, 스프링 대신 접촉 강성 k_c\n유제를 안 풀었다면: 정적 힘 0.32 N만 보고\n'0.5 N 안'이라 판정했을 것" % m8["t_slow_2mm_s"], fs=10.5)
    setup(ax, (0, 1), (0, 1), "(e) 판정과 환류")
    legend(fig.axes[1], ("given", "unk", "fric", "iner"), loc=(0.62, 0.0))
    fig.suptitle("M8  펜 내려찍기 순간의 충격 힘 — 동역학(일-에너지, 스프링) ↔ Meriam 3/108", fontsize=15, x=0.01, ha="left", fontweight="bold")
    save(fig, os.path.join(OUT, "M8_D5e_펜_내려찍기_충격.jpg"))


# ---------------- M9 이송 시간 ----------------
def m9():
    fig = plt.figure(figsize=(19, 10.5))
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1.2, 1.0], height_ratios=[1, 1], hspace=0.35, wspace=0.18)
    ax = fig.add_subplot(gs[:, 0])
    t1, t2 = 18.88, 71.13
    ax.plot([0, t1, t1 + t2, 2 * t1 + t2], [0, 111.1, 111.1, 0], color=UNK, lw=2.5)
    ax.fill_between([0, t1, t1 + t2, 2 * t1 + t2], [0, 111.1, 111.1, 0], color=UNK, alpha=0.12)
    ax.text(t1 / 2, 40, "a = 0.6 g", ha="center")
    ax.text(t1 + t2 / 2, 115, "v_max = 400 km/h = 111.1 m/s", ha="center")
    ax.text(t1 + t2 / 2, 50, "넓이 = 거리 10 km", ha="center", color="#555")
    ax.set_xlabel("t (s)"); ax.set_ylabel("v (m/s)")
    ax.set_ylim(0, 135)
    ax.set_title("(a) 교재 Meriam 2/27 — 최소 시간 (사다리꼴)\n해설집 t = 108.9 s, AI 108.9 s", loc="left", fontsize=12, fontweight="bold")
    m9 = R["M9"]
    r15 = [x for x in m9["rows"] if x["rpm"] == 15.0][0]
    ax = fig.add_subplot(gs[0, 1])
    for dist, nm, c in ((D["dy"], "Y 58 mm", UNK), (D["dx"], "X 28 mm", "#7fb3e6"), (D["dz"], "바닥 36.5 mm", "#555")):
        v = r15["v_mms"]; a = D["a_xy"]
        ta = v / a; T = dist / v + ta
        ax.plot([0, ta, T - ta, T], [0, v, v, 0], lw=2, color=c, label="%s: %.1f s" % (nm, T))
    ax.set_xlabel("t (s)"); ax.set_ylabel("v (mm/s)")
    ax.set_ylim(0, 2.6)
    ax.legend(fontsize=10, loc="upper right")
    ax.set_title("(b) 우리: 15 rpm (2 mm/s), 가속 0.02 m/s² → 가속 구간 0.1 s뿐", loc="left", fontsize=12, fontweight="bold")
    ax = fig.add_subplot(gs[1, 1])
    r10 = [x for x in m9["rows"] if x["rpm"] == 10.0][0]
    names = ["T8 리드 8\n10 rpm", "T8 리드 8\n15 rpm", "벨트 GT2 20T\n15 rpm (비교)"]
    vals = [r10["t_y"], r15["t_y"], m9["belt"]["t_y"]]
    b = ax.barh(names, vals, color=["#9fb6dd", UNK, "#2e8b57"])
    for i, v in enumerate(vals):
        ax.text(v + 0.5, i, "%.1f s" % v, va="center")
    ax.set_xlabel("Y 58 mm 이동 시간 (s)")
    ax.set_xlim(0, 52)
    ax.set_title("(c) 이동 시간을 정하는 것은 속도 상한", loc="left", fontsize=12, fontweight="bold")
    ax = fig.add_subplot(gs[:, 2])
    note(ax, (0.0, 0.98), "식 (2/27과 같음):  거리 D ≥ v²/a 이면\n  t = D / v + v / a  (사다리꼴)\n\n속도 상한 v = 리드 × rpm / 60\n  28BYJ-48 반 스텝 최대 약 1000 Hz → 15 rpm\n  → 2.0 mm/s (10 rpm 1.33 mm/s)\n\n15 rpm: X 28 mm %.1f s, Y 58 mm %.1f s,\n          바닥 36.5 mm %.1f s\n가속 구간 몫: %.1f %% → 가속도를 키워도 소용없음\n\n판정: R6 (한 마리 3분) — 조건부\n기구·판별 합 63.9 s (r2 표) → 급이 ≤ 약 105 s\n\n환류\n① 시간을 줄이려면 속도 상한을 올려야 함:\n   벨트(Y %.1f s) 또는 NEMA17 (승준 제안)\n② 지금 리드스크루 유지 시 급이(잉크 건조)\n   시간이 R6를 가름 → 샤피 건조 시험\n\n유제를 안 풀었다면: 가속도·토크를 키우는\n쪽으로 잘못 손댔을 것" % (
        r15["t_x"], r15["t_y"], r15["t_z"], r15["accel_share"] * 100, m9["belt"]["t_y"]), fs=10.5)
    setup(ax, (0, 1), (0, 1), "(d) 식·판정·환류")
    fig.suptitle("M9  X·Y·바닥 이송 시간 — 동역학(직선 운동, 가속도·속도 제한) ↔ Meriam 2/27", fontsize=15, x=0.01, ha="left", fontweight="bold")
    save(fig, os.path.join(OUT, "M9_D5e_이송시간_사다리꼴.jpg"))


# ---------------- M10 고유진동수 ----------------
def m10():
    fig = plt.figure(figsize=(19, 11))
    gs = fig.add_gridspec(2, 3, width_ratios=[0.8, 1.2, 1.05], height_ratios=[1, 0.95], hspace=0.3, wspace=0.15)
    ax = fig.add_subplot(gs[0, 0])
    body(ax, [(-2, 6.5), (2, 6.5), (2, 6.8), (-2, 6.8)], fc="#c9ced6")
    ys = np.linspace(3.2, 6.5, 200)
    ax.plot(0.5 * np.sin((ys - 3.2) * 2 * math.pi * 5 / 3.3), ys, color="#555", lw=1.5)
    rect(ax, -1.0, 1.6, 2.0, 1.6, fc="#d9c7a3")
    label(ax, (0, 2.4), "30 kg", fs=10, box=False)
    force(ax, (0, 1.6), (0, -1.2), GIVEN, "mg", push=False, off=(0.35, -0.1), ha="left")
    force(ax, (0, 3.2), (0, 1.0), UNK, "k δ_st", push=False, off=(0.6, 0.6), ha="left")
    note(ax, (0.0, 0.2), "정적 처짐 δ_st = 50 mm\nk = mg/δ_st = 5,890 N/m\nf_n = (1/2π)√(k/m) = (1/2π)√(g/δ_st)\n해설집 2.23 Hz, AI 2.229 Hz", fs=10)
    setup(ax, (-3, 3), (-2.8, 7.2), "(a) 교재 Meriam 8/8")
    ax = fig.add_subplot(gs[0, 1])
    body(ax, [(0, -0.12), (8, -0.12), (8, 0.12), (0, 0.12)], fc="#c9ced6")
    for x in (0, 8):
        ax.add_patch(Circle((x, 0), 0.12, fc="white", ec="#333", zorder=7))
    rect(ax, 3.0, 0.12, 2.0, 0.9, fc="#9fb6dd", alpha=0.8)
    label(ax, (4.0, 0.58), "X 빔 몫", fs=9, box=False)
    force(ax, (4.0, 0.12), (0, -0.9), GIVEN, "R = 3.23 N (봉 A, 대기)", push=False, off=(0.15, -0.25), ha="left", fs=10)
    xs = np.linspace(0, 8, 100)
    ax.plot(xs, -0.55 * np.sin(np.pi * xs / 8), color=UNK, ls="--", lw=1.4)
    label(ax, (1.4, -0.95), "처짐 δ_st (M6)", c=UNK, fs=9)
    label(ax, (4.0, 1.6), "Ø8 봉, 받침 사이 163 mm (단순지지 가정)", fs=10, box=False)
    label(ax, (10.0, 0.0), "→", fs=28, box=False)
    body(ax, [(11.2, 1.4), (13.2, 1.4), (13.2, 1.55), (11.2, 1.55)], fc="#c9ced6")
    ys = np.linspace(0.6, 1.4, 100)
    ax.plot(12.2 + 0.25 * np.sin((ys - 0.6) * 2 * math.pi * 4 / 0.8), ys, color="#555")
    rect(ax, 11.6, -0.3, 1.2, 0.9, fc="#9fb6dd")
    label(ax, (12.2, -0.75), "k_eq = R / δ_st", fs=10, box=False)
    setup(ax, (-0.6, 14), (-1.6, 2.2), "(b) 우리: 봉 = 스프링, 빔 몫 = 질량")
    ax = fig.add_subplot(gs[0, 2])
    m10 = R["M10"]
    note(ax, (0.0, 0.98), "f_n = (1/2π)√(g / δ_st)  (8/8과 같은 식)\n\nX 봉 A 대기 δ 0.0072 mm → f_n = %.0f Hz\nX 봉 최악 δ 0.0100 mm → f_n = %.0f Hz\nY 봉 최악 δ 0.0026 mm → f_n = %.0f Hz\n홀더가 말벌 위에 얹힘 (k_c 300~3000): %.0f ~ %.0f Hz\n\n들뜨게 하는 것 = 28BYJ-48 스텝 주파수\n  f_step = rpm × 4096 / 60\n  10 rpm %.0f Hz, 15 rpm %.0f Hz → f_n과 멂\n  공진 띠 %.0f ~ %.0f Hz ↔ %.1f ~ %.1f rpm" % (
        m10["fn_rest"], m10["fn_worst"], m10["fn_yrod"], min(m10["holder_on_contact_Hz"].values()), max(m10["holder_on_contact_Hz"].values()),
        m10["f_step_10_15"][0], m10["f_step_10_15"][1], m10["band_Hz"][0], m10["band_Hz"][1], m10["band_rpm"][0], m10["band_rpm"][1]), fs=10.5)
    setup(ax, (0, 1), (0, 1), "(c) 식과 결과")
    ax = fig.add_subplot(gs[1, :2])
    rpm = np.linspace(0, 16, 400)
    ax.plot(rpm, rpm * 4096 / 60, color="#333", lw=2, label="스텝 주파수 (반 스텝)")
    ax.axhspan(m10["band_Hz"][0], m10["band_Hz"][1], color=GIVEN, alpha=0.15)
    ax.text(10.2, m10["band_Hz"][1] + 15, "X 봉 고유진동수 158~186 Hz (±10 %%)", color=GIVEN, fontsize=10)
    ax.axhline(m10["fn_yrod"], color="#7fb3e6", lw=1.5, ls="--")
    ax.text(10.2, m10["fn_yrod"] + 15, "Y 봉 %.0f Hz" % m10["fn_yrod"], color="#2f6db3", fontsize=10)
    ax.axvspan(m10["band_rpm"][0], m10["band_rpm"][1], color=GIVEN, alpha=0.25)
    ax.text(m10["band_rpm"][1] + 0.2, 60, "피할 속도 %.1f ~ %.1f rpm" % tuple(m10["band_rpm"]), color=GIVEN, fontsize=10)
    ax.axvspan(10, 15, color="#2e8b57", alpha=0.15)
    ax.text(10.1, 820, "운전 속도\n10~15 rpm", color="#2e8b57", fontsize=10)
    ax.set_xlabel("모터 회전수 (rpm)"); ax.set_ylabel("주파수 (Hz)")
    ax.set_xlim(0, 16); ax.set_ylim(0, 1150)
    ax.legend(loc="upper left", fontsize=10)
    ax.set_title("(d) 스텝 주파수와 고유진동수 (공진 지도)", loc="left", fontsize=12, fontweight="bold")
    ax = fig.add_subplot(gs[1, 2])
    note(ax, (0.0, 0.97), "판정: 만족 (운전 10~15 rpm은 공진 띠와 3.7배 이상 떨어짐)\n\n환류 (제어)\n① 순항 속도로 2~3 rpm 쓰지 않기\n② 시동 가속 0.1 s 동안 공진 띠를 빨리 지나감 → 그대로\n③ 찍는 동안은 X·Y 모터 정지 → 점 번짐과 무관\n\n주의 [추측]: 스텝 진동은 주로 축 방향.\n봉의 세로 굽힘을 얼마나 흔드는지는 모름 → 소음·떨림이\n2~3 rpm에서 커지는지 J6에서 같이 확인\n\n유제를 안 풀었다면: M6 처짐 0.01 mm로 '충분'만 보고\n처짐에 숨은 고유진동수(공진 속도)를 놓쳤을 것", fs=10.5)
    setup(ax, (0, 1), (0, 1), "(e) 판정과 환류")
    fig.suptitle("M10  봉의 고유진동수와 스텝 모터 공진 — 동역학(진동) ↔ Meriam 8/8  (M6 처짐에서 이어짐)", fontsize=15, x=0.01, ha="left", fontweight="bold")
    save(fig, os.path.join(OUT, "M10_D5e_고유진동수_공진.jpg"))


if __name__ == "__main__":
    for f in (m7, m8, m9, m10):
        f()
    print("ok")
