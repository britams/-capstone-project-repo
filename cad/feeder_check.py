# -*- coding: utf-8 -*-
"""급이 방 검사 — FreeCAD 없이 (서현, 2026-11-10, CAP-AI-56)

값은 cad/D5g_feeder_uln.py 의 FD 를 그대로 읽는다 (한 곳에서만 고침). 마킹실·바닥 치수는 D5e CH·FLOOR.
검사 6개 (모두 통과해야 함):
  1 열팽창: 맑은 날·햇빛에 튜브 안 공기(+수증기)가 부풀어 밀어낸 물 높이 + 표면장력 1 mm < 벽 구멍 아래 끝
  2 솜 바깥 끝이 물에 잠김 (1.5 mm 이상), 물길 바닥(364) 아래로 안 내려감
  3 솜이 벽 구멍 안에 들어감 (기울어진 솜이 벽 두께 3 mm를 지날 때 필요한 높이 ≤ 구멍 지름)
  4 솜이 마킹실 안으로 안 나옴 → 바닥(벽에서 0.5 mm 떨어짐)을 0~36.5 mm 올려도 겹침 0
  5 급이 높이에서 말벌 입이 솜 끝 높이에 있고, 말벌이 격자에 안 눌림
  6 솜이 빨아올릴 높이 ≤ 25 mm
실행: python cad/feeder_check.py   (현재 값 + 예전 50 mL 값 비교)
"""
import ast
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_fd():
    src = open(os.path.join(HERE, "D5g_feeder_uln.py"), encoding="utf-8").read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "FD":
            return {k.arg: ast.literal_eval(k.value) for k in node.value.keywords}
    raise SystemExit("FD 못 찾음")


CH = dict(cx=55.0, inner=40.0, wall=3.0, zc0=335.0, z_grid_bot=385.0)   # D5e_module_kinematic.py CH (마킹실 안 y −20~20, 벽 20~23)
FLOOR = dict(t=6.0, clear=0.5, stroke=36.5, top_rest=341.0)
HORNET_H = 7.5          # D5e HORNET h
MOUTH_ABOVE_FLOOR = 3.0  # 말벌 입 높이 [추측 — 표본으로 확인]
THREAD_R = {8.685: 9.625, 14.86: 14.86}   # 물 높이에 걸리는 튜브 바깥 반지름 (15 mL는 입구 쪽 나사 Ø19.25)
TUBE_V = {8.685: 17.0, 14.86: 52.0}       # 튜브 안 전체 부피 mL (가득 + 원뿔) [가능성 높음]
F_FEED = 31.0           # 급이 높이 (바닥 리프트 mm) — 관련코딩저장/pi_link/process.py, design/control_sim/trap_sim.py 와 같아야 함
WEATHER = {"맑은 날 5→30 °C": (5.0, 30.0, 0.0), "햇빛 5→45 °C + 기압 −2 kPa": (5.0, 45.0, 2.0)}


def psat(t):  # kPa, Magnus
    return 0.61094 * math.exp(17.625 * t / (t + 243.04))


def roll_geom(f):
    t = (f["x"], f["tip_y"], f["tip_z"]); e = (f["x"], f["end_y"], f["end_z"])
    d = [e[i] - t[i] for i in range(3)]; L = math.sqrt(sum(c * c for c in d)); u = [c / L for c in d]
    return t, u, L


def in_roll(p, t, u, L, r):
    d = [p[i] - t[i] for i in range(3)]; s = sum(d[i] * u[i] for i in range(3))
    if s < 0 or s > L:
        return False
    q = [d[i] - s * u[i] for i in range(3)]
    return q[0] ** 2 + q[1] ** 2 + q[2] ** 2 <= r * r


def water_area(f, t, u, L, h=0.2):
    """물 높이에서 열린 물 면적 mm² (그릇 − 튜브 + 물길 − 솜 − 코튼롤 잡이 리브)"""
    z = f["mouth_z"]; rt = THREAD_R.get(f["tube_r"], f["tube_r"]); A = 0.0
    y0 = f["ch_y0"]; ybowl = f["tube_y"] - f["bowl_ri"]
    xs = f["x"] - f["bowl_ri"]
    nx = int(2 * f["bowl_ri"] / h); ny = int((f["tube_y"] + f["bowl_ri"] - y0) / h)
    for i in range(nx):
        x = xs + (i + 0.5) * h
        for j in range(ny):
            y = y0 + (j + 0.5) * h
            rr = (x - f["x"]) ** 2 + (y - f["tube_y"]) ** 2
            inbowl = rr <= f["bowl_ri"] ** 2
            inch = abs(x - f["x"]) <= f["ch_w"] / 2 and y <= ybowl + 1
            if not (inbowl or inch) or rr <= rt ** 2 or in_roll((x, y, z), t, u, L, f["roll_r"]):
                continue
            A += h * h
    return A


