import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Rectangle, Polygon
import numpy as np
plt.rcParams.update({"font.family": "Noto Sans CJK JP", "axes.unicode_minus": False})
RED, BLUE, ORG, GRN, GRY = "#C0392B", "#1F4E9A", "#D35400", "#2E7D32", "#555555"
pf, pe, rf = "#DDEAF5", "#5B87B0", "#BFD6EC"
def darrow(ax, p1, p2, c, lw=2.2):
    ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="<|-|>", color=c, lw=lw, mutation_scale=15, shrinkA=0, shrinkB=0))
def box(ax, xy, t, c, fs=12.5, ha="center"):
    ax.text(*xy, t, fontsize=fs, color=c, fontweight="bold", ha=ha, va="center",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=c, lw=1.5))
fig = plt.figure(figsize=(12, 19), dpi=150)
fig.text(0.03, 0.988, "걸쇠 w · p · k 와 레일 깊이 g — 포획통 뒤집어 놓고", fontsize=21, fontweight="bold", va="top")
fig.text(0.03, 0.968, "지름은 이미 잼: 걸쇠 고리 81.2 / 85.6, 큰 벽 93.1. 크기·높이는 개념도(모르는 값).", fontsize=12, color=GRY, va="top")

# ---------- A. 위에서 본 걸쇠 하나 (확대)
ax = fig.add_axes([0.03, 0.62, 0.94, 0.31]); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("A. 위에서 본 걸쇠 하나 (확대)", fontsize=15, fontweight="bold", loc="left")
ax.add_patch(Wedge((0, 0), 48.0, 58, 122, width=1.45, fc=pf, ec=pe, lw=1.5))      # 큰 벽
ax.add_patch(Wedge((0, 0), 42.8, 58, 122, width=2.2, fc=rf, ec=pe, lw=1.8))       # 걸쇠 고리
ax.add_patch(Polygon([(-4, 36.3), (4, 36.3), (4, 44.8), (-4, 44.8)], fc="#F6C9C2", ec=RED, lw=2))  # 걸쇠
ax.text(0, 40.2, "걸쇠", fontsize=12, color=RED, ha="center", va="center", fontweight="bold")
ax.text(-27, 33.0, "걸쇠 고리 (두께 2.2)", fontsize=11.5, color=pe, rotation=37, ha="center")
ax.text(-30.5, 38.5, "큰 벽", fontsize=11.5, color=pe, rotation=37, ha="center")
ax.text(19.5, 43.6, "레일 (폭 3.75)", fontsize=11, color=GRY, rotation=-24, ha="center")
darrow(ax, (-4, 49.0), (4, 49.0), BLUE); box(ax, (0, 51.3), "w 걸쇠 폭 — 바깥 조로 양 옆면", BLUE)
darrow(ax, (6.5, 36.3), (6.5, 40.6), ORG); box(ax, (21, 35.3), "p_in 안쪽으로 튀어나온 길이", ORG, fs=11.5)
darrow(ax, (-6.5, 42.3), (-6.5, 44.8), GRN, lw=1.8); box(ax, (-22, 45.0), "p_out 바깥쪽으로 튀어나온 길이", GRN, fs=11.5)
ax.text(0, 29.0, "↓ 가운데 쪽", fontsize=11, color=GRY, ha="center")
ax.set_xlim(-38, 38); ax.set_ylim(28, 54)

# ---------- B. p는 지름으로 재서 계산
axB = fig.add_axes([0.05, 0.47, 0.9, 0.11]); axB.axis("off")
axB.set_title("B. p는 직접 재기 어려우니 마주 보는 걸쇠끼리 재서 계산", fontsize=15, fontweight="bold", loc="left")
axB.text(0.0, 0.70, "• 걸쇠 안쪽 끝끼리 (안쪽 조, 마주 보는 두 걸쇠)  = E_in   →   p_in = (81.2 − E_in) ÷ 2", fontsize=13, color=ORG, transform=axB.transAxes)
axB.text(0.0, 0.38, "• 걸쇠 바깥면끼리 (바깥 조, 아까 사진처럼 걸쇠 위를 문 것) = E_out  →   p_out = (E_out − 85.6) ÷ 2", fontsize=13, color=GRN, transform=axB.transAxes)
axB.text(0.0, 0.06, "  걸쇠가 4개라 마주 보는 쌍이 2쌍 → 둘 다 재기", fontsize=12, color=GRY, transform=axB.transAxes)

