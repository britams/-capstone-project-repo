# -*- coding: utf-8 -*-
"""hub_boards.py — 서보 허브·게이트 허브 만능기판 배치 + 넷 검사 + SVG 그림 (서현 CAP-AI-50, 2026-11-08)

판 크기·자리는 CAD(cad/D5g_real_parts.py HUBS)를 그대로: 서보 허브 60 × 40, 게이트 허브 70 × 30, 네 귀 M2 기둥(가장자리 3 mm).
연결은 design/circuit/circuit.py 의 NETS 가 원본 — 이 스크립트는 판 위 연결이 그 넷과 '똑같은지' 검사한다.
  같은 넷인데 판에서 안 이어짐 → 오류,  다른 넷인데 판에서 이어짐(합선) → 오류.

판 위 연결 규칙 (AI 판단, 서현 위임)
  - 구멍 2.54 간격, 기둥 구멍에서 2.6 mm 안의 구멍은 안 씀
  - 땜납 다리(bridge): 납땜 면에서 가로·세로로 이웃한 구멍만
  - 버스(bus): 한 줄을 따라 깐 맨 구리선 (납땜 면) — +5V_B, GND, EMIT_LO
  - 점퍼(jumper): 부품 면의 피복선, 버스를 넘어갈 때만 (판마다 개수를 셈)
  - 저항은 세워 꽂기 (다리 간격 2.54) — 1/4 W 세움 [가능성 높음 — 흔한 방법]
  - 헤더 핀 1 × n (2.54) — 하네스표의 듀폰 커넥터가 꽂힘
  - (CAP-AI-54) 부품 몸통 겹침 검사: 위에서 본 몸통(아래 BODY)끼리, 귀 기둥(Ø4), 판 가장자리와 틈 ≥ 0 — 승준 CAD(SJ-53)가 찾은 C1·C2·SB540 겹침 때문

실행:  python 전기회로/hub_boards.py   →  전기회로/out/*.svg, hub_pinout.md, 검사 결과 출력 (오류면 종료 코드 1)
"""
import math
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "design", "circuit"))
import circuit  # noqa: E402  (NETS 만 씀 — 회로도 그리기는 안 부름)

OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
P = 2.54
NODE_NET = {n: net for net, lst in circuit.NETS.items() for n, _a, _note in lst}
# 위에서 본 몸통 (mm) — 흔한 부품 외형 [가능성 높음 — 사양서 대표값, 실물로 확인]
BODY = {"0.1µ": ("rect", 2.5, 5.0),        # 세라믹 디스크 Ø5 × 두께 2.5, 다리 2.54 (판이 다리 방향)
        "1000µ": ("circ", 5.0),           # 전해 1000 µF 10 V Ø10, 다리 5.0
        "SB540": ("rect", 5.3, 9.5)}      # DO-201AD 누움 Ø5.3 × 9.5, 다리 Ø1.2~1.3 → 구멍 Ø1.5
MOUNT_R = 2.0                              # M2 기둥·나사 머리 Ø4
XH4 = (12.4, 5.75)                         # JST XH B4B-XH-A 하우징 (핀 4 × 2.5)


