# -*- coding: utf-8 -*-
"""급이부 — 부품별 CAD 파일 → 조립 파일 (서현, 2026-11-10, CAP-AI-58)

서현 지시 (11/10 15:29): "부품별로 캐드 파일 만들고 부품별로 설계하자. 그 다음 모두 맞추는 것으로. 급이부만."

순서
  1) parts()    : 부품마다 FCStd 하나. 각자 자기 원점(아래 ORIGIN)에서 그림. 안에 '치수' 시트(부품 도면 값)와 '맞춤' 시트(다른 부품과 만나는 자리).
  2) assemble() : A143_급이방_조립.FCStd — 부품 파일을 App::Link로 불러 PLACE(자리)에 놓음. 같은 부품 여러 개는 링크 여러 개.
  3) check()    : 부품끼리 겹침(나사산 물림·인서트 녹아 박힘만 허용), 맞춤 자리 일치, 나사 물림·끝 여유, 출력 크기·무게.
치수는 한 곳: cad/D5g_feeder_uln.py 의 FD·FDX·INS·FOOT (feeder_check.py, D5g_full 도 같은 값을 읽음).
McMaster 부품(STEP)은 cad/vendor_step/parts/ 에 부품 파일을 만듦 (레포에 안 올림 — .gitignore). 조립 파일은 링크만 담으므로 올려도 됨.
실행 (FreeCAD 1.1, GUI 없이도 됨):
    import sys; sys.path.insert(0, r"<repo>\\cad"); import feeder_parts as FP; FP.run()
"""
import json
import math
import os

import FreeCAD as App
import Part

V = App.Vector
R = App.Rotation
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "parts", "feeder")
VEN = os.path.join(HERE, "vendor_step")
VOUT = os.path.join(VEN, "parts")
PETG = 1.27   # g/cm³ [가능성 높음 — 필라멘트 업체 표 1.27]


def _fd():
    import D5g_feeder_uln as FU
    return FU, FU.FD, FU.FDX, FU.INS, FU.FOOT


# ---------------- 원점 (조립 좌표에서 각 부품 원점이 놓이는 곳) ----------------
def origins():
    FU, f, e, ins, ft = _fd()
    import D5g_feeder_pump as FP
    px = f["x"] + f["post_dx"]
    return {
        "143": V(px, f["post_y"], f["post_foot_z"]),                # 발 아래 면, 기둥 축
        "143l": V(f["x"], f["ch_y0"], f["wall_top"]),               # 뚜껑 아래 면, 물길 앞 끝 가운데
        "142n": V(f["x"], f["tip_y"], f["tip_z"]),                  # 코튼롤 안 끝 가운데, 축 +z
        "144b": V(FP.HB["bot_x"], FP.HB["y_face"], FP.HB["z0"]),    # 걸이 판 아래 끝, 레일 바깥 면, 병 축 x
        "144n": FP.bottle_center(),                                 # 병 바닥 가운데
        "144p": FP.pump_center(),                                   # 펌프 모터 아래 끝 가운데
        "144h": V(0, 0, 0),                                         # 관 3개: 휘는 것이라 조립 자리 그대로 (자기 원점 = 조립 원점)
    }


# ---------------- 부품 모양 (자기 원점 기준) ----------------
def shape_143_143l():
    FU, f, e, ins, ft = _fd()
    tr, lid, _w, _i, _t, _s = FU.feeder_detail_shapes(Part.makeBox(1, 1, 1, V(-500, -500, -500)))
    o = origins()
    tr = tr.copy(); tr.translate(-o["143"])
    lid = lid.copy(); lid.translate(-o["143l"])
    return tr, lid


def shape_142n():
    FU, f, *_ = _fd()
    L = math.dist((f["tip_y"], f["tip_z"]), (f["end_y"], f["end_z"]))
    return Part.makeCylinder(f["roll_r"], L, V(0, 0, 0))


def _moved(s, o):
    s = s.copy(); s.translate(-o); return s


def shape_pump_parts():
    import D5g_feeder_pump as FP
    o = origins()
    bt, cap = FP.bottle()
    pm, ports = FP.pump()
    return _moved(FP.holder(), o["144b"]), _moved(bt.fuse(cap), o["144n"]), _moved(pm.fuse(ports), o["144p"])


