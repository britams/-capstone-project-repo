import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch
from PIL import Image
import numpy as np, sys
plt.rcParams.update({"font.family": "Noto Sans CJK JP", "axes.unicode_minus": False})
REPO = "/home/claude/-capstone-project-repo"
OUT = sys.argv[1]
RED, BLUE, ORG, GRN, GRY = "#C0392B", "#1F4E9A", "#D35400", "#2E7D32", "#555555"
BOX = dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.92)

def darrow(ax, p1, p2, c=BLUE, lw=2.4):
    ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="<|-|>", color=c, lw=lw, mutation_scale=16, shrinkA=0, shrinkB=0))
def lead(ax, txt, xy, xyt, c=RED, fs=12.5, ha="center"):
    ax.annotate(txt, xy=xy, xytext=xyt, fontsize=fs, color=c, fontweight="bold", ha=ha, va="center",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=c, lw=1.2, alpha=0.95),
                arrowprops=dict(arrowstyle="-|>", color=c, lw=2.0, mutation_scale=14, shrinkA=2, shrinkB=2))
def lab(ax, xy, txt, c=BLUE, fs=12.5, ha="center"):
    ax.text(*xy, txt, fontsize=fs, color=c, fontweight="bold", ha=ha, va="center",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=c, lw=1.2, alpha=0.95))

# ===================== 1쪽: 트랩 결합부 =====================
fig = plt.figure(figsize=(12, 19.5), dpi=150)
fig.text(0.03, 0.985, "상용 트랩 결합부 — 캘리퍼스로 잴 곳", fontsize=22, fontweight="bold", va="top")
fig.text(0.03, 0.968, "모듈이 끼워지는 곳은 ‘차양막 가운데 구멍 둘레’와 ‘포획통 바닥 테두리’ 두 군데뿐이다. 줄자 값(±1~2 mm)을 0.1 mm로 다시 재고, 빈 칸(높이·홈·걸쇠)을 채운다.",
         fontsize=11.5, color=GRY, va="top", wrap=True)

# A. 차양막 (위에서)
axA = fig.add_axes([0.02, 0.548, 0.47, 0.40])
im = Image.open(f"{REPO}/design/img/실측사진/차양막_구멍_턱.jpg").crop((0, 150, 619, 1000))
axA.imshow(im, extent=(0, 619, 1000, 150)); axA.set_xlim(0, 619); axA.set_ylim(1000, 150); axA.axis("off")
axA.set_title("A. 차양막 가운데 구멍 (위에서 본 모습)", fontsize=14, fontweight="bold", loc="left")
darrow(axA, (150, 552), (450, 552))
lab(axA, (300, 600), "D1 구멍 안지름\n(안쪽 조)")
for x in (50, 550):
    axA.plot([x, x], [552, 905], color=BLUE, lw=1.2, ls="--")
darrow(axA, (50, 895), (550, 895))
lab(axA, (300, 935), "D2 바깥 고리의 바깥지름 (바깥 조)")
lead(axA, "a 토막 길이\n(토막 4개 각각)", (100, 630), (150, 770))
lead(axA, "b 토막 사이 틈 폭", (300, 338), (300, 215))
lead(axA, "c 홈 폭\n(토막~바깥 고리)", (75, 520), (95, 300), c=ORG)
lead(axA, "D2i 바깥 고리 안지름\n+ 고리 두께 t", (540, 640), (480, 790), c=BLUE)

# B. 포획통 바닥 (뒤집어서)
axB = fig.add_axes([0.51, 0.548, 0.47, 0.40])
im = Image.open(f"{REPO}/design/img/실측사진/포획통_바닥.jpg").crop((0, 200, 619, 1050))
axB.imshow(im, extent=(0, 619, 1050, 200)); axB.set_xlim(0, 619); axB.set_ylim(1050, 200); axB.axis("off")
axB.set_title("B. 포획통 바닥 테두리 (뒤집어서 본 모습)", fontsize=14, fontweight="bold", loc="left")
for xy in [(345, 402), (105, 557), (485, 628), (268, 783)]:
    axB.plot(*xy, "o", ms=26, mfc="none", mec=RED, mew=2.5)
