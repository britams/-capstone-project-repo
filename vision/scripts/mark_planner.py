"""mark_planner.py — 흉부 확률로 찍을 지점을 고르고 경로를 짜서 MCU 명령으로 바꾸기 (CAP-AI-SJ-24)

승준 아이디어: 3D 프린트 격자 → 찍을 수 있는 위치가 정해짐 → AI가 '흉부일 확률'이 높은 지점에 우선순위를 매기고
경로를 계산 → MCU(아두이노)는 받은 경로만 빠르게 실행.

이 모듈이 하는 일
  1. reachable_points(grid, tip_d)   : 격자 구멍(또는 슬롯) 안에서 마커 팁 중심이 갈 수 있는 점들
  2. point_success_prob(...)         : 비전이 준 흉부 위치·방향(+불확실성)으로 각 점이 '점이 흉부 안전영역 안에 찍힐' 확률
  3. choose_targets(...)             : 확률 높은 순, 서로 겹치지 않게 k개
  4. order_path(...)                 : 시작점에서 출발해 X·Y 동시 이동 시간 기준 최단 순서 (최근접 + 2-opt)
  5. to_commands(...)                : trap_controller 명령 줄 (MOVE / PEN) 또는 PATH 한 줄

좌표: 인터페이스 정의서 — 원점 격자 가운데, +x 방생 문 쪽, +y 먹이통 쪽, mm
흉부 '안전영역' = 흉부 등판 타원(길이 L, 폭 w)을 계수 kL·kW로 줄이고 점 반지름만큼 더 줄인 타원 (날개 뿌리·머리·배에 안 묻게)
"""
from dataclasses import dataclass
import itertools
import math

import numpy as np


@dataclass
class Grid:
    kind: str = 'square'      # 'square' = 사각 구멍 격자, 'slot' = 한 방향 막대(슬롯) + 드문 보강 리브
    pitch: float = 4.4        # 구멍(슬롯) 간격
    opening: float = 3.0      # 구멍(슬롯) 폭
    rib_pitch: float = 12.0   # slot일 때 가로 보강 리브 간격
    rib_w: float = 1.0        # slot일 때 리브 폭
    half: float = 18.0        # 마킹 영역 반폭 (D6 s_x = s_y = ±18)
    clearance: float = 0.1    # 팁과 구멍 벽 틈


