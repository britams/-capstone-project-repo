# -*- coding: utf-8 -*-
"""출력 줄이기 1묶음 — 관·꺾임·깔때기 (서현 11/15 "출력 5개 미만", CAP-AI-62)
  관 110·172·174 (PVC 13A) → 사는 것 (맞춤 절단 판매) — 모양 그대로, 이름만
  깔때기 111·173 → 국내 PP 깔때기 (사는 것) — 모양 그대로 [추측: 지름 60 급, 목에 열수축관]
  꺾임 110b·172b → 입구·격리 문 하우징과 **한 덩어리 프린트** (남기는 프린트 3개 중 1개): 규격 PVC 엘보(중심 → 끝 36)는
      관 축(x 0)과 하우징(x 13.5) 사이 13.5 mm에 안 들어감 → 하우징에 꺾임을 붙여 같이 뽑음 [AI 판단]
  방생 T: JIS/KS TS 13 치수 [가능성 높음 — 미스미 표 Z 10 · H 36 = 받는 깊이 26]로 다시, 가운데 x 135 → 150 (G6이 관 위에 남게)
한 번만 (다시는 split/S2_마킹부_before_b1.FCStd에서). freecad.exe cad/s2_buy_batch1.py (cwd = cad) → split/S2, split/_buy_b1.json"""
import json, os, sys, traceback, glob, time
HERE = os.getcwd(); OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
rep = dict(hits=[])


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
    import D5e_module_kinematic as K
    V = App.Vector
    ex, ez = V(1, 0, 0), V(0, 0, 1)
    s2 = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    ob = lambda p: [o for o in s2.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]
    # 1) 이름만
    ren = {"110_entry_duct": "110_entry_duct (수도용 PVC 13A 바깥 18·안 13, 115 mm — 맞춤 절단으로 삼, 4° 기울어 깔때기 목 → 하우징 꺾임)",
           "172_isolation_duct": "172_isolation_duct (수도용 PVC 13A 바깥 18·안 13, 195 mm — 맞춤 절단으로 삼, 하우징 꺾임 → 깔때기 173)",
           "111_entry_funnel": "111_entry_funnel (국내 PP 깔때기 Ø60 급 — 사는 것, 목에 열수축관 111h [추측: 판매처 치수로 맞춤])",
           "173_isolation_funnel": "173_isolation_funnel (국내 PP 깔때기 Ø50 급 — 사는 것, 목에 열수축관 173h [추측])"}
    for k, v in ren.items():
        for o in ob(k):
            o.Label = v
    # 2) 문 하우징 + 꺾임 한 덩어리
    parts = ob("112_entry_gate_housing") + ob("170_isolation_gate_housing") + ob("110b") + ob("172b_isolation")
    sh = parts[0].Shape
    for o in parts[1:]:
        sh = sh.fuse(o.Shape)
    sh = sh.removeSplitter()
    rep["housing_solids"] = len(sh.Solids)
    for o in parts:
        s2.removeObject(o.Name)
    n = s2.addObject("Part::Feature", "B1_housing")
    n.Shape = sh
    n.Label = "112_entry_iso_gate_housing (입구·격리 문 하우징 + 꺾임 2 한 덩어리 — 남기는 프린트, PVC 관이 꺾임 소켓에 끼움)"
    # 3) 방생 T 다시 (TS 13: 가운데 → 받는 바닥 10, → 끝 36)
    for p in ("174_release_duct", "175_release_feed_tee", "175s_", "142h_", "142n_", "144hf_tube_feed_end"):
        for o in ob(p):
            s2.removeObject(o.Name)
    ZR, XT, Z, H, OR = 377.0, 150.0, 10.0, 36.0, 13.0
    tube = K.tube
    pvc1 = tube(9.0, 6.5, XT - Z - 90.5, V(90.5, 0, ZR), ex)
    tee = tube(OR, 6.5, 2 * H, V(XT - H, 0, ZR), ex).fuse(tube(OR, 6.5, H, V(XT, 0, ZR), V(0, 0, -1)))
    for p0, d in ((V(XT - H, 0, ZR), ex), (V(XT + Z, 0, ZR), ex), (V(XT, 0, ZR - H), ez)):
        tee = tee.cut(K.cyl(9.1, H - Z, p0, d))
    tee = tee.cut(K.cyl(6.5, 2 * H + 2, V(XT - H - 1, 0, ZR), ex)).cut(K.cyl(6.5, H, V(XT, 0, ZR - H), ez)).removeSplitter()
    zb = ZR - Z
    stub = tube(9.0, 6.5, 40.0, V(XT, 0, zb - 40.0), ez)
    ztop = ZR - 6.5 + 2.0
    hose = tube(6.5, 5.0, ztop - 1.0 - (zb - 60.0), V(XT, 0, zb - 60.0), ez)
    cotton = K.cyl(5.0, 38.0, V(XT, 0, ztop - 38.0))
    fe = K.cyl(2.5, 25.0, V(XT, 0, zb - 65.0))
    add = [("174_release_duct_PVC (수도용 PVC 13A 바깥 18·안 13, %d mm — 맞춤 절단으로 삼, 방생 문 → T)" % round(XT - Z - 90.5), pvc1, (0.85, 0.85, 0.85)),
           ("175_release_feed_tee (수도용 PVC TS 티 13 — 가지 아래, 오른쪽 끝이 출구 · 급이 자리, 구매)", tee, (0.85, 0.85, 0.85)),
           ("175s_feed_stub_PVC (PVC 13A 40 mm — T 가지 아래, 호스 받침, 맞춤 절단)", stub, (0.85, 0.85, 0.85)),
           ("142h_feed_hose (실리콘 호스 바깥 13 · 안 10 — 솜 잡음, 구매)", hose, (0.9, 0.6, 0.6)),
           ("142n_cotton_roll_#2 (Ø10 × 38, 구매 — 위 끝이 방생 관 바닥 위 2 mm, 2일마다 호스째 빼서 갈기)", cotton, (0.97, 0.97, 0.9)),
           ("144hf_tube_feed_end (실리콘 관 3.5 × 5 끝 — 펌프 → 호스 밑, 나머지 길 그림 생략)", fe, (0.9, 0.6, 0.6))]
    for lab, shp, col in add:
        n = s2.addObject("Part::Feature", "B1_%d" % len(s2.Objects))
        n.Shape, n.Label = shp, lab
    rep["release"] = dict(pvc1=round(XT - Z - 90.5, 1), tee=(XT - H, XT + H), branch_end=ZR - H)
    _save(s2, os.path.join(OUT, "S2_마킹부.FCStd"))
    # 정지 겹침
    every = []
    for f in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        every += [(f[:2] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    CH = ("112_entry_iso", "174_release_duct", "175", "142h", "142n", "144hf_tube_feed_end")
    grp = ("174_release_duct", "175", "142", "144hf")
    ok = (("112_entry_iso", "112_entry_gate"), ("112_entry_iso", "170_isolation_gate"), ("112_entry_iso", "196_gate_G2"), ("112_entry_iso", "196_gate_G3"),
          ("112_entry_iso", "112s"), ("112_entry_iso", "110_entry_duct"), ("112_entry_iso", "172_isolation_duct"), ("112_entry_iso", "300_"),
          ("174_release_duct", "176_release"), ("174_release_duct", "196_gate_G6"), ("174_release_duct", "199c"))
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
json.dump(rep, open(os.path.join(OUT, "_buy_b1.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
