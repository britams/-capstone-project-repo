# -*- coding: utf-8 -*-
"""D5e 한 마리 처리 동작 애니메이션 (CAP-AI-20)

FreeCAD GUI에서 D5e_module_kinematic.FCStd(또는 make_doc으로 만든 문서)를 연 상태로:
    ns = {}; exec(open("D5e_animate.py").read(), ns); ns["render"](doc, out_dir, f0, f1)
프레임마다 스프레드시트 'Joints'의 관절 값을 바꾸고 다시 계산 → 화면 저장 (전체 + 마킹실 확대).
글자(단계·실제 시간)는 frames.json을 보고 나중에 붙인다 (PIL). 시간은 보기 좋게 줄였고 실제 시간은 글자로 적는다.
"""
import json
import math
import os

FPS = 12
XM0, YM0 = 65.0, -40.0
UP, DOWN = 45.6, -20.0          # 펜 서보: 10 mm 들림 / 놓음
SUP = 0.56                      # 말벌 등 위 팁 받침
THX, THY = 59.4, 0.0            # 흉부 좌표 (격자 눈 위)
Z_FLOOR = 341.0                 # 바닥 윗면 (내림)
HZ = 3.75                       # 말벌 몸 높이 절반

# (시작 s, 끝 s, 단계 이름, 실제 시간 설명)
STEPS = [
    (0.0, 1.5, "대기: 입구 문 열림, 마커는 캡 컵", ""),
    (1.5, 4.5, "말벌이 입구 통로로 들어옴 (빛 게이트 감지)", "실제 몇 s~몇 분 (말벌 행동)"),
    (4.5, 5.5, "입구 문 닫힘 (MG90S + 혼 핀 미닫이)", "실제 약 1 s"),
    (5.5, 6.5, "카메라 판별 (종·크기)", "실제 약 2 s"),
    (6.5, 9.5, "바닥 상승 36.5 mm → 말벌 등을 격자에 붙임", "실제 18 s (28BYJ-48 15 rpm, T8 리드 8)"),
    (9.5, 10.5, "펜 들기 (SG90 혼 → 홀더 10 mm)", "실제 약 0.3 s"),
    (10.5, 13.5, "마커 X·Y 이동: 대기 → 흉부 좌표", "실제 최대 29 s (X·Y 동시, 2 mm/s)"),
    (13.5, 15.6, "찍기 2회 (팁이 격자 눈을 지나 흉부에)", "실제 약 1.6 s"),
    (15.6, 16.4, "펜 들기", ""),
    (16.4, 19.4, "마커 복귀 → 캡 컵 (마르지 않게)", "급이와 병렬"),
    (19.4, 20.4, "펜 놓음 = 캡", ""),
    (20.4, 21.9, "바닥 6.5 mm 내림 → 급이 자리", ""),
    (21.9, 24.0, "급이 = 잉크 건조", "실제 약 105 s 이하여야 R6 3분"),
    (24.0, 25.0, "방생 문 열림", "실제 약 1 s"),
    (25.0, 28.0, "말벌 방생 통로로 나감", "실제 10 s 가정"),
    (28.0, 29.0, "방생 문 닫힘", ""),
    (29.0, 31.5, "바닥 내림", "실제 15 s"),
    (31.5, 32.5, "입구 문 열림 → 다음 말벌", ""),
]
T_END = 32.5

