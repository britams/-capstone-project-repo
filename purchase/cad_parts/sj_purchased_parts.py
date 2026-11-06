# -*- coding: utf-8 -*-
"""구매 부품 라이브러리 + D5e 치수 대조 (승준, CAP-AI-SJ-38, 2026-11-06)

목적
- D5e 모델에 들어간 '사야 하는 부품'을 판매 규격 치수로 따로 그려, 서현 CAD(D5f)에 그대로 가져다 쓸 수 있게 한다.
- D5e_full_assembly 문서가 열려 있으면, 모델 속 부품 치수를 이 규격과 대조해 결과를 출력한다 (check()).
- cad/ 는 서현 담당이라 이 파일은 purchase/ 에 둔다. 모델(.FCStd)을 고치지 않는다.

실행 (FreeCAD 1.x 파이썬 콘솔 / MCP)
    import sys; sys.path.insert(0, r"<repo>/purchase/cad_parts"); import sj_purchased_parts as P
    doc = P.make_library()      # 부품을 한 줄로 늘어놓은 새 문서 "SJ_purchased_parts"
    P.check()                   # D5e_full_assembly 문서가 열려 있으면 대조표 출력

치수 근거 (주석의 [확실]/[가능성 높음]/[추측]은 근거의 강도)
- LM8UU: d 8, D 15, L 24, 링 홈 간격 17.5, 홈 폭 1.1, 홈 바닥 Ø14.3 — 미스미·THK LM 시리즈 표준 [확실]
- LM6UU: d 6, D 12, L 19, 링 홈 간격 13.5, 홈 폭 1.1, 홈 바닥 Ø11.5 — 같은 표준 [확실]
- T8 리드스크루: Tr8 × 8 (4줄, 피치 2, 리드 8). 외경 8, 골지름 약 6 — 3D 프린터용 국내 유통 규격 [가능성 높음]
  · McMaster 에는 리드 8 T8 이 없음. 가장 가까운 것 = 2391N11 (M8 × 2.5, 리드 10, 아세탈 플랜지 너트) — 11/06 McMaster 'T8 Nuts' 페이지 확인
- T8 황동 플랜지 너트: 플랜지 Ø22 × 3.5, 몸통 Ø10.2, 길이 15, 4 × Ø3.5 PCD 16 — D5e 와 같은 값 [가능성 높음]
- 커플링 5 → 8: Ø19.1 × 25.4 (McMaster 4147N159 와 같은 치수, 서현 D5e 근거), 국내 'D19L25 5×8' [가능성 높음]
- 연마봉 길이: 11/06 FreeCAD 에서 D5e 모델을 재서 얻은 값 (아래 LENGTHS) [확실 — 모델 기준]
- 마이크로 스위치 KW11-3Z (레버형): 본체 20 × 10.2 × 6.4, 구멍 Ø2.3 × 2 간격 9.5 [가능성 높음 — 판매처 외형도 대표값]
- 육각 구멍붙이 볼트 ISO 4762: M3 머리 Ø5.5 × 3, M5 머리 Ø8.5 × 5 [확실]
"""
import FreeCAD as App
import Part

V = App.Vector

# D5e 모델에서 잰 길이 (FreeCAD, 2026-11-06, D5e_full_assembly) — 자르는 길이
LENGTHS = {
    "213_x_rods": (8.0, 163.0, 2),            # Ø8 연마봉 (LM8UU 짝)
    "207_y_rods": (6.0, 124.0, 2),            # Ø6 연마봉 (LM6UU 짝)
    "157_guide_rod": (4.0, 108.0, 1),         # Ø4 봉 (바닥 캐리지 돌림 막이)
    "223_holder_guide_pins": (3.0, 69.0, 2),  # Ø3 핀 (펜 홀더 안내)
    "155_lead_screw_T8": (8.0, 80.0, 1),      # 바닥 승강
    "214_x_lead_screw_T8": (8.0, 92.8, 1),    # X
    "208_y_lead_screw_T8": (8.0, 132.7, 1),   # Y
}

LM = {"LM8UU": dict(d=8.0, D=15.0, L=24.0, B=17.5, W=1.1, D1=14.3),
      "LM6UU": dict(d=6.0, D=12.0, L=19.0, B=13.5, W=1.1, D1=11.5)}