def shape_tubes():
    """관 3개 — 열린 전체 모델(D5g_frame_detail)에 있으면 그 경로(걸림 없는 높이로 고른 것), 없으면 기본 높이"""
    import D5g_feeder_pump as FP
    d = App.listDocuments().get("D5g_frame_detail")
    out = {}
    for pre in ("144h_", "144hf_", "144hd_"):
        o = [x for x in d.Objects if x.Label.startswith(pre)] if d else []
        out[pre] = o[0].Shape.copy() if o else None
    if None in out.values():
        suck, feed = FP.tube_paths(300.0)
        out = {"144h_": FP.tube_along(suck), "144hf_": FP.tube_along(feed), "144hd_": FP.tube_along(FP.drain_path(330.0, 85.0))}
    return out


def magnet():
    FU, f, e, *_ = _fd()
    return Part.makeCylinder(e["mag_d"] / 2, e["mag_t"], V(0, 0, 0))


def _step(pn):
    p = os.path.join(VEN, pn + ".STEP")
    return Part.read(p) if os.path.exists(p) else None


def shape_mcm(pn):
    """McMaster 부품을 공통 자리로: 축 z. 인서트 = 큰 끝 z 0, 몸이 −z. 나사 = 머리 밑면 z 0, 머리 +z, 나사산 −z"""
    s = _step(pn)
    src = "STEP"
    if pn == "94459A130":
        if s is None:
            s, src = Part.makeCylinder(2.37, 4.3, V(0, 0, -4.3)), "표 치수 (STEP 없음)"
        else:
            s = s.copy(); s.rotate(V(0, 0, 0), V(1, 0, 0), 90); s.translate(V(0, 0, -2.15))
    elif pn == "92000A118":
        if s is None:
            s, src = Part.makeCylinder(1.5, 8, V(0, 0, -8)).fuse(Part.makeCylinder(3, 2.5, V(0, 0, 0))), "표 치수 (STEP 없음)"
        else:
            s = s.copy(); s.translate(V(0, 0, -2.75))
    return s, src


