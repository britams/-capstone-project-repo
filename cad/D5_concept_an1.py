# -*- coding: utf-8 -*-
"""D5 개념 모델 — 안 1 바닥 승강형 (CAP-AI-10)

FreeCAD에서 실행 (MCP execute_code 또는 매크로). 모든 치수는 **잠정(개략 비율)** —
D6 설계 변수표가 나오면 P 사전 값만 바꿔 다시 생성한다.
단위 mm. 원점 = 상용 트랩 차양막 윗면 중심, z 위쪽.
도면부호는 design/2026-10-28_D5_개념설계_안1.md 와 같다.
"""
import FreeCAD as App
import Part

DOC_NAME = "D5_concept_an1"
SAVE_PATH = None  # 예: r"C:\Users\Seohyun_Lee\Desktop\capstone design_이서현\CAD files\D5_concept_an1.FCStd"
FLOOR_STATE = "down"  # "down" = 도 2(a) 대기·진입, "up" = 도 2(b) 자세 고정·마킹

# ---- 잠정 치수 (D6에서 확정) ----
P = dict(
    hole_r=30,          # 102 하부 결합부 반지름 (차양막 구멍, 실측 전)
    body_R=65,          # 100 하우징 바깥 반지름
    body_H=150,         # 100 하우징 높이
    wall=3,             # 벽 두께
    cham_W=40,          # 120 마킹실 안쪽 폭 (여왕벌 몸길이 약 30 + 여유)
    cham_cx=15,         # 120 마킹실 중심 x (입구가 차양막 구멍 안쪽에 오도록 옆으로)
    cham_z0=30,         # 120 마킹실 바닥 높이
    cham_H=36,          # 120 마킹실 높이
    entry_r=4.5,        # 110 입구 반지름 (지름 9 — 시판 봄철 트랩 기준, 표본으로 확정)
    entry_x=-20,        # 110 입구 위치 (차양막 구멍 반지름 hole_r - 벽 안쪽이어야 함)
    grid_pitch=4.5,     # 130 격자 피치
    grid_hole=3.0,      # 130 격자 눈 (마커 팁 통과, 머리 못 빠짐 — 표본으로 확정)
    grid_t=1.5,         # 130 격자 두께
    floor_t=3,          # 140 승강 바닥 두께
    floor_stroke=22,    # 140 바닥 행정 (마킹실 높이 - 말벌 몸 높이 근처)
    marker_r=5,         # 160 마커 반지름
    marker_L=70,        # 160 마커 길이
    marker_park_x=26,   # 160 대기 위치 (마킹실 중심에서)
    top_ring_r=30,      # 104 상부 결합부 반지름
)


def box(dx, dy, dz, x, y, z):
    return Part.makeBox(dx, dy, dz, App.Vector(x, y, z))


def cyl(r, h, x, y, z, d=App.Vector(0, 0, 1)):
    return Part.makeCylinder(r, h, App.Vector(x, y, z), d)


def tube(R, r, h, x, y, z, d=App.Vector(0, 0, 1)):
    return cyl(R, h, x, y, z, d).cut(cyl(r, h, x, y, z, d))


