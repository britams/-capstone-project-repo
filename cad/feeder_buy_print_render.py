# -*- coding: utf-8 -*-
"""급이 방 — '사는 것 vs 3D 프린트' 색 구분 분해 그림 (서현, 2026-11-10, CAP-AI-58)

서현 질문 (11/10 16:04): "어떤 것이 솜이고 내가 사야 하는 부분과 3D 프린터로 뽑아야 되는 부품을 나눠줘"
GUI 매크로:  "C:\\Program Files\\FreeCAD 1.1\\bin\\freecad.exe" cad\\feeder_buy_print_render.py
결과: cad/img/parts/feeder/급이방_사는것_프린트.png
"""
import os, json
import FreeCAD as App
import FreeCADGui as Gui
import Part

REPO = os.environ.get("D5G_REPO", r"C:\capstone\-capstone-project-repo")
ASM = os.path.join(REPO, "cad", "parts", "feeder", "A143_급이방_조립.FCStd")
OUT = os.path.join(REPO, "cad", "img", "parts", "feeder")
FONT = r"C:\Windows\Fonts\malgun.ttf"
FONTB = r"C:\Windows\Fonts\malgunbd.ttf"
W, H = 2600, 2000
V = App.Vector
PRINT, BUY, COTTON = (0.20, 0.50, 0.95), (0.95, 0.55, 0.15), (1.0, 0.95, 0.30)

# (링크 이름 머리, 분해 이동, 색, 번호, 설명) — 번호 1~2 = 프린트, 3~ = 구매
ITEMS = [
    ("L_143", V(0, 0, 0), PRINT, "1", "물길·그릇·기둥 (143) — 3D 프린트 PETG, 1개"),
    ("L_143l", V(0, 0, 45), PRINT, "2", "뚜껑 (143l) — 3D 프린트 PETG, 1개"),
    ("L_142n", V(0, -45, 0), COTTON, "3", "솜 = 코튼롤 2호 Ø10 × 38 (치과 재료) — 구매, 갈아 끼움"),
    ("L_144n", V(0, 0, 95), BUY, "4", "15 mL 원뿔 튜브 (코닝 352096) — 구매, 설탕물 넣고 거꾸로 꽂음"),
    ("L_143i", V(0, 0, 25), BUY, "5", "열 압입 인서트 M3 (McMaster 94459A130) — 구매 6개 (뚜껑 4 + 발 2)"),
    ("L_143t", V(0, 0, 70), BUY, "6", "손나사 M3 × 8 (McMaster 92545A111) — 구매 4개, 손으로 돌림"),
    ("L_143fi", V(0, 0, -15), BUY, "", ""),
    ("L_143f_", V(0, 0, -45), BUY, "7", "냄비머리 나사 M3 × 8 (McMaster 92000A118) — 구매 2개, 데크 아래에서"),
]


def run():
    App.ParamGet("User parameter:BaseApp/Preferences/View").SetBool("UseNavigationAnimations", False)
    src = App.openDocument(ASM)
    doc = App.newDocument("view_tmp")
    Gui.activeDocument().activeView().setCameraType("Orthographic")
    first = {}
    for o in src.Objects:
        if o.TypeId != "App::Link":
            continue
        for pre, d, col, n, txt in ITEMS:
            if o.Name.startswith(pre) and not (pre == "L_143" and o.Name != "L_143") and not (pre == "L_143f_" and o.Name.startswith("L_143fi")):
                s = Part.getShape(o).copy()
                s.translate(d)
                f = doc.addObject("Part::Feature", o.Name)
                f.Shape = s
                f.ViewObject.ShapeColor = col
                f.ViewObject.LineColor = (0.2, 0.2, 0.2)
                if n and n not in first:
                    first[n] = f
                break
    doc.recompute()
    v = Gui.activeDocument().activeView()
    v.viewIsometric(); v.fitAll(); Gui.updateGui()
    vw, vh = v.getSize()
    k = max(W / vw, H / vh)
    tags = []
    for pre, d, col, n, txt in ITEMS:
        if n and n in first:
            sh = first[n].Shape
            c = sh.BoundBox.Center
            sx, sy = v.getPointOnViewport(c)
            tags.append(((W / 2 + (sx - vw / 2) * k, H / 2 - (sy - vh / 2) * k), n, txt, col))
    path = os.path.join(OUT, "급이방_사는것_프린트.png")
    v.saveImage(path, W, H, "White")
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open(path).convert("RGB")
    dr = ImageDraw.Draw(im)
    f1, f2, f3 = ImageFont.truetype(FONTB, 50), ImageFont.truetype(FONT, 32), ImageFont.truetype(FONTB, 38)
    dr.text((40, 30), "급이 방 — 파란색 = 3D 프린트로 뽑음 · 주황 = 사는 것 · 노란색 = 솜", fill=(0, 0, 0), font=f1)
    dr.text((40, 100), "분해 그림 (위로·옆으로 띄워 놓음). 실제로는 모두 제자리에 끼워짐 · 단위 mm", fill=(90, 90, 90), font=f2)
    for (x, y), n, _, col in tags:
        bx, by = x + 110, y - 100
        dr.line([(x, y), (bx, by)], fill=(30, 30, 30), width=3)
        c = tuple(int(255 * t) for t in col)
        dr.ellipse([bx - 30, by - 30, bx + 30, by + 30], fill=c, outline=(30, 30, 30), width=4)
        dr.text((bx, by), n, fill=(0, 0, 0), font=f3, anchor="mm")
    x0, y0 = 1560, 260                       # 표는 오른쪽 위 (아래에 두면 발 나사를 가림)
    f4 = ImageFont.truetype(FONT, 28)
    dr.rectangle([x0 - 20, y0 - 25, W - 20, y0 + 92 * len(tags) + 10], fill=(255, 255, 255), outline=(120, 120, 120), width=2)
    for i, (_, n, txt, col) in enumerate(tags):
        c = tuple(int(255 * t) for t in col)
        yy = y0 + 92 * i
        dr.rectangle([x0, yy + 4, x0 + 32, yy + 36], fill=c, outline=(30, 30, 30), width=2)
        a, _, b = txt.partition(" — ")
        dr.text((x0 + 50, yy), "%s  %s" % (n, a), fill=(0, 0, 0), font=f4)
        dr.text((x0 + 90, yy + 40), b, fill=(80, 80, 80), font=f4)
    im.save(path)
    json.dump([path], open(os.path.join(OUT, "_bp_done.json"), "w", encoding="utf-8"), ensure_ascii=False)


try:
    run()
except Exception:
    import traceback
    open(os.path.join(OUT, "_bp_error.txt"), "w", encoding="utf-8").write(traceback.format_exc())
os._exit(0)