# ---------------- 부품 목록: (번호, 파일, 이름, 구분, 출처, 모양, 치수 줄, 맞춤 줄, 폴더) ----------------
def part_defs():
    FU, f, e, ins, ft = _fd()
    import D5g_feeder_pump as FP
    o = origins()
    tr, lid = shape_143_143l()
    hb, bt, pm = shape_pump_parts()
    tb = shape_tubes()
    px = f["x"] + f["post_dx"]
    th = math.degrees(math.atan2(f["tip_z"] - f["end_z"], f["end_y"] - f["tip_y"]))
    z = lambda Z: round(Z - o["143"].z, 2)            # 조립 z → 143 자기 z
    y = lambda Y: round(Y - o["143"].y, 2)
    x = lambda X: round(X - o["143"].x, 2)
    d143 = [
        ("발", "%g × %g × %g (x × y × z)" % (2 * ft["half_x"], 2 * ft["half_y"], ft["t"]), "mm"),
        ("발 인서트 구멍", "Ø%g 관통 × 2, y ±%g (간격 %g)" % (ins["hole"], ft["dy"], 2 * ft["dy"]), "94459A130 구멍 최대 Ø4, 최소 두께 5.1"),
        ("기둥", "%g × %g, z %g → %g (높이 %g)" % (f["post_w"], f["post_w"], ft["t"], z(f["floor_z"]), z(f["floor_z"]) - ft["t"]), "mm"),
        ("물길 (안)", "폭 %g, 바닥 두께 %g, 벽 %g, y %g → %g (끝 벽 %g)" % (f["ch_w"], f["floor_t"], f["ch_t"], y(f["ch_y0"]), y(f["ch_y1"]), f["ch_t"]), "mm"),
        ("물길 높이", "바닥 아래 z %g, 바닥 윗면 %g, 벽 위 %g" % (z(f["floor_z"]), z(f["floor_z"] + f["floor_t"]), z(f["wall_top"])), "mm"),
        ("앞벽 + 솜 구멍", "두께 %g, Ø%g, 솜 축 따라 %.1f° 아래로" % (f["front_t"], 2 * f["front_hole_r"], th), "mm"),
        ("펌프 노즐", "+x 벽 바깥 Ø%g × %g, 바브 Ø%g 2개, 구멍 Ø%g, (y %g, z %g)" % (f["nz_od"], f["nz_L"], f["nz_barb"], f["nz_bore"], y(f["nz_y"]), z(f["nz_z"])), "관 안 3.5에 끼움"),
        ("물빠짐 바브", "바닥 아래 Ø%g × %g, 구멍 Ø2, (x %g, y %g)" % (f["nz_od"], f["nz_L"], x(f["x"]), y(f["dr_y"])), "고인 물 → 프레임 밖"),
        ("뚜껑 기둥", "Ø%g × 4 (x %g ±%g, y %s): 자석 자리 Ø%.1f × %.1f 2개 + 핀 구멍 Ø%g × %g 2개 (대각)" % (2 * e["boss_r"], x(f["x"]), e["lid_dx"], [y(v) for v in e["lid_y"]], e["mag_d"] + 0.2, e["mag_t"] + 0.1, ins["hole"], ins["depth"]), "mm"),
        ("코튼롤 잡이 리브", "벽에서 1 나옴, y %g → %g" % (y(e["pinch"][0]), y(e["pinch"][1])), "mm"),
        ("재료·출력", "PETG, 기둥 발이 판에 닿게 세워 출력", "출력 방향은 README 참고"),
    ]
    m143 = [
        ("데크 101", "발 아래 면 z 0 = 데크 윗면 z %g, 나사 M3 × 8 두 개가 데크 아래에서" % f["post_foot_z"], "데크 구멍 Ø3.4 (x %g, y %g ±%g)" % (px, f["post_y"], ft["dy"])),
        ("뚜껑 143l", "뚜껑 기둥 윗면 z %g = 뚜껑 아래 면" % z(f["wall_top"]), "자석·핀 자리 같은 식"),
        ("관 144hf", "노즐 바브에 7 mm 끼움", "펌프에서 옴"),
        ("관 144hd", "물빠짐 바브에 7 mm 끼움", "프레임 밖으로"),
        ("코튼롤 142n", "앞벽 구멍 축 = 솜 축", "바깥 끝이 물길 바닥에 닿음"),
        ("마킹실 벽 120", "앞벽 바깥 y %g = 벽 바깥 면 y %g (붙이지 않음, 솜만 벽 구멍 Ø%g 지남)" % (y(f["ch_y0"]), f["ch_y0"], 2 * f["wall_hole_r"]), "물이 물길 안에서 끝남"),
    ]
    L = math.dist((f["tip_y"], f["tip_z"]), (f["end_y"], f["end_z"]))
    H = FP.HB
    return [
        ("143", "P143_물길그릇.FCStd", "물길·기둥·노즐 143", "설계 (3D 프린트 PETG)", "D5g_feeder_uln.feed_trough + feeder_detail_shapes", tr, d143, m143, OUT),
        ("143l", "P143l_뚜껑.FCStd", "급이 방 뚜껑 143l", "설계 (3D 프린트 PETG)", "D5g_feeder_uln.trough_lid + 자석·핀",
         lid, [("판 두께", "2", "mm"), ("자석 자리", "아래에서 Ø%.1f × %.1f, 2개" % (e["mag_d"] + 0.2, e["mag_t"] + 0.1), "물길 쪽 자석과 극 맞춤"),
               ("핀", "Ø%g × %g, 2개 (대각)" % (e["pin_d"], e["pin_L"]), "물길 기둥 구멍 Ø4에 들어감"), ("손잡이 혀", "16 × %g (+y 끝)" % e["tab"], "손가락으로 들어 올림")],
         [("143", "아래 면 z 0 = 143 뚜껑 기둥 윗면", "자석·핀 자리 = 143 기둥 축")], OUT),
        ("144b", "P144b_병펌프걸이.FCStd", "급이 병·펌프 걸이 144b", "설계 (3D 프린트 PETG)", "D5g_feeder_pump.holder", hb,
         [("판", "%g × %g × %g (x × z × 두께), M5 구멍 Ø5.5 2개 (x %s, z %g)" % (H["x1"] - H["x0"], H["z1"] - H["z0"], H["t"], [round(v - o["144b"].x, 1) for v in H["bolt_x"]], round(H["bolt_z"] - o["144b"].z, 1)), "mm"),
          ("병 컵", "안 Ø%g, 바닥 3, 높이 15" % (FP.BOT["d"] + 2 * H["gap"]), "병을 위로 들어 꺼냄"),
          ("병 고리", "안 Ø%g, z %g → %g" % (FP.BOT["d"] + 2 * H["gap"], H["ring_z"][0] - o["144b"].z, H["ring_z"][1] - o["144b"].z), ""),
          ("펌프 받침", "모터 Ø%.1f 자리 + 케이블 타이 홈 2" % (FP.PUMP["motor_d"] + 1), "펌프 몸 구멍 위치 몰라서 타이로 [추측]")],
         [("레일 100b (y +170, 데크 높이)", "판 뒤 면 = 레일 바깥 면 y %g, M5 × 8 + 드롭인 T너트 2" % H["y_face"], "프레임 조립 뒤에도 붙임")], OUT),
        ("144n", "P144n_병250mL.FCStd", "급이 병 250 mL (Nalgene 2104-0008) + 뚜껑", "구매", "Ø61 × 131 [가능성 높음 — 판매처 표], 뚜껑 모양 [추측]", bt,
         [("병", "Ø%g × %g" % (FP.BOT["d"], FP.BOT["h"]), "HDPE"), ("뚜껑 구멍", "관 Ø5 + 공기 Ø2", "드릴로 뚫음")], [("144b", "바닥 = 컵 바닥 윗면", "")], OUT),
        ("144p", "P144p_펌프.FCStd", "연동 펌프 Adafruit 3910", "구매", "모터 Ø27.8, 길이 66.8 [확실 — Adafruit] · 머리·관 자리 [추측]", pm,
         [("전기", "5~6 V, 0.5 A, UNO 2 D6 → MOSFET Q3", ""), ("유량", "최대 100 mL/min (6 V)", "5 V에서 약 83 [추측]")], [("144b", "모터 아래 끝 = 받침 위", "케이블 타이 2")], OUT),
        ("142n", "P142n_코튼롤.FCStd", "코튼롤 2호 (치과 재료)", "구매", "Ø10 × 38 [가능성 높음 — 판매처 표]", shape_142n(),
         [("크기", "Ø%g × %.2f (모델 길이 = 안 끝 → 바깥 끝)" % (2 * f["roll_r"], L), "mm")], [("143", "앞벽 구멍 축 위", "")], OUT),
        ("143m", "P143m_자석6x2.FCStd", "자석 Ø6 × 2 N35", "구매", "일반 규격 [가능성 높음]", magnet(),
         [("크기", "Ø%g × %g" % (e["mag_d"], e["mag_t"]), "니켈 도금, 접착제로 고정")], [("143·143l", "자리 Ø%.1f에 끼움" % (e["mag_d"] + 0.2), "")], OUT),
        ("144h_", "P144h_관_병펌프.FCStd", "실리콘 관 3.5 × 5 (병 → 펌프)", "구매", "조립 자리 그대로", tb["144h_"], [("관", "안 3.5 · 바깥 5", "식품용")], [("144n·144p", "뚜껑 구멍 → 펌프 들어옴", "")], OUT),
        ("144hf_", "P144hf_관_펌프노즐.FCStd", "실리콘 관 3.5 × 5 (펌프 → 노즐)", "구매", "조립 자리 그대로", tb["144hf_"], [("관", "안 3.5 · 바깥 5", "식품용")], [("144p·143", "펌프 나감 → 노즐 바브", "")], OUT),
        ("144hd_", "P144hd_관_물빠짐.FCStd", "실리콘 관 3.5 × 5 (물빠짐 → 바깥)", "구매", "조립 자리 그대로", tb["144hd_"], [("관", "안 3.5 · 바깥 5", "식품용, 끝은 열림")], [("143", "물빠짐 바브", "")], OUT),
        ("94459A130", "P94459A130_인서트M3.FCStd", "열 압입 인서트 M3 (McMaster 94459A130)", "구매", "", shape_mcm("94459A130"),
         [("설치 길이", "4.3", "mm"), ("구멍", "최대 Ø4, 최소 두께 5.1", "McMaster 표")], [("143 발 구멍", "큰 끝 z 0 = 구멍 입구", "")], VOUT),
        ("92000A118", "P92000A118_냄비M3x8.FCStd", "냄비머리 십자 M3 × 8 (McMaster 92000A118)", "구매", "", shape_mcm("92000A118"),
         [("머리", "Ø6 × 2.5, PH1", "mm")], [("데크", "머리 밑면 z 0 = 데크 아래 면", "")], VOUT),
    ]