# ---------- C. 옆 단면 (뒤집어서 테두리가 위)
axC = fig.add_axes([0.04, 0.10, 0.92, 0.34]); axC.set_aspect("equal"); axC.axis("off")
axC.set_title("C. 옆에서 자른 모습 (포획통 뒤집음 → 테두리가 위)", fontsize=15, fontweight="bold", loc="left")
axC.add_patch(Rectangle((30, -2), 22, 2, fc=pf, ec=pe))                       # 바닥판
axC.add_patch(Rectangle((40.6, 0), 2.2, 13, fc=rf, ec=pe, lw=1.6))            # 걸쇠 고리 (높이 13 가정)
axC.add_patch(Rectangle((46.55, 0), 1.45, 11, fc=pf, ec=pe, lw=1.6))          # 큰 벽 (높이 11 가정)
axC.add_patch(Rectangle((36.3, 9.0), 4.3, 2.0, fc="#F6C9C2", ec=RED, lw=1.8))  # 걸쇠 (안쪽)
axC.add_patch(Rectangle((42.8, 9.0), 1.2, 2.0, fc="#F6C9C2", ec=RED, lw=1.8))  # 걸쇠 (바깥)
axC.plot([30, 30], [-3, 17], color=GRY, lw=1, ls="-.")
axC.text(30.3, 17.5, "← 포획통 가운데 쪽", fontsize=10.5, color=GRY, va="center")
axC.text(31, -3.6, "포획통 바닥판", fontsize=10.5, color=pe)
axC.text(41.7, 13.8, "걸쇠 고리", fontsize=10.5, color=pe, ha="center")
axC.text(47.3, 11.8, "큰 벽", fontsize=10.5, color=pe, ha="center")
axC.text(38.4, 10.0, "걸쇠", fontsize=10, color=RED, ha="center", va="center")
# k1 k2 (걸쇠 고리 끝에서)
darrow(axC, (39.6, 13), (39.6, 11.0), RED, lw=1.6); axC.text(39.3, 12.0, "k1", fontsize=12.5, color=RED, ha="right", va="center", fontweight="bold")
darrow(axC, (35.3, 13), (35.3, 9.0), RED, lw=1.6); axC.text(35.0, 11.0, "k2", fontsize=12.5, color=RED, ha="right", va="center", fontweight="bold")
axC.plot([35.0, 42.8], [13, 13], color=RED, lw=0.8, ls=":")
# g1 g2 (레일 바닥까지)
darrow(axC, (44.3, 13), (44.3, 0), BLUE, lw=1.8); axC.text(44.0, 4.5, "g1", fontsize=12.5, color=BLUE, ha="right", va="center", fontweight="bold")
darrow(axC, (45.6, 11), (45.6, 0), BLUE, lw=1.8); axC.text(45.85, 5.5, "g2", fontsize=12.5, color=BLUE, ha="left", va="center", fontweight="bold")
axC.plot([42.8, 48.5], [11, 11], color=BLUE, lw=0.8, ls=":")
axC.text(49.2, 8.5, "레일", fontsize=11, color=GRY)
axC.set_xlim(28, 62); axC.set_ylim(-5, 19)
# 설명 상자
axC.text(50.5, 16.5, "k1: 걸쇠 고리 끝 → 걸쇠 가까운 면\nk2: 걸쇠 고리 끝 → 걸쇠 먼 면\n     (걸쇠 두께 = k2 − k1)\ng1: 걸쇠 고리 끝 → 레일 바닥\ng2: 큰 벽 끝 → 레일 바닥\n     (두 벽 높이 차 = g1 − g2)\n모두 깊이 막대",
         fontsize=11.5, color="#222222", va="top", linespacing=1.45,
         bbox=dict(boxstyle="round,pad=0.5", fc="#F7F7F7", ec="#BBBBBB"))

# ---------- D. 요령 + 남은 것
fig.text(0.04, 0.085, "요령", fontsize=15, fontweight="bold")
fig.text(0.04, 0.062, "• 테두리가 2 mm로 얇아 캘리퍼스 끝이 안 서면: 자를 테두리 위에 가로로 걸치고 캘리퍼스 끝을 자 윗면에 대고 잰다 → 자 두께만큼 더 나오니, 자 두께를 따로 재서 뺀다.", fontsize=11.5, color="#222222")
fig.text(0.04, 0.042, "• 걸쇠 4개 모두 w · k1 · k2를 잼 (서로 다를 수 있음). 화면이 보이게 한 장씩 사진.", fontsize=11.5, color="#222222")
fig.text(0.04, 0.018, "그다음 남은 것: 차양막 D2i · t (맞물림 확인에 중요) · 빈 구간 b의 낮은 턱 높이 · 토막 끝 계단 · 마커", fontsize=12, color=RED, fontweight="bold")
fig.savefig("gwpk_설명.png", dpi=150, facecolor="white", bbox_inches="tight", pad_inches=0.25)
