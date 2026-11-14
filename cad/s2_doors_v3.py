# -*- coding: utf-8 -*-
"""전체 수정 2단계: 새 마킹실(lift_v3)에 맞춰 S2 문 3개·통로·마커 대기 자리를 옮김 (서현 11/14 20:07 "하던거 해", CAP-AI-62)
  freecad.exe cad/s2_doors_v3.py (cwd = cad) → split/S2_마킹부_v3.FCStd + split/_doors_v3.json + img/parts/lift/S2v3d_*.png
결정 (서현 11/14): 입구 −x · 방생 +x · 격리 −y · 급이 +y, 마커 대기 PARK (65, −40) → (95, −40)
S2(체인 결과)를 다시 만들지 않고 고쳐 씀 (s2_lift.py와 같은 방식). 옮긴 묶음은 모양 그대로 Placement만 바꿈:
  입구 (112·G2): y 거울 (서보 −y → +y) + z +27.5 (축 349 → 376.5). 110b 꺾임 +27.5, 110 PVC 위 끝 336 → 363.5
  격리 (170·G3): (x−55, y) → (y, x−55) 거울 (−x 벽 → −y 벽, 서보는 −x 쪽) + z −0.5. 옛 172·172b 통로 빼고 새 길:
      −y 문 → PVC −y → 꺾임(−y→+z) → PVC 세로 (55, −135) → 꺾임(+z→가운데 쪽) → PVC 가로 z 557 (갠트리·마커 위) → 꺾임(→+z) → PVC → 깔때기 173
  방생 (176·G5): y 거울 (서보 +y 쪽 — 대기 컵 자리 비움). 목 174·굴뚝 175·G6 그대로 (축 377 ≈ 376.5)
  마커 (빔과 같이 x로 움직이는 것 + 컵 219): x +30. 고정(X 봉·X 리드·X 모터·X 원점)은 그대로. 컵 받침 220 새로 (방생 하우징 −y 면에 붙음)
"""
import json, os, sys, math, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "split")
REPLACED = ("120_", "121_", "130_", "140_", "146_", "147_", "148", "149_", "151", "152_", "153m", "153s", "154_", "155", "157", "158_", "159",
            "227f", "227p", "REF_hornet", "REF_mark_dot", "172_isolation_duct", "172b_isolation_bend", "220_cup_bracket")
DPARK = 10.0                                   # (11/14 1차 검사) +30이면 빔 끝 블록·X 너트가 X 커플링(216)에, 캐리지가 방생 굴뚝(175)에 닿음 → +10
MARKER = ("201_", "202_", "203_", "204_", "205", "206_", "207_", "208_", "209", "210_", "211_", "212_", "219_", "221_", "222_", "223_",
          "224_", "225_", "227y")
