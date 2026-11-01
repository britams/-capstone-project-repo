# -*- coding: utf-8 -*-
"""자유물체도 그리기 공용 도구 (S4 상세 자유물체도, CAP-AI-20)

색 규칙 (모든 그림 같음)
  빨강 실선  = 주어진 힘·하중 (크기를 앎)
  파랑 실선  = 구하는 힘·반력 (미지)
  주황 실선  = 마찰력 (μN, 방향은 미끄러짐을 막는 쪽)
  보라 점선  = 관성력 −m·a (달랑베르, 동역학 그림만)
  초록       = 모멘트·토크 (곡선 화살표)
  회색       = 치수·각도·좌표축
"""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Arc, Polygon, Rectangle, Circle

plt.rcParams.update({"font.family": "Noto Sans CJK JP", "axes.unicode_minus": False, "mathtext.fontset": "dejavusans"})
GIVEN, UNK, FRIC, INER, MOM, DIM, EDGE = "#c0392b", "#1f4e9a", "#d35400", "#7d3c98", "#117a65", "#666666", "#222222"
BODY, BODY2, GROUND = "#eef1f6", "#fdf2d0", "#bfa77a"


def _v(p):
    return np.asarray(p, dtype=float)


def unit(deg):
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


def arrow(ax, tail, head, c, lw=2.4, ls="-", ms=18, z=6, style="-|>"):
    ax.add_patch(FancyArrowPatch(tuple(_v(tail)), tuple(_v(head)), arrowstyle=style, mutation_scale=ms, color=c,
                                 lw=lw, linestyle=ls, zorder=z, shrinkA=0, shrinkB=0))


def label(ax, p, text, c="#000000", fs=11, ha="center", va="center", box=True, z=9, rot=0, weight="normal"):
    kw = dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.88) if box else None
    ax.text(*_v(p), text, color=c, fontsize=fs, ha=ha, va=va, zorder=z, bbox=kw, rotation=rot, fontweight=weight)


def force(ax, p, vec, c, text=None, push=True, off=(0, 0), fs=11, lw=2.4, ls="-", ha="center", va="center", ms=18):
    """p = 작용점, vec = 그림에서의 화살표 벡터(길이 = 그림 길이). push=True: 머리가 작용점(미는 힘), False: 꼬리가 작용점(당기는 힘)"""
    p, vec = _v(p), _v(vec)
    tail, head = (p - vec, p) if push else (p, p + vec)
    arrow(ax, tail, head, c, lw=lw, ls=ls, ms=ms)
    if text:
        anchor = tail if push else head
        label(ax, anchor + _v(off), text, c=c, fs=fs, ha=ha, va=va)
    return tail, head


def dim(ax, p1, p2, text, off=0.0, fs=10, c=DIM, ext=True, tpos=0.5, toff=None, rot=None):
    """치수선: p1–p2를 수직 방향으로 off만큼 띄워 그림"""
    p1, p2 = _v(p1), _v(p2)
    d = p2 - p1
    L = np.linalg.norm(d)
    if L == 0:
        return
    t = d / L
    n = np.array([-t[1], t[0]])
    q1, q2 = p1 + n * off, p2 + n * off
    if ext and abs(off) > 0:
        ax.plot(*zip(p1 + n * 0.15 * np.sign(off), q1 + n * 0.25 * np.sign(off)), color=c, lw=0.8, zorder=3)
        ax.plot(*zip(p2 + n * 0.15 * np.sign(off), q2 + n * 0.25 * np.sign(off)), color=c, lw=0.8, zorder=3)
    ax.add_patch(FancyArrowPatch(tuple(q1), tuple(q2), arrowstyle="<|-|>", mutation_scale=10, color=c, lw=0.9, zorder=3,
                                 shrinkA=0, shrinkB=0))
    ang = math.degrees(math.atan2(t[1], t[0]))
    if ang > 90:
        ang -= 180
    if ang < -90:
        ang += 180
    m = q1 + (q2 - q1) * tpos + (n * (toff if toff is not None else 0.0))
    label(ax, m, text, c=c, fs=fs, rot=ang if rot is None else rot)