def _sheet(doc, name, rows, head):
    sh = doc.addObject("Spreadsheet::Sheet", name)
    for c, t in zip("ABC", head):
        sh.set(c + "1", t)
    for i, r in enumerate(rows, start=2):
        for c, t in zip("ABC", r):
            sh.set("%s%d" % (c, i), "'" + str(t))
    return sh


def parts():
    os.makedirs(OUT, exist_ok=True); os.makedirs(VOUT, exist_ok=True)
    made = {}
    for num, fn, name, kind, src, shp, dims, mates, d in part_defs():
        if isinstance(shp, tuple):
            shp, src = shp
        nm = os.path.splitext(fn)[0]
        if nm in App.listDocuments():
            App.closeDocument(nm)
        doc = App.newDocument(nm)
        o = doc.addObject("Part::Feature", "Body")
        o.Label, o.Shape = "%s %s" % (num, name), shp
        if App.GuiUp and getattr(o, "ViewObject", None):      # (16:26 서현) 기본 파일 색 규칙: 3D 프린트 = 파랑, 그 밖 = 회색 (D5g_print_color 와 같음)
            import D5g_print_color as PCOL
            o.ViewObject.ShapeColor = PCOL.PRINT if kind.startswith("설계") else PCOL.OTHER
        _sheet(doc, "치수", [("구분", kind, ""), ("출처", src, "")] + dims, ("항목", "값", "비고"))
        _sheet(doc, "맞춤", mates, ("상대", "맞는 자리", "비고"))
        doc.recompute()
        path = os.path.join(d, fn)
        doc.saveAs(path)
        bb = shp.BoundBox
        made[num] = dict(file=os.path.relpath(path, HERE), solids=len(shp.Solids), volume_cm3=round(shp.Volume / 1000, 2),
                         mass_g=round(shp.Volume / 1000 * PETG, 1) if kind.startswith("설계") else None,
                         size=[round(bb.XLength, 2), round(bb.YLength, 2), round(bb.ZLength, 2)], src=src)
    return made


