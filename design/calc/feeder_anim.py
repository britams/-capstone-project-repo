# -*- coding: utf-8 -*-
"""급이 방 원리 동영상 (서현, 2026-11-10, CAP-AI-56) — 고친 설계 치수(cad/D5g_feeder_uln.py FD)로 옆 단면을 그림.
장면: ① 채우기 → ② 물 높이 유지(공기 방울) → ③ 솜이 빨아올림 + 말벌 급이 → ④ 더운 날: 예전 50 mL는 넘침 / 지금 15 mL는 안 넘침
결과: design/img/feeder/급이방_원리.mp4 · .gif · 장면별 png
"""
import os, sys, math
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(REPO, "cad"))
import feeder_check as FC
F = FC.load_fd()
OUT = os.path.join(REPO, "design", "img", "feeder")
plt.rcParams.update({"font.family": "Noto Sans CJK JP", "font.size": 12})
WAT, PRT, GR, COT, RED, GRN = "#9ecae1", "#e8a33c", "#8a8a8a", "#f4f1e6", "#d62728", "#2ca02c"
HOLE0, HOLE1 = F["wall_hole_z"] - F["wall_hole_r"], F["wall_hole_z"] + F["wall_hole_r"]


def roll(ax, wet):
    t = np.array([F["tip_y"], F["tip_z"]]); e = np.array([F["end_y"], F["end_z"]])
    d = (t - e) / np.linalg.norm(t - e); n = np.array([-d[1], d[0]]); r = F["roll_r"]
    ax.add_patch(Polygon([e + n * r, t + n * r, t - n * r, e - n * r], fc=COT, ec="#776", lw=1.2, zorder=4))
    if wet > 0:   # 젖은 부분 (바깥 끝 → 안 끝)
        m = e + (t - e) * wet
        ax.add_patch(Polygon([e + n * r, m + n * r, m - n * r, e - n * r], fc="#7fb3d5", ec="none", alpha=.85, zorder=5))


