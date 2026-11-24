# -*- coding: utf-8 -*-
"""조립 설명서 그림용 FreeCAD 준비 스크립트 (승준 PC FreeCAD 안에서 실행).
Claude: execute_code로  exec(open(r"<이 파일 경로>", encoding="utf-8").read())  를 실행.
- 원본 FCStd를 열고 (이미 열려 있으면 그대로), 사본 문서 'ASM_manual'에 모양만 복사한다. 원본은 저장·수정하지 않는다.
- 단계 그림에 쓰는 '나눈 키'(brk_front 등)를 만든다.
- builtins.ASM_FN 에 그림 함수(run_job 등)를 넣는다.  → 그다음 freecad_run_jobs.py 실행.
"""
from pivy import coin
import FreeCAD as App, FreeCADGui as Gui, Part, json, math, os, builtins

SRC_PATH = r"C:\Users\user\Desktop\창의적종합설계\FreeCAD_2026-11-18\D5g_full_SJ1123_플라스틱판_NEMA17.FCStd"
SRC_NAME = "D5g_full_SJ1123_플라스틱판_NEMA17"
WD = r"C:\Users\user\Desktop\창의적종합설계\조립설명서_2026-11-24\_work"
os.makedirs(WD, exist_ok=True)
App.ParamGet("User parameter:BaseApp/Preferences/View").SetBool("UseNavigationAnimations", False)

SRC = App.getDocument(SRC_NAME) if SRC_NAME in App.listDocuments() else App.openDocument(SRC_PATH)
EXCL_PREFIX = ("G_S1", "G_S2", "G_S3", "F144", "FEED_", "PK_", "LM_", "N11_", "PREF_camera_view", "P190_pi5_aihat", "E00")
EXCL = {"B1b_113", "B1b_114", "B2_111", "B2_114", "B3_112", "B3_113", "P225_x_nut_T8", "XYn101", "XYn102", "B3_116"}
if "ASM_manual" in App.listDocuments():
    App.closeDocument("ASM_manual")
A = App.newDocument("ASM_manual")
for o in SRC.Objects:
    if o.Name in EXCL or o.Name.startswith(EXCL_PREFIX):
        continue
    if not hasattr(o, "Shape") or o.Shape.isNull():
        continue
    f = A.addObject("Part::Feature", o.Name)
    f.Shape = o.Shape.copy()

# 203p 마커 클립 2개 (docs/2026-11-18_승준_FreeCAD_파일_기록.md 3-2 코드)
V = App.Vector; cx, cy = 75.0, -40.0; cl = []
for z0 in (435.75, 447.75):
    h = 9.5; zc = z0 + h / 2
    ring = Part.makeCylinder(9.15, h, V(cx, cy, z0)).cut(Part.makeCylinder(7.3, h + 2, V(cx, cy, z0 - 1)))
    tab = Part.makeBox(4.0, 17.05, h, V(80.15, -38.0, z0)).cut(Part.makeCylinder(7.3, h + 2, V(cx, cy, z0 - 1)))
    c = ring.fuse(tab).cut(Part.makeBox(4.0, 1.0, h + 2, V(cx - 9.15 - 1, cy - 0.5, z0 - 1)))
    c = c.cut(Part.makeCylinder(1.7, 20, V(70, -25.5, zc), V(1, 0, 0))).removeSplitter()
    cl.append(c)
A.addObject("Part::Feature", "C203p").Shape = Part.makeCompound(cl)


def split(src, new, idx):
    s = A.getObject(src).Shape
    if A.getObject(new):
        A.removeObject(new)
    A.addObject("Part::Feature", new).Shape = Part.makeCompound([s.Solids[i].copy() for i in idx])


def ctr(sol):
    b = sol.BoundBox
    return (b.Center.x, b.Center.y, b.Center.z)


def assign(bolt_src, brk, gid):
    out = {}
    for j, s in enumerate(A.getObject(bolt_src).Shape.Solids):
        c = ctr(s); best = None; bd = 1e9
        for i, b in enumerate(brk):
            cc = ctr(b); dd = sum((c[k] - cc[k]) ** 2 for k in range(3))
            if dd < bd:
                bd = dd; best = i
        out.setdefault(gid[best], []).append(j)
    return out


def group(name, sols):
    if A.getObject(name):
        A.removeObject(name)
    A.addObject("Part::Feature", name).Shape = Part.makeCompound(sols)