# ---------------- 조립: 자리 ----------------
def placements():
    FU, f, e, ins, ft = _fd()
    o = origins()
    px = f["x"] + f["post_dx"]
    d = V(0, f["end_y"] - f["tip_y"], f["end_z"] - f["tip_z"])
    flip = R(V(1, 0, 0), 180)
    P = [("143", "143", App.Placement(o["143"], R())),
         ("143l", "143l", App.Placement(o["143l"], R())),
         ("142n", "142n", App.Placement(o["142n"], R(V(0, 0, 1), d))),
         ("144b", "144b", App.Placement(o["144b"], R())),
         ("144n", "144n", App.Placement(o["144n"], R())),
         ("144p", "144p", App.Placement(o["144p"], R())),
         ("144h_", "144h", App.Placement()), ("144hf_", "144hf", App.Placement()), ("144hd_", "144hd", App.Placement())]
    k = 0
    for sx in (-1, 1):                                  # 자석: 물길 기둥 (대각 2) + 뚜껑 (같은 자리 위)
        for i, cy in enumerate(e["lid_y"]):
            if (sx < 0) == (i == 0):
                k += 1
                cx = f["x"] + sx * e["lid_dx"]
                P.append(("143m", "143m_%d" % k, App.Placement(V(cx, cy, f["wall_top"] - e["mag_t"]), R())))
                P.append(("143m", "143mm_%d" % k, App.Placement(V(cx, cy, f["wall_top"]), R())))
    for j, sy in enumerate((-ft["dy"], ft["dy"]), start=1):
        P.append(("94459A130", "143fi_%d" % j, App.Placement(V(px, f["post_y"] + sy, f["post_foot_z"]), flip)))
        P.append(("92000A118", "143f_%d" % j, App.Placement(V(px, f["post_y"] + sy, f["post_foot_z"] - 5.0), flip)))
    return P


COLOR = {}   # 색은 부품 파일 Body 색 그대로 (프린트 파랑 · 그 밖 회색 — D5g_print_color)


