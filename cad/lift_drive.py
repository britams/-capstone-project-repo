# -*- coding: utf-8 -*-
"""바닥 올리는 장치(바닥 구동) 다시 — 산 부품 치수대로, 떠 있는 것 없게 (서현 11/12 03:35, CAP-AI-62)

서현: "모터 올리는 부분 모터랑 설계도 카탈로그 보고 설계 다시 똑바로 해. 붕 떠 있는 것은 뇌를 사용하지 않고 만든 거잖아"
찾은 것 [확실 — 모델·git 기록]:
  1. 캐리지 158이 사라져 있었음 (부피 16,514 → 2,770 mm³). 11/12 00:5x edit_s2에서 press_parts가 캐리지와 받침 칸을 합칠 때
     원래 캐리지 모양이 '유효하지 않은 고체'(isValid False)라 합치기에서 빠짐 → 너트 159·볼 부싱 149가 공중에 뜸. 내 잘못.
  2. 돌림 막이 봉 157 (Ø4): 위 끝이 마킹실 바닥판 121의 헐거운 구멍 속, 아래 끝은 모터판에 얹혀만 있음 → 잡아 주는 것 없음
  3. 리드스크루 155 위 끝 z 322: 아무 데도 안 닿음 (모터 축 하나에만 매달림)
  4. 캐리지에 봉 157이 지나갈 부싱이 없었음
고침 (모두 산 부품 + 지금 자리):
  - 모터 28BYJ-48 (Adafruit 858 STEP) 그대로, 판 아래 귀 M3
  - 커플링 McMaster 4147N159: 8 × 5, 바깥 19.1, 길이 25.4, 멈춤 나사 [확실 — 판매처 표] (모델 치수 그대로 맞음)
  - 리드스크루 T8 (Tr8 × 8) z 242 → 334 (92 mm: 100 mm 사서 자름) — 위 끝을 플랜지 볼베어링 F688ZZ에
  - F688ZZ: 안 8 · 바깥 16 · 폭 5 · 플랜지 Ø18 × 1.1 [가능성 높음 — ISO 688 플랜지형 표준 치수] → 121에 Ø16 구멍, 플랜지는 아래에서 걸림
  - 너트 T8 황동 플랜지 (Ø22 × 3.5, 몸 Ø10.2, 길이 15, 구멍 4 × Ø3.5 PCD 16 45°) [가능성 높음 — 판매 대표값] → 캐리지 아래에 M3 × 8 네 개
  - 봉 157 Ø4: 아래는 모터판 구멍 Ø4.1을 지나 판 위에 축 칼라, 위는 121 아래 막힌 구멍(깊이 3) + 아래에 축 칼라 → 위아래 고정
  - 축 칼라 Ø4: 바깥 10 · 폭 5 · M3 멈춤 나사 [가능성 높음 — 판매 대표값] 2개
  - 캐리지 158 새로 (깨끗한 고체): x 37~73 · y ±20 · z 262~274 (옆판 안쪽과 1 mm), 볼 부싱 LM4UU 2 (149 누름 축, 157b 봉) 박음
    — 작고 단순한 상자라 3D 프린트 PETG 그대로 (알루미늄으로 바꿀지는 남은 결정). 누름 받침 칸·스위치 받침판은 press_parts 그대로
  - LM4UU: 안 4 · 바깥 8 · 길이 12 [확실 — 표준]
"""
import FreeCAD as App
import Part

V = App.Vector
SCR = (55.0, -13.0)            # 리드스크루·너트 축
ROD = (55.0, 13.0)             # 돌림 막이 봉 157
PSH = (65.0, 4.0)              # 누름 축 147
CAR = dict(x0=37.0, x1=73.0, y0=-20.0, y1=20.0, z0=262.0, z1=274.0)
NUT = dict(fl_r=11.0, fl_t=3.5, body_r=5.1, L=15.0, pcd=16.0, hole_r=1.75, z0=258.5)
BRG = dict(d=8.0, D=16.0, B=5.0, fl_D=18.0, fl_t=1.1)       # F688ZZ
COL = dict(d=4.0, D=10.0, W=5.0)                            # 축 칼라 Ø4
LM4 = dict(d=4.0, D=8.0, L=12.0)
Z = dict(plate=(225.0, 228.0), base=(330.0, 335.0), screw=(242.0, 334.0), rod=(225.0, 333.0))


def cyl(r, z0, z1, xy):
    return Part.makeCylinder(r, z1 - z0, V(xy[0], xy[1], z0))


def carriage_base():
    c = CAR
    car = Part.makeBox(c["x1"] - c["x0"], c["y1"] - c["y0"], c["z1"] - c["z0"], V(c["x0"], c["y0"], c["z0"]))
    car = car.cut(cyl(NUT["body_r"] + 0.1, c["z0"] - 1, c["z1"] + 1, SCR))                    # 너트 몸 Ø10.4
    import math
    for k in range(4):
        a = math.radians(45 + 90 * k)
        p = (SCR[0] + NUT["pcd"] / 2 * math.cos(a), SCR[1] + NUT["pcd"] / 2 * math.sin(a))
        car = car.cut(cyl(1.25, c["z0"] - 1, c["z0"] + 10, p))                                  # M3 셀프 탭 Ø2.5
    for xy in (PSH, ROD):
        car = car.cut(cyl(LM4["D"] / 2, c["z0"] - 1, c["z1"] + 1, xy))                          # LM4UU 박는 구멍 Ø8
    return car


