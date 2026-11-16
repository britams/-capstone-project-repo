# -*- coding: utf-8 -*-
"""XY 플랫폼만 떼어 따로 설계 → 다시 붙이기 (서현 11/16 18:49 "선형 액추 할 때처럼 부품 떼서 … xy 플레이트 부분 떼어서 수정해. 그리고 나중에 붙여", CAP-AI-62)
  P153m 리니어 모듈(ks_15by25_module.py)처럼 부품 파일 하나로 — 좌표는 조립과 같음 (붙일 때 옮기지 않게).
  XY_MODE=detach (기본): S2에서 XY·스탬핑 부품을 떼어 split/P2xy_XY플랫폼.FCStd (+ 프레임 레일은 REF_로) →
      모터 LM-NK1134를 판매처 도면 모양으로 다시 그림 (상자 → 모서리 깎인 28각 · 앞뒤 알루미늄 뚜껑 · 앞 M2.6 구멍 4 · 뒤 단자)
      → 부품 파일 안 겹침 검사 → 그림 4장 cad/img/parts/xy/P2xy_*.png → split/_xy_platform.json
  XY_MODE=attach: P2xy의 REF_ 아닌 물체 모양을 S2의 같은 이름(머리말 "번호_이름") 물체에 넣고 저장 → split/_xy_attach.json
  freecad.exe cad/xy_platform.py (cwd = cad, 창 있어야 그림) — 끝에 os._exit (서현 GUI에서 돌리지 말 것)"""
import json, os, sys, traceback, math
HERE = os.getcwd(); OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
IMG = os.path.join(HERE, "img", "parts", "xy")
MODE = os.environ.get("XY_MODE", "detach")
NAME = "P2xy_XY플랫폼"
PRE = ("201_", "202_", "203_", "205", "206_", "207_", "208_", "209_", "211_", "212_", "213_", "214_", "215_", "217_", "218_", "221_",
       "222_", "224_", "225_", "226p", "226s", "227x", "227y", "153b_stepper_bolts")
REFS = ("100b_rail_gantry", "100d_gantry_rail")
rep = dict(mode=MODE, hits=[])


def key(label):
    return label.split(" (")[0].split(" —")[0].strip()


def lm1134(c, n, face):
    """LM-NK1134 몸 (나사 빼고) — 28각 모서리 깎음 C3 [추측 — NEMA11 사진], 앞 뚜껑 5 · 뒤 뚜껑 5 알루미늄 (몸 28, 철심 27.4), 턱 Ø22 × 2,
    앞 M2.6 구멍 23 × 23 깊이 3.5, 뒤 단자 6 × 14 × 5 [추측] — 전체 길이 34 [가능성 높음 — 판매처 도면]"""
    import FreeCAD as App, Part
    V = App.Vector

    def sq(a, z0, z1, ch):
        h = a / 2
        pts = [V(-h + ch, -h, 0), V(h - ch, -h, 0), V(h, -h + ch, 0), V(h, h - ch, 0), V(h - ch, h, 0), V(-h + ch, h, 0), V(-h, h - ch, 0), V(-h, -h + ch, 0)]
        f = Part.Face(Part.makePolygon(pts + [pts[0]]))
        s = f.extrude(V(0, 0, z1 - z0)); s.translate(V(0, 0, z0))
        return s
    m = sq(28.0, -5.0, 0.0, 3.0).fuse(sq(27.4, -29.0, -5.0, 3.3)).fuse(sq(28.0, -34.0, -29.0, 3.0))
    m = m.fuse(Part.makeCylinder(11.0, 2.0, V(0, 0, 0)))
    for a in (-11.5, 11.5):
        for b in (-11.5, 11.5):
            m = m.cut(Part.makeCylinder(1.3, 3.5, V(a, b, -3.5)))
    m = m.fuse(Part.makeBox(14, 6, 5, V(-7, 14 - 0.5, -33)))       # 뒤 단자 (한쪽 옆)
    m = m.removeSplitter()
    m.Placement = App.Placement(c + n * (face - c.dot(n)), App.Rotation(V(0, 0, 1), n))
    return m