def assemble():
    files = {p[0]: os.path.join(p[8], p[1]) for p in part_defs()}
    src = {}
    for num, path in files.items():
        nm = os.path.splitext(os.path.basename(path))[0]
        src[num] = App.listDocuments().get(nm) or App.openDocument(path)
    if "A143_급이방_조립" in App.listDocuments():
        App.closeDocument("A143_급이방_조립")
    asm = App.newDocument("A143_급이방_조립")
    apath = os.path.join(OUT, "A143_급이방_조립.FCStd")
    asm.saveAs(apath)                       # 바깥 파일 링크는 조립 파일이 먼저 저장돼 있어야 함
    links = []
    for num, tag, pl in placements():
        lk = asm.addObject("App::Link", "L_" + tag)
        lk.LinkedObject = src[num].getObject("Body")
        lk.LinkTransform = True                 # 부품 파일 Body의 자리(자기 원점으로 옮긴 것)를 살림 — 없으면 링크가 그 자리를 버려서 부품이 엉뚱한 곳에 놓임 (11/10 확인)
        lk.Placement = pl
        lk.Label = "%s ← %s" % (tag, os.path.basename(files[num]))
        if getattr(lk, "ViewObject", None):
            try:
                lk.ViewObject.OverrideMaterial = True
                lk.ViewObject.OverrideMaterial = False
            except Exception:
                pass
        links.append((num, tag, lk))
    asm.recompute()
    asm.save()
    return asm, links


# ---------------- 검사 ----------------
EXPECT = {("94459A130", "143"): "인서트가 녹아 박히는 부피 (구멍 Ø4 < 인서트 바깥 Ø4.74)",
          ("92000A118", "94459A130"): "나사산 물림",
          ("144hf_", "143"): "관이 노즐 바브에 끼움 (바브 Ø4.6 > 관 안 3.5)", ("144hd_", "143"): "관이 물빠짐 바브에 끼움",
          ("144h_", "144p"): "관이 펌프 관 자리에 끼움", ("144hf_", "144p"): "관이 펌프 관 자리에 끼움",
          ("144h_", "144n"): "관이 뚜껑 구멍을 지나 병 안으로"}


def check(links):
    FU, f, e, ins, ft = _fd()
    sh = {tag: (num, Part.getShape(lk)) for num, tag, lk in links}
    r = {"overlaps_ok": [], "overlaps_bad": []}
    tags = list(sh)
    for i, a in enumerate(tags):
        for b in tags[i + 1:]:
            na, sa = sh[a]; nb, sb = sh[b]
            if not sa.BoundBox.intersect(sb.BoundBox):
                continue
            v = sa.common(sb).Volume
            if v <= 0.01:
                continue
            why = EXPECT.get((na, nb)) or EXPECT.get((nb, na))
            # 인서트와 나사는 같은 자리끼리만 허용 (번호 같음: 143i_k ↔ 143t_k, 143fi_j ↔ 143f_j)
            if why and {na, nb} == {"92000A118", "94459A130"} and a.split("_")[-1] != b.split("_")[-1]:
                why = None
            (r["overlaps_ok"] if why else r["overlaps_bad"]).append((a, b, round(v, 2), why or ""))
    # 맞춤 자리 (숫자)
    r["mates"] = {
        "자석·핀 자리 = 뚜껑·물길 같은 식": "FDX lid_dx·lid_y — 모양 겹침 0으로 확인",
        "발 나사 끝 z": f["post_foot_z"] - 5.0 + 8.0,
        "발 나사 물림": round(min(ins["L"], 8.0 - 5.0), 2),
        "발 나사 끝 ↔ 발 윗면": round(f["post_foot_z"] + ft["t"] - (f["post_foot_z"] + 3.0), 2),
        "발 인서트 최소 두께 5.1 ≤ 발 두께": ft["t"],
    }
    # 물·솜 (feeder_check.py 와 같은 계산)
    try:
        import feeder_check as FC
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ok = FC.check(FC.load_fd(), "부품 조립")
        r["feeder_check"] = dict(ok=ok, text=buf.getvalue())
    except Exception as ex:
        r["feeder_check"] = dict(ok=None, text=repr(ex))
    return r


def run():
    import sys
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    made = parts()
    asm, links = assemble()
    rep = dict(parts=made, check=check(links))
    json.dump(rep, open(os.path.join(OUT, "_check.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    return rep
