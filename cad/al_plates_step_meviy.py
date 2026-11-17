# -*- coding: utf-8 -*-
"""알루미늄 레이저 판 17장 전부 → meviy STEP 한 폴더 + 구멍 표 (서현 11/18 01시 '가공할 것은 부품 파일로 하나하나, 파일명·위치·재질까지', CAP-AI-62)
xy_plates_step_meviy.py (XY 판 9장)를 넓힌 것: + 문판 112f·170f·176f (1.5T) · 194b 비상정지판 (4T) · 197 드라이버받침 · 199a Pi선반벽 · 226p X원점팔 (3T) · 144b 펌프걸이 (4T).
모델은 안 바꿈. 판마다 STEP (A5052), 구멍마다 자리·탭/접시/관통·끝단 거리 (meviy 가이드 p.12 끝단 ↔ 구멍 1 mm).
freecad.exe cad/al_plates_step_meviy.py (cwd = cad) → print/meviy/*.step + 구멍표_meviy.md + split/_meviy.json, 바탕화면 '주문제작 파일\\meviy_알루미늄_STEP'"""
import json, os, math, shutil, traceback
HERE = os.getcwd(); OUT = os.path.join(HERE, "print", "meviy"); os.makedirs(OUT, exist_ok=True)
DESK = r"C:\Users\Seohyun_Lee\Desktop\capstone design\주문제작 파일\meviy_알루미늄_STEP"
TAP = {0.8: "M2 탭 (밑구멍 Ø1.6)", 1.25: "M3 탭 (밑구멍 Ø2.5)"}
# (문서, 객체 이름 앞, 고르기, 파일 이름, 두께 표기, 개수, 쓰임)
PL = [("S2_마킹부", "212_beam_plates", "YA", "YA_빔판A", "3", 1, "X 빔 −y 끝 (SC8UU·Y 봉 끝)"),
      ("S2_마킹부", "212_beam_plates", "YB", "YB_빔판B", "3", 1, "X 빔 +y 끝"),
      ("S2_마킹부", "212_beam_plates", "XN", "XN_X너트판", "3", 1, "X 리드 너트 (M2 탭 2)"),
      ("S2_마킹부", "211_y_motor_plate", None, "YM_Y모터판", "3", 1, "Y 모터"),
      ("S2_마킹부", "217_x_motor_plate", None, "217_X모터판", "3", 1, "X 모터"),
      ("S2_마킹부", "206_carriage_plates", "CP", "CP_캐리지판", "3", 1, "Y 캐리지 (LMK8UU 2)"),
      ("S2_마킹부", "206_carriage_plates", "SP", "SP_안내판", "3", 1, "펜 홀더 안내 (M3 탭 3 · 접시 1)"),
      ("S2_마킹부", "206_carriage_plates", "SV", "SV_서보판", "3", 1, "펜 서보 SG90"),
      ("S2_마킹부", "202_holder_plate_HV", None, "HV_홀더판", "3", 1, "펜 홀더 (P 클립)"),
      ("S2_마킹부", "112_entry_gate_flap", None, "112f_입구문판", "1.5", 1, "입구 문 (서보 혼)"),
      ("S2_마킹부", "170_isolation_gate_flap", None, "170f_격리문판", "1.5", 1, "격리 문 (서보 혼)"),
      ("S2_마킹부", "176_release_gate_flap", None, "176f_방생문판", "1.5", 1, "방생 문 (서보 혼)"),
      ("S3_프레임회로", "194b_estop_plate", None, "194b_비상정지판", "4", 1, "비상 정지 스위치 (Ø25.5)"),
      ("S3_프레임회로", "197_drv_bracket", None, "197_드라이버받침", "3", 1, "DRV8825 보드"),
      ("S3_프레임회로", "199a_pi_shelf_plates", "PV", "199a_Pi선반벽", "3", 1, "Pi 선반 벽 (FALCS 2)"),
      ("S2_마킹부", "226p_x_home_arm", None, "226p_X원점팔", "3", 1, "X 원점 스위치"),
      ("S1_급이부", "144b_feeder_holder", None, "144b_펌프걸이", "4", 1, "급이 펌프 (나중)")]