lead(axB, "e 걸쇠 4개: 폭 w · 튀어나온 길이 p\n· 테두리 끝에서 걸쇠까지 높이 k", (345, 380), (330, 265))
lead(axB, "D3 테두리 벽 지름\n(안쪽 벽 · 홈 안 · 홈 바깥)\n줄자 67 / 83 / 94", (40, 700), (150, 960), c=BLUE)
lead(axB, "g 홈 깊이 (깊이 막대)", (560, 470), (480, 330), c=ORG)

# C. 반단면 개념도
axC = fig.add_axes([0.04, 0.325, 0.92, 0.19])
axC.set_title("C. 옆에서 자른 모습 (개념도 — 사진 A의 반지름 비율로 그림, 높이는 모르는 값)", fontsize=14, fontweight="bold", loc="left")
axC.set_aspect("equal"); axC.axis("off")
g = "#9CCB7A"; ge = "#4E7A35"
# 차양막 판
axC.add_patch(Rectangle((20, -3), 32, 3, fc=g, ec=ge))
# 안쪽 턱 (collar) r 27.5~31
axC.add_patch(Rectangle((27.5, 0), 3.5, 7, fc=g, ec=ge))
# 토막 r 31~39.5
axC.add_patch(Polygon([(31, 0), (39.5, 0), (39.5, 5), (37.5, 5), (37.5, 6.5), (31, 6.5)], fc=g, ec=ge))
# 바깥 고리 r 41.5~45
axC.add_patch(Rectangle((41.5, 0), 3.5, 9, fc=g, ec=ge))
axC.plot([20, 52], [0, 0], color=ge, lw=0.8)
axC.text(21, -6, "차양막 판", fontsize=11, color=ge)
axC.text(26.0, 9.2, "안쪽 턱", fontsize=10.5, color=ge, ha="center")
axC.text(35.2, 9.2, "토막", fontsize=10.5, color=ge, ha="center")
axC.text(43.2, 11.2, "바깥 고리", fontsize=10.5, color=ge, ha="center")
# 중심선
axC.plot([20, 20], [-4, 14], color=GRY, lw=1, ls="-.")
axC.text(20.3, 13.5, "← 구멍 가운데 쪽", fontsize=10, color=GRY, va="center")
# 치수
darrow(axC, (25.5, 0), (25.5, 7), c=ORG, lw=1.8); axC.text(24.9, 3.5, "h1", fontsize=12, color=ORG, ha="right", va="center", fontweight="bold")
darrow(axC, (32.2, 0.2), (32.2, 6.5), c=ORG, lw=1.8); axC.text(32.7, 3.3, "h2", fontsize=12, color=ORG, ha="left", va="center", fontweight="bold")
darrow(axC, (47, 0), (47, 9), c=ORG, lw=1.8); axC.text(47.5, 4.5, "h3", fontsize=12, color=ORG, ha="left", va="center", fontweight="bold")
darrow(axC, (39.5, 2.5), (41.5, 2.5), c=ORG, lw=1.5); axC.text(40.5, 1.0, "c", fontsize=12, color=ORG, ha="center", fontweight="bold")
darrow(axC, (41.5, 10.2), (45, 10.2), c=BLUE, lw=1.5); axC.text(45.6, 10.2, "t", fontsize=12, color=BLUE, va="center", fontweight="bold")
axC.annotate("토막 끝 계단 높이 (있으면)", xy=(38.5, 5.6), xytext=(36, 15.5), fontsize=10.5, color=RED, ha="center",
             arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.4))
