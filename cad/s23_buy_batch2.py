# -*- coding: utf-8 -*-
"""출력 줄이기 2묶음 — 남은 출력 18개를 사는 것·레이저 판으로 (서현 11/15 19:54 "일단 전체 수정해봐", 목표 출력 3개, CAP-AI-62)
남기는 출력 3: 300 마킹실 상자 · 112 입구·격리 문 하우징(+꺾임) · 176 방생 문 하우징
  모양 그대로 판으로 (두께 그대로, 레이저 DXF): 문판 3 (알루미늄 1.5) · 220 컵 받침 (아크릴 5) · 199c G6 받침 (아크릴 2) · 194b 비상 정지 판 (알루미늄 4)
      104 돔 연결부 (아크릴 5 × 2 겹침) · 102 칼라 (아크릴 5 × 3 겹침) · 144b 병 걸이 (알루미늄 4)
  다시 만듦: 197 ULN 받침 X·Y → 알루미늄 3 평판 · 199b·d·e 안장 받침 → 바깥 2 mm 판 (아크릴 2) + 케이블 타이
      226 X 원점 집게 → SK8 (봉에 조임) + 팔 판 (알루미늄 3), 스위치는 팔 위에 바로 (z −7.6)
      181 카메라 걸이 → 판 CB (아크릴 3) + M3 기둥 2 (45 + 8 이어서)
      199a Pi 선반 → 바닥 판 PB (아크릴 3) + 벽 판 PV (알루미늄 3, 위 가로대 −y 면) + 작은 L 브래킷 2
  이름만 사는 것: 219 뚜껑 컵 → 마커 여분 뚜껑, 193h 와고 받침 → WAGO 221-500 고정 캐리어 [가능성 높음]
한 번만 (다시는 split/*_before_b2.FCStd에서). freecad.exe cad/s23_buy_batch2.py (cwd = cad) → split/S1·S2·S3, print/laser/*.dxf, split/_buy_b2.json"""
import json, os, sys, traceback, glob, time, math
HERE = os.getcwd(); OUT = os.path.join(HERE, "split"); LZ = os.path.join(HERE, "print", "laser"); sys.path.insert(0, HERE)
rep = dict(hits=[], dxf={})


def _save(doc, path):
    try:
        doc.save(); App.closeDocument(doc.Name); return
    except OSError:
        pass
    App.closeDocument(doc.Name)
    tmp = sorted(glob.glob(path + ".*-*"), key=os.path.getmtime)[-1]
    for _ in range(60):
        try:
            os.replace(tmp, path); return
        except OSError:
            time.sleep(2)
    raise OSError("replace failed " + tmp)