class Board:
    def __init__(self, name, title, L, W, mount_off=3.0, mount_keep=2.6):
        self.name, self.title, self.L, self.W = name, title, L, W
        self.nc = int((L - 2.0) // P) + 1
        self.nr = int((W - 2.0) // P) + 1
        self.mx = (L - (self.nc - 1) * P) / 2
        self.my = (W - (self.nr - 1) * P) / 2
        self.mounts = [(mount_off, mount_off), (L - mount_off, mount_off), (mount_off, W - mount_off), (L - mount_off, W - mount_off)]
        self.keep = mount_keep
        self.pins = {}          # (c,r) → (노드, 표시 글자, 종류)
        self.res = []           # (이름, 값, h1, h2)
        self.links = []         # ('bridge'|'bus'|'jumper', h1, h2, 넷 이름(그림 색))
        self.free_pads = {}     # (c,r) → 표시 (J_I2C 처럼 판과 안 이어지는 부품)
        self.col_labels = []    # (칸, 글자) — 그림 위쪽에 게이트·서보 이름
        self.errors = []
        self.housings = []      # (이름, cx, cy, 가로, 세로) — 판과 안 이어지는 부품 몸통 (J_I2C)
        self.drill = {}         # (c,r) → 넓힐 구멍 지름 mm (만능기판 기본 Ø1.0)
        self.near = []

    def xy(self, h):
        c, r = h
        return self.mx + c * P, self.my + r * P

    def ok_hole(self, h):
        c, r = h
        if not (0 <= c < self.nc and 0 <= r < self.nr):
            return False
        x, y = self.xy(h)
        return all(math.hypot(x - mx, y - my) > self.keep for mx, my in self.mounts)

    def _use(self, h, what):
        if not self.ok_hole(h):
            self.errors.append("%s: 쓸 수 없는 구멍 %s (판 밖 또는 기둥 근처)" % (what, h))
        if h in self.pins or any(h in (a, b) for _n, _v, a, b in self.res) or h in self.free_pads:
            self.errors.append("%s: 구멍 %s 에 부품 다리가 이미 있음" % (what, h))

    def pin(self, h, node, label, kind="hdr"):
        self._use(h, label)
        self.pins[h] = (node, label, kind)

    def resistor(self, name, value, h1, n1, h2, n2, span=1):
        """다리 2개 부품. span = 다리 사이 구멍 수 (세운 저항 1, 전해 콘덴서 2 = 5.08 mm, 누운 다이오드 6 = 15.2 mm)"""
        self._use(h1, name)
        self._use(h2, name)
        if abs(h1[0] - h2[0]) + abs(h1[1] - h2[1]) != span or (h1[0] != h2[0] and h1[1] != h2[1]):
            self.errors.append("%s: 다리 간격이 %d 칸 (한 줄로)이어야 함" % (name, span))
        self.res.append((name, value, h1, h2))
        self.pins[("R", name, 1)] = (n1, name, "rleg")      # 다리 노드 기록 (자리는 h1/h2)
        self.pins[("R", name, 2)] = (n2, name, "rleg")
        self._rleg = getattr(self, "_rleg", {})
        self._rleg[h1], self._rleg[h2] = n1, n2

    def bridge(self, *holes, net=""):
        for a, b in zip(holes, holes[1:]):
            if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
                self.errors.append("땜납 다리는 이웃 구멍끼리만: %s–%s" % (a, b))
            for h in (a, b):
                if not self.ok_hole(h):
                    self.errors.append("땜납 다리 구멍 %s 못 씀" % (h,))
            self.links.append(("bridge", a, b, net))

    def bus(self, row, c0, c1, net):
        for c in range(c0, c1 + 1):
            if not self.ok_hole((c, row)):
                self.errors.append("버스 %s 구멍 %s 못 씀" % (net, (c, row)))
        self.links.append(("bus", (c0, row), (c1, row), net))

    def jumper(self, a, b, net=""):
        self.links.append(("jumper", a, b, net))

    def _jumper_ends_free(self):
        """부품 면 점퍼는 다리·핀이 없는 빈 구멍(또는 버스 구멍)에서만 시작·끝날 수 있다."""
        legs = set(h for h in self.pins if isinstance(h[0], int)) | set(getattr(self, "_rleg", {}))
        return ["점퍼 끝 %s 에 헤더 핀/저항 다리가 있음 (점퍼를 꽂을 수 없음)" % (h,)
                for kind, a, b, _n in self.links if kind == "jumper" for h in (a, b) if h in legs]

    # ---- 몸통 겹침 (CAP-AI-54) ----
    def bodies(self):
        """위에서 본 몸통: ('rect', 이름, cx, cy, 가로, 세로) / ('circ', 이름, cx, cy, 반지름)"""
        out = []
        for h, (node, label, kind) in self.pins.items():
            if kind == "hdr":                                  # 듀폰 하우징 한 칸
                out.append(("rect", "%s %s" % (label, h)) + self.xy(h) + (2.5, 2.5))
            elif kind == "wire":                               # 납땜한 전선이 위로 섬 (피복 Ø2)
                out.append(("circ", "%s %s" % (label, h)) + self.xy(h) + (1.0,))
        for name, val, h1, h2 in self.res:
            (x1, y1), (x2, y2) = self.xy(h1), self.xy(h2)
            cx, cy, along_x = (x1 + x2) / 2, (y1 + y2) / 2, y1 == y2
            shape = BODY.get(val)
            if shape is None:                                  # 세운 저항: 몸통이 첫 다리 위
                out.append(("circ", name, x1, y1, 1.25))
            elif shape[0] == "circ":
                out.append(("circ", name, cx, cy, shape[1]))
            else:                                              # (가로질러, 다리 방향)
                a, l = shape[1], shape[2]
                out.append(("rect", name, cx, cy, l if along_x else a, a if along_x else l))
        out += [("rect",) + t for t in self.housings]
        return out

    def footprint_check(self):
        def gap(p, q):
            if p[0] == "circ" and q[0] == "circ":
                return math.hypot(p[2] - q[2], p[3] - q[3]) - p[4] - q[4]
            if p[0] == "circ":
                p, q = q, p
            if q[0] == "circ":                                 # 사각형 p ↔ 원 q
                dx = max(abs(q[2] - p[2]) - p[4] / 2, 0)
                dy = max(abs(q[3] - p[3]) - p[5] / 2, 0)
                return math.hypot(dx, dy) - q[4]
            return max(abs(p[2] - q[2]) - (p[4] + q[4]) / 2, abs(p[3] - q[3]) - (p[5] + q[5]) / 2)
        bs = self.bodies()
        errs, near = [], []
        for i, p in enumerate(bs):
            for q in bs[i + 1:]:
                g = gap(p, q)
                if g < 0:
                    errs.append("몸통 겹침: %s ↔ %s (%.2f mm)" % (p[1], q[1], g))
                elif g < 0.5 and g > 0.05:                      # 0.04 = 2.54 간격 이웃 하우징 (정상)
                    near.append((round(g, 2), p[1], q[1]))
            for mx, my in self.mounts:
                if gap(p, ("circ", "기둥", mx, my, MOUNT_R)) < 0:
                    errs.append("몸통 겹침: %s ↔ 귀 기둥 (%.1f, %.1f)" % (p[1], mx, my))
            hx, hy = (p[4], p[4]) if p[0] == "circ" else (p[4] / 2, p[5] / 2)
            if p[2] - hx < 0 or p[2] + hx > self.L or p[3] - hy < 0 or p[3] + hy > self.W:
                errs.append("판 밖으로 나감: %s" % p[1])
        self.near = sorted(near)
        return errs

    # ---- 검사 ----
    def groups(self):
        parent = {}

        def f(x):
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def u(a, b):
            parent[f(a)] = f(b)
        for kind, a, b, _n in self.links:
            if kind == "bus":
                for c in range(a[0], b[0]):
                    u((c, a[1]), (c + 1, a[1]))
            else:
                u(a, b)
        return f

    def node_holes(self):
        out = []
        for h, (node, label, kind) in self.pins.items():
            if kind != "rleg":
                out.append((node, h, label))
        for h, node in getattr(self, "_rleg", {}).items():
            out.append((node, h, "저항 다리"))
        return out

    def check(self):
        errs = list(self.errors) + self._jumper_ends_free() + self.footprint_check()
        f = self.groups()
        nh = self.node_holes()
        for node, h, label in nh:
            if node not in NODE_NET:
                errs.append("%s (%s): circuit.py 에 없는 노드 %s" % (label, h, node))
        by_group = defaultdict(set)
        by_net = defaultdict(set)
        for node, h, label in nh:
            net = NODE_NET.get(node, "?")
            by_group[f(h)].add(net)
            by_net[net].add(f(h))
        for g, nets in by_group.items():
            if len(nets) > 1:
                errs.append("합선: 판에서 이어진 한 덩어리에 넷 %s" % sorted(nets))
        for net, gs in by_net.items():
            if len(gs) > 1:
                errs.append("끊김: 넷 %s 가 판에서 %d 덩어리로 나뉨" % (net, len(gs)))
        # 다리·버스가 지나가는 빈 구멍이 다른 넷 부품 구멍과 같은 덩어리인지는 위에서 걸림
        return errs

    def stats(self):
        n = defaultdict(int)
        for kind, *_ in self.links:
            n[kind] += 1
        return dict(헤더핀=sum(1 for v in self.pins.values() if v[2] == "hdr"), 전선자리=sum(1 for v in self.pins.values() if v[2] == "wire"),
                    저항=len(self.res), 땜납다리=n["bridge"], 버스=n["bus"], 점퍼=n["jumper"], 구멍=f"{self.nc} × {self.nr}")

    # ---- 그림 ----
    def svg(self, solder_side=False):
        s = 13.0                                  # mm → px
        pad = 46
        Wpx, Hpx = self.L * s + 2 * pad, self.W * s + 2 * pad + 60
        col = {"+5V_B": "#d1495b", "GND": "#3d4451", "EMIT_LO": "#8a4fd1"}

        def X(x):
            return pad + ((self.L - x) if solder_side else x) * s

        def Y(y):
            return pad + (self.W - y) * s                   # r 0 이 아래

        def H(h):
            x, y = self.xy(h)
            return X(x), Y(y)
        o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.0f %.0f" font-family="Malgun Gothic, sans-serif">' % (Wpx, Hpx)]
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="#e8d9a8" stroke="#9c8a55"/>' % (pad, pad, self.L * s, self.W * s))
        for mx, my in self.mounts:
            o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fff" stroke="#777"/>' % (X(mx), Y(my), 1.0 * s))
        for c in range(self.nc):
            for r in range(self.nr):
                if self.ok_hole((c, r)):
                    x, y = H((c, r))
                    o.append('<circle cx="%.1f" cy="%.1f" r="3.2" fill="#c9a25a" stroke="#8a6d30" stroke-width="0.6"/>' % (x, y))
                    if (c, r) in self.drill:                   # 넓힐 구멍: 빨간 고리
                        o.append('<circle cx="%.1f" cy="%.1f" r="7" fill="none" stroke="#e00" stroke-width="2"/>' % (x, y))
        # 버스·다리 (납땜 면 것) — 부품 면 그림에서는 옅게
        op = "1" if solder_side else "0.35"
        for kind, a, b, net in self.links:
            if kind in ("bus", "bridge"):
                (x1, y1), (x2, y2) = H(a), H(b)
                w = 4.5 if kind == "bus" else 5.5
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" stroke-linecap="round" opacity="%s"/>'
                         % (x1, y1, x2, y2, col.get(net, "#2e6fd8"), w, op))
        if solder_side:                               # 점퍼는 부품 면에 있음 → 여기서는 들어가는 구멍만 표시
            for kind, a, b, net in self.links:
                if kind == "jumper":
                    for h in (a, b):
                        x, y = H(h)
                        o.append('<circle cx="%.1f" cy="%.1f" r="6" fill="none" stroke="%s" stroke-width="2"/>' % (x, y, col.get(net, "#2e6fd8")))
        if not solder_side:
            for kind, a, b, net in self.links:
                if kind == "jumper":
                    (x1, y1), (x2, y2) = H(a), H(b)
                    mxp, myp = (x1 + x2) / 2 + 10, (y1 + y2) / 2
                    o.append('<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="3" stroke-dasharray="1 0"/>'
                             % (x1, y1, mxp, myp, x2, y2, col.get(net, "#2e6fd8")))
                    o.append('<circle cx="%.1f" cy="%.1f" r="2.5" fill="%s"/><circle cx="%.1f" cy="%.1f" r="2.5" fill="%s"/>'
                             % (x1, y1, col.get(net, "#2e6fd8"), x2, y2, col.get(net, "#2e6fd8")))
            for name, val, a, b in self.res:
                (x1, y1), (x2, y2) = H(a), H(b)
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#555" stroke-width="2"/>' % (x1, y1, x2, y2))
                o.append('<ellipse cx="%.1f" cy="%.1f" rx="7" ry="7" fill="#7fb3d5" stroke="#2c5d80"/>' % (x1, y1))
                o.append('<text x="%.1f" y="%.1f" font-size="8.5" text-anchor="middle" fill="#13324a">%s</text>' % (x1, y1 + 3, val))
            for h, (node, label, kind) in self.pins.items():
                if kind == "rleg":
                    continue
                x, y = H(h)
                if kind == "wire":                        # 전선 납땜 자리: 흰 네모 + 오른쪽 글자
                    o.append('<rect x="%.1f" y="%.1f" width="13" height="13" fill="#fff" stroke="#000" stroke-width="1.5"/>' % (x - 6.5, y - 6.5))
                    o.append('<text x="%.1f" y="%.1f" font-size="10.5" fill="#000">%s</text>' % (x + 9, y + 4, label))
                    continue
                uno = label.startswith("→")
                short = label.split()[-1].rstrip(")")[-3:] if uno else (label.split()[-1] if label else "")
                short = {"TX+": "T+", "RX+": "R+", "RX−": "R−", "TX−": "T−", "흰": "S"}.get(short, short)
                o.append('<rect x="%.1f" y="%.1f" width="15" height="15" rx="2" fill="%s" stroke="#000"/>' % (x - 7.5, y - 7.5, "#2e6fd8" if uno else "#222"))
                o.append('<text x="%.1f" y="%.1f" font-size="%s" text-anchor="middle" fill="#fff" font-weight="bold">%s</text>'
                         % (x, y + 3.5, "8" if len(short) > 2 else "10", short))
            for cx, text in self.col_labels:
                x, _ = H((cx, self.nr - 1))
                o.append('<text x="%.1f" y="%.1f" font-size="12" text-anchor="middle" font-weight="bold" fill="#5a3d00">%s</text>' % (x if not solder_side else x, pad + 13, text))
            for bd in self.bodies():                       # 부품 몸통 테두리 (CAP-AI-54) — 헤더·세운 저항은 빼고
                if bd[0] == "rect" and not bd[1].endswith(")") or bd[0] == "rect" and bd[1].startswith("J_I2C"):
                    w, h_ = bd[4] * s, bd[5] * s
                    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#b03a2e" stroke-width="1.5" stroke-dasharray="4 3"/>'
                             % (X(bd[2]) - w / 2, Y(bd[3]) - h_ / 2, w, h_))
                    o.append('<text x="%.1f" y="%.1f" font-size="9" fill="#b03a2e">%s</text>' % (X(bd[2]) - w / 2, Y(bd[3]) - h_ / 2 - 2, bd[1]))
                elif bd[0] == "circ" and bd[4] > 2:
                    o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#b03a2e" stroke-width="1.5" stroke-dasharray="4 3"/>'
                             % (X(bd[2]), Y(bd[3]), bd[4] * s))
                    o.append('<text x="%.1f" y="%.1f" font-size="9" fill="#b03a2e">%s</text>' % (X(bd[2]) + bd[4] * s * 0.7, Y(bd[3]) - bd[4] * s * 0.7, bd[1]))
            for h, label in self.free_pads.items():
                x, y = H(h)
                o.append('<rect x="%.1f" y="%.1f" width="10" height="10" fill="#fff" stroke="#999"/>' % (x - 5, y - 5))
                o.append('<text x="%.1f" y="%.1f" font-size="8" fill="#777">%s</text>' % (x + 8, y + 3, label))
        side = "납땜 면 (뒤집어 본 모습 — 좌우가 바뀜)" if solder_side else "부품 면 (위에서 본 모습)"
        o.append('<text x="%d" y="%.1f" font-size="15" font-weight="bold">%s — %s</text>' % (pad, pad - 14, self.title, side))
        o.append('<text x="%d" y="%.1f" font-size="11" fill="#444">빨강 +5V_B · 검정 GND · 보라 EMIT_LO(송신 켜기) · 파랑 신호 · 굵은 선 = 납땜 면 구리선/땜납 다리'
                 '%s</text>' % (pad, Hpx - 30, " · 곡선 = 부품 면 점퍼(피복선) · 파란 동그라미 = 세운 저항" if not solder_side else ""))
        o.append('<text x="%d" y="%.1f" font-size="11" fill="#444">%.0f × %.0f mm, 구멍 %d × %d (2.54 mm), 귀 기둥 M2 — 아래 줄이 r0, 왼쪽 칸이 c0%s</text>'
                 % (pad, Hpx - 14, self.L, self.W, self.nc, self.nr, " (납땜 면은 좌우 반대)" if solder_side else ""))
        o.append("</svg>")
        return "\n".join(o)


