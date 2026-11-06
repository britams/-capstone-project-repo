# -*- coding: utf-8 -*-
"""D5g 고정(체결) 보강 — 얹기만 했던 부품을 볼트로 잡음 (승준, 2026-11-06 밤, CAP-AI-SJ-49)

승준 지적: '부품 지지도 안 되어 있다'. 닿음 그래프(모든 부품 쌍 거리 ≤ 0.3 mm)로 보면 상용 트랩(REF) 말고는 전부
프레임과 이어져 있었지만, '닿음'일 뿐 볼트가 없는 곳이 있었음 [확실 — 검사 스크립트 결과]:
  218 X 봉 받침 4개(레일 위 얹기), 217 X 모터판(레일 아래 붙기), 105 위판, 101 데크(급이 발 볼트만 지나감),
  199a Pi 선반(구멍만 있고 볼트 없음), 194b 비상 정지 판(구멍만), 151 구동 옆판 2장·102 칼라(데크에 그냥 닿음)
고친 것:
  2020 프레임에 닿는 것 → M5 볼트 + 슬라이드 T너트 (100f·100g와 같은 물건)
  데크에 서는 3D 프린트 부품 → 아래에서 M3 × 10 볼트가 데크를 지나 부품 속 열 압입 인서트(McMaster 94459A130)에
  볼트 McMaster: M5 × 8 91292A122? → 표는 purchase/ 문서 (M5 × 8은 M12 미스미 짝), M5 × 10 91292A124, M3 × 10 91292A113 [확실 — 페이지 제목]
"""
import FreeCAD as App
import Part

V = App.Vector


def tnut_at(G, p, n, along):
    """슬라이드 T너트: 프로파일 면 위 점 p, 바깥 법선 n, 홈 방향 along (D5g T너트 모양 그대로)"""
    t = G.tnut_local("rail")
    t.translate(V(-G.BR["hole_at"], 0, 0))
    return G.to_world(t, tuple(p), tuple(along), tuple(n))


def bolt_at(p, n, t_part, L, d=5.0, head_d=8.5, head_h=5.0):
    """p: 받는 면 위 점, n: 바깥 법선(볼트 머리 쪽), t_part: 조이는 부품 두께. 머리는 p + n·t_part 위"""
    n = V(*n)
    n.normalize()
    q = V(*p) + n * t_part
    return Part.makeCylinder(d / 2, L, q, n * -1).fuse(Part.makeCylinder(head_d / 2, head_h, q, n))


def hole(p, n, d, depth_back=30.0, depth_front=30.0):
    n = V(*n)
    n.normalize()
    return Part.makeCylinder(d / 2, depth_back + depth_front, V(*p) - n * depth_back, n)


