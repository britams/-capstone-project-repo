# -*- coding: utf-8 -*-
"""D5g 그림 — 전체 조립도 4장 + 전기 배치(위) + 부품번호 풍선도 (서현, 2026-11-09, CAP-AI-55)

FreeCAD GUI 매크로로 돌린다 (saveImage는 화면이 있어야 함):
    set D5G_FILE=<...>\D5g_full.FCStd
    "C:\Program Files\FreeCAD 1.1\bin\freecad.exe" cad\D5g_render.py
정투영, 시점 애니메이션 끔 (CLAUDE.md). 전체 조립도에는 2020 프레임 + 상용 트랩(REF_trap_*)이 들어감.
글자·풍선은 FreeCAD 안의 Pillow로 그린다 (맑은 고딕). 결과: cad/img/D5g_*.png
"""
import os, sys, json
import FreeCAD as App
import FreeCADGui as Gui
import Part

REPO = os.environ.get("D5G_REPO", r"C:\capstone\-capstone-project-repo")
FN = os.environ.get("D5G_FILE", os.path.join(REPO, "cad", "D5g_full.FCStd"))
OUT = os.environ.get("D5G_IMG", os.path.join(REPO, "cad", "img"))
FONT = r"C:\Windows\Fonts\malgun.ttf"
W, H = 2400, 1800
V = App.Vector

UPPER = ("REF_trap_container", "REF_trap_cap", "REF_trap_silicone_star", "105_top_plate", "104_dome_coupling")
VIEWS = [  # (파일 이름, 시점, 맞출 상자 또는 None, 숨길 머리말, 제목)
    ("D5g_도1_전체_등각", "iso", None, (), "D5g 전체 조립 — 등각 (2020 프레임 + 상용 트랩) · 파랑 = 3D 프린트, 회색 = 그 밖"),
    ("D5g_도2_정면", "front", None, (), "D5g 전체 조립 — 정면 (-y에서 봄) · 파랑 = 3D 프린트, 회색 = 그 밖"),
    ("D5g_도3_측면", "right", None, (), "D5g 전체 조립 — 측면 (+x에서 봄) · 파랑 = 3D 프린트, 회색 = 그 밖"),
    ("D5g_도4_위", "top", None, UPPER, "D5g 전체 조립 — 위 (위판·포획통 숨김) · 파랑 = 3D 프린트, 회색 = 그 밖"),
]
# 전기 배치: 데크 위만 보이게 (z 300 위 부품, 상용 트랩 위쪽 숨김)
ELEC_BOX = (-200, 110, -95, 95, 195, 260)
ELEC_TAGS = [("193g", "게이트 허브 193g"), ("193j", "J_I2C 193j"), ("193v_servo_hub (", "서보 허브 193v"), ("196m_mosfet_module", "MOSFET 모듈 196m"),
             ("198x_hx711", "HX711 198x (새)"), ("194j", "DC 잭 194j (새)"), ("194_estop", "비상 정지 194"), ("194f", "퓨즈 194f"),
             ("193w_wago_221", "와고 193w"), ("191_arduino_uno", "UNO 1·2 (191·192)"), ("195p_uln2003_F", "ULN2003 F 195p"), ("148_load", "로드셀 148"), ("153_floor", "바닥 모터 153")]
BALLOON_BOX = (-200, 190, -130, 130, 190, 620)   # 모듈 부분 (프레임 일부 포함)
BALLOONS = ["100a", "101_", "105_", "110_", "112_", "120_", "130_", "153_", "148_load", "170_", "176_", "180_", "181_", "193g_gate_hub (",
            "193v_servo_hub (", "194_estop", "194b", "194j", "196m_mosfet_module", "198x_", "199a", "201_", "205_", "209_", "215_",
            "217_", "219_", "143_", "REF_trap_body", "226_", "227x", "227y", "227f"]


def setup():
    p = App.ParamGet("User parameter:BaseApp/Preferences/View")
    p.SetBool("UseNavigationAnimations", False)
    doc = App.openDocument(FN)
    Gui.activeDocument().activeView().setCameraType("Orthographic")
    return doc


def _objs(doc):
    return [o for o in doc.Objects if hasattr(o, "Shape") and o.TypeId != "App::DocumentObjectGroup" and o.ViewObject]


def _fit(doc, v, box):
    if not box:
        v.fitAll()
        return
    x0, x1, y0, y1, z0, z1 = box
    vis = {o.Name: o.ViewObject.Visibility for o in _objs(doc)}
    fb = doc.addObject("Part::Feature", "FitBox")
    fb.Shape = Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
    for o in _objs(doc):
        if o.Name != "FitBox":
            o.ViewObject.Visibility = False
    v.fitAll()
    for o in _objs(doc):
        if o.Name in vis:
            o.ViewObject.Visibility = vis[o.Name]
    doc.removeObject("FitBox")


def shoot(doc, name, kind, box, hide, keep=None):
    v = Gui.activeDocument().activeView()
    hidden = []
    for o in _objs(doc):
        h = o.Label.startswith(hide) if hide else False
        if keep is not None and not keep(o):
            h = True
        if h and o.ViewObject.Visibility:
            o.ViewObject.Visibility = False
            hidden.append(o)
    getattr(v, {"iso": "viewIsometric", "front": "viewFront", "right": "viewRight", "top": "viewTop"}[kind])()
    _fit(doc, v, box)
    Gui.updateGui()
    vw, vh = v.getSize()
    path = os.path.join(OUT, name + ".png")
    v.saveImage(path, W, H, "White")
    # 화면 좌표: 저장 그림은 같은 시점을 W × H로 — 가운데 기준 비례
    k = max(W / vw, H / vh) if vw and vh else 1.0     # 넓은 창 → 그림 높이에 맞춤 (min이면 화살표가 0.52배로 줄었음, 11/09 확인)
    def proj(p):
        sx, sy = v.getPointOnViewport(p)
        return (W / 2 + (sx - vw / 2) * k, H / 2 - (sy - vh / 2) * k)
    for o in hidden:
        o.ViewObject.Visibility = True
    return path, proj