# ============================================================================
# 게이트 허브 70 × 30 — 빛 게이트 9쌍 + 레일 감지 + Q4 연결 (+ J_I2C 따로)
# ============================================================================
def gate_hub():
    b = Board("gate_hub", "게이트 허브", 70.0, 30.0)
    TOP, GNDR, EMR = 10, 0, 1             # 버스 줄: 위 +5V_B, 아래 GND, 그 위 EMIT_LO
    order = ["G2", "G2b", "G3", "G3b", "G5", "G5b", "G1", "G4", "G6"]
    c = 2
    for g in order:
        a, k = c, c + 1
        sig = "U2.%s" % circuit.GATE_PIN[g]
        if g in circuit.DOOR_GATES:
            # 헤더 a열 위→아래: C(포토TR 컬렉터) · A(LED 긴 다리) · E(포토TR 이미터=신호) · K(LED 짧은 다리)
            b.pin((a, 9), "PT_%s.C" % g, "%s C" % g)
            b.pin((a, 8), "LED_%s.A" % g, "%s A" % g)
            b.pin((a, 7), "PT_%s.E" % g, "%s E" % g)
            b.pin((a, 6), "LED_%s.K" % g, "%s K" % g)
            b.bridge((a, 9), (a, 10), net="+5V_B")                       # C → +5V
            b.resistor("RLED_%s" % g, "220", (k, 9), "RLED_%s.1" % g, (k, 8), "RLED_%s.2" % g)
            b.bridge((k, 9), (k, 10), net="+5V_B")
            b.bridge((k, 8), (a, 8), net="LEDA")                         # 220 Ω 끝 → A
            b.bridge((a, 7), (k, 7), net="SIG")                          # E → 신호 핀
            b.pin((k, 7), sig, "→UNO2 %s" % circuit.GATE_PIN[g])
            b.bridge((k, 7), (k, 6), net="SIG")
            b.resistor("RL_%s" % g, "10k", (k, 6), "RL_%s.1" % g, (k, 5), "RL_%s.2" % g)
            b.bridge((k, 5), (k, 4), (k, 3), (k, 2), net="GND")
            b.jumper((k, 2), (k, 0), net="GND")                           # EMIT 줄을 넘어 GND 버스로
            b.bridge((a, 6), (a, 5), (a, 4), (a, 3), (a, 2), (a, 1), net="EMIT_LO")   # K → EMIT_LO
            b.col_labels.append((a + 0.5, g))
        else:
            b.col_labels.append((a + 0.5, g))
            # Adafruit 2167: 헤더 a열 위→아래: TX+ · RX+ · SIG(흰) · RX GND · TX GND(켜기)
            b.pin((a, 9), "TX_%s.V+" % g, "%s TX+" % g)
            b.pin((a, 8), "RX_%s.V+" % g, "%s RX+" % g)
            b.pin((a, 7), "RX_%s.OUT" % g, "%s 흰" % g)
            b.pin((a, 6), "RX_%s.GND" % g, "%s RX−" % g)
            b.pin((a, 5), "TX_%s.GND" % g, "%s TX−" % g)
            b.bridge((a, 10), (a, 9), (a, 8), net="+5V_B")
            b.resistor("R_%s" % g, "10k", (k, 9), "R_%s.2" % g, (k, 8), "R_%s.1" % g)   # 풀업
            b.bridge((k, 9), (k, 10), net="+5V_B")
            b.bridge((k, 8), (k, 7), net="SIG")
            b.bridge((a, 7), (k, 7), net="SIG")
            b.pin((k, 7), sig, "→UNO2 %s" % circuit.GATE_PIN[g])
            b.bridge((a, 6), (k, 6), (k, 5), (k, 4), (k, 3), (k, 2), net="GND")   # RX GND → 옆 칸 따라 내려감
            b.jumper((k, 2), (k, 0), net="GND")                           # EMIT 줄을 넘어 GND 버스로
            b.bridge((a, 5), (a, 4), (a, 3), (a, 2), (a, 1), net="EMIT_LO")          # TX GND → EMIT_LO
        c += 2
    # 레일 감지 R_RS: +5V_B → 10 kΩ → UNO 2 D2
    b.resistor("R_RS", "10k", (c, 9), "R_RS.1", (c, 8), "R_RS.2")
    b.bridge((c, 9), (c, 10), net="+5V_B")
    b.pin((c, 7), "U2.D2", "→UNO2 D2")
    b.bridge((c, 8), (c, 7), net="SIG")
    b.col_labels.append((c, "레일"))
    c += 1
    # 전원 들어옴 (와고에서 22 AWG 납땜) + Q4 MOSFET 모듈로
    b.pin((c, 10), "TB.+5V", "+5V 입력", kind="wire")
    b.pin((c, 0), "TB.GND", "GND", kind="wire")
    b.pin((c, 1), "Q4.OUT-", "→Q4 OUT−", kind="wire")
    b.pin((c + 3, 0), "Q4.GND", "→Q4 GND", kind="wire")
    b.bus(TOP, 2, c, "+5V_B")
    b.bus(GNDR, 2, c + 3, "GND")
    b.bus(EMR, 2, c, "EMIT_LO")
    # J_I2C (판과 안 이어짐 — Pi 4선이 지나가는 자리). CAP-AI-54 (Issue #9 5번): CAD 193j는 가로(x)로 놓여 핀이 줄 사이(y 15)에 옴
    # → 줄 6, 칸 22~25 가로로 (레일 핀 c20과 띄움). 핀 간격 2.5 vs 구멍 2.54 — 끝 핀에서 0.06 mm [가능성 높음 — 꽂힘]
    jc, jr = 22, 6
    for i, nm in enumerate(("VS", "GND", "SDA", "SCL")):
        b.free_pads[(jc + i, jr)] = "J_I2C " + nm
    (x0, y0), (x1, _y1) = b.xy((jc, jr)), b.xy((jc + 3, jr))
    b.housings.append(("J_I2C (JST XH 4P)", (x0 + x1) / 2, y0, XH4[0], XH4[1]))
    return b


