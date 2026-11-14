# -*- coding: utf-8 -*-
"""300 마킹실 상자 (프린트) + 300p 아크릴 격자판 (주문 제작) — 부품 파일 따로 (서현 11/14 16:04 "초록 프린트 부분만 프린트 할 수 있게 자세하게 부품 파일로 따로", CAP-AI-62)

모양은 lift_v2.marking_box() 그대로 (조립과 같은 것). 내보냄: cad/print/lift/300_마킹실상자.{step,stl,FCStd} + 그림
프린트: 윗면(z 8, 평평)을 판에 — 밑 혀가 위로 섬. PETG 또는 PLA, 벽 3겹 이상, 채움 40 % 이상 [추측 — 일반 권장]
  문 구멍 Ø13 2개는 옆으로 누운 구멍 → 서포트 켬 (구멍 안만)
  프린트 뒤: M3 열압입 인서트 4개 (구멍 Ø4.0 × 6, 윗면 (±15.5, ±15.5))
붙는 것: 300p 투명 아크릴 격자판 (주문 제작, 300p_아크릴격자판.dxf) + M3 × 8 + M3 DIN 125 4 · 밑 혀 M5 × 10 + 2020 M5 T너트 2 (세운 2020 +y 홈). 문 구멍 4: −x 입구·+x 방생·−y 격리 Ø13, +y 급이 Ø11.2 (솜 축 따라 기욺)
"""
import os
import FreeCAD as App
import Part
import lift_v2 as L

V = App.Vector


def plate(out_dir):
    """300p 투명 아크릴 격자판 — 주문 제작용 부품 파일 따로: .FCStd · .step (+ .dxf는 lift_plate_dxf.py)"""
    p = L.acrylic_plate()
    base = os.path.join(out_dir, "300p_아크릴격자판")
    p.exportStep(base + ".step")
    d = App.newDocument("P300p_acrylic_plate")
    o = d.addObject("Part::Feature", "P300p")
    o.Shape, o.Label = p, "300p_acrylic_plate (투명 아크릴 2T 40 × 40, 네모 구멍 3.0 간격 4.4 × 37, 나사 구멍 Ø3.4 × 4 — 주문 제작)"
    if App.GuiUp:
        o.ViewObject.ShapeColor = (0.55, 0.75, 0.95)
        o.ViewObject.Transparency = 40
    d.recompute()
    d.saveAs(base + ".FCStd")
    bb = p.BoundBox
    return dict(doc=d.Name, valid=p.isValid(), size=(round(bb.XLength, 2), round(bb.YLength, 2), round(bb.ZLength, 2)),
                holes=len(L.grid_centers()), volume_cm3=round(p.Volume / 1000, 3))


def make(out_dir):
    s = L.marking_box()
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.join(out_dir, "300_마킹실상자")
    s.exportStep(base + ".step")
    import MeshPart
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.2, Relative=False)
    m.write(base + ".stl")
    doc = App.newDocument("P300_marking_box")
    o = doc.addObject("Part::Feature", "P300")
    o.Shape, o.Label = s, "300_marking_box (프린트 1개 — 바닥면을 판에)"
    if App.GuiUp:
        o.ViewObject.ShapeColor = (0.2, 0.7, 0.3)
    doc.recompute()
    doc.saveAs(base + ".FCStd")
    bb = s.BoundBox
    pl = plate(out_dir)
    return doc, dict(plate=pl, valid=s.isValid(), solids=len(s.Solids), volume_cm3=round(s.Volume / 1000, 2),
                     size=(round(bb.XLength, 2), round(bb.YLength, 2), round(bb.ZLength, 2)),
                     mesh_facets=m.CountFacets, mesh_solid=m.isSolid(), fillet=len(s.Faces))
