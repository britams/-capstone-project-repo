# -*- coding: utf-8 -*-
"""스프링 146 2차 그림 (서현, 2026-11-06, CAP-AI-25) — fbd_lib 색 규칙
  spring146_FBD2_안내마찰.jpg : 말벌이 가운데에서 e만큼 벗어날 때 바닥+밀대 자유물체도 (Riley 9-6 방법)
  spring146_FBD3_동역학.jpg   : 바닥 질량-스프링 모델 (Meriam 8/1 방법) — 관성력 −m a 포함
  spring146_시간응답.png      : 시간 적분 (k_c 3000, HX711 10/80 Hz) — N_h(t)
실행: python3 design/calc/spring146_fbd2.py
"""
import os
import math
import matplotlib.pyplot as plt
import fbd_lib as F
import spring146_calc2 as S

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "img", "calc")


def guide_fbd():
    fig, axs = plt.subplots(1, 2, figsize=(14.5, 8.2), gridspec_kw=dict(width_ratios=[1.15, 1]))
    ax = axs[0]
    F.setup(ax, (-12, 14), (-3, 22), "① 바닥 + 밀대 (말벌이 e만큼 벗어남)")
    F.rect(ax, -9.75, 15.0, 19.5, 1.5)                       # 바닥판 (39 → 그림 축척 0.5)
    F.rect(ax, -0.5, 1.0, 1.0, 14.0)                          # 밀대
    F.rect(ax, -2.2, 0.4, 4.4, 0.6)                           # 칼라
    # 안내 구멍 (바닥판 121, 두께 5 mm) — 떼어 냄: 점선으로 자리만
    for x in (-1.3, 0.8):
        F.rect(ax, x, 8.0, 0.5, 2.5, fc="none", ec="#999999", ls="--")
    F.label(ax, (-8.0, 13.2), "안내 구멍 자리 (점선)\n떼어 내고 반력으로", fs=8.5, c="#777777", box=False)
    # 힘
    F.force(ax, (6.0, 16.5), (0, -3.2), F.UNK, "N_h (말벌)", push=True, off=(0, 0.6), fs=10)
    F.dim(ax, (0, 18.6), (6.0, 18.6), "e (≤ 20 mm)", fs=9)
    F.force(ax, (0, 0.4), (0, 3.2), F.UNK, None, push=True)
    F.label(ax, (2.6, -1.4), "F_s = k_s·x (스프링)", c=F.UNK, fs=10)
    F.force(ax, (0, 14.4), (0, -2.0), F.GIVEN, None, push=False)
    F.label(ax, (-1.6, 13.4), "W", c=F.GIVEN, fs=10)
    F.force(ax, (0.5, 10.5), (-2.6, 0), F.UNK, None, push=True)
    F.label(ax, (5.0, 11.2), "R (위 끝, 벽이 밂)", c=F.UNK, fs=9.5)
    F.force(ax, (-0.5, 8.0), (2.6, 0), F.UNK, None, push=True)
    F.label(ax, (-5.6, 7.0), "R (아래 끝, 벽이 밂)", c=F.UNK, fs=9.5)
    F.force(ax, (0.5, 10.5), (0, -2.0), F.FRIC, None, push=False, lw=2.0)
    F.force(ax, (-0.5, 8.0), (0, -2.0), F.FRIC, None, push=False, lw=2.0)
    F.label(ax, (2.3, 7.6), "μR ×2\n(올라가는 중 → 아래로)", c=F.FRIC, fs=9)
    F.dim(ax, (-9.5, 8.0), (-9.5, 10.5), "L 5 mm", fs=9, rot=90)
    F.legend(ax, items=("given", "unk", "fric"), loc=(0.0, 0.0), fs=8.5)

    ax = axs[1]
    F.setup(ax, (0, 10), (0, 12), "② 식과 결과 (A 정역학)")
    txt = ("ΣM (밀대 축):  N_h·e = R·L\n"
           "ΣF_z:  F_s = N_h + W + 2μR\n"
           "      = N_h (1 + 2μe/L) + W\n\n"
           "로드셀 0점(W) 맞추고 F_s − W = F_p에서 멈춤 →\n"
           "  N_h = F_p / (1 + 2μe/L)\n\n"
           "지금 (Ø5 구멍 5 mm, PLA μ 0.2~0.5), e = 20 mm:\n"
           "  N_h = 0.19 ~ 0.10 N  (F_p의 38 ~ 20 %)\n"
           "  → 말벌을 붙잡지 못할 수 있음 (덜 누르는 쪽)\n\n"
           "LM4UU 12 mm (μ 0.002~0.005), e = 20 mm:\n"
           "  N_h = 0.497 ~ 0.492 N  (F_p의 99 ~ 98 %)\n\n"
           "바닥판이 벽에 끼어 모멘트를 받을 수 있나?\n"
           "  기운 판 폭 최대 √(39² + 6²) = 39.46 < 40 mm → 못 받음\n"
           "  → 모멘트는 모두 밀대 안내가 받음")
    F.note(ax, (0.2, 11.6), txt, fs=10.5, transform=ax.transData)
    fig.suptitle("A 정역학 — 밀대 안내 마찰 (Riley 9-6 방법: 두 접촉점 + 마찰 + 모멘트)", fontsize=13, fontweight="bold")
    p = os.path.join(IMG, "spring146_FBD2_안내마찰.jpg")
    F.save(fig, p)
    return p


