# -*- coding: utf-8 -*-
"""나사 겹침 고치기 (서현 11/17 01:23 "나사끼리 겹치는 것 … 전부 확인", CAP-AI-62) — check_screw_clash.py 결과로
  A. S3 갠트리 높이(레일 z 440~460) 모서리 L 브래킷 8개가 12 mm 높게 그려져 레일 살과 겹치고, 그 볼트(M5 × 8)가 레일 속에 박혀 있음
     → 브래킷·볼트·T너트를 z −12 (데크·위 레일 모서리와 같은 꼴: 브래킷이 레일 밑, 볼트 레일 밑면 −1.2)
  B. S2 상자 혀 나사 308s: M5 머리(Ø9.5) 두 개가 8 mm 간격이라 겹침 → 혀 깊이 24 → 28, 구멍 −21·−29 → −21·−32 (11 mm, lift_v2 BOXD)
  C. S2 X 원점 팔 226p: M5 × 8 + 스프링너트 2가 x 29·37 (8 mm) — 같은 홈의 스프링너트(길이 10)끼리 겹침
     → 구멍 x 27·39 (12 mm), 팔 밑동을 x 21~45 (y −178~−160)로 넓힘, 226s를 머리 있는 나사로 다시 그림, DXF 226p 다시
한 번만 — 다시는 split/S2·S3 *_before_scr.FCStd에서. GUI FreeCAD에서 exec 가능 (os._exit 없음) → split/_fix_screw.json"""
import json, os, sys, shutil, traceback, importlib, glob, time
import FreeCAD as App, Part
HERE = r"C:\capstone\-capstone-project-repo\cad"; OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
rep = dict()
V = App.Vector


