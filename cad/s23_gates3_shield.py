# -*- coding: utf-8 -*-
"""빛 게이트 3쌍 + 전원 12 V 하나 + 센서 쉴드 (서현 11/17 04~05시 결정, CAP-AI-62) — design/2026-11-17_전원_12V하나_센서쉴드_서현.md
S2: G1(114 송·수신, 받침 199d·199e, 나사 199s)·G6(196_gate_G6, 받침 199c) 지움, 153b 라벨 M2.5 × 6 → × 5 (P2xy도), 211 기둥 라벨
S3: 허브 193g·193v (부품·선·J_I2C·기둥·스페이서·나사) 지움, 판 DC 잭 194j·판 퓨즈홀더 194f 지움, 와고 받침 193h·볼트 193s 지움 → 와고는 폼 테이프로 z −1,
    UNO 2를 UNO 1 위에서 데크 (x −45~30, y 35~88)로 (쉴드 위 점퍼 높이 때문), 기둥 '사이 15' 3 → UNO 2 밑 5 mm 3, 데크에 Ø3.4 구멍 3 + DXF 다시,
    새 부품 (판매처 치수 모름 → [추측] 상자): 센서 쉴드 V5 2 (193k), XL4015 2 (193x), 잭 변환 SZH-LC002 (194c), 퓨즈홀더 FHAM1 (194u)
한 번만 — 다시는 split/S2·S3·P2xy *_before_g3.FCStd에서. GUI FreeCAD에서 exec 가능 (os._exit 없음) → split/_gates3_shield.json"""
import json, os, sys, shutil, traceback, glob, time, math
import FreeCAD as App, Part
HERE = r"C:\capstone\-capstone-project-repo\cad"; OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
DESK = r"C:\Users\Seohyun_Lee\Desktop\capstone design\주문제작 파일\레이저_데크위판"
V = App.Vector
rep = dict(removed=[], added=[])


