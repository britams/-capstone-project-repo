# -*- coding: utf-8 -*-
"""D5e 전체 조립 — 2020 알루미늄 프로파일 프레임(실제 T홈 단면) + 상용 트랩(야생 말벌 포획기, 실측표) + D5e 모듈 (CAP-AI-21)
D5e_module_kinematic.py 의 모듈은 그대로 쓰고, 단순 상자였던 100_frame과 원기둥·원뿔이었던 REF 트랩만 바꾼다.

실행 (FreeCAD 1.x GUI, 매크로 또는 MCP):
    import sys; sys.path.insert(0, r"<repo>/cad"); import D5e_full_assembly as A; doc = A.make_full(); A.render_all(doc, r"<repo>/cad")
치수 근거
- 2020 프로파일: 바깥 20×20, 홈 입구 6.2, 가운데 구멍 Ø4.2 (미스미 HFS5-2020 꼴 대표값) [가능성 높음] — 자르는 길이는 프레임 기하에서 나옴
- 트랩: design/2026-10-28_상용트랩_실측표.md — 차양막 Ø260·윗면 180, 차양막 아래 145, 구멍 D1 55·턱 D2 90, 포획통 높이 220·바닥 D3 94,
  노란 깔때기 D6 50 → D5 19. 유인액 통·몸통 지름·포획통 최대 지름은 사진 비례로 잡은 값 [추측]
"""
import math

import FreeCAD as App
import Part

import D5e_module_kinematic as K

V = App.Vector
DOC = "D5e_full_assembly"
S = 20.0

# ---------------- 2020 프로파일 ----------------
P2020 = dict(slot=6.2, lip=1.8, ch_w=8.0, ch_d=3.2, bore=4.2)


def section2020():
    """원점 중심, XY 평면의 2020 T홈 단면 (면)"""
    h = S / 2
    face = Part.makePlane(S, S, V(-h, -h, 0))
    sol = face.extrude(V(0, 0, 1))
    cuts = []
    for ang in (0, 90, 180, 270):
        rot = App.Rotation(V(0, 0, 1), ang)
        lip = Part.makeBox(P2020["slot"], P2020["lip"] + 0.2, 3, V(-P2020["slot"] / 2, h - P2020["lip"], -1))
        ch = Part.makeBox(P2020["ch_w"], P2020["ch_d"], 3, V(-P2020["ch_w"] / 2, h - P2020["lip"] - P2020["ch_d"], -1))
        for b in (lip, ch):
            b.rotate(V(0, 0, 0), V(0, 0, 1), ang)
            cuts.append(b)
    cuts.append(Part.makeCylinder(P2020["bore"] / 2, 3, V(0, 0, -1)))
    sol = sol.cut(Part.makeCompound(cuts))
    return [f for f in sol.Faces if abs(f.Surface.Axis.z) > 0.99 and f.CenterOfMass.z < 0.5][0]


SEC = None


def member(p0, p1):
    """p0 → p1 으로 뻗은 2020 부재 (단면 중심선 기준)"""
    global SEC
    if SEC is None:
        SEC = section2020()
    p0, p1 = V(*p0), V(*p1)
    d = p1 - p0
    L = d.Length
    f = SEC.copy()
    sol = f.extrude(V(0, 0, L))
    rot = App.Rotation(V(0, 0, 1), d)
    sol.Placement = App.Placement(p0, rot)
    return sol


def bracket(p, nx, nz, t=3.0):
    """L 브래킷 20×20 (p: 기둥 면·레일 중심선·레일 면이 만나는 점, nx: 레일 방향, nz: 레일 면에서 바깥(브래킷 쪽))
    가로 다리는 레일 면에 붙고(레일 방향 20), 세로 다리는 기둥 면에 붙음(nz 방향 20). 폭은 레일 폭 20 가운데."""
    a = Part.makeBox(S, S, t, V(0, -S / 2, 0))
    b = Part.makeBox(t, S, S, V(0, -S / 2, 0))
    shp = a.fuse(b)
    m = App.Matrix()
    ex, ez = V(*nx), V(*nz)
    ey = ez.cross(ex)
    m.A11, m.A21, m.A31 = ex.x, ex.y, ex.z
    m.A12, m.A22, m.A32 = ey.x, ey.y, ey.z
    m.A13, m.A23, m.A33 = ez.x, ez.y, ez.z
    shp = shp.transformGeometry(m)
    shp.translate(V(*p))
    return shp