# 관절 키프레임: 이름 → [(t, 값), ...]  (사이는 부드럽게)
KEY = {
    "door_entry": [(0, -60), (4.5, -60), (5.5, 60), (31.5, 60), (32.5, -60)],
    "door_iso": [(0, 60)],
    "door_rel": [(0, 60), (24.0, 60), (25.0, -60), (28.0, -60), (29.0, 60)],
    "floor": [(0, 0), (6.5, 0), (9.5, 36.5), (20.4, 36.5), (21.9, 30.0), (29.0, 30.0), (31.5, 0)],
    "xm": [(0, XM0), (10.5, XM0), (13.5, THX), (16.4, THX), (19.4, XM0)],
    "ym": [(0, YM0), (10.5, YM0), (13.5, THY), (16.4, THY), (19.4, YM0)],
    "horn": [(0, DOWN), (9.5, DOWN), (10.5, UP), (13.5, UP), (14.1, DOWN), (14.5, DOWN), (14.8, 15.0), (15.1, DOWN), (15.6, DOWN),
             (16.4, UP), (19.4, UP), (20.4, DOWN)],
    "support": [(0, 0), (13.4, 0), (13.5, SUP), (16.4, SUP), (16.5, 0)],
}
# 말벌 (가슴 중심 x, y, z_바닥기준 높이(바닥 위면 위로 HZ 또는 통로 바닥 위로), 방향)
HORNET_KEY = [(0, (-6.0, 0.0, 343.0 + HZ, 0)), (1.5, (-6.0, 0.0, 343.0 + HZ, 0)), (3.0, (30.0, 0.0, 343.0 + HZ, 0)),
              (3.4, (37.0, 0.0, Z_FLOOR + HZ, 0)), (4.5, (THX, THY, Z_FLOOR + HZ, 0)),
              (25.0, None), (26.0, (THX + 14, 0.0, None, 0)), (28.0, (150.0, 0.0, None, 0))]


def ease(u):
    return u * u * (3 - 2 * u)


def interp(keys, t):
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            if t1 == t0:
                return v1
            return v0 + (v1 - v0) * ease((t - t0) / (t1 - t0))
    return keys[-1][1]


BEND_R, Z_ENTRY = 20.0, 349.0     # 입구 통로 굽힘 (D5e)
ZB0 = Z_ENTRY - BEND_R
OFF = 6.0 - HZ                    # 통로 중심선에서 바닥(굽힘 안쪽 벽) 쪽으로


def hornet_path(t):
    """입구: 세로관(벽에 붙어 오름) → 굽힘 → 문 → 마킹실 바닥"""
    if t < 1.5:
        z = interp([(0, ZB0 - 30), (1.5, ZB0)], t)
        return OFF, 0.0, z, 90.0
    if t < 2.8:
        ph = math.radians(interp([(1.5, 0.0), (2.8, 90.0)], t))
        px, pz = BEND_R - BEND_R * math.cos(ph), ZB0 + BEND_R * math.sin(ph)
        return px + OFF * math.cos(ph), 0.0, pz - OFF * math.sin(ph), 90.0 - math.degrees(ph)
    x = interp([(2.8, BEND_R), (4.5, THX)], t)
    z = interp([(2.8, Z_ENTRY - OFF), (3.95, Z_ENTRY - OFF), (4.25, Z_FLOOR + HZ)], t)   # 배까지 문을 지난 뒤 바닥으로 (2 mm 내려섬)
    return x, 0.0, z, 0.0


def pose_at(t):
    J = {k: interp(v, t) for k, v in KEY.items()}
    floor = J["floor"]
    if t < 4.5:
        hx, hy, hz, hp = hornet_path(t)
    elif t < 25.0:
        hx, hy, hz, hp = THX, THY, Z_FLOOR + floor + HZ, 0.0
    else:                                                   # 방생: 바닥 윗면 = 방생 통로 바닥 (z 371)
        hx, hy, hz, hp = interp([(25.0, THX), (28.0, 150.0)], t), 0.0, Z_FLOOR + floor + HZ, 0.0
    J["hx"], J["hy"], J["hz"], J["hpitch"] = hx, hy, hz, hp
    J["dot"] = 1 if t >= 15.1 else 0
    J["hornet_visible"] = 1 if t < 27.1 else 0          # 한 방향 실리콘 깔때기(175)는 말벌이 밀면 벌어짐 — 모델은 닫힌 모양이라 그 앞에서 숨김
    return J


def step_at(t):
    for (a, b, name, real) in STEPS:
        if a <= t < b:
            return name, real
    return STEPS[-1][2], STEPS[-1][3]


def frames():
    n = int(round(T_END * FPS))
    return [(i, i / FPS) for i in range(n)]