def build(doc):
    w = P["wall"]
    W = P["cham_W"]
    cx = P["cham_cx"]
    assert abs(P["entry_x"]) + P["entry_r"] + 2 <= P["hole_r"] - w, "입구가 차양막 구멍 밖에 있음"
    assert P["entry_x"] + P["entry_r"] + 2 <= cx - W / 2 - w, "입구 관이 마킹실과 겹침"
    z0 = P["cham_z0"]
    H = P["cham_H"]
    parts = {}

    # 상용 트랩 (참고, 가상선 역할) — 차양막 일부
    parts["REF_awning"] = cyl(130, 4, 0, 0, -4).cut(cyl(P["hole_r"], 4, 0, 0, -4))

    # 102 하부 결합부, 104 상부 결합부
    parts["102_lower_coupling"] = tube(P["hole_r"], P["hole_r"] - w, 12, 0, 0, -12)
    parts["104_upper_coupling"] = tube(P["top_ring_r"], P["top_ring_r"] - w, 10, 0, 0, P["body_H"])

    # 100 하우징 (얇은 원통 껍데기 + 바닥판)
    shell = tube(P["body_R"], P["body_R"] - w, P["body_H"], 0, 0, 0)
    base = cyl(P["body_R"], w, 0, 0, 0).cut(cyl(P["entry_r"] + 2, w, P["entry_x"], 0, 0))
    lid = cyl(P["body_R"], w, 0, 0, P["body_H"] - w).cut(cyl(P["top_ring_r"] - w, w, 0, 0, P["body_H"] - w))
    parts["100_housing"] = shell.fuse(base).fuse(lid)

    # 110 입구 (세로 관) + 112 입구 문
    parts["110_entry"] = tube(P["entry_r"] + 2, P["entry_r"], z0 + 10, P["entry_x"], 0, 0)
    parts["112_entry_gate"] = box(10, 14, 2, P["entry_x"] - 5, -7, z0 + 10)
    parts["114_entry_sensor"] = box(6, 4, 6, P["entry_x"] - 3, 8, z0 - 2)

    # 120 마킹실 (사각 관, 투명·미끄러운 플라스틱)
    outer = box(W + 2 * w, W + 2 * w, H, cx - W / 2 - w, -W / 2 - w, z0)
    inner = box(W, W, H, cx - W / 2, -W / 2, z0)
    side_in = box(w + 1, 2 * P["entry_r"] + 2, 2 * P["entry_r"] + 2, cx - W / 2 - w - 0.5, -P["entry_r"] - 1, z0 + 2)
    parts["120_marking_chamber"] = outer.cut(inner).cut(side_in)
    # 입구 관과 마킹실을 잇는 짧은 수평 통로
    parts["110_entry"] = parts["110_entry"].fuse(
        tube(P["entry_r"] + 2, P["entry_r"], (cx - W / 2) - P["entry_x"],
             P["entry_x"], 0, z0 + 2 + P["entry_r"] + 1, App.Vector(1, 0, 0)))

    # 130 격자망 (마킹실 천장)
    g = box(W + 2 * w, W + 2 * w, P["grid_t"], cx - W / 2 - w, -W / 2 - w, z0 + H)
    n = int(W // P["grid_pitch"])
    off = -(n - 1) * P["grid_pitch"] / 2
    holes = []
    for i in range(n):
        for j in range(n):
            hx = cx + off + i * P["grid_pitch"]
            hy = off + j * P["grid_pitch"]
            holes.append(box(P["grid_hole"], P["grid_hole"], P["grid_t"],
                             hx - P["grid_hole"] / 2, hy - P["grid_hole"] / 2, z0 + H))
    parts["130_grid"] = g.cut(Part.makeCompound(holes))

    # 140 승강 바닥 + 142 급이구
    fz = z0 + 1 + (P["floor_stroke"] if FLOOR_STATE == "up" else 0)
    floor = box(W - 1, W - 1, P["floor_t"], cx - (W - 1) / 2, -(W - 1) / 2, fz)
    parts["140_lift_floor"] = floor.cut(cyl(3, 1.5, cx + W / 2 - 8, 0, fz + P["floor_t"] - 1.5))
    parts["142_feeder"] = cyl(3, 1.5, cx + W / 2 - 8, 0, fz + P["floor_t"] - 1.5)

    # 146 완충 스프링, 148 하중 센서, 150 바닥 구동부 (리드스크루 + 모터)
    parts["146_spring"] = tube(5, 4, 8, cx, 0, fz - 8)
    parts["148_load_cell"] = box(12, 12, 4, cx - 6, -6, fz - 12)
    parts["150_floor_drive"] = cyl(2, fz - 12 - 8, cx, 0, 8).fuse(cyl(14, 5, cx, 0, w))

    # 144 먹이통·심지
    parts["144_food_tank"] = cyl(9, 18, -36, -28, w)  # 심지 경로는 D6에서

    # 160 마커 (FLOOR_STATE=up 이면 마킹 위치, 아니면 대기 위치) + 162 홀더 + 164 구동부 + 166 캡
    mx = cx if FLOOR_STATE == "up" else cx + P["marker_park_x"]
    mz = z0 + H + P["grid_t"] + (0 if FLOOR_STATE == "up" else 12)
    parts["160_marker"] = cyl(P["marker_r"], P["marker_L"], mx, 0, mz).fuse(
        Part.makeCone(0.8, P["marker_r"], 6, App.Vector(mx, 0, mz - 6)))
    parts["162_marker_holder"] = tube(P["marker_r"] + 3, P["marker_r"], 20, mx, 0, mz + 30)
    parts["164_marker_drive"] = box(12, 23, 30, mx + P["marker_r"] + 3, -11.5, mz + 25)
    parts["166_marker_cap"] = tube(P["marker_r"] + 2, P["marker_r"] + 0.5, 12,
                                   cx + P["marker_park_x"], 0, z0 + H + P["grid_t"])

    # 170 분기 문, 172 격리 통로(→ 상용 포획통), 174 방생 출구(→ 밖, 한 방향 깔때기)
    parts["170_branch_gate"] = box(2, 16, 16, cx + W / 2 + w, -8, z0 + H - 18)
    parts["172_isolation_path"] = tube(6, 4.5, P["body_H"] - (z0 + H - 10), cx - W / 2 - w - 8, -12, z0 + H - 10)
    parts["174_release_exit"] = tube(7, 5, P["body_R"] - (cx + W / 2 + w), cx + W / 2 + w, 0, z0 + H - 12,
                                     App.Vector(1, 0, 0)).fuse(
        Part.makeCone(10, 3, 10, App.Vector(P["body_R"] - 2, 0, z0 + H - 12), App.Vector(1, 0, 0)))

    # 180 카메라, 182 조명, 190 제어부
    parts["180_camera"] = box(25, 24, 12, cx - 12.5, -12, P["body_H"] - 30)
    parts["182_light"] = tube(16, 13, 3, cx, 0, P["body_H"] - 36)
    parts["190_controller"] = box(24, 50, 20, -52, -25, 95)

    gray = {"100_housing": (0.85, 0.85, 0.85), "120_marking_chamber": (0.75, 0.75, 0.75),
            "REF_awning": (0.9, 0.9, 0.9)}
    transparent = {"100_housing": 80, "120_marking_chamber": 55, "REF_awning": 70, "104_upper_coupling": 40}
    for name, shp in parts.items():
        o = doc.addObject("Part::Feature", name)
        o.Shape = shp
        if App.GuiUp:
            vo = o.ViewObject
            vo.ShapeColor = gray.get(name, (0.55, 0.55, 0.55))
            vo.LineColor = (0.1, 0.1, 0.1)
            vo.Transparency = transparent.get(name, 0)
    return parts


def section(doc, parts):
    """앞쪽 절반(y<0)을 잘라 낸 측단면용 사본 그룹."""
    cutter = box(400, 200, 400, -200, -200, -100)
    grp = doc.addObject("App::DocumentObjectGroup", "SECTION_y0")
    for name, shp in parts.items():
        s = shp.cut(cutter)
        if s.isNull() or s.Volume < 1e-6:
            continue
        o = doc.addObject("Part::Feature", "SEC_" + name)
        o.Shape = s
        grp.addObject(o)
        if App.GuiUp:
            o.ViewObject.ShapeColor = (0.7, 0.7, 0.7)
            o.ViewObject.LineColor = (0.0, 0.0, 0.0)
    return grp


if DOC_NAME in App.listDocuments():
    App.closeDocument(DOC_NAME)
doc = App.newDocument(DOC_NAME)
parts = build(doc)
sec = section(doc, parts)
doc.recompute()
if SAVE_PATH:
    doc.saveAs(SAVE_PATH)
print("objects:", len(doc.Objects), "floor:", FLOOR_STATE)
