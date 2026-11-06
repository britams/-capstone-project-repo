# -*- coding: utf-8 -*-
"""스프링 146 자유물체도 (서현, 2026-11-06, CAP-AI-24) — fbd_lib 색 규칙
왼쪽: 쌓임 순서와 절단면 / 가운데: 바닥+밀대 (받침 떼고 반력) / 오른쪽: 말벌
실행: python3 design/calc/spring146_fbd.py → design/img/calc/spring146_FBD.jpg
"""
import os
import matplotlib.pyplot as plt
import fbd_lib as F

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "img", "calc", "spring146_FBD.jpg")


def spring_zigzag(ax, x, y0, y1, w=0.9, n=6, c="#222222"):
    import numpy as np
    ys = np.linspace(y0, y1, 2 * n + 1)
    xs = [x + (w if i % 2 else -w) if 0 < i < 2 * n else x for i in range(2 * n + 1)]
    ax.plot(xs, ys, color=c, lw=1.6, zorder=3)


def panel_stack(ax):
    F.setup(ax, (-6, 9), (-1, 21), "① 쌓임 순서와 절단 (D5e)")
    F.rect(ax, -4, 18.5, 8, 0.8, fc="#d9d9d9")                       # 격자
    F.label(ax, (5.6, 18.9), "격자 (고정)", fs=9, ha="left", box=False)
    F.rect(ax, -2.0, 16.2, 4.0, 2.3, fc=F.BODY2)                     # 말벌
    F.label(ax, (5.6, 17.3), "말벌 (등 높이 h)", fs=9, ha="left", box=False)
    F.rect(ax, -4, 15.2, 8, 1.0)                                     # 바닥 140
    F.label(ax, (5.6, 15.7), "바닥 140", fs=9, ha="left", box=False)
    F.rect(ax, -0.4, 10.0, 0.8, 5.2)                                 # 밀대 147
    F.label(ax, (5.6, 12.6), "밀대 147 (Ø4)", fs=9, ha="left", box=False)
    F.rect(ax, -1.6, 9.4, 3.2, 0.6)                                  # 칼라
    spring_zigzag(ax, 0, 6.2, 9.4)
    F.label(ax, (5.6, 7.8), "스프링 146 (k_s)", fs=9, ha="left", box=False)
    F.rect(ax, -2.0, 4.6, 4.0, 1.6, fc="#e8e8e8")                    # 로드셀
    F.label(ax, (5.6, 5.4), "로드셀 148 (HX711)", fs=9, ha="left", box=False)
    F.rect(ax, -3.5, 2.4, 7.0, 2.2, fc="#e8e8e8")                    # 캐리지
    F.label(ax, (5.6, 3.5), "캐리지 + T8 너트", fs=9, ha="left", box=False)
    F.arrow(ax, (-4.8, 1.0), (-4.8, 4.0), F.DIM, lw=1.6)
    F.label(ax, (-4.8, 0.3), "v = 1.96 mm/s", fs=9, c=F.DIM, box=False)
    ax.plot([-5.5, 5.0], [9.7, 9.7], color="#c0392b", lw=1.0, ls=(0, (5, 3)))
    F.label(ax, (-5.4, 10.3), "절단 A", fs=9, c="#c0392b", ha="left", box=False)
    ax.plot([-5.5, 5.0], [16.2, 16.2], color="#c0392b", lw=1.0, ls=(0, (5, 3)))
    F.label(ax, (-5.4, 16.8), "절단 B", fs=9, c="#c0392b", ha="left", box=False)


def panel_floor(ax):
    F.setup(ax, (-7, 8), (-1, 21), "② 바닥 + 밀대 (절단 A·B 사이)")
    F.rect(ax, -4, 15.2, 8, 1.0)
    F.rect(ax, -0.4, 10.0, 0.8, 5.2)
    F.rect(ax, -1.6, 9.4, 3.2, 0.6)
    F.cg(ax, (0, 13.6), name="G", off=(0.7, 0.2))
    F.force(ax, (0, 16.2), (0, -3.0), F.UNK, "N_h (말벌이 바닥을 누름)", push=True, off=(0, 0.6), fs=9)
    F.force(ax, (0, 13.6), (0, -3.0), F.GIVEN, None, push=False)
    F.label(ax, (-2.9, 11.6), "W = m g\n= 0.097 N", c=F.GIVEN, fs=9)
    F.force(ax, (0, 9.4), (0, 3.6), F.UNK, "F_s = k_s·x", push=True, off=(2.6, 0.8), fs=9)
    F.force(ax, (3.2, 13.6), (0, -2.4), F.INER, None, push=False, ls="--", lw=2.0)
    F.label(ax, (4.6, 11.4), "−m a\n≈ 0", c=F.INER, fs=9)
    F.note(ax, (-6.8, 4.0), "ΣF_z = 0 (a ≈ 0):\nF_s = N_h + W\n로드셀 읽음 = F_s → 0점 맞추면 = N_h\n멈춤: N_h = F_p = 0.5 N", fs=9, transform=ax.transData)


def panel_hornet(ax):
    F.setup(ax, (-6, 8), (-1, 21), "③ 말벌 (절단 B 위)")
    F.rect(ax, -2.0, 13.0, 4.0, 2.3, fc=F.BODY2)
    F.force(ax, (0, 15.3), (0, -2.6), F.UNK, "R_g (격자 반력)", push=True, off=(0, 0.6), fs=9)
    F.force(ax, (0, 13.0), (0, 2.6), F.UNK, None, push=True)
    F.label(ax, (2.6, 11.0), "N_h (바닥 반작용)", c=F.UNK, fs=9)
    F.note(ax, (-5.8, 8.6), "R_g = N_h (말벌 무게 0.003 N 무시)\n말벌 몸 + 접촉 = 스프링 k_c\nk_eff = k_s k_c / (k_s + k_c)\n캐리지가 Δ 올라가면 N_h = k_eff·Δ", fs=9, transform=ax.transData)
    F.legend(ax, items=("given", "unk", "iner"), loc=(0.0, 0.0), fs=8.5)


def main():
    fig, axs = plt.subplots(1, 3, figsize=(15, 7.6))
    panel_stack(axs[0])
    panel_floor(axs[1])
    panel_hornet(axs[2])
    fig.suptitle("스프링 146 자유물체도 — 받침(캐리지·격자)은 떼고 반력으로", fontsize=13, fontweight="bold")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    F.save(fig, OUT)
    print(OUT)


if __name__ == "__main__":
    main()
