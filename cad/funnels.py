# -*- coding: utf-8 -*-
"""깔때기 111·173 → 산 깔때기 McMaster 9017T211 (서현 11/12 03:03 "이 깔떼기도 살 수 있지 않나?", CAP-AI-62)

고른 것: McMaster 9017T211 — PP 분말 깔때기 Style E (짧고 넓은 목)
  윗지름 2 3/4" (69.9), 높이 2 3/4", 목 바깥 9/16" (14.3), 목 길이 1" [확실 — 판매처 표]
  목 안지름 0.48" = 12.2 [확실 — 판매처 STEP의 원기둥 면 반지름 0.24"] → 통로 안 12와 같음 (말벌 지나감)
  비교: 실험용 깔때기는 목이 3/8" 이하(안 7 아래) → 말벌 못 지나감. 9017T212(윗지름 85.7)는 바닥 모터 153과 겹침
가공 (산 것을 자르기만):
  - 윗테두리를 잘라 윗지름 61 (지금 자리 그대로 — 그보다 크면 바닥 모터 귀(x 34)에 닿음) → 원뿔 높이 37.4 [가능성 높음 — 원뿔 기울기 0.625를 판매처 치수에서 계산]
  - 목을 5 mm만 남기고 자름 (입구 게이트 G1 z 260부터를 피함)
  - 목 ↔ PVC 13A는 맞대고 열수축 튜브 Ø25 (2:1) 20 mm로 감쌈 (목 바깥 14.3, PVC 바깥 18 — 서로 안 들어감) → 안쪽 턱 12.2 → 13 (0.4)
모양은 단순 원뿔 (레포는 공개라 McMaster STEP을 넣지 않음). 벽 두께 1.5 [추측 — 판매처 표에 없음]
"""
import FreeCAD as App
import Part

V = App.Vector
F = dict(top_r=30.5, neck_or=7.15, neck_ir=6.1, cone_h=37.4, neck_L=5.0, wall=1.5)
HS = dict(L=20.0, t=0.5)                 # 열수축 튜브 (수축 뒤 두께 [추측])
JOBS = (  # (깔때기 라벨, 축 x, 넓은 끝 z, 방향(+1: 위로 좁아짐), 관 라벨, 열수축 라벨)
    ("111_entry_funnel", 0.0, 205.0, +1, "110_entry_duct", "111h_heat_shrink"),
    ("173_isolation_funnel", 1.5, None, -1, "172_isolation_duct", "173h_heat_shrink"),
)
LABEL = {
    "111_entry_funnel": "111_entry_funnel (McMaster 9017T211 PP 깔때기 — 윗테 잘라 Ø61, 목 5 남김, 구매)",
    "173_isolation_funnel": "173_isolation_funnel (McMaster 9017T211 PP 깔때기 — 윗테 잘라 Ø61, 목 5 남김, 구매)",
    "111h_heat_shrink": "111h_heat_shrink (열수축 튜브 Ø25 2:1, 20 mm — 깔때기 목 ↔ PVC, 구매)",
    "173h_heat_shrink": "173h_heat_shrink (열수축 튜브 Ø25 2:1, 20 mm — PVC ↔ 깔때기 목, 구매)",
}


def funnel(ax, z_neck_end, d):
    """d = +1: 목이 위(z_neck_end가 목 위 끝), 원뿔은 아래로 넓어짐. d = −1: 목이 아래(z_neck_end가 목 아래 끝)"""
    f = F
    zj = z_neck_end - d * f["neck_L"]                     # 목 ↔ 원뿔
    zw = zj - d * f["cone_h"]                             # 넓은 끝
    neck = Part.makeCylinder(f["neck_or"], f["neck_L"], V(ax, 0, min(zj, z_neck_end)))
    neck = neck.cut(Part.makeCylinder(f["neck_ir"], f["neck_L"] + 2, V(ax, 0, min(zj, z_neck_end) - 1)))
    zlo, zhi = min(zj, zw), max(zj, zw)
    r_lo, r_hi = (f["top_r"], f["neck_or"]) if d > 0 else (f["neck_or"], f["top_r"])
    outer = Part.makeCone(r_lo, r_hi, zhi - zlo, V(ax, 0, zlo))
    inner = Part.makeCone(r_lo - f["wall"], r_hi - f["wall"], zhi - zlo + 0.02, V(ax, 0, zlo - 0.01))
    inner = inner.fuse(Part.makeCylinder(f["neck_ir"], zhi - zlo + 2, V(ax, 0, zlo - 1)))
    return neck.fuse(outer.cut(inner)).removeSplitter(), zw