def dyn_fbd():
    fig, axs = plt.subplots(1, 2, figsize=(14.5, 8.0), gridspec_kw=dict(width_ratios=[1, 1.1]))
    ax = axs[0]
    F.setup(ax, (-9, 11), (-2, 21), "① 모델: 캐리지(속도 v) – 스프링 k_s – 바닥 m – 말벌 k_c – 격자")
    F.rect(ax, -5, 18.2, 10, 0.8, fc="#d9d9d9")
    F.label(ax, (6.0, 18.6), "격자 (고정)", fs=9, ha="left", box=False)
    from spring146_fbd import spring_zigzag
    spring_zigzag(ax, 0, 14.2, 18.2, w=0.6, n=4, c="#7a5c00")
    F.label(ax, (1.2, 16.2), "k_c, c (말벌)", fs=9, ha="left", box=False, c="#7a5c00")
    F.rect(ax, -4, 12.6, 8, 1.6)
    F.label(ax, (4.6, 13.4), "바닥 + 강철 축 m = 19.2 g (D5f)", fs=9, ha="left", box=False)
    spring_zigzag(ax, 0, 6.6, 12.6, w=0.9, n=6)
    F.label(ax, (1.4, 9.6), "k_s", fs=10, ha="left", box=False)
    F.rect(ax, -4, 4.6, 8, 2.0, fc="#e8e8e8")
    F.label(ax, (4.6, 5.6), "캐리지 + 로드셀", fs=9, ha="left", box=False)
    F.arrow(ax, (-6.5, 3.0), (-6.5, 6.0), F.DIM, lw=1.6)
    F.label(ax, (-6.5, 1.6), "z_c = v t\n(F_p 넘으면 멈춤)", fs=8.5, c=F.DIM, box=False)
    F.arrow(ax, (10.2, 12.2), (10.2, 14.6), F.DIM, lw=1.4)
    F.label(ax, (10.2, 11.4), "x", fs=10, c=F.DIM, box=False)

    ax = axs[1]
    F.setup(ax, (-7, 11), (-2, 21), "② 바닥 자유물체도 (관성력 포함)")
    F.rect(ax, -4, 9.0, 8, 1.6)
    F.cg(ax, (0, 9.8), name="G", off=(0.7, 0.6))
    F.force(ax, (0, 10.6), (0, -3.0), F.UNK, "N_h = k_c(x − gap) + c·(dx/dt)", push=True, off=(0, 0.7), fs=9.5)
    F.force(ax, (0, 9.0), (0, 3.0), F.UNK, None, push=True)
    F.label(ax, (0, 5.3), "F_s = k_s (z_c − x)", c=F.UNK, fs=9.5)
    F.force(ax, (-2.5, 9.8), (0, -2.2), F.GIVEN, None, push=False)
    F.label(ax, (-3.9, 7.0), "W = m g", c=F.GIVEN, fs=9.5)
    F.force(ax, (3.0, 9.8), (0, -2.2), F.INER, None, push=False, ls="--", lw=2.0)
    F.label(ax, (4.6, 7.0), "−m a", c=F.INER, fs=9.5)
    F.note(ax, (-6.8, 3.6),
           "ΣF = 0 (달랑베르):  F_s − W − N_h − m a = 0\n"
           "닿는 순간 진폭 = v / ω2,  ω2 = √((k_s + k_c)/m)  (Meriam 8/1)\n"
           "  k_c 3000: 4.9 µm → ΔN_h = 0.015 N (2.9 %)\n"
           "멈출 때 진폭 0.16 µm → 0.0005 N\n"
           "시간 적분 최대 넘침: 10 Hz 5.3 %, 80 Hz 4.4 % (감쇠 0)", fs=9.5, transform=ax.transData)
    F.legend(ax, items=("given", "unk", "iner"), loc=(0.62, 0.86), fs=8.5)
    fig.suptitle("C 동역학 — 바닥 질량-스프링 (Meriam 8/1 방법)", fontsize=13, fontweight="bold")
    p = os.path.join(IMG, "spring146_FBD3_동역학.jpg")
    F.save(fig, p)
    return p


