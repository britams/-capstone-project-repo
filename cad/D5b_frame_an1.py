# -*- coding: utf-8 -*-
"""D5 개념 모델 2차 — 안 1 + 바닥에 서는 알루미늄 프로파일 프레임 (CAP-AI-13)

서현 결정 (2026-10-28):
- 상용 트랩에는 하중을 주지 않는다 (플라스틱이라 약함). 마킹 모듈·급이부·구동부는 **바닥에 서는 프레임**이 받친다.
- 원통 하우징 커버는 없앰. 외부 구조는 **알루미늄 프로파일** (크기 지정 없음 → 2020 기본값).
- 포획통은 모듈 위에 **돌려 끼움** (차양막 턱을 복사한 결합부). 차양막·몸통은 떼어 낼 수 없음.
- 모듈 아래는 차양막 턱에 하중 없이 덮이는 칼라(틈 막이)만.

단위 mm, 원점 = 바닥 중심, z 위쪽. 상용 트랩 치수는 design/2026-10-28_상용트랩_실측표.md
(줄자 측정 ±1~2 mm). ★ = 실측, 나머지는 잠정.
"""
import FreeCAD as App
import Part

DOC_NAME = "D5b_frame_an1"
SAVE_PATH = None
FLOOR_STATE = "down"   # "down" 대기·진입 / "up" 자세 고정·마킹

T = dict(                 # 상용 트랩 (참고 형상)
    body_r=100,           # 몸통·유인액 통 반지름 (잠정, 미측정)
    body_h=145,           # ★ H22 바닥 → 차양막 아래
    awning_top=180,       # ★ H21 바닥 → 차양막 윗면
    awning_r=130,         # 차양막 반지름 (제품 26 cm)
    hole_d=55,            # ★ D1 차양막 구멍 안지름
    ring_od=90,           # ★ D2 구멍 둘레 턱 바깥지름
    ring_h=10,            # h 턱 높이 (미측정, 잠정)
    dome_h=220,           # ★ H1 포획통 높이
    dome_r=100,           # 포획통 반지름 (잠정)
    dome_bottom_id=67,    # ★ D3 포획통 바닥 안지름
)
F = dict(                 # 프레임 (2020 프로파일)
    s=20,                 # 프로파일 단면
    half=170,             # 기둥 중심 위치 ±half (트랩 반지름 130 + 여유)
    rail_z=175,           # 모듈 받침 레일 아래면 높이 (차양막 r=70 지점 위)
    cross_y=75,           # 모듈 받침 가로 레일 y 위치 (차양막 턱 반지름 45 바깥)
    top_z=330,            # 위 레일 아래면 높이
)
M = dict(                 # 마킹 모듈 (이전 1차 모델의 잠정값 유지)
    plate_t=5,            # 받침판 두께 (아크릴)
    gap=3,                # 칼라와 차양막 턱 사이 틈 (하중 0)
    wall=3,
    cham_W=40, cham_cx=15, cham_dz=25, cham_H=36,
    entry_r=4.5, entry_x=-18,
    grid_pitch=4.5, grid_hole=3.0, grid_t=1.5,
    floor_t=3, floor_stroke=22,
    marker_r=5, marker_L=70, marker_park_x=26,
)


def box(dx, dy, dz, x, y, z):
    return Part.makeBox(dx, dy, dz, App.Vector(x, y, z))


def cyl(r, h, x, y, z, d=App.Vector(0, 0, 1)):
    return Part.makeCylinder(r, h, App.Vector(x, y, z), d)


def tube(R, r, h, x, y, z, d=App.Vector(0, 0, 1)):
    return cyl(R, h, x, y, z, d).cut(cyl(r, h, x, y, z, d))


