# -*- coding: utf-8 -*-
"""S4 ③ 교과서 유제 7개의 자세한 자유물체도 (jpg) — CAP-AI-20
실행: python3 design/calc/s4_fbd_textbook.py → design/img/fbd/T1~T7_*.jpg
교재 그림을 베끼지 않고 주어진 수치로 새로 그림. 값은 s4_textbook_check.py와 같은 식.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fbd_lib import (plt, GIVEN, UNK, FRIC, INER, MOM, DIM, unit, arrow, label, force, dim, angle, moment, triad, ground,  # noqa: E402
                     pin, roller, point, cg, out_of_page, body, rect, note, legend, setup, save, Circle, Polygon)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "img", "fbd")
os.makedirs(OUT, exist_ok=True)
g = 9.81


# ---------------- T1 Riley 9-66 사각나사 프레스 ----------------
def t1():
    W, r, Lead, mu = 400.0, 0.020, 0.100, 0.15
    al = math.degrees(math.atan(Lead / (2 * math.pi * r)))
    ph = math.degrees(math.atan(mu))
    M = W * r * math.tan(math.radians(al + ph))
    fig, axs = plt.subplots(1, 4, figsize=(19, 6.2), gridspec_kw=dict(width_ratios=[0.9, 1.25, 0.8, 1.1]))
    # (a) 공간도
    ax = axs[0]
    body(ax, [(-4, 0), (4, 0), (4, 0.6), (-4, 0.6)], fc="#dfe3ea")                     # 받침
    body(ax, [(-4, 0.6), (-3.4, 0.6), (-3.4, 7), (-4, 7)], fc="#dfe3ea")
    body(ax, [(3.4, 0.6), (4, 0.6), (4, 7), (3.4, 7)], fc="#dfe3ea")
    body(ax, [(-4, 7), (4, 7), (4, 7.8), (-4, 7.8)], fc="#dfe3ea")                     # 위 너트 틀
    for k in range(10):
        y = 2.4 + k * 0.62
        ax.plot([-0.45, 0.45], [y, y + 0.3], color="#555", lw=1)
    body(ax, [(-0.45, 2.2), (0.45, 2.2), (0.45, 9.0), (-0.45, 9.0)], fc="#c9ced6")     # 나사
    body(ax, [(-1.8, 1.4), (1.8, 1.4), (1.8, 2.2), (-1.8, 2.2)], fc="#b9c6dd")         # 누름판
    body(ax, [(-2.2, 0.6), (2.2, 0.6), (2.2, 0.9), (-2.2, 0.9)], fc="#fff3c4")         # 종이
    ax.plot([-3, 3], [9.3, 9.3], color="#555", lw=4)                                    # 손잡이
    moment(ax, (0, 9.3), 1.6, 200, 340, text="M (조이는 모멘트)", toff=(0.6, -0.5))
    force(ax, (0, 1.25), (0, -1.0), GIVEN, "W = 400 N\n(종이가 받는 힘)", push=False, off=(1.9, 0))
    label(ax, (0, -0.8), "사각나사 1줄, r_m = 20 mm\n리드 L = 100 mm, μ = 0.15", fs=10)
    setup(ax, (-5, 5), (-1.6, 10.6), "(a) 공간도 (프레스)")
    # (b) 나사산 한 조각을 펼친 그림 — 조일 때
    ax = axs[1]
    a = math.radians(al)
    Ls = 9.0
    ax.plot([0, Ls * math.cos(a)], [0, Ls * math.sin(a)], color="#555", lw=2)
    ax.plot([0, Ls * math.cos(a)], [0, 0], color=DIM, lw=0.8, ls="--")
    ax.fill([0, Ls * math.cos(a), Ls * math.cos(a)], [0, 0, Ls * math.sin(a)], color="#eef1f6", zorder=0)
    angle(ax, (0, 0), 1.6, 0, al, "α = %.2f°\n(리드각)" % al)
    s0 = 4.0
    base = np.array([s0 * math.cos(a), s0 * math.sin(a)])
    pts = rect(ax, base[0], base[1], 2.2, 1.4, ang=al, fc="#b9c6dd")
    c = (np.array(pts[0]) + np.array(pts[2])) / 2
    label(ax, c, "나사산\n한 조각", fs=9, box=False)
    force(ax, c, (0, -2.2), GIVEN, "W = 400 N", push=False, off=(0.1, -0.35), ha="left")
    force(ax, c, (2.4, 0), UNK, "P = M / r_m", push=False, off=(0.5, 0.35), ha="left")
    n_hat, t_hat = np.array([-math.sin(a), math.cos(a)]), np.array([math.cos(a), math.sin(a)])
    cp = base + t_hat * 1.1                                                              # 접촉점
    force(ax, cp, n_hat * 2.3, UNK, "N", push=False, off=(-0.3, 0.3))
    force(ax, cp, -t_hat * 1.6, FRIC, "μN (아래로: 조각이\n빗면 위로 미끄러짐)", push=False, off=(-1.0, -0.6), fs=9)
    Rdir = np.array([math.cos(math.radians(90 + al + ph)), math.sin(math.radians(90 + al + ph))])
    force(ax, cp, Rdir * 3.2, UNK, "R (N과 μN의 합)", push=False, off=(-1.3, 0.35), ha="center")
    ax.plot([cp[0], cp[0]], [cp[1], cp[1] + 3.2], color=DIM, lw=0.8, ls=":")
    angle(ax, cp, 2.4, 90 + al, 90 + al + ph, "φ = %.2f°" % ph, tr=1.25)
    angle(ax, cp, 1.3, 90, 90 + al + ph, "α+φ", tr=1.45)
    triad(ax, (0.3, 5.6), 1.0)
    note(ax, (0.02, 0.98), "나사가 종이를 누르며 나아가는 것을\n'W를 빗면 위로 밀어 올리는 조각'으로 펼침\n(나사 한 바퀴 = 빗면 2πr_m 가며 L만큼 오름)", fs=9)
    setup(ax, (-0.5, 9.6), (-0.6, 9.3), "(b) 자유물체도: 조일 때 (임박 운동)")
    # (c) 힘 삼각형
    ax = axs[2]
    Wl = 4.0
    Pl = Wl * math.tan(math.radians(al + ph))
    o = np.array([0.5, 5.0])
    arrow(ax, o, o + [0, -Wl], GIVEN)
    label(ax, o + [-0.6, -Wl / 2], "W", c=GIVEN)
    arrow(ax, o + [0, -Wl], o + [Pl, -Wl], UNK)
    label(ax, o + [Pl / 2, -Wl - 0.4], "P = W tan(α+φ)", c=UNK, fs=10)
    arrow(ax, o + [Pl, -Wl], o, UNK)
    label(ax, o + [Pl / 2 + 0.5, -Wl / 2 + 0.3], "R", c=UNK)
    angle(ax, o, 1.0, -90, -90 + (al + ph), "%.2f°" % (al + ph), tr=1.6)
    note(ax, (0.02, 0.24), "M = W r_m tan(α + φ)\n  = 400 × 0.020 × tan %.2f°\n  = %.3f N·m" % (al + ph, M), fs=10)
    setup(ax, (-0.5, 5.5), (-1.3, 5.8), "(c) 힘 삼각형")
    # (d) 풀 때 (M = 0)
    ax = axs[3]
    ax.plot([0, Ls * math.cos(a)], [0, Ls * math.sin(a)], color="#555", lw=2)
    ax.fill([0, Ls * math.cos(a), Ls * math.cos(a)], [0, 0, Ls * math.sin(a)], color="#eef1f6", zorder=0)
    angle(ax, (0, 0), 1.6, 0, al, "α", tr=1.4)
    pts = rect(ax, base[0], base[1], 2.2, 1.4, ang=al, fc="#b9c6dd")
    c = (np.array(pts[0]) + np.array(pts[2])) / 2
    force(ax, c, (0, -2.2), GIVEN, "W", push=False, off=(0.3, -0.2), ha="left")
    force(ax, cp, n_hat * 2.3, UNK, "N", push=False, off=(-0.3, 0.3))
    force(ax, cp, t_hat * 1.6, FRIC, "μN 최대\n(위로)", push=False, off=(0.7, 0.6), fs=9)
    Rdir2 = np.array([math.cos(math.radians(90 + al - ph)), math.sin(math.radians(90 + al - ph))])
    force(ax, cp, Rdir2 * 3.0, UNK, "R 최대 기울기", push=False, off=(0.1, 0.45), fs=9)
    ax.plot([cp[0], cp[0]], [cp[1], cp[1] + 3.2], color=DIM, lw=0.8, ls=":")
    note(ax, (0.02, 0.98), "M = 0이면 W와 R만 남음 → R이 연직이어야 평형\n→ R과 N 사이 각 = α 가 필요\n하지만 마찰이 낼 수 있는 최대각 φ = %.2f° < α = %.2f°\n→ 평형 불가: 저절로 풀림 (자립 안 함)\n풀림을 막는 모멘트 = W r_m tan(α − φ) = %.2f N·m" % (
        ph, al, W * r * math.tan(math.radians(al - ph))), fs=9)
    setup(ax, (-0.5, 9.6), (-0.6, 9.3), "(d) 풀 때: 자립 판정")
    legend(axs[1], ("given", "unk", "fric"), loc=(0.55, 0.0))
    fig.suptitle("T1  Riley·Sturges 2판 문제 9-66 — 사각나사 프레스의 조이는 모멘트와 자립 (→ M1 승강 나사)", fontsize=14, x=0.01, ha="left", fontweight="bold")
    save(fig, os.path.join(OUT, "T1_Riley9-66_나사.jpg"))


# ---------------- T2 Meriam 3/1 ----------------
def t2():
    m, v0, mu = 50.0, 6.0, 0.40
    a = mu * g
    fig, axs = plt.subplots(1, 3, figsize=(16, 5.6), gridspec_kw=dict(width_ratios=[1.1, 0.9, 1.0]))
    ax = axs[0]
    ground(ax, (-4, 0), (5, 0), n=18, h=0.3)
    rect(ax, -1.5, 0, 3, 2.2, fc="#d9c7a3")
    cg(ax, (0, 1.1))
    label(ax, (0.9, 1.75), "50 kg", fs=10, box=False)
    force(ax, (0, 1.1), (0, -2.4), GIVEN, "mg = %.1f N" % (m * g), push=False, off=(0.2, -0.3), ha="left")
    force(ax, (0, 0), (0, 2.6), UNK, "N", push=True, off=(0.35, 0.2), ha="left")
    force(ax, (-0.4, 0), (-2.2, 0), FRIC, "F = μ_k N\n(속도 반대쪽)", push=False, off=(-0.3, 0.55), fs=10)
    arrow(ax, (-1.0, 2.9), (1.4, 2.9), "#2e8b57", lw=1.6, ls="--")
    label(ax, (0.2, 3.3), "v₀ = 6 m/s (속도 — 힘 아님)", c="#2e8b57", fs=9)
    triad(ax, (-3.6, 2.3), 1.0)
    setup(ax, (-4.4, 5.2), (-2.0, 3.8), "(a) 자유물체도")
    ax = axs[1]
    rect(ax, -1.5, 0, 3, 2.2, fc="#d9c7a3", ls="--")
    force(ax, (0, 1.1), (-2.4, 0), INER, "m a  (a = −μ_k g)", push=False, off=(-0.5, 0.45), ls="--")
    label(ax, (-3.3, 1.1), "=", fs=26, box=False)
    setup(ax, (-4.0, 2.4), (-2.0, 3.8), "(b) 운동 그림 (ΣF = m a)")
    ax = axs[2]
    note(ax, (0.02, 0.95), "ΣF_y = 0:  N − mg = 0 → N = %.1f N\n\nΣF_x = m a:  −μ_k N = m a\n→ a = −μ_k g = −%.3f m/s²\n\n멈출 때까지:  0 = v₀ + a t\n→ t = v₀ / (μ_k g) = %.3f s\n\n거리:  0 = v₀² + 2 a x\n→ x = v₀² / (2 μ_k g) = %.3f m\n\n교재·해설집: t = 1.529 s, x = 4.59 m" % (
        m * g, a, v0 / a, v0 ** 2 / (2 * a)), fs=11)
    setup(ax, (0, 1), (0, 1), "(c) 식")
    legend(axs[0], ("given", "unk", "fric", "iner"), loc=(0.62, 0.62))
    fig.suptitle("T2  Meriam·Kraige·Bolton 9판 SI 문제 3/1 — 마찰로 멈추는 상자 (→ M2 이송 시간)", fontsize=14, x=0.01, ha="left", fontweight="bold")
    save(fig, os.path.join(OUT, "T2_Meriam3-1_마찰감속.jpg"))


# ---------------- T3 Meriam 3/2 ----------------
def t3():
    m, th, mus, muk = 50.0, 15.0, 0.20, 0.15
    N = m * g * math.cos(math.radians(th))
    Wt = m * g * math.sin(math.radians(th))
    fig, axs = plt.subplots(1, 2, figsize=(17, 7.2), gridspec_kw=dict(width_ratios=[1.25, 1.0]))
    ax = axs[0]
    a = math.radians(th)
    t_hat, n_hat = np.array([math.cos(a), math.sin(a)]), np.array([-math.sin(a), math.cos(a)])
    L = 11.0
    ax.fill([0, L * math.cos(a), L * math.cos(a)], [0, 0, L * math.sin(a)], color="#eef1f6", zorder=0)
    ax.plot([0, L * math.cos(a)], [0, L * math.sin(a)], color="#555", lw=2)
    ax.plot([0, L], [0, 0], color="#555", lw=1)
    angle(ax, (0, 0), 2.0, 0, th, "15°")
    s0 = 4.0
    b0 = t_hat * s0
    pts = rect(ax, b0[0], b0[1], 3.0, 2.0, ang=th, fc="#d9c7a3")
    G = (np.array(pts[0]) + np.array(pts[2])) / 2
    cg(ax, G)
    force(ax, G, (0, -3.0), GIVEN, "mg = 490.5 N", push=False, off=(0.25, -0.3), ha="left")
    ax.plot(*zip(G, G - n_hat * 2.9), color=GIVEN, lw=1, ls=":")
    ax.plot(*zip(G, G - t_hat * 0.78), color=GIVEN, lw=1, ls=":")
    label(ax, G - n_hat * 2.9 + [0.3, -0.2], "mg cos15° = %.1f" % N, c=GIVEN, fs=9, ha="left")
    label(ax, G - t_hat * 1.5 + n_hat * 0.3, "mg sin15° = %.1f" % Wt, c=GIVEN, fs=9)
    mid_left = (np.array(pts[0]) + np.array(pts[3])) / 2
    force(ax, mid_left, t_hat * 2.6, GIVEN, "P (빗면과 나란히)\n0 / 150 / 300 N", push=True, off=(-0.3, 0.6), fs=10)
    cpt = (np.array(pts[0]) + np.array(pts[1])) / 2
    force(ax, cpt, n_hat * 3.2, UNK, "N", push=True, off=(-0.4, -0.2))
    force(ax, cpt + t_hat * 0.8, t_hat * 2.0, FRIC, "F (방향은 경우마다)", push=False, off=(1.0, -0.5), fs=10)
    triad(ax, (8.0, 0.8), 1.2, a=th, names=("x (빗면 위)", "y"))
    setup(ax, (-0.8, 11.5), (-2.4, 7.2), "(a) 자유물체도 (x: 빗면 위쪽 +)")
    ax = axs[1]
    rows = []
    for P, book in ((0.0, -1.118), (150.0, 0.0), (300.0, 2.04)):
        need = Wt - P                                    # 평형에 필요한 F (위쪽 +)
        if abs(need) <= mus * N:
            acc, Fact, st = 0.0, need, "멈춤 (|F| ≤ μ_s N)"
        else:
            sgn = 1 if P - Wt > 0 else -1
            Fact = -sgn * muk * N
            acc = (P - Wt + Fact) / m
            st = "미끄러짐 → F = μ_k N"
        rows.append((P, need, mus * N, st, Fact, acc, book))
    txt = "N = mg cos15° = %.1f N,  μ_s N = %.1f N,  μ_k N = %.1f N\n\n" % (N, mus * N, muk * N)
    for (P, need, Fm, st, Fact, acc, book) in rows:
        txt += "P = %3.0f N:  평형이면 F = mg sin15° − P = %+.1f N\n   %s\n   F = %+.1f N  →  a = (P − mg sin15° + F)/m = %+.3f m/s²  (교재 %+.3f)\n\n" % (
            P, need, st, Fact, acc, book)
    txt += "순서: ① 멈춰 있다고 놓고 필요한 F를 구함 → ② |F| ≤ μ_s N 이면 멈춤\n③ 넘으면 미끄러지는 방향 반대로 F = μ_k N 을 넣고 ΣF_x = m a"
    note(ax, (0.0, 0.97), txt, fs=10.5)
    setup(ax, (0, 1), (0, 1), "(b) 세 경우 (정지 마찰 검사 → 운동 마찰)")
    legend(axs[0], ("given", "unk", "fric"), loc=(0.0, 0.72))
    fig.suptitle("T3  Meriam 9판 SI 문제 3/2 — 빗면 위 상자: 움직이기 시작하는가, 가속도는 (→ M2 추력·출발)", fontsize=14, x=0.01, ha="left", fontweight="bold")
    save(fig, os.path.join(OUT, "T3_Meriam3-2_빗면마찰.jpg"))


# ---------------- T4 Riley 6-49 ----------------
def t4():
    W, R, hb, th = 300.0, 9.0, 3.0, 20.0
    a = math.radians(th)
    s_hat, n_hat = np.array([math.cos(a), math.sin(a)]), np.array([-math.sin(a), math.cos(a)])
    beta = math.acos((R - hb) / R)
    O = np.array([0.0, 0.0])
    A = O - R * n_hat
    d = R * math.sin(beta)
    B = O - (R - hb) * n_hat + d * s_hat
    u = (O - B) / np.linalg.norm(O - B)
    RB = W / u[1]
    P = -RB * u[0]
    fig, axs = plt.subplots(1, 2, figsize=(16.5, 8), gridspec_kw=dict(width_ratios=[1.35, 1.0]))
    ax = axs[0]
    p0, p1 = A - s_hat * 10, A + s_hat * 16
    ax.fill([p0[0], p1[0], p1[0]], [p0[1], p0[1], p1[1]], color="#eef1f6", zorder=0)
    ax.plot(*zip(p0, p1), color="#555", lw=2)
    ax.plot([p0[0], p1[0]], [p0[1], p0[1]], color="#555", lw=1)
    angle(ax, p0, 3.0, 0, th, "20°")
    blk = [B, B + s_hat * 5, B + s_hat * 5 - n_hat * hb, B - n_hat * hb]
    body(ax, blk, fc="#e3d3b0")
    ax.add_patch(Circle(tuple(O), R, fc="#dfe3ea", ec="#222", lw=1.6, zorder=1))
    point(ax, O, "O", off=(-1.0, 0.6))
    point(ax, A, "A", off=(-1.2, -0.6))
    point(ax, B, "B", off=(0.5, 0.7))
    force(ax, O, (0, -6.0), GIVEN, "W = 300 lb", push=False, off=(0.4, -0.5), ha="left")
    force(ax, O, (-6.0, 0), UNK, "P", push=True, off=(-0.6, 0.5))
    force(ax, B, (O - B) * 0.75, UNK, "R_B (모서리 → 중심)", push=False, off=(1.6, 1.0), fs=10)
    force(ax, A, n_hat * 3.0, "#999999", "A = 0 (넘어가기 시작)", push=True, off=(-0.5, -0.8), ls="--", fs=9)
    dim(ax, O, O - R * n_hat, "r = 9 in", off=-1.2, fs=9)
    dim(ax, B, B - n_hat * hb, "3 in", off=-1.0, fs=9)
    ax.plot(*zip(O, O - (R - hb) * n_hat), color=DIM, lw=0.8, ls=":")
    ax.plot(*zip(O - (R - hb) * n_hat, B), color=DIM, lw=0.8, ls=":")
    label(ax, O - (R - hb) * n_hat * 0.5 + s_hat * -0.9, "9 − 3 = 6 in", c=DIM, fs=9)
    label(ax, O - (R - hb) * n_hat + s_hat * d * 0.5 + n_hat * -0.6, "d = 9 cos α = %.3f in" % d, c=DIM, fs=9)
    ang_s = math.degrees(math.atan2(*(B - O)[::-1]))
    angle(ax, O, 3.2, ang_s, math.degrees(math.atan2(*(-n_hat)[::-1])) + 360 if ang_s > 0 else math.degrees(math.atan2(*(-n_hat)[::-1])), "", tr=1.3)
    label(ax, O + np.array([1.8, -2.6]), "α = sin⁻¹(6/9)\n= %.2f°" % math.degrees(math.asin((R - hb) / R)), c=DIM, fs=9)
    moment(ax, B, 1.6, 120, 300, text="ΣM_B = 0", toff=(1.2, -0.4))
    triad(ax, (-11, 6), 1.6)
    setup(ax, (-14, 14), (-13, 10), "(a) 자유물체도 (넘어가기 시작하는 순간)")
    ax = axs[1]
    note(ax, (0.0, 0.97), "임박 조건: 빗면 반력 A = 0 (원기둥이 빗면에서 뜨기 시작)\n→ 힘은 W, P, R_B 세 개뿐 — R_B는 중심 O를 지남 (매끄러운 접촉)\n\nΣM_B = 0 (B 기준, 반시계 +):\n P sin20°·d − P cos20°·6 + W sin20°·6 + W cos20°·d = 0\n P (%.4f − %.4f) = −300 (%.4f + %.4f)\n → P = %.1f lb  (해설집 750 lb)\n\n같은 값을 힘 평형으로:  R_B의 방향 u = (O − B)/|O − B|\n ΣF_y: R_B u_y − W = 0 → R_B = %.1f lb\n ΣF_x: P − R_B u_x = 0 → P = %.1f lb\n\n→ 우리 문제(M3): '접촉 반력이 0이 되는 순간이 한계'\n   원기둥 A = 0 ↔ 말벌이 격자에서 떨어짐 R_g = 0" % (
        math.sin(a) * d, math.cos(a) * 6, math.sin(a) * 6, math.cos(a) * d, P, RB, P), fs=10.5)
    setup(ax, (0, 1), (0, 1), "(b) 식")
    legend(axs[0], ("given", "unk"), loc=(0.0, 0.0))
    fig.suptitle("T4  Riley·Sturges 2판 문제 6-49 — 턱을 넘기는 힘: 접촉 반력 0 조건 (→ M3 찍는 힘 한계)", fontsize=14, x=0.01, ha="left", fontweight="bold")
    save(fig, os.path.join(OUT, "T4_Riley6-49_접촉반력0.jpg"))


# ---------------- T5 Riley 6-41 ----------------
def t5():
    Pm, ang = 30.0, 30.0
    A, B, C = np.array([0, 0.0]), np.array([4, 5.5]), np.array([4, 11.0])
    Q = (Pm * math.cos(math.radians(ang)) * 11 + Pm * math.sin(math.radians(ang)) * 4) / 5.5
    Ax, Ay = Q - Pm * math.cos(math.radians(ang)), Pm * math.sin(math.radians(ang))
    fig, axs = plt.subplots(1, 2, figsize=(15.5, 8.4), gridspec_kw=dict(width_ratios=[1.15, 1.0]))
    ax = axs[0]
    path = [A, B, np.array([5.6, 8.4]), np.array([5.8, 9.8]), np.array([5.2, 10.8]), C]
    ax.plot(*zip(*path), color="#888", lw=9, solid_capstyle="round", zorder=1)
    ax.plot(*zip(*path), color="#c9ced6", lw=6.5, solid_capstyle="round", zorder=1)
    ax.add_patch(Polygon([C + [-1.1, 0.5], C + [0.2, 1.3], C + [0.7, 0.5], C + [-0.6, -0.3]], closed=True, fc="#333", zorder=2))
    pin(ax, A, s=0.9)
    for p, nme, off in ((A, "A", (-0.9, 0.3)), (B, "B", (0.5, -0.5)), (C, "C", (0.9, 0.5))):
        point(ax, p, nme, off=off)
    Pv = np.array([math.cos(math.radians(-ang)), math.sin(math.radians(-ang))])
    force(ax, C, Pv * 3.2, GIVEN, "P = 30 lb", push=True, off=(-0.9, 0.7))
    ax.plot([C[0] - 3.6, C[0]], [C[1], C[1]], color=DIM, lw=0.8, ls=":")
    angle(ax, C, 2.2, 180 - ang, 180, "30°", tr=1.3)
    force(ax, C, (Pv[0] * 2.7, 0), GIVEN, None, push=True, ls="--", lw=1.5)
    label(ax, C + [-1.4, -0.4], "P cos30° = %.2f" % (Pm * math.cos(math.radians(ang))), c=GIVEN, fs=9)
    force(ax, C, (0, Pv[1] * 2.7), GIVEN, None, push=True, ls="--", lw=1.5)
    label(ax, C + [0.25, 1.9], "P sin30° = %.1f" % (Pm * math.sin(math.radians(ang))), c=GIVEN, fs=9, ha="left")
    force(ax, B, (-3.0, 0), UNK, "Q (브레이크 실린더)", push=False, off=(-0.4, 0.55))
    force(ax, A, (2.4, 0), UNK, "A_x", push=False, off=(0.4, -0.45))
    force(ax, A, (0, 2.4), UNK, "A_y", push=False, off=(-0.55, 0.2))
    dim(ax, A, A + [4, 0], "4 in", off=-1.6)
    dim(ax, A + [-2.2, 0], A + [-2.2, 5.5], "5½ in", off=0.0)
    dim(ax, A + [-2.2, 5.5], A + [-2.2, 11], "5½ in", off=0.0)
    moment(ax, A, 1.3, 30, 160, text="ΣM_A = 0", toff=(-0.5, 0.6))
    triad(ax, (6.5, 0.5), 1.1)
    setup(ax, (-4.2, 8.5), (-2.5, 13.2), "(a) 자유물체도 (페달 전체)")
    ax = axs[1]
    note(ax, (0.0, 0.97), "ΣM_A = 0 (반시계 +):\n −(P cos30°)(11) − (P sin30°)(4) + Q (5.5) = 0\n → Q = (%.2f × 11 + 15 × 4) / 5.5 = %.2f lb\n\nΣF_x = 0:  A_x + P cos30° − Q = 0 → A_x = %.2f lb\nΣF_y = 0:  A_y − P sin30° = 0 → A_y = %.2f lb\n|A| = %.2f lb,  방향 tan⁻¹(A_y/A_x) = %.2f°\n(해설집: Q = 62.87 lb, A = 39.82 lb ∠ 22.13°)\n\n→ 우리 문제(M4): 핀 A = 서보 축, 페달 = 혼\n   ΣM_축 = 0 → 서보 토크 T = (혼 끝 힘) × (축까지 수직 거리)\n   팔 길이는 '힘의 작용선까지 수직 거리'로 잼 (각도에 따라 변함)" % (
        Pm * math.cos(math.radians(ang)), Q, Ax, Ay, math.hypot(Ax, Ay), math.degrees(math.atan2(Ay, Ax))), fs=10.5)
    setup(ax, (0, 1), (0, 1), "(b) 식")
    legend(axs[0], ("given", "unk"), loc=(0.62, 0.0))
    fig.suptitle("T5  Riley·Sturges 2판 문제 6-41 — 브레이크 페달: 핀에 대한 모멘트 평형 (→ M4 펜 들기 서보)", fontsize=14, x=0.01, ha="left", fontweight="bold")
    save(fig, os.path.join(OUT, "T5_Riley6-41_레버모멘트.jpg"))


# ---------------- T6 Riley 9-43 ----------------
def t6():
    Wd, mu, mub, w, Ld, ah, gap = 2.0, 0.60, 0.10, 30.0, 18.0, 3.0, 0.75
    th = math.asin(gap / Ld)
    a_arm = (w - ah) * math.cos(th)
    b_arm = w * math.cos(th) + Ld * math.sin(th)
    d_arm = Ld * math.cos(th) - w * math.sin(th)
    den = 2 * mu * a_arm - d_arm - mu * b_arm
    N = mub * Wd * (b_arm / 2 - a_arm) / den
    P = mub * Wd + 2 * mu * N
    fig, axs = plt.subplots(1, 2, figsize=(18, 8.6), gridspec_kw=dict(width_ratios=[1.3, 1.0]))
    ax = axs[0]
    te = math.radians(6.0)                                      # 그림만 6°로 과장
    R = np.array([[math.cos(te), -math.sin(te)], [math.sin(te), math.cos(te)]])
    FL = np.array([0.0, 0.0])                                   # 앞 왼쪽 모서리 (그림 기준)
    corners = [FL, FL + R @ [w, 0], FL + R @ [w, Ld], FL + R @ [0, Ld]]
    xs = [c_[0] for c_ in corners]
    xL, xR = min(xs), max(xs)
    for xw in (xL, xR):
        ax.add_patch(plt.Rectangle((xw - 1.2 if xw == xL else xw, -3), 1.2, 25, fc="#d8cdb8", ec="#8a7a5c", zorder=0))
    body(ax, corners, fc="#f3ead7")
    Apt, Bpt = corners[3], corners[1]                           # 뒤 왼쪽 A, 앞 오른쪽 B
    point(ax, Apt, "A", off=(-1.6, 0.5))
    point(ax, Bpt, "B", off=(0.6, -0.9))
    H = FL + R @ [ah, 0]                                         # 손잡이
    point(ax, H, None)
    label(ax, H + [-0.2, 1.2], "손잡이", fs=9, box=False)
    force(ax, H, (0, -5.0), GIVEN, "P (당기는 힘)", push=False, off=(0.3, -0.3), ha="left")
    force(ax, Apt, (3.0, 0), UNK, "A_n", push=True, off=(-1.9, 0.0))
    force(ax, Apt, (0, 3.2), FRIC, "A_f = 0.6 A_n\n+ 0.1 (W/2)", push=False, off=(0.3, 0.6), fs=9, ha="left")
    force(ax, Bpt, (-3.0, 0), UNK, "B_n", push=True, off=(1.9, 0.0))
    force(ax, Bpt, (0, 3.2), FRIC, "B_f = 0.6 B_n\n+ 0.1 (W/2)", push=False, off=(0.6, 0.6), fs=9, ha="left")
    Gc = FL + R @ [w / 2, Ld / 2]
    out_of_page(ax, Gc, r=0.45, inward=True, text="W = 2 lb (지면 안쪽, 바닥 레일 둘이 1 lb씩)", off=(0.7, 0))
    moment(ax, Bpt, 2.0, 100, 200, text="ΣM_B", toff=(-0.6, 0.5))
    ax.annotate("", xy=(xR, 21.5), xytext=(xR - 0.0 + 1.2, 21.5), arrowprops=dict(arrowstyle="<->", color=DIM))
    label(ax, (xR + 1.6, 22.2), "틈 0.75 in", c=DIM, fs=9)
    dim(ax, (H[0], -4.0), (Bpt[0], -4.0), "a = 27 cos θ = %.2f in" % a_arm, off=0, fs=9)
    dim(ax, (Apt[0], 24.0), (Bpt[0], 24.0), "b = %.2f in" % b_arm, off=0, fs=9)
    dim(ax, (Bpt[0] + 3.2, Bpt[1]), (Bpt[0] + 3.2, Apt[1]), "d = %.2f in" % d_arm, off=0, fs=9, rot=90)
    label(ax, FL + R @ [w / 2, -1.2], "폭 30 in (손잡이 간격 24, 양옆 3)", c=DIM, fs=9)
    label(ax, FL + R @ [w + 1.5, Ld / 2], "깊이 18 in", c=DIM, fs=9, rot=90)
    triad(ax, (-6, 14), 1.8, names=("x", "y (안쪽)"))
    label(ax, (12, -8.5), "위에서 본 그림 · 기울기 θ는 그림에서 6°로 과장 (해설집 θ = sin⁻¹(0.75/18) = 2.39°, 정확히는 2.48°)", fs=9, c="#555")
    setup(ax, (-9, 37), (-10, 26), "(a) 자유물체도 (서랍, 위에서 봄)")
    ax = axs[1]
    note(ax, (0.0, 0.97), "대각 두 모서리만 옆면에 닿음 (A: 뒤 왼쪽, B: 앞 오른쪽)\n임박 운동: 옆면 마찰 0.6 N, 바닥 레일 마찰 0.1 × (W/2)\n\nΣF_x = 0:  A_n − B_n = 0 → A_n = B_n = N\nΣF_y = 0:  A_f + B_f − P = 0 → P = 0.2 + 1.2 N\nΣM_B = 0:  P·a − A_n·d − A_f·b = 0\n→ N (2μa − d − μb) = 0.1 W (b/2 − a)\n→ N = %.4f lb,  P = %.3f lb  (해설집 1.202 lb)\n\n끼임 조건: 2μa − d − μb ≥ 0 → μ ≥ d / (2a − b) = %.2f\n기울기를 무시(θ = 0)하면 μ_c = 18/24 = 0.75, P = 1.000 lb (−17 %%)\n→ 끼임 근처에서는 기하를 정확히 넣어야 함\n\n→ 우리 문제(M5): 손잡이 = X 나사(봉 A 선 위), 옆면 = 봉,\n   서랍 깊이 = 부싱 길이 L, 폭 = 봉 간격 d\n   손잡이를 옆면 위로 옮긴 꼴(a_h = 0)이면 μ_c = L / d" % (N, P, d_arm / (2 * a_arm - b_arm)), fs=10.5)
    setup(ax, (0, 1), (0, 1), "(b) 식 (해설집 기하 그대로)")
    legend(axs[0], ("given", "unk", "fric"), loc=(0.0, 0.0))
    fig.suptitle("T6  Riley·Sturges 2판 문제 9-43 — 손잡이 하나로 당기는 서랍의 끼임 (→ M5 한쪽 구동 X 빔, 펜 홀더 안내)", fontsize=14, x=0.01, ha="left", fontweight="bold")
    save(fig, os.path.join(OUT, "T6_Riley9-43_서랍끼임.jpg"))


# ---------------- T7 Gere 9.3-1 ----------------
def t7():
    P, L, a, E, I = 45e3, 3.0, 2.1, 200e9, 9800e-8
    b = L - a
    RA, RB = P * b / L, P * a / L
    x1 = math.sqrt((L ** 2 - b ** 2) / 3)
    dmax = P * b * (L ** 2 - b ** 2) ** 1.5 / (9 * math.sqrt(3) * L * E * I)
    thA = P * a * b * (L + b) / (6 * L * E * I)
    fig = plt.figure(figsize=(16, 12.5))
    gs = fig.add_gridspec(4, 2, width_ratios=[1.55, 1.0], height_ratios=[1.25, 0.8, 0.8, 0.95], hspace=0.38)
    ax = fig.add_subplot(gs[0, 0])
    body(ax, [(0, -0.12), (L, -0.12), (L, 0.12), (0, 0.12)], fc="#c9ced6")
    pin(ax, (0, -0.12), s=0.22)
    roller(ax, (L, -0.12), s=0.22)
    point(ax, (0, 0), "A", off=(-0.18, 0.28))
    point(ax, (L, 0), "B", off=(0.15, 0.28))
    force(ax, (a, 0.12), (0, -0.75), GIVEN, "P = 45 kN", push=True, off=(0.25, 0.25), ha="left")
    force(ax, (0, -0.4), (0, 0.6), UNK, "R_A = Pb/L = %.1f kN" % (RA / 1e3), push=False, off=(0.1, 0.75), fs=10, ha="left")
    force(ax, (L, -0.4), (0, 0.6), UNK, "R_B = Pa/L = %.1f kN" % (RB / 1e3), push=False, off=(-0.1, 0.75), fs=10, ha="right")
    dim(ax, (0, -0.85), (a, -0.85), "a = 2.1 m", off=0)
    dim(ax, (a, -0.85), (L, -0.85), "b = 0.9 m", off=0)
    dim(ax, (0, -1.15), (L, -1.15), "L = 3.0 m", off=0)
    triad(ax, (-0.45, 0.5), 0.25)
    setup(ax, (-0.6, 3.6), (-1.35, 1.25), "(a) 자유물체도 (보 전체, 자중 무시)")
    ax.set_aspect("auto")
    ax = fig.add_subplot(gs[1, 0])
    ax.fill_between([0, a, a, L], [RA / 1e3, RA / 1e3, -RB / 1e3, -RB / 1e3], 0, step=None, color="#9fb6dd", alpha=0.8)
    ax.axhline(0, color="#333", lw=1)
    ax.set_xlim(-0.2, 3.2); ax.set_ylabel("V (kN)")
    ax.text(a / 2, RA / 1e3 + 2, "+%.1f" % (RA / 1e3), ha="center"); ax.text((a + L) / 2, -RB / 1e3 - 5, "−%.1f" % (RB / 1e3), ha="center")
    ax.set_title("(b) 전단력 선도", loc="left", fontsize=12, fontweight="bold"); ax.set_ylim(-40, 22)
    ax = fig.add_subplot(gs[2, 0])
    Mmax = P * a * b / L / 1e3
    ax.fill([0, a, L], [0, Mmax, 0], color="#f1c27d", alpha=0.85)
    ax.axhline(0, color="#333", lw=1)
    ax.text(a, Mmax + 2, "M_max = Pab/L = %.2f kN·m (하중 아래)" % Mmax, ha="center")
    ax.set_xlim(-0.2, 3.2); ax.set_ylim(0, 40); ax.set_ylabel("M (kN·m)")
    ax.set_title("(c) 굽힘 모멘트 선도", loc="left", fontsize=12, fontweight="bold")
    ax = fig.add_subplot(gs[3, 0])
    xs = np.linspace(0, L, 400)
    v = np.where(xs <= a, -P * b * xs * (L ** 2 - b ** 2 - xs ** 2) / (6 * L * E * I),
                 -P * a * (L - xs) * (L ** 2 - a ** 2 - (L - xs) ** 2) / (6 * L * E * I))
    ax.plot(xs, v * 1e3, color=UNK, lw=2)
    ax.axhline(0, color="#333", lw=1)
    ax.plot([x1], [-dmax * 1e3], "o", color=UNK)
    ax.annotate("δ_max = %.3f mm\nx₁ = √((L² − b²)/3) = %.3f m" % (dmax * 1e3, x1), xy=(x1, -dmax * 1e3), xytext=(x1 - 1.1, -0.55),
                arrowprops=dict(arrowstyle="->", color="#333"))
    ax.plot([0, 0.6], [0, -thA * 0.6 * 1e3], color="#888", ls="--")
    ax.text(0.62, -thA * 0.6 * 1e3, "θ_A = %.2e rad" % thA, va="center")
    ax.set_xlim(-0.2, 3.2); ax.set_ylim(-1.3, 0.2); ax.set_xlabel("x (m)"); ax.set_ylabel("v (mm)")
    ax.set_title("(d) 처짐 곡선 (예제 9-3 식, E = 200 GPa)", loc="left", fontsize=12, fontweight="bold")
    ax = fig.add_subplot(gs[:, 1])
    hI, bI, tw, tf = 300, 125, 10.8, 16.2
    sc = 1 / 60
    pts = [(-bI / 2, -hI / 2), (bI / 2, -hI / 2), (bI / 2, -hI / 2 + tf), (tw / 2, -hI / 2 + tf), (tw / 2, hI / 2 - tf), (bI / 2, hI / 2 - tf),
           (bI / 2, hI / 2), (-bI / 2, hI / 2), (-bI / 2, hI / 2 - tf), (-tw / 2, hI / 2 - tf), (-tw / 2, -hI / 2 + tf), (-bI / 2, -hI / 2 + tf)]
    body(ax, [(x * sc, y * sc + 6.2) for x, y in pts], fc="#c9ced6")
    label(ax, (0, 6.2 + 3.1), "IPN 300 단면 (강축 굽힘)\nh 300, b 125, I = 9,800 cm⁴", fs=10)
    note(ax, (0.0, 0.62), "주어진 것: L = 3 m, a = 2.1 m, b = 0.9 m, P = 45 kN\nIPN 300 (부록) I = 9,800 cm⁴ = 9.8 × 10⁻⁵ m⁴\n문제에 E 없음 → 정답은 E = 200 GPa일 때 나옴\n(210 GPa로 풀면 δ_max 0.986 mm, −5 %%)\n\nδ_max = P b (L² − b²)^{3/2} / (9√3 L E I) = %.3f mm\nθ_A = P a b (L + b) / (6 L E I) = %.2e rad\n(교재 1.04 mm, 9.4 × 10⁻⁴ rad)\n\n해설집은 미국판 수치 (L 10 ft, P 10 kip,\nI 285 in⁴, E 29,000 ksi) → 0.0349 in, 7.93 × 10⁻⁴ rad\n같은 식으로 재현 (0.08 %%)\n\n→ 우리 문제(M6): a = b = L/2 (움직이는 하중의\n   최악 위치) → δ = PL³/48EI, 원형 단면 I = πd⁴/64" % (dmax * 1e3, thA), fs=10.5)
    setup(ax, (-3, 3), (0, 10.5), "(e) 단면과 식")
    fig.suptitle("T7  Gere·Goodno 9판 SI 문제 9.3-1 — 단순보 집중하중의 처짐 (→ M6 봉 처짐)", fontsize=14, x=0.01, ha="left", fontweight="bold")
    save(fig, os.path.join(OUT, "T7_Gere9.3-1_단순보처짐.jpg"))


if __name__ == "__main__":
    for f in (t1, t2, t3, t4, t5, t6, t7):
        f()
    print("ok", sorted(os.listdir(OUT)))