def angle(ax, c, r, a1, a2, text, fs=10, col=DIM, tr=1.32, lw=1.0):
    """각도 호: 중심 c, 반지름 r, a1→a2 (도, 반시계)"""
    c = _v(c)
    ax.add_patch(Arc(tuple(c), 2 * r, 2 * r, theta1=min(a1, a2), theta2=max(a1, a2), color=col, lw=lw, zorder=4))
    am = math.radians((a1 + a2) / 2)
    label(ax, c + tr * r * np.array([math.cos(am), math.sin(am)]), text, c=col, fs=fs)


def moment(ax, c, r, a_from, a_to, col=MOM, text=None, toff=(0, 0), fs=11, lw=2.0):
    """곡선 화살표 (a_from → a_to, 도). a_to > a_from 이면 반시계"""
    c = _v(c)
    th = np.radians(np.linspace(a_from, a_to, 40))
    xs, ys = c[0] + r * np.cos(th), c[1] + r * np.sin(th)
    ax.plot(xs[:-3], ys[:-3], color=col, lw=lw, zorder=6)
    arrow(ax, (xs[-4], ys[-4]), (xs[-1], ys[-1]), col, lw=lw, ms=14)
    if text:
        am = math.radians(a_to)
        label(ax, c + 1.35 * r * np.array([math.cos(am), math.sin(am)]) + _v(toff), text, c=col, fs=fs)


def triad(ax, o, L, a=0, names=("x", "y"), fs=11):
    o = _v(o)
    for i, (nm, aa) in enumerate(((names[0], a), (names[1], a + 90))):
        e = unit(aa) * L
        arrow(ax, o, o + e, DIM, lw=1.4, ms=12)
        label(ax, o + e * 1.22, nm, c=DIM, fs=fs, box=False)
    ax.plot(*o, "o", color=DIM, ms=3)


def ground(ax, p1, p2, side=-1, n=12, h=None, c="#555555"):
    """빗금 지면: p1→p2 선 + side(−1: 오른쪽 아래) 쪽 빗금"""
    p1, p2 = _v(p1), _v(p2)
    d = p2 - p1
    L = np.linalg.norm(d)
    t = d / L
    nrm = np.array([-t[1], t[0]]) * side
    h = h if h is not None else L / n * 0.9
    ax.plot(*zip(p1, p2), color=c, lw=1.6, zorder=3)
    for k in range(n + 1):
        q = p1 + d * k / n
        ax.plot(*zip(q, q - nrm * h + t * h * 0.6), color=c, lw=0.8, zorder=2)


def pin(ax, p, s=1.0, c="#555555"):
    p = _v(p)
    ax.add_patch(Polygon([p, p + [-0.6 * s, -1.0 * s], p + [0.6 * s, -1.0 * s]], closed=True, fc="#d5d8dc", ec=c, lw=1.2, zorder=4))
    ax.add_patch(Circle(tuple(p), 0.16 * s, fc="white", ec=c, lw=1.2, zorder=5))
    ground(ax, p + [-0.9 * s, -1.0 * s], p + [0.9 * s, -1.0 * s], n=6, h=0.3 * s)


def roller(ax, p, s=1.0, c="#555555"):
    p = _v(p)
    ax.add_patch(Polygon([p, p + [-0.6 * s, -0.75 * s], p + [0.6 * s, -0.75 * s]], closed=True, fc="#d5d8dc", ec=c, lw=1.2, zorder=4))
    for dx in (-0.35, 0.35):
        ax.add_patch(Circle(tuple(p + [dx * s, -0.88 * s]), 0.13 * s, fc="white", ec=c, lw=1.0, zorder=4))
    ground(ax, p + [-0.9 * s, -1.01 * s], p + [0.9 * s, -1.01 * s], n=6, h=0.3 * s)


def point(ax, p, name=None, off=(0.3, 0.3), fs=12, c="#000000", ms=5):
    p = _v(p)
    ax.plot(*p, "o", color=c, ms=ms, zorder=8)
    if name:
        label(ax, p + _v(off), name, c=c, fs=fs, box=False, weight="bold")