# 프레임 모서리 브래킷 (앞·뒤·왼·오른 사다리) + 볼트 + 스프링너트
E = A.getObject("P100e_bracket_2020_L").Shape.Solids
gid = {}
for i, s in enumerate(E):
    b = s.BoundBox
    if b.YMax < -159 and b.YMin > -181 and b.XMin > -161 and b.XMax < 161: g = "brk_front"
    elif b.YMin > 159 and b.XMin > -161 and b.XMax < 161: g = "brk_back"
    elif b.XMax < -159: g = "brk_left"
    else: g = "brk_right"
    gid[i] = g
fb = assign("P100f_bolt_M5x8", E, gid); fn = assign("P100g_tnut_M5_slot6", E, gid)
FB = A.getObject("P100f_bolt_M5x8").Shape.Solids; FN = A.getObject("P100g_tnut_M5_slot6").Shape.Solids
for g in ("brk_front", "brk_back", "brk_left", "brk_right"):
    group(g, [E[i].copy() for i in gid if gid[i] == g] + [FB[j].copy() for j in fb[g]] + [FN[j].copy() for j in fn[g]])
# T 이음 브래킷 (데크 가로대 · 위 가로대 · 갠트리 레일)
E2 = A.getObject("P100e2_bracket_2020_L_T이음").Shape.Solids
tg = {"tb_deck": range(0, 8), "tb_top": range(8, 16), "tb_gantry": range(16, 20)}
gid2 = {i: g for g, r in tg.items() for i in r}
fb2 = assign("P100f2_bolt_M5x8_T이음", E2, gid2); fn2 = assign("P100g2_tnut_M5_slot6_T이음", E2, gid2)
FB2 = A.getObject("P100f2_bolt_M5x8_T이음").Shape.Solids; FN2 = A.getObject("P100g2_tnut_M5_slot6_T이음").Shape.Solids
for g, r in tg.items():
    group(g, [E2[i].copy() for i in r] + [FB2[j].copy() for j in fb2[g]] + [FN2[j].copy() for j in fn2[g]])
# 부품 → 프레임 볼트
J = A.getObject("P100j_bolt_M5_parts").Shape.Solids; K = A.getObject("P100k_tnut_M5_parts").Shape.Solids
for g, idx in {"top_bolts": [0, 1, 2, 3], "deck_bolts": [4, 5, 6, 7], "pi_bolts": [8, 9], "estop_bolts": [10, 11]}.items():
    group(g, [J[i].copy() for i in idx] + [K[i].copy() for i in idx])
# 그 밖에 나눈 키
split("V3_P10", "bar_bolts_bar", [0, 1]); split("V3_P10", "bar_bolts_deck", [2, 3])
ear = A.getObject("EarScr").Shape.Solids
split("EarScr", "ear_112", [i for i, s in enumerate(ear) if s.BoundBox.Center.x < 55])
split("EarScr", "ear_176", [i for i, s in enumerate(ear) if s.BoundBox.Center.x >= 55])
split("SJ_uno_st", "uno1_st", [0, 1, 2]); split("SJ_uno_st", "uno2_st", [3, 4, 5])
split("B2_112", "beamL", [0]); split("B2_112", "beamL_bolts", [1, 2, 3, 4]); split("B2_112", "rodend_csk", [5, 6, 7, 8])
split("B2_112", "rodend_A", [5, 7]); split("B2_112", "rodend_B", [6, 8])
split("B2_112", "sc_csk_A", [9, 11, 13, 15]); split("B2_112", "sc_csk_B", [10, 12, 14, 16])
sc = A.getObject("B2_110").Shape.Solids
split("B2_110", "sc8uu_A", [i for i, s in enumerate(sc) if s.BoundBox.Center.y < 0])
split("B2_110", "sc8uu_B", [i for i, s in enumerate(sc) if s.BoundBox.Center.y > 0])
split("B2_115", "ym_standoffs", [0, 3, 6]); split("B2_115", "ym_csk", [1, 4, 7]); split("B2_115", "ym_pan", [2, 5, 8])
split("B3_114", "spsv_standoffs", [0, 3, 6]); split("B3_114", "sv_pan", [1, 4, 7]); split("B3_114", "sp_set", [2, 5, 8])
split("B3_114", "falcs", [17, 18]); split("B3_114", "falcs_screws", [9, 10, 11, 12, 13, 14, 15, 16])
split("B3_117", "shoulder_set", [0, 1, 2, 3]); split("B3_117", "clip_screws", [4, 5, 6, 7])
split("B2_001", "pi_PB", [0]); split("B2_001", "pi_PV", [1])
split("DRV_pcb", "drv_board", [0, 5]); split("DRV_pcb", "drv_modules", [1, 2, 3, 4])
A.recompute()
GA = Gui.getDocument("ASM_manual")
Gui.ActiveDocument = GA


