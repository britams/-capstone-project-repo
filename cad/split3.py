# -*- coding: utf-8 -*-
"""전체 모델을 3부분으로 나눠 저장 + 마지막에 링크로 조립 (서현, 2026-11-11, CAP-AI-62)

서현 지시 (11/11 23:27): "급이부, 마킹부, 프레임 및 회로로 나누어서 보자. 캐드 용량이 줄어 오류가 줄 것.
각각 수정을 다 마치면 그 세 개를 마지막에 어셈."
경계 (서현 답): 벌이 지나는 길(통로·문·게이트 센서·바닥 승강·누름)은 마킹부.

  S1_급이부      142·143·144 (물길·뚜껑·솜·병·펌프·관·버림통·걸이와 그 볼트)
  S2_마킹부      104, 110~176 (통로·문·마킹실·격자·바닥 승강·누름·스프링), 196_gate·199b~e (게이트 센서·받침),
                 200~227 (마커 XY·원점 스위치), REF_hornet 등 말벌·마킹 참고
  S3_프레임회로  100~105 (2020 프레임·브래킷·볼트·데크·위판), 180~199 (카메라·Pi·UNO·ULN·와고·비상 정지·MOSFET),
                 REF_trap* (산 상용 트랩 — 조립도에 늘 같이)

세 파일 모두 같은 원점(전체 모델 좌표)을 쓴다 → 조립 S0은 위치를 옮기지 않고 링크만 건다.
쓰는 법:
  1) 따로 띄운 freecad.exe: split3_build.py (G.make() → export, 색 그대로 복사) — 쓰는 창이 멈추지 않게
  2) (색을 다시 넣을 때만) GUI: import split3 as S; S.color_all(folder)
  3) 경계 검사: S.boundary_check(folder) — 서로 다른 부분끼리만, 상자 겹치는 쌍만 (모든 쌍 거리 계산 금지 — 11/11 FreeCAD 멈춤)
"""
import json
import os

import FreeCAD as App

NAMES = ("S1_급이부", "S2_마킹부", "S3_프레임회로")
ASM = "S0_전체조립"
GATE_HOLD = ("199b", "199c", "199d", "199e")
# 헤드리스에서 잃는 투명도 (GUI에서 다시 넣음)
TRANSP = (("REF_trap", 60), ("130_grid", 50), ("144h", 35), ("REF_camera_view", 80), ("196_gate", 70))


def group_of(label):
    """0 급이 · 1 마킹 · 2 프레임회로 · None 모름 (모르면 보고해서 표를 고친다)"""
    p = label.split(" ")[0]
    if p.startswith(("142", "143", "144")):
        return 0
    if p.startswith("REF_trap"):
        return 2
    if p.startswith("REF_"):
        return 1
    if p.startswith("196_gate") or p.startswith(GATE_HOLD):
        return 1
    if not p[:3].isdigit():
        return None
    n = int(p[:3])
    if n == 104 or 110 <= n <= 176 or 200 <= n <= 227:
        return 1
    if 100 <= n <= 105 or 180 <= n <= 199:
        return 2
    return None


def _solid_objects(doc):
    for o in doc.Objects:
        if o.TypeId in ("App::DocumentObjectGroup", "App::Part", "App::Link") or not hasattr(o, "Shape"):
            continue
        if o.Shape.isNull() or not o.Shape.Solids:         # (11/12) 원점 평면(XZ-평면 등) 같은 고체 없는 것 빼기
            continue
        yield o