def cg(ax, p, r=0.35, name="G", off=(0.45, 0.45), fs=11):
    """무게중심 기호 (사분원 칠함)"""
    p = _v(p)
    ax.add_patch(Circle(tuple(p), r, fc="white", ec="black", lw=1.0, zorder=7))
    for a0 in (0, 180):
        ax.add_patch(matplotlib.patches.Wedge(tuple(p), r, a0, a0 + 90, fc="black", ec="black", zorder=7))
    if name:
        label(ax, p + _v(off), name, fs=fs, box=False)


def out_of_page(ax, p, r=0.3, inward=False, text=None, c=GIVEN, off=(0.5, 0)):
    """⊙ 지면 밖으로 / ⊗ 지면 안으로"""
    p = _v(p)
    ax.add_patch(Circle(tuple(p), r, fc="white", ec=c, lw=1.5, zorder=7))
    if inward:
        ax.plot([p[0] - r * 0.6, p[0] + r * 0.6], [p[1] - r * 0.6, p[1] + r * 0.6], color=c, lw=1.5, zorder=8)
        ax.plot([p[0] - r * 0.6, p[0] + r * 0.6], [p[1] + r * 0.6, p[1] - r * 0.6], color=c, lw=1.5, zorder=8)
    else:
        ax.plot(*p, "o", color=c, ms=3, zorder=8)
    if text:
        label(ax, p + _v(off), text, c=c, fs=10, ha="left")


def body(ax, pts, fc=BODY, ec=EDGE, lw=1.6, z=1, alpha=1.0, ls="-"):
    ax.add_patch(Polygon([tuple(_v(q)) for q in pts], closed=True, fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha, ls=ls))


def rect(ax, x, y, w, h, ang=0, fc=BODY, ec=EDGE, lw=1.6, z=1, ls="-", alpha=1.0, about=None):
    """회전 사각형: 왼쪽 아래 (x, y), 폭 w, 높이 h, about(기본 왼쪽 아래)을 중심으로 ang도 회전"""
    c0 = _v(about) if about is not None else _v((x, y))
    R = np.array([[math.cos(math.radians(ang)), -math.sin(math.radians(ang))], [math.sin(math.radians(ang)), math.cos(math.radians(ang))]])
    pts = [_v(q) for q in ((x, y), (x + w, y), (x + w, y + h), (x, y + h))]
    pts = [c0 + R @ (q - c0) for q in pts]
    body(ax, pts, fc=fc, ec=ec, lw=lw, z=z, ls=ls, alpha=alpha)
    return pts


def note(ax, xy, text, fs=10, ha="left", va="top", fc="#fbfbfb", ec="#999999", transform=None):
    ax.text(*xy, text, fontsize=fs, ha=ha, va=va, zorder=10, linespacing=1.45,
            bbox=dict(boxstyle="round,pad=0.5", fc=fc, ec=ec, lw=0.8), transform=transform or ax.transAxes)


def legend(ax, items=("given", "unk", "fric"), loc=(0.01, 0.01), fs=9):
    names = dict(given=("주어진 힘", GIVEN, "-"), unk=("구하는 힘·반력", UNK, "-"), fric=("마찰력", FRIC, "-"),
                 iner=("관성력 −ma", INER, "--"), mom=("모멘트·토크", MOM, "-"))
    hs = [matplotlib.lines.Line2D([0], [0], color=names[k][1], lw=2.4, ls=names[k][2]) for k in items]
    lg = ax.legend(hs, [names[k][0] for k in items], loc="lower left", bbox_to_anchor=loc, fontsize=fs, frameon=True, framealpha=0.9)
    lg.set_zorder(12)


def setup(ax, xlim, ylim, title=None, fs=12):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=fs, loc="left", fontweight="bold")


def save(fig, path, dpi=200):
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white", pil_kwargs=dict(quality=92, optimize=True))
    plt.close(fig)
