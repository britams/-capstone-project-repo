# -*- coding: utf-8 -*-
"""S1_급이부만 고치기 — 따로 띄운 freecad.exe로: freecad.exe cad/edit_s1.py (CAP-AI-62)
1) S1 열기  2) 둘레 40 mm 안의 마킹부·프레임 부품을 CTX_로 넣기  3) D5g_feeder_uln.feeder_detail_apply (143) → D5g_feeder_pump.apply (병·펌프·관·버림통)
4) CTX 지우기  5) 색 규칙  6) 저장 → split/_edit_s1.json"""
import json, os, sys, time, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "split")
rep = dict(ok=False, t=time.strftime("%H:%M:%S"))
try:
    import FreeCAD as App
    import split3 as S
    d = App.openDocument(os.path.join(OUT, "S1_급이부.FCStd"))
    rep["ctx"] = len(S.add_context(d, OUT))
    import D5g_feeder_uln as FU
    FU.feeder_detail_apply(d)          # 143 물길·뚜껑·기둥·앵글·나사·너트·니플 (CTX의 120 벽도 고쳐지지만 버려짐 — 벽은 S2 몫)
    import D5g_feeder_pump as FPMP
    r = FPMP.apply(d)
    rep["feeder_pump"] = {k: r[k] for k in ("drain_tube", "feed_tube_z", "feed_tube_len_mm", "drain_tube_len_mm", "bad", "bottle_lift_blockers", "cap_hand_blockers", "holder_on_rail_mm") if k in r}
    rep["overlaps"] = r.get("overlaps")
    # 143 하드웨어 ↔ 전부 (상자 겹치는 것만). 허용: 나사산 물림·관이 바브에
    allow = {("143n_", "143_feed_trough"), ("143n_", "144hf_tube_feed"), ("143n_", "144hd_tube_drain"), ("143hn_", "143h_screws_M3")}
    hw = [o for o in d.Objects if o.Label.startswith(("143p_", "143a_", "143b_", "143h_", "143hn_", "143n_", "143m_", "143mm_"))]
    h143 = []
    for a_ in hw:
        for o in d.Objects:
            if o is a_ or o.TypeId != "Part::Feature" or not a_.Shape.BoundBox.intersect(o.Shape.BoundBox):
                continue
            v = a_.Shape.common(o.Shape).Volume
            if v > 0.05:
                x, y = a_.Label.split(" ")[0], o.Label.split(" ")[0]
                ok = any((x.startswith(p) and y == q) or (y.startswith(p) and x == q) for p, q in allow)
                h143.append((x, y, round(v, 2), "허용" if ok else "문제"))
    rep["hw143"] = h143
    rep["bad"] = [h for h in h143 if h[3] == "문제"] + list(r.get("bad", []))
    S.remove_context(d)
    S.color_doc(d)
    d.recompute()
    d.save()
    rep["objects"] = len([o for o in d.Objects if o.TypeId == "Part::Feature"])
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
with open(os.path.join(OUT, "_edit_s1.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
