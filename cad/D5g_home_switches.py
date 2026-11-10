# -*- coding: utf-8 -*-
"""D5g 원점 스위치 3개 + 투명 격자 (서현, 2026-11-09, CAP-AI-55)

서현 결정 (11/09): 원점(리밋) 스위치 KW11-3Z 3개를 CAD에 넣고 X·Y 원점과 펜 대기 자리를 잰다 / 격자 130 = 투명 아크릴 1.5.
D5g_frame_detail.make() 끝에서 부른다. 다른 스크립트는 고치지 않는다.

스위치 KW11-3Z 레버형: 본체 20 × 6.4 × 10.2, 구멍 Ø2.3 × 2 간격 9.5, 레버 28 [가능성 높음 — 승준
purchase/cad_parts/sj_purchased_parts.py KW11 값, 판매처 대표값. 실물 재기]. 국부 좌표: L(20)·W(6.4, 구멍 방향)·H(10.2, 레버 쪽).
레버는 '눌린 자리'로 그림: 레버 끝 면 = 본체 위 12.2 (H + 1.5 + 0.5).

펌웨어 (design/circuit/firmware/trap_motion): HOME_F 0 / HOME_X −18 / HOME_Y −40 mm, X 0 = CAD x 55, Y = CAD y 그대로.
  F : 바닥 0 (가장 아래)에서 캐리지 158 아랫면 z 262 (레버 자리) 가 레버를 누름 → 스위치는 151_L 안쪽 면 (x 36)에 M2 × 12 두 개
  X : xm 37 (펌웨어 −18, 지금 대기 65에서 dx −28)에서 Y 모터 브래킷 211 −x 면 (69.9 − 28 = 41.9) 이 레버를 누름
      → X 봉(−y) 집게 + 팔 226 (3D 프린트, M3 조임 나사) 밑에 스위치
  Y : ym −40 (지금 자세 그대로)에서 펜 홀더 202 −y 면 (y −54) 이 레버를 누름 (206 면은 212A에 가려짐) → 빔 끝 블록 212A −x 면에 M2 × 12 두 개
"""
import FreeCAD as App
import Part

V = App.Vector
KW = dict(L=20.0, W=6.4, H=10.2, hole_d=2.3, hole_p=9.5, hole_z=3.0, lever=28.0, lever_off=-4.0, lever_t=0.5, lever_gap=1.5)
LEVER_TOP = KW["H"] + KW["lever_gap"] + KW["lever_t"]   # 12.2
XM_HOME, XM_PARK = 37.0, 65.0
DX_HOME = XM_HOME - XM_PARK                              # −28


def _box(O, ax, lo, hi):
    """국부 상자 (lo, hi: (l, w, h)) → 세상 좌표 (축은 ± 세상 축이라 상자 그대로)"""
    pts = []
    for l in (lo[0], hi[0]):
        for w in (lo[1], hi[1]):
            for h in (lo[2], hi[2]):
                pts.append(O + ax[0] * l + ax[1] * w + ax[2] * h)
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
    z0, z1 = min(p.z for p in pts), max(p.z for p in pts)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def switch(O, eL, eW, eH, screw_from="W+", screw_len=12.0):
    """O = 국부 원점 (본체 모서리). eL·eW·eH = 세상 단위 벡터. 반환 (본체+레버, 나사 2, 레버 상자)"""
    k = KW
    ax = (eL, eW, eH)
    body = _box(O, ax, (0, 0, 0), (k["L"], k["W"], k["H"]))
    holes, screws = [], []
    for l in ((k["L"] - k["hole_p"]) / 2, (k["L"] + k["hole_p"]) / 2):
        c = O + eL * l + eH * k["hole_z"]
        holes.append(Part.makeCylinder(k["hole_d"] / 2, k["W"] + 2, c - eW * 1, eW))
        # M2 십자 냄비머리: 머리 Ø3.8 × 1.3 은 W+ 면 바깥, 몸통은 −eW 쪽으로 (본체 지나 받는 면에 박힘)
        top = c + eW * k["W"]
        head = Part.makeCylinder(1.9, 1.3, top, eW)
        shank = Part.makeCylinder(1.0, screw_len, top - eW * screw_len, eW)
        screws.append(head.fuse(shank))
    body = body.cut(Part.makeCompound(holes))
    lever = _box(O, ax, (k["lever_off"], 1.0, k["H"] + k["lever_gap"]), (k["lever_off"] + k["lever"], k["W"] - 1.0, LEVER_TOP))
    return body.fuse(lever).removeSplitter(), screws, lever


def _get(doc, pre):
    return [o for o in doc.Objects if hasattr(o, "Shape") and o.Label.startswith(pre)]


