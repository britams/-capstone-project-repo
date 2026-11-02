import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Rectangle, Polygon
import numpy as np
plt.rcParams.update({"font.family": "Noto Sans CJK JP", "axes.unicode_minus": False})
RED, BLUE, ORG, GRY = "#C0392B", "#1F4E9A", "#D35400", "#555555"
pf, pe = "#DDEAF5", "#5B87B0"
fig = plt.figure(figsize=(12, 15.5), dpi=150)
fig.text(0.03, 0.985, "D3 — 포획통 바닥에서 잴 지름 3개 (뒤집어 놓고)", fontsize=21, fontweight="bold", va="top")
fig.text(0.03, 0.962, "D3는 ‘걸쇠 고리’ 하나의 안·바깥 지름 2개와, 그 바깥 큰 벽의 안지름 1개다. 크기는 개념도(비율만 대략).", fontsize=12, color=GRY, va="top")
def darrow(ax, p1, p2, c, lw=2.4):
    ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="<|-|>", color=c, lw=lw, mutation_scale=16, shrinkA=0, shrinkB=0))
def box(ax, xy, t, c, fs=13):
    ax.text(*xy, t, fontsize=fs, color=c, fontweight="bold", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=c, lw=1.5))
# ---------- 위에서 본 모습
ax = fig.add_axes([0.03, 0.40, 0.94, 0.52]); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("A. 포획통 바닥을 뒤집어 위에서 본 모습", fontsize=15, fontweight="bold", loc="left")
ax.add_patch(Circle((0, 0), 56, fc="#F3F7FB", ec=pe, lw=1))          # 포획통 몸
ax.add_patch(Wedge((0, 0), 48.5, 0, 360, width=1.5, fc=pf, ec=pe, lw=1.5))   # 바깥 큰 벽 (안쪽면 r 47)
ax.add_patch(Wedge((0, 0), 41.5, 0, 360, width=1.5, fc="#BFD6EC", ec=pe, lw=1.8))  # 걸쇠 고리 (r 40~41.5)
ax.add_patch(Circle((0, 0), 33, fc="white", ec="#AAB8C6", lw=1, ls="--"))   # 바닥 판
for k in range(18):
    a = np.radians(k * 20); r0, r1 = 12, 28
    ax.plot([r0*np.cos(a), r1*np.cos(a)], [r0*np.sin(a), r1*np.sin(a)], color="#C9D3DC", lw=5, solid_capstyle="round")
ax.add_patch(Circle((0, 0), 6, fc="#E8EEF3", ec="#9AA9B7")); ax.text(0, 0, "D4", fontsize=10, ha="center", va="center", color=GRY)
for ang in (90, 180, 270, 0):
    a = np.radians(ang); c, s = np.cos(a), np.sin(a)
    ax.add_patch(Polygon([((40 - 3.5)*c - 3*s, (40 - 3.5)*s + 3*c), ((41.5 + 1)*c - 3*s, (41.5 + 1)*s + 3*c),
                          ((41.5 + 1)*c + 3*s, (41.5 + 1)*s - 3*c), ((40 - 3.5)*c + 3*s, (40 - 3.5)*s - 3*c)], fc="#F6C9C2", ec=RED, lw=1.5))
# 치수 (걸쇠 피해서 45° 방향)
d = np.radians(45); e = np.array([np.cos(d), np.sin(d)])
darrow(ax, tuple(-40 * e), tuple(40 * e), BLUE)
box(ax, (-28, 10), "D3a 걸쇠 고리 안지름\n안쪽 조 · 매끈한 안쪽 벽끼리", BLUE)
d2 = np.radians(-30); e2 = np.array([np.cos(d2), np.sin(d2)])
for sgn in (-1, 1):
    p = sgn * 41.5 * e2; ax.plot([p[0], p[0] + 0], [p[1], p[1]], "o", color=ORG, ms=6)
