# -*- coding: utf-8 -*-
"""리니어 모듈 Keshuo 15BY25-77 하나만 3D로 (서현 11/12 12:37 "일단 넣지 말고 도면을 토대로 3d로 제대로 그려… 리프트 부품만", CAP-AI-62)

판매처 3D(STEP)는 없음 — 판매처 치수도 6af992a1….webp + 사진 49c7eadc….webp (motormicro.com)만 있음 [확실, 11/12 확인].
GrabCAD의 비슷한 것(DVD 픽업 이송 모듈 B-04E 등)은 로그인해야 받을 수 있어 못 받음 → 같은 짜임(모터 + 접은 판 + 리드 + 봉 + 슬라이더)으로 직접 그림.

좌표 (모듈 혼자): x = 축 방향 (모터 뒤 0 → 끝 88), y = 폭 가운데 0, z = 바닥판 아랫면 0
[확실 — 치수도/사진]  전체 88 · 모터 Ø15 · 모터 + 단자판 폭 18 · 판 폭 14.5 · 끝판 높이 15 · 바닥 2-M3 간격 48
                      · 슬라이더 길이 10 · 바닥 아랫면 → 슬라이더 윗면 10.5 · 슬라이더 위 2-M2.5 (간격 10) · 리드 M3 × 0.5 · 행정 62
[추측 — 도면에 없음, 사서 잼] 판 두께 0.8 · 모터 길이 13 · 가이드 봉 Ø3 자리 (리드 옆 −3.5, 아래) · 봉 베어링 Ø5 · 옆 턱 높이 2.5 · 슬라이더 바닥 높이 1.5
  freecad.exe 창에서: exec(open("cad/ks_15by25_module.py").read()); make(save_dir)
"""
import os
import FreeCAD as App
import Part

V = App.Vector
D = dict(L=88.0, md=15.0, mt=13.0, W=14.5, H=15.0, t=0.8, hp=48.0, sl=10.0, top=10.5, slz=1.5, sh=10.0,
         ax=7.5, rod=3.0, rod_y=-3.5, rod_z=4.0, lip=2.5, stroke=62.0)


# 슬라이더 가운데 x: 행정 0 (모터 쪽) — 판 안쪽 길이 73.4 − 슬라이더 10 = 63.4 ≥ 행정 62, 양 끝 0.7씩 남김
X_START = D["mt"] + D["t"] + 0.7 + D["sl"] / 2
STEPS_PER_MM = 360 / 18 / 0.5 * 2        # 18°/걸음 → 20 걸음/바퀴, 리드 0.5 mm → 40 걸음/mm, 반걸음 80 [확실 — 판매처 표]


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cylx(r, x0, x1, y, z):
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def parts(slider_x=None):
    """반환 {이름: (모양, 색)} — 슬라이더 가운데 x (기본: 행정 가운데)"""
    d = D
    W2, t = d["W"] / 2, d["t"]
    xf0, xf1 = d["mt"], d["L"]                                      # 판: 모터 앞면 → 끝
    # 모터: 캔 + 뒤 뚜껑 (조금 작게) + 단자판 (옆으로 3 나옴 → 폭 18)
    motor = cylx(d["md"] / 2, 0.6, d["mt"], 0, d["ax"]).fuse(cylx(d["md"] / 2 - 0.6, 0, 0.6, 0, d["ax"]))
    motor = motor.cut(box(2.0, 9.0, -1, 1, d["ax"] + 6.8, d["ax"] + 8))                          # 캔 위 홈 (사진)
    pcb = box(1.0, 8.0, d["md"] / 2, d["md"] / 2 + 0.8, d["ax"] - 4.5, d["ax"] + 2.5)
    for i, z in enumerate((-3.5, -1.5, 0.5, 2.0)):
        pcb = pcb.fuse(Part.makeCylinder(0.6, 2.2, V(3.0 + 1.3 * i, d["md"] / 2 + 0.8, d["ax"] + z - 0.5), V(0, 1, 0)))   # 선 납땜 4 (18 − 15 = 3)
    # 접은 판: 바닥 + 양 끝판 + 옆 턱 (홈 3개씩)
    fr = box(xf0, xf1, -W2, W2, 0, t)
    fr = fr.fuse(box(xf0, xf0 + t, -W2, W2, 0, d["H"])).fuse(box(xf1 - t, xf1, -W2, W2, 0, d["H"]))
    for ys in (-W2, W2 - t):
        lip = box(xf0, xf1, ys, ys + t, 0, d["lip"])
        for xn in (30.0, 52.0, 74.0):
            lip = lip.cut(box(xn - 4, xn + 4, ys - 1, ys + 2, t, d["lip"] + 1))
        fr = fr.fuse(lip)
    xm = (xf0 + xf1) / 2
    for dx in (-d["hp"] / 2, d["hp"] / 2):
        fr = fr.cut(Part.makeCylinder(1.25, 3, V(xm + dx, 0, -1)))                                 # 2-M3 (탭 Ø2.5)
    fr = fr.cut(box(xm - 12, xm + 12, -2.5, 2.5, -1, 2))                                            # 바닥 창 (치수도 아래 그림)
    fr = fr.cut(cylx(1.6, xf0 - 1, xf0 + 2, 0, d["ax"])).cut(cylx(d["rod"] / 2, xf0 - 1, xf1 + 1, d["rod_y"], d["rod_z"]))
    fr = fr.cut(cylx(2.5, xf1 - 2, xf1 + 1, 0, d["ax"]))                                          # 끝판에 받침 끼우는 구멍
    fr = fr.removeSplitter()
    bush = cylx(2.5, xf1 - t, xf1, 0, d["ax"]).cut(cylx(1.5, xf1 - 3, xf1 + 1, 0, d["ax"]))         # 리드 끝 받침 — 끝판 구멍에 끼움 (안쪽에 튀어나오면 행정 62가 안 나옴, 11/12 움직임 검사)
    # 리드 M3 (나사산은 그리지 않음) + 가이드 봉
    screw = cylx(1.5, d["mt"], xf1 - 0.2, 0, d["ax"])
    rod = cylx(d["rod"] / 2, xf0, xf1, d["rod_y"], d["rod_z"])
    # 구리 슬라이더
    xc = X_START + d["stroke"] / 2 if slider_x is None else slider_x
    s = box(xc - d["sl"] / 2, xc + d["sl"] / 2, -W2 + 1.0, W2 - 1.0, d["slz"], d["top"])
    s = s.cut(cylx(1.5, xc - 6, xc + 6, 0, d["ax"])).cut(cylx(d["rod"] / 2, xc - 6, xc + 6, d["rod_y"], d["rod_z"]))
    s = s.cut(cylx(2.5, xc - 6, xc - d["sl"] / 2 + 1.5, d["rod_y"], d["rod_z"]))                  # 봉 쪽 베어링 자리 (사진의 검은 고리)
    for dy in (-d["sh"] / 2, d["sh"] / 2):
        s = s.cut(Part.makeCylinder(1.0, 5, V(xc, dy, d["top"] - 4)))                              # 2-M2.5 (탭 Ø2)
    brg = cylx(2.5, xc - d["sl"] / 2 + 0.2, xc - d["sl"] / 2 + 1.5, d["rod_y"], d["rod_z"]).cut(cylx(d["rod"] / 2, xc - 6, xc + 6, d["rod_y"], d["rod_z"]))
    G, G2, G3 = (0.62, 0.62, 0.64), (0.75, 0.75, 0.77), (0.45, 0.45, 0.47)      # 산 그대로 = 회색 (서현 색 규칙)
    return {"모터 15BY25 (Ø15 × 13)": (motor, G2), "단자판·선 납땜 4": (pcb, G3), "접은 판 (바닥 + 끝판 2 + 옆 턱)": (fr, G),
            "리드 M3 × 0.5": (screw, G3), "가이드 봉 Ø3": (rod, G3), "리드 끝 받침": (bush, G2),
            "구리 슬라이더 10 × 12.5 (2-M2.5)": (s.removeSplitter(), G2), "슬라이더 베어링": (brg, G3)}