# 포획통 바닥 (오른쪽, 뒤집힌 테두리)
ox = 58
pe = "#7FA7C9"; pf = "#DDEAF5"
axC.add_patch(Rectangle((ox, 12), 32, 2.5, fc=pf, ec=pe))           # 바닥판
axC.add_patch(Rectangle((ox + 13.5, 2), 2.0, 10, fc=pf, ec=pe))     # 안쪽 벽 (r 33.5)
axC.add_patch(Rectangle((ox + 21.5, 0), 1.6, 12, fc=pf, ec=pe))     # 홈 안 벽 (r 41.5)
axC.add_patch(Rectangle((ox + 27.0, 0), 1.6, 12, fc=pf, ec=pe))     # 홈 바깥 벽 (r 47)
axC.add_patch(Rectangle((ox + 15.5, 3), 3.0, 1.6, fc="#F6C9C2", ec=RED))  # 걸쇠
axC.plot([ox, ox], [-1, 16], color=GRY, lw=1, ls="-.")
axC.text(ox + 0.3, 16.5, "← 포획통 가운데 쪽 (뒤집어서 테두리가 아래로)", fontsize=10, color=GRY, va="center")
axC.text(ox + 1, 10.2, "포획통 바닥판", fontsize=10.5, color=pe)
darrow(axC, (ox + 23.1, 0.3), (ox + 23.1, 12), c=ORG, lw=1.6); axC.text(ox + 25.2, 6, "g", fontsize=12, color=ORG, ha="center", va="center", fontweight="bold")
darrow(axC, (ox + 15.5, 1.6), (ox + 18.5, 1.6), c=RED, lw=1.4); axC.text(ox + 17, 0.3, "p", fontsize=12, color=RED, ha="center", fontweight="bold")
darrow(axC, (ox + 19.6, 2), (ox + 19.6, 4.6), c=RED, lw=1.4); axC.text(ox + 20.4, 3.3, "k", fontsize=12, color=RED, va="center", fontweight="bold")
axC.text(ox + 13.5, -2.2, "D3 = 벽마다 안·바깥 지름", fontsize=10.5, color=BLUE)
axC.set_xlim(17, 95); axC.set_ylim(-8, 18)

# D. 기록표
axD = fig.add_axes([0.03, 0.02, 0.94, 0.27]); axD.axis("off")
axD.set_title("D. 기록표 — 지름은 방향을 바꿔 3번, 높이는 2번", fontsize=14, fontweight="bold", loc="left")
rows = [
    ["D1", "차양막 구멍 안지름", "안쪽 조", "55", ""],
    ["D2", "바깥 고리 바깥지름", "바깥 조", "90", ""],
    ["D2i · t", "바깥 고리 안지름 · 고리 두께", "안쪽 조 · 바깥 조", "(사진 어림 약 83)", ""],
    ["a · b", "토막 길이(끝~끝 직선) · 토막 사이 틈 (4곳)", "바깥 조 · 안쪽 조", "—", ""],
    ["c", "토막과 바깥 고리 사이 홈 폭", "안쪽 조 끝", "—", ""],
    ["h1 · h2 · h3", "판 윗면 → 안쪽 턱 · 토막 · 바깥 고리 꼭대기", "깊이 막대", "—", ""],
    ["D3", "포획통 바닥 벽 지름 (안쪽 벽 · 홈 안 · 홈 바깥)", "안쪽 조 · 바깥 조", "67 / 83 / 94", ""],
    ["g", "포획통 홈 깊이 (테두리 끝 → 홈 바닥)", "깊이 막대", "—", ""],
    ["w · p · k", "걸쇠 폭 · 튀어나온 길이 · 테두리 끝에서 높이", "바깥 조 · 깊이 막대", "—", ""],
    ["D4 · D5", "실리콘 포획술 구멍 · 노란 깔때기 좁은 끝 (2쪽)", "안쪽 조", "5 / 19", ""],
]
tb = axD.table(cellText=rows, colLabels=["기호", "어디", "캘리퍼스", "줄자 값 (mm)", "캘리퍼스 값 (mm)"],
               colWidths=[0.11, 0.42, 0.16, 0.15, 0.16], loc="upper left", cellLoc="left")