def nut_screws():
    import math
    out = []
    for k in range(4):
        a = math.radians(45 + 90 * k)
        p = (SCR[0] + NUT["pcd"] / 2 * math.cos(a), SCR[1] + NUT["pcd"] / 2 * math.sin(a))
        zb = NUT["z0"]
        out.append(cyl(2.75, zb - 2.0, zb, p).fuse(cyl(1.5, zb, zb + 8.0, p)))                   # 냄비머리 M3 × 8
    return Part.makeCompound(out)


def collar(zc0, xy):
    c = cyl(COL["D"] / 2, zc0, zc0 + COL["W"], xy).cut(cyl(COL["d"] / 2, zc0 - 1, zc0 + COL["W"] + 1, xy))
    ss = Part.makeCylinder(1.5, 3.0, V(xy[0] + COL["D"] / 2 - 0.5, xy[1], zc0 + COL["W"] / 2), V(1, 0, 0))   # 멈춤 나사 머리 쪽
    return c.fuse(ss)


def bearing():
    z0, z1 = Z["base"]
    ring = cyl(BRG["D"] / 2, z0, z1, SCR).cut(cyl(BRG["d"] / 2, z0 - 1, z1 + 1, SCR))
    fl = cyl(BRG["fl_D"] / 2, z0 - BRG["fl_t"], z0, SCR).cut(cyl(BRG["d"] / 2, z0 - 2, z0 + 1, SCR))
    return ring.fuse(fl)


def lm4(xy, z0):
    return cyl(LM4["D"] / 2, z0, z0 + LM4["L"], xy).cut(cyl(LM4["d"] / 2, z0 - 1, z0 + LM4["L"] + 1, xy))


LABELS = {
    "158": "158_carriage (바닥 캐리지 — 36 × 40 × 12 상자 + 누름 받침 칸, LM4UU 2 박음, 너트 M3 × 4, 작은 3D 프린트 PETG)",
    "155": "155_lead_screw_T8 (Tr8 × 8, 100 mm 사서 92로 자름 — 아래 커플링, 위 F688ZZ, 구매)",
    "155b": "155b_screw_top_bearing (F688ZZ 플랜지 볼베어링 8 × 16 × 5 — 121에 박음, 구매)",
    "157": "157_guide_rod (돌림 막이 봉 Ø4 × 108 경화 — 아래 모터판·위 121 막힌 구멍, 칼라 2, 구매)",
    "157b": "157b_guide_bushing_LM4UU (봉 157 볼 부싱 — 캐리지에 박음, 구매)",
    "157c": "157c_rod_collars (축 칼라 Ø4 × 2 — 모터판 위·121 아래, M3 멈춤 나사, 구매)",
    "159s": "159s_nut_screws (M3 × 8 냄비머리 4 — T8 너트 플랜지 → 캐리지 셀프 탭, 구매)",
}


def _set(doc, head, shp, prefix="LD_"):
    old = [o for o in doc.Objects if o.Label.split(" ")[0].split("_")[0] == head and o.TypeId == "Part::Feature"]
    if old:
        o = old[0]
    else:
        o = doc.addObject("Part::Feature", prefix + head)
    o.Shape = shp
    if head in LABELS:
        o.Label = LABELS[head]
    return o


def apply(doc):
    """반환: (만든 것들, press 보고) — press_apply 대신 부름"""
    import D5g_feeder_uln as FU
    made = []
    # 1) 캐리지 + 누름 받침 칸·걸쇠·스위치 (press_parts는 깨끗한 캐리지 위에)
    for o in [o for o in doc.Objects if o.Label.startswith(("148c_", "227p"))]:
        doc.removeObject(o.Name)
    car, latch, sw, scr, rep = FU.press_parts(carriage_base())
    rep["carriage_valid"] = car.isValid()
    rep["carriage_vol"] = round(car.Volume)
    made.append(_set(doc, "158", car))
    for nm, shp in (("148c_spring_latch (걸쇠 — 축 147에 끼워 순간접착, +y 혀가 누름 스위치를 누름, 3D 프린트 PETG 작은 것)", latch),
                    ("227p_press_switch (KW11-3Z 누름 스위치 PSW — NC, 스프링 4.8 mm(0.5 N)에서 딸깍, UNO 1 A1)", sw),
                    ("227ps_press_switch_screws (M2 × 10 십자 냄비머리 2 — 받침판에 셀프 탭, 긴 구멍으로 힘 맞춤)", scr)):
        o = doc.addObject("Part::Feature", "P" + nm.split(" ")[0])
        o.Label, o.Shape = nm, shp
        made.append(o)
    # 2) 리드스크루 위 끝 + 베어링
    made.append(_set(doc, "155", cyl(4.0, Z["screw"][0], Z["screw"][1], SCR)))
    made.append(_set(doc, "155b", bearing()))
    # 3) 봉 157 + 칼라 2 + 부싱
    made.append(_set(doc, "157", cyl(2.0, Z["rod"][0], Z["rod"][1], ROD)))
    made.append(_set(doc, "157c", Part.makeCompound([collar(Z["plate"][1], ROD), collar(Z["base"][0] - COL["W"], ROD)])))
    made.append(_set(doc, "157b", lm4(ROD, CAR["z0"])))
    made.append(_set(doc, "159s", nut_screws()))
    # 4) 판 구멍: 모터판 152 (봉 Ø4.1 + 모터 귀 접시머리 자리), 121 (베어링 Ø16 관통, 봉 막힌 구멍 Ø4.1 깊이 3)
    p152 = [o for o in doc.Objects if o.Label.startswith("152_")]
    if p152:
        p152[0].Shape = p152[0].Shape.cut(cyl(2.05, Z["plate"][0] - 1, Z["plate"][1] + 1, ROD))
        plate_bolt_holes(doc)
    b121 = [o for o in doc.Objects if o.Label.startswith("121_")]
    if b121:
        s = b121[0].Shape.cut(cyl(BRG["D"] / 2, Z["base"][0] - 1, Z["base"][1] + 1, SCR))
        s = s.cut(cyl(2.05, Z["base"][0] - 1, Z["rod"][1], ROD))
        b121[0].Shape = s
    doc.recompute()
    return made, rep


