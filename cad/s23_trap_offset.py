# -*- coding: utf-8 -*-
"""트랩 아래(포획기)·위(포획통)를 관 축으로 옮기고 깔때기는 곧게 (서현 11/17 10:59 "격리실·포획실 위치를 옮기면 깔때기를 이상하게 안 만들어도 … 움직일 거야", CAP-AI-62)
s2_ducts_vertical.py 다음에 (관 110 (0, 9) · 172 (1.5, −9) 수직, 하우징 꺾임 수직은 그대로 씀).
  아래: REF 트랩 몸·미끼컵·깔때기·차양막·링 + 칼라 102 + 칼라 볼트 100m을 y +9, 데크 가운데 구멍 Ø55 + 칼라 구멍 4를 y +9
        깔때기 111 = 옛 곧은 콘을 y +9 (넓은 끝이 데크 구멍과 같은 축)
        UNO 2 (+ 쉴드·점퍼·기둥 3·데크 구멍 3)를 y +2 — 옮긴 111 아래 끝이 UNO 2 기판 밑에 닿지 않게
  위:   REF 포획통·뚜껑·실리콘 별 + 돔 연결부 104를 y −9, 위판 가운데 구멍 Ø55를 y −9, 깔때기 173 = 곧은 콘 (1.5, −9)
한 번만 — 다시는 split/S2·S3 *_before_trap.FCStd에서. GUI FreeCAD에서 exec 가능 (os._exit 없음) → split/_trap_offset.json"""
import json, os, sys, shutil, traceback, glob, time, math
import FreeCAD as App, Part
HERE = r"C:\capstone\-capstone-project-repo\cad"; OUT = os.path.join(HERE, "split")
DESK = r"C:\Users\Seohyun_Lee\Desktop\capstone design\주문제작 파일"
V = App.Vector
DN, UP, DU = V(0, 9.0, 0), V(0, -9.0, 0), V(0, 2.0, 0)
rep = dict(moved=[])


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


def cyl(r, h, p, d=V(0, 0, 1)):
    return Part.makeCylinder(r, h, p, d)


def mv(o, v):
    s = o.Shape.copy(); s.translate(v); o.Shape = s; rep["moved"].append(o.Label[:40])


def rehole(sh, z0, z1, holes):                      # holes: [(r, 옛 (x, y), 새 (x, y))] — 옛 구멍 메우고 새로 뚫음
    for r, a, b in holes:
        sh = sh.fuse(cyl(r + 1.0, z1 - z0, V(a[0], a[1], z0)))      # r + 0.01이면 옛 구멍 벽 0.01 띠가 남아 DXF에 작은 호가 생김
    for r, a, b in holes:
        sh = sh.cut(cyl(r, z1 - z0 + 2, V(b[0], b[1], z0 - 1)))
    return sh.removeSplitter()


