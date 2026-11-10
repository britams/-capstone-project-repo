# -*- coding: utf-8 -*-
"""3D 프린트 부품만 색 다르게 — 전체 모델 (서현, 2026-11-10, CAP-AI-58)

서현 지시 (11/10 16:14): "CAD 그릴 때 프린트할 부분만 색 다르게 해줄 수 있어? 전체적으로"
규칙:
  - 3D 프린트 = 파랑 (0.20, 0.50, 0.95), 불투명
  - 그 밖(구매품·판 가공·프레임·전기·트랩) = 회색 한 가지 (0.80, 0.80, 0.82), 원래 투명도는 그대로 (트랩·격자는 비침)
  - 이전에는 프린트 = 주황 (SJ-53)이었는데, 황동 인서트·베이지 데크·빨간 기판과 섞여 구분이 안 됐음 → 프린트만 색, 나머지는 회색
판정은 한 곳: D5g_parts_table.py 의 이름 표에서 규격에 '3D 프린트'가 있으면 프린트.
  표에 없는 이름은 프린트 아님으로 두고 보고(missing)에 적음 → 표를 고침.
D5g_frame_detail.make() 끝에서 부름. 열린 문서에 바로 써도 됨: import D5g_print_color as PC; PC.apply(doc)
"""
import FreeCAD as App

PRINT = (0.20, 0.50, 0.95)
OTHER = (0.80, 0.80, 0.82)
PETG = 1.27   # g/cm³ [가능성 높음]


def is_print(label):
    import D5g_parts_table as PT
    head, ko, kind, spec = PT.name_of(label)
    return head, ko, ("3D 프린트" in spec), spec


def apply(doc):
    rep = dict(printed=[], missing=[])
    for o in doc.Objects:
        if not hasattr(o, "Shape") or o.TypeId == "App::DocumentObjectGroup" or o.Shape.isNull():
            continue
        head, ko, pr, spec = is_print(o.Label)
        if head is None:
            rep["missing"].append(o.Label.split(" ")[0])
        if pr:
            bb = o.Shape.BoundBox
            rep["printed"].append(dict(num=head.strip("_"), name=ko, label=o.Label.split(" ")[0], spec=spec,
                                       solids=len(o.Shape.Solids), size=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)],
                                       volume_cm3=round(o.Shape.Volume / 1000, 1), mass_g=round(o.Shape.Volume / 1000 * PETG, 1)))
        if not App.GuiUp or not getattr(o, "ViewObject", None):
            continue
        vo = o.ViewObject
        if pr:
            vo.ShapeColor, vo.Transparency = PRINT, 0
            vo.LineColor = (0.10, 0.20, 0.45)
        else:
            vo.ShapeColor = OTHER
            vo.LineColor = (0.35, 0.35, 0.38)
    return rep


def markdown(rep):
    """프린트 부품 목록 (Craft-Lab에 들고 갈 표)"""
    out = ["| 번호 | 이름 | 모델 이름 | 개수 | 크기 x × y × z (mm, 묶음 전체) | 부피 cm³ | PETG g (꽉 채움) | 메모 |",
           "|---|---|---|---|---|---|---|---|"]
    tot_v = tot_m = 0
    for r in sorted(rep["printed"], key=lambda r: r["label"]):
        out.append("| %s | %s | `%s` | %d | %s | %.1f | %.1f | %s |" % (r["num"], r["name"], r["label"], max(1, r["solids"]),
                   " × ".join("%g" % v for v in r["size"]), r["volume_cm3"], r["mass_g"], r["spec"]))
        tot_v += r["volume_cm3"]; tot_m += r["mass_g"]
    out.append("| | **합계** | | | | **%.1f** | **%.0f** | 실제 출력은 채움 15~30 %%라 이보다 가벼움 |" % (tot_v, tot_m))
    return "\n".join(out)