def make(save_dir=None, name="P153m_리니어모듈_15BY25-77"):
    if name in App.listDocuments():
        App.closeDocument(name)
    doc = App.newDocument(name)
    for i, (k, (shp, col)) in enumerate(parts().items()):
        o = doc.addObject("Part::Feature", "KS%02d" % i)
        o.Label, o.Shape = "153m_%02d %s" % (i, k), shp
        if App.GuiUp:
            o.ViewObject.ShapeColor = col
    doc.recompute()
    if save_dir:
        doc.saveAs(os.path.join(save_dir, name + ".FCStd"))
    return doc


def check(doc):
    """겹침(부피 > 0.01) · 전체 크기 · 슬라이더 윗면 높이"""
    obs = doc.Objects
    hits = []
    for i in range(len(obs)):
        for j in range(i + 1, len(obs)):
            v = obs[i].Shape.common(obs[j].Shape).Volume
            if v > 0.01:
                hits.append((obs[i].Label, obs[j].Label, round(v, 3)))
    bb = Part.makeCompound([o.Shape for o in obs]).BoundBox
    sl = [o for o in obs if "슬라이더 10" in o.Label][0].Shape.BoundBox
    return dict(hits=hits, size=(round(bb.XLength, 2), round(bb.YLength, 2), round(bb.ZLength, 2)), slider_top=round(sl.ZMax, 2),
                valid=[o.Label for o in obs if not o.Shape.isValid()])


def move(doc, s_mm):
    """슬라이더·베어링을 행정 s_mm (0~62) 자리로 — 반환 움직이는 것과 고정된 것의 겹침"""
    mov = [o for o in doc.Objects if "슬라이더" in o.Label]
    fix = [o for o in doc.Objects if o not in mov]
    for o in mov:
        o.Placement = App.Placement(V(s_mm - D["stroke"] / 2, 0, 0), App.Rotation())
    hits = []
    for a in mov:
        sa = a.Shape.copy()
        sa.Placement = a.Placement
        for f in fix:
            v = sa.common(f.Shape).Volume
            if v > 0.01:
                hits.append((a.Label, f.Label, round(v, 3)))
    return hits
