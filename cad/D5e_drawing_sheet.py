# -*- coding: utf-8 -*-
"""D5e 전체 조립도 한 장 (FreeCAD 렌더 5장 + 2020 단면 상세 + 부재·부품 표 + 표제란) — CAP-AI-21
실행: python3 cad/D5e_drawing_sheet.py <렌더 png 폴더> → cad/D5e_전체조립도.png
렌더는 cad/D5e_full_assembly.py 의 render() (정투영, 흰 바탕)
"""
import os
import sys

import numpy as np
from PIL import Image, ImageOps

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "design", "calc"))
from fbd_lib import plt, dim, label, DIM  # noqa: E402
from matplotlib.patches import Polygon, Circle, Rectangle  # noqa: E402

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D5e_전체조립도.png")


def crop(name):
    im = Image.open(os.path.join(SRC, "D5e_%s.png" % name)).convert("RGB")
    bb = ImageOps.invert(im).getbbox()
    return np.asarray(im.crop((max(bb[0] - 6, 0), max(bb[1] - 6, 0), min(bb[2] + 6, im.width), min(bb[3] + 6, im.height))))


fig = plt.figure(figsize=(24, 16.5))
gs = fig.add_gridspec(2, 4, width_ratios=[1.15, 0.85, 0.85, 1.25], height_ratios=[1, 0.82], hspace=0.12, wspace=0.06)

# 도1 등각
ax = fig.add_subplot(gs[:, 0])
ax.imshow(crop("도1_전체_등각"))
ax.axis("off")
ax.set_title("도1  전체 등각", loc="left", fontsize=14, fontweight="bold")

# 도2·도3 정면·측면 + 치수 (정투영: 그림 폭 = 프레임 바깥 360 mm, 높이 = 0 ~ 845 mm)
for k, (nm, ttl) in enumerate((("도2_정면", "도2  정면 (−y에서 봄)"), ("도3_측면", "도3  측면 (+x에서 봄)"))):
    ax = fig.add_subplot(gs[0, 1 + k])
    im = crop(nm)
    h, w = im.shape[:2]
    sc = (w - 12) / 360.0
    ax.imshow(im, extent=(-180 - 6 / sc, 180 + 6 / sc, -6 / sc, (h - 6) / sc), aspect="equal")
    for z, t in ((0, ""),):
        pass
    dim(ax, (-180, -40), (180, -40), "360 (프레임 바깥)", off=0, fs=10)
    dim(ax, (-215, 0), (-215, 610), "610 (기둥)", off=0, fs=10, rot=90)
    dim(ax, (215, 0), (215, 845), "845 (포획통 꼭대기)", off=0, fs=10, rot=90)
    dim(ax, (-250, 0), (-250, 205), "205 받침판", off=0, fs=9, rot=90)
    ax.set_xlim(-275, 245)
    ax.set_ylim(-70, 880)
    ax.axis("off")
    ax.set_title(ttl, loc="left", fontsize=14, fontweight="bold")

# 도4 위
ax = fig.add_subplot(gs[1, 1:3])
ax.imshow(crop("도4_위"))
ax.axis("off")
ax.set_title("도4  위 (포획통·위 받침판 숨김)", loc="left", fontsize=14, fontweight="bold")

# 도5 모듈 확대
ax = fig.add_subplot(gs[0, 3])
ax.imshow(crop("도5_모듈_등각"))
ax.axis("off")
ax.set_title("도5  마킹 모듈 확대 (프레임 숨김)", loc="left", fontsize=14, fontweight="bold")

# 2020 단면 상세 + 표
sub = gs[1, 3].subgridspec(1, 2, width_ratios=[0.8, 1.6], wspace=0.05)
ax = fig.add_subplot(sub[0])
h = 10.0
ax.add_patch(Rectangle((-h, -h), 20, 20, fc="#c9ced6", ec="#333", lw=1.2))
for ang in (0, 90, 180, 270):
    R = np.array([[np.cos(np.radians(ang)), -np.sin(np.radians(ang))], [np.sin(np.radians(ang)), np.cos(np.radians(ang))]])
    lip = np.array([(-3.1, 8.2), (3.1, 8.2), (3.1, 10.05), (-3.1, 10.05)])
    ch = np.array([(-4.0, 5.0), (4.0, 5.0), (4.0, 8.2), (-4.0, 8.2)])
    for poly in (lip, ch):
        ax.add_patch(Polygon((R @ poly.T).T, closed=True, fc="white", ec="#333", lw=0.8))
ax.add_patch(Circle((0, 0), 2.1, fc="white", ec="#333", lw=0.8))
dim(ax, (-10, -13), (10, -13), "20", off=0, fs=10)
dim(ax, (-3.1, 13), (3.1, 13), "홈 6.2", off=0, fs=9)
label(ax, (0, -2.0 - 2.5), "Ø4.2 (M5 탭)", fs=8, c=DIM)
ax.set_xlim(-16, 16)
ax.set_ylim(-17, 17)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("2020 단면 (20 시리즈)", loc="left", fontsize=12, fontweight="bold")
ax = fig.add_subplot(sub[1])
ax.axis("off")
rows = [("부품", "치수·수량"),
        ("기둥 2020", "610 × 4"),
        ("레일 2020", "320 × 21"),
        ("프로파일 합계", "9.16 m"),
        ("L 브래킷 20×20", "32"),
        ("트랩 몸통+유인액 통", "Ø≈200 × 145"),
        ("트랩 차양막", "Ø260, 윗면 180"),
        ("구멍 / 턱", "Ø55 / Ø90"),
        ("노란 깔때기 ×2", "Ø50 → Ø19"),
        ("포획통", "높이 220, 바닥 Ø94"),
        ("마킹 모듈", "D5e")]
tb = ax.table(cellText=rows[1:], colLabels=rows[0], loc="upper left", cellLoc="left", colWidths=[0.5, 0.5])
tb.auto_set_font_size(False)
tb.set_fontsize(10.5)
tb.scale(1, 1.75)
ax.text(0.0, 0.2, "트랩 치수: design/2026-10-28_상용트랩_실측표.md\n(몸통 지름·포획통 최대 지름은 사진 비례 [추측])", transform=ax.transAxes, fontsize=9.5, va="top")
for (r, c), cell in tb.get_celld().items():
    if r == 0:
        cell.set_facecolor("#e8e8e8")
ax.text(0.0, 0.02, "말벌 자동 마킹 트랩 D5e 전체 조립도 · 팀 초벌 · 2026-11-02 · 단위 mm · 정투영 렌더(축척 없음)\n"
        "cad/D5e_full_assembly.py (FreeCAD) · 이음·간섭 검사: 프레임·트랩–모듈 겹침 0 · CAP-AI-21",
        transform=ax.transAxes, fontsize=9.5, va="bottom", bbox=dict(fc="#fbfbfb", ec="#999"))
fig.suptitle("D5e 전체 조립도 — 2020 알루미늄 프로파일 프레임 + 상용 트랩(야생 말벌 포획기) + 마킹 모듈", fontsize=18, x=0.01, ha="left", fontweight="bold")
fig.savefig(OUT, dpi=110, bbox_inches="tight", facecolor="white")
print(OUT)
