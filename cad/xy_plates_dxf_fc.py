# -*- coding: utf-8 -*-
"""XY 알루미늄 판 → 레이저 DXF (R12, mm) — CAD 판 모양에서 바로 뽑음 (11/15, CAP-AI-62)
freecad.exe cad/xy_plates_dxf_fc.py (cwd = cad) → print/xy/*.dxf + print/xy/_plates.json
판마다 가장 큰 평면(접시 자리가 없는 쪽)을 펴서. 탭 구멍은 밑구멍(M2 Ø1.6, M3 Ø2.5)으로 — 파일 이름의 "탭"·"접시"는 업체(meviy)에 같이 맡길 가공: 법선 y 판은 (x, z), 법선 x 판은 (y, z). 원점 = 판 왼쪽 아래."""
import json, os, traceback
HERE = os.getcwd(); OUT = os.path.join(HERE, "print", "xy"); os.makedirs(OUT, exist_ok=True)
rep = {}
try:
    import FreeCAD as App, Part
    d = App.openDocument(os.path.join(HERE, "split", "S2_마킹부.FCStd"), True)
    want = [("212_beam_plates", ["YA_빔판A_알루미늄3T_M4접시6", "YB_빔판B_알루미늄3T_M4접시6", "XN_X너트판_알루미늄3T_M2탭2"]),
            ("211_y_motor_plate", ["YM_Y모터판_알루미늄3T_M3접시3"]),
            ("217_x_motor_plate", ["217_X모터판_알루미늄3T"]),
            ("206_carriage_plates", ["CP_캐리지판_알루미늄3T", "SP_안내판_알루미늄3T_M3탭3", "SV_서보판_알루미늄3T"]),
            ("202_holder_plate_HV", ["HV_홀더판_알루미늄3T_M3접시2"])]
    for pre, names in want:
        o = [x for x in d.Objects if x.Label.startswith(pre)][0]
        sols = o.Shape.Solids
        if pre == "212_beam_plates":       # YA (y −59), YB (y 49), XN (두께 x 3)
            byname = {}
            for s in o.Shape.Solids:
                b = s.BoundBox
                k = "XN" if b.XLength < 4 else ("YA" if b.Center.y < 0 else "YB")
                byname[k] = s
            sols = [byname["YA"], byname["YB"], byname["XN"]]
        if pre == "206_carriage_plates":   # CP (두께 y), SP (x ≈ 88.6), SV (x ≈ 101.6)
            cp = [x for x in sols if x.BoundBox.YLength < 4][0]
            px = sorted([x for x in sols if x.BoundBox.XLength < 4], key=lambda x: x.BoundBox.Center.x)
            sols = [cp] + px
        for nm, s in zip(names, sols):
            amax = max(f.Area for f in s.Faces)        # (11/17) 접시 자리가 없는 쪽 면 (원 반지름 합이 작은 면) = 뚫는 구멍 지름
            f0 = max(s.Faces, key=lambda f: f.Area); n0 = f0.normalAt(0, 0)
            cand = [f for f in s.Faces if "Plane" in f.Surface.TypeId and f.Area > 0.6 * amax and abs(abs(f.normalAt(0, 0).dot(n0)) - 1) < 1e-6]
            f = min(cand, key=lambda f: sum(e.Curve.Radius for e in f.Edges if "Circle" in e.Curve.TypeId))
            nx = abs(f.normalAt(0, 0).x) > 0.9
            b = s.BoundBox
            u0, v0 = (b.YMin if nx else b.XMin), b.ZMin
            uv = lambda p: ((p.y if nx else p.x) - u0, p.z - v0)
            ents = []
            hole = {}                                   # (11/17) 양쪽 면 원 중 같은 자리는 작은 것 (접시 자리가 양쪽에 나뉘어 있어도 뚫는 지름)
            for ff in cand:
                for e in ff.Edges:
                    if "Circle" in e.Curve.TypeId and e.isClosed():
                        cc = uv(e.Curve.Center); k = (round(cc[0], 2), round(cc[1], 2))
                        hole[k] = min(hole.get(k, 99.0), e.Curve.Radius)
            for k, r in hole.items():
                ents.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (k[0], k[1], r))
            for e in f.Edges:
                c = e.Curve
                if "Circle" in c.TypeId and e.isClosed():
                    continue
                if isinstance(c, Part.Line) or e.Curve.TypeId == "Part::GeomLine":
                    a, z = uv(e.Vertexes[0].Point), uv(e.Vertexes[-1].Point)
                    ents.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (a[0], a[1], z[0], z[1]))
                elif "Circle" in c.TypeId:
                    cc = uv(c.Center)
                    if e.isClosed():
                        ents.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (cc[0], cc[1], c.Radius))
                    else:
                        import math
                        a, z = uv(e.Vertexes[0].Point), uv(e.Vertexes[-1].Point)
                        a0 = math.degrees(math.atan2(a[1] - cc[1], a[0] - cc[0])); a1 = math.degrees(math.atan2(z[1] - cc[1], z[0] - cc[0]))
                        ents.append("0\nARC\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f\n50\n%.3f\n51\n%.3f" % (cc[0], cc[1], c.Radius, a0, a1))
                else:
                    raise RuntimeError("edge type " + c.TypeId)
            w, h = (b.YLength if nx else b.XLength), b.ZLength
            fn = "%s_%gx%g.dxf" % (nm, round(w, 1), round(h, 1))
            with open(os.path.join(OUT, fn), "w", encoding="ascii") as fo:
                fo.write("0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(ents) + "\n0\nENDSEC\n0\nEOF\n")
            rep[fn] = dict(edges=len(ents), holes=sum(1 for x in ents if "CIRCLE" in x), w=round(w, 2), h=round(h, 2), t=round(min(b.XLength, b.YLength), 2))
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_plates.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
