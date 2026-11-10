# -*- coding: utf-8 -*-
"""급이 방 상세 그림 — 조립(등각)·분해(등각)·부품표 (서현, 2026-11-10, CAP-AI-57)

FreeCAD GUI 매크로 (saveImage는 화면 필요). D5g_render.py와 같은 방식:
    set D5G_FILE=<repo>\\cad\\D5g_full.FCStd
    "C:\\Program Files\\FreeCAD 1.1\\bin\\freecad.exe" cad\\D5g_feeder_render.py
결과: cad/img/D5g_급이방_조립.png, cad/img/D5g_급이방_분해.png (정투영, 애니메이션 끔, 글자는 Pillow·맑은 고딕)
"""
import os, json
import FreeCAD as App
import FreeCADGui as Gui

REPO = os.environ.get("D5G_REPO", r"C:\capstone\-capstone-project-repo")
FN = os.environ.get("D5G_FILE", os.path.join(REPO, "cad", "D5g_full.FCStd"))
OUT = os.path.join(REPO, "cad", "img")
FONT = r"C:\Windows\Fonts\malgun.ttf"
W, H = 2400, 1800
V = App.Vector

# (머리말, 분해 방향·거리, 그림 번호, 이름)
PARTS = [
    ("143_feed_trough", V(0, 0, 0), "1", "물길·그릇·기둥·집게 143 (PETG 3D 프린트, 앞벽 솜 구멍)"),
    ("143l_", V(0, 0, 70), "2", "뚜껑 143l (PETG)"),
    ("143t_", V(0, 0, 110), "3", "손나사 M3 × 8 — McMaster 92545A111 × 4"),
    ("143i_", V(0, 0, 35), "4", "열 압입 인서트 M3 — McMaster 94459A130 × 4"),
    ("144n_", V(0, 0, 150), "5", "15 mL 원뿔 튜브 — 코닝 352096 × 1"),
    ("142n_", V(0, -35, 0), "6", "코튼롤 2호 Ø10 × 38 (치과 재료) × 1"),
    ("143fi_", V(0, 0, 25), "7", "발 인서트 M3 — McMaster 94459A130 × 2"),
    ("143f_screw", V(0, 0, -45), "8", "냄비머리 M3 × 8 (데크 아래에서) — McMaster 92000A118 × 2"),
    ("101_deck", V(0, 0, 0), "", ""),
    ("100c_cross_deck_yp80", V(0, 0, 0), "", ""),
    ("120_chamber_walls", V(0, 0, 0), "", ""),
]
BOX = (15, 120, 40, 125, 185, 500)   # 급이 방 둘레


def setup():
    App.ParamGet("User parameter:BaseApp/Preferences/View").SetBool("UseNavigationAnimations", False)
    doc = App.openDocument(FN)
    Gui.activeDocument().activeView().setCameraType("Orthographic")
    return doc


def pick(doc, pre):
    if pre == "100c_cross_deck_yp80":
        return [o for o in doc.Objects if o.Name == "P100c_cross_deck_yp80"]
    return [o for o in doc.Objects if o.Label.startswith(pre) and hasattr(o, "Shape")]


def shoot(doc, name, explode):
    v = Gui.activeDocument().activeView()
    show = {}
    for pre, d, n, _ in PARTS:
        for o in pick(doc, pre):
            show[o.Name] = (d if explode else V(0, 0, 0), n)
    for o in doc.Objects:
        if getattr(o, "ViewObject", None):
            o.ViewObject.Visibility = o.Name in show
    moved = []
    for nm, (d, n) in show.items():
        o = doc.getObject(nm)
        if d.Length > 0:
            o.Placement.Base = o.Placement.Base + d
            moved.append((o, d))
        if o.Label.startswith(("101_deck", "100c_", "120_")):
            o.ViewObject.Transparency = 75
    v.viewIsometric()
    v.fitAll()
    Gui.updateGui()
    vw, vh = v.getSize()
    k = max(W / vw, H / vh)
    tags = []
    for pre, d, n, txt in PARTS:
        if not n:
            continue
        for o in pick(doc, pre)[:1]:
            c = o.Shape.BoundBox.Center
            sx, sy = v.getPointOnViewport(c)
            tags.append(((W / 2 + (sx - vw / 2) * k, H / 2 - (sy - vh / 2) * k), n, txt))
    path = os.path.join(OUT, name + ".png")
    v.saveImage(path, W, H, "White")
    for o, d in moved:
        o.Placement.Base = o.Placement.Base - d
    return path, tags


def annotate(path, title, tags, note):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open(path).convert("RGB")
    dr = ImageDraw.Draw(im)
    f1, f2, f3 = ImageFont.truetype(FONT, 46), ImageFont.truetype(FONT, 30), ImageFont.truetype(FONT, 34)
    dr.text((40, 30), title, fill=(0, 0, 0), font=f1)
    dr.text((40, 95), note, fill=(80, 80, 80), font=f2)
    for (x, y), n, _ in tags:
        bx, by = x + 90, y - 90
        dr.line([(x, y), (bx, by)], fill=(200, 30, 30), width=3)
        dr.ellipse([bx - 26, by - 26, bx + 26, by + 26], fill=(255, 255, 255), outline=(200, 30, 30), width=4)
        dr.text((bx, by), n, fill=(200, 30, 30), font=f3, anchor="mm")
    y0 = H - 40 - 44 * len(tags)
    dr.rectangle([30, y0 - 20, 1300, H - 25], fill=(255, 255, 255), outline=(120, 120, 120), width=2)
    for i, (_, n, txt) in enumerate(tags):
        dr.text((50, y0 + 44 * i), "%s  %s" % (n, txt), fill=(0, 0, 0), font=f2)
    im.save(path)


def run():
    doc = setup()
    done = []
    for name, ex, title in (("D5g_급이방_조립", False, "급이 방 상세 — 조립 (등각, 정투영)"),
                            ("D5g_급이방_분해", True, "급이 방 상세 — 분해 (등각, 정투영) · 나사 = McMaster STEP")):
        p, tags = shoot(doc, name, ex)
        annotate(p, title, tags, "데크·가로대·마킹실 벽은 반투명 · 단위 mm · CAP-AI-57")
        done.append(p)
    json.dump(done, open(os.path.join(OUT, "_feeder_render_done.json"), "w", encoding="utf-8"), ensure_ascii=False)


try:
    run()
except Exception:
    import traceback
    open(os.path.join(OUT, "_feeder_render_error.txt"), "w", encoding="utf-8").write(traceback.format_exc())
os._exit(0)
