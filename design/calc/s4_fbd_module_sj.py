# -*- coding: utf-8 -*-
"""S4 M1~M6 우리 문제 자유물체도 (D5e) — 승준이 서현 CAP-AI-20 '남은 일 3번'을 이어서 (CAP-AI-SJ-29)
실행: python3 design/calc/s4_fbd_module_sj.py → design/img/fbd/M1~M6_D5e_*.jpg
값은 s4_calc_d5e_sj.py(run)에서 읽음. 그림 규칙은 fbd_lib(서현)과 같음: 받침·닿는 물체는 떼어 내고 반력으로,
빨강 = 주어진 힘, 파랑 = 구하는 힘·반력, 주황 = 마찰, 보라 점선 = 관성력, 초록 = 모멘트·토크, 회색 = 치수·떼어 낸 물체.
화살표 머리가 작용점에 닿으면 미는 힘, 꼬리가 작용점에 있으면 당기는 힘.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fbd_lib import (plt, GIVEN, UNK, FRIC, INER, MOM, DIM, unit, label, force, dim, angle, moment, triad,  # noqa: E402
                     point, cg, out_of_page, body, rect, note, legend, setup, save, Circle)
from matplotlib.patches import Ellipse                          # noqa: E402
import s4_calc_d5e_sj as C5                                     # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "img", "fbd")
os.makedirs(OUT, exist_ok=True)
R = C5.run()
P = C5.P
TITLE = dict(fontsize=14, x=0.01, ha="left", fontweight="bold")


def cut(ax, x0, x1, y0, y1):
    """떼어 낸 물체 자리 (회색 점선 테두리)"""
    ax.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], color="#999", lw=1.0, ls="--", zorder=0)


def textpanel(ax, title):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(title, fontsize=12, loc="left", fontweight="bold")


# ======================================================================= M1
def m1():
    r = R["M1"]
    cons = r["회전 막이 + 기울어짐 짝힘 (보수적)"]
    base = r["서현 r2와 같은 식 (안내봉 마찰 없음)"]
    mid = r["회전 막이만 (F_g = T/26)"]
    ms = r["_mass"]
    fig = plt.figure(figsize=(21, 12))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.45, 0.85, 1.0], height_ratios=[1, 0.62], hspace=0.10, wspace=0.08)
    # (a) 캐리지 + 너트, 옆에서 (y–z). 원점: 캐리지 아래 면, y는 전역 y
    ax = fig.add_subplot(gs[0, 0])
    rect(ax, -20, 0, 40, 12, fc="#e8ecf3")
    rect(ax, -24, -3.5, 22, 3.5, fc="#f5e3b3")                       # 너트 플랜지 (황동)
    rect(ax, -18.1, 0, 10.2, 11.5, fc="#f5e3b3", ls=":", alpha=0.7)    # 너트 몸통 (캐리지 구멍 안)
    label(ax, (-26, -1.8), "159 T8 너트\n(캐리지에 나사 4개)", fs=9, c="#7a5c00", ha="right")
    label(ax, (5.5, 3.0), "158 캐리지 (PLA, 두께 12)", fs=9, box=False)
    cut(ax, -15, -11, -14, -3.5)
    label(ax, (-13, -16.0), "나사 155 (떼어 냄)", fs=8.5, c="#777")
    cut(ax, 11, 15, -9, 22)
    label(ax, (13, 23.6), "안내봉 157 Ø4 (떼어 냄)", fs=8.5, c="#777")
    cut(ax, -6, 6, 12, 18)
    label(ax, (-12, 17.5), "로드셀 148 (떼어 냄)", fs=8.5, c="#777")
    force(ax, (-13, -3.5), (0, 9), UNK, None, push=True)
    label(ax, (-24, -10.5), "F_n (너트 추력)\n= %.3f N" % cons["F"], c=UNK, fs=10)
    force(ax, (0, 12), (0, -8), GIVEN, None, push=True)
    label(ax, (2.0, 26.5), "F_up = W_위 + F_p = %.3f + %.1f = %.3f N\n(로드셀이 캐리지를 누름, y 0)" % (
        ms["m_upper"] / 1000 * 9.81, P["F_press"], cons["F_up"]), c=GIVEN, fs=9.5)
    ycg = ms["cg_carriage"][1]
    cg(ax, (ycg, 6.0), r=0.9, name=None)
    force(ax, (ycg, 6.0), (0, -8.5), GIVEN, None, push=False)
    label(ax, (ycg + 4.5, -6.0), "W_c = %.3f N" % cons["W_c"], c=GIVEN, fs=10)
    # 안내봉 짝힘: 하중이 나사 축 오른쪽(+y) → 시계 방향 기울임 → 캐리지 위는 +y, 아래는 −y로 감
    # → 위: 구멍 왼쪽 벽이 봉에 닿음, 봉이 캐리지를 −y로 밂 / 아래: 구멍 오른쪽 벽, 봉이 +y로 밂
    force(ax, (11, 11.0), (-5.5, 0), UNK, None, push=True)
    label(ax, (19.5, 13.6), "N_p", c=UNK, fs=10)
    force(ax, (15, 1.0), (5.5, 0), UNK, None, push=True)
    label(ax, (24.0, -1.6), "N_p = %.3f N" % cons["N_p"], c=UNK, fs=10)
    force(ax, (15, 11.0), (0, -6), FRIC, None, push=False)
    force(ax, (11, 1.0), (0, -6), FRIC, None, push=False)
    label(ax, (24.5, 5.6), "μ_g N_p ×2 (아래로)", c=FRIC, fs=9.5)
    out_of_page(ax, (13, 6.5), r=0.9, c=UNK)
    label(ax, (26.0, 16.2), "⊙ F_g = T/26 (회전 막이, x 방향)", c=UNK, fs=9.5)
    dim(ax, (-13, -21), (0, -21), "13", off=0)
    dim(ax, (0, -21), (13, -21), "13", off=0)
    dim(ax, (34, 0), (34, 12), "L_c = 12", off=0, rot=90)
    moment(ax, (-13, 6), 4.0, 150, 30, col=MOM)
    label(ax, (-13, 12.8), "ΣM_나사축", c=MOM, fs=9)
    triad(ax, (-40, 21), 4, names=("y", "z"))
    setup(ax, (-44, 40), (-25, 31), "(a) 캐리지 + 너트 — 옆에서 (y–z), 바닥 올리는 중")
    # (b) 위에서 (x–y): 회전 막이
    ax = fig.add_subplot(gs[0, 1])
    rect(ax, -18, -20, 36, 40, fc="#e8ecf3")
    ax.add_patch(Circle((0, -13), 4.0, fc="white", ec="#999", ls="--", lw=1.0, zorder=2))
    ax.add_patch(Circle((0, 13), 2.0, fc="white", ec="#999", ls="--", lw=1.0, zorder=2))
    label(ax, (9.5, -9.0), "나사 축", fs=8.5, c="#777", box=False)
    moment(ax, (0, -13), 6.5, -40, 220, col=MOM)
    label(ax, (0, -26.5), "T (나사가 너트·캐리지를 돌리려 함, 반시계)", c=MOM, fs=9.5)
    force(ax, (2.0, 13), (8, 0), UNK, None, push=False)
    label(ax, (7, 17.5), "F_g = T / 26 = %.3f N" % cons["F_g"], c=UNK, fs=9.5)
    dim(ax, (-23, -13), (-23, 13), "26", off=0, rot=90)
    triad(ax, (-28, 18), 4)
    setup(ax, (-32, 30), (-30, 25), "(b) 위에서 (x–y) — 회전 막이")
    # (c) 나사산 조각 (펼친 빗면)
    ax = fig.add_subplot(gs[0, 2])
    lam, phi = cons["lead_angle_deg"], cons["fric_angle_deg"]
    a = math.radians(lam)
    t_hat, n_hat = np.array([math.cos(a), math.sin(a)]), np.array([-math.sin(a), math.cos(a)])
    Ls = 13.0
    ax.fill([0, Ls * math.cos(a), Ls * math.cos(a)], [0, 0, Ls * math.sin(a)], color="#eef1f6", zorder=0)
    ax.plot([0, Ls * math.cos(a)], [0, Ls * math.sin(a)], color="#555", lw=2)
    ax.plot([0, Ls * math.cos(a)], [0, 0], color=DIM, lw=0.8, ls="--")
    label(ax, (9.5, 0.8), "나사 (떼어 냄)", fs=8.5, c="#777", box=False)
    b0 = t_hat * 5.0
    body(ax, [b0, b0 + t_hat * 3.4, b0 + t_hat * 3.4 + n_hat * 2.0, b0 + n_hat * 2.0], fc="#f5e3b3")
    c0 = b0 + t_hat * 1.7
    top = c0 + n_hat * 2.0
    force(ax, top, (0, -3.0), GIVEN, None, push=True)
    label(ax, top + [0.2, 3.7], "F = %.3f N (너트가 들 짐)" % cons["F"], c=GIVEN, fs=10)
    left = b0 + n_hat * 1.0
    force(ax, left, (3.2, 0), UNK, None, push=True)
    label(ax, left + [-4.3, 0.6], "Q = 2T / d_m", c=UNK, fs=10)
    force(ax, c0, n_hat * 2.8, UNK, None, push=True)
    label(ax, c0 - n_hat * 2.8 + [0.9, -0.3], "N", c=UNK, fs=10)
    force(ax, c0 + t_hat * 0.9, -t_hat * 2.6, FRIC, None, push=False)
    label(ax, (2.2, 3.6), "μ′N  (μ′ = μ sec α)", c=FRIC, fs=9.5)
    angle(ax, (0, 0), 3.2, 0, lam, "λ = %.1f°" % lam, tr=1.35)
    d_res = unit(90 + lam + phi)
    ax.plot(*zip(c0 - d_res * 3.2, c0 + d_res * 1.2), color=DIM, lw=0.9, ls=":")
    angle(ax, c0, 2.2, 90 + lam, 90 + lam + phi, "φ′ = %.2f°" % phi, tr=1.6)
    setup(ax, (-1.0, 14.0), (-2.5, 11.0), "(c) 나사산 한 조각 (펼친 빗면, 올림)")
    # (d) 식
    ax = fig.add_subplot(gs[1, :])
    txt = ("주어진 것 (D5e, FreeCAD 부피 × 밀도): 바닥 묶음 %.1f g (위 %.1f g + 캐리지·너트 %.1f g — r2보다 +%.1f g, 황동 T8 너트가 모델에 들어감), F_p = 0.5 N (가정, R7 미정)\n"
           "나사 Tr8×8: d_m 7, 리드 8 → λ = %.2f°,  μ 0.15 → φ′ = arctan(μ sec 15°) = %.2f°,  T = k_T F,  k_T = (d_m/2)(l + πμd_m sec α)/(πd_m − μl sec α) = %.3f mm\n"
           "① 서현 r2 식 (안내봉 마찰 없음): F_n = F_up + W_c = %.3f N → T = %.2f N·mm, 안전율 34.3 / T = %.1f\n"
           "② + 회전 막이 (서현 CAP-AI-20): ΣM_z: T = F_g × 26 → F_n = (F_up + W_c) / (1 − μ_g k_T / 26) = %.3f N → T = %.2f N·mm (안전율 %.1f)\n"
           "③ + 기울어짐 짝힘 (승준 추가): 하중 F_up이 나사 축에서 13 mm 옆 → 캐리지가 기울려 함. 나사는 아래 유연 커플링에만 잡혀 모멘트를 거의 못 받음 → 안내봉이 캐리지 두께 12 mm로 받음 [가능성 높음]\n"
           "    ΣM_나사축: M = F_up × 13 + W_c × (y_c + 13) = %.2f N·mm → N_p = M / L_c = %.3f N → 마찰 2μ_g N_p = %.3f N (μ_g 0.3: PLA 구멍–강봉)\n"
           "    F_n = (F_up + W_c + 2μ_g N_p) / (1 − μ_g k_T / 26) = %.3f N → T = %.2f N·mm, 안전율 %.1f.  이 마찰은 하중에서 생기고 추력에서는 안 생김 → 끼임 없음\n"
           "자립: 리드각 %.1f° > 마찰각 %.2f° → 자립 안 함. 전원이 꺼지면 무게 %.3f N만으로 내림 토크 %.2f N·mm → 28BYJ-48 감속기(1/64)가 막아야 함 (J6 확인)\n"
           "판정: 만족 (최악 안전율 %.1f). 단 모터 토크 34.3 mN·m는 120 Hz(약 1.8 rpm) 값 → 10~15 rpm 토크는 J6 부하 시험 (서현 r2와 같음)" % (
               ms["m_total"], ms["m_upper"], ms["m_carriage"], ms["m_total"] - 41.84, lam, phi, ms["k_T"],
               base["F"], base["T_Nmm"], base["SF"], mid["F"], mid["T_Nmm"], mid["SF"],
               ms["M_tilt"], cons["N_p"], 2 * P["mu_guide"] * cons["N_p"], cons["F"], cons["T_Nmm"], cons["SF"],
               lam, phi, ms["W_total"], ms["TL_power_off"], cons["SF"]))
    note(ax, (0.0, 0.98), txt, fs=10.4)
    textpanel(ax, "(d) 식과 값")
    legend(ax, ("given", "unk", "fric", "mom"), loc=(0.885, 0.0))
    fig.suptitle("M1  바닥 승강 나사 — 캐리지·너트 자유물체도, 나사산 조각 (D5e, 기계요소설계)", **TITLE)
    save(fig, os.path.join(OUT, "M1_D5e_승강나사_캐리지.jpg"))


# ======================================================================= M2
def m2():
    r = R["M2"]
    ec = r["eccentric"]
    Y = r["Y (볼 부싱)"]
    X = r["X (볼 부싱)"]
    fig = plt.figure(figsize=(20, 10.5))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.2, 1.0], height_ratios=[1, 0.42], hspace=0.10, wspace=0.06)
    ax = fig.add_subplot(gs[0, 0])
    zr = [z - 453 for z in P["yrod_z"]]                  # 봉 높이 (나사 z 453 기준): −15, +15
    rect(ax, -10, -53, 20, 90, fc="#e8ecf3")             # 206 캐리지 (x xb−10 ~ xb+10, z 400~490)
    rect(ax, -24.0, -45, 14.0, 30, fc="#dfe6f1")         # 홀더 202
    rect(ax, -34.4 + 0.0, -60, 14.7, 82, fc="#fff3c4", alpha=0.85)    # 마커 (일부)
    label(ax, (-27, 15), "마커 201", fs=9, box=False)
    label(ax, (-17, -30), "홀더", fs=9, box=False)
    label(ax, (0, 30), "206 Y 캐리지\n+ 서보 205", fs=9, box=False)
    for z in zr:
        ax.add_patch(Circle((0, z), 3.0, fc="white", ec="#999", ls="--", lw=1.0, zorder=3))
    label(ax, (31, 26), "Y 봉 Ø6 ×2 (떼어 냄), z 438·468", fs=8.5, c="#777")
    gx, gz = ec["cg_x_minus_xb"], ec["cg"][2] - 453
    cg(ax, (gx, gz), r=1.4, name="G", off=(-2.4, 2.2))
    force(ax, (gx, gz), (0, -20), GIVEN, None, push=False)
    label(ax, (gx - 1, gz - 23.5), "W_y = %.3f N" % Y["W"], c=GIVEN, fs=10)
    force(ax, (3.0, zr[1]), (10, 0), UNK, None, push=False)
    label(ax, (19, zr[1] + 3), "H = %.3f N" % ec["H"], c=UNK, fs=10)
    force(ax, (-3.0, zr[0]), (-8, 0), UNK, None, push=False)
    label(ax, (-7.0, zr[0] - 4.5), "H", c=UNK, fs=10)
    for z in zr:
        force(ax, (0, z + 3), (0, 9), UNK, None, push=True)      # 부싱이 봉 위에 얹힘 → 봉 윗점에서 위로
    label(ax, (8.5, -24), "V1 + V2 = W_y", c=UNK, fs=9.5)
    out_of_page(ax, (0, 0), r=1.4, c=UNK)
    label(ax, (30, -6), "⊙ 나사 추력 F (y, 지면 밖)\n   z 453 = 두 봉 가운데", c=UNK, fs=9.5)
    for z in zr:
        out_of_page(ax, (5.5, z + 4.5), r=0.9, inward=True, c=FRIC)
    label(ax, (30, 6.5), "⊗ 마찰 μN (지면 안)", c=FRIC, fs=9.5)
    dim(ax, (gx, -58), (0, -58), "e = %.1f" % abs(gx), off=0)
    dim(ax, (13, zr[0]), (13, zr[1]), "s = 30", off=0, rot=90)
    moment(ax, (gx, gz), 7, 120, 230, col=MOM)
    label(ax, (gx - 11, gz + 8), "W·e", c=MOM, fs=10)
    triad(ax, (-44, 33), 5, names=("x", "z"))
    setup(ax, (-48, 44), (-64, 44), "(a) Y 캐리지 묶음 — 옆에서 (x–z): 무게중심이 봉 줄에서 −x로 %.1f mm" % abs(gx))
    # (b) 이송 방향 (y): 질점
    ax = fig.add_subplot(gs[0, 1])
    rect(ax, 0, 0, 10, 6, fc="#e8ecf3")
    label(ax, (5, 3), "Y 묶음\nm = %.0f g" % ec["m_y"], fs=10, box=False)
    force(ax, (10, 3.6), (6, 0), UNK, None, push=False)
    label(ax, (17.5, 4.6), "F (나사 추력)", c=UNK, fs=10)
    force(ax, (0, 2.0), (-5, 0), FRIC, None, push=False)
    label(ax, (-6.5, 1.0), "μ(W_y + 2H)", c=FRIC, fs=10)
    force(ax, (0, 4.4), (-5, 0), INER, None, push=False, ls="--")
    label(ax, (-6.5, 5.4), "−m a", c=INER, fs=10)
    ax.plot([-9, 21], [0, 0], color="#bbb", lw=0.8)
    triad(ax, (-8, 8), 2, names=("y", "z"))
    note(ax, (0.02, 0.04), "Meriam 3/2 꼴: 정지 마찰을 넘는 추력 → ΣF_y = m a\nF = μ(W_y + 2H) + m a,  a = 0.02 m/s² (0.1 s에 2 mm/s)\n볼 부싱 μ 0.005 (카탈로그보다 크게)", fs=10, va="bottom")
    setup(ax, (-10, 22), (-7, 11), "(b) 이송 방향 (y) — 달랑베르")
    ax = fig.add_subplot(gs[1, :])
    txt = ("Y: W_y = %.3f N (r2 1.158 → D5e: 안내 핀·황동 너트·서보 받침 추가), e = %.2f mm → M = W e = %.2f N·mm → H = M / 30 = %.3f N\n"
           "   F = 0.005 × (%.3f + 2 × %.3f) + %.4f × 0.02 = %.4f N → T = k_T F = %.3f N·mm → 안전율 %.0f\n"
           "X: 빔 묶음 %.0f g, W_B = %.3f N, 끼임 연립(M5, k = 1)으로 P = %.4f N (Q_p %.3f, Q_y %.3f N) → T = %.3f N·mm → 안전율 %.0f.  PLA 부싱이면 끼임 (M5)\n"
           "판정: 만족 — 토크 여유 수백 배. 이송 시간(R6)은 모터 속도로만 정해져 서현 r2 표 그대로 (급이 상한 약 105 s, 15 rpm·재시도 1회)" % (
               Y["W"], gx, ec["M"], ec["H"], Y["W"], ec["H"], ec["m_y"] / 1000, Y["F"], Y["T_Nmm"], Y["SF"],
               r["m_x"], X["W_B"], X["F"], X["Qp"], X["Qy"], X["T_Nmm"], X["SF"]))
    note(ax, (0.0, 0.98), txt, fs=10.8)
    textpanel(ax, "(c) 식과 값")
    legend(ax, ("given", "unk", "fric", "iner", "mom"), loc=(0.885, 0.0))
    fig.suptitle("M2  X·Y 이송 — Y 캐리지 편심 짝힘과 이송 방향 힘 (D5e, 기계요소설계 + 동역학)", **TITLE)
    save(fig, os.path.join(OUT, "M2_D5e_이송_편심짝힘.jpg"))


# ======================================================================= M3
def m3():
    r0 = R["M3"]["스프링 없음"]
    rs = R["M3"]["스프링 최대 (F_p − W_h)"]
    G = R["geom_mark"]
    zmid = C5.C["HZ0"] + 20
    fig = plt.figure(figsize=(21, 12))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.3, 0.85, 0.85], height_ratios=[1, 0.45], hspace=0.10, wspace=0.08)
    # (a) 홀더 + 마커 (x–z), 원점 = 핀 줄 x_pin, z = 슬리브 가운데
    ax = fig.add_subplot(gs[0, 0])
    xT, xG, xs = r0["xT"], r0["xG"], G["x_s"] - G["x_pin"]
    zt = C5.C["ZT0"] + 0.56 - zmid
    zG = C5.group("z")[1][2] - zmid
    body(ax, [(xT - 0.6, zt), (xT + 0.6, zt), (xT + 7.35, zt + 14), (xT - 7.35, zt + 14)], fc="#fff3c4")
    rect(ax, xT - 7.35, zt + 14, 14.7, 60, fc="#fff3c4")
    label(ax, (xT, 22), "마커 201", fs=9, box=False)
    rect(ax, xT + 2, -20, -3.5 - (xT + 2), 30, fc="#dfe6f1")
    label(ax, (-8.5, -15), "홀더 202", fs=9, box=False)
    rect(ax, -3.5, -20, 7, 40, fc="#c9d3e6")
    ax.plot([0, 0], [-27, 30], color="#999", lw=1.0, ls="--", zorder=0)
    label(ax, (0, 32.5), "안내 핀 Ø3 ×2 (떼어 냄) — 슬리브 길이 40", fs=8.5, c="#777")
    cut(ax, xT - 3, xT + 3, zt - 4, zt)
    label(ax, (xT - 10, zt - 2.5), "말벌 등 (떼어 냄)", fs=8.5, c="#777")
    force(ax, (xT, zt), (0, 8), UNK, None, push=True)
    label(ax, (xT - 7.5, zt - 6.0), "N_tip", c=UNK, fs=11)
    cg(ax, (xG, zG), r=1.3, name="G", off=(-2.4, 2.2))
    force(ax, (xG, zG), (0, -12), GIVEN, None, push=False)
    label(ax, (xG, zG - 15.5), "W_h = %.3f N" % r0["W_h"], c=GIVEN, fs=10)
    force(ax, (xs, 10), (0, -9), GIVEN, None, push=True)
    label(ax, (xs + 8.0, 26.0), "F_s (스프링 204, 아래로)", c=GIVEN, fs=10)
    # N_tip(왼쪽 위로)이 W_h보다 팔이 길어 시계 방향 경향 → 위 끝은 +x로, 아래 끝은 −x로 감 → 핀이 위는 −x, 아래는 +x로 밂
    force(ax, (1.5, 18.5), (-7, 0), UNK, None, push=True)
    label(ax, (11.5, 18.5), "N1", c=UNK, fs=10)
    force(ax, (-1.5, -18.5), (7, 0), UNK, None, push=True)
    label(ax, (-11.5, -18.5), "N2", c=UNK, fs=10)
    force(ax, (3.5, 6), (0, 9), FRIC, None, push=False)
    label(ax, (13.5, 10.5), "f (위로) ≤ μ_pin ΣN", c=FRIC, fs=10)
    dim(ax, (xT, -66), (0, -66), "팁 %.1f" % abs(xT), off=0)
    dim(ax, (xG, -60), (0, -60), "G %.1f" % abs(xG), off=0)
    dim(ax, (0, -30), (xs, -30), "+%.1f" % xs, off=0, toff=2.2)
    dim(ax, (20, -20), (20, 20), "h = 40", off=0, rot=90)
    triad(ax, (-35, 33), 4, names=("x", "z"))
    setup(ax, (-38, 30), (-70, 46), "(a) 홀더 + 마커 (201~203) — 옆에서 (x–z), 혼은 탭에서 떨어짐")
    # (b) 말벌
    ax = fig.add_subplot(gs[0, 1])
    ax.add_patch(Ellipse((0, 0), 16, 7, fc="#d9c7a6", ec="#5a4630", lw=1.4, zorder=1))
    label(ax, (0, -0.6), "말벌 H", fs=10, box=False)
    ax.plot([-9, -3.0], [3.5, 3.5], color="#999", lw=3, zorder=0)
    ax.plot([3.0, 9], [3.5, 3.5], color="#999", lw=3, zorder=0)
    label(ax, (-10.5, 5.4), "격자 (떼어 냄)", fs=8.5, c="#777", ha="left")
    force(ax, (0, 3.4), (0, -6), UNK, None, push=True)
    label(ax, (0, 10.8), "N_tip (팁이 격자 구멍으로 누름)", c=UNK, fs=10)
    force(ax, (-5.5, 3.0), (0, -4.5), UNK, None, push=True)
    force(ax, (5.5, 3.0), (0, -4.5), UNK, None, push=True)
    label(ax, (-6.8, 8.2), "R_g", c=UNK, fs=10)
    label(ax, (6.8, 8.2), "R_g", c=UNK, fs=10)
    force(ax, (0, -3.5), (0, 7), GIVEN, None, push=True)
    label(ax, (0, -12.0), "F_p (바닥이 밂)", c=GIVEN, fs=10)
    note(ax, (0.03, 0.03), "ΣF_z: F_p = ΣR_g + N_tip\n격자에 붙어 있으려면 ΣR_g ≥ 0\n→ N_tip ≤ F_p  (T4 Riley 6-49 꼴)", fs=10, va="bottom")
    setup(ax, (-13, 13), (-22, 14), "(b) 말벌 — 격자·팁·바닥 사이")
    # (c) 바닥 + 밀대
    ax = fig.add_subplot(gs[0, 2])
    rect(ax, -9.75, 10, 19.5, 3, fc="#cfe8d4")
    rect(ax, -1, -6, 2, 16, fc="#c9ced6")
    label(ax, (5.8, 4), "밀대 147\n(스프링 146)", fs=9, box=False)
    force(ax, (0, 13), (0, -6), GIVEN, None, push=True)
    label(ax, (0, 20.5), "F_p (말벌이 바닥을 누름)", c=GIVEN, fs=10)
    force(ax, (-6, 11.5), (0, -6), GIVEN, None, push=False)
    label(ax, (-6, 4.2), "W_위", c=GIVEN, fs=10)
    cut(ax, -3, 3, -10, -6)
    force(ax, (0, -6), (0, 6), UNK, None, push=True)
    label(ax, (0, -14.0), "L (로드셀이 받침)", c=UNK, fs=10)
    note(ax, (0.03, 0.03), "L = F_p + W_위 → 로드셀은 F_p를 읽음.\nN_tip이 바뀌면 R_g만 바뀌고 F_p는 그대로\n(N_tip > F_p로 말벌이 밀려날 때만 바뀜)", fs=10, va="bottom")
    setup(ax, (-13, 13), (-24, 24), "(c) 바닥 + 밀대 — 로드셀이 읽는 힘")
    ax = fig.add_subplot(gs[1, :])
    txt = ("D5e: 홀더 안내가 레일(r2) → 핀 2개(Ø3, 슬리브 40). 홀더가 말벌 등에 앉아 멈추면 핀 마찰 f는 위쪽, 0 ~ f_max (정지 마찰)\n"
           "  ΣF_z: N_tip = W_h + F_s − f,   ΣM(핀 줄): M_y = −x_T N_tip + x_G W_h + x_s F_s,  M_x = −y_G W_h,   f_max = μ_pin · 2(|M_x| + |M_y|) / h\n"
           "  팁 x_T = %.2f, 무게중심 x_G = %.2f (y_G = %.2f), 스프링 x_s = +%.2f mm (핀 줄 기준) — 팁과 무게중심이 핀 줄 같은 쪽이라 모멘트가 거의 상쇄됨\n"
           "스프링 없음: f_max = %.4f N → N_tip = %.3f ~ %.3f N  (r2 레일: 0.233 ~ 0.321 N, 마찰 몫 28 %% → D5e 핀: 4 %%)\n"
           "스프링 최대 F_s = F_p − W_h = %.3f N (홀더가 r2보다 0.2 g 무거워 0.179 → 0.177): N_tip = %.3f ~ %.3f N ≤ F_p 0.5 N\n"
           "  ※ 승준 ME2 스프링(5 mm 눌림에 0.18 N)을 그대로 쓰면 N_tip 0.503 N > 0.5 → 4 mm 눌림(0.144 N)으로 줄이거나 F_p를 올려야 함\n"
           "판정: R_g ≥ 0 만족. 핀 안내로 찍는 힘이 더 일정해짐 (마찰 몫 28 %% → 4 %%). R3·R7(F_ink·F_harm)은 여전히 시험 전 — 판정 불가" % (
               r0["xT"], r0["xG"], C5.group("z")[1][1], xs, r0["f_max"], r0["N_tip_range"][0], r0["N_tip_range"][1],
               rs["Fs"], rs["N_tip_range"][0], rs["N_tip_range"][1]))
    note(ax, (0.0, 0.98), txt, fs=10.6)
    textpanel(ax, "(d) 식과 값")
    legend(ax, ("given", "unk", "fric"), loc=(0.895, 0.0))
    fig.suptitle("M3  찍는 힘 — 물체 셋(홀더·말벌·바닥)으로 나눈 자유물체도 (D5e, 정역학)", **TITLE)
    save(fig, os.path.join(OUT, "M3_D5e_찍는힘_물체셋.jpg"))


# ======================================================================= M4
def m4():
    cases = R["M4"]
    r0 = cases["스프링 없음"]
    rs = cases["스프링 최대 + k 0.036 (10 mm 들면 +0.36 N)"]
    w = r0["worst"]
    fig = plt.figure(figsize=(22, 12.5))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.3, 0.9, 1.05], height_ratios=[1, 0.5], hspace=0.12, wspace=0.10)
    # (a) 홀더 — 앞에서 (y–z), 원점 = 두 핀 가운데, 슬리브 가운데 높이
    ax = fig.add_subplot(gs[0, 0])
    rect(ax, -14, -20, 28, 30, fc="#dfe6f1")
    for yp in (-10, 10):
        rect(ax, yp - 3.5, -20, 7, 40, fc="#c9d3e6")
        ax.plot([yp, yp], [-28, 30], color="#999", lw=1.0, ls="--", zorder=0)
    label(ax, (0, 31.5), "안내 핀 Ø3 ×2 (떼어 냄)", fs=8.5, c="#777")
    dz = r0["dz_tab"]
    rect(ax, 14, dz, 26, 3, fc="#dfe6f1")
    rect(ax, 14, dz + 3, 12, 3.5, fc="#dfe6f1")
    label(ax, (37, dz + 9.0), "탭 (202)", fs=9, box=False)
    e = w["e_y"]
    ax.add_patch(Circle((e, dz - 2), 2, fc="white", ec="#999", ls="--", lw=1.0, zorder=3))
    label(ax, (e + 9.5, dz - 4.5), "혼 끝 (떼어 냄)", fs=8.5, c="#777")
    force(ax, (e, dz), (0, 11), UNK, None, push=True)
    label(ax, (e + 1, dz - 14.5), "F (혼이 탭을 밂)", c=UNK, fs=10.5)
    force(ax, (e - 0.5, dz + 0.6), (-8, 0), FRIC, None, push=False)
    label(ax, (e - 6, dz + 3.6), "μ_h F", c=FRIC, fs=10)
    cg(ax, (r0["yG"], -4), r=1.3, name="G", off=(-2.6, 2.0))
    force(ax, (r0["yG"], -4), (0, -11), GIVEN, None, push=False)
    label(ax, (r0["yG"] + 4.5, -14), "W_h", c=GIVEN, fs=10)
    force(ax, (0, 10), (0, -8), GIVEN, None, push=True)
    label(ax, (0, 21), "F_s (스프링, 아래로)", c=GIVEN, fs=10)
    # M_x > 0 (F가 +y에서 위로) → 반시계 경향 → 위 끝은 −y로, 아래 끝은 +y로 감 → 핀이 위는 +y, 아래는 −y로 밂
    force(ax, (8.5, 18.5), (6, 0), UNK, None, push=True)
    label(ax, (2.0, 24.5), "N1 (핀마다)", c=UNK, fs=10)
    force(ax, (11.5, -18.5), (-6, 0), UNK, None, push=True)
    label(ax, (22.5, -18.5), "N2 (핀마다)", c=UNK, fs=10)
    force(ax, (-13.5, 14), (0, -8), FRIC, None, push=False)
    force(ax, (-6.5, 14), (0, -8), FRIC, None, push=False)
    label(ax, (-22, 9), "f = μ_pin ΣN\n(아래로)", c=FRIC, fs=10)
    dim(ax, (0, 27), (e, 27), "e_y = 21.1 + 14 cos θ = %.1f" % e, off=0)
    dim(ax, (-10, -26), (10, -26), "핀 간격 20", off=0)
    dim(ax, (-27, -20), (-27, 20), "h = 40", off=0, rot=90)
    moment(ax, (0, 0), 6.5, 20, 120, col=MOM)
    label(ax, (-6.5, 4.5), "M_x", c=MOM, fs=10)
    triad(ax, (-31, 25), 4, names=("y", "z"))
    setup(ax, (-34, 48), (-32, 34), "(a) 홀더 — 앞에서 (y–z), 펜 들기 (θ = %.0f°, T 최대)" % w["theta"])
    # (b) 혼
    ax = fig.add_subplot(gs[0, 1])
    th = math.radians(25.0)
    O = np.array([0.0, 0.0])
    tip = O + 14 * np.array([math.cos(th), math.sin(th)])
    ax.plot(*zip(O, tip), color="#888", lw=8, solid_capstyle="round", zorder=1)
    ax.add_patch(Circle(tuple(tip), 2, fc="#eee", ec="#333", lw=1.2, zorder=2))
    ax.add_patch(Circle(tuple(O), 3.5, fc="#eee", ec="#333", lw=1.2, zorder=2))
    point(ax, O, None)
    label(ax, (0, -5.0), "O (서보 축)", fs=10, box=False)
    cpt = tip + [0, 2]
    ax.plot([cpt[0] - 8, cpt[0] + 5], [cpt[1], cpt[1]], color="#999", lw=1.0, ls="--")
    label(ax, (cpt[0] - 9.5, cpt[1] + 1.4), "탭 아래 면 (떼어 냄)", fs=8.5, c="#777")
    force(ax, cpt, (0, -9), UNK, None, push=True)
    label(ax, (cpt[0], cpt[1] + 10.5), "F (탭이 혼을 누름)", c=UNK, fs=10)
    force(ax, cpt, (6, 0), FRIC, None, push=False)
    label(ax, (cpt[0] + 4.0, cpt[1] + 2.4), "μ_h F", c=FRIC, fs=10)
    moment(ax, O, 6.5, -50, 95, col=MOM)
    label(ax, (-7.5, 8.5), "T (반시계)", c=MOM, fs=10)
    ax.plot([tip[0], tip[0]], [-8, tip[1]], color=DIM, lw=0.8, ls=":")
    dim(ax, (0, -8), (tip[0], -8), "14 cos θ", off=0)
    ax.plot([0, 21], [0, 0], color=DIM, lw=0.8, ls=":")
    dim(ax, (21, 0), (21, cpt[1]), "14 sin θ + 2", off=0, rot=90)
    angle(ax, O, 8.0, 0, 25, "θ", tr=1.2)
    note(ax, (0.02, 0.02), "ΣM_O: T = F (14 cos θ) + μ_h F (14 sin θ + 2)\n탭이 평평해 F는 연직, 혼 끝 원 중심을 지남\n혼 면은 탭에 대해 −y로 미끄러짐 → 혼에 +y 마찰", fs=10, va="bottom")
    setup(ax, (-14, 24), (-22, 27), "(b) 서보 혼 — 옆에서 (y–z)")
    # (c) T(θ)
    ax = fig.add_subplot(gs[0, 2])
    for name, c, ls in (("스프링 없음, μ_pin 0.2", "#7fb3d5", "--"), ("스프링 없음", "#1f4e9a", "-"), ("스프링 없음, μ_pin 0.4", "#0b2545", ":"),
                        ("스프링 최대 + k 0.036 (10 mm 들면 +0.36 N)", "#c0392b", "-"), ("스프링 최대, μ_pin 0.4", "#7b241c", ":")):
        cs = cases[name]
        if cs.get("jam"):
            continue
        rows = cs["rows"]
        nm = name.replace(" (10 mm 들면 +0.36 N)", "").replace("스프링 없음", "스프링 없음, μ_pin 0.3") if ("μ_pin" not in name) else name
        ax.plot([q["theta"] for q in rows], [q["T"] for q in rows], color=c, ls=ls, lw=2,
                label="%s → 최대 %.1f (안전율 %.1f)" % (nm, cs["T_max"], cs["SF"]))
    ax.plot([q["theta"] for q in r0["rows"]], [q["T_ideal"] for q in r0["rows"]], color="#888", lw=1.4, label="마찰 없을 때 (스프링 없음)")
    ax.set_xlabel("혼 각 θ (°)  — 0: 들기 시작, 45.6: 10 mm 들림")
    ax.set_ylabel("서보 토크 T (N·mm)")
    ax.set_xlim(0, 46)
    ax.set_ylim(0, 68)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8.8, loc="upper left")
    ax.set_title("(c) 들어 올리는 동안 토크 (SG90 정지 토크 176.6 N·mm)", fontsize=12, loc="left", fontweight="bold")
    ax = fig.add_subplot(gs[1, :])
    xF_, dzm = abs(r0["xF"]), abs(r0["dz_tab"]) * r0["mu_h"]
    mu_c_e10 = 1 / (2 * (10 + xF_ + dzm) / 40 + r0["mu_h"])
    mu_c_h60 = 1 / (2 * (35.1 + xF_ + dzm) / 60 + r0["mu_h"])
    txt = ("미지수 F. ΣF_z: F − W_h − F_s − f = 0,  f = μ_pin ΣN,  ΣN = 2(|M_x| + |M_y|) / h + μ_h F  (슬리브 위·아래 끝 가로 접촉력 크기 합 — 보수적)\n"
           "  M_x = F e_y − W_h y_G + dz_tab μ_h F  (dz_tab = %.1f: 탭이 슬리브 가운데보다 아래),  M_y = −x_F F + x_G W_h + x_s F_s  (x_F = %.2f, x_G = %.2f)\n"
           "  → F = (W_h + F_s) / (1 − μ_pin [2(e_y + |x_F| + |dz_tab| μ_h) / h + μ_h])  — 서현 어림 2μe/h = 0.53과 같은 꼴에 혼 마찰·M_y 항을 더함\n"
           "스프링 없음 (μ_pin 0.3, μ_h 0.3): θ %.0f°에서 F = %.3f N (W_h %.3f N의 %.1f배), T = %.2f N·mm → 안전율 %.1f  (마찰이 없으면 %.2f N·mm)\n"
           "스프링 최대 (F_s 0.177 N → 10 mm 들면 0.537 N): T 최대 %.2f N·mm → 안전율 %.1f\n"
           "끼임 한계 μ_c = 1 / [2(e_y + |x_F| + |dz_tab| μ_h) / h + μ_h] = %.2f — μ_pin 0.3이면 여유 %.2f배뿐. μ_pin 0.4: 안전율 %.1f(스프링 없음)·%.1f(최대), μ_pin 0.5: 끼임\n"
           "판정: SG90 토크는 만족 (안전율 ≥ 7). 하지만 핀 안내가 서랍 꼴이라 마찰 여유가 작음 (서현 어림 '안전율 약 18'은 혼 마찰·탭 높이를 빼서 큼)\n"
           "환류 제안 (서현 결정): ① 핀 쌍을 혼이 미는 줄 쪽으로 옮겨 e_y ≤ 10 → μ_c %.2f  ② 슬리브를 황동 파이프 또는 Ø3 볼 부싱으로  ③ 슬리브 길이 40 → 60이면 μ_c %.2f" % (
               r0["dz_tab"], r0["xF"], r0["xG"], w["theta"], w["F"], r0["W_h"], w["F"] / r0["W_h"], w["T"], r0["SF"], w["T_ideal"],
               rs["T_max"], rs["SF"], r0["mu_c_pin"], r0["mu_c_pin"] / 0.3,
               cases["스프링 없음, μ_pin 0.4"]["SF"], cases["스프링 최대, μ_pin 0.4"]["SF"], mu_c_e10, mu_c_h60))
    note(ax, (0.0, 0.98), txt, fs=10.4)
    textpanel(ax, "(d) 식과 값")
    legend(ax, ("given", "unk", "fric", "mom"), loc=(0.895, 0.0))
    fig.suptitle("M4  펜 들기 서보 — 홀더(핀 2개 안내)·혼 자유물체도와 토크 (D5e, 정역학)", **TITLE)
    save(fig, os.path.join(OUT, "M4_D5e_펜들기_혼_핀안내.jpg"))


# ======================================================================= M5
def m5():
    m = R["M5"]
    cs = m["cases"]
    pins = R["M4"]
    fig = plt.figure(figsize=(22, 11.5))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.0, 0.85, 1.15], height_ratios=[1, 0.36], hspace=0.12, wspace=0.10)
    # (a) 위에서 (x–y): 요 — 추력 +x
    ax = fig.add_subplot(gs[0, 0])
    d = m["d"]
    rect(ax, -14, -9, 28, 18 + d, fc="#e8ecf3")
    for yy in (0, d):
        rect(ax, -12, yy - 4, 24, 8, fc="#c9d3e6")
        ax.plot([-44, 40], [yy, yy], color="#999", lw=1.0, ls="--", zorder=0)
    label(ax, (-33, 4.5), "봉 A (y −65, 떼어 냄)", fs=8.5, c="#777")
    label(ax, (-33, d + 4.5), "봉 B (y +57, 떼어 냄)", fs=8.5, c="#777")
    force(ax, (-14, -2.5), (12, 0), UNK, None, push=True)
    label(ax, (-27, -8.5), "P (나사 추력, 봉 A 선)", c=UNK, fs=10)
    force(ax, (12, -2.0), (-8, 0), FRIC, None, push=True)
    label(ax, (26, -6.0), "μ N_A (뒤로)", c=FRIC, fs=9.5)
    force(ax, (12, d - 2.0), (-8, 0), FRIC, None, push=True)
    label(ax, (27, d - 6.0), "μ(W_B + 2Q_y …) (뒤로)", c=FRIC, fs=9.5)
    force(ax, (-12, d + 4), (0, 8), UNK, None, push=False)
    label(ax, (-15, d + 14.5), "Q_y", c=UNK, fs=10)
    force(ax, (12, d - 4), (0, -8), UNK, None, push=False)
    label(ax, (15, d - 15), "Q_y", c=UNK, fs=10)
    force(ax, (0, d / 2 + 15), (-9, 0), INER, None, push=False, ls="--")
    label(ax, (-6, d / 2 + 19), "−m a", c=INER, fs=10)
    label(ax, (0, d + 27), "k = 1: 짝힘 두 점이 모두 B 부싱 (그림)\nk = 0.5: A·B에 하나씩 대각 (Riley 9-43 서랍)", fs=9, c="#444")
    dim(ax, (34, 0), (34, d), "d = %.0f" % d, off=0, rot=90)
    dim(ax, (-12, -15), (12, -15), "L = 24 (LM8UU)", off=0)
    triad(ax, (-42, -20), 6)
    setup(ax, (-48, 50), (-26, d + 36), "(a) X 빔 — 위에서 (x–y): 요(yaw)")
    # (b) 옆에서 (x–z): 피치
    ax = fig.add_subplot(gs[0, 1])
    h = m["h"]
    rect(ax, -14, -10, 28, 25 + h, fc="#e8ecf3")
    rect(ax, -12, h - 4, 24, 8, fc="#c9d3e6")
    ax.plot([-36, 36], [h, h], color="#999", lw=1.0, ls="--", zorder=0)
    ax.plot([-36, 36], [0, 0], color="#999", lw=1.0, ls=":", zorder=0)
    label(ax, (-27, h + 4.5), "X 봉 z 480", fs=8.5, c="#777")
    label(ax, (-27, 4.5), "X 나사 z 425", fs=8.5, c="#777")
    force(ax, (-14, 0), (12, 0), UNK, None, push=True)
    label(ax, (-22, -5), "P", c=UNK, fs=10)
    force(ax, (-12, h + 4), (0, 8), UNK, None, push=False)
    label(ax, (-15, h + 14.5), "Q_p", c=UNK, fs=10)
    force(ax, (12, h - 4), (0, -8), UNK, None, push=False)
    label(ax, (15.5, h - 15), "Q_p", c=UNK, fs=10)
    force(ax, (0, h / 2), (0, -12), GIVEN, None, push=False)
    label(ax, (4, h / 2 - 9), "W", c=GIVEN, fs=10)
    dim(ax, (24, 0), (24, h), "h = %.0f" % h, off=0, rot=90)
    triad(ax, (-33, h + 16), 5, names=("x", "z"))
    note(ax, (0.02, 0.02), "ΣM_y: Q_p L = h P + |M_w|\n(나사가 봉보다 h 아래에서 밂)", fs=10, va="bottom")
    setup(ax, (-38, 34), (-26, h + 30), "(b) X 빔 — 옆에서 (x–z): 피치")
    # (c) 막대: μ / μ_c
    ax = fig.add_subplot(gs[0, 2])
    items = [("X: PLA 부싱 (μ 0.3)", cs["PLA 부싱"]["comb_B"]), ("X: 소결 청동 (0.15)", cs["소결 청동"]["comb_B"]),
             ("X: LM8UU (0.005)", cs["볼 부싱 LM8UU"]["comb_B"]), ("X: LM8UU 유효 L 17", cs["볼 부싱 LM8UU (유효 길이 17, 감도)"]["comb_B"]),
             ("펜 홀더 핀 μ 0.2", pins["스프링 없음, μ_pin 0.2"]["jam_coef"]), ("펜 홀더 핀 μ 0.3", pins["스프링 없음"]["jam_coef"]),
             ("펜 홀더 핀 μ 0.4", pins["스프링 없음, μ_pin 0.4"]["jam_coef"]), ("펜 홀더 핀 μ 0.5", pins["스프링 없음, μ_pin 0.5"]["jam_coef"])]
    ys = np.arange(len(items))[::-1]
    vals = [v for _, v in items]
    cols = ["#c0392b" if v >= 1 else ("#d35400" if v > 0.6 else "#1f4e9a") for v in vals]
    ax.barh(ys, vals, color=cols)
    for yv, v in zip(ys, vals):
        ax.text(v + 0.06, yv, "%.2f" % v, va="center", fontsize=10)
    ax.axvline(1.0, color="#c0392b", lw=1.5, ls="--")
    ax.text(1.05, len(items) - 0.45, "끼임 (≥ 1)", color="#c0392b", fontsize=10)
    ax.set_yticks(ys)
    ax.set_yticklabels([n for n, _ in items], fontsize=10)
    ax.set_xlim(0, 4.9)
    ax.set_xlabel("마찰 증폭 = μ / μ_c   (X: 2μ(kd + h)/L, k = 1 / 펜 홀더: M4 식)")
    ax.grid(axis="x", alpha=0.3)
    ax.set_title("(c) 끼임 판정 — X 빔(r2와 같음)과 D5e 펜 홀더 핀", fontsize=12, loc="left", fontweight="bold")
    ax = fig.add_subplot(gs[1, :])
    lm = cs["볼 부싱 LM8UU"]
    txt = ("X 빔 (Riley 9-43 꼴): (1) P = μ(W + 2Q_p + 2Q_y) + m a  (2) Q_p L = h P + |M_w|  (3) Q_y L = d μ(W_B + 2k Q_y + 2k Q_p) + m a e_y  → 행렬식 0: μ_c = L / 2(k d + h)\n"
           "  D5e도 d = 122, h = 55, L = 24 그대로 → μ_c = %.3f (k 1) / %.3f (k 0.5): LM8UU μ 0.005면 여유 %.1f배 — r2 판정 그대로 (μ_c는 질량과 무관)\n"
           "펜 홀더 핀 (D5e 새 항목, M4와 같은 식): 미는 점이 두 핀 줄에서 e_y = 31~35 mm 옆 → μ_c = %.2f.  μ_pin 0.3 → 0.68 (여유 1.5배), 0.4 → 0.91, 0.5 → 끼임\n"
           "판정: X 빔 만족. 펜 홀더는 PLA 구멍–강 핀의 실제 마찰(인쇄 면 거칠기·먼지)에 따라 끼일 수 있음 → M4 환류 ①~③ 중 하나 권장 [가능성 높음]" % (
               lm["mu_c_comb_B"], lm["mu_c_comb_AB"], lm["SF_mu"], pins["스프링 없음"]["mu_c_pin"]))
    note(ax, (0.0, 0.98), txt, fs=10.6)
    textpanel(ax, "(d) 식과 값")
    legend(ax, ("given", "unk", "fric", "iner"), loc=(0.895, 0.0))
    fig.suptitle("M5  한쪽 구동 X 빔의 끼임(요 + 피치)과 D5e 펜 홀더 핀 안내 (정역학 마찰 / 안내 요소 선정)", **TITLE)
    save(fig, os.path.join(OUT, "M5_D5e_끼임_X빔_펜홀더.jpg"))


# ======================================================================= M6
def m6():
    rr = R["M6"]["rest"]
    rm = R["M6"]["mark"]
    A = rr["X 봉 A (무게중심 배분)"]
    worst = rr["X 봉 한 개가 전부 (최악)"]
    Yw = rr["Y 봉 한 개가 세로 전부 + 수평 짝힘 (최악)"]
    L = P["L_xrod"]
    F = A["F"]
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 2, width_ratios=[1.35, 1.0], height_ratios=[0.9, 0.75, 0.75], hspace=0.38, wspace=0.08)
    ax = fig.add_subplot(gs[0, 0])
    rect(ax, 0, -2, L, 4, fc="#d5d8dc")
    force(ax, (L / 2, 2), (0, -20), GIVEN, None, push=True)
    label(ax, (L / 2, 25.5), "R_A = %.3f N  (빔 묶음 무게의 %.0f %%, 대기 자세 — LM8UU 부싱이 봉을 누름)" % (F, 100 * rr["_beam"]["R_A_share"]), c=GIVEN, fs=10)
    force(ax, (0, -2), (0, 14), UNK, None, push=True)
    force(ax, (L, -2), (0, 14), UNK, None, push=True)
    label(ax, (0, -19), "R_A / 2", c=UNK, fs=10)
    label(ax, (L, -19), "R_A / 2", c=UNK, fs=10)
    label(ax, (0, 7), "받침 218 (떼어 냄)", fs=8.5, c="#777")
    label(ax, (L, 7), "받침 218 (떼어 냄)", fs=8.5, c="#777")
    dim(ax, (0, -28), (L, -28), "L = %.0f (봉 길이 = 받침 사이 최대, 보수적)" % L, off=0)
    dim(ax, (0, 12), (L / 2, 12), "%.1f" % (L / 2), off=0)
    setup(ax, (-14, L + 14), (-33, 30), "(a) X 봉 A (Ø8 강) — 단순보, 하중이 가운데 (빔이 지나가는 최악 위치)")
    ax = fig.add_subplot(gs[1, 0])
    ax.fill_between([0, L / 2, L / 2, L], [F / 2, F / 2, -F / 2, -F / 2], color="#7fb3d5", alpha=0.7)
    ax.plot([0, 0, L / 2, L / 2, L, L], [0, F / 2, F / 2, -F / 2, -F / 2, 0], color="#1f4e9a", lw=2)
    ax.axhline(0, color="#333", lw=0.8)
    ax.text(L / 4, F / 2 * 1.2, "V = +%.3f N" % (F / 2), ha="center", fontsize=10)
    ax.text(3 * L / 4, -F / 2 * 1.5, "V = −%.3f N" % (F / 2), ha="center", fontsize=10)
    ax.set_xlim(-14, L + 14)
    ax.set_ylim(-F, F)
    ax.set_ylabel("V (N)")
    ax.set_title("(b) 전단력도 SFD", fontsize=12, loc="left", fontweight="bold")
    ax.grid(alpha=0.3)
    ax = fig.add_subplot(gs[2, 0])
    Mmax = F * L / 4
    ax.fill_between([0, L / 2, L], [0, Mmax, 0], color="#a9dfbf", alpha=0.8)
    ax.plot([0, L / 2, L], [0, Mmax, 0], color="#117a65", lw=2)
    ax.axhline(0, color="#333", lw=0.8)
    ax.text(L / 2, Mmax * 1.08, "M_max = R_A L / 4 = %.1f N·mm" % Mmax, ha="center", fontsize=10)
    ax.set_xlim(-14, L + 14)
    ax.set_ylim(0, Mmax * 1.35)
    ax.set_ylabel("M (N·mm)")
    ax.set_xlabel("x (mm, 봉 끝에서)")
    ax.set_title("(c) 굽힘 모멘트도 BMD", fontsize=12, loc="left", fontweight="bold")
    ax.grid(alpha=0.3)
    ax = fig.add_subplot(gs[:, 1])
    I8 = math.pi * 8 ** 4 / 64
    txt = ("주어진 것: X 빔 묶음 %.0f g (r2 387 → D5e: X 너트·Y 커플링·\n  모터 브래킷이 모델에 들어감)\n"
           "  W_x = %.3f N,  무게중심 y: 찍기 %.1f / 대기 %.1f mm\n"
           "  봉 A 몫 R_A = W_x (y_B − y_G)/(y_B − y_A): 찍기 %.0f %% · 대기 %.0f %%\n"
           "  Ø8 강봉 E = 200 GPa,  I = πd⁴/64 = %.1f mm⁴,  S = πd³/32 = %.2f mm³\n\n"
           "Gere 9.3-1 식 (a = b = L/2):\n"
           "  δ = R L³ / (48 E I),   M = R L / 4,   σ = M / S\n\n"
           "X 봉 A (대기, 가장 무거움): R = %.3f N\n"
           "  δ = %.4f mm,  σ = %.2f MPa\n"
           "X 봉 한 개가 전부 받을 때 (최악): R = %.3f N\n"
           "  δ = %.4f mm,  σ = %.2f MPa\n"
           "  (서현 어림 0.0070 × (163/153)³ = 0.0085 mm는 길이만 바꾼 값 —\n"
           "   질량 18 %% 증가까지 넣으면 0.0100 mm)\n"
           "Y 봉 Ø6, L 104 (세로 전부 %.3f N + 편심 수평 %.3f N 합성):\n"
           "  R = %.3f N → δ = %.4f mm,  σ = %.2f MPa\n\n"
           "판정: 만족 — 최악 처짐 0.010 mm는 정확도 ±1 mm의 1/100.\n"
           "봉 지름은 LM 부싱 규격(Ø8·Ø6)에 맞춰 유지 (r2와 같음)" % (
               rr["_beam"]["m_g"], rr["_beam"]["Wx"], rm["_beam"]["cg"][1], rr["_beam"]["cg"][1],
               100 * rm["_beam"]["R_A_share"], 100 * rr["_beam"]["R_A_share"], I8, math.pi * 8 ** 3 / 32,
               F, A["delta"], A["sigma"], worst["F"], worst["delta"], worst["sigma"],
               Yw["F_vert"], Yw["H"], Yw["F"], Yw["delta"], Yw["sigma"]))
    note(ax, (0.0, 0.98), txt, fs=11)
    textpanel(ax, "(d) 식과 값")
    legend(ax, ("given", "unk"), loc=(0.0, 0.0))
    fig.suptitle("M6  X 고정 봉 처짐 — 자유물체도·SFD·BMD (D5e, 재료역학)", **TITLE)
    save(fig, os.path.join(OUT, "M6_D5e_봉처짐_SFD_BMD.jpg"))


if __name__ == "__main__":
    for f in (m1, m2, m3, m4, m5, m6):
        f()
    print("saved to", os.path.abspath(OUT))
