# -*- coding: utf-8 -*-
"""S1 급이부 PC판: 단순 모양 대신 산 부품 STEP (CAP-AI-62)

  freecad.exe cad/s1_vendor.py   (따로 띄운 창, cwd = cad)
레포의 S1_급이부.FCStd는 그대로 (단순 모양). McMaster CAD는 공개 레포에 올리지 않음 →
결과는 PC의 'capstone design_이서현\\CAD files\\split\\S1_급이부_STEP.FCStd' 에만 저장.

넣는 것 (받은도면 step파일):
  143n  니플 2 — McMaster 6220N79 (니켈 도금 황동, M5 × 0.8, 관 안 4 mm, 길이 14) [확실 — 판매처 표]
        STEP 좌표: 축 x, 섬유 패킹 바깥 면 x −0.24 = 받침 면, 나사는 −x, 바브는 +x
  143hn 너트 4 — McMaster 90592A085 (M3, 폭 5.5, 높이 2.4 표 / STEP 2.73 — 모따기 포함) [확실 — 판매처 표]
        STEP 좌표: 축 z, z −1.39 ~ 1.34
나사(M3 × 12·16·8)는 아직 단순 모양 — 길이별 STEP을 받은 뒤.
"""
import json, os, sys, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
STEP = r"C:\Users\Seohyun_Lee\Desktop\capstone design\받은도면 step파일" + "\\"
PC = r"C:\Users\Seohyun_Lee\Desktop\capstone design_이서현\CAD files\split"
OUT = os.path.join(HERE, "split")
rep = dict(ok=False)
try:
    import FreeCAD as App
    import Part
    V = App.Vector
    import D5g_feeder_uln as FU
    import split3 as S
    FU.feeder_hardware()                                   # 자리만 얻음 (PLACES)
    nip = Part.read(STEP + "6220N79_Brass Low-Pressure Barbed Tube Fitting.STEP")
    nut = Part.read(STEP + "90592A085_Steel Hex Nut.STEP")

    def put(shape, local_pt, local_dir, p, d):
        s = shape.copy()
        s.translate(-local_pt)
        rot = App.Rotation(local_dir, d)
        s.Placement = App.Placement(p, rot).multiply(s.Placement)
        return s

    nips = [put(nip, V(-0.24, 0, 0), V(-1, 0, 0), p, d) for p, d in FU.PLACES["nipple"]]
    nuts = [put(nut, V(0, 0, -1.39), V(0, 0, 1), q, d) for q, d in FU.PLACES["nut"]]
    d = App.openDocument(os.path.join(OUT, "S1_급이부.FCStd"))
    old = {}
    for o in d.Objects:
        h = o.Label.split(" ")[0]
        if h in ("143n_nipple_M5_barb", "143hn_nuts_M3"):
            old[h] = o
    old["143n_nipple_M5_barb"].Shape = Part.makeCompound(nips)
    old["143n_nipple_M5_barb"].Label = "143n_nipple_M5_barb (McMaster 6220N79 STEP — 니켈 황동 M5, 관 안 4, 2개)"
    old["143hn_nuts_M3"].Shape = Part.makeCompound(nuts)
    old["143hn_nuts_M3"].Label = "143hn_nuts_M3 (McMaster 90592A085 STEP — M3 너트 4)"
    rep["nipples"], rep["nuts"] = len(nips), len(nuts)
    # 겹침: 새 두 부품 ↔ S1 전부 + 둘레 (허용 = 나사산 물림)
    S.add_context(d, OUT)
    allow = {("143n", "143_feed_trough"), ("143n", "144hf_tube_feed"), ("143n", "144hd_tube_drain"), ("143hn", "143h_screws_M3")}
    hits = []
    for key in ("143n_nipple_M5_barb", "143hn_nuts_M3"):
        a = old[key]
        for o in d.Objects:
            if o is a or o.TypeId != "Part::Feature" or not a.Shape.BoundBox.intersect(o.Shape.BoundBox):
                continue
            v = a.Shape.common(o.Shape).Volume
            if v > 0.05:
                b = o.Label.split(" ")[0]
                ok = any(key.startswith(x) and b == y for x, y in allow)
                hits.append((key, b, round(v, 2), "허용" if ok else "문제"))
    rep["overlaps"] = hits
    rep["bad"] = [h for h in hits if h[3] == "문제"]
    S.remove_context(d)
    S.color_doc(d)
    os.makedirs(PC, exist_ok=True)
    d.saveAs(os.path.join(PC, "S1_급이부_STEP.FCStd"))
    rep["saved"] = os.path.join(PC, "S1_급이부_STEP.FCStd")
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
with open(os.path.join(OUT, "_s1_vendor.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