def frame():
    """프레임 부재 목록 (이름, 형상, 길이) — D5e FR 값 그대로"""
    c, s = K.FR["c"], S
    top = K.TOP_BOT
    mem = []
    for i, (x, y) in enumerate(((-c, -c), (c, -c), (c, c), (-c, c))):
        mem.append(("100a_post_%d" % (i + 1), member((x, y, 0), (x, y, top)), top))
    levels = [("0", 0.0), ("deck", K.FR["deck_z"]), ("gantry", K.FR["gantry_z"]), ("top", K.FR["top_z"])]
    for nm, z in levels:
        zc = z + s / 2
        for y in (-c, c):
            mem.append(("100b_rail_%s_x%+d" % (nm, y), member((-c + s / 2, y, zc), (c - s / 2, y, zc)), 2 * c - s))
        for x in (-c, c):
            mem.append(("100b_rail_%s_y%+d" % (nm, x), member((x, -c + s / 2, zc), (x, c - s / 2, zc)), 2 * c - s))
    for nm, z in (("deck", K.FR["deck_z"]), ("top", K.FR["top_z"])):
        for y in (-K.FR["cross_y"], K.FR["cross_y"]):
            mem.append(("100c_cross_%s_y%+d" % (nm, y), member((-c + s / 2, y, z + s / 2), (c - s / 2, y, z + s / 2)), 2 * c - s))
    gx = K.FR["gantry_x"]
    mem.append(("100d_gantry_rail_x%+d" % gx, member((gx, -c + s / 2, K.FR["gantry_z"] + s / 2), (gx, c - s / 2, K.FR["gantry_z"] + s / 2)), 2 * c - s))
    # 브래킷: 기둥–둘레 레일 이음마다 레일 아래 (바닥 단은 위)
    br = []
    for nm, z in levels:
        for (x, y) in ((-c, -c), (c, -c), (c, c), (-c, c)):
            sx, sy = (1 if x < 0 else -1), (1 if y < 0 else -1)
            zb = z + s if nm == "0" else z
            nzv = (0, 0, 1) if nm == "0" else (0, 0, -1)
            br.append(bracket((x + sx * s / 2, y, zb), (sx, 0, 0), nzv))
            br.append(bracket((x, y + sy * s / 2, zb), (0, sy, 0), nzv))
    return mem, Part.makeCompound(br)


# ---------------- 상용 트랩 (REF, 하중 없음) ----------------
def revolve(pts):
    """(r, z) 점들로 z축 회전체"""
    w = Part.makePolygon([V(r, 0, z) for r, z in pts] + [V(pts[0][0], 0, pts[0][1])])
    return Part.Face(w).revolve(V(0, 0, 0), V(0, 0, 1), 360)