def plate_bolt_holes(doc):
    """(11/12 05:10 서현 사진) 모터 귀 접시머리 M3가 모터판 152를 구멍 없이 지나고 있었음 → 나사 모양대로 파고 몸통 Ø3.4"""
    p = [o for o in doc.Objects if o.Label.startswith("152_")][0]
    bo = [o for o in doc.Objects if o.Label.startswith("153b")]
    s = p.Shape
    for b in (bo[0].Shape.Solids if bo else []):
        if b.BoundBox.ZMax < 240 and b.BoundBox.intersect(s.BoundBox):
            c = b.BoundBox.Center
            s = s.cut(b).cut(cyl(1.7, Z["plate"][0] - 1, Z["plate"][1] + 1, (c.x, c.y)))
    p.Shape = s
    return round(sum(b.common(s).Volume for b in (bo[0].Shape.Solids if bo else [])), 3)   # 0 이어야 함


MOVING = ("158_", "159", "157b", "149_", "146_", "147_", "148c_", "140_", "227p", "227ps")


def check(doc, made, travel=36.5):
    """(1) 새·바뀐 부품 ↔ 전부 겹침 (2) 바닥 0 → 36.5 올리는 동안 움직이는 것 ↔ 고정된 것 (4 mm마다)"""
    allow = (("159s", "158_"), ("159s", "159_"), ("157b", "158_"), ("149_", "158_"), ("155_", "159_"), ("155_", "154_"), ("155_", "155b"),
             ("157_", "157c"), ("157_", "157b"), ("157_", "152_"), ("157_", "121_"), ("155b", "121_"), ("227ps", "158_"), ("148c", "147_"))
    objs = [o for o in doc.Objects if o.TypeId == "Part::Feature" and not o.Shape.isNull() and o.Shape.Solids and "beam" not in o.Label
            and not o.Label.startswith("REF_")]          # REF_hornet·mark_dot: 바닥이 말벌을 격자로 누르는 것이 목적이라 뺌

    def vol(a, b):
        return sum(s.common(b).Volume for s in a.Solids if s.BoundBox.intersect(b.BoundBox))

    def ok(ka, kb):
        return any((ka.startswith(p) and kb.startswith(q)) or (kb.startswith(p) and ka.startswith(q)) for p, q in allow)
    hits = []
    for a in made:
        for o in objs:
            if o is a or (o in made and o.Name < a.Name) or not a.Shape.BoundBox.intersect(o.Shape.BoundBox):
                continue
            ka, kb = a.Label.split(" ")[0], o.Label.split(" ")[0]
            try:
                v = vol(a.Shape, o.Shape)
            except Exception as e:
                hits.append((ka, kb, "ERR %s" % e, "확인"))
                continue
            if v > 0.05:
                hits.append((ka, kb, round(v, 2), "허용" if ok(ka, kb) else "문제"))
    mv = [o for o in objs if o.Label.startswith(MOVING)]
    fx = [o for o in objs if not o.Label.startswith(MOVING)]
    sweep = []
    for k in range(0, 11):
        dz = min(travel, 4.0 * k)
        for a in mv:
            s = a.Shape.copy()
            s.translate(V(0, 0, dz))
            for b in fx:
                if not s.BoundBox.intersect(b.Shape.BoundBox):
                    continue
                ka, kb = a.Label.split(" ")[0], b.Label.split(" ")[0]
                if ok(ka, kb):
                    continue
                try:
                    v = vol(s, b.Shape)
                except Exception:
                    v = -1
                if v > 0.5 or v < 0:
                    sweep.append((dz, ka, kb, round(v, 1)))
    return hits, sweep