def export(doc, folder):
    """doc의 모양을 세 파일로 복사해 저장하고 S0 조립 파일을 만든다. 보고 dict를 돌려줌."""
    os.makedirs(folder, exist_ok=True)
    subs, parts = [], []
    for nm in NAMES:
        if nm in App.listDocuments():
            App.closeDocument(nm)
        d = App.newDocument(nm)
        pt = d.addObject("App::Part", "Part")
        pt.Label = nm
        subs.append(d)
        parts.append(pt)
    rep = dict(count=[0, 0, 0], unknown=[], volume_cm3=[0.0, 0.0, 0.0], files={})
    for o in _solid_objects(doc):
        g = group_of(o.Label)
        if g is None:
            rep["unknown"].append(o.Label.split(" ")[0])
            continue
        c = subs[g].addObject("Part::Feature", o.Name)
        c.Label = o.Label
        c.Shape = o.Shape.copy()
        parts[g].addObject(c)
        if App.GuiUp and o.ViewObject and c.ViewObject:      # 색·투명도·숨김 그대로
            for k in ("ShapeColor", "LineColor", "Transparency", "Visibility"):
                try:
                    setattr(c.ViewObject, k, getattr(o.ViewObject, k))
                except Exception:
                    pass
        rep["count"][g] += 1
        try:
            rep["volume_cm3"][g] += o.Shape.Volume / 1000
        except Exception:
            pass
    for d in subs:
        d.recompute()
        f = os.path.join(folder, d.Name + ".FCStd")
        d.saveAs(f)
        rep["files"][d.Name] = round(os.path.getsize(f) / 1e6, 2)
    rep["files"][ASM] = make_asm(folder, subs, parts)
    rep["volume_cm3"] = [round(v, 1) for v in rep["volume_cm3"]]
    return rep


def make_asm(folder, subs=None, parts=None):
    """S0: 세 파일의 App::Part를 링크로 건다 (옮기지 않음). 조립 문서를 먼저 저장해야 다른 문서로 링크가 걸림 (11/11 오류)."""
    if subs is None:
        subs = [App.getDocument(nm) if nm in App.listDocuments() else App.openDocument(os.path.join(folder, nm + ".FCStd")) for nm in NAMES]
        parts = [d.getObject("Part") for d in subs]
    if ASM in App.listDocuments():
        App.closeDocument(ASM)
    a = App.newDocument(ASM)
    fa = os.path.join(folder, ASM + ".FCStd")
    a.saveAs(fa)
    for d, pt in zip(subs, parts):
        lk = a.addObject("App::Link", "L_" + d.Name.split("_")[0])
        lk.Label = d.Name
        lk.LinkedObject = pt
        lk.LinkTransform = True
    a.recompute()
    a.save()
    return round(os.path.getsize(fa) / 1e6, 2)


def color_doc(d):
    """GUI에서: 프린트 = 파랑, 그 밖 = 회색 (D5g_print_color 규칙) + 투명도.
    PCOL.apply는 App::Part(모양 있음, 색 없음)에서 오류 → 부품만 골라 같은 규칙으로 (11/11)"""
    import D5g_print_color as PCOL
    rep = dict(printed=[], missing=[])
    for o in _solid_objects(d):
        head, ko, pr, spec = PCOL.is_print(o.Label)
        if head is None:
            rep["missing"].append(o.Label.split(" ")[0])
        if pr:
            rep["printed"].append(o.Label.split(" ")[0])
        if not App.GuiUp or not getattr(o, "ViewObject", None):
            continue
        t = 0
        for head_, tt in TRANSP:
            if o.Label.startswith(head_):
                t = tt
        for k, v in (("ShapeColor", PCOL.PRINT if pr else PCOL.OTHER),
                     ("LineColor", (0.10, 0.20, 0.45) if pr else (0.35, 0.35, 0.38)), ("Transparency", t)):
            try:                      # 보기 객체 종류에 따라 없는 속성이 있음 (FreeCAD 1.1, 11/11)
                setattr(o.ViewObject, k, v)
            except Exception:
                pass
    return rep


def color_all(folder):
    out = {}
    for nm in NAMES:
        d = App.openDocument(os.path.join(folder, nm + ".FCStd"))
        r = color_doc(d)
        out[nm] = dict(printed=len(r["printed"]), missing=sorted(set(r["missing"])))
        d.save()
    return out


def boundary_check(folder, tol=0.5):
    """서로 다른 부분끼리 겹침 (mm³). 상자가 겹치는 쌍만 common을 계산한다."""
    docs = [App.openDocument(os.path.join(folder, nm + ".FCStd")) for nm in NAMES]
    objs = [list(_solid_objects(d)) for d in docs]
    hits = []
    for i in range(3):
        for j in range(i + 1, 3):
            for a in objs[i]:
                ba = a.Shape.BoundBox
                for b in objs[j]:
                    if not ba.intersect(b.Shape.BoundBox):
                        continue
                    try:
                        v = a.Shape.common(b.Shape).Volume
                    except Exception as e:
                        hits.append((a.Label[:40], b.Label[:40], "ERR %s" % e))
                        continue
                    if v > tol:
                        hits.append((a.Label[:40], b.Label[:40], round(v, 1)))
    return hits


