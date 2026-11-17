# -*- coding: utf-8 -*-
"""문판 3장 (112f·170f·176f) — 서보 날개(혼)에 나사로 붙일 긴 구멍 + 날개 가운데 나사 자리 홈 (서현 11/18 01:30 'A', CAP-AI-62)
  옛 모델: 문판이 날개와 겹쳐만 있고 구멍 0 (al_plates_step_meviy.py 구멍 표에서 찾음).
  날개 줄 (가운데 축 → 날개 끝 구멍, 모델은 30° 아래)을 따라 축에서 5.5~11.5 mm 긴 구멍 폭 2.2 → 그 사이 날개 구멍에 날개 봉지의 작은 나사 2개
  (1차는 16까지 — 문판 아래 안쪽 모서리 (y 17.2, z 369)를 뚫고 나가 판 모양이 깨짐 → 11.5. 끝단 검사는 판 바깥선으로)
  (MG90S 날개 구멍 간격은 모름 [추측]). 축 자리 (날개를 서보에 고정하는 나사 머리)는 판 끝에 Ø6 홈 — 문판이 그 머리에 뜨지 않게.
  긴 구멍·홈은 통로 구멍 (Ø12) 밖 (닫혔을 때 말벌이 못 지나감) — 거리는 split/_flapslot.json. 220 컵받침은 이름표만 (폼 양면테이프, AI 판단).
한 번만 — 다시는 split/S2_마킹부_before_flapslot.FCStd에서. freecad.exe 따로 (cwd = cad) → split/_flapslot.json + print/laser/1xxf DXF"""
import json, os, shutil, traceback, math
HERE = os.getcwd(); OUT = os.path.join(HERE, "split")
DESK = r"C:\Users\Seohyun_Lee\Desktop\capstone design\주문제작 파일\레이저_판"
R0, R1, W, NR = 5.5, 11.5, 2.2, 3.0
rep = {}
try:
    import FreeCAD as App, Part
    V = App.Vector
    P, B = os.path.join(OUT, "S2_마킹부.FCStd"), os.path.join(OUT, "S2_마킹부_before_flapslot.FCStd")
    shutil.copy(B, P) if os.path.exists(B) else shutil.copy(P, B)
    d = App.openDocument(P, True)
    ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)][0]

    def dxf_yz(sh, path):                               # x 판: 두께 가운데를 잘라 (y, z) 선·원
        bb = sh.BoundBox; ws = sh.slice(V(1, 0, 0), (bb.XMin + bb.XMax) / 2); e = []
        for w in ws:
            for ed in w.Edges:
                c = ed.Curve
                if "Circle" in type(c).__name__ and ed.isClosed():
                    e.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (c.Center.y - bb.YMin, c.Center.z - bb.ZMin, c.Radius))
                else:
                    pts = [ed.Vertexes[0].Point, ed.Vertexes[-1].Point] if "Line" in type(c).__name__ else ed.discretize(Deflection=0.01)
                    for p, q in zip(pts[:-1], pts[1:]):
                        e.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (p.y - bb.YMin, p.z - bb.ZMin, q.y - bb.YMin, q.z - bb.ZMin))
        open(path, "w", encoding="ascii").write("0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(e) + "\n0\nENDSEC\n0\nEOF\n")
        return len(e)

    for key, horn, bore, fn in (("112_entry_gate_flap", "112_entry_gate_horn", (9.0, 376.5), "112f_입구문판_알루미늄1.5T.dxf"),
                                ("170_isolation_gate_flap", "170_isolation_gate_horn", (-9.0, 376.5), "170f_격리문판_알루미늄1.5T.dxf"),
                                ("176_release_gate_flap", "176_release_gate_horn", (0.0, 377.0), "176f_방생문판_알루미늄1.5T.dxf")):
        fo = ob(key); s = fo.Shape.Solids[0]; b = s.BoundBox
        hc = [f.Surface for f in ob(horn).Shape.Faces if "Cylinder" in f.Surface.TypeId]
        H = [c.Center for c in hc if abs(c.Radius - 4.0) < 0.01][0]; A = [c.Center for c in hc if abs(c.Radius - 1.0) < 0.01][0]
        u = V(0, A.y - H.y, A.z - H.z); u.normalize(); n = V(0, -u.z, u.y)
        x0, T = b.XMin - 1, b.XLength + 2
        p1 = V(x0, H.y, H.z) + u * R0; p2 = V(x0, H.y, H.z) + u * R1; r = W / 2
        wire = Part.Wire([Part.LineSegment(p1 + n * r, p2 + n * r).toShape(), Part.Arc(p2 + n * r, p2 + u * r, p2 - n * r).toShape(),
                          Part.LineSegment(p2 - n * r, p1 - n * r).toShape(), Part.Arc(p1 - n * r, p1 - u * r, p1 + n * r).toShape()])
        slot = Part.Face(wire).extrude(V(T, 0, 0))
        notch = Part.makeCylinder(NR, T, V(x0, H.y, H.z), V(1, 0, 0))
        s2 = Part.Solid(s.cut(slot).cut(notch).removeSplitter().Solids[0])
        g = max(s2.Faces, key=lambda f: f.Area); inner = [w for w in g.Wires if not w.isSame(g.OuterWire)]
        by, bz = bore
        dmin = min((math.hypot(q.y - by, q.z - bz) for q in (p1, p2)))
        rep[key[:4]] = dict(valid=s2.isValid(), vol_before=round(s.Volume, 1), vol_after=round(s2.Volume, 1),
                            slot_from=[round(p1.y, 2), round(p1.z, 2)], slot_to=[round(p2.y, 2), round(p2.z, 2)],
                            slot_to_bore_edge=round(dmin - r - 6.0, 2), notch_to_bore_edge=round(math.hypot(H.y - by, H.z - bz) - NR - 6.0, 2),
                            slot_closed=len(inner) == 1, slot_to_outline=round(min(w.distToShape(g.OuterWire)[0] for w in inner), 2) if inner else None)
        fo.Shape = s2
        fo.Label = fo.Label.split(" (")[0] + " (문판 — 알루미늄 1.5 mm 레이저, 서보 날개 줄 따라 긴 구멍 폭 2.2 (축에서 %g~%g) + 날개 나사 자리 홈 Ø6 — 날개 봉지의 작은 나사 2 (11/18))" % (R0, R1)
        rep[key[:4]]["dxf_entities"] = dxf_yz(s2, os.path.join(HERE, "print", "laser", fn))
        if os.path.isdir(DESK):
            shutil.copy(os.path.join(HERE, "print", "laser", fn), DESK)
    o = ob("220_cup_bracket"); o.Label = "220_cup_bracket (컵 받침 — 아크릴 5 mm 레이저, 방생 문 하우징 −y 선반 위에 폼 양면테이프 (11/18, 뚜껑 컵만 얹힘 — 구멍 없음))"
    d.recompute(); d.save(); App.closeDocument(d.Name)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_flapslot.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
