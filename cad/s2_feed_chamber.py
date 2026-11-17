# -*- coding: utf-8 -*-
"""급이실 (서현 11/17 12:03~12:20, CAP-AI-62) — 급이부 없는 도면(D5g_full_no)에 부품을 더하는 방식
  흐름: 마킹 → 펌프로 설탕물 정량 → 안쪽 문(방생 문 176) 열림 → 마킹실에 벌이 안 보이고 G5가 비면 176 닫힘 + 로그 '방생 시각'.
  밖 문 없음 (서현 '밖에 문은 빼버리는 게 낫지 않나?') — 급이실 출구는 늘 열림, 벌은 먹고 스스로 나감.
  177  급이실 = 3D 프린트 한 덩어리: 입구 관 (176 출구 소켓에 5 mm 끼움, G5 빔 x 91을 가리지 않게 x 93부터) · 방 28 × 24 × 18 · 출구 관 (x 162까지) ·
       바닥 서랍 홈 (−y로 열림) · +y 벽 호스 구멍 Ø5.2. 방 바닥 = 관 안쪽 바닥 (z 370)
  177d 접시 서랍 = 3D 프린트: 접시 Ø12 × 3 (약 0.34 mL), 윗면이 방 바닥, −y 손잡이로 빼서 씻음
  144hf 실리콘 관 끝 (안 3 · 바깥 5): +y 벽으로 들어와 접시 위 14 mm에서 떨어뜨림. 위(z 397~)는 XY 캐리지가 지나가서 관을 위로 안 뺌
  옛 아크릴 관 174는 S2에 그대로 둠 (급이부 없는 판 D5g_full_no용) — D5g_full에서는 _add_feed.py가 174를 뺌
한 번만 — 다시는 split/S2_마킹부_before_feed.FCStd에서. GUI FreeCAD에서 exec 가능 (os._exit 없음) → split/_feed_chamber.json"""
import json, os, shutil, traceback, glob, time
import FreeCAD as App, Part
HERE = r"C:\capstone\-capstone-project-repo\cad"; OUT = os.path.join(HERE, "split")
DESK = r"C:\Users\Seohyun_Lee\Desktop\capstone design\주문제작 파일\프린트_5개_최종"
V = App.Vector; ex = V(1, 0, 0)
Y0, Z0 = 0.0, 377.0                                   # 방생 길 축 (176 출구 소켓, 관 174와 같음)
rep = {}


def _save(doc, path):                               # 저장 잠김이면 임시 파일을 바꿔 넣음 (fix_screw_clash와 같음)
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


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