def annotate(path, title, tags=(), note=None, columns=False):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 40)
    fs = ImageFont.truetype(FONT, 26)
    d.rectangle([20, 20, 60 + d.textlength(title, font=f), 85], fill=(255, 255, 255))
    d.text((40, 30), title, fill=(20, 20, 20), font=f)
    if note:
        d.rectangle([20, H - 70, 60 + d.textlength(note, font=fs), H - 20], fill=(255, 255, 255))
        d.text((40, H - 60), note, fill=(80, 80, 80), font=fs)
    if columns:                      # 왼쪽·오른쪽 두 줄, 세로 순서대로 → 선이 안 엇갈림
        left = sorted([t for t in tags if t[0][0] < W / 2], key=lambda t: t[0][1])
        right = sorted([t for t in tags if t[0][0] >= W / 2], key=lambda t: t[0][1])
        for col, xs, al in ((left, 60, -1), (right, W - 60, 1)):
            n = len(col)
            for i, ((x, y), txt) in enumerate(col):
                ly = 130 + (H - 230) * (i + 0.5) / max(n, 1)
                tw = d.textlength(txt, font=fs)
                r = (xs - tw - 20, ly - 18, xs, ly + 18) if al > 0 else (xs, ly - 18, xs + tw + 20, ly + 18)
                d.line([(x, y), (r[0] if al > 0 else r[2], ly)], fill=(200, 30, 30), width=2)
                d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(200, 30, 30))
                d.rounded_rectangle(r, radius=12, outline=(200, 30, 30), width=3, fill=(255, 255, 255))
                d.text((r[0] + 10, r[1] + 2), txt, fill=(20, 20, 20), font=fs)
        im.save(path)
        im.save(path[:-4] + ".jpg", quality=92)
        return
    placed = []
    for (x, y), txt in tags:
        tw = d.textlength(txt, font=fs)
        # 풍선 자리: 부품에서 바깥쪽(그림 가운데 반대)으로 120 px, 겹치면 아래로 밀기
        dx = 1 if x >= W / 2 else -1
        bx, by = x + dx * 140, y - 60
        for _ in range(40):
            r = (bx - (tw if dx < 0 else 0) - 10, by - 18, bx + (0 if dx < 0 else tw) + 10, by + 18)
            if not any(not (r[2] < q[0] or r[0] > q[2] or r[3] < q[1] or r[1] > q[3]) for q in placed):
                break
            by += 40
        r = (max(4, r[0]), max(90, r[1]), min(W - 4, r[2]), r[3])
        placed.append(r)
        d.line([(x, y), ((r[2] if dx < 0 else r[0]), (r[1] + r[3]) / 2)], fill=(200, 30, 30), width=3)
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(200, 30, 30))
        d.rounded_rectangle(r, radius=12, outline=(200, 30, 30), width=3, fill=(255, 255, 255))
        d.text((r[0] + 10, r[1] + 2), txt, fill=(20, 20, 20), font=fs)
    im.save(path)
    im.save(path[:-4] + ".jpg", quality=92)


def _center(doc, pre):
    for o in _objs(doc):
        if o.Label.startswith(pre) and o.ViewObject.Visibility and not o.Shape.isNull():
            return o.Shape.BoundBox.Center, o.Label
    return None, None


def run():
    os.makedirs(OUT, exist_ok=True)
    doc = setup()
    done = []
    for name, kind, box, hide, title in VIEWS:
        p, _ = shoot(doc, name, kind, box, hide)
        annotate(p, title, note="정투영 · 단위 mm · %s" % os.path.basename(FN))
        done.append(p)
    # 전기 배치 (위에서, 데크 위만)
    keep = lambda o: o.Shape.BoundBox.ZMin < 300 and o.Shape.BoundBox.ZMax > 195 and not o.Label.startswith("REF_")
    p, proj = shoot(doc, "D5g_전기배치_위", "top", ELEC_BOX, (), keep)
    tags = []
    for pre, txt in ELEC_TAGS:
        c, lab = _center(doc, pre)
        if c:
            tags.append((proj(V(c.x, c.y, 260)), txt))
    annotate(p, "D5g 전기 배치 — 데크 위 (위에서 봄)", tags, note="새로 넣음: HX711 198x (-44.5, 54) · DC 잭 194j (-184, -35, 225) · J_I2C 193j 줄 6 칸 22~25 (CAP-AI-55)")
    done.append(p)
    # 풍선도 (등각)
    p, proj = shoot(doc, "D5g_부품번호_풍선도", "iso", BALLOON_BOX, UPPER)
    tags = []
    for pre in BALLOONS:
        c, lab = _center(doc, pre)
        if c:
            tags.append((proj(c), lab.split(" ")[0].split("_")[0] if not lab.startswith("REF") else "REF 트랩 몸통"))
    annotate(p, "D5g 부품 번호 — 모듈 (이름은 cad/2026-11-06_D5g_부품표_승준.md)", tags, columns=True)
    done.append(p)
    json.dump(done, open(os.path.join(OUT, "_render_done.json"), "w", encoding="utf-8"), ensure_ascii=False)


try:
    run()
except Exception:
    import traceback
    open(os.path.join(OUT, "_render_error.txt"), "w", encoding="utf-8").write(traceback.format_exc())
os._exit(0)