def heat_shrink(ax, zj, d):
    """맞댄 곳 zj 둘레: 관 쪽(바깥 9) 10 + 목 쪽(바깥 7.15) 10"""
    t = HS["t"]
    h = HS["L"] / 2
    if d > 0:      # 목이 위 → 관은 위
        p = Part.makeCylinder(9.0 + t, h, V(ax, 0, zj)).cut(Part.makeCylinder(9.0, h + 1, V(ax, 0, zj - 0.5)))
        n = Part.makeCylinder(F["neck_or"] + t, h, V(ax, 0, zj - h)).cut(Part.makeCylinder(F["neck_or"], h + 1, V(ax, 0, zj - h - 0.5)))
    else:
        p = Part.makeCylinder(9.0 + t, h, V(ax, 0, zj - h)).cut(Part.makeCylinder(9.0, h + 1, V(ax, 0, zj - h - 0.5)))
        n = Part.makeCylinder(F["neck_or"] + t, h, V(ax, 0, zj)).cut(Part.makeCylinder(F["neck_or"], h + 1, V(ax, 0, zj - 0.5)))
    ring = Part.makeCylinder(9.0 + t, t, V(ax, 0, zj - t / 2)).cut(Part.makeCylinder(F["neck_ir"], 2, V(ax, 0, zj - 1)))
    return p.fuse(n).fuse(ring).removeSplitter()


def apply(doc):
    rep, made = {}, []
    for flab, ax, z_wide, d, plab, hlab in JOBS:
        fo = [o for o in doc.Objects if o.Label.startswith(flab)][0]
        po = [o for o in doc.Objects if o.Label.startswith(plab)][0]
        pb = po.Shape.BoundBox
        if d > 0:              # 111: 넓은 끝 z 205 → 목 위 끝 = 관 아래 끝
            zj = z_wide + F["cone_h"] + F["neck_L"]
            shp, _ = funnel(ax, zj, d)
            po.Shape = po.Shape.common(Part.makeBox(400, 400, 1000, V(-200, -200, zj)))   # 관 아래를 깔때기 목 끝까지 자름
        else:                  # 173: 관 위 끝 = 목 아래 끝
            zj = pb.ZMax
            shp, _ = funnel(ax, zj, d)
        fo.Shape, fo.Label = shp, LABEL[flab]
        for x in [x for x in doc.Objects if x.Label.startswith(hlab)]:
            doc.removeObject(x.Name)
        h = doc.addObject("Part::Feature", "HS_" + hlab.split("_")[0])
        h.Label, h.Shape = LABEL[hlab], heat_shrink(ax, zj, d)
        L = round(po.Shape.BoundBox.ZLength)
        po.Label = po.Label.replace("%d mm 자름" % round(pb.ZLength), "%d mm 자름" % L) if "mm 자름" in po.Label else po.Label
        rep[flab] = dict(joint_z=round(zj, 1), funnel_z=[round(shp.BoundBox.ZMin, 1), round(shp.BoundBox.ZMax, 1)], pipe_L=L)
        made += [fo, h, po]
    doc.recompute()
    return made, rep


def check(doc, made):
    allow = (("111h", "110_"), ("111h", "111_"), ("173h", "172_"), ("173h", "173_"))
    hits = []
    for a in made:
        for o in doc.Objects:
            if o is a or o.TypeId != "Part::Feature" or o.Shape.isNull() or "beam" in o.Label:
                continue
            if not a.Shape.BoundBox.intersect(o.Shape.BoundBox) or (o in made and o.Name < a.Name):
                continue
            ka, kb = a.Label.split(" ")[0], o.Label.split(" ")[0]
            try:
                v = sum(s.common(o.Shape).Volume for s in a.Shape.Solids if s.BoundBox.intersect(o.Shape.BoundBox))
            except Exception as e:
                hits.append((ka, kb, "ERR %s" % e, "확인"))
                continue
            if v > 0.05:
                ok = any((ka.startswith(p) and kb.startswith(q)) or (kb.startswith(p) and ka.startswith(q)) for p, q in allow)
                hits.append((ka, kb, round(v, 2), "허용" if ok else "문제"))
    return hits