rep = {}
try:
    import FreeCAD as App, Part
    V = App.Vector

    def pick(o, sel):
        sols = o.Shape.Solids
        if sel is None:
            return sols[0]
        if sel in ("YA", "YB", "XN"):
            for s in sols:
                b = s.BoundBox
                if ("XN" if b.XLength < 4 else ("YA" if b.Center.y < 0 else "YB")) == sel:
                    return s
        if sel == "CP":
            return [s for s in sols if s.BoundBox.YLength < 4][0]
        if sel in ("SP", "SV"):
            px = sorted([s for s in sols if s.BoundBox.XLength < 4], key=lambda s: s.BoundBox.Center.x)
            return px[0] if sel == "SP" else px[1]
        if sel == "PV":
            return [s for s in sols if s.BoundBox.YLength < 4][0]

    def holes_of(s):                                   # xy_plates_step_meviy.py와 같은 읽기
        b = s.BoundBox
        f0 = max(s.Faces, key=lambda f: f.Area); n = f0.normalAt(0, 0)
        ax = max(range(3), key=lambda i: abs((n.x, n.y, n.z)[i])); uax = [i for i in range(3) if i != ax]
        lo = (b.XMin, b.YMin, b.ZMin); hi = (b.XMax, b.YMax, b.ZMax); t = hi[ax] - lo[ax]
        outer = f0.OuterWire; holes = {}
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
            r = h["r"]; kind = TAP.get(round(r, 2), "관통 Ø%.1f" % (2 * r))
            if h["csk"]:
                kind = "접시 Ø%.1f %.0f° (%s 쪽), 관통 Ø%.1f" % (h["csk"][0], h["csk"][1], h["csk"][2], 2 * r)
            if r > 8:
                kind = "관통 Ø%.1f" % (2 * r)
            rows.append(dict(u=round(p - lo[uax[0]], 2), v=round(q - lo[uax[1]], 2), kind=kind, edge=round(edge, 2),
                             land=round(t - (h["csk"][0] / 2 - r) / math.tan(math.radians(h["csk"][1] / 2)), 2) if h["csk"] else None))
        return [round(hi[uax[0]] - lo[uax[0]], 1), round(hi[uax[1]] - lo[uax[1]], 1), round(t, 2)], rows

    docs = {}
    md = ["# 알루미늄 판 17장 — meviy STEP과 구멍 표 (11/18, CAP-AI-62)", "",
          "재질 **A5052, 표면 처리 없음, 각 1장**. 파일: `cad/print/meviy/*.step` (바탕화면 `주문제작 파일\\meviy_알루미늄_STEP`). "
          "meviy에 STEP을 올리고, 아래 표에서 **'탭'이라 적힌 구멍만** 더블클릭 → 속성 '탭' + 나사 크기 (meviy 가이드 p.13). 접시는 모델에 90° 원뿔로 그려져 있음.",
          "자리 (u, v) = 판을 펴서 왼쪽 아래 모서리에서 mm. '쪽' = 접시가 파인 면. ⚠ = 끝단 1 mm 안 됨.", ""]
    for doc, pre, sel, nm, tt, q, use in PL:
        if doc not in docs:
            docs[doc] = App.openDocument(os.path.join(HERE, "split", doc + ".FCStd"), True)
        o = [x for x in docs[doc].Objects if x.TypeId.startswith("Part::") and x.Label.startswith(pre)][0]
        s = pick(o, sel)
        size, rows = holes_of(s)
        fn = "%s_A5052_%sT.step" % (nm, tt)
        s.exportStep(os.path.join(OUT, fn))
        ntap = sum(1 for r in rows if "탭" in r["kind"]); ncsk = sum(1 for r in rows if r["kind"].startswith("접시"))
        bad = [r for r in rows if r["edge"] < 1.0]
        rep[nm] = dict(file=fn, size=size, holes=len(rows), tap=ntap, csk=ncsk, min_edge=min([r["edge"] for r in rows] or [99]), bad=bad, valid=s.isValid(), qty=q, use=use)
        md.append("## %s — %.1f × %.1f × %.1f mm, %d장 (`%s`) — %s" % (nm, size[0], size[1], size[2], q, fn, use))
        md.append("| 구멍 | 자리 (u, v) | 가공 | 끝단까지 | 접시 밑 남는 두께 |"); md.append("|---|---|---|---|---|")
        for i, r in enumerate(rows, 1):
            md.append("| %d | (%.2f, %.2f) | %s | %.2f mm%s | %s |" % (i, r["u"], r["v"], r["kind"], r["edge"], " ⚠" if r["edge"] < 1.0 else "",
                                                                ("%.2f mm" % r["land"]) if r["land"] is not None else ""))
        if not rows:
            md.append("| — | — | 구멍 없음 | — | — |")
        md.append("")
    for d in docs.values():
        App.closeDocument(d.Name)
    open(os.path.join(OUT, "구멍표_meviy.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    os.makedirs(DESK, exist_ok=True)
    for f in os.listdir(OUT):
        shutil.copy(os.path.join(OUT, f), DESK)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(HERE, "split", "_meviy.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