def reachable_points(grid: Grid, tip_d: float, step: float = 0.25):
    """팁(지름 tip_d)이 구멍을 지나 말벌 등에 닿을 수 있는 팁 중심 점들 (N×2)."""
    m = grid.opening / 2 - tip_d / 2 - grid.clearance
    if m < 0:
        return np.zeros((0, 2))
    n = int(grid.half // grid.pitch)
    centers = np.arange(-n, n + 1) * grid.pitch
    offs = np.arange(-m, m + 1e-9, step) if m > 0 else np.array([0.0])
    pts = []
    if grid.kind == 'square':
        for cx, cy in itertools.product(centers, centers):
            for dx, dy in itertools.product(offs, offs):
                pts.append((cx + dx, cy + dy))
    else:  # slot: 슬롯이 x 방향으로 길고, y 방향으로 pitch 간격. x 방향엔 rib_pitch마다 리브(폭 rib_w)
        xs = np.arange(-grid.half, grid.half + 1e-9, step)
        rib_c = np.arange(-int(grid.half // grid.rib_pitch) - 1, int(grid.half // grid.rib_pitch) + 2) * grid.rib_pitch
        bad = np.zeros_like(xs, dtype=bool)
        for rc in rib_c:
            bad |= np.abs(xs - rc) < grid.rib_w / 2 + tip_d / 2 + grid.clearance
        xs = xs[~bad]
        for cy in centers:
            for dy in offs:
                for x in xs:
                    pts.append((x, cy + dy))
    p = np.array(pts)
    return p[(np.abs(p[:, 0]) <= grid.half) & (np.abs(p[:, 1]) <= grid.half)]


def in_safe(px, py, tx, ty, th, L, w, kL, kW, r_dot):
    """점(px,py)에 지름 2r_dot 점을 찍었을 때 안전영역 안인가 (배열 브로드캐스트)."""
    a = kL * L / 2 - r_dot
    b = kW * w / 2 - r_dot
    a = np.maximum(a, 1e-6)
    b = np.maximum(b, 1e-6)
    c, s = np.cos(th), np.sin(th)
    dx, dy = px - tx, py - ty
    u = dx * c + dy * s
    v = -dx * s + dy * c
    ok = (u / a) ** 2 + (v / b) ** 2 <= 1.0
    return ok & (kL * L / 2 > r_dot) & (kW * w / 2 > r_dot)


def point_success_prob(points, est, unc, kL, kW, r_dot, rng, n_samples=256, sigma_mech=0.0):
    """est = (x, y, θ, L, w) 비전 추정, unc = (σ_xy, σ_θ, σ_size). 각 점의 성공 확률 (점 개수 배열)."""
    x, y, th, L, w = est
    sxy, sth, ssz = unc
    tx = x + rng.normal(0, sxy, n_samples)
    ty = y + rng.normal(0, sxy, n_samples)
    tt = th + rng.normal(0, sth, n_samples)
    Ls = np.maximum(L + rng.normal(0, ssz, n_samples), 1.0)
    ws = np.maximum(w + rng.normal(0, ssz, n_samples), 1.0)
    px = points[:, 0:1]
    py = points[:, 1:2]
    if sigma_mech > 0:   # 기구 위치 오차: 명령한 점에서 표본마다 흔들어 찍힘
        px = px + rng.normal(0, sigma_mech, (len(points), n_samples))
        py = py + rng.normal(0, sigma_mech, (len(points), n_samples))
    ok = in_safe(px, py, tx[None], ty[None], tt[None], Ls[None], ws[None], kL, kW, r_dot)
    return ok.mean(axis=1)


def choose_targets(points, probs, k=3, min_sep=1.5, p_min=0.0):
    """확률 높은 순으로, 서로 min_sep 이상 떨어진 점 k개 (p_min 미만은 버림)."""
    order = np.argsort(-probs)
    chosen = []
    for i in order:
        if probs[i] < p_min:
            break
        if all(math.dist(points[i], points[j]) >= min_sep for j in chosen):
            chosen.append(i)
        if len(chosen) == k:
            break
    return [(tuple(float(c) for c in points[i]), float(probs[i])) for i in chosen]


def move_time(a, b, vx, vy, t_settle=0.05):
    """X·Y를 동시에 움직일 때 시간 = 더 오래 걸리는 축 (체비쇼프)."""
    return max(abs(a[0] - b[0]) / vx, abs(a[1] - b[1]) / vy) + t_settle


def order_path(start, targets, vx, vy):
    """최근접 이웃으로 시작 → 2-opt로 다듬기. targets = [(x,y), ...]"""
    if len(targets) <= 1:
        return list(targets)
    rest = list(targets)
    route, cur = [], start
    while rest:
        j = min(range(len(rest)), key=lambda i: move_time(cur, rest[i], vx, vy))
        cur = rest.pop(j)
        route.append(cur)

    def cost(r):
        return sum(move_time(p, q, vx, vy) for p, q in zip([start] + r[:-1], r))
    improved = True
    while improved:
        improved = False
        for i in range(len(route) - 1):
            for j in range(i + 1, len(route)):
                new = route[:i] + route[i:j + 1][::-1] + route[j + 1:]
                if cost(new) < cost(route) - 1e-9:
                    route, improved = new, True
    return route


def to_commands(route, n_dab=2, single_line=False):
    """trap_controller 명령. single_line=True면 제안 명령 'PATH n x1 y1 … d' 한 줄 (펌웨어 추가 필요)."""
    if single_line:
        return ['PATH %d %s %d' % (len(route), ' '.join('%.2f %.2f' % p for p in route), n_dab)]
    cmds = []
    for x, y in route:
        cmds += ['MOVE X %.2f' % x, 'MOVE Y %.2f' % y]
        for _ in range(n_dab):
            cmds += ['PEN DOWN', 'PEN UP']
    return cmds


def plan(est, unc, grid=Grid(), tip_d=2.0, dot_d=1.5, kL=0.75, kW=0.7, sigma_mech=0.15,
         k=1, p_min=0.5, start=(10.0, -40.0), vx=1.96, vy=1.96, rng=None, radius=5.0):
    """한 번에: 후보 → 확률 → 선택 → 경로 → 명령. p_min 미만뿐이면 [] (찍지 말고 자세 다시 잡기)."""
    rng = rng or np.random.default_rng(0)
    pts = reachable_points(grid, tip_d)
    near = pts[np.hypot(pts[:, 0] - est[0], pts[:, 1] - est[1]) <= radius]
    if len(near) == 0:
        return dict(targets=[], route=[], commands=[], p_best=0.0)
    probs = point_success_prob(near, est, unc, kL, kW, dot_d / 2, rng, sigma_mech=sigma_mech)
    tg = choose_targets(near, probs, k=k, min_sep=dot_d, p_min=p_min)
    route = order_path(start, [t[0] for t in tg], vx, vy)
    return dict(targets=tg, route=route, commands=to_commands(route), p_best=float(probs.max()))


if __name__ == '__main__':
    # 예: 흉부 추정 (1.0, -0.5) mm, 30°, L 5.5, w 4.1, 비전 불확실성 σ 0.4 mm·8°·0.1 mm
    est = (1.0, -0.5, math.radians(30), 5.5, 4.1)
    unc = (0.4, math.radians(8), 0.1)
    for g in (Grid(), Grid(kind='slot', pitch=4.0)):
        r = plan(est, unc, grid=g, k=3, p_min=0.0)
        print(g.kind, 'p_best=%.2f' % r['p_best'], [(tuple(round(c, 2) for c in t[0]), round(t[1], 2)) for t in r['targets']])
        print('  ', r['commands'][:6], '…')