def rise_mm(f, A, T1, T2, dP):
    k = (101.3 - psat(T1)) / (101.3 - dP - psat(T2)) * (T2 + 273.15) / (T1 + 273.15) - 1   # 부피 늘어나는 비율 (공기 + 수증기)
    Vt = TUBE_V.get(f["tube_r"], 50.0)
    dV = Vt * k / (1 + k) * 1000.0    # 가장 나쁜 채움 비율 (공기가 늘어난 만큼 밀어낼 물이 남아 있는 한계)
    return k, dV / A


def check(f, label):
    ok_all = True
    t, u, L = roll_geom(f)
    th = math.degrees(math.asin((f["tip_z"] - f["end_z"]) / L))
    hole_bot = f["wall_hole_z"] - f["wall_hole_r"]
    print("\n== %s ==  튜브 반지름 %.2f, 물 높이 %.1f, 솜 기울기 %.1f°, 솜 길이 %.2f" % (label, f["tube_r"], f["mouth_z"], th, L))

    def res(name, ok, txt):
        nonlocal ok_all
        ok_all &= ok
        print("  [%s] %s — %s" % ("통과" if ok else "실패", name, txt))
    A = water_area(f, t, u, L)
    worst = 0
    for nm, (T1, T2, dP) in WEATHER.items():
        k, h = rise_mm(f, A, T1, T2, dP); worst = max(worst, h)
        print("      %s: 부피 +%.1f %% → 물 +%.1f mm" % (nm, k * 100, h))
    top = f["mouth_z"] + worst + 1.0
    res("1 열팽창", top < hole_bot - 0.5, "물 면 %.0f mm², 최악 물 높이 %.1f (표면장력 1 포함) vs 벽 구멍 아래 끝 %.1f (여유 %.1f)" % (A, top, hole_bot, hole_bot - top))
    low = f["end_z"] - f["roll_r"] * math.cos(math.radians(th))
    imm = f["mouth_z"] - low
    res("2 솜 잠김", imm >= 1.5 and low >= f["floor_z"] + f["floor_t"] - 0.3, "솜 바깥 끝 가장 낮은 점 %.2f, 잠김 %.1f mm (물길 바닥 %.0f)" % (low, imm, f["floor_z"] + f["floor_t"]))
    need = 2 * f["roll_r"] / math.cos(math.radians(th)) + CH["wall"] * math.tan(math.radians(th))
    res("3 벽 구멍", need <= 2 * f["wall_hole_r"] + 0.2, "필요 높이 %.2f vs 구멍 Ø%.1f" % (need, 2 * f["wall_hole_r"]))
    # 4 바닥 겹침 (바닥판: x cx±19.5, y ±19.5, 두께 6, 윗면 341+lift)
    y_in = CH["inner"] / 2; fe = y_in - FLOOR["clear"]
    hits = []
    for lift in [i * 0.5 for i in range(int(FLOOR["stroke"] / 0.5) + 1)]:
        zt = FLOOR["top_rest"] + lift; n = 0; h = 0.25
        y = fe - 3.0
        while y < fe:
            z = zt - FLOOR["t"]
            while z < zt:
                x = f["x"] - f["roll_r"]
                while x <= f["x"] + f["roll_r"]:
                    if in_roll((x, y, z), t, u, L, f["roll_r"]):
                        n += 1
                    x += h
                z += h
            y += h
        if n:
            hits.append((lift, round(n * h ** 3, 1)))
    yi = min(f["tip_y"] - f["roll_r"] * math.sin(math.radians(th)), f["tip_y"])
    res("4 바닥과 솜", not hits, "솜 안 끝 가장 안쪽 y %.2f (벽 안 면 %.0f, 바닥 끝 %.1f), 겹침 %s" % (yi, y_in, fe, hits[:3] if hits else "0"))
    zf = FLOOR["top_rest"] + F_FEED; mouth = zf + MOUTH_ABOVE_FLOOR
    face = (f["tip_z"] - f["roll_r"] / math.cos(math.radians(th)), f["tip_z"] + f["roll_r"] / math.cos(math.radians(th)))
    res("5 급이 높이", face[0] + 0.5 <= mouth <= face[1] - 0.5 and zf + HORNET_H < CH["z_grid_bot"],
        "F %.0f → 바닥 %.0f, 입 %.0f, 솜 끝 %.1f~%.1f, 말벌 위 %.1f < 격자 %.0f" % (F_FEED, zf, mouth, face[0], face[1], zf + HORNET_H, CH["z_grid_bot"]))
    lift = face[1] - f["mouth_z"]
    res("6 빨아올림", lift <= 25.0, "물 → 솜 끝 위 %.1f mm (면 심지는 수 cm까지 [가능성 높음 — 실물 시험])" % lift)
    return ok_all


if __name__ == "__main__":
    f = load_fd()
    ok = check(f, "지금 값 (D5g_feeder_uln.py)")
    old = dict(f, tube_r=14.86, mouth_z=369.0, tip_y=16.0, tip_z=379.0, end_y=54.0, end_z=372.0, wall_hole_z=378.2)
    check(old, "참고: 11/06 승준 값 (50 mL, 물 369) — 실패해야 맞음")
    print("\n결과:", "모두 통과" if ok else "실패 있음")
    sys.exit(0 if ok else 1)
