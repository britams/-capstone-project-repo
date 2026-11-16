# -*- coding: utf-8 -*-
"""11/16 21:28 서현 "깔떼기는 3d 프린트 해 / 코튼롤 필요 없을 것 … 모터로 설탕물 그릇에 / 3. 완제품 모듈로 바꾸는 시도" (CAP-AI-62)
  ① 깔때기 111·173: 산 깔때기 모양(McMaster 9017T211)에서 콘만 남기고 목 안 Ø14 + 아크릴 관(바깥 18) 끼우는 소켓 Ø18.3 → 3D 프린트. 열수축관 111h·173h 뺌
     111 소켓 11 (관 110 아래 끝), 173 소켓 8.5 (G4 받침 199b와 안 닿게)
  ② 급이: 솜 142n · 호스 142h · 아크릴 토막 175s 뺌 → T 175 가지를 그릇으로 (안 Ø13, 관 바닥 아래 깊이 4.5, 바닥 4, 가운데 Ø5.1 구멍에 펌프 관 144hf)
  ③ 문 빛 게이트: 3 mm LED 6쌍 → Adafruit 2167 5쌍 (20 × 10 × 8, LED는 10 폭 가운데·끝에서 5 [추측 — G6과 같은 꼴]).
     2167 몸 폭 10이라 빔 간격 6 → 11: G2 x 20.5 · G2b 31.5 (y +9, 몸 +y로), G3 31.5 · G3b 20.5 (y −9, 몸 −y로), G5 x 91 (y 0, 몸 −y로).
     G5b 없앰 (방생 문 앞은 마킹실 안 → 카메라). 하우징 112·176에 빔 구멍 Ø3.2, 몸은 위·아래 면에 양면 폼테이프
  ④ 176 하우징 끝(x 86) ↔ 관 174(x 90.5) 사이 4.5 mm 틈 발견 → 출구 소켓 (바깥 r 11, 관 받는 r 9.15, 앞 r 7, +y는 서보 때문에 y 8.9에서 자름)
실제 작업은 GUI FreeCAD 숨은 문서로 한 번 했음 (이 파일은 같은 값 기록). 다시는 split/S2_마킹부_before_gf.FCStd에서.
검사 [확실 — CAD]: 바뀐 것 ↔ S1·S2·S3 정지 겹침 0 (빔 ↔ 투명 관 174 빼고), STL 6개 닫힌 한 덩어리"""
import os
import FreeCAD as App, Part
V = App.Vector; ex = V(1, 0, 0)
S = os.path.join(os.getcwd(), "split")
d = App.openDocument(os.path.join(S, "S2_마킹부_before_gf.FCStd"), True)
ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]


def duct_end(lab, top):
    sh = ob(lab)[0].Shape
    cy = [f for f in sh.Faces if "Cylinder" in f.Surface.TypeId and abs(f.Surface.Radius - 9) < 0.01][0].Surface
    pl = [f for f in sh.Faces if "Plane" in f.Surface.TypeId]
    f = (max if top else min)(pl, key=lambda f: f.CenterOfMass.z)
    a = cy.Axis
    return f.CenterOfMass, (a if a.z > 0 else -a)


# ① 깔때기
E, a = duct_end("110_entry_duct", False)
f = ob("111_entry_funnel")[0]
b = f.Shape.common(Part.makeBox(80, 80, 36.2, V(-40, -40, 200)))
b = b.fuse(Part.makeCylinder(11, E.z + 1.5 - 236.2, V(0, 0, 236.2))).fuse(Part.makeCylinder(11, 11, E - a * 0.5, a))
f.Shape = b.cut(Part.makeCylinder(7, 30, V(0, 0, 225))).cut(Part.makeCylinder(9.15, 20, E, a)).removeSplitter()
E, a = duct_end("172_isolation_duct", True)
f = ob("173_isolation_funnel")[0]
b = f.Shape.common(Part.makeBox(80, 80, 40, V(-40, -40, 596.2)))
b = b.fuse(Part.makeCylinder(11, 596.2 - (E.z + 0.5) + 0.01, V(1.5, 0, E.z + 0.5))).fuse(Part.makeCylinder(11, 11, E + a * 0.5, -a))
b = b.cut(Part.makeCylinder(7, 40, V(1.5, 0, 575))).cut(Part.makeCylinder(9.15, 20, E, -a))
f.Shape = b.cut(Part.makeBox(60, 60, 15.5, V(-28, -30, 560))).removeSplitter()
for p in ("111h_heat_shrink", "173h_heat_shrink", "175s_feed_stub", "142h_feed_hose", "142n_cotton"):
    for o in ob(p):
        d.removeObject(o.Name)
# ② 그릇
t = ob("175_release_feed_tee")[0]
sh = t.Shape.fuse(Part.makeCylinder(9.1, 27, V(150, 0, 340.5))).cut(Part.makeBox(40, 40, 32, V(130, -20, 330)))
t.Shape = sh.cut(Part.makeCylinder(6.5, 12, V(150, 0, 366))).cut(Part.makeCylinder(2.55, 6, V(150, 0, 361))).removeSplitter()
ob("144hf_tube_feed_end")[0].Shape = Part.makeCylinder(2.5, 26, V(150, 0, 340))
# ③ ④ 게이트·176 소켓
for p in ("196_gate_G2", "196_gate_G3", "196_gate_G5"):
    for o in ob(p):
        d.removeObject(o.Name)
h2, h6 = ob("112_entry_iso_gate_housing")[0], ob("176_release_gate_housing")[0]
sl = Part.makeCylinder(11, 12.1, V(85.9, 0, 377), ex).cut(Part.makeCylinder(7, 12.2, V(85.8, 0, 377), ex))
sl = sl.cut(Part.makeCylinder(9.15, 8, V(90.5, 0, 377), ex)).cut(Part.makeBox(20, 10, 30, V(80, 8.9, 360)))
s2, s6 = h2.Shape, h6.Shape.fuse(sl)
G = (("G2", 20.5, 9, 1, 386.0, 362.0), ("G2b", 31.5, 9, 1, 387.2, 362.0), ("G3", 31.5, -9, -1, 387.2, 362.0),
     ("G3b", 20.5, -9, -1, 388.2, 362.0), ("G5", 91.0, 0, -1, 388.5, 365.5))
for n, x, y, yd, zt, zb in G:
    hole = Part.makeCylinder(1.6, zt - zb + 2, V(x, y, zb - 1))
    if x < 50:
        s2 = s2.cut(hole)
    else:
        s6 = s6.cut(hole)
    y0 = y - 5 if yd > 0 else y - 15
    o = d.addObject("Part::Feature", "GM_" + n)
    o.Shape = Part.makeCompound([Part.makeBox(10, 20, 8, V(x - 5, y0, zt)), Part.makeBox(10, 20, 8, V(x - 5, y0, zb - 8))])
    o.Label = "196_gate_%s_tx_rx (Adafruit 2167 송·수신 완제품 — 납땜 없음, 양면 폼테이프)" % n
    o = d.addObject("Part::Feature", "GB_" + n); o.Shape = Part.makeCylinder(0.6, zt - zb, V(x, y, zb)); o.Label = "196_gate_%s_beam" % n
h2.Shape, h6.Shape = s2.removeSplitter(), s6.removeSplitter()
d.recompute(); d.saveAs(os.path.join(S, "S2_마킹부.FCStd"))