try:
    import FreeCAD as App, Part
    V = App.Vector
    if MODE == "detach":
        import FreeCADGui as Gui
        import split3 as S
        src = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"), True)
        s3 = App.openDocument(os.path.join(OUT, "S3_프레임회로.FCStd"), True)
        if NAME in App.listDocuments():
            App.closeDocument(NAME)
        doc = App.newDocument(NAME)
        n = 0
        for o in src.Objects:
            if o.TypeId.startswith("Part::") and not o.Shape.isNull() and o.Label.startswith(PRE):
                p = doc.addObject("Part::Feature", "XY%03d" % n); p.Shape = o.Shape.copy(); p.Label = o.Label; n += 1
        for o in s3.Objects:
            if o.TypeId.startswith("Part::") and o.Label.startswith(REFS):
                p = doc.addObject("Part::Feature", "REF%03d" % n); p.Shape = o.Shape.copy(); p.Label = "REF_" + o.Label; n += 1
        App.closeDocument(src.Name); App.closeDocument(s3.Name)
        rep["objects"] = n
        # 모터 다시 그림 (같은 자리: X 앞면 x 160 · 나사 −x / Y 앞면 y −101.9 · 나사 +y)
        for lab, c, nn, face in (("215_x_stepper", V(0, -65.0, 425.0), V(-1, 0, 0), -160.0), ("209_y_stepper", V(101.4, 0, 453.0), V(0, 1, 0), -101.9)):
            o = [x for x in doc.Objects if x.Label.startswith(lab)][0]
            old = o.Shape.BoundBox
            o.Shape = lm1134(c, nn, face)
            nb = o.Shape.BoundBox
            rep[lab] = [[round(v, 1) for v in (old.XMin, old.XMax, old.YMin, old.YMax, old.ZMin, old.ZMax)],
                        [round(v, 1) for v in (nb.XMin, nb.XMax, nb.YMin, nb.YMax, nb.ZMin, nb.ZMax)]]
            if "모서리" not in o.Label:
                o.Label = o.Label.replace("몸 28 × 28 × 34", "몸 28 × 28 × 34 (모서리 C3 · 앞뒤 뚜껑 · 뒤 단자 [추측])")
        doc.recompute()
        S.color_doc(doc)
        for o in doc.Objects:
            if o.Label.startswith("REF_"):
                o.ViewObject.ShapeColor = (0.75, 0.75, 0.75); o.ViewObject.Transparency = 60
        # 부품 파일 안 겹침 (모터만, 붙어야 하는 판·나사·볼트 빼고)
        ok = ("211_y_motor_plate", "217_x_motor_plate", "153b", "208_y_lead", "214_x_lead")
        for m in [x for x in doc.Objects if x.Label.startswith(("215_x_stepper", "209_y_stepper"))]:
            for o in doc.Objects:
                if o is m or o.Label.startswith(ok):
                    continue
                if m.Shape.BoundBox.intersect(o.Shape.BoundBox):
                    v = m.Shape.common(o.Shape).Volume
                    if v > 0.05:
                        rep["hits"].append([m.Label[:40], o.Label[:40], round(v, 1)])
        doc.saveAs(os.path.join(OUT, NAME + ".FCStd"))
        # 그림
        os.makedirs(IMG, exist_ok=True)
        App.ParamGet("User parameter:BaseApp/Preferences/View").SetBool("UseNavigationAnimations", False)
        v = Gui.activeDocument().activeView(); v.setCameraType("Orthographic")
        from PIL import Image, ImageDraw, ImageFont
        F = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 36)
        shots = []
        for nm, kind, t in (("등각", "viewIsometric", "등각"), ("정면", "viewFront", "정면 (−y에서 봄)"), ("위", "viewTop", "위"), ("옆", "viewRight", "옆 (+x에서 봄)")):
            getattr(v, kind)(); v.fitAll(); Gui.updateGui()
            p = os.path.join(IMG, "P2xy_%s.png" % nm)
            v.saveImage(p, 2000, 1500, "White")
            im = Image.open(p).convert("RGB"); d = ImageDraw.Draw(im)
            title = "P2xy XY 플랫폼 — %s · 모터 LM-NK1134 (나사 일체형) · 파랑 = 레이저, 회색 = 사는 것, 옅은 회색 = 프레임 레일(참고)" % t
            d.rectangle([15, 15, 40 + d.textlength(title, font=F), 70], fill=(255, 255, 255)); d.text((28, 22), title, fill=(20, 20, 20), font=F)
            im.save(p); shots.append(os.path.basename(p))
        rep["img"] = shots
        App.closeDocument(doc.Name)
    else:
        part = App.openDocument(os.path.join(OUT, NAME + ".FCStd"), True)
        s2 = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
        by = {}
        for o in s2.Objects:
            if o.TypeId.startswith("Part::") and o.Label.startswith(PRE):
                by.setdefault(key(o.Label), []).append(o)
        done, miss, added, removed = 0, [], [], []
        labels_new = lambda L: L
        for p in part.Objects:
            if not p.TypeId.startswith("Part::") or p.Label.startswith("REF_"):
                continue
            tg = [o for o in by.get(key(p.Label), []) if o.Label == p.Label] or by.get(key(p.Label), [])
            if len(tg) == 0:                       # 부품 파일에서 새로 생긴 것 → S2에 더함
                n = s2.addObject("Part::Feature", "XYn%d" % len(s2.Objects)); n.Shape = p.Shape.copy(); n.Label = p.Label; added.append(p.Label[:50]); continue
            if len(tg) != 1:
                miss.append([p.Label[:50], len(tg)]); continue
            tg[0].Shape = p.Shape.copy(); tg[0].Label = p.Label; done += 1
        labs = set(p.Label for p in part.Objects if p.TypeId.startswith("Part::") and not p.Label.startswith("REF_"))
        for o in list(s2.Objects):                  # 부품 파일에서 지운 것 → S2에서도 지움
            if o.TypeId.startswith("Part::") and o.Label.startswith(PRE) and o.Label not in labels_new(labs):
                removed.append(o.Label[:50]); s2.removeObject(o.Name)
        s2.save()
        rep["attached"] = done; rep["miss"] = miss; rep["added"] = added; rep["removed"] = removed
        App.closeDocument(part.Name); App.closeDocument(s2.Name)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_xy_platform.json" if MODE == "detach" else "_xy_attach.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