NUT = dict(fl_d=22.0, fl_t=3.5, body_d=10.2, L=15.0, pcd=16.0, hole_d=3.5)
CPL = dict(D=19.1, L=25.4, b1=5.0, b2=8.0)
KW11 = dict(L=20.0, W=6.4, H=10.2, hole_d=2.3, hole_p=9.5, lever=28.0)


def cyl(r, h, p=V(0, 0, 0), d=V(0, 0, 1)):
    return Part.makeCylinder(r, h, p, d)


def linear_bushing(name):
    """LM 볼 부싱: 바깥 원통 − 축 구멍 − 고정 링 홈 2개"""
    s = LM[name]
    body = cyl(s["D"] / 2, s["L"]).cut(cyl(s["d"] / 2, s["L"] + 2, V(0, 0, -1)))
    for z in ((s["L"] - s["B"]) / 2 - s["W"], (s["L"] + s["B"]) / 2):
        ring = cyl(s["D"] / 2 + 1, s["W"], V(0, 0, z)).cut(cyl(s["D1"] / 2, s["W"] + 1, V(0, 0, z - 0.5)))
        body = body.cut(ring)
    return body


def rod(d, L):
    return cyl(d / 2, L)


def lead_screw(L):
    """T8 나사: 외경 8 원통 + 골 표시(피치 2 마다 홈 0.5) — 겉모양용"""
    s = cyl(4.0, L)
    z = 1.0
    while z < L - 1.0:
        s = s.cut(cyl(4.5, 0.5, V(0, 0, z)).cut(cyl(3.5, 0.5, V(0, 0, z))))
        z += 2.0
    return s


def t8_nut():
    n = NUT
    f = cyl(n["fl_d"] / 2, n["fl_t"]).fuse(cyl(n["body_d"] / 2, n["L"]))
    f = f.cut(cyl(4.0, n["L"] + 2, V(0, 0, -1)))
    import math
    for k in range(4):
        a = math.radians(45 + 90 * k)
        f = f.cut(cyl(n["hole_d"] / 2, n["fl_t"] + 2, V(n["pcd"] / 2 * math.cos(a), n["pcd"] / 2 * math.sin(a), -1)))
    return f.removeSplitter()


def coupling():
    c = CPL
    s = cyl(c["D"] / 2, c["L"])
    s = s.cut(cyl(c["b1"] / 2, c["L"] / 2 + 0.1, V(0, 0, -0.05)))
    s = s.cut(cyl(c["b2"] / 2, c["L"] / 2 + 0.1, V(0, 0, c["L"] / 2)))
    # 나선 홈 대신 가운데 홈 3줄 (겉모양) — 실제는 나선형 슬릿
    for z in (9.7, 12.2, 14.7):
        s = s.cut(cyl(c["D"] / 2 + 1, 0.8, V(0, 0, z)).cut(cyl(c["D"] / 2 - 2.5, 0.8, V(0, 0, z))))
    # 고정 나사 M3 구멍 (양쪽)
    for z in (4.0, c["L"] - 4.0):
        s = s.cut(cyl(1.25, c["D"], V(0, 0, z), V(1, 0, 0)))
    return s


def microswitch():
    k = KW11
    b = Part.makeBox(k["L"], k["W"], k["H"])
    for x in ((k["L"] - k["hole_p"]) / 2, (k["L"] + k["hole_p"]) / 2):
        b = b.cut(cyl(k["hole_d"] / 2, k["W"] + 2, V(x, -1, 3.0), V(0, 1, 0)))
    lever = Part.makeBox(k["lever"], k["W"] - 2, 0.5, V(-4, 1, k["H"] + 1.5))
    return b.fuse(lever)


def socket_screw(m, L):
    head = {3: (5.5, 3.0), 5: (8.5, 5.0), 4: (7.0, 4.0)}[m]
    return cyl(head[0] / 2, head[1], V(0, 0, L)).fuse(cyl(m / 2, L))