def _save(doc, path):                               # 저장 잠김이면 임시 파일을 바꿔 넣음 (fix_screw_clash와 같음)
    try:
        doc.save(); return
    except OSError:
        pass
    tmp = sorted(glob.glob(path + ".*-*"), key=os.path.getmtime)[-1]
    for _ in range(60):
        try:
            os.replace(tmp, path); return
        except OSError:
            time.sleep(2)
    raise OSError("replace failed " + tmp)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def dxf_from_shape(sh, path):                       # _buyfix1115.py와 같은 방식 (판 가운데를 잘라 선·원·호)
    bb = sh.BoundBox; ws = sh.slice(V(0, 0, 1), (bb.ZMin + bb.ZMax) / 2); e = []; nh = 0
    for w in ws:
        for ed in w.Edges:
            c = ed.Curve
            if "Circle" in type(c).__name__:
                cc, r = c.Center, c.Radius
                if ed.isClosed():
                    e.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (cc.x - bb.XMin, cc.y - bb.YMin, r)); nh += 1
                else:
                    a0 = math.degrees(math.atan2(ed.Vertexes[0].Point.y - cc.y, ed.Vertexes[0].Point.x - cc.x))
                    a1 = math.degrees(math.atan2(ed.Vertexes[-1].Point.y - cc.y, ed.Vertexes[-1].Point.x - cc.x))
                    if c.Axis.z < 0: a0, a1 = a1, a0
                    e.append("0\nARC\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f\n50\n%.3f\n51\n%.3f" % (cc.x - bb.XMin, cc.y - bb.YMin, r, a0, a1))
            else:
                pts = [ed.Vertexes[0].Point, ed.Vertexes[-1].Point] if "Line" in type(c).__name__ else ed.discretize(Deflection=0.02)
                for p, q in zip(pts[:-1], pts[1:]):
                    e.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (p.x - bb.XMin, p.y - bb.YMin, q.x - bb.XMin, q.y - bb.YMin))
    open(path, "w", encoding="ascii").write("0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(e) + "\n0\nENDSEC\n0\nEOF\n")
    return dict(size=[round(bb.XLength, 1), round(bb.YLength, 1)], entities=len(e), circles=nh)


try:
    for f in ("S2_마킹부", "S3_프레임회로", "P2xy_XY플랫폼"):
        P, B = os.path.join(OUT, f + ".FCStd"), os.path.join(OUT, f + "_before_g3.FCStd")
        shutil.copy(B, P) if os.path.exists(B) else shutil.copy(P, B)

    def drop(d, pres):
        for o in [o for o in d.Objects if o.Label.startswith(pres)]:
            rep["removed"].append(d.Name[:3] + " " + o.Label[:50]); d.removeObject(o.Name)

    def relabel(d, pre, old, new):
        for o in d.Objects:
            if o.Label.startswith(pre) and old in o.Label:
                o.Label = o.Label.replace(old, new)
    # ---------- S2 · P2xy ----------
    for f in ("S2_마킹부", "P2xy_XY플랫폼"):
        d = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        if f.startswith("S2"):
            drop(d, ("114_entry_sensor", "196_gate_G6", "199c_gate_holder", "199d_gate_holder", "199e_gate_holder", "199s_gate_screws"))
        relabel(d, "153b_stepper_bolts", "M2.5 × 6 냄비머리 4", "M2.5 × 5 냄비머리 4 (11/17 디바이스마트 낱개는 × 5 — 그림 길이 6)")
        for o in d.Objects:
            if o.Label.startswith("211_") and "40" in o.Label and ("기둥" in o.Label or "standoff" in o.Label):
                o.Label = o.Label + " — 11/17 국내: 금속 M-15 + F-25 이어서 40 (디바이스마트)"
                rep["added"].append("relabel " + o.Label[:60])
        d.recompute(); _save(d, os.path.join(OUT, f + ".FCStd")); App.closeDocument(d.Name)
    # ---------- S3 ----------
    d = App.openDocument(os.path.join(OUT, "S3_프레임회로.FCStd"), True)
    ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]
    hubs = [(-127.5, -56.5, -14.5, 16.5), (-30.5, 30.5, 45.5, 86.5)]           # 게이트 허브 · 서보 허브 자리 (xy)
    inhub = lambda s: any(a <= s.BoundBox.Center.x <= b and c <= s.BoundBox.Center.y <= e for a, b, c, e in hubs)
    for p in ("198s_board_screws", "198n_board_spacers"):
        o = ob(p)[0]; keep = [s for s in o.Shape.Solids if not inhub(s)]
        rep["removed"].append("%s 일부 %d개" % (p, len(o.Shape.Solids) - len(keep))); o.Shape = Part.makeCompound(keep)
    ob("198s_board_screws")[0].Label = "198s_board_screws (십자 냄비머리 — MOSFET 모듈 위 4 · 아래 2 · 긴 나사 2, 11/17 허브 몫 지움)"
    ob("198n_board_spacers")[0].Label = "198n_board_spacers (나일론 스페이서 2 — MOSFET 모듈 −y 쪽, 11/17 서보 허브 몫 지움)"
    drop(d, ("193g_gate_hub", "193v_servo_hub", "193j_J_I2C", "198h_hub_standoff", "194j_dc_jack_panel", "194f_panel_fuse_holder",
             "193h_wago_holder", "193s_bolt_M3x10_wago"))
    for p in ("193w_wago_221", "193w_wago_levers"):
        o = ob(p)[0]; s = o.Shape.copy(); s.translate(V(0, 0, -1)); o.Shape = s
    ob("193w_wago_221")[0].Label = "193w_wago_221-415 × 5 (12 V 1 · GND 2 · 5 V 1 + 예비 1 — 11/17 받침 없이 폼 테이프 1 mm로 데크에, 판매품 29.9 × 18.6 × 8.3)"
    # UNO 2: UNO 1 위 (z 226.6) → 데크 (z 210), x −131.3 → −45, y −75 → 35
    u1 = ob("191_arduino_uno")[0]; u2 = ob("192_arduino_uno2")[0]
    pcb = [s for s in u1.Shape.Solids if abs(s.BoundBox.XLength - 68.6) < 0.5 and abs(s.BoundBox.YLength - 53.3) < 0.5][0].BoundBox
    D2 = V(-45.0 - u1.Shape.BoundBox.XMin, 35.0 - u1.Shape.BoundBox.YMin, 0)
    s = u2.Shape.copy(); s.translate(V(D2.x, D2.y, u1.Shape.BoundBox.ZMin - u2.Shape.BoundBox.ZMin)); u2.Shape = s
    u2.Label = "192_arduino_uno2 (실제 모양 — 11/17 데크 위 x −45~30, y 35~88로 옮김: 센서 쉴드 위 점퍼 때문에 UNO 1 위에 못 겹침)"
    st = ob("198u_uno_standoff")[0]; low = [x for x in st.Shape.Solids if x.BoundBox.ZMax < 210.5]
    new = [x.copy() for x in low]
    for x in new: x.translate(D2)
    st.Shape = Part.makeCompound(low + new)
    st.Label = "198u_uno_standoff (M3 기둥 5 mm × 6 — UNO 1·2 밑 각 3, 키트 C. 11/17 사이 15 없앰)"
    # 데크 구멍 3 (UNO 1 기둥 구멍과 같은 지름)
    dk = ob("101_deck")[0]; dsh = dk.Shape
    rr = []
    for x in low:
        c = x.BoundBox.Center
        for e in dsh.Edges:
            if "Circle" in type(e.Curve).__name__ and abs(e.Curve.Center.x - c.x) < 0.3 and abs(e.Curve.Center.y - c.y) < 0.3:
                rr.append(e.Curve.Radius)
    r_hole = min(rr) if rr else 1.7
    for x in new:
        c = x.BoundBox.Center
        dsh = dsh.cut(Part.makeCylinder(r_hole, 20, V(c.x, c.y, 195)))
    dk.Shape = dsh.removeSplitter()
    rep["deck_hole_r"] = round(r_hole, 2); rep["deck_new_holes"] = [[round(x.BoundBox.Center.x, 1), round(x.BoundBox.Center.y, 1)] for x in new]
    # 센서 쉴드 V5 [추측 57 × 53 — 받으면 확인]: UNO 머리핀 위에 꽂음 (USB 반대쪽 끝에 맞춤)
    zs = max(x.BoundBox.ZMax for x in u1.Shape.Solids if abs(x.BoundBox.ZLength - 10.1) < 0.6)   # 암 머리핀 위
    def shield(dx, dy):
        x1 = pcb.XMax + dx; x0 = x1 - 57.0; y0 = pcb.YMin + dy; y1 = y0 + 53.3
        z0 = zs + 1.0
        parts = [box(x0, x1, y0, y1, z0, z0 + 1.6),                                   # 기판
                 box(x0 + 3, x1 - 2, y1 - 8.1, y1 - 0.5, z0 + 1.6, z0 + 10.1),       # 디지털 3핀 줄 (G·V·S)
                 box(x1 - 35, x1 - 2, y0 + 0.5, y0 + 8.1, z0 + 1.6, z0 + 10.1),      # 아날로그 3핀 줄
                 box(x0 + 2, x0 + 12, y0 + 14, y0 + 24, z0 + 1.6, z0 + 11.6)]        # 외부 전원 나사 단자
        jump = [box(x0 + 3, x1 - 2, y1 - 8.1, y1 - 0.5, z0 + 10.1, z0 + 24.1),       # 꽂힌 점퍼 자리 (듀폰 14)
                box(x1 - 35, x1 - 2, y0 + 0.5, y0 + 8.1, z0 + 10.1, z0 + 24.1)]
        return Part.makeCompound(parts), Part.makeCompound(jump)
    def add(name, label, shape, color):
        o = d.addObject("Part::Feature", name); o.Shape = shape; o.Label = label
        if App.GuiUp and getattr(o, "ViewObject", None):
            o.ViewObject.ShapeColor = color
        rep["added"].append(label[:50]); return o
    for k, (dx, dy) in enumerate(((0, 0), (D2.x, D2.y)), 1):
        sh, jp = shield(dx, dy)
        add("SH%d" % k, "193k_sensor_shield_UNO%d (아두이노 센서 쉴드 V5.0 SZH-EK049 — 57 × 53 [추측 — 받고 확인], 서보·게이트·스위치 3핀, 외부 5 V 나사 단자, 구매)" % k, sh, (0.1, 0.35, 0.1))
        add("SJ%d" % k, "193kj_shield_jumpers_UNO%d (꽂힌 듀폰 점퍼 자리 — 높이 14, 선은 위로)" % k, jp, (0.2, 0.2, 0.2))
    # XL4015 표시형 2 [추측 66 × 36 × 20], 잭 변환 SZH-LC002 [추측 33 × 14 × 13], FHAM1 [추측 38 × 14 × 10] — 모두 폼 테이프 1 mm로 데크에
    add("XL1", "193x_xl4015_5V (강압 ① 12 → 5.0 V = +5V_B, 전압 표시 SZH-PWSDF-036 — 66 × 36 × 20 [추측], 폼 테이프, 구매)", box(-127.0, -61.0, -19.0, 17.0, 206.0, 226.0), (0.1, 0.2, 0.6))
    add("XL2", "193x_xl4015_7V4 (강압 ② 12 → 7.4 V mightyZAP, 전압 표시 SZH-PWSDF-036 — 66 × 36 × 20 [추측], 폼 테이프, 구매)", box(32.0, 98.0, 52.0, 88.0, 206.0, 226.0), (0.1, 0.2, 0.6))
    add("JK1", "194c_dc_jack_terminal (SZH-LC002 DC 2.1 암 → 나사 단자 — 12 V 5 A 어댑터 꽂음, 33 × 14 × 13 [추측], 폼 테이프, 구매)", box(50.0, 83.0, -86.0, -72.0, 206.0, 219.0), (0.15, 0.15, 0.15))
    add("FU1", "194u_fuse_holder_FHAM1 (자동차 블레이드 퓨즈 5 A 홀더 — 12 V 줄, 38 × 14 × 10 [추측], 폼 테이프, 구매)", box(50.0, 88.0, -66.0, -52.0, 206.0, 216.0), (0.8, 0.1, 0.1))
    d.recompute(); _save(d, os.path.join(OUT, "S3_프레임회로.FCStd"))
    # 데크 DXF (바탕화면 + 레포)
    info = dxf_from_shape(dk.Shape, os.path.join(HERE, "print", "laser", "101_deck_레이저_5T.dxf"))
    try:
        shutil.copy(os.path.join(HERE, "print", "laser", "101_deck_레이저_5T.dxf"), os.path.join(DESK, "101_deck_레이저_5T.dxf"))
    except Exception as ex:
        info["desk"] = str(ex)
    rep["deck_dxf"] = info
    # 정지 겹침: 새·옮긴 것 ↔ 전부 (S1·S2·S2a·S3)
    every = []
    for f in ("S1_급이부", "S2_마킹부", "S2a_바닥구동"):
        dd = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        every += [(f[:3] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    every += [("S3 " + o.Label, o.Shape.copy()) for o in d.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith(("REF", "190_"))]
    CH = ("192_", "193k", "193x", "194c", "194u", "198u", "193w")
    ok = (("192_", "198u"), ("193k", "191_"), ("193k", "192_"), ("193kj", "193k"), ("198u", "101_deck"), ("198u", "191_"), ("193w_wago_221", "193w_wago_lev"))
    hits = []
    for la, sa in every:
        ta = la.split(" ", 1)[1]
        if not ta.startswith(CH):
            continue
        for lb, sb in every:
            tb = lb.split(" ", 1)[1]
            if la == lb or (tb.startswith(CH) and lb < la):
                continue
            if any(ta.startswith(p) and tb.startswith(q) or ta.startswith(q) and tb.startswith(p) for p, q in ok):
                continue
            try:
                if sa.BoundBox.intersect(sb.BoundBox):
                    v = sa.common(sb).Volume
                    if v > 0.05:
                        hits.append([ta[:40], tb[:40], round(v, 1)])
            except Exception:
                pass
    rep["hits"] = hits
    App.closeDocument(d.Name)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_gates3_shield.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False)[:3000])