def render(doc, out_dir, f0=0, f1=None, views=None, W=1280, H=720):
    import FreeCAD as App
    import FreeCADGui as Gui
    sh = doc.getObject("Joints")
    byl = {o.Label: o for o in doc.Objects}
    v = Gui.getDocument(doc.Name).ActiveView
    os.makedirs(out_dir, exist_ok=True)
    meta = []
    for i, t in frames()[f0:f1]:
        J = pose_at(t)
        for k in ("floor", "xm", "ym", "horn", "support", "door_entry", "door_iso", "door_rel", "hx", "hy", "hz", "hpitch"):
            sh.set(k, "%.4f" % J[k])
        doc.recompute()
        byl["REF_mark_dot"].ViewObject.Visibility = bool(J["dot"]) and bool(J["hornet_visible"])
        byl["REF_hornet"].ViewObject.Visibility = bool(J["hornet_visible"])
        for vname, cam_str in (views or {}).items():       # views: 이름 → v.getCamera() 문자열
            v.setCamera(cam_str)
            ww, hh = (W, H) if vname == "main" else (560, 420)
            v.saveImage(os.path.join(out_dir, "%s_%04d.png" % (vname, i)), ww, hh, "White")
        name, real = step_at(t)
        meta.append(dict(i=i, t=round(t, 3), step=name, real=real, J={k: round(J[k], 3) for k in ("floor", "xm", "ym", "horn", "door_entry", "door_rel")}))
    with open(os.path.join(out_dir, "frames_%04d_%04d.json" % (f0, f0 + len(meta))), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)
    return len(meta)


HIDE = {"100_frame", "190_pi5_aihat", "191_arduino_uno", "180_camera", "181_camera_bracket", "182_light_ring", "105_top_plate",
        "104_dome_coupling", "173_isolation_funnel", "REF_camera_view", "102_collar", "101_deck", "111_entry_funnel", "FitBox", "P204a", "P204b"}
TRANSP = {"172_isolation_duct": 45, "110_entry_duct": 45, "174_release_duct": 45, "120_chamber_walls": 72, "130_grid": 55,
          "112_entry_gate_housing": 45, "170_isolation_gate_housing": 45, "176_release_gate_housing": 45, "175_release_oneway": 30}


def setup_visibility(doc):
    for o in doc.Objects:
        if o.TypeId == "Spreadsheet::Sheet" or not hasattr(o, "ViewObject") or o.ViewObject is None:
            continue
        hide = o.Label in HIDE or o.Name in HIDE or o.Label.startswith("REF_trap")
        o.ViewObject.Visibility = not hide
        if o.Label in TRANSP:
            o.ViewObject.Transparency = TRANSP[o.Label]
        if o.Label == "130_grid":
            o.ViewObject.ShapeColor = (0.3, 0.3, 0.3)
        if o.Label == "REF_hornet":
            o.ViewObject.ShapeColor = (0.80, 0.42, 0.08)     # 잘 보이게 주황 (실물은 검은 갈색 + 주황 띠)
        if o.Label == "REF_mark_dot":
            o.ViewObject.ShapeColor = (1.0, 0.95, 0.0)


def make_views(doc):
    """전체(main)와 마킹실 확대(inset) 카메라 문자열"""
    import FreeCAD as App
    import FreeCADGui as Gui
    import Part
    V = App.Vector
    v = Gui.getDocument(doc.Name).ActiveView

    def cam_rot(d):
        d = V(*d).normalize()
        zc = d * -1
        up = V(0, 0, 1)
        yc = (up - zc * up.dot(zc)).normalize()
        return App.Rotation(yc.cross(zc), yc, zc, "ZYX")

    fb = doc.getObject("FitBox") or doc.addObject("Part::Feature", "FitBox")
    out = {}
    for name, box, d in (("main", (-20, 165, -115, 55, 250, 495), (1.0, 1.6, -1.1)),
                         ("inset", (26, 84, -26, 26, 336, 404), (0.45, 1.6, -0.32))):
        for o in doc.Objects:
            if hasattr(o, "ViewObject") and o.ViewObject is not None:
                o.ViewObject.Visibility = False
        fb.Shape = Part.makeBox(box[1] - box[0], box[3] - box[2], box[5] - box[4], V(box[0], box[2], box[4]))
        fb.ViewObject.Visibility = True
        v.setCameraType("Orthographic")
        v.setCameraOrientation(cam_rot(d))
        v.fitAll()
        out[name] = v.getCamera()
    setup_visibility(doc)
    return out
