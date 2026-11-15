# -*- coding: utf-8 -*-
"""급이를 마킹실 밖 방생 통로로 (서현 11/15 18:48 "급이를 마킹실에다 두지 말고 나가자 마자 바로 주면 … 마킹실이랑 급이실이랑 나누자", "가로" = 유인액, CAP-AI-62)
  방생: 문 176 → 수도용 PVC 13A 관 → PVC 13A T자 이음 (가지가 아래) → T 오른쪽 끝이 바로 출구 (프레임 안, 위·옆이 열림)
  급이: T 가지 아래에 PVC 13A 토막 → 그 안에 실리콘 호스 (바깥 13 · 안 10) → 코튼롤 2호 Ø10 × 38, 위 끝이 관 바닥 위 2 mm
        말벌이 관 바닥을 걸어 나가며 젖은 솜 위를 지나감. 펌프 관(3.5 × 5)이 호스 밑으로 들어와 솜을 적심 (관 나머지 길은 휘는 관이라 그림 생략)
        펌프는 트랩 맨 아래 유인액 통에서 빨아옴 → 병·병 뚜껑·클램프·버림통·옛 물길(143 계열)·솜(마킹실 +y)·물빠짐 관 뺌
  뺌 (S2): 174 방생 목, 175 굴뚝 (프린트 2). 176 하우징 출구 구멍 Ø18.3 (PVC 끼움). G6 받침·센서는 관이 굵어진 만큼 위아래 1 mm
  상자 +y 솜 구멍은 lift_v2 BOXD feed=False (s2_doors_swap처럼 상자 모양을 다시 넣음)
치수 [추측 — 판매처 표 확인할 것]: T 이음 13A 길이 50 · 바깥 25 · 받는 깊이 16 · 가지 끝까지 32
한 번만 (다시는 split/S1·S2 *_before_feed.FCStd에서). freecad.exe cad/s2_release_feed.py (cwd = cad) → split/S1·S2, split/_release_feed.json"""
import json, os, sys, traceback, glob, time
HERE = os.getcwd(); OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
rep = dict(hits=[], removed=[])


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


