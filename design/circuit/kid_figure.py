# -*- coding: utf-8 -*-
"""회로 한 장 그림 (초등학생용) — 서현, 2026-11-06, CAP-AI-29
빨강 굵은 선 = 힘 쓰는 전기 (5 V 구동 레일), 주황 = 머리 전기 (Pi 27 W), 파랑 가는 선 = 신호(명령·보고), 검정 = GND(돌아오는 길)
실행: python3 design/circuit/kid_figure.py → design/img/circuit/회로_한장그림.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({"font.family": "Noto Sans CJK JP", "axes.unicode_minus": False})
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "img", "circuit", "회로_한장그림.png")
RED, ORG, BLU, BLK, GRY = "#c0392b", "#d68910", "#1f4e9a", "#222222", "#666666"


def box(ax, x, y, w, h, text, fc, ec="#333333", fs=11, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15", fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal")


def line(ax, pts, c, lw, ls="-", arrow=False):
    xs, ys = zip(*pts)
    if arrow:
        ax.plot(xs[:-1] + (xs[-1],), ys[:-1] + (ys[-1],), color=c, lw=lw, ls=ls, zorder=1)
        ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle="-|>", mutation_scale=14, color=c, lw=lw, zorder=2))
    else:
        ax.plot(xs, ys, color=c, lw=lw, ls=ls, zorder=1)


def main():
    fig, ax = plt.subplots(figsize=(15, 9.5), dpi=150)
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 21.6)
    ax.axis("off")
    ax.text(0.3, 21.0, "우리 기계의\n전기 지도", fontsize=17, fontweight="bold", va="top")

    # 전기 길 1: 머리용
    box(ax, 0.5, 15.2, 4.2, 2.0, "콘센트 ①\n27 W 어댑터\n(머리 전용)", "#fdebd0")
    box(ax, 7.5, 14.6, 6.0, 3.2, "머리 = Raspberry Pi 5\n+ AI HAT+ + AI 카메라\n(보고, 생각하고, 명령)", "#d6eaf8", bold=True)
    line(ax, [(4.7, 16.2), (7.5, 16.2)], ORG, 4)
    ax.text(5.0, 16.6, "머리 전기", color=ORG, fontsize=10)
    box(ax, 15.5, 16.2, 2.6, 1.6, "AI 카메라", "#eaf2f8", fs=10)
    line(ax, [(13.5, 17.0), (15.5, 17.0)], BLU, 1.6)

    # USB 두 줄 → UNO 1, UNO 2 (전기 + 대화)
    box(ax, 6.0, 9.0, 5.0, 2.6, "손 1 = UNO 1\n움직임 담당", "#d5f5e3", bold=True)
    box(ax, 15.0, 9.0, 5.0, 2.6, "손 2 = UNO 2\n문·문지기·불 담당", "#d5f5e3", bold=True)
    line(ax, [(9.0, 14.6), (9.0, 11.6)], BLU, 2.2, arrow=True)
    line(ax, [(12.0, 14.6), (12.0, 13.2), (17.5, 13.2), (17.5, 11.6)], BLU, 2.2, arrow=True)
    ax.text(9.2, 13.0, "USB 줄 1\n(손 1의 전기 + 대화)", color=BLU, fontsize=9.5)
    ax.text(13.0, 13.45, "USB 줄 2 (손 2의 전기 + 대화)", color=BLU, fontsize=9.5)

    # 전기 길 2: 힘 쓰는 것용
    box(ax, 23.5, 15.2, 5.8, 2.0, "콘센트 ② 5 V 3 A 어댑터\n(힘 쓰는 것 전용)", "#fadbd8")
    box(ax, 24.6, 12.4, 3.6, 1.6, "퓨즈 3 A\n(너무 많으면 끊김)", "#fdedec", fs=10)
    box(ax, 24.6, 10.0, 3.6, 1.6, "비상 정지 버튼\n(누르면 끊김)", "#fdedec", fs=10)
    box(ax, 22.0, 6.6, 7.4, 2.2, "와고 커넥터 묶음 (전기 나눠 주는 곳)\n+5 V 묶음 / GND 묶음", "#f9e79f", bold=True)
    line(ax, [(26.4, 15.2), (26.4, 14.0)], RED, 4)
    line(ax, [(26.4, 12.4), (26.4, 11.6)], RED, 4)
    line(ax, [(26.4, 10.0), (26.4, 8.8)], RED, 4)

    # 힘 쓰는 것들 (아래 줄)
    things = [(0.5, "스테핑 모터 3개\n(바닥·펜 X·펜 Y)\n+ ULN2003 3개"), (5.4, "펜 서보 SG90\n+ 원점 스위치 3\n+ 로드셀(HX711)"),
              (10.3, "문 서보\nMG90S 3개"), (15.2, "빛 문지기\n(빛 게이트) 9쌍"), (20.1, "조명 2개 (위·아래)\n(MOSFET로 켜고 끔)")]
    for x, t in things:
        box(ax, x, 1.2, 4.4, 2.6, t, "#fef9e7", fs=10)
    # 신호 (파랑): UNO 1 → 앞 둘, UNO 2 → 뒤 셋
    for x in (2.7, 7.6):
        line(ax, [(8.5, 9.0), (8.5, 5.4), (x, 5.4), (x, 3.8)], BLU, 1.5, arrow=True)
    for x in (12.5, 17.4, 22.3):
        line(ax, [(17.5, 9.0), (17.5, 5.0), (x, 5.0), (x, 3.8)], BLU, 1.5, arrow=True)
    ax.text(0.6, 5.7, "명령·보고 (파랑, 가는 선)", color=BLU, fontsize=10)
    # 힘 전기 (빨강): 단자대 → 모든 힘 쓰는 것 (로드셀 제외 — 로드셀은 UNO 1의 조용한 5 V)
    line(ax, [(22.0, 7.2), (1.0, 7.2), (1.0, 3.8)], RED, 3.2)
    for x in (6.0, 10.8, 15.7, 20.6):
        line(ax, [(x, 7.2), (x, 3.8)], RED, 3.2)
    ax.text(12.0, 7.45, "힘 쓰는 전기 +5 V (빨강, 굵은 선)", color=RED, fontsize=10)
    # GND (검정 점선)
    line(ax, [(29.0, 6.6), (29.0, 0.5), (1.6, 0.5), (1.6, 1.2)], BLK, 1.8, ls="--")
    for x in (7.2, 12.0, 17.0, 22.0):
        line(ax, [(x, 0.5), (x, 1.2)], BLK, 1.8, ls="--")
    line(ax, [(10.05, 9.0), (10.05, 0.5)], BLK, 1.8, ls="--")
    line(ax, [(19.85, 9.0), (19.85, 0.5)], BLK, 1.8, ls="--")
    ax.text(23.0, 0.05, "GND = 전기가 돌아가는 길 (검정 점선) — 모두 한 점에 모음", color=BLK, fontsize=10)
    # 규칙 상자
    ax.text(7.5, 21.0, "약속 3개\n① 머리 전기와 힘 전기는 따로 (모터가 힘을 써도 머리가 안 꺼지게)\n"
            "② 돌아오는 길(GND)은 한 점에서 모두 이음 (같은 '바닥 높이')\n③ UNO의 5 V 핀과 힘 전기 +5 V는 절대 잇지 않음",
            fontsize=10.5, va="top", bbox=dict(boxstyle="round,pad=0.4", fc="#fbfbfb", ec="#999999"))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight", facecolor="white")
    print(OUT)


if __name__ == "__main__":
    main()