darrow(ax, tuple(-41.5 * e2), tuple(41.5 * e2), ORG)
box(ax, (38, -48), "D3b 걸쇠 고리 바깥지름\n바깥 조 · 매끈한 바깥 벽끼리\n(아까 사진에서 잰 곳, 걸쇠 피해서)", ORG, fs=12)
d3 = np.radians(112); e3 = np.array([np.cos(d3), np.sin(d3)]); darrow(ax, tuple(-47 * e3), tuple(47 * e3), "#2E7D32")
box(ax, (-2, -10), "D3c 바깥 큰 벽 안지름\n안쪽 조 · 걸쇠 피해서", "#2E7D32", fs=12)
ax.annotate("걸쇠 4개 (w · p · k)", xy=(0, 42.5), xytext=(30, 55), fontsize=13, color=RED, fontweight="bold", ha="center",
            arrowprops=dict(arrowstyle="-|>", color=RED, lw=2))
ax.annotate("레일 = 걸쇠 고리와 큰 벽 사이 틈\n(차양막 바깥 고리가 들어감, 깊이 g)", xy=(-44.2, -12), xytext=(-40, -55), fontsize=12.5, color=GRY, fontweight="bold", ha="center",
            arrowprops=dict(arrowstyle="-|>", color=GRY, lw=1.8))
ax.text(-58, 52, "서현 줄자 값: 67 / 83 / 94\n(어느 벽인지 기록 없음)", fontsize=11.5, color=GRY, va="top")
ax.set_xlim(-62, 62); ax.set_ylim(-62, 62)
# ---------- 끼워진 단면 (추정)
ax2 = fig.add_axes([0.05, 0.03, 0.9, 0.33]); ax2.set_aspect("equal"); ax2.axis("off")
ax2.set_title("B. 끼우면 이렇게 맞물리는 것으로 보임 (추정 — D3 재면 확인)", fontsize=15, fontweight="bold", loc="left")
g, ge = "#9CCB7A", "#4E7A35"
ax2.add_patch(Rectangle((26, -3), 24, 3, fc=g, ec=ge))
ax2.add_patch(Rectangle((28.35, 0), 3.0, 9.9, fc=g, ec=ge))           # 안쪽 턱 9.9
ax2.add_patch(Rectangle((31.35, 0), 8.2, 8.9, fc=g, ec=ge))           # 토막 8.9
ax2.add_patch(Rectangle((41.5, 0), 3.3, 8.0, fc=g, ec=ge))            # 바깥 고리 8.0 (바깥 r 44.8)
# 포획통 (위에서 내려옴)
ax2.add_patch(Rectangle((26, 12.5), 24, 2, fc=pf, ec=pe))
ax2.add_patch(Rectangle((39.8, 3.0), 1.5, 9.5, fc="#BFD6EC", ec=pe))  # 걸쇠 고리
ax2.add_patch(Rectangle((37.0, 9.4), 2.8, 1.2, fc="#F6C9C2", ec=RED))  # 걸쇠 (토막 위에 걸림)
ax2.add_patch(Rectangle((46.3, 1.0), 1.5, 11.5, fc=pf, ec=pe))        # 바깥 큰 벽
ax2.plot([26, 26], [-4, 16], color=GRY, lw=1, ls="-.")
ax2.text(26.3, 16.5, "← 가운데 쪽", fontsize=10.5, color=GRY, va="center")
for t, xy, c in [("차양막 안쪽 턱 9.9", (29.8, -5.5), ge), ("토막 8.9", (35.4, -5.5), ge), ("바깥 고리 8.0", (43.2, -5.5), ge)]:
    ax2.text(*xy, t, fontsize=10.5, color=c, ha="center")
ax2.text(41.0, 17.2, "포획통 걸쇠 고리 → 토막과 바깥 고리 사이 홈(c)에 들어감", fontsize=11, color=pe, ha="center", fontweight="bold")
ax2.annotate("", xy=(40.5, 12.4), xytext=(40.5, 16.3), arrowprops=dict(arrowstyle="-|>", color=pe, lw=1.5))
ax2.text(51.5, 6, "차양막 바깥 고리(89.6)\n→ 포획통 레일에 들어감", fontsize=11, color=ge, va="center", fontweight="bold")
ax2.text(36.6, 11.3, "걸쇠가 토막 위에 걸려 잠김 →", fontsize=10.5, color=RED, ha="right", va="center")
ax2.set_xlim(24, 62); ax2.set_ylim(-8, 19)
fig.savefig("D3_설명.png", dpi=150, facecolor="white", bbox_inches="tight", pad_inches=0.25)