def make_parts():
    X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
    out = []
    # F — 본체 x 36~42.4 (W: 구멍 방향 +x, 옆판 151_L 면 x 36에 붙음), y 3.3~23.3 (L), z 229.8~240 (H 위)
    sF, scF, lvF = switch(V(36.0, 3.3, 262.0 - LEVER_TOP), Y, X, Z)   # 158 아랫면은 이 자리(x 37~46, y −20~20)에서 z 262 [확실 — 선 쏘아 잼]
    # 위 switch()는 나사 머리를 W+ 면(x 42.4) 밖에 두고 몸통을 −x로 12 → 옆판 안 5.6 mm
    out.append(("227f_home_switch_F (KW11-3Z — 바닥 0 mm에서 캐리지 158 아랫면이 누름, 151_L 안쪽 면에 M2 × 12 두 개)", sF, (0.15, 0.15, 0.15)))
    out.append(("227fs_switch_screws_F (M2 × 12 십자 냄비머리 2 — 151_L에 셀프 탭)", Part.makeCompound(scF), (0.1, 0.1, 0.1)))
    # X — 레버 끝 면 x 41.9 (211 −x 면 at 원점), H = +x, L = y (−98 ~ −78), W = z (467.6 ~ 474, 구멍 방향 +z → 나사 머리는 위로? 아니라 아래에서)
    x_lev = 69.9 + DX_HOME - 0.05                            # 41.85 (211 면과 0.05 틈 — 닿음 판정)
    sX, _scX, lvX = switch(V(x_lev - LEVER_TOP, -98.0, 474.0), Y, V(0, 0, -1), X)
    # 나사는 아래(본체 밑면 z 467.6)에서 위로 팔 226 안으로 — 직접 만듦
    scX = []
    for l in ((KW["L"] - KW["hole_p"]) / 2, (KW["L"] + KW["hole_p"]) / 2):
        c = V(x_lev - LEVER_TOP + KW["hole_z"], -98.0 + l, 474.0 - KW["W"])
        scX.append(Part.makeCylinder(1.9, 1.3, c - V(0, 0, 1.3)).fuse(Part.makeCylinder(1.0, 12.0, c)))
    out.append(("227x_home_switch_X (KW11-3Z — xm 37 (펌웨어 X −18)에서 Y 모터 브래킷 211 −x 면이 누름, 팔 226 밑에 M2 × 12 두 개)", sX, (0.15, 0.15, 0.15)))
    out.append(("227xs_switch_screws_X (M2 × 12 십자 냄비머리 2 — 아래에서 팔 226에 셀프 탭)", Part.makeCompound(scX), (0.1, 0.1, 0.1)))
    # 226 X 봉 집게 + 팔 (3D 프린트): 집게 x 22~41, y −73~−57, z 472~488 (Ø8 봉 구멍 y −65 z 480, 아래 틈 1 + M3 조임)
    cl = Part.makeBox(19, 16, 18, V(22, -73, 470))
    cl = cl.cut(Part.makeCylinder(4.0, 21, V(21.5, -65, 480), X))
    cl = cl.cut(Part.makeBox(21, 1.0, 11, V(21.5, -65.5, 470 - 1)))                    # 아래 쪼갬 틈 (조이면 봉을 잡음)
    cl = cl.cut(Part.makeCylinder(1.7, 17, V(24.5, -73.5, 473.5), Y))                  # M3 조임 나사 구멍 (y 방향, 봉 아래, 팔 옆)
    arm = Part.makeBox(13, 27, 14, V(28, -100, 474))                                   # 팔 x 28~41 (나사 머리 x 21.8~27.3 비킴)
    out.append(("226_x_home_clamp (3D 프린트 — X 봉 −y 집게 + 팔, M3 × 16 조임 1, 스위치 X 받침)", cl.fuse(arm).removeSplitter(), (0.95, 0.45, 0.05)))
    out.append(("226s_clamp_screw (M3 × 16 십자 냄비머리 + 너트 — 집게 조임)", Part.makeCylinder(2.75, 2.0, V(24.5, -75.0, 473.5), Y).fuse(
        Part.makeCylinder(1.5, 16, V(24.5, -73.0, 473.5), Y)).fuse(Part.makeCylinder(3.2, 2.4, V(24.5, -57.0, 473.5), Y)), (0.1, 0.1, 0.1)))
    # Y — 빔 끝 블록 212A −x 면 (x 77.4)에 붙음: W = −x (x 71 ~ 77.4, 구멍 방향), L = z (440 ~ 460), H = +y (레버 끝 면 y −55)
    y_lev = -54.0          # 펜 홀더 202 −y 면 (x 67~81.4). 206 −y 면(−55)은 x 82~ 라 끝 블록 212A가 1 mm 틈으로 가림 [확실 — 선 쏘아 잼]
    xb = 77.3              # 212A −x 면 77.39 에서 0.1 띄움
    sY, _s, lvY = switch(V(xb, y_lev - LEVER_TOP, 440.0), Z, V(-1, 0, 0), Y)
    scY = []
    for l in ((KW["L"] - KW["hole_p"]) / 2, (KW["L"] + KW["hole_p"]) / 2):
        c = V(xb - KW["W"], y_lev - LEVER_TOP + KW["hole_z"], 440.0 + l)
        scY.append(Part.makeCylinder(1.9, 1.3, c - X * 1.3, X).fuse(Part.makeCylinder(1.0, 12.0, c, X)))
    out.append(("227y_home_switch_Y (KW11-3Z — ym −40에서 펜 홀더 202 −y 면이 누름, 빔 끝 블록 212A −x 면에 M2 × 12 두 개, 빔과 같이 움직임)", sY, (0.15, 0.15, 0.15)))
    out.append(("227ys_switch_screws_Y (M2 × 12 십자 냄비머리 2 — 212A에 셀프 탭)", Part.makeCompound(scY), (0.1, 0.1, 0.1)))
    levers = {"F": lvF, "X": lvX, "Y": lvY}
    return out, levers