def scene(ax, level, title, sub, tube_r=None, tube_water=60, wet=1.0, floor_lift=0, bubble=None, hornet_drink=False,
          spill=False, tube_up=False, thumb=False, old=False):
    ax.clear(); ax.set_xlim(-28, 132); ax.set_ylim(326, 500); ax.set_aspect("equal"); ax.axis("off")
    ax.text(-26, 497, title, fontsize=17, fontweight="bold", va="top")
    ax.text(-26, 487, sub, fontsize=12, va="top")
    tr = tube_r or F["tube_r"]
    # 마킹실
    for y0 in (-23, 20):
        ax.add_patch(Rectangle((y0, 335), 3, 50, fc=GR))
    ax.add_patch(Rectangle((20, HOLE0), 3, HOLE1 - HOLE0, fc="white", zorder=3))
    ax.add_patch(Rectangle((-23, 385), 46, 1.5, fc="#5aa9d6")); ax.text(0, 388, "격자", ha="center", fontsize=10)
    zt = 341 + floor_lift
    ax.add_patch(Rectangle((-19.5, zt - 6), 39, 6, fc="#bdbdbd", ec="k")); ax.text(0, zt - 3, "바닥", ha="center", va="center", fontsize=10)
    ax.text(-6, 352 if floor_lift < 20 else 345, "마킹실", fontsize=13, color="#555")
    # 말벌 (머리 = +y 쪽)
    hx = 6 if hornet_drink else -8
    body = Polygon([(hx - 14, zt), (hx, zt), (hx + 3, zt + 4.5), (hx - 12, zt + 7.5)], fc="#2b2b2b", zorder=6)
    ax.add_patch(body); ax.add_patch(Circle((hx + 4.5 + (8 if hornet_drink else 0), zt + 3.2), 3.2, fc="#2b2b2b", zorder=6))
    if hornet_drink:
        ax.plot([hx + 15, 20.3], [zt + 3, zt + 3.5], color="#2b2b2b", lw=2, zorder=6)
    # 물길·그릇
    ax.add_patch(Rectangle((23, 361), 89.5, 3, fc=PRT)); ax.add_patch(Rectangle((112.5, 361), 2.5, 39, fc=PRT))
    ax.add_patch(Rectangle((23, 364), 89.5, level - 364, fc=WAT, ec="none"))
    if spill:
        ax.add_patch(Polygon([(23, HOLE0), (20, HOLE0), (20, 372), (16, 360), (12, 341 + floor_lift), (17, 341 + floor_lift), (19, 362)], fc=RED, alpha=.55, zorder=7))
        ax.text(-21, 378, "설탕물이\n마킹실로 샘", color=RED, fontsize=13, fontweight="bold", zorder=8)
    # 튜브
    if tube_up:   # 채우는 중 (바로 세움, 그릇 밖 위)
        ax.add_patch(Rectangle((95 - tr, 400), 2 * tr, 80, fc="none", ec="#444", lw=1.6))
        ax.add_patch(Rectangle((95 - tr + 0.8, 402), 2 * tr - 1.6, tube_water, fc=WAT, ec="none"))
    else:
        mz = F["mouth_z"] if not old else 369.0
        ax.add_patch(Rectangle((95 - tr, mz), 2 * tr, 100, fc="none", ec="#444", lw=1.6, zorder=3))
        ax.add_patch(Rectangle((95 - tr + 0.8, mz), 2 * tr - 1.6, tube_water, fc=WAT, ec="none", zorder=2))
        ax.text(95, mz + tube_water + 12, "공기", ha="center", fontsize=11)
        ax.text(95, mz + tube_water / 2, "설탕\n물", ha="center", va="center", fontsize=11, zorder=5)
        for z in (424, 434): ax.plot([95 + tr, 95 + tr + 6], [z, z], color=PRT, lw=3)
        if thumb:
            ax.add_patch(Circle((95, mz - 3), 7, fc="#f1c27d", ec="#a0522d", zorder=9)); ax.text(105, mz - 6, "엄지로 막고 뒤집음", fontsize=11)
        if bubble is not None:
            ax.add_patch(Circle((95, bubble), 2.6, fc="white", ec="#3a7dbf", lw=1.5, zorder=4))
    roll(ax, wet)
    ax.plot([20, 125], [level, level], ls="--", color="#3a7dbf", lw=1)
    ax.text(126, level, "물 %.1f" % level, color="#3a7dbf", fontsize=10, va="center")
    ax.plot([20, 26], [HOLE0, HOLE0], color=RED, lw=2, zorder=10); ax.annotate("벽 구멍 아래 끝 %.1f" % HOLE0, xy=(24, HOLE0), xytext=(40, 352), color=RED, fontsize=10, zorder=10, arrowprops=dict(arrowstyle="->", color=RED))


FR = 24
SC = [  # (프레임 수, 함수)
    (60, "fill"), (70, "flip"), (90, "keep"), (90, "wick"), (90, "drink"), (80, "hot_old"), (80, "hot_new")]
TOTAL = sum(n for n, _ in SC)
fig, ax = plt.subplots(figsize=(12.8, 9.2)); fig.subplots_adjust(0, 0, 1, 1)
k_hot = FC.rise_mm  # 상승 계산
A_new = FC.water_area(F, *FC.roll_geom(F))
_, h_new = FC.rise_mm(F, A_new, 5, 45, 2)
old = dict(F, tube_r=14.86, mouth_z=369.0, tip_y=16.0, tip_z=379.0, end_y=54.0, end_z=372.0, wall_hole_z=378.2)
A_old = FC.water_area(old, *FC.roll_geom(old)); _, h_old = FC.rise_mm(old, A_old, 5, 45, 2)