def _save(doc, path):                               # 저장 잠김이면 임시 파일을 바꿔 넣음
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
try:
    import lift_v2 as L, lift_v3 as L3
    importlib.reload(L); importlib.reload(L3)
    box, cyl = L.box, L.cyl
    for f in ("S2_마킹부", "S3_프레임회로"):
        P, B = os.path.join(OUT, f + ".FCStd"), os.path.join(OUT, f + "_before_scr.FCStd")
        shutil.copy(B, P) if os.path.exists(B) else shutil.copy(P, B)
    # ---------- A ----------
    d3 = App.openDocument(os.path.join(OUT, "S3_프레임회로.FCStd"), True)
    ob3 = lambda p: [o for o in d3.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]
    br = ob3("100e_bracket_2020_L")[0]
    moved_bb, keep, n_br = [], [], 0
    for s in br.Shape.Solids:
        if abs(s.BoundBox.ZMin - 432.0) < 0.3:
            t = s.copy(); t.translate(V(0, 0, -12)); keep.append(t); moved_bb.append(s.BoundBox); n_br += 1
        else:
            keep.append(s)
    br.Shape = Part.makeCompound(keep)
    n_hw = 0
    for p in ("100f_bolt_M5x8", "100g_tnut_M5_slot6"):
        o = ob3(p)[0]
        out = []
        for s in o.Shape.Solids:
            c = s.BoundBox.Center
            near = any(bb.XMin - 6 <= c.x <= bb.XMax + 6 and bb.YMin - 6 <= c.y <= bb.YMax + 6 and 430 <= c.z <= 458 for bb in moved_bb)
            if near:
                t = s.copy(); t.translate(V(0, 0, -12)); out.append(t); n_hw += 1
            else:
                out.append(s)
        o.Shape = Part.makeCompound(out)
    rep["A"] = dict(brackets=n_br, hardware=n_hw)
    d3.recompute(); _save(d3, os.path.join(OUT, "S3_프레임회로.FCStd")); App.closeDocument(d3.Name)
    # ---------- B · C ----------
    d2 = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"), True)
    ob2 = lambda p: [o for o in d2.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]
    mw = App.Matrix(); mw.move(L3.WORLD)
    ob2("300_marking_box")[0].Shape = L.marking_box().transformed(mw)
    tx, ty, tt, td = L.BOXD["tongue"]
    ts = []
    for z in L.BOXD["tongue_holes"]:
        ts.append(L.pan(V(tx, ty + tt, z), V(0, -1, 0), 5.0, 10.0))
        ts.append(L.box(tx - 5, tx + 5, 5.0, 9.0, z - 3, z + 3))
    ob2("308s_tongue_screws")[0].Shape = Part.makeCompound(ts).transformed(mw)
    arm = ob2("226p_x_home_arm")[0]
    a = arm.Shape.fuse(box(21.0, 45.0, -178.0, -160.0, 460.0, 463.0))
    a = a.fuse(cyl(2.76, 3, V(29.0, -170.0, 460.0))).fuse(cyl(2.76, 3, V(37.0, -170.0, 460.0))).removeSplitter()   # 옛 구멍 메움
    BX = (27.0, 39.0)
    for x in BX:
        a = a.cut(cyl(2.75, 5, V(x, -170.0, 459.0)))
    arm.Shape = a.removeSplitter()
    hw = [L.pan(V(x, -170.0, 463.0), V(0, 0, -1), 5.0, 8.0) for x in BX] + [box(x - 5, x + 5, -173, -167, 454.0, 458.0) for x in BX]
    ob2("226s_x_home_bolts")[0].Shape = Part.makeCompound(hw)
    ob2("226s_x_home_bolts")[0].Label = "226s_x_home_bolts (20시리즈 M5 × 8 + 스프링너트 2, 구매 — 11/17 간격 8 → 12, 스프링너트끼리 겹침 없앰)"
    ob2("308s_tongue_screws")[0].Label = "308s_tongue_screws (M5 × 10 둥근머리 렌치 2 + 20시리즈 M5 스프링너트 2 — 상자 혀 → 세운 막대, 구매 — 11/17 간격 8 → 11, 머리 겹침 없앰)"
    d2.recompute(); _save(d2, os.path.join(OUT, "S2_마킹부.FCStd")); App.closeDocument(d2.Name)
    # DXF 226p
    f = max([x for x in a.Faces if x.Surface.TypeId == "Part::GeomPlane"], key=lambda x: x.Area); bb = a.BoundBox
    uv = lambda p: (p.x - bb.XMin, p.y - bb.YMin)
    ents = []
    for e in f.Edges:
        cv = e.Curve
        if "Circle" in cv.TypeId and e.isClosed():
            cc = uv(cv.Center); ents.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (cc[0], cc[1], cv.Radius)); continue
        pts = [uv(p) for p in e.discretize(Deflection=0.02)]
        for p0, p1 in zip(pts[:-1], pts[1:]):
            ents.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (p0[0], p0[1], p1[0], p1[1]))
    open(os.path.join(HERE, "print", "laser", "226p_X원점팔_알루미늄3T.dxf"), "w", encoding="ascii").write(
        "0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(ents) + "\n0\nENDSEC\n0\nEOF\n")
    rep["arm_bb"] = [round(v, 1) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax)]
    # 정지 겹침: 바뀐 것 ↔ 전부
    every = []
    for f_ in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, f_ + ".FCStd"), True)
        every += [(f_[:2] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    CH = ("100e_bracket_2020_L", "300_marking_box", "308s", "226p", "226s")
    ok = (("300_marking_box", "300"), ("300_marking_box", "301"), ("300_marking_box", "304"), ("300_marking_box", "307"), ("300_marking_box", "308"),
          ("300_marking_box", "112_entry_iso"), ("300_marking_box", "176_release"), ("300_marking_box", "300e"),
          ("308s", "307v"), ("226s", "226p"), ("226s", "100b"), ("226p", "227x"), ("226p", "100b"), ("100e", "100f"), ("100e", "100g"))
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
            if sa.BoundBox.intersect(sb.BoundBox):
                v = sa.common(sb).Volume
                if v > 0.05:
                    hits.append([ta[:40], tb[:40], round(v, 1)])
    rep["hits"] = hits
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_fix_screw.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False)[:3000])