PARTS = [
    ("LM8UU_x2_X", lambda: linear_bushing("LM8UU")),
    ("LM6UU_x2_Y", lambda: linear_bushing("LM6UU")),
    ("rod_d8_L163_x2", lambda: rod(8, 163)),
    ("rod_d6_L124_x2", lambda: rod(6, 124)),
    ("rod_d4_L108_x1", lambda: rod(4, 108)),
    ("pin_d3_L69_x2", lambda: rod(3, 69)),
    ("T8_screw_L80_floor", lambda: lead_screw(80)),
    ("T8_screw_L93_X", lambda: lead_screw(93)),
    ("T8_screw_L133_Y", lambda: lead_screw(133)),
    ("T8_brass_flange_nut_x3", t8_nut),
    ("coupling_5x8_D19L25_x3", coupling),
    ("microswitch_KW11_x3", microswitch),
    ("M3x10_socket_x12", lambda: socket_screw(3, 10)),
    ("M5x10_socket_x64", lambda: socket_screw(5, 10)),
]


def make_library(doc_name="SJ_purchased_parts"):
    if doc_name in App.listDocuments():
        App.closeDocument(doc_name)
    doc = App.newDocument(doc_name)
    x = 0.0
    for name, fn in PARTS:
        shp = fn()
        b = shp.BoundBox
        shp.translate(V(x - b.XMin, -b.YMin - b.YLength / 2, -b.ZMin))
        o = doc.addObject("Part::Feature", name)
        o.Shape = shp
        x += b.XLength + 15.0
    doc.recompute()
    try:
        import FreeCADGui as Gui
        Gui.getDocument(doc_name).activeView().viewIsometric()
        Gui.SendMsgToActiveView("ViewFit")
    except Exception:
        pass
    return doc


def check(asm="D5e_full_assembly"):
    """D5e 모델 속 구매 부품 치수를 규격과 대조 → (부품, 모델 값, 규격 값, 판정) 목록"""
    if asm not in App.listDocuments():
        print("D5e_full_assembly 문서가 열려 있지 않음")
        return []
    d = App.getDocument(asm)
    rows = []

    def solids(label):
        o = [x for x in d.Objects if x.Label == label]
        return o[0].Shape.Solids if o else []

    def diams(s):
        return sorted({round(f.Surface.Radius * 2, 2) for f in s.Faces if f.Surface.TypeId == "Part::GeomCylinder"})

    for label, (dia, L, n) in LENGTHS.items():
        ss = solids(label)
        for s in ss:
            b = s.BoundBox
            got_L = max(b.XLength, b.YLength, b.ZLength)
            ok = abs(got_L - L) < 0.5 and dia in diams(s)
            rows.append((label, f"Ø{max(diams(s) or [0])} × {got_L:.1f}", f"Ø{dia} × {L}", "OK" if ok else "다름"))
        if len(ss) != n:
            rows.append((label, f"{len(ss)}개", f"{n}개", "개수 다름"))
    for label, key in (("222_x_bearings_LM8UU", "LM8UU"), ("221_y_bearings_LM6UU", "LM6UU")):
        s = LM[key]
        for so in solids(label):
            b = so.BoundBox
            got = sorted([b.XLength, b.YLength, b.ZLength])
            ok = abs(got[2] - s["L"]) < 0.3 and abs(got[1] - s["D"]) < 0.3 and s["d"] in diams(so)
            rows.append((label, f"{got[1]:.1f} × {got[2]:.1f}", f"Ø{s['D']} × {s['L']}", "OK" if ok else "다름"))
    for label in ("154_coupling", "210_y_coupling", "216_x_coupling"):
        for so in solids(label):
            b = so.BoundBox
            got = sorted([b.XLength, b.YLength, b.ZLength])
            ok = abs(got[2] - CPL["L"]) < 0.3 and abs(got[1] - CPL["D"]) < 0.3
            rows.append((label, f"{got[1]:.1f} × {got[2]:.1f}", f"Ø{CPL['D']} × {CPL['L']}", "OK" if ok else "다름"))
    for label in ("159_floor_nut_T8", "224_y_nut_T8", "225_x_nut_T8"):
        for so in solids(label):
            b = so.BoundBox
            got = sorted([b.XLength, b.YLength, b.ZLength])
            ok = abs(got[2] - NUT["fl_d"]) < 0.3 and abs(got[0] - NUT["L"]) < 0.3
            rows.append((label, f"{got[2]:.1f} / L {got[0]:.1f}", f"Ø{NUT['fl_d']} / L {NUT['L']}", "OK" if ok else "다름"))
    for r in rows:
        print("{:26s} 모델 {:18s} 규격 {:16s} {}".format(*r))
    return rows