def save_json(rep, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1, default=str)


def add_context(doc, folder, margin=40.0):
    """다른 두 파일에서 이 부분 둘레(margin mm) 안에 드는 부품만 복사해 넣음 — 이름은 CTX_ 로 시작, 라벨은 그대로.
    한 부분을 고칠 때 벽·프레임에 부딪히는지 보려고. 고친 뒤 remove_context로 꼭 지운다."""
    bb = None
    for o in _solid_objects(doc):
        bb = o.Shape.BoundBox if bb is None else bb.united(o.Shape.BoundBox)
    bb.enlarge(margin)
    names = []
    for nm in NAMES:
        if nm == doc.Name:
            continue
        opened = nm not in App.listDocuments()
        d = App.openDocument(os.path.join(folder, nm + ".FCStd"), hidden=True) if opened else App.getDocument(nm)
        for o in _solid_objects(d):
            if o.Shape.BoundBox.intersect(bb):
                c = doc.addObject("Part::Feature", "CTX_" + o.Name)
                c.Label = o.Label
                c.Shape = o.Shape.copy()
                names.append(c.Name)
        if opened:
            App.closeDocument(d.Name)
    return names


def remove_context(doc):
    for o in [o for o in doc.Objects if o.Name.startswith("CTX_")]:
        doc.removeObject(o.Name)
    for o in [o for o in doc.Objects if o.TypeId == "Part::Feature" and not o.InList]:   # 고친 단계가 새로 만든 것 → Part 안으로
        pt = doc.getObject("Part")
        if pt:
            pt.addObject(o)


def merge_full(folder, path):
    """전체 도면: 세 파일을 한 문서로 합쳐 저장 (서현 '전체 수정' 때만). 묶음 3개 = 세 부분, 색·투명도 그대로."""
    name = os.path.splitext(os.path.basename(path))[0]
    if name in App.listDocuments():
        App.closeDocument(name)
    full = App.newDocument(name)
    rep = {}
    for nm in NAMES:
        src = App.openDocument(os.path.join(folder, nm + ".FCStd"))
        g = full.addObject("App::DocumentObjectGroup", "G_" + nm.split("_")[0])
        g.Label = nm
        n = 0
        for o in _solid_objects(src):
            c = full.addObject("Part::Feature", o.Name)
            c.Label = o.Label
            c.Shape = o.Shape.copy()
            g.addObject(c)
            if App.GuiUp and o.ViewObject and c.ViewObject:
                for k in ("ShapeColor", "LineColor", "Transparency", "Visibility"):
                    try:
                        setattr(c.ViewObject, k, getattr(o.ViewObject, k))
                    except Exception:
                        pass
            n += 1
        rep[nm] = n
        App.closeDocument(src.Name)
    full.recompute()
    full.saveAs(path)
    rep["MB"] = round(os.path.getsize(path) / 1e6, 2)
    return rep


LIFT = ("140_", "146_", "147_", "148c", "149_", "151_", "152_", "153", "154_", "155", "157", "158_", "159", "121_", "227f", "227p")


def extract(folder, heads=LIFT, name="S2a_바닥구동"):
    """S2에서 바닥 올리는 장치만 떼어 따로 저장 (서현 11/12 04:52 '위로 올리는 부품만 떼어서'). 좌표는 그대로."""
    src = App.openDocument(os.path.join(folder, "S2_마킹부.FCStd"), hidden=True)
    if name in App.listDocuments():
        App.closeDocument(name)
    d = App.newDocument(name)
    for o in _solid_objects(src):
        if o.Label.startswith(heads):
            c = d.addObject("Part::Feature", o.Name)
            c.Label, c.Shape = o.Label, o.Shape.copy()
    App.closeDocument(src.Name)
    color_doc(d)
    d.recompute()
    d.saveAs(os.path.join(folder, name + ".FCStd"))
    return d