# ---------------------------------------------------------------- 그림 함수
def _norm(v):
    l = math.sqrt(sum(c * c for c in v)); return [c / l for c in v]


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cam_basis(d, up=(0, 0, 1)):
    d = _norm(d); u = _norm([up[i] - _dot(up, d) * d[i] for i in range(3)]); b = [-c for c in d]
    return _cross(u, b), u, b, d


def view_for(d, up, bbs, Wpx, Hpx, margin=1.08):
    r, u, b, dd = cam_basis(d, up)
    xs = []; ys = []; zs = []
    for bb in bbs:
        for X in (bb[0], bb[3]):
            for Y in (bb[1], bb[4]):
                for Z in (bb[2], bb[5]):
                    p = (X, Y, Z); xs.append(_dot(p, r)); ys.append(_dot(p, u)); zs.append(_dot(p, dd))
    cxp = (min(xs) + max(xs)) / 2; cyp = (min(ys) + max(ys)) / 2; czp = (min(zs) + max(zs)) / 2
    height = max(max(ys) - min(ys), (max(xs) - min(xs)) / (Wpx / Hpx)) * margin
    c3 = [r[i] * cxp + u[i] * cyp + dd[i] * czp for i in range(3)]
    return {"r": r, "u": u, "d": dd, "c": c3, "height": height, "W": Wpx, "H": Hpx}


def apply_cam(cv):
    v = GA.ActiveView
    v.setCameraType("Orthographic")
    r, u, dd = cv["r"], cv["u"], cv["d"]; b = [-x for x in dd]
    M = App.Matrix(r[0], u[0], b[0], 0, r[1], u[1], b[1], 0, r[2], u[2], b[2], 0, 0, 0, 0, 1)
    q = App.Rotation(M).Q
    cam = v.getCameraNode()
    cam.orientation.setValue(q[0], q[1], q[2], q[3])
    cam.position.setValue(*[cv["c"][i] - dd[i] * 4000 for i in range(3)])
    cam.height.setValue(cv["height"]); cam.focalDistance.setValue(4000)
    cam.nearDistance.setValue(100.0); cam.farDistance.setValue(9000.0)   # 안 넣으면 빈 그림


P0 = {}


def base_pl(k):
    if k not in P0:
        P0[k] = A.getObject(k).Placement
    return P0[k]


GREY = (0.80, 0.81, 0.83); NEW = (1.0, 0.50, 0.05)


def run_job(j):
    nat = j.get("nat", []); cols = j.get("colors", {})
    keys_all = set(j["done"]) | set(j["new"]) | set(nat)
    for o in A.Objects:
        vo = GA.getObject(o.Name)
        if o.Name in keys_all:
            vo.Visibility = True; vo.DisplayMode = "Flat Lines"; vo.LineWidth = 1.0; vo.Transparency = 0
            if o.Name in j["new"]:
                vo.ShapeColor = NEW; vo.LineColor = (0.38, 0.16, 0.0)
            elif o.Name in nat:
                c = tuple(cols.get(o.Name, (0.8, 0.8, 0.8))); vo.ShapeColor = c; vo.LineColor = tuple(max(0, x * 0.45) for x in c)
            else:
                vo.ShapeColor = GREY; vo.LineColor = (0.40, 0.40, 0.42)
        else:
            vo.Visibility = False
    moved = {}
    for k, ov in j["off"].items():
        o = A.getObject(k)
        if o is None:
            continue
        p0 = base_pl(k); o.Placement = App.Placement(App.Vector(*ov), App.Rotation()).multiply(p0); moved[k] = p0
    bbs = []
    for k in j["focus"]:
        o = A.getObject(k)
        if o is None:
            continue
        b = o.Shape.BoundBox; bbs.append([b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax])
    cv = view_for(j["d"], j["up"], bbs, j["W"], j["H"], j["margin"])
    apply_cam(cv)
    GA.ActiveView.saveImage(WD + "\\" + j["name"] + ".png", j["W"], j["H"], "White")
    for k, p0 in moved.items():
        A.getObject(k).Placement = p0
    json.dump({"file": j["name"] + ".png", "cam": cv}, open(WD + "\\" + j["name"] + ".json", "w", encoding="utf-8"))


builtins.ASM_FN = dict(view_for=view_for, apply_cam=apply_cam, base_pl=base_pl, run_job=run_job, P0=P0)
print("ASM_manual ready:", len(A.Objects), "objects")