def trap_lower():
    out = {}
    # 유인액 통 (갈색, 주름) z 0~75 [추측: 사진 비례]
    cup = revolve([(0, 0), (72, 0), (78, 6), (92, 75), (0, 75)])
    flutes = [Part.makeCylinder(7, 70, V(92 * math.cos(math.radians(a)), 92 * math.sin(math.radians(a)), 6)) for a in range(0, 360, 20)]
    out["REF_trap_bait_cup"] = cup.cut(Part.makeCompound(flutes))
    # 몸통 (초록) z 75~145, 위 구멍 D7 55
    body = revolve([(0, 75), (95, 75), (100, 110), (100, 145), (0, 145)])
    body = body.cut(Part.makeCylinder(27.5, 80, V(0, 0, 100)))
    # 노란 깔때기 2개: 바깥 벽 Ø50 → 안쪽 Ø19, 25° 아래로 기울어 들어감
    fun = []
    for a in (90, 270):
        u = V(math.cos(math.radians(a)), math.sin(math.radians(a)), 0)
        p0 = u * 101 + V(0, 0, 112)
        d = (u * -1) * math.cos(math.radians(25)) + V(0, 0, -math.sin(math.radians(25)))
        outer = Part.makeCone(25, 9.5 + 1.5, 45, p0, d)
        inner = Part.makeCone(23.5, 9.5, 46, p0 - d * 0.5, d)
        body = body.cut(Part.makeCone(24, 9.5, 45, p0, d))
        fun.append(outer.cut(inner))
    out["REF_trap_body"] = body
    out["REF_trap_funnels"] = Part.makeCompound(fun)
    # 차양막 (초록): 바깥 Ø260, 아래 145 → 윗면 180, 가운데 구멍 D1 55, 바깥 테두리 두께 6
    aw = revolve([(27.5, 172), (130, 145), (130, 151), (45, 180), (27.5, 180)])
    ribs = [Part.makeBox(90, 2, 6, V(42, -1, 0)) for _ in range(8)]
    rib_c = []
    for i, r in enumerate(ribs):
        r.rotate(V(0, 0, 0), V(0, 0, 1), i * 45 + 22.5)
        r = r.common(revolve([(44, 150), (128, 150), (128, 156), (44, 186)]))
        rib_c.append(r)
    out["REF_trap_awning"] = aw.fuse(Part.makeCompound(rib_c)) if rib_c else aw
    # 턱 D2 90 / 안 55, 높이 10, 돌려 끼움 홈 4개 (실측표: 4토막)
    ring = Part.makeCylinder(45, 10, V(0, 0, 180)).cut(Part.makeCylinder(27.5, 12, V(0, 0, 179)))
    gaps = []
    for i in range(4):
        g = Part.makeBox(30, 8, 6, V(25, -4, 184))
        g.rotate(V(0, 0, 0), V(0, 0, 1), i * 90 + 45)
        gaps.append(g)
    out["REF_trap_ring"] = ring.cut(Part.makeCompound(gaps))
    return out


def trap_container(z0):
    """포획통 (투명): 바닥 테두리 D3 94/안 67, 높이 220 (고무마개 포함), 최대 Ø190 [추측]"""
    out = {}
    pts = [(33.5, z0), (47, z0), (47, z0 + 12)]
    for i in range(1, 19):
        t = i / 18.0
        th = -math.pi / 2 + t * math.pi * 0.86
        r = 95 * math.cos(th)
        z = z0 + 12 + 85 + 85 * math.sin(th) * (1.0 if th > 0 else 0.98)
        pts.append((max(r, 20), z))
    pts += [(18, z0 + 188), (16, z0 + 188), (16, z0 + 186)]
    outer = revolve([(0, z0 + 12)] + pts[2:] + [(0, z0 + 188)])
    shell = outer.cut(revolve([(0, z0 + 13.5)] + [(max(r - 1.5, 15), z) for r, z in pts[3:-3]] + [(14.5, z0 + 186.5), (0, z0 + 186.5)]))
    rim = Part.makeCylinder(47, 12, V(0, 0, z0)).cut(Part.makeCylinder(33.5, 14, V(0, 0, z0 - 1)))
    out["REF_trap_container"] = shell.fuse(rim)
    out["REF_trap_cap"] = Part.makeCylinder(17, 32, V(0, 0, z0 + 188))
    # 바닥 실리콘 포획술: 가운데 Ø5 구멍, 별 모양 살 16개 (사진)
    star = Part.makeCone(33, 2.5, 18, V(0, 0, z0 + 12)).cut(Part.makeCone(31.5, 1.0, 18, V(0, 0, z0 + 12)))
    slits = []
    for i in range(16):
        b = Part.makeBox(28, 2.2, 20, V(4, -1.1, z0 + 11))
        b.rotate(V(0, 0, 0), V(0, 0, 1), i * 22.5)
        slits.append(b)
    out["REF_trap_silicone_star"] = star.cut(Part.makeCompound(slits))
    return out


# ---------------- 문서 ----------------
COLORS = {"REF_trap_bait_cup": ((0.45, 0.30, 0.20), 0), "REF_trap_body": ((0.42, 0.70, 0.30), 0), "REF_trap_funnels": ((0.95, 0.70, 0.15), 0),
          "REF_trap_awning": ((0.50, 0.80, 0.30), 0), "REF_trap_ring": ((0.50, 0.80, 0.30), 0),
          "REF_trap_container": ((0.80, 0.88, 0.95), 70), "REF_trap_cap": ((0.12, 0.12, 0.12), 0), "REF_trap_silicone_star": ((0.95, 0.95, 0.95), 30),
          "100_brackets": ((0.40, 0.40, 0.42), 0)}