def time_plot():
    """press_sim과 같은 식을 기록용으로 다시 돌림"""
    IN = S.IN
    k_s = S.machine_elements()["choice"]["k"]
    fig, ax = plt.subplots(figsize=(8.6, 4.8), dpi=150)
    for f_hx, col in ((10.0, "#d35400"), (80.0, "#1f4e9a")):
        m, v, W, kc, gap = IN["m_floor"], IN["v"], IN["m_floor"] * 9.81, 3000.0, 0.2e-3
        x, xd, t, dt = -W / k_s, v, 0.0, 2e-6
        t_next, t_halt, halted = 0.0, None, False
        T, N = [], []
        t_contact = (gap - x) / v
        while t < t_contact + 3.5:
            zc = v * t if not halted else v * t_halt
            pen = x - gap
            n = max(kc * pen, 0.0) if pen > 0 else 0.0
            a = (k_s * (zc - x) - W - n) / m
            xd += a * dt
            x += xd * dt
            t += dt
            if not halted and t >= t_next:
                t_next += 1 / f_hx
                if k_s * (zc - x) - W >= IN["F_p"] and t_halt is None:
                    t_halt = t + IN["t_stop"]
            if t_halt is not None and t >= t_halt:
                halted = True
            if int(t / dt) % 200 == 0:
                T.append(t - t_contact)
                N.append(n)
        ax.plot(T, N, color=col, lw=1.6, label="HX711 %d Hz" % f_hx)
    ax.axhline(IN["F_p"], color="#c0392b", ls="--", lw=1)
    ax.text(0.05, IN["F_p"] + 0.008, "F_p 0.5 N", color="#c0392b", fontsize=9)
    ax.set_xlim(0, 3.2)
    ax.set_ylim(0, 0.6)
    ax.set_xlabel("닿은 뒤 시간 (s)")
    ax.set_ylabel("말벌을 누르는 힘 N_h (N)")
    ax.set_title("시간 적분: k_s %.1f N/m, 단단한 말벌 k_c 3000 N/m, 감쇠 0 (가장 나쁜 경우)\n선 두께 = 닿을 때 생긴 64 Hz 진동 ±0.015 N (감쇠가 없어 줄지 않음)" % k_s, fontsize=10)
    ax.grid(color="#e5e5e5", lw=0.6)
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    fig.tight_layout()
    p = os.path.join(IMG, "spring146_시간응답.png")
    fig.savefig(p)
    plt.close(fig)
    return p


if __name__ == "__main__":
    for p in (guide_fbd(), dyn_fbd(), time_plot()):
        print(p)