def build(doc):
    P = {}
    # ---- 상용 트랩 (REF_, 하중 없음) ----
    P["REF_body"] = cyl(T["body_r"], T["body_h"], 0, 0, 0)
    P["REF_awning"] = Part.makeCone(T["awning_r"], T["ring_od"] / 2, T["awning_top"] - T["body_h"],
                                    App.Vector(0, 0, T["body_h"])).cut(
        cyl(T["hole_d"] / 2, 200, 0, 0, T["body_h"]))
    P["REF_ring"] = tube(T["ring_od"] / 2, T["hole_d"] / 2, T["ring_h"], 0, 0, T["awning_top"])

    s, h = F["s"], F["half"]
    base_z = F["rail_z"] + s + M["plate_t"]          # 모듈 받침판 윗면
    # ---- 100 프레임 (2020) ----
    fr = []
    for x in (-h, h):
        for y in (-h, h):
            fr.append(box(s, s, F["top_z"] + s, x - s / 2, y - s / 2, 0))          # 기둥
    for z in (0, F["rail_z"], F["top_z"]):
        for y in (-h, h):
            fr.append(box(2 * h - s, s, s, -h + s / 2, y - s / 2, z))              # x방향 레일
        if z == 0:
            for x in (-h, h):
                fr.append(box(s, 2 * h - s, s, x - s / 2, -h + s / 2, z))          # 바닥 y방향
    for x in (-h, h):
        fr.append(box(s, 2 * h - s, s, x - s / 2, -h + s / 2, F["rail_z"]))        # 받침 y방향
        fr.append(box(s, 2 * h - s, s, x - s / 2, -h + s / 2, F["top_z"]))
    for y in (-F["cross_y"], F["cross_y"]):
        fr.append(box(2 * h - s, s, s, -h + s / 2, y - s / 2, F["rail_z"]))        # 모듈 받침 가로
        fr.append(box(2 * h - s, s, s, -h + s / 2, y - s / 2, F["top_z"]))         # 위 가로
    P["100_frame_2020"] = Part.makeCompound(fr)

    # ---- 101 모듈 받침판 (프레임에 고정), 102 칼라 (차양막 턱 위에 하중 없이) ----
    plate = box(2 * F["cross_y"] + s + 20, 2 * F["cross_y"] + s, M["plate_t"],
                -F["cross_y"] - s / 2 - 10, -F["cross_y"] - s / 2, F["rail_z"] + s)
    P["101_module_plate"] = plate.cut(cyl(T["hole_d"] / 2 - 2, 50, 0, 0, F["rail_z"]))
    col_z0 = T["awning_top"] + T["ring_h"] + M["gap"]
    P["102_collar"] = tube(T["ring_od"] / 2 + 6, T["ring_od"] / 2 + 1, F["rail_z"] + s - col_z0 + 8,
                           0, 0, col_z0 - 8).fuse(
        tube(T["ring_od"] / 2 + 6, T["hole_d"] / 2 - 2, 3, 0, 0, F["rail_z"] + s - 3))

    # ---- 마킹 모듈 (받침판 위) ----
    w, W, cx = M["wall"], M["cham_W"], M["cham_cx"]
    z0 = base_z + M["cham_dz"]
    H = M["cham_H"]
    assert abs(M["entry_x"]) + M["entry_r"] + 2 <= T["hole_d"] / 2 - 2, "입구가 차양막 구멍 밖"
    P["110_entry"] = tube(M["entry_r"] + 2, M["entry_r"], z0 + 10 - (F["rail_z"] + s), M["entry_x"], 0, F["rail_z"] + s).fuse(
        tube(M["entry_r"] + 2, M["entry_r"], (cx - W / 2) - M["entry_x"], M["entry_x"], 0, z0 + 2 + M["entry_r"] + 1,
             App.Vector(1, 0, 0)))
    P["112_entry_gate"] = box(10, 14, 2, M["entry_x"] - 5, -7, z0 + 10)
    outer = box(W + 2 * w, W + 2 * w, H, cx - W / 2 - w, -W / 2 - w, z0)
    inner = box(W, W, H, cx - W / 2, -W / 2, z0)
    side = box(w + 1, 2 * M["entry_r"] + 2, 2 * M["entry_r"] + 2, cx - W / 2 - w - 0.5, -M["entry_r"] - 1, z0 + 2)
    P["120_marking_chamber"] = outer.cut(inner).cut(side)
    g = box(W + 2 * w, W + 2 * w, M["grid_t"], cx - W / 2 - w, -W / 2 - w, z0 + H)
    n = int(W // M["grid_pitch"]); off = -(n - 1) * M["grid_pitch"] / 2
    holes = [box(M["grid_hole"], M["grid_hole"], M["grid_t"], cx + off + i * M["grid_pitch"] - M["grid_hole"] / 2,
                 off + j * M["grid_pitch"] - M["grid_hole"] / 2, z0 + H) for i in range(n) for j in range(n)]
    P["130_grid"] = g.cut(Part.makeCompound(holes))
    fz = z0 + 1 + (M["floor_stroke"] if FLOOR_STATE == "up" else 0)
    P["140_lift_floor"] = box(W - 1, W - 1, M["floor_t"], cx - (W - 1) / 2, -(W - 1) / 2, fz)
    P["142_feeder"] = cyl(3, 1.5, cx + W / 2 - 8, 0, fz + M["floor_t"])
    P["146_spring"] = tube(5, 4, 8, cx, 0, fz - 8)
    P["148_load_cell"] = box(12, 12, 4, cx - 6, -6, fz - 12)
    P["150_floor_drive"] = cyl(2, fz - 12 - base_z, cx, 0, base_z)
    P["144_food_tank"] = cyl(12, 30, 70, -40, base_z)
    mx = cx if FLOOR_STATE == "up" else cx + M["marker_park_x"]
    mz = z0 + H + M["grid_t"] + (0 if FLOOR_STATE == "up" else 12)
    P["160_marker"] = cyl(M["marker_r"], M["marker_L"], mx, 0, mz).fuse(
        Part.makeCone(0.8, M["marker_r"], 6, App.Vector(mx, 0, mz - 6)))
    P["164_marker_drive"] = box(12, 23, 30, mx + M["marker_r"] + 3, -11.5, mz + 25)
    P["166_marker_cap"] = tube(M["marker_r"] + 2, M["marker_r"] + 0.5, 12, cx + M["marker_park_x"], 0, z0 + H + M["grid_t"])
    P["170_branch_gate"] = box(2, 16, 16, cx + W / 2 + w, -8, z0 + H - 18)
    P["174_release_exit"] = tube(7, 5, 60, cx + W / 2 + w, 0, z0 + H - 12, App.Vector(1, 0, 0)).fuse(
        Part.makeCone(10, 3, 10, App.Vector(cx + W / 2 + w + 60, 0, z0 + H - 12), App.Vector(1, 0, 0)))

    # ---- 위 받침판, 104 포획통 결합부 (차양막 턱 복사, 돌려 끼움), 172 격리 통로 ----
    top_plate_z = F["top_z"] + s
    tp = box(2 * F["cross_y"] + s + 20, 2 * F["cross_y"] + s, M["plate_t"],
             -F["cross_y"] - s / 2 - 10, -F["cross_y"] - s / 2, top_plate_z)
    P["105_top_plate"] = tp.cut(cyl(T["hole_d"] / 2, 50, 0, 0, top_plate_z - 10))
    P["104_dome_coupling"] = tube(T["ring_od"] / 2, T["hole_d"] / 2, T["ring_h"], 0, 0, top_plate_z + M["plate_t"])
    P["172_isolation_path"] = tube(6, 4.5, top_plate_z - (z0 + H - 10), cx - W / 2 - w - 8, -12, z0 + H - 10)

    # ---- 카메라, 조명, 제어부 (위 받침판 아래) ----
    P["180_camera"] = box(25, 24, 12, cx - 37.5, 3, top_plate_z - 40)   # 마커와 겹치지 않게 비켜 둠 (환류 7)
    P["182_light"] = tube(16, 13, 3, cx, 0, top_plate_z - 48)
    P["190_controller"] = box(60, 40, 25, -90, 40, base_z)

    # ---- 상용 포획통 (REF, 위 결합부에 돌려 끼움) ----
    dz = top_plate_z + M["plate_t"] + T["ring_h"]
    P["REF_dome"] = Part.makeSphere(T["dome_r"], App.Vector(0, 0, dz + T["dome_r"] - 30)).common(
        cyl(T["dome_r"] + 1, T["dome_h"], 0, 0, dz))

    col = {"100_frame_2020": (0.6, 0.6, 0.65)}
    tr = {"REF_body": 75, "REF_awning": 70, "REF_ring": 50, "REF_dome": 85, "101_module_plate": 60,
          "105_top_plate": 60, "120_marking_chamber": 50}
    for k, shp in P.items():
        o = doc.addObject("Part::Feature", k)
        o.Shape = shp
        if App.GuiUp:
            o.ViewObject.ShapeColor = col.get(k, (0.85, 0.85, 0.85) if k.startswith("REF") else (0.55, 0.55, 0.55))
            o.ViewObject.LineColor = (0.1, 0.1, 0.1)
            o.ViewObject.Transparency = tr.get(k, 0)
    return P


def section(doc, parts):
    cutter = box(600, 300, 900, -300, -300, -50)
    grp = doc.addObject("App::DocumentObjectGroup", "SECTION_y0")
    for k, shp in parts.items():
        s = shp.cut(cutter)
        if s.isNull() or s.Volume < 1e-6:
            continue
        o = doc.addObject("Part::Feature", "SEC_" + k)
        o.Shape = s
        grp.addObject(o)
        if App.GuiUp:
            o.ViewObject.ShapeColor = (0.95, 0.95, 0.95) if not k.startswith("100") else (0.7, 0.7, 0.75)
            o.ViewObject.LineColor = (0, 0, 0)
    return grp


if DOC_NAME in App.listDocuments():
    App.closeDocument(DOC_NAME)
doc = App.newDocument(DOC_NAME)
parts = build(doc)
section(doc, parts)
doc.recompute()
if SAVE_PATH:
    doc.saveAs(SAVE_PATH)
print("objects:", len(doc.Objects), "floor:", FLOOR_STATE)