try:
    import FreeCAD as App, Part
    import lift_v2 as L
    import lift_v3 as L3
    import D5e_module_kinematic as K
    V = App.Vector
    ex, ez = V(1, 0, 0), V(0, 0, 1)
    ZR, XT = 377.0, 135.0                       # 방생 축 높이, T 가운데 x
    TL, TO, TD, TB = 50.0, 12.5, 16.0, 32.0     # T 길이·바깥 반지름·받는 깊이·가지 길이
    tube = lambda ro, ri, h, p, d: K.tube(ro, ri, h, p, d)

    s2 = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    ob = lambda d, p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]
    for p in ("174_release", "175_release"):
        for o in ob(s2, p):
            rep["removed"].append(o.Label[:40]); s2.removeObject(o.Name)
    mw = App.Matrix(); mw.move(L3.WORLD)
    for o in ob(s2, "300_marking_box"):
        o.Shape = L.marking_box().transformed(mw)
    for o in ob(s2, "176_release_gate_housing"):
        o.Shape = o.Shape.cut(K.cyl(9.15, 8, V(90.0, 0, ZR), ex))
    for p in ("196_gate_G6_tx_rx", "199c_gate_holder_G6"):
        for o in ob(s2, p):
            out = []
            for sl in o.Shape.Solids:
                t = sl.copy(); t.translate(V(0, 0, -1 if sl.BoundBox.Center.z < ZR else 1)); out.append(t)
            o.Shape = Part.makeCompound(out)
    x0 = XT - TL / 2
    pvc1 = tube(9.0, 6.5, x0 + TD - 90.5, V(90.5, 0, ZR), ex)
    tee = tube(TO, 6.5, TL, V(x0, 0, ZR), ex).fuse(tube(TO, 6.5, TB, V(XT, 0, ZR), V(0, 0, -1)))
    tee = tee.cut(K.cyl(9.1, TD, V(x0, 0, ZR), ex)).cut(K.cyl(9.1, TD, V(x0 + TL - TD, 0, ZR), ex)).cut(K.cyl(9.1, TD, V(XT, 0, ZR - TB), ez))
    tee = tee.cut(K.cyl(6.5, TL + 2, V(x0 - 1, 0, ZR), ex)).cut(K.cyl(6.5, TB, V(XT, 0, ZR - TB), ez)).removeSplitter()
    zb = ZR - TB + TD                           # 가지 받는 끝 (토막 위 끝)
    stub = tube(9.0, 6.5, 40.0, V(XT, 0, zb - 40.0), ez)
    zc_top = ZR - 6.5 + 2.0                     # 솜 위 끝: 관 안 바닥 + 2
    hose = tube(6.5, 5.0, zc_top - 1.0 - (zb - 60.0), V(XT, 0, zb - 60.0), ez)
    cotton = K.cyl(5.0, 38.0, V(XT, 0, zc_top - 38.0))
    feed_end = K.cyl(2.5, 25.0, V(XT, 0, zb - 60.0 - 5.0))
    add = [("174_release_duct_PVC (수도용 PVC 13A — 바깥 18·안 13, %d mm, 방생 문 → T, 11/15 굴뚝·목 대신)" % round(x0 + TD - 90.5), pvc1, (0.85, 0.85, 0.85)),
           ("175_release_feed_tee (수도용 PVC 13A T자 이음 — 가지 아래, 오른쪽 끝이 출구 · 급이 자리, 구매)", tee, (0.85, 0.85, 0.85)),
           ("175s_feed_stub_PVC (PVC 13A 40 mm — T 가지 아래, 호스 받침)", stub, (0.85, 0.85, 0.85)),
           ("142h_feed_hose (실리콘 호스 바깥 13 · 안 10 — 솜 잡음, 구매)", hose, (0.9, 0.6, 0.6)),
           ("142n_cotton_roll_#2 (Ø10 × 38, 구매 — 위 끝이 방생 관 바닥 위 2 mm, 2일마다 호스째 빼서 갈기)", cotton, (0.97, 0.97, 0.9)),
           ("144hf_tube_feed_end (실리콘 관 3.5 × 5 끝 — 펌프 → 호스 밑, 나머지 길 그림 생략)", feed_end, (0.9, 0.6, 0.6))]
    for lab, sh, col in add:
        n = s2.addObject("Part::Feature", "RF_%d" % len(s2.Objects))
        n.Shape, n.Label = sh, lab
        if App.GuiUp:
            n.ViewObject.ShapeColor = col
    _save(s2, os.path.join(OUT, "S2_마킹부.FCStd"))
    s1 = App.openDocument(os.path.join(OUT, "S1_급이부.FCStd"))
    for p in ("142n", "143", "144n", "144nc", "144c_", "144w", "144h_", "144hf", "144hd"):
        for o in ob(s1, p):
            rep["removed"].append(o.Label[:40]); s1.removeObject(o.Name)
    _save(s1, os.path.join(OUT, "S1_급이부.FCStd"))
    rep["path"] = dict(pvc1=round(x0 + TD - 90.5, 1), tee_x=(x0, x0 + TL), cotton_top=zc_top, hose=(zb - 60.0, zc_top - 1.0))
    # 정지 겹침: 바뀐 것 ↔ 전부
    every = []
    for f in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        every += [(f[:2] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    CH = ("174_release_duct", "175_release_feed", "175s", "142h", "142n", "144hf_tube_feed_end", "176_release_gate_housing", "196_gate_G6", "199c", "300_")
    grp = ("174_release_duct", "175", "142", "144hf", "176_release_gate_housing")
    ok = (("300_", "300"), ("300_", "301"), ("300_", "304"), ("300_", "308"), ("300_", "307"), ("300_", "196_gate"),
          ("196_gate_G6", "199c"), ("196_gate_G6", "174_release_duct"), ("199c", "174_release_duct"), ("176_release", "196_gate_G5"), ("176_release", "176"), ("176_release", "112s"))
    probe = [(l, sh) for l, sh in every if l.split(" ", 1)[1].startswith(CH)]
    seen = set()
    for la, sa in probe:
        for lb, sb in every:
            if la == lb or (lb, la) in seen:
                continue
            ta, tb = la.split(" ", 1)[1], lb.split(" ", 1)[1]
            if ta.startswith(grp) and tb.startswith(grp):
                continue
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
json.dump(rep, open(os.path.join(OUT, "_release_feed.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