def make_full(J=None):
    P, M = K.build()
    for n in [n for n in P if n.startswith("REF_trap") or n == "100_frame"]:
        P.pop(n)
        M.pop(n)
    K.DOC_NAME = DOC
    doc = K.make_doc(P, M, J)
    mem, br = frame()
    grp = doc.addObject("App::DocumentObjectGroup", "G100_frame_2020")
    grp.Label = "100_frame_2020 (%d개)" % len(mem)
    for nm, shp, L in mem:
        o = doc.addObject("Part::Feature", "P" + nm.replace("+", "p").replace("-", "m"))
        o.Label = "%s (2020, L %d)" % (nm, round(L))
        o.Shape = shp
        grp.addObject(o)
        if App.GuiUp:
            o.ViewObject.ShapeColor = (0.75, 0.77, 0.80)
    ob = doc.addObject("Part::Feature", "P100_brackets")
    ob.Label = "100_brackets"
    ob.Shape = br
    trap = trap_lower()
    trap.update(trap_container(K.TOP_BOT + K.TOP["t"] + K.TRAP["ring_h"]))
    tg = doc.addObject("App::DocumentObjectGroup", "GREF_trap")
    tg.Label = "REF 상용 트랩 (야생 말벌 포획기, 실측표)"
    for nm, shp in trap.items():
        o = doc.addObject("Part::Feature", "P" + nm)
        o.Label = nm
        o.Shape = shp
        tg.addObject(o)
    doc.recompute()
    if App.GuiUp:
        for o in doc.Objects:
            if o.Label in COLORS:
                col, tr = COLORS[o.Label]
                o.ViewObject.ShapeColor = col
                o.ViewObject.Transparency = tr
            if o.Label in ("REF_camera_view",):
                o.ViewObject.Visibility = False
    return doc


def cut_list():
    mem, _ = frame()
    out = {}
    for nm, shp, L in mem:
        out[round(L)] = out.get(round(L), 0) + 1
    return out


VIEWS = [
    ("도1_전체_등각", "iso", None, ()),
    ("도2_정면", "front", None, ()),
    ("도3_측면", "right", None, ()),
    ("도4_위", "top", None, ("REF_trap_container", "REF_trap_cap", "REF_trap_silicone_star", "105_top_plate", "104_dome_coupling")),
    ("도5_모듈_등각", "iso", (-140, 190, -130, 130, 200, 500), ("REF_trap_container", "REF_trap_cap", "REF_trap_silicone_star", "105_top_plate", "104_dome_coupling")),
]


def render(doc, out_dir, view, W=1800, H=1500):
    import FreeCADGui as Gui
    name, kind, box, hide = view
    gd = Gui.getDocument(doc.Name)
    v = gd.ActiveView if gd.ActiveView else Gui.activeDocument().activeView()
    hidden = []
    for o in doc.Objects:
        if o.Label in hide and o.ViewObject.Visibility:
            o.ViewObject.Visibility = False
            hidden.append(o)
    getattr(v, {"iso": "viewIsometric", "front": "viewFront", "right": "viewRight", "top": "viewTop"}[kind])()
    if box:
        x0, x1, y0, y1, z0, z1 = box
        fb = doc.addObject("Part::Feature", "FitBox")
        fb.Shape = Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
        vis = {o.Name: o.ViewObject.Visibility for o in doc.Objects if hasattr(o, "ViewObject") and o.ViewObject}
        for o in doc.Objects:
            if hasattr(o, "ViewObject") and o.ViewObject and o.Name != "FitBox":
                o.ViewObject.Visibility = False
        v.fitAll()
        for o in doc.Objects:
            if o.Name in vis:
                o.ViewObject.Visibility = vis[o.Name]
        doc.removeObject("FitBox")
    else:
        v.fitAll()
    path = "%s/D5e_%s.png" % (out_dir, name)
    v.saveImage(path, W, H, "White")
    for o in hidden:
        o.ViewObject.Visibility = True
    return path
