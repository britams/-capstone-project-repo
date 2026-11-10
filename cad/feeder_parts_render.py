# -*- coding: utf-8 -*-
"""급이부 부품별 그림 — 부품 파일마다 등각·정면·윗면·옆면 4장 + 치수 표 (서현, 2026-11-10, CAP-AI-58)

GUI 매크로 (saveImage는 화면 필요):
    "C:\\Program Files\\FreeCAD 1.1\\bin\\freecad.exe" cad\\feeder_parts_render.py
결과: cad/img/parts/feeder/<부품 파일 이름>.png (정투영, 애니메이션 끔), 조립은 A143_급이방_조립.png
"""
import os, json, glob
import FreeCAD as App
import FreeCADGui as Gui

REPO = os.environ.get("D5G_REPO", r"C:\capstone\-capstone-project-repo")
SRC = [os.path.join(REPO, "cad", "parts", "feeder"), os.path.join(REPO, "cad", "vendor_step", "parts")]
OUT = os.path.join(REPO, "cad", "img", "parts", "feeder")
FONT = r"C:\Windows\Fonts\malgun.ttf"
VW, VH = 1100, 850


def views(doc, base):
    v = Gui.getDocument(doc.Name).activeView()
    v.setCameraType("Orthographic")
    out = []
    for nm, fn in (("등각", v.viewIsometric), ("정면 (-y에서)", v.viewFront), ("윗면", v.viewTop), ("오른쪽 (+x에서)", v.viewRight)):
        fn(); v.fitAll(); Gui.updateGui()
        p = os.path.join(OUT, "_%s_%d.png" % (base, len(out)))
        v.saveImage(p, VW, VH, "White")
        out.append((nm, p))
    return out


def rows(doc):
    r = []
    for sh_name in ("치수", "맞춤"):
        sh = doc.getObject(sh_name)
        if sh is None:
            continue
        r.append(("", "[%s]" % sh_name, ""))
        i = 2
        while True:
            try:
                a = sh.get("A%d" % i)
            except Exception:
                break
            if a in (None, ""):
                break
            vals = []
            for c in "BC":
                try:
                    vals.append(str(sh.get("%s%d" % (c, i))))
                except Exception:
                    vals.append("")
            r.append(tuple(t.replace("−", "-") for t in (str(a), vals[0], vals[1])))   # 맑은 고딕에 − 글자 없음
            i += 1
    return r


def compose(base, title, shots, table):
    from PIL import Image, ImageDraw, ImageFont
    f1, f2, f3 = ImageFont.truetype(FONT, 40), ImageFont.truetype(FONT, 26), ImageFont.truetype(FONT, 22)
    th = 34 * len(table) + 40
    W, H = 2 * VW, 110 + 2 * VH + th
    im = Image.new("RGB", (W, H), "white")
    dr = ImageDraw.Draw(im)
    dr.text((30, 30), title, fill=(0, 0, 0), font=f1)
    for k, (nm, p) in enumerate(shots):
        x0, y0 = (k % 2) * VW, 110 + (k // 2) * VH
        im.paste(Image.open(p).convert("RGB"), (x0, y0))
        dr.rectangle([x0, y0, x0 + VW - 1, y0 + VH - 1], outline=(180, 180, 180), width=2)
        dr.text((x0 + 20, y0 + 15), nm, fill=(200, 30, 30), font=f2)
        os.remove(p)
    y = 110 + 2 * VH + 20
    for a, b, c in table:
        dr.text((30, y), a, fill=(0, 0, 0), font=f3)
        dr.text((330, y), b, fill=(0, 0, 0), font=f3)
        dr.text((1500, y), c, fill=(90, 90, 90), font=f3)
        y += 34
    path = os.path.join(OUT, base + ".png")
    im.save(path)
    return path


def run():
    App.ParamGet("User parameter:BaseApp/Preferences/View").SetBool("UseNavigationAnimations", False)
    os.makedirs(OUT, exist_ok=True)
    done = []
    files = sorted(glob.glob(os.path.join(SRC[0], "P*.FCStd"))) + sorted(glob.glob(os.path.join(SRC[1], "P*.FCStd"))) + \
        [os.path.join(SRC[0], "A143_급이방_조립.FCStd")]
    for fn in files:
        if not os.path.exists(fn):
            continue
        doc = App.openDocument(fn)
        base = os.path.splitext(os.path.basename(fn))[0]
        body = doc.getObject("Body")
        title = (body.Label if body else "급이 방 조립 (부품 파일 링크 %d개)" % len([o for o in doc.Objects if o.TypeId == "App::Link"])) + \
            " — %s · 정투영 · 단위 mm · CAP-AI-58" % os.path.basename(fn)
        shots = views(doc, base)
        done.append(compose(base, title, shots, rows(doc)))
    json.dump(done, open(os.path.join(OUT, "_render_done.json"), "w", encoding="utf-8"), ensure_ascii=False)


try:
    run()
except Exception:
    import traceback
    open(os.path.join(OUT, "_render_error.txt"), "w", encoding="utf-8").write(traceback.format_exc())
os._exit(0)