def apply(doc):
    for o in [x for x in doc.Objects if x.Label.startswith(("226_", "226s_", "227"))]:
        doc.removeObject(o.Name)
    out, _lv = make_parts()
    rep = {}
    for nm, shp, col in out:
        o = doc.addObject("Part::Feature", "HS_" + nm.split(" ")[0])
        o.Label = nm
        o.Shape = shp
        if App.GuiUp:
            o.ViewObject.ShapeColor = col
        grp = [g for g in doc.Objects if g.Name == ("GSJ_B" if nm.startswith("226_") else "GSJ_A")]
        if grp:
            grp[0].addObject(o)
        b = shp.BoundBox
        rep[nm.split(" ")[0]] = [round(v, 1) for v in (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax)]
    # 격자 130 = 투명 아크릴 1.5 (서현 11/09) — 모양·치수 그대로, 이름·색만
    for o in _get(doc, "130_grid"):
        o.Label = "130_grid (투명 아크릴 1.5 레이저 가공 — 구멍 Ø3 · 간격 4.4 그대로, 서현 11/09)"
        if App.GuiUp:
            o.ViewObject.ShapeColor = (0.75, 0.90, 1.0)
            o.ViewObject.Transparency = 70
    doc.recompute()
    return rep


# ---------------- 검사: 원점 자세에서 레버가 닿는지 + 움직이는 길 전체에서 겹침 ----------------
BEAM = ("207_", "208_", "209_", "209r", "210_", "211_", "212_", "222_", "225_", "227y")
CARR = ("201_", "202_", "203_", "205", "206_", "221_", "223_", "224_")
FLOOR = ("140_", "146_", "147_", "148", "149_", "158_", "159_", "227p")   # (CAP-AI-60) 누름 스위치는 캐리지와 같이 움직임


def check(doc):
    _out, lv = make_parts()
    objs = [o for o in doc.Objects if hasattr(o, "Shape") and o.TypeId != "App::DocumentObjectGroup" and not o.Shape.isNull()
            and (not App.GuiUp or o.ViewObject.Visibility) and not o.Label.startswith(("REF_", "196_gate"))]
    new = [o for o in objs if o.Label.startswith(("226", "227"))]
    res = {"contact": {}, "hits": []}

    def off(o, dx, dy, dz):
        return V(dx if o.Label.startswith(BEAM + CARR) else 0, dy if o.Label.startswith(CARR) else 0,
                 dz if o.Label.startswith(FLOOR) else 0)

    def mbb(b, v):                       # 상자만 옮김 (모양 복사 없이)
        return App.BoundBox(b.XMin + v.x, b.YMin + v.y, b.ZMin + v.z, b.XMax + v.x, b.YMax + v.y, b.ZMax + v.z)

    # 닿음 (원점 자세): 레버 ↔ 누르는 부품 거리
    for ax, pre, d in (("F", "158_", (0, 0, 0)), ("X", "211_", (DX_HOME, 0, 0)), ("Y", "202_", (0, 0, 0))):
        o = [x for x in objs if x.Label.startswith(pre)][0]
        s = o.Shape.copy()
        s.translate(V(*d))
        res["contact"][ax] = round(lv[ax].distToShape(s)[0], 3)
    # 겹침: 자세 여러 개 (X −28·−14·0·+7.6, Y 0·+29·+57.6, 바닥 0·18·36.5)
    poses = [(dx, dy, dz) for dx in (DX_HOME, -14.0, 0.0, 7.6) for dy in (0.0, 29.0, 57.6) for dz in (0.0, 36.5)]   # 24 자세
    sol = {o.Name: [(s, s.BoundBox) for s in (o.Shape.Solids or [o.Shape])] for o in objs}
    for n in new:
        for o in objs:
            if o is n:
                continue
            for p in poses:
                vn = V(p[0], 0, 0) if n.Label.startswith("227y") else V(0, 0, 0)
                vo = off(o, *p)
                if not mbb(n.Shape.BoundBox, vn).intersect(mbb(o.Shape.BoundBox, vo)):
                    continue
                v = 0.0                                          # 고체 상자끼리 닿는 것만 복사·불 연산
                for a_, ab in sol[n.Name]:
                    for b_, bb in sol[o.Name]:
                        if mbb(ab, vn).intersect(mbb(bb, vo)):
                            sa, sb = a_.copy(), b_.copy()
                            sa.translate(vn)
                            sb.translate(vo)
                            v += sa.common(sb).Volume
                if v > 0.01:
                    res["hits"].append((n.Label[:24], o.Label[:50], [round(q, 1) for q in p], round(v, 3)))
                    break
    return res