def dxf(path, solid):
    """가장 큰 평면을 펴서 R12 DXF (축에 나란한 판만). 원점 = 판 왼쪽 아래"""
    f = max([x for x in solid.Faces if x.Surface.TypeId == "Part::GeomPlane"], key=lambda x: x.Area)
    n = f.normalAt(0, 0); b = solid.BoundBox
    if abs(n.z) > 0.9:
        uv = lambda p: (p.x - b.XMin, p.y - b.YMin); wh = (b.XLength, b.YLength)
    elif abs(n.x) > 0.9:
        uv = lambda p: (p.y - b.YMin, p.z - b.ZMin); wh = (b.YLength, b.ZLength)
    else:
        uv = lambda p: (p.x - b.XMin, p.z - b.ZMin); wh = (b.XLength, b.ZLength)
    ents = []
    for e in f.Edges:
        c = e.Curve
        if "Circle" in c.TypeId and e.isClosed():
            cc = uv(c.Center)
            ents.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (cc[0], cc[1], c.Radius))
            continue
        pts = [uv(p) for p in e.discretize(Deflection=0.02)] if "Line" not in c.TypeId else [uv(e.Vertexes[0].Point), uv(e.Vertexes[-1].Point)]
        for a, z in zip(pts[:-1], pts[1:]):
            ents.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (a[0], a[1], z[0], z[1]))
    with open(path, "w", encoding="ascii") as fo:
        fo.write("0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(ents) + "\n0\nENDSEC\n0\nEOF\n")
    return [round(wh[0], 1), round(wh[1], 1)]


try:
    import FreeCAD as App, Part
    import lift_v2 as L
    V = App.Vector
    box, cyl = L.box, L.cyl
    ex, ey, ez = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
    os.makedirs(LZ, exist_ok=True)
    laser = []                                              # (파일 이름, 고체)

    def ob(d, p):
        return [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]

    def relabel(d, p, tail):
        for o in ob(d, p):
            o.Label = o.Label.split(" (")[0] + " (" + tail + ")"
            yield o

    def addp(d, lab, sh):
        n = d.addObject("Part::Feature", "B2_%d" % len(d.Objects)); n.Shape, n.Label = sh, lab; return n

    # ---------------- S1
    s1 = App.openDocument(os.path.join(OUT, "S1_급이부.FCStd"))
    for o in relabel(s1, "144b_feeder_holder", "펌프 걸이 — 알루미늄 4 mm 레이저, 데크 레일에 M5 2"):
        laser.append(("144b_펌프걸이_알루미늄4T", o.Shape.Solids[0]))
    _save(s1, os.path.join(OUT, "S1_급이부.FCStd"))
    # ---------------- S2
    s2 = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    for p, nm in (("112_entry_gate_flap", "112f_입구문판"), ("170_isolation_gate_flap", "170f_격리문판"), ("176_release_gate_flap", "176f_방생문판")):
        for o in relabel(s2, p, "문판 — 알루미늄 1.5 mm 레이저, 서보 혼에 M2"):
            laser.append((nm + "_알루미늄1.5T", o.Shape.Solids[0]))
    for o in relabel(s2, "220_cup_bracket", "컵 받침 — 아크릴 5 mm 레이저, 방생 문 하우징 −y 면에 M2"):
        laser.append(("220_컵받침_아크릴5T", o.Shape.Solids[0]))
    for o in relabel(s2, "199c_gate_holder_G6", "G6 받침 2 — 아크릴 2 mm 레이저, 관 위아래 + 케이블 타이"):
        laser.append(("199c_G6받침_아크릴2T_x2", o.Shape.Solids[0]))
    for o in relabel(s2, "104_dome_coupling", "돔 연결부 — 아크릴 5 mm 레이저 2장 겹침, M3로 함께 조임"):
        laser.append(("104_돔연결부_아크릴5T_x2", o.Shape.Solids[0]))
    list(relabel(s2, "219_cap_cup", "뚜껑 컵 — 마커 여분 뚜껑 (사는 것), 컵 받침 220 구멍에 끼움"))
    for p, nm in (("199b_gate_holder_G4", "199b_G4받침"), ("199d_gate_holder_G1_tx", "199d_G1송신받침"), ("199e_gate_holder_G1_rx", "199e_G1수신받침")):
        for o in ob(s2, p):
            out = []
            for sl in o.Shape.Solids:
                f = max([x for x in sl.Faces if x.Surface.TypeId == "Part::GeomPlane"], key=lambda x: x.Area)
                out.append(f.extrude(f.normalAt(0, 0) * -2.0))
            o.Shape = Part.makeCompound(out) if len(out) > 1 else out[0]
            o.Label = o.Label.split(" (")[0] + " (안장 → 아크릴 2 mm 레이저 판 + 케이블 타이 2로 관에 묶음)"
            laser.append((nm + "_아크릴2T" + ("_x%d" % len(out) if len(out) > 1 else ""), out[0]))
    # 226 X 원점 집게 → SK8 + 팔 판
    for p in ("226_", "226s_"):
        for o in ob(s2, p):
            s2.removeObject(o.Name)
    sw = ob(s2, "227x")
    for o in sw:
        o.Placement.Base = o.Placement.Base + V(0, 0, -7.6)
    scr = [s.BoundBox.Center for o in ob(s2, "227xs") for s in o.Shape.Solids]
    XC, YR, Z0 = 10.0, -70.0, 460.0             # SK8는 스위치(x 29.7~41.9) 옆 — 밑에 두면 스위치·볼트와 겹침
    sk = box(XC - 7, XC + 7, YR - 21, YR + 21, Z0, Z0 + 6).fuse(box(XC - 7, XC + 7, YR - 10.5, YR + 10.5, Z0, Z0 + 32.8))
    sk = sk.cut(cyl(4.0, 16, V(XC - 8, YR, Z0 + 20), ex)).cut(cyl(2.75, 8, V(XC, YR - 16, Z0 - 1))).cut(cyl(2.75, 8, V(XC, YR + 16, Z0 - 1))).removeSplitter()
    ap = box(XC - 7, 42.5, -112.0, YR + 21, Z0 - 3, Z0)
    for yy in (YR - 16, YR + 16):
        ap = ap.cut(cyl(2.75, 5, V(XC, yy, Z0 - 4)))
    for c in scr:
        ap = ap.cut(cyl(1.2, 5, V(c.x, c.y, Z0 - 4)))
    ap = ap.removeSplitter()
    addp(s2, "226_x_home_SK8 (SK8 — X 봉에 조여 고정, 구매)", sk)
    addp(s2, "226p_x_home_arm (팔 판 — 알루미늄 3 mm 레이저, SK8 밑에 M5 2, 위에 스위치 M2 2 + 너트)", ap)
    addp(s2, "226s_x_home_bolts (M5 × 10 + 너트 2, 구매)", Part.makeCompound([cyl(2.5, 12, V(XC, yy, Z0 - 5)) for yy in (YR - 16, YR + 16)]))
    laser.append(("226p_X원점팔_알루미늄3T", ap))
    _save(s2, os.path.join(OUT, "S2_마킹부.FCStd"))
    # ---------------- S3
    s3 = App.openDocument(os.path.join(OUT, "S3_프레임회로.FCStd"))
    for p, nm in (("197_uln_bracket_X", "197X_ULN받침"), ("197_uln_bracket_Y", "197Y_ULN받침")):
        for o in ob(s3, p):
            sl = o.Shape.Solids[0]
            f = [x for x in sl.Faces if x.Surface.TypeId == "Part::GeomPlane" and abs(x.normalAt(0, 0).z) > 0.9 and abs(x.BoundBox.ZMax - sl.BoundBox.ZMax) < 1e-3]
            f = max(f, key=lambda x: x.Area)
            o.Shape = f.extrude(V(0, 0, -3.0))
            o.Label = o.Label.split(" (")[0] + " (알루미늄 3 mm 레이저 평판 — 레일 위 M5 2, 기판 기둥 4)"
            laser.append((nm + "_알루미늄3T", o.Shape))
    for o in relabel(s3, "102_collar", "칼라 — 아크릴 5 mm 레이저 3장 겹침, M3로 함께 조임"):
        laser.append(("102_칼라_아크릴5T_x3", o.Shape.Solids[0]))
    for o in relabel(s3, "194b_estop_plate", "비상 정지 판 — 알루미늄 4 mm 레이저, 구멍 Ø25.5"):
        laser.append(("194b_비상정지판_알루미늄4T", o.Shape.Solids[0]))
    list(relabel(s3, "193h_wago_holder", "와고 받침 — WAGO 221-500 고정 캐리어 (사는 것), 데크에 M3"))
    # 181 카메라 걸이 → CB + 기둥 2
    cs = [s.BoundBox.Center for o in ob(s3, "180s_camera_screws") for s in o.Shape.Solids]
    bb = [s.BoundBox.Center for o in ob(s3, "181s_bracket_bolts") for s in o.Shape.Solids]
    for p in ("181_", "181s_"):
        for o in ob(s3, p):
            s3.removeObject(o.Name)
    cb = box(38.5, 71.5, -23.5, 18.5, 554.0, 557.0)
    for c in cs:
        cb = cb.cut(cyl(1.2, 5, V(c.x, c.y, 553)))
    for c in bb:
        cb = cb.cut(cyl(1.7, 5, V(c.x, c.y, 553)))
    cb = cb.removeSplitter()
    addp(s3, "181_camera_plate (카메라 판 — 아크릴 3 mm 레이저, 카메라 M2 × 8 + 너트 4)", cb)
    addp(s3, "181s_camera_standoffs (M3 수-암 기둥 45 + 8 이어서 2 + M3 × 8 2 — 위판 → 카메라 판, 구매)",
         Part.makeCompound([cyl(2.75, 53.0, V(c.x, c.y, 557.0)) for c in bb]))
    laser.append(("181_카메라판_아크릴3T", cb))
    # 199a Pi 선반 → PB + PV + L 브래킷 2
    pis = [s.BoundBox.Center for o in ob(s3, "198p_pi_standoff") for s in o.Shape.Solids]
    pv_bolts = []
    for o in ob(s3, "100j_bolt_M5_parts"):
        for s in o.Shape.Solids:
            c = s.BoundBox.Center
            if -127 < c.x < -38 and 60 < c.y < 75 and 590 < c.z < 612:
                pv_bolts.append(c)
    rep["pi_bolts"] = [[round(c.x, 1), round(c.y, 1), round(c.z, 1)] for c in pv_bolts]
    for o in ob(s3, "199a_"):
        s3.removeObject(o.Name)
    pb = box(-127.0, -38.0, 3.0, 67.0, 562.0, 565.0)
    for c in pis:
        pb = pb.cut(cyl(1.35, 5, V(c.x, c.y, 561)))
    BX = (-110.0, -55.0)
    for x in BX:
        pb = pb.cut(cyl(1.7, 5, V(x, 59.5, 561)))
    pv = box(-127.0, -38.0, 67.0, 70.0, 547.0, 610.0)
    for c in pv_bolts:
        pv = pv.cut(cyl(2.75, 5, V(c.x, 66, c.z), ey))
    for x in BX:
        pv = pv.cut(cyl(1.7, 5, V(x, 66, 554.0), ey))
    pb, pv = pb.removeSplitter(), pv.removeSplitter()
    brk = Part.makeCompound([box(x - 5, x + 5, 52.0, 67.0, 560.0, 562.0).fuse(box(x - 5, x + 5, 65.0, 67.0, 547.0, 562.0)) for x in BX])
    addp(s3, "199a_pi_shelf_plates (Pi 선반 — 바닥 판 PB 아크릴 3 + 벽 판 PV 알루미늄 3, 레이저 · 위 가로대 −y 면에 M5 2)", Part.makeCompound([pb, pv]))
    addp(s3, "199ab_pi_shelf_brackets (작은 L 브래킷 2 + M3 × 8·너트 4 — PB 밑 ↔ PV, 구매)", brk)
    laser += [("199a_Pi선반바닥_아크릴3T", pb), ("199a_Pi선반벽_알루미늄3T", pv)]
    _save(s3, os.path.join(OUT, "S3_프레임회로.FCStd"))
    # ---------------- DXF
    for nm, sh in laser:
        try:
            rep["dxf"][nm] = dxf(os.path.join(LZ, nm + ".dxf"), sh)
        except Exception as e:
            rep["dxf"][nm] = "ERR " + str(e)[:80]
    # ---------------- 정지 겹침 (바뀐 것 ↔ 전부)
    every = []
    for f in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        every += [(f[:2] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    CH = ("199b", "199d", "199e", "226", "227x", "197", "181", "199a")
    ok = (("226_x_home_SK8", "213"), ("226s", "226"), ("226p", "227x"), ("227x", "227x"), ("181s", "105"), ("181s", "181"), ("181_", "180"),
          ("199a", "198p"), ("199ab", "199a"), ("199a", "100j"), ("199a", "100k"), ("199a", "100c"), ("197", "198"), ("197", "100h"), ("197", "100i"), ("197", "100b"), ("197", "100d"),
          ("199b", "196_gate_G4"), ("199b", "199s"), ("199d", "196_gate_G1"), ("199e", "196_gate_G1"), ("199d", "199s"), ("199e", "199s"))
    probe = [(l, sh) for l, sh in every if l.split(" ", 1)[1].startswith(CH)]
    seen = set()
    for la, sa in probe:
        for lb, sb in every:
            if la == lb or (lb, la) in seen:
                continue
            ta, tb = la.split(" ", 1)[1], lb.split(" ", 1)[1]
            if any(ta.startswith(p) and tb.startswith(q) or ta.startswith(q) and tb.startswith(p) for p, q in ok):
                continue
            if sa.BoundBox.intersect(sb.BoundBox):
                try:
                    v = sa.common(sb).Volume
                except Exception:
                    v = 0.0
                if v > 0.05:
                    rep["hits"].append([la[:45], lb[:45], round(v, 1)]); seen.add((la, lb))
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_buy_b2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