# ============================================================================
# 서보 허브 60 × 40 — 펜 SG90 + 문 MG90S 3
# ============================================================================
def servo_hub():
    b = Board("servo_hub", "서보 허브", 60.0, 40.0)
    servos = [("SG90", "U1.A0", "펜 (UNO1 A0)"), ("MG_IN", "U2.D9", "입구 (UNO2 D9)"),
              ("MG_CAP", "U2.D10", "격리 (UNO2 D10)"), ("MG_REL", "U2.D11", "방생 (UNO2 D11)")]
    GND_R, V_R = 12, 4
    for i, (part, sig, label) in enumerate(servos):
        c = 3 + 4 * i
        # 서보 3핀 헤더 (세로, 위→아래): 갈색 GND · 빨강 +5V · 주황 신호 (서보 커넥터 순서)
        b.pin((c, 11), "%s.GND" % part, "%s 갈" % label.split()[0])
        b.pin((c, 10), "%s.V+" % part, "빨")
        b.pin((c, 9), "%s.SIG" % part, "주")
        b.bridge((c, 11), (c, 12), net="GND")
        b.bridge((c, 10), (c + 1, 10), net="+5V_B")
        b.bridge((c + 1, 10), (c + 1, 9), (c + 1, 8), (c + 1, 7), (c + 1, 6), (c + 1, 5), (c + 1, 4), net="+5V_B")
        b.bridge((c, 9), (c, 8), (c, 7), net="SIG")
        b.pin((c, 6), sig, "→" + label)
        b.col_labels.append((c + 0.5, label.split()[0]))
        b.bridge((c, 7), (c, 6), net="SIG")
    # 레일 부품 (circuit.py C1·C2가 서보 허브, CAP-AI-50 역극성 D_RP): 모두 +5V 버스(r4) ↔ GND 버스(r12)
    # CAP-AI-54 (Issue #9 3·4번): 몸통이 겹쳐 다시 놓음 — D_RP c17, C1은 위로 (몸통이 GND 버스 위), C2는 전원 들어오는 c20
    b.resistor("D_RP", "SB540", (17, 5), "D_RP.K", (17, 11), "D_RP.A", span=6)                 # 줄 표시(K)가 +5V 쪽!
    b.bridge((17, 5), (17, 4), net="+5V_B")
    b.bridge((17, 11), (17, 12), net="GND")
    b.drill[(17, 5)] = b.drill[(17, 11)] = 1.5                                                # 다리 Ø1.2~1.3 > 구멍 Ø1.0
    b.resistor("C1", "1000µ", (19, 11), "C1.+", (19, 13), "C1.-", span=2)                     # 전해 — 긴 다리 +
    b.bridge((19, 11), (19, 10), (19, 9), (19, 8), (19, 7), (19, 6), (19, 5), (19, 4), net="+5V_B")
    b.bridge((19, 13), (19, 12), net="GND")
    b.resistor("C2", "0.1µ", (20, 5), "C2.1", (20, 6), "C2.2")                               # 세라믹 100 nF (2.54)
    b.bridge((20, 5), (20, 4), net="+5V_B")
    b.bridge((20, 6), (20, 7), (20, 8), (20, 9), (20, 10), (20, 11), (20, 12), net="GND")
    b.col_labels.append((18.5, "레일 부품"))
    pc = 22                                   # CAP-AI-54: 전원 전선은 오른쪽 끝 (c20이면 C1 몸통 밑)
    b.pin((pc, V_R), "TB.+5V", "+5V 입력 20AWG", kind="wire")
    b.pin((pc, GND_R), "TB.GND", "GND 입력 20AWG", kind="wire")
    b.bus(GND_R, 3, pc, "GND")
    b.bus(V_R, 4, pc, "+5V_B")
    return b


