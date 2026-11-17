# -*- coding: utf-8 -*-
"""XY 알루미늄 판 9장 → meviy에 올릴 STEP + 구멍 표 (서현 11/17 17:27 '1번은 제대로 해', CAP-AI-62)
meviy 사용자 가이드 (2026-08-10) p.10 판금 구멍 종류: 탭·버링탭·접시(카운터싱크) 지원, p.13 탭은 나사산을 그리지 말고 밑구멍 원통으로 두고
올린 뒤 그 구멍을 더블클릭해 '탭' 속성, p.12 끝단 ↔ 구멍 1 mm 이상. 모델 S2의 판은 이미 그렇게 생김 (탭 = 밑구멍 Ø1.6·Ø2.5, 접시 = 90° 원뿔).
이 스크립트는 모델을 바꾸지 않음 — 판마다 STEP, 구멍마다 (자리 · 뚫는 지름 · 접시 지름·각도·쪽 · 끝단까지 거리)를 읽어 검사.
freecad.exe cad/xy_plates_step_meviy.py (cwd = cad) → print/xy_step/*.step + 구멍표.md + split/_xy_step.json, 바탕화면 레이저_XY판/STEP_meviy/"""
import json, os, math, shutil, traceback
HERE = os.getcwd(); OUT = os.path.join(HERE, "print", "xy_step"); os.makedirs(OUT, exist_ok=True)
DESK = r"C:\Users\Seohyun_Lee\Desktop\capstone design\주문제작 파일\레이저_XY판\STEP_meviy"
TAP = {0.8: "M2 탭 (밑구멍 Ø1.6)", 1.25: "M3 탭 (밑구멍 Ø2.5)"}       # 반지름 → 탭
rep = {}
try:
    import FreeCAD as App, Part
    V = App.Vector
    d = App.openDocument(os.path.join(HERE, "split", "S2_마킹부.FCStd"), True)
    want = [("212_beam_plates", ["YA_빔판A", "YB_빔판B", "XN_X너트판"]),
            ("211_y_motor_plate", ["YM_Y모터판"]),
            ("217_x_motor_plate", ["217_X모터판"]),
            ("206_carriage_plates", ["CP_캐리지판", "SP_안내판", "SV_서보판"]),
            ("202_holder_plate_HV", ["HV_홀더판"])]
    md = ["# XY 알루미늄 판 9장 — meviy 올리는 법과 구멍 표 (11/17, CAP-AI-62)", "",
          "재질 **알루미늄 A5052, 두께 3 mm, 각 1장, 표면 처리 없음**. 파일: `print/xy_step/*.step` (바탕화면 `주문제작 파일\\레이저_XY판\\STEP_meviy`).",
          "1. meviy에 STEP을 올림 (판금). 2. 아래 표에서 **'탭'이라 적힌 구멍만** 더블클릭 → 속성 '탭' + 나사 크기 (meviy 가이드 p.13). 접시 구멍은 모델에 이미 90° 원뿔로 그려져 있어 그대로 (메뉴에 '접시'로 잡히는지만 확인).",
          "3. 견적 화면에 가공 불가 표시가 나오면 그 판·구멍을 Claude에게 알려 줌 → 관통 구멍 + 너트로 바꿈.", "",
          "자리 (u, v) = 판을 펴서 왼쪽 아래 모서리에서 mm (DXF와 같은 원점). '쪽' = 접시가 파인 면.", ""]
    for pre, names in want:
        o = [x for x in d.Objects if x.Label.startswith(pre)][0]
        sols = o.Shape.Solids
        if pre == "212_beam_plates":
            byname = {}
            for s in sols:
                b = s.BoundBox
                byname["XN" if b.XLength < 4 else ("YA" if b.Center.y < 0 else "YB")] = s
            sols = [byname["YA"], byname["YB"], byname["XN"]]
        if pre == "206_carriage_plates":
            cp = [x for x in sols if x.BoundBox.YLength < 4][0]
            px = sorted([x for x in sols if x.BoundBox.XLength < 4], key=lambda x: x.BoundBox.Center.x)
            sols = [cp] + px
        for nm, s in zip(names, sols):
            b = s.BoundBox
            f0 = max(s.Faces, key=lambda f: f.Area); n = f0.normalAt(0, 0)
            ax = max(range(3), key=lambda i: abs((n.x, n.y, n.z)[i]))          # 판 두께 방향
            uax = [i for i in range(3) if i != ax]
            lo = (b.XMin, b.YMin, b.ZMin); hi = (b.XMax, b.YMax, b.ZMax)
            t = hi[ax] - lo[ax]
            outer = f0.OuterWire
            holes = {}
            for f in s.Faces:
                st = f.Surface.TypeId
                if "Cylinder" in st or "Cone" in st:
                    c = f.Surface.Center if "Cylinder" in st else f.Surface.Apex
                    a = f.Surface.Axis
                    if abs((a.x, a.y, a.z)[ax]) < 0.99:
                        continue
                    key = tuple(round((c.x, c.y, c.z)[i], 2) for i in uax)
                    h = holes.setdefault(key, dict(r=99.0, csk=None))
                    if "Cylinder" in st:
                        h["r"] = min(h["r"], f.Surface.Radius)
                    else:
                        rmax = max(e.Curve.Radius for e in f.Edges if "Circle" in e.Curve.TypeId)
                        zc = [(e.Curve.Center.x, e.Curve.Center.y, e.Curve.Center.z)[ax] for e in f.Edges if "Circle" in e.Curve.TypeId and abs(e.Curve.Radius - rmax) < 1e-6][0]
                        side = ("+" if zc > (lo[ax] + hi[ax]) / 2 else "−") + "xyz"[ax]
                        h["csk"] = (round(2 * rmax, 2), round(abs(2 * math.degrees(f.Surface.SemiAngle)), 1), side)
            rows = []
            for (p, q), h in sorted(holes.items()):
                pt = [0, 0, 0]; pt[uax[0]], pt[uax[1]] = p, q; v0 = f0.Vertexes[0].Point; pt[ax] = (v0.x, v0.y, v0.z)[ax]
                rr = max(h["r"], (h["csk"][0] / 2) if h["csk"] else 0)
                edge = outer.distToShape(Part.Vertex(V(*pt)))[0] - rr
                r = h["r"]
                kind = TAP.get(round(r, 2), "관통 Ø%.1f" % (2 * r))
                if h["csk"]:
                    kind = "접시 Ø%.1f %.0f° (%s 쪽), 관통 Ø%.1f" % (h["csk"][0], h["csk"][1], h["csk"][2], 2 * r)
                if r > 8:                                                   # 모터 턱 같은 큰 구멍
                    kind = "관통 Ø%.1f" % (2 * r)
                rows.append(dict(u=round(p - lo[uax[0]], 2), v=round(q - lo[uax[1]], 2), kind=kind, edge=round(edge, 2),
                                 land=round(t - (h["csk"][0] / 2 - r) / math.tan(math.radians(h["csk"][1] / 2)), 2) if h["csk"] else None))
            fn = "%s_A5052_3T.step" % nm
            s.exportStep(os.path.join(OUT, fn))
            w, hh = hi[uax[0]] - lo[uax[0]], hi[uax[1]] - lo[uax[1]]
            bad = [r_ for r_ in rows if r_["edge"] < 1.0]
            rep[nm] = dict(size=[round(w, 1), round(hh, 1), round(t, 2)], holes=rows, edge_lt_1mm=bad, valid=s.isValid())
            md.append("## %s — %.1f × %.1f × %.1f mm (`%s`)" % (nm, w, hh, t, fn))
            md.append("| 구멍 | 자리 (u, v) | 가공 | 끝단까지 | 접시 밑 남는 두께 |")
            md.append("|---|---|---|---|---|")
            for i, r_ in enumerate(rows, 1):
                md.append("| %d | (%.2f, %.2f) | %s | %.2f mm%s | %s |" % (i, r_["u"], r_["v"], r_["kind"], r_["edge"], " ⚠" if r_["edge"] < 1.0 else "",
                                                                    ("%.2f mm" % r_["land"]) if r_["land"] is not None else ""))
            md.append("")
    App.closeDocument(d.Name)
    open(os.path.join(OUT, "구멍표_meviy.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    os.makedirs(DESK, exist_ok=True)
    for f in os.listdir(OUT):
        shutil.copy(os.path.join(OUT, f), DESK)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(HERE, "split", "_xy_step.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