tb.auto_set_font_size(False); tb.set_fontsize(11.5); tb.scale(1, 1.75)
for (r, c), cell in tb.get_celld().items():
    cell.set_edgecolor("#C8C8C8")
    if r == 0:
        cell.set_facecolor("#3A332B"); cell.get_text().set_color("white"); cell.get_text().set_fontweight("bold")
    elif c == 4:
        cell.set_facecolor("#FBEFD3")
fig.savefig(f"{OUT}/2026-11-02_캘리퍼스_측정위치_1_트랩결합부_승준.png", dpi=150, facecolor="white", bbox_inches="tight", pad_inches=0.25)
plt.close(fig)

# ===================== 2쪽: 캘리퍼스 쓰는 법 · 마커 · D4/D5 =====================
fig = plt.figure(figsize=(12, 19), dpi=150)
fig.text(0.03, 0.985, "캘리퍼스 쓰는 법 · 마커 · 통로 구멍", fontsize=22, fontweight="bold", va="top")

# E. 캘리퍼스
axE = fig.add_axes([0.03, 0.70, 0.94, 0.235]); axE.set_aspect("equal"); axE.axis("off")
axE.set_title("E. 어느 부분으로 재나", fontsize=14, fontweight="bold", loc="left")
st = "#B8BEC6"; se = "#5A6370"
axE.add_patch(Rectangle((0, 0), 150, 8, fc=st, ec=se))                     # 본척
axE.add_patch(Polygon([(0, 0), (8, 0), (8, -22), (4, -26), (0, -22)], fc=st, ec=se))    # 고정 바깥 조
axE.add_patch(Polygon([(2, 8), (7, 8), (7, 16), (4, 19), (2, 16)], fc=st, ec=se))       # 고정 안쪽 조
axE.add_patch(Rectangle((40, -3), 34, 14, fc="#D7DCE2", ec=se))             # 슬라이더
axE.add_patch(Polygon([(40, -3), (48, -3), (48, -22), (44, -26), (40, -22)], fc="#D7DCE2", ec=se))
axE.add_patch(Polygon([(41, 11), (46, 11), (46, 16), (43, 19), (41, 16)], fc="#D7DCE2", ec=se))
axE.add_patch(Rectangle((52, 0), 18, 7, fc="#2F3A45", ec=se)); axE.text(61, 3.5, "12.34", color="#9EF0A0", fontsize=11, ha="center", va="center", family="monospace")
axE.add_patch(Rectangle((150, 3.2), 22, 1.6, fc=st, ec=se))                 # 깊이 막대
axE.text(61, 9.0, "ZERO", fontsize=8, ha="center", color=se)
lead(axE, "바깥 조 (아래 큰 조) — 바깥지름·두께\n(D2, t, 토막 길이, 걸쇠 폭)", (44, -21), (30, -40), c=BLUE, fs=11.5)
lead(axE, "안쪽 조 (위 작은 조) — 구멍 안지름\n(D1, D2i, D4, D5, 틈·홈 폭)", (44, 18), (100, 27), c=BLUE, fs=11.5)
lead(axE, "깊이 막대 — 높이·깊이\n(h1~h3, g, k)", (170, 4), (160, -22), c=ORG, fs=11.5)
lead(axE, "재기 전 조를 닫고 ZERO", (61, 8.5), (110, -38), c=GRN, fs=11.5)
axE.set_xlim(-8, 185); axE.set_ylim(-48, 34)