def dxf_from_shape(sh, path):                       # s23_gates3_shield.py와 같음 (판 가운데를 잘라 선·원·호)
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
    for f in ("S2_마킹부", "S3_프레임회로"):
        P, B = os.path.join(OUT, f + ".FCStd"), os.path.join(OUT, f + "_before_trap.FCStd")
        shutil.copy(B, P) if os.path.exists(B) else shutil.copy(P, B)
    # ---------- S2: 깔때기 곧게, 돔 연결부 ----------
    old = App.openDocument(os.path.join(OUT, "S2_마킹부_before_vert.FCStd"), True)
    cone0 = [o for o in old.Objects if o.Label.startswith("111_entry_funnel")][0].Shape.common(Part.makeBox(80, 80, 36.2, V(-40, -40, 200)))
    App.closeDocument(old.Name)
    d = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"), True)
    ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)][0]
    cone = cone0.copy(); cone.translate(DN)                  # 옛 곧은 콘 (s2_gates_funnels_feed) 그대로 y +9
    E = V(0, 9.0, 248.5)
    b = cone.fuse(cyl(11, E.z + 1.5 - 236.2, V(E.x, E.y, 236.2))).fuse(cyl(11, 11, V(E.x, E.y, E.z - 0.5)))
    f = ob("111_entry_funnel")
    f.Shape = b.cut(cyl(7, 30, V(E.x, E.y, 230))).cut(cyl(9.15, 20, E)).removeSplitter()
    f.Label = f.Label.split(" (11/17")[0] + " (11/17 곧은 깔때기, 트랩·데크 구멍과 같이 y +9 — 관 110 수직 축)"
    E = V(1.5, -9.0, 584.4)
    circ = lambda r, c: Part.Wire(Part.makeCircle(r, c))
    outer = Part.makeLoft([circ(11.0, V(E.x, E.y, 596.2)), circ(25.9, V(E.x, E.y, 620.0))], True)     # 넓은 끝 Ø52, 두께 1.5 (옛 모양과 같은 치수)
    inner = Part.makeLoft([circ(9.5, V(E.x, E.y, 596.2)), circ(24.4 + 0.05 * 14.9 / 23.8, V(E.x, E.y, 620.05))], True)
    b = outer.cut(inner).fuse(cyl(11, 596.2 - (E.z + 0.5), V(E.x, E.y, E.z + 0.5))).fuse(cyl(11, 11, V(E.x, E.y, E.z + 0.5), V(0, 0, -1)))
    b = b.cut(cyl(7, 22, V(E.x, E.y, 575))).cut(cyl(9.15, 20, E, V(0, 0, -1)))
    f = ob("173_isolation_funnel")
    f.Shape = b.cut(Part.makeBox(60, 60, 15.5, V(-28, -30, 560))).removeSplitter()
    f.Label = f.Label.split(" (11/17")[0] + " (11/17 곧은 깔때기, 포획통·위판 구멍과 같이 y −9 — 관 172 수직 축)"
    mv(ob("104_dome_coupling"), UP)
    for p in ("111_entry_funnel", "173_isolation_funnel"):
        rep[p[:3] + "_valid"] = [ob(p).Shape.isValid(), len(ob(p).Shape.Solids)]
    d.recompute(); _save(d, os.path.join(OUT, "S2_마킹부.FCStd"))
    import MeshPart
    for p, nm in (("111_entry_funnel", "111_입구깔때기"), ("173_isolation_funnel", "173_격리깔때기")):
        m = MeshPart.meshFromShape(Shape=ob(p).Shape, LinearDeflection=0.05, AngularDeflection=0.3)
        fn = os.path.join(HERE, "print", "3d", nm + ".stl"); m.write(fn)
        shutil.copy(fn, os.path.join(DESK, "프린트_5개_최종", nm + ".stl"))
        rep["stl_" + nm] = dict(solid=m.isSolid(), vol_cm3=round(ob(p).Shape.Volume / 1000, 2))
    # ---------- S3: 트랩 위·아래, 데크·위판 구멍, UNO 2 ----------
    s3 = App.openDocument(os.path.join(OUT, "S3_프레임회로.FCStd"), True)
    o3 = lambda p: [o for o in s3.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]
    for p in ("REF_trap_bait_cup", "REF_trap_body", "REF_trap_funnels", "REF_trap_awning", "REF_trap_ring", "102_collar", "100m_bolt_M3x10_deck"):
        for o in o3(p):
            mv(o, DN)
    for p in ("REF_trap_container", "REF_trap_cap", "REF_trap_silicone_star"):
        for o in o3(p):
            mv(o, UP)
    for p in ("192_arduino_uno2", "193k_sensor_shield_UNO2", "193kj_shield_jumpers_UNO2"):
        for o in o3(p):
            mv(o, DU)
    st = o3("198u_uno_standoff")[0]
    u2st = [x for x in st.Shape.Solids if x.BoundBox.Center.y > 0]
    keep = [x.copy() for x in st.Shape.Solids if x.BoundBox.Center.y <= 0]
    new = [x.copy() for x in u2st]
    for x in new:
        x.translate(DU)
    st.Shape = Part.makeCompound(keep + new)
    dk = o3("101_deck")[0]
    holes = [(27.5, (0, 0), (0, 9))] + [(1.7, (sx * 45.5, sy * 26.2), (sx * 45.5, sy * 26.2 + 9)) for sx in (-1, 1) for sy in (-1, 1)]
    holes += [(1.7, (round(x.BoundBox.Center.x, 2), round(x.BoundBox.Center.y, 2)), (round(x.BoundBox.Center.x, 2), round(x.BoundBox.Center.y + 2, 2))) for x in u2st]
    dk.Shape = rehole(dk.Shape, 200.0, 205.0, holes)
    for x, y in ((-121.5, 83.3), (-61.7, 83.3)):                # (11/17 11:10 발견) MOSFET 긴 나사 2가 데크에 구멍 없이 그려져 있었음 → Ø3.4 관통 + 아래 너트
        dk.Shape = dk.Shape.cut(cyl(1.7, 7, V(x, y, 199)))
    sc = o3("198s_board_screws")[0]
    sc.Label = sc.Label.replace(", 11/17 허브 몫 지움)", ", 11/17 허브 몫 지움 · 긴 나사 2는 데크 Ø3.4 관통 + 아래 M3 너트 = M3 × 16, 키트 A)")
    tp = o3("105_top_plate")[0]
    tp.Shape = rehole(tp.Shape, 610.0, 615.0, [(27.5, (0, 0), (0, -9))])
    rep["deck_holes"] = holes
    s3.recompute(); _save(s3, os.path.join(OUT, "S3_프레임회로.FCStd"))
    for o, nm, sub in ((dk, "101_deck_레이저_5T", "레이저_데크위판"), (tp, "105_top_plate_레이저_5T", "레이저_데크위판")):
        fn = os.path.join(HERE, "print", "laser", nm + ".dxf")
        rep["dxf_" + nm] = dxf_from_shape(o.Shape, fn)
        shutil.copy(fn, os.path.join(DESK, sub, nm + ".dxf"))
    # ---------- 정지 겹침: 옮긴·바뀐 것 ↔ 전부 ----------
    every = []
    for ff in ("S1_급이부", "S2a_바닥구동"):
        dd = App.openDocument(os.path.join(OUT, ff + ".FCStd"), True)
        every += [(ff[:3] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull()]
        App.closeDocument(dd.Name)
    every += [("S2_ " + o.Label, o.Shape.copy()) for o in d.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull()]
    every += [("S3_ " + o.Label, o.Shape.copy()) for o in s3.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("190_")]
    CH = ("REF_trap", "102_collar", "100m_bolt", "104_dome", "111_entry_funnel", "173_isolation_funnel", "192_arduino_uno2", "193k_sensor_shield_UNO2",
          "193kj_shield_jumpers_UNO2", "198u", "101_deck", "105_top_plate")
    ok = (("REF_trap", "REF_trap"), ("102_collar", "REF_trap_ring"), ("102_collar", "100m"), ("100m", "101_deck"), ("104_dome", "REF_trap"), ("104_dome", "105_top"),
          ("111_entry", "110_entry"), ("173_iso", "172_iso"), ("192_", "198u"), ("193k", "192_"), ("193kj", "193k"), ("198u", "101_deck"), ("101_deck", "100"),
          ("105_top", "100"), ("101_deck", "102_collar"), ("101_deck", "198s"), ("111_entry", "101_deck"), ("REF_trap_awning", "100"), ("193w", "101_deck"))
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
    App.closeDocument(d.Name); App.closeDocument(s3.Name)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_trap_offset.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False)[:3000])