def fasten(doc, G):
    """반환: 새로 만든 문서 객체 목록. G = D5g_frame_detail 모듈"""
    import D5e_module_kinematic as K
    get = lambda pre: [o for o in doc.Objects if o.Label.startswith(pre) and hasattr(o, "Shape")][0]
    bolts, nuts = [], []
    notes = []
    gz_top = K.FR["gantry_z"] + 20.0                                     # 갠트리 레일 윗면 472
    # 1) 218 X 봉 받침: 레일 폭 전체로 늘리고 레일 가운데 홈에 M5 × 10 세로 (받침 바닥 두께 16 중 6 남기고 깊은 자리파기)
    o = get("218_rod_supports")
    new = []
    for s in o.Shape.Solids:
        b = s.BoundBox
        yc = (b.YMin + b.YMax) / 2
        if b.XMin < 0:            # 100d 위 (x −28 ~ −8)
            xr, x0, x1 = -18.0, -28.0, b.XMax
        else:                     # 둘레 레일 y+170 위 (x 160 ~ 180)
            xr, x0, x1 = 170.0, b.XMin, 180.0
        if x0 < b.XMin - 0.01:                                           # 늘린 부분만 붙임 (봉 구멍은 그대로)
            s = s.fuse(Part.makeBox(b.XMin - x0 + 0.5, b.YLength, b.ZLength, V(x0, b.YMin, b.ZMin)))
        if x1 > b.XMax + 0.01:
            s = s.fuse(Part.makeBox(x1 - b.XMax + 0.5, b.YLength, b.ZLength, V(b.XMax - 0.5, b.YMin, b.ZMin)))
        s = s.cut(Part.makeCylinder(2.75, 40, V(xr, yc, gz_top - 5)))
        s = s.cut(Part.makeCylinder(4.75, 20, V(xr, yc, gz_top + 6.0)))                       # 머리 자리 (위 6 mm 살 남김)
        new.append(s.removeSplitter())
        bolts.append(bolt_at((xr, yc, gz_top), (0, 0, 1), 6.0, 10.0))
        nuts.append(tnut_at(G, (xr, yc, gz_top), (0, 0, 1), (0, 1, 0)))
    o.Shape = Part.makeCompound(new)
    o.Label = "218_rod_supports (X 봉 받침 4, 3D 프린트 — 레일에 M5 × 10 + T너트)"
    notes.append("218 × 4: M5 × 10 + T너트")
    # 2) 217 X 모터판: 위에 날개(두께 4)를 붙여 레일 아랫면 홈에 M5 × 8 두 개
    o = get("217_x_motor_plate")
    zr = K.FR["gantry_z"]                                                  # 레일 아랫면 452
    b = o.Shape.BoundBox
    fl = Part.makeBox(180.0 - 158.0, b.YLength, 4.0, V(158.0, b.YMin, zr - 4.0))
    sh = o.Shape.fuse(fl)
    for yy in (b.YMin + 7.0, b.YMax - 7.0):
        sh = sh.cut(Part.makeCylinder(2.75, 20, V(170.0, yy, zr - 10)))
        bolts.append(bolt_at((170.0, yy, zr), (0, 0, -1), 4.0, 8.0))
        nuts.append(tnut_at(G, (170.0, yy, zr), (0, 0, -1), (0, 1, 0)))
    o.Shape = sh.removeSplitter()
    o.Label = "217_x_motor_plate (3D 프린트 — 위 날개를 레일 아랫면에 M5 × 8 두 개)"
    notes.append("217: M5 × 8 × 2 + T너트")
    # 3) 105 위판 / 101 데크: 가로대(y ±80) 윗면 홈에 M5 × 10 네 개씩
    for pre, z_rail_top, pts, t in (("105_top_plate", K.FR["top_z"] + 20.0, [(-60, -80), (60, -80), (-60, 80), (60, 80)], 5.0),
                                    ("101_deck", K.FR["deck_z"] + 20.0, [(-122, -80), (88, -80), (-50, 80), (88, 80)], 5.0)):
        o = get(pre)
        sh = o.Shape
        for x, y in pts:
            sh = sh.cut(Part.makeCylinder(2.75, 20, V(x, y, z_rail_top - 5)))
            bolts.append(bolt_at((x, y, z_rail_top), (0, 0, 1), t, 10.0))
            nuts.append(tnut_at(G, (x, y, z_rail_top), (0, 0, 1), (1, 0, 0)))
        o.Shape = sh.removeSplitter()
        notes.append("%s: M5 × 10 × 4 + T너트" % pre.split("_")[0])
    get("105_top_plate").Label = "105_top_plate (위판 — 가로대에 M5 × 10 네 개)"
    # 4) 199a Pi 선반: 벽(두께 3) 구멍 2개 → 위 가로대(y+80) 안쪽 면(y 70) 옆 홈 (z 600)
    o = get("199a_pi_shelf")
    for f in o.Shape.Faces:
        if f.Surface.__class__.__name__ == "Cylinder" and abs(f.Surface.Radius - 2.75) < 0.01 and abs(f.Surface.Axis.y) > 0.99:
            c = f.Surface.Center
            p = (c.x, K.FR["cross_y"] - 10.0, K.FR["top_z"] + 10.0)
            if not any(abs(p[0] - bb.BoundBox.Center.x) < 0.5 and abs(bb.BoundBox.Center.y - (p[1] - 5)) < 3 for bb in bolts):
                bolts.append(bolt_at(p, (0, -1, 0), 3.0, 8.0))
                nuts.append(tnut_at(G, p, (0, -1, 0), (1, 0, 0)))
    notes.append("199a: M5 × 8 × 2 + T너트")
    # 5) 194b 비상 정지 판: 구멍 2 (x −185 축) → 데크 높이 둘레 레일 바깥 면(x −180) 홈 (z 190)
    o = get("194b_estop_plate")
    for f in o.Shape.Faces:
        if f.Surface.__class__.__name__ == "Cylinder" and abs(f.Surface.Radius - 2.75) < 0.01:
            c = f.Surface.Center
            p = (-180.0, c.y, c.z)
            bolts.append(bolt_at(p, (-1, 0, 0), 4.0, 8.0))
            nuts.append(tnut_at(G, p, (-1, 0, 0), (0, 1, 0)))
    notes.append("194b: M5 × 8 × 2 + T너트")
    # 6) 데크 위 3D 프린트 부품: 아래에서 M3 × 10 (데크 5 + 인서트 5) — 151 옆판은 바깥에 보스(Ø7, 높이 8) 붙임, 102 칼라는 데크 아래라 위에서 아래로
    deck = get("101_deck")
    dz = K.FR["deck_z"] + 25.0                                           # 데크 윗면 205
    m3, ins = [], []
    dsh = deck.Shape
    for pre, pts, side in (("151_drive_side_L", [(29.0, 20.0), (29.0, -20.0)], "up"),
                           ("151_drive_side_R", [(81.0, 20.0), (81.0, -20.0)], "up"),
                           ("102_collar", [(45.47, 26.25), (45.47, -26.25), (-45.47, 26.25), (-45.47, -26.25)], "down")):
        o = get(pre)
        sh = o.Shape
        for x, y in pts:
            if side == "up":
                sh = sh.fuse(Part.makeCylinder(3.5, 8.0, V(x, y, dz)))
                if pre.endswith("L"):
                    sh = sh.fuse(Part.makeBox(3.0, 6.0, 8.0, V(x, y - 3.0, dz)))
                else:
                    sh = sh.fuse(Part.makeBox(3.0, 6.0, 8.0, V(x - 3.0, y - 3.0, dz)))
                sh = sh.cut(Part.makeCylinder(2.0, 6.0, V(x, y, dz)))
                ins.append(Part.makeCylinder(2.0, 4.3, V(x, y, dz)).cut(Part.makeCylinder(1.25, 5, V(x, y, dz - 0.5))))
                m3.append(bolt_at((x, y, dz - 5.0), (0, 0, -1), 0.0, 10.0, 3.0, 5.5, 3.0))
            else:
                zc = dz - 5.0                                            # 칼라 윗면 = 데크 아랫면 200
                sh = sh.fuse(Part.makeCylinder(3.5, 15.0, V(x, y, zc - 15.0)))         # 칼라 고리(두께 3) 바깥에 보스 Ø7 (트랩 고리 r45 쪽은 안 건드림)
                sh = sh.cut(Part.makeCylinder(2.0, 6.0, V(x, y, zc - 6.0)))
                ins.append(Part.makeCylinder(2.0, 4.3, V(x, y, zc - 4.3)).cut(Part.makeCylinder(1.25, 5, V(x, y, zc - 4.8))))
                m3.append(bolt_at((x, y, zc), (0, 0, 1), 5.0, 10.0, 3.0, 5.5, 3.0))
            dsh = dsh.cut(Part.makeCylinder(1.7, 20, V(x, y, dz - 10)))
        o.Shape = sh.removeSplitter()
    deck.Shape = dsh.removeSplitter()
    deck.Label = "101_deck (데크 판 — 가로대에 M5 × 10 네 개, 급이 발·보드·옆판·칼라 구멍)"
    notes.append("151 L/R·102: M3 × 10 × 8 + 인서트 8")
    out = []
    for nm, lst, col in (("100j_bolt_M5_parts (부품 → 프레임, %d개)" % len(bolts), bolts, (0.1, 0.1, 0.1)),
                         ("100k_tnut_M5_parts (%d개)" % len(nuts), nuts, (0.85, 0.75, 0.2)),
                         ("100m_bolt_M3x10_deck (데크 아래에서, %d개, McMaster 91292A113)" % len(m3), m3, (0.1, 0.1, 0.1)),
                         ("100n_insert_M3_heatset_deck (%d개, McMaster 94459A130)" % len(ins), ins, (0.8, 0.65, 0.25))):
        for old in [x for x in doc.Objects if x.Label.split(" ")[0] == nm.split(" ")[0]]:
            doc.removeObject(old.Name)
        ob = doc.addObject("Part::Feature", "P" + nm.split(" ")[0])
        ob.Label, ob.Shape = nm, Part.makeCompound(lst)
        out.append((ob, col))
    doc.recompute()
    print("체결 보강:", "; ".join(notes))
    return out