def draw(i):
    s = 0
    for n, name in SC:
        if i < s + n:
            p = (i - s) / max(n - 1, 1); break
        s += n
    L = F["mouth_z"]
    if name == "fill":
        scene(ax, 364.2, "① 설탕물 채우기", "튜브(15 mL)를 집게에서 옆으로 빼서 설탕물을 가득 채운다 (설탕 1 : 물 1)", tube_up=True, tube_water=76 * p, wet=0)
    elif name == "flip":
        lv = 364.2 + (L - 364.2) * min(1, max(0, (p - .35) / .5))
        scene(ax, lv, "② 거꾸로 꽂기", "입구를 엄지로 막고 뒤집어 그릇 받침(리브)에 세우고 집게에 '딸깍'.\n그릇 물이 튜브 입구 높이(%.0f)까지 차면 저절로 멈춘다" % L,
              tube_water=60 - 2 * min(1, p * 2), thumb=p < .35, wet=0)
    elif name == "keep":
        lv = L - 0.8 * math.sin(math.pi * min(1, p * 1.6)) if p < .6 else L
        bub = L + 3 + 55 * ((p - .45) / .55) if p > .45 else None
        scene(ax, lv, "③ 물 높이가 스스로 유지됨 (병아리 물그릇)", "물이 줄어 입구 아래로 내려가면 → 입구로 공기 방울이 '꼴깍' 들어가고\n→ 그만큼 튜브 물이 내려와 다시 입구 높이로. 사람이 맞출 것이 없음",
              tube_water=58 - 2 * p, bubble=bub, wet=0)
    elif name == "wick":
        scene(ax, L, "④ 솜(코튼롤)이 설탕물을 빨아올림", "솜 바깥 끝이 물에 2 mm 잠기고, 안 끝은 마킹실 벽 구멍 속 (벽 안 면 뒤 0.2 mm).\n솜이 물을 끌어올려 벽 구멍의 솜 면이 늘 젖어 있음 (펌프·전기 없음)", tube_water=56, wet=p)
    elif name == "drink":
        scene(ax, L, "⑤ 말벌이 먹음 (찍은 뒤 60 s)", "바닥을 31 mm 올림(바닥 372) → 말벌 입 높이가 솜 면(372.8~383.2)과 같음.\n솜은 벽 속이라 누르기 때 바닥이 끝까지 올라도 안 닿음", tube_water=56, floor_lift=31 * min(1, p * 2.5), hornet_drink=p > .45)
    elif name == "hot_old":
        h = h_old * min(1, p * 1.4)
        scene(ax, 369 + h, "⑥ 더운 날 — 예전 설계 (50 mL, 물 369)", "튜브 안 공기가 데워져 물을 밀어냄: 햇빛이면 +%.1f mm\n→ 벽 구멍(372.6) 위로 → 마킹실로 샘 (실패)" % h_old,
              tube_r=14.86, tube_water=40, old=True, spill=369 + h > 372.6, wet=1)
    else:
        h = h_new * min(1, p * 1.4)
        scene(ax, L + h, "⑦ 더운 날 — 고친 설계 (15 mL, 물 366)", "공기가 적고 물 면이 넓어 햇빛이어도 +%.1f mm → 물 %.1f < 벽 구멍 %.1f (통과)\n(cad/feeder_check.py 검사 6개 통과)" % (h_new, L + h_new, HOLE0),
              tube_water=56, wet=1)
    return []


anim = FuncAnimation(fig, draw, frames=TOTAL, interval=1000 / FR)
os.makedirs(OUT, exist_ok=True)
anim.save(os.path.join(OUT, "급이방_원리.mp4"), writer=FFMpegWriter(fps=FR, bitrate=2400))
s = 0
for n, name in SC:   # 장면별 마지막 그림
    draw(s + n - 1); fig.savefig(os.path.join(OUT, "장면_%s.png" % name), dpi=90); s += n
print("mp4 ok", round(h_old, 1), round(h_new, 1))
