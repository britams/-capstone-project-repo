# -*- coding: utf-8 -*-
"""S4 그림: 4-1 전체 외력·절단면 + M1~M6 자유물체도 (개략, 치수는 D5 4차 모델)
실행: python3 design/calc/s4_figs.py → design/img/S4_*.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Polygon
plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "img")
os.makedirs(OUT, exist_ok=True)
RED, BLUE, GRAY, DARK = "#c0392b", "#1f4e9a", "#9aa0a6", "#333333"


def arrow(ax, x0, y0, x1, y1, c=RED, lw=2.2, txt=None, dx=4, dy=0, fs=12, ha="left"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=16, color=c, lw=lw))
    if txt:
        ax.text(x1 + dx if dy == 0 else x0 + dx, (y1 if dy == 0 else y0) + dy, txt, color=c, fontsize=fs, ha=ha, va="center")


def box(ax, x, y, w, h, fc="#e8eaed", ec=DARK, lw=1.2, ls="-", txt=None, fs=10):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, ls=ls))
    if txt:
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, color=DARK)


def cut(ax, x0, y0, x1, y1, n):
    ax.plot([x0, x1], [y0, y1], color=BLUE, lw=1.6, ls=(0, (8, 3, 1.5, 3)))
    ax.text(x1 + 3, y1, n, color=BLUE, fontsize=15, fontweight="bold", va="center")


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------- 4-1 전체 외력과 절단면 (정면 개략, 단위 mm) ----------
fig, ax = plt.subplots(figsize=(9.2, 10))
c = 170
for x in (-c, c):
    box(ax, x - 10, 0, 20, 610, fc="#c9ced6")                      # 기둥
for z in (0, 180, 452, 590):
    box(ax, -c - 10, z, 2 * c + 20, 20, fc="#c9ced6")               # 단
ax.text(-c - 14, 600, "100 프레임", fontsize=9, ha="right", va="center")
box(ax, -130, 200, 230, 5, fc="#dfe6ee")
ax.text(-125, 212, "101 받침판", fontsize=9)
box(ax, 32, 330, 46, 56, fc="#f3f4f6", txt="120\n마킹실", fs=9)
box(ax, 32, 205, 46, 125, fc="#f3f4f6", txt="150\n승강부", fs=9)
box(ax, 50, 400, 80, 90, fc="#dbe3f3", txt="200 XYZ", fs=9)
box(ax, 42.5, 586, 25, 14, fc="#f3f4f6")
ax.text(72, 580, "180 카메라", fontsize=9, va="center")
box(ax, -70, 610, 140, 5, fc="#dfe6ee")
box(ax, -45, 615, 90, 10, fc="#dfe6ee")
ax.text(-50, 621, "104", fontsize=9, va="center", ha="right")
ax.add_patch(Circle((0, 725), 100, fc="#f6f6f6", ec=GRAY, ls="--"))
ax.text(0, 760, "상용 포획통 (REF)", ha="center", va="center", fontsize=10, color="#666")
ax.add_patch(Rectangle((-100, 0), 200, 145, fc="none", ec=GRAY, ls="--"))
ax.text(0, 70, "상용 트랩 몸통 (REF)\n— 모듈과 접촉 없음", ha="center", fontsize=9, color="#666")
# 외력
arrow(ax, -80, 560, -80, 480, c=RED); ax.plot([-80], [560], "o", color=RED)
ax.text(-72, 540, "W_m (모듈·프레임 자중, 질량중심)", color=RED, fontsize=11, va="center")
arrow(ax, 0, 700, 0, 628, c=RED); ax.text(10, 668, "W_d (포획통 자중 → 104)", color=RED, fontsize=11, va="center")
for x in (-c, c):
    arrow(ax, x, -70, x, -4, c=RED); ax.text(x + 8, -55, ("N_L" if x < 0 else "N_R"), color=RED, fontsize=12)
# 절단면 (XYZ 상자 안 높이별) — 번호는 오른쪽 열
for y, n, x0, x1 in ((268, "①", 25, 85), (478, "②", 50, 130), (412, "③", 50, 130), (428, "④", 50, 130), (446, "⑤", 50, 130), (462, "⑥", 50, 130)):
    ax.plot([x0, x1], [y, y], color=BLUE, lw=1.6, ls=(0, (8, 3, 1.5, 3)))
    ax.plot([x1, 205], [y, y if n == "①" else 330 + (478 - y) * 0 + {"②": 520, "③": 400, "④": 430, "⑤": 460, "⑥": 490}.get(n, y) - 330], color=BLUE, lw=0.6)
    yy = y if n == "①" else {"②": 520, "③": 400, "④": 430, "⑤": 460, "⑥": 490}[n]
    ax.text(208, yy, n, color=BLUE, fontsize=15, fontweight="bold", va="center")
lab = {"①": "승강 나사 155", "②": "Y 나사 208", "③": "홀더 202", "④": "Z 서보 205", "⑤": "X 빔 212", "⑥": "X 봉 213"}
for n, yy in (("①", 268), ("②", 520), ("③", 400), ("④", 430), ("⑤", 460), ("⑥", 490)):
    ax.text(232, yy, lab[n], color=BLUE, fontsize=9, va="center")
ax.set_xlim(-330, 300); ax.set_ylim(-90, 840); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("도 S4-1  전체 구성도(정면 개략)의 외력과 가상 절단면 ①~⑥", fontsize=13)
save(fig, "S4_4-1_외력_절단면.png")

# ---------- M1 승강 나사 ----------
fig, ax = plt.subplots(figsize=(6, 6.4))
box(ax, -20, 0, 40, 6, fc="#f3f4f6", txt="140 바닥", fs=9)
ax.add_patch(Rectangle((-6, 6), 12, 6, fc="#ffe9a8", ec=DARK)); ax.text(-8, 9, "H", fontsize=9, va="center", ha="right")
box(ax, -2, -60, 4, 60, fc="#d0d4da")
ax.text(4, -30, "147 밀대", fontsize=9)
box(ax, -18, -80, 36, 14, fc="#dbe3f3", txt="158 캐리지(너트)", fs=9)
box(ax, -4, -150, 8, 70, fc="#c9ced6")
ax.text(6, -135, "155 T8 나사", fontsize=9)
cut(ax, -30, -92, 22, -92, "①")
arrow(ax, 0, 34, 0, 13, c=RED); ax.text(-4, 30, "F_p (격자에 붙이는 힘의 반작용)", color=RED, fontsize=10, ha="right", va="center")
arrow(ax, 30, 3, 30, -18, txt="W_f", fs=11)
arrow(ax, 0, -125, 0, -100, c=BLUE, txt="F (나사 축력)", dx=8, fs=11)
ax.annotate("", xy=(14, -110), xytext=(-14, -110), arrowprops=dict(arrowstyle="->", color=BLUE, connectionstyle="arc3,rad=0.5", lw=2))
ax.text(-16, -118, "T (구동 토크)", color=BLUE, fontsize=11, ha="right")
ax.text(-60, -165, "l = 8 mm, d_m = 7 mm, α = 15°, μ = 0.15", fontsize=10)
ax.set_xlim(-65, 75); ax.set_ylim(-175, 45); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("M1  절단 ①: 승강 바닥·캐리지 + T8 나사", fontsize=12)
save(fig, "S4_M1_FBD.png")

# ---------- M2 Y 캐리지 이송 ----------
fig, ax = plt.subplots(figsize=(7, 4.6))
ax.plot([-60, 60], [0, 0], color=GRAY, lw=4); ax.plot([-60, 60], [30, 30], color=GRAY, lw=4)
ax.text(62, 0, "207 Y 봉 (z 445)", fontsize=9, va="center"); ax.text(62, 30, "207 Y 봉 (z 475)", fontsize=9, va="center")
box(ax, -15, -10, 30, 50, fc="#dbe3f3", txt="206 + 201~205\n(m_y)", fs=9)
arrow(ax, -45, 15, -16, 15, c=BLUE, txt="F (나사 추력)", dx=-62, dy=8, fs=10)
arrow(ax, 30, 15, 50, 15, c=RED); ax.text(28, 21, "f = μ·N (봉 마찰)", color=RED, fontsize=10)
arrow(ax, 0, 46, 0, 62, c=RED, txt="N (봉 반력: 무게 + 편심 짝힘 ±H)", dx=3, fs=10)
arrow(ax, 0, -14, 0, -32, txt="W = m_y·g", dx=4, fs=10)
ax.text(-58, -48, "운동: 0 → v (2 mm/s)를 0.1 s에 → 관성력 m·a 더함", fontsize=10)
ax.set_xlim(-75, 90); ax.set_ylim(-55, 75); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("M2  절단 ②: Y 캐리지 (X 빔도 같은 꼴)", fontsize=12)
save(fig, "S4_M2_FBD.png")

# ---------- M3 홀더 + 말벌 ----------
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 5.4))
box(a1, -8, 0, 16, 60, fc="#fafafa", txt="201\n마커", fs=9)
box(a1, 8, 20, 12, 30, fc="#dbe3f3", txt="202", fs=9)
a1.plot([20, 20], [-10, 75], color=GRAY, lw=3); a1.text(22, 70, "206 캐리지 면", fontsize=9)
arrow(a1, -14, 40, -14, 22, txt="W_h", dx=-2, fs=11, ha="right")
arrow(a1, 14, 72, 14, 51, c=BLUE, txt="F_s (204 스프링)", dx=-30, dy=6, fs=10)
arrow(a1, 0, -24, 0, -2, txt="N_tip", dx=3, fs=11)
arrow(a1, 26, 35, 26, 45, c=DARK, txt="f (레일 마찰, 내려와 멈춘 뒤 위쪽)", dx=2, fs=9)
cut(a1, -25, 55, 30, 55, "③")
a1.set_xlim(-40, 70); a1.set_ylim(-30, 85); a1.set_aspect("equal"); a1.axis("off"); a1.set_title("(a) 홀더 + 마커", fontsize=11)
box(a2, -20, 0, 40, 8, fc="#ffe9a8", txt="H", fs=10)
a2.plot([-34, 10], [8.6, 8.6], color=DARK, lw=3); a2.plot([14, 34], [8.6, 8.6], color=DARK, lw=3)
a2.text(36, 3.5, "130 격자", fontsize=9, va="center")
arrow(a2, 0, -26, 0, -1, c=RED); a2.text(-3, -20, "F_p (바닥 140)", color=RED, fontsize=11, ha="right")
arrow(a2, -14, 18, -14, 8.8, c=BLUE); a2.text(-16, 22, "R_g", color=BLUE, fontsize=11, ha="right")
arrow(a2, 12, 36, 12, 8.4, c=RED); a2.text(15, 32, "F_tip = N_tip (마커 팁)", color=RED, fontsize=11)
a2.text(-34, -40, "평형: F_p = R_g + F_tip,  R_g ≥ 0 이어야 격자에 붙어 있음", fontsize=10)
a2.set_xlim(-40, 75); a2.set_ylim(-45, 42); a2.set_aspect("equal"); a2.axis("off"); a2.set_title("(b) 말벌 (찍는 순간)", fontsize=11)
fig.suptitle("M3  절단 ③: 찍는 힘", fontsize=12)
save(fig, "S4_M3_FBD.png")

# ---------- M4 서보 혼 ----------
fig, ax = plt.subplots(figsize=(7.5, 6))
ax.add_patch(Circle((0, 0), 3, fc="#c9ced6", ec=DARK))
ax.plot([0, 11.9 * 0.866], [0, 11.9 * 0.5], color=DARK, lw=5)
ax.text(-12, -6, "205 SG90 축", fontsize=9)
arrow(ax, 10.3, 14, 10.3, 6.2, c=RED); ax.text(12, 14, "F_lift (홀더 탭이 혼을 누름)", color=RED, fontsize=11, va="center")
ax.annotate("", xy=(-4, 4), xytext=(-4, -4), arrowprops=dict(arrowstyle="->", color=BLUE, connectionstyle="arc3,rad=-0.8", lw=2))
ax.text(-15, 2, "T", color=BLUE, fontsize=12)
ax.text(2, -9, "r ≤ 11.9 mm (혼 길이 = 팔의 상한)", fontsize=10)
cut(ax, 2, -6, 2, 6, "④")
ax.set_xlim(-18, 25); ax.set_ylim(-12, 26); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("M4  절단 ④: 펜 들기 서보 혼", fontsize=12)
save(fig, "S4_M4_FBD.png")

# ---------- M5 X 빔 끼임: (a) 위에서 봄 = 요(yaw), (b) 옆에서 봄 = 피치 ----------
fig, (ax, bx) = plt.subplots(1, 2, figsize=(12.5, 6.2), gridspec_kw=dict(width_ratios=[1.15, 1]))
ax.plot([-40, 60], [0, 0], color=GRAY, lw=4); ax.plot([-40, 60], [122, 122], color=GRAY, lw=4)
ax.text(62, 0, "213 봉 A (y = −65)", fontsize=9, va="center"); ax.text(62, 122, "213 봉 B (y = +57)", fontsize=9, va="center")
box(ax, -12, -8, 24, 16, fc="#dbe3f3", txt="A", fs=10); box(ax, -12, 114, 24, 16, fc="#dbe3f3", txt="B", fs=10)
ax.add_patch(Rectangle((-3, 8), 6, 106, fc="#eef1f7", ec=DARK))
ax.text(5, 61, "빔 (207·208·206 …)", fontsize=9, rotation=90, va="center")
arrow(ax, -38, -3, -13, -3, c=BLUE, txt="P (X 나사, 봉 A 선 위)", dx=-36, dy=-8, fs=10)
arrow(ax, 12, 3, 30, 3, txt="μW_A", dx=1, dy=7, fs=10)
arrow(ax, 12, 125, 30, 125, txt="μW_B", dx=14, dy=7, fs=10)
# B 부싱 양 끝 측압 짝힘 (k = 1) / 대각 접촉 (k = 0.5: A 앞 + B 뒤)
arrow(ax, 12, 106, 12, 113, c=DARK); arrow(ax, -12, 138, -12, 131, c=DARK)
ax.text(14, 104, "Q", fontsize=10); ax.text(-24, 140, "Q", fontsize=10)
arrow(ax, -12, 16, -12, 9, c="#7a7a7a"); ax.text(-24, 18, "Q (k = 0.5)", fontsize=8, color="#7a7a7a")
ax.annotate("", xy=(-12, 150), xytext=(12, 150), arrowprops=dict(arrowstyle="<->", color=DARK))
ax.text(-14, 154, "L = 24 (LM8UU)", fontsize=10)
ax.annotate("", xy=(-30, 0), xytext=(-30, 122), arrowprops=dict(arrowstyle="<->", color=DARK))
ax.text(-46, 61, "d = 122", fontsize=11, rotation=90, va="center")
ax.text(-58, -38, "k = 1: 짝힘 접점 둘 다 B → 요 끼임 2μd/L ≥ 1\nk = 0.5: A·B에 하나씩(서랍처럼 대각) → μd/L ≥ 1", fontsize=9)
cut(ax, 40, 20, 40, 100, "⑤")
ax.set_xlim(-62, 112); ax.set_ylim(-52, 165); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("(a) 위에서 봄 — 요(yaw)", fontsize=11)
bx.plot([-50, 70], [55, 55], color=GRAY, lw=4); bx.text(72, 55, "213 봉 (z 480)", fontsize=9, va="center")
bx.plot([-50, 70], [0, 0], color=GRAY, lw=3, ls="--"); bx.text(72, 0, "214 X 나사 (z 425)", fontsize=9, va="center")
box(bx, -12, 47, 24, 16, fc="#dbe3f3", txt="부싱", fs=9)
bx.add_patch(Rectangle((-8, -6), 16, 53, fc="#eef1f7", ec=DARK)); bx.text(-10, 25, "끝 블록 A\n(212)", fontsize=9, ha="right")
arrow(bx, -38, 0, -9, 0, c=BLUE, txt="P", dx=-12, dy=6, fs=11)
arrow(bx, 12, 58, 30, 58, txt="μ(W + 2Q_p)", dx=1, dy=7, fs=10)
arrow(bx, -12, 71, -12, 64, c=DARK); arrow(bx, 12, 39, 12, 46, c=DARK)
bx.text(-24, 73, "Q_p", fontsize=10); bx.text(14, 36, "Q_p", fontsize=10)
bx.annotate("", xy=(30, 0), xytext=(30, 55), arrowprops=dict(arrowstyle="<->", color=DARK)); bx.text(34, 27, "h = 55", fontsize=10, rotation=90, va="center")
bx.text(-50, -28, "피치: Q_p L = h P → 2μh/L ≥ 1 이면 끼임\n합침: 2μ(k d + h)/L ≥ 1 → μ_c = L / 2(k d + h)", fontsize=9)
bx.set_xlim(-55, 110); bx.set_ylim(-40, 90); bx.set_aspect("equal"); bx.axis("off")
bx.set_title("(b) 옆에서 봄 (−y 쪽) — 피치", fontsize=11)
fig.suptitle("M5  절단 ⑤: 한쪽 구동 X 빔의 끼임 (요 + 피치)", fontsize=12)
save(fig, "S4_M5_FBD.png")

# ---------- M6 봉 처짐 ----------
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.plot([0, 153], [0, 0], color=DARK, lw=5)
ax.add_patch(Polygon([[0, -1], [-6, -10], [6, -10]], fc="#c9ced6", ec=DARK))
ax.add_patch(Polygon([[153, -1], [147, -10], [159, -10]], fc="#c9ced6", ec=DARK))
arrow(ax, 76.5, 30, 76.5, 3, c=RED); ax.text(80, 26, "F = R_A (봉 A 몫 61~71 %) / 최악: 빔 전체", color=RED, fontsize=9)
arrow(ax, 0, -30, 0, -11, c=BLUE, txt="F/2", dx=3, fs=10); arrow(ax, 153, -30, 153, -11, c=BLUE, txt="F/2", dx=3, fs=10)
ax.annotate("", xy=(0, -22), xytext=(153, -22), arrowprops=dict(arrowstyle="<->", color=DARK)); ax.text(30, -33, "L = 153 mm (Ø8 강봉, 받침 중심 간 141보다 길게 = 보수적)", fontsize=9)
cut(ax, 35, -18, 35, 10, "⑥")
ax.set_xlim(-15, 185); ax.set_ylim(-42, 40); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("M6  절단 ⑥: X 고정 봉 (단순지지 보, 가운데 하중 = 최악 위치)", fontsize=12)
save(fig, "S4_M6_FBD.png")
print("ok", sorted(f for f in os.listdir(OUT) if f.startswith("S4_")))