rep = dict(ok=False)
try:
    import FreeCAD as App
    import Part
    import lift_v3 as L3
    import D5e_module_kinematic as K
    V = App.Vector

    def mat(rows):
        m = App.Matrix()
        (m.A11, m.A12, m.A13, m.A14), (m.A21, m.A22, m.A23, m.A24), (m.A31, m.A32, m.A33, m.A34) = rows
        return m
    M_ENTRY = mat(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, 1, 27.5)))
    M_ISO = mat(((0, 1, 0, 55), (1, 0, 0, -55), (0, 0, 1, -0.5)))
    M_REL = mat(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, 1, 0)))
    M_PARK = mat(((1, 0, 0, DPARK), (0, 1, 0, 0), (0, 0, 1, 0)))
    M_UP = mat(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 27.5)))

    src = os.path.join(OUT, "S2_마킹부_before_v3.FCStd")              # 한 번 바꾼 뒤에는 옛 S2(백업)에서 다시 시작 — 두 번 옮기지 않게
    d = App.openDocument(src if os.path.exists(src) else os.path.join(OUT, "S2_마킹부.FCStd"))
    key = lambda o: o.Label.split(" ")[0]
    group = {}                                                      # 이름 → 묶음

    def put(o, shp, g, label=None):
        o.Shape = shp
        group[o.Name] = g
        if label:
            o.Label = label

    def tr(o, m, g):
        put(o, o.Shape.transformed(m), g)

    def split(o, rule):
        """여러 덩어리 compound를 규칙(덩어리 → (행렬, 묶음))으로 나눠 새 물체로"""
        parts = {}
        for s in o.Shape.Solids:
            m, g = rule(s.BoundBox)
            parts.setdefault(g, (m, []))[1].append(s)
        for g, (m, ss) in parts.items():
            n = d.addObject("Part::Feature", o.Name + "_" + g)
            sh = Part.makeCompound(ss)
            n.Shape = sh.transformed(m) if m else sh
            n.Label = o.Label + " [%s]" % g
            group[n.Name] = g
        d.removeObject(o.Name)

    I = App.Matrix()
    for o in list(d.Objects):
        if not o.TypeId.startswith("Part::"):
            continue
        k = key(o)
        if k.startswith(REPLACED):
            d.removeObject(o.Name)
        elif k.startswith("112_entry_gate"):
            tr(o, M_ENTRY, "entry")
        elif k.startswith("196_gate_G2"):
            tr(o, M_UP, "entry")                                     # 센서는 거울 안 함 (다리가 +y로 굽어 꺾임 조각을 비킴)
        elif k.startswith(("170_isolation_gate", "196_gate_G3")):
            tr(o, M_ISO, "iso")
        elif k.startswith(("176_release_gate", "196_gate_G5")):
            tr(o, M_REL, "rel")
        elif k.startswith("110b"):
            tr(o, M_UP, "entry_duct")
        elif k.startswith("110_entry_duct"):
            od, idd = 18.0, 13.0
            t = K.tube(od / 2, idd / 2, 363.5 - 247.4, V(0, 0, 247.4)).cut(K.cyl(1.6, 30, V(-15, 0, 275.0), V(1, 0, 0)))
            put(o, t, "entry_duct", o.Label.replace("89 mm", "%d mm" % round(363.5 - 247.4)))
        elif k.startswith("112s_gate_servo_screws"):
            split(o, lambda b: (M_REL, "rel") if b.Center.x > 50 else ((M_ISO, "iso") if b.Center.z > 365 else (M_ENTRY, "entry")))
        elif k.startswith(("196_gate_G4", "199b_gate_holder_G4")):
            tr(o, mat(((1, 0, 0, 53.5), (0, 1, 0, -135), (0, 0, 1, -35))), "iso_duct")
        elif k.startswith("199s_gate_screws"):
            split(o, lambda b: (mat(((1, 0, 0, 53.5), (0, 1, 0, -135), (0, 0, 1, -35))), "iso_duct") if b.Center.z > 540 else (None, "fixed"))
        elif k.startswith(("153b_", "153n_")):
            split(o, lambda b: (M_PARK, "marker") if b.Center.x < 125 else (None, "fixed"))
        elif k.startswith(MARKER):
            tr(o, M_PARK, "marker")
        else:
            group[o.Name] = "fixed"

    # 방생 하우징 (+y로 뒤집음) 먼 모서리를 급이 노즐 니플·관(S1) 자리만큼 깎음
    for o in d.Objects:
        if group.get(o.Name) == "rel" and key(o).startswith("176_release_gate_housing"):
            o.Shape = o.Shape.cut(K.box(73.9, 90.0, 41.0, 46.0, 355.0, 395.0))
            o.Label = o.Label + " [11/14: +y로 뒤집음, 먼 모서리 x 74~90·y 41~ 깎음 — 급이 니플·관]"
    # 새 마킹실 + 리프트 v3
    v = App.newDocument("_v3tmp")
    L3.make(v)
    mw = App.Matrix()
    mw.move(L3.WORLD)
    for o in v.Objects:
        n = d.addObject("Part::Feature", "V3_" + o.Name)
        n.Shape, n.Label = o.Shape.transformed(mw), o.Label
        group[n.Name] = "v3"
    App.closeDocument(v.Name)

    # 컵 받침 220: 컵 아래 → 방생 하우징 −y 면 (y −10)
    cx_cup, cy_cup = K.PARK[0] + DPARK, K.PARK[1]
    n = d.addObject("Part::Feature", "CupBracket")
    n.Shape = K.box(74.5, cx_cup + 7, cy_cup - 8, -10.2, 375.0, 380.0)            # 상자(x ~74) 밖만 — 컵 반쪽을 받침
    n.Label = "220_cup_bracket (11/14: 대기 (95, −40) 컵 받침 — 방생 문 하우징 −y 면에 M2 셀프 탭 2, 작은 3D 프린트)"
    group[n.Name] = "marker_fixed"

    # 격리 새 통로
    hs = [o for o in d.Objects if group.get(o.Name) == "iso" and key(o).startswith("170_isolation_gate_housing")][0].Shape.BoundBox
    yf, z0 = hs.YMin, 376.5
    R, ro, ri = 12.0, 9.0, 6.5
    sock = lambda p, dirv: K.tube(11.0, 9.2, 12.0, p, dirv)

    def pvc(p0, p1):
        dv = p1 - p0
        return K.tube(ro, ri, dv.Length, p0, dv.normalize())

    def elbow(p0, t0, t1):
        t0, t1 = V(t0).normalize(), V(t1).normalize()
        c = p0 + t1 * R
        ang = math.degrees(t0.getAngle(t1))
        body = K.bend(ro, p0, t0, c, ang).cut(K.bend(ri, p0, t0, c, ang))
        p1 = c - t1 * R + t0 * 0                                 # 중심에서 끝 단면까지
        p1 = c + (p0 - c) * math.cos(math.radians(ang)) + t0 * R * math.sin(math.radians(ang))
        return body, p1
    yB = -123.0                                                  # (11/14 움직임 검사) −83이면 세로관(y −95)이 X로 움직이는 Y 모터·커플링·브래킷(y −123~−74)에 닿음 → 세로관 y −135
    A, B = V(55, yf, z0), V(55, yB, z0)
    e1, C = elbow(B, V(0, -1, 0), V(0, 0, 1))
    Zt = 545.0
    D_ = V(C.x, C.y, Zt)
    XT = 1.5                                                      # 깔때기 쪽 세로 축 x (옛 172와 같음 — 갠트리 레일 틈)
    h = V(XT - D_.x, -D_.y, 0).normalize()
    e2, E = elbow(D_, V(0, 0, 1), h)
    G = V(XT, 0, E.z + R)
    F = G - h * R - V(0, 0, R)
    e3, G2 = elbow(F, h, V(0, 0, 1))
    duct = [pvc(A, B), pvc(C, D_), pvc(E, F), pvc(G2, V(XT, 0, 585.0))]
    bends = [e1.fuse(sock(B, V(0, 1, 0))), e2, e3]
    n = d.addObject("Part::Feature", "IsoDuct")
    n.Shape = Part.makeCompound(duct)
    lens = [round((A - B).Length), round((C - D_).Length), round((E - F).Length), round((G2 - V(XT, 0, 585)).Length)]
    n.Label = "172_isolation_duct (11/14 새 길 — 수도용 PVC 13A 바깥 18·안 13, %s mm 4토막, 구매)" % "·".join(str(x) for x in lens)
    group[n.Name] = "iso_duct"
    n = d.addObject("Part::Feature", "IsoBends")
    n.Shape = Part.makeCompound(bends)
    n.Label = "172b_isolation_bends (꺾임 조각 3 — R 12·안 13, 작은 3D 프린트)"
    group[n.Name] = "iso_duct"
    rep["iso_path"] = dict(A=list(A), B=list(B), C=list(C), D=list(D_), E=list(E), F=list(F), G=list(G2), lens=lens)

    # 겹침: 바뀐 묶음 ↔ 다른 묶음 (S2 안) + S1·S3
    changed = [o for o in d.Objects if group.get(o.Name, "fixed") != "fixed" and o.TypeId.startswith("Part::")]
    others = [(o.Label, o.Shape, group.get(o.Name, "fixed")) for o in d.Objects if o.TypeId.startswith("Part::")]
    for f in ("S1_급이부", "S3_프레임회로"):
        s = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        for o in s.Objects:
            if o.TypeId.startswith("Part::"):
                try:
                    if not o.Shape.isNull() and o.Shape.Volume > 0:
                        others.append((f[:2] + " " + o.Label, o.Shape.copy(), "ext"))
                except Exception:
                    pass
        App.closeDocument(s.Name)
    hits = []
    for a in changed:
        ga = group[a.Name]
        for lb, sb, gb in others:
            if gb == ga or lb == a.Label or lb.startswith("REF_camera") or a.Label.startswith("REF_camera"):
                continue
            if ga in ("iso_duct",) and gb == "iso":
                pass
            if a.Label.startswith("110_entry_duct") and lb.startswith(("111h_", "199s_")):
                continue
            if a.Label.startswith("196_gate_G2_ir_pair") and lb.startswith("110b") or a.Label.startswith("172_isolation_duct") and lb.startswith("173h"):
                continue                                             # 원래 S2에도 같은 양 (19.9·30.4)                                             # 원래 S2에도 같은 양 (30.4·6.2) — 열수축관·안장 나사
            if not a.Shape.BoundBox.intersect(sb.BoundBox):
                continue
            vv = a.Shape.common(sb).Volume
            if vv > 0.05:
                hits.append((a.Label[:45], ga, lb[:45], gb, round(vv, 1)))
    seen, uniq = set(), []
    for h_ in hits:
        kk = tuple(sorted((h_[0], h_[2])))
        if kk not in seen:
            seen.add(kk)
            uniq.append(h_)
    rep["hits"] = uniq
    if App.GuiUp:                                                    # 색 규칙: 프린트 초록 · 사서 고침/주문 제작 파랑 · 그대로 산 것 회색
        GREEN, BLUE, GRAY, DARK = (0.2, 0.7, 0.3), (0.55, 0.75, 0.95), (0.75, 0.75, 0.77), (0.35, 0.35, 0.37)
        rule = (("300_", GREEN, 50), ("300p", BLUE, 60), ("300s", DARK, 0), ("304s", DARK, 0), ("308s", DARK, 0), ("309s", DARK, 0),
                ("172b_", GREEN, 0), ("220_", GREEN, 0))
        for o in d.Objects:
            if not (o.Name.startswith(("V3_", "IsoDuct", "IsoBends", "CupBracket")) and o.ViewObject):
                continue
            c, t = GRAY, 0
            for pre, cc, tt in rule:
                if key(o).startswith(pre):
                    c, t = cc, tt
                    break
            o.ViewObject.ShapeColor, o.ViewObject.Transparency = c, t
    d.saveAs(os.path.join(OUT, "S2_마킹부_v3.FCStd"))
    if App.GuiUp:
        import FreeCADGui as Gui
        col = dict(entry=(0.9, 0.5, 0.2), iso=(0.6, 0.3, 0.8), rel=(0.2, 0.5, 0.9), iso_duct=(0.6, 0.3, 0.8), entry_duct=(0.9, 0.5, 0.2),
                   v3=(0.2, 0.7, 0.3), marker=(0.95, 0.8, 0.2), marker_fixed=(0.95, 0.8, 0.2))
        for o in d.Objects:
            g = group.get(o.Name, "fixed")
            if hasattr(o, "ViewObject") and o.ViewObject:
                if g in col:
                    o.ViewObject.ShapeColor = col[g]
                    o.ViewObject.Transparency = 0
                elif o.TypeId.startswith("Part::"):
                    o.ViewObject.Transparency = 70
        vw = Gui.getDocument(d.Name).activeView()
        vw.setCameraType("Orthographic")
        img = os.path.join(HERE, "img", "parts", "lift")
        for nm, fn in (("등각", vw.viewIsometric), ("정면", vw.viewFront), ("위", vw.viewTop), ("옆", vw.viewRight)):
            fn(); vw.fitAll()
            vw.saveImage(os.path.join(img, "S2v3d_%s.png" % nm), 1600, 1200, "White")
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
with open(os.path.join(OUT, "_doors_v3.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