def pinout_md(boards):
    L = ["# 허브 기판 핀 표 (자동 생성 — `전기회로/hub_boards.py`, 고치지 말고 스크립트를 고칠 것)", ""]
    for b in boards:
        L += ["## %s (%g × %g mm, 구멍 %d × %d)" % (b.title, b.L, b.W, b.nc, b.nr), "", "| 구멍 (칸, 줄) | 표시 | 노드 (circuit.py) | 넷 |", "|---|---|---|---|"]
        for h, (node, label, kind) in sorted(((h, v) for h, v in b.pins.items() if v[2] != "rleg"), key=lambda t: (t[0][0], -t[0][1])):
            L.append("| c%d, r%d | %s | `%s` | %s |" % (h[0], h[1], label or "—", node, NODE_NET.get(node, "?")))
        L += ["", "저항: " + ", ".join("%s %s (c%d r%d–r%d)" % (n, v, a[0], a[1], c[1]) for n, v, a, c in b.res), ""]
        st = b.stats()
        L.append("수: " + ", ".join("%s %s" % kv for kv in st.items()))
        if b.drill:
            L += ["", "**구멍 넓힘** (드릴): " + ", ".join("c%d r%d → Ø%.1f mm" % (h[0], h[1], d) for h, d in sorted(b.drill.items()))]
        if b.housings:
            L += ["", "판과 안 이어지는 부품: " + ", ".join("%s 가운데 (%.2f, %.2f) mm, %.2f × %.2f" % t for t in b.housings) + " — 판 왼쪽 아래 귀퉁이 기준, 긴 쪽이 x"]
        L.append("")
    return "\n".join(L)


def main():
    boards = [gate_hub(), servo_hub()]
    bad = 0
    for b in boards:
        errs = b.check()
        print("== %s: %s" % (b.title, "검사 통과 (넷 일치, 합선 0, 끊김 0)" if not errs else "오류 %d" % len(errs)))
        for e in errs:
            print("   ", e)
        bad += len(errs)
        print("   ", b.stats())
        if b.near:
            print("    몸통 틈 < 0.5 mm:", "; ".join("%s ↔ %s %.2f" % (x, y, g) for g, x, y in b.near))
        if b.drill:
            print("    구멍 넓힘:", ", ".join("c%d r%d → Ø%.1f" % (h[0], h[1], d) for h, d in sorted(b.drill.items())))
        for t in b.housings:
            print("    %s 가운데 (%.2f, %.2f) mm, %.2f × %.2f (판 왼쪽 아래 기준)" % t)
        for side in (False, True):
            fn = os.path.join(OUT, "%s_%s.svg" % (b.name, "solder" if side else "top"))
            open(fn, "w", encoding="utf-8").write(b.svg(side))
    open(os.path.join(OUT, "hub_pinout.md"), "w", encoding="utf-8").write(pinout_md(boards))
    print("그림 →", os.path.relpath(OUT, REPO))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
