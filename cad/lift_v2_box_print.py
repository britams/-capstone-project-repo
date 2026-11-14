# -*- coding: utf-8 -*-
"""300 마킹실 상자 — 프린트용 부품 파일 따로 (서현 11/14 16:04 "초록 프린트 부분만 프린트 할 수 있게 자세하게 부품 파일로 따로", CAP-AI-62)

모양은 lift_v2.marking_box() 그대로 (조립과 같은 것). 내보냄: cad/print/lift/300_마킹실상자.{step,stl,FCStd} + 그림
프린트: 바닥면(z −10)을 판에, PETG 또는 PLA, 벽 3겹 이상, 채움 40 % 이상 [추측 — 일반 권장]
  문 구멍 Ø13 2개는 옆으로 누운 구멍 → 서포트 켬 (구멍 안만)
  프린트 뒤: M3 열압입 인서트 4개 (구멍 Ø4.0 × 6, 윗면에서 인두로) — 서현이 하는 일은 인서트 넣기와 나사 조이기뿐
붙는 것: 망 Ø33 × 0.5 (턱 Ø33.4 × 0.5) · M3 × 6 + M3 DIN 9021 4 · 뒤 날개 M4 × 10 + M4 DIN 125 + 2020 M4 T너트 2
"""
import os
import FreeCAD as App
import Part
import lift_v2 as L

V = App.Vector


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
    return doc, dict(valid=s.isValid(), solids=len(s.Solids), volume_cm3=round(s.Volume / 1000, 2),
                     size=(round(bb.XLength, 2), round(bb.YLength, 2), round(bb.ZLength, 2)),
                     mesh_facets=m.CountFacets, mesh_solid=m.isSolid(), fillet=len(s.Faces))