# F. 마커
axF = fig.add_axes([0.03, 0.43, 0.94, 0.26]); axF.set_aspect("equal"); axF.axis("off")
axF.set_title("F. 샤피 크리에이티브 마커 (펜 홀더 조임 띠 · 캡 컵 크기용, D6 ‘잠정’ 값)", fontsize=14, fontweight="bold", loc="left")
yb = "#F2D35B"; ye = "#8A7420"
# 몸통: 끝(오른쪽) → 팁
axF.add_patch(Rectangle((0, -6), 95, 12, fc="#EEEEEE", ec="#777777"))       # 몸통
axF.add_patch(Rectangle((95, -7.5), 25, 15, fc=yb, ec=ye))                  # 굵은 그립부
axF.add_patch(Polygon([(120, -7.5), (130, -4), (130, 4), (120, 7.5)], fc=yb, ec=ye))  # 앞 원뿔
axF.add_patch(Rectangle((130, -1.8), 6, 3.6, fc="#FFF2A8", ec=ye))           # 팁
axF.add_patch(Polygon([(136, -1.8), (138, -1.0), (138, 1.0), (136, 1.8)], fc="#FFF2A8", ec=ye))
darrow(axF, (0, -14), (138, -14), c=GRY, lw=1.6); axF.text(69, -17.5, "L 전체 길이 (캡 뺀 것)", fontsize=11.5, color=GRY, ha="center", fontweight="bold")
darrow(axF, (60, -6), (60, 6), c=BLUE, lw=1.6); axF.text(58, 0, "d_b 몸통 지름", fontsize=11.5, color=BLUE, ha="right", va="center", fontweight="bold")
darrow(axF, (107, -7.5), (107, 7.5), c=RED, lw=1.8); axF.text(107, 11, "d_g 그립 지름 (홀더가 무는 곳)\n+ d_max 가장 굵은 곳", fontsize=11.5, color=RED, ha="center", fontweight="bold")
darrow(axF, (138, 10), (107, 10), c=RED, lw=1.2)
axF.text(124, 20, "x: 팁 끝 → 가장 굵은 곳 거리", fontsize=11, color=RED, ha="center")
darrow(axF, (133, -3.5), (133, 3.5), c=ORG, lw=1.4)
axF.annotate("d_tip 팁 지름 · l_tip 팁 나온 길이", xy=(136, -2), xytext=(140, -26), fontsize=11.5, color=ORG, ha="center", fontweight="bold",
             arrowprops=dict(arrowstyle="-|>", color=ORG, lw=1.4))
axF.text(0, 20, "캡도: 캡 바깥지름·안쪽 깊이 (캡 컵 참고)", fontsize=11, color=GRY)
axF.set_xlim(-8, 165); axF.set_ylim(-32, 26)
fig.text(0.05, 0.445, "지금 값: 그립 14.7 · 최대 18.9 mm (판매처 사양). 그림의 모양은 개념도 — 굵은 곳 위치는 실물로 확인", fontsize=11, color=GRY)

# G. D4 D5 (서현 실측위치 그림에서 잘라 씀)
src = Image.open(f"{REPO}/design/img/상용트랩_실측위치.jpg")
W, H = src.size
c1 = src.crop((0, int(H * 0.548), W // 2, H)); c2 = src.crop((W // 2, int(H * 0.548), W, H))
axG1 = fig.add_axes([0.03, 0.02, 0.45, 0.37]); axG1.imshow(c1); axG1.axis("off")
axG1.set_title("G. D4 실리콘 포획술 구멍 — 손대지 않은 채\n안쪽 조를 살짝 (벌어지면 값이 커짐)", fontsize=12.5, fontweight="bold", loc="left")
axG2 = fig.add_axes([0.52, 0.02, 0.45, 0.37]); axG2.imshow(c2); axG2.axis("off")
axG2.set_title("H. D5 노란 깔때기 좁은 끝 안지름 — 안쪽 조\n(말벌이 실제로 지나가는 크기)", fontsize=12.5, fontweight="bold", loc="left")
fig.savefig(f"{OUT}/2026-11-02_캘리퍼스_측정위치_2_마커_통로_승준.png", dpi=150, facecolor="white", bbox_inches="tight", pad_inches=0.25)
print("ok")