try:
    P, B = os.path.join(OUT, "S2_마킹부.FCStd"), os.path.join(OUT, "S2_마킹부_before_feed.FCStd")
    shutil.copy(B, P) if os.path.exists(B) else shutil.copy(P, B)
    d = App.openDocument(P, True)
    ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]
    for o in ob("177") + ob("144hf_"):
        d.removeObject(o.Name)
    # 177 급이실
    body = Part.makeCylinder(9.0, 116.5 - 93.0, V(93.0, Y0, Z0), ex)                 # 입구 관 (소켓 r 9.15에 x 93~98 끼움)
    body = body.fuse(box(116.0, 148.0, -15.0, 15.0, 363.0, 392.0))                   # 방 바깥
    body = body.fuse(Part.makeCylinder(9.0, 162.0 - 147.0, V(147.0, Y0, Z0), ex))    # 출구 관
    body = body.cut(box(118.0, 146.0, -12.0, 12.0, 370.0, 388.0))                    # 방 안 (바닥 z 370 = 관 안 바닥)
    body = body.cut(Part.makeCylinder(7.0, 75.0, V(90.0, Y0, Z0), ex))              # 길 Ø14
    body = body.cut(box(121.0, 141.0, -16.0, 12.5, 364.5, 370.0))                    # 서랍 홈 (−y로 열림)
    body = body.cut(Part.makeCylinder(2.6, 8.0, V(131.0, 17.0, 384.0), V(0, -1, 0)))  # 호스 구멍 (+y 벽)
    ch = d.addObject("Part::Feature", "FEED_CH"); ch.Shape = body.removeSplitter()
    ch.Label = "177_feed_chamber (급이실 — 3D 프린트 (학교) 한 덩어리: 176 소켓에 끼우는 입구 관 · 방 28 × 24 × 18 · 출구 관 x 162 · 바닥 접시 서랍 홈 · 호스 구멍 Ø5.2, 밖 문 없음 — 11/17)"
    # 177d 접시 서랍
    dr = box(121.2, 140.8, -15.0, 12.3, 364.7, 370.0).fuse(box(121.2, 140.8, -20.0, -15.0, 364.7, 372.0))
    dr = dr.cut(Part.makeCylinder(6.0, 3.0, V(131.0, 0.0, 367.0)))
    dw = d.addObject("Part::Feature", "FEED_DR"); dw.Shape = dr.removeSplitter()
    dw.Label = "177d_feed_dish_drawer (설탕물 접시 서랍 — 3D 프린트 (학교), 접시 Ø12 × 3 약 0.34 mL, 윗면 = 급이실 바닥, −y 손잡이로 빼서 씻음 — 11/17)"
    # 144hf 실리콘 관 끝
    hf = Part.makeCylinder(2.5, 37.0, V(131.0, 3.0, 384.0), V(0, 1, 0)).cut(Part.makeCylinder(1.5, 37.0, V(131.0, 3.0, 384.0), V(0, 1, 0)))
    ho = d.addObject("Part::Feature", "FEED_HF"); ho.Shape = hf
    ho.Label = "144hf_tube_feed_end (실리콘 관 안 3 · 바깥 5 끝 — 펌프 → 급이실 +y 벽 → 접시 위 14 mm에서 떨어뜨림, 관 길은 그리지 않음 — 11/17)"
    for o in ob("144p_pump"):
        o.Label = "144p_pump (연동 펌프 Kamoer NKP 12 V PP-A703, 구매 — 모양은 같은 계열 Adafruit 3910 [가능성 높음], 12 V 레일 MOSFET Q3)"
    rep["chamber"] = dict(valid=ch.Shape.isValid(), solids=len(ch.Shape.Solids), vol_cm3=round(ch.Shape.Volume / 1000, 2))
    rep["drawer"] = dict(valid=dw.Shape.isValid(), solids=len(dw.Shape.Solids), vol_cm3=round(dw.Shape.Volume / 1000, 2))
    d.recompute(); _save(d, P)
    # STL
    import MeshPart
    for o, nm in ((ch, "177_급이실"), (dw, "177d_접시서랍")):
        m = MeshPart.meshFromShape(Shape=o.Shape, LinearDeflection=0.05, AngularDeflection=0.3)
        fn = os.path.join(HERE, "print", "3d", nm + ".stl"); m.write(fn)
        shutil.copy(fn, os.path.join(DESK, nm + ".stl"))
        rep["stl_" + nm] = m.isSolid()
    # 정지 겹침: 새 것 ↔ 전부 (174는 급이부 없는 판 몫이라 뺌)
    every = []
    for ff in ("S1_급이부", "S2a_바닥구동", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, ff + ".FCStd"), True)
        every += [(ff[:3] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("190_")]
        App.closeDocument(dd.Name)
    every += [("S2_ " + o.Label, o.Shape.copy()) for o in d.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull()]
    CH = ("177", "144hf_")
    ok = (("177_feed", "177d"), ("177_feed", "144hf"), ("177", "174_release"), ("144hf", "174_release"), ("177_feed", "176_release_gate_housing"))
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
            try:
                if sa.BoundBox.intersect(sb.BoundBox):
                    v = sa.common(sb).Volume
                    if v > 0.05:
                        hits.append([ta[:40], tb[:40], round(v, 1)])
            except Exception:
                pass
    rep["hits"] = hits
    h6 = ob("176_release_gate_housing")[0].Shape
    rep["fit_176"] = round(ch.Shape.common(h6).Volume, 3)            # 소켓 r 9.15 > 관 r 9 → 0이어야
    rep["fit_drawer"] = round(ch.Shape.common(dw.Shape).Volume, 3)
    beam = Part.makeCylinder(1.6, 30, V(91.0, 0.0, 362.0))             # G5 빔 (x 91) 길을 급이실이 가리면 안 됨
    rep["g5_blocked"] = round(ch.Shape.common(beam).Volume, 3)
    App.closeDocument(d.Name)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_feed_chamber.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False)[:3000])
