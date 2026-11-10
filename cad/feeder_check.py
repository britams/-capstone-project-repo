# -*- coding: utf-8 -*-
"""급이 방 검사 — FreeCAD 없이 (서현, 2026-11-10, CAP-AI-56 → 11/10 밤 펌프 방식으로 다시, CAP-AI-59)

값은 cad/D5g_feeder_uln.py 의 FD 를 그대로 읽는다 (한 곳에서만 고침). 마킹실·바닥 치수는 D5e CH·FLOOR.
(11/10 밤) '거꾸로 병' → '바깥 병 + 연동 펌프가 먹일 때만 몇 방울 + 물빠짐'. 고인 물이 없어 열팽창 검사는 없앰.
검사 7개 (모두 통과해야 함):
  1 펌프 고장(명령 최대 시간 내내 돎) 때 나온 물 ≤ 물길이 넘침 높이까지 담는 양 (물빠짐이 막혀도)
  2 물빠짐 구멍이 바닥 높이에 있음 (고인 물이 바로 빠짐)
  3 노즐이 솜 바로 옆 (벽 안 면 ↔ 솜 틈 ≤ 1.5, 높이가 솜 축 ± 반지름 0.6 안)
  4 솜이 벽 구멍 안에 들어감
  5 솜이 마킹실 안으로 안 나옴 (바닥 0~36.5 올려도 겹침 0)
  6 급이 높이에서 말벌 입이 솜 끝 높이, 말벌이 격자에 안 눌림
  7 노즐 → 솜 끝 거리 ≤ 40 (면 심지가 젖어 가는 길) [가능성 높음 — 실물 시험]
실행: python cad/feeder_check.py
"""
import ast
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def load_fd():
    src = open(os.path.join(HERE, "D5g_feeder_uln.py"), encoding="utf-8").read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "FD":
            return {k.arg: ast.literal_eval(k.value) for k in node.value.keywords}
    raise SystemExit("FD 못 찾음")


def pump_limits():
    """펌웨어 trap_doors 의 PUMP 최대 시간(ms)과 Pi 한 번 양(ms)을 코드에서 읽음 — 숫자를 두 곳에 안 적으려고"""
    fw = open(os.path.join(REPO, "design", "circuit", "firmware", "trap_doors", "trap_doors.ino"), encoding="utf-8").read()
    mx = int(re.search(r"PUMP_MAX_MS\s*=\s*(\d+)", fw).group(1))
    pr = open(os.path.join(REPO, "관련코딩저장", "pi_link", "process.py"), encoding="utf-8").read()
    dose = float(re.search(r"feed_pump_ms:\s*float\s*=\s*([\d.]+)", pr).group(1))
    return mx, dose


CH = dict(cx=55.0, inner=40.0, wall=3.0, zc0=335.0, z_grid_bot=385.0)   # D5e_module_kinematic.py CH (마킹실 안 y −20~20, 벽 20~23)
FLOOR = dict(t=6.0, clear=0.5, stroke=36.5, top_rest=341.0)
HORNET_H = 7.5          # D5e HORNET h
MOUTH_ABOVE_FLOOR = 3.0  # 말벌 입 높이 [추측 — 표본으로 확인]
F_FEED = 31.0           # 급이 높이 (바닥 리프트 mm) — 관련코딩저장/pi_link/process.py, design/control_sim/trap_sim.py 와 같아야 함
FLOW = 100.0 * 5.0 / 6.0  # mL/min: Adafruit 3910 최대 100 (6 V) → 5 V 레일에서 약 5/6 [추측 — 실측으로 바꿈]


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


def overflow_z(f):
    """넘침 높이 = min(마킹실 벽 구멍 아래 끝, 물길 앞벽 솜 구멍 아래 끝)"""
    hb = f["wall_hole_z"] - f["wall_hole_r"]
    yb = f["ch_y0"] + f["front_t"]
    th = math.atan2(f["tip_z"] - f["end_z"], f["end_y"] - f["tip_y"])
    zc = f["tip_z"] - (yb - f["tip_y"]) * math.tan(th)
    return min(hb, zc - f["front_hole_r"] / math.cos(th))


def trough_volume(f, z_top, h=0.25):
    """물길 안(앞벽 뒤 ~ 끝 벽 앞) 바닥 윗면 → z_top 사이 빈 부피 (솜 빼고) mm³"""
    t, u, L = roll_geom(f)
    y0, y1 = f["ch_y0"] + f["front_t"], f["ch_y1"] - f["ch_t"]
    z0 = f["floor_z"] + f["floor_t"]
    n = 0
    x = f["x"] - f["ch_w"] / 2 + h / 2
    while x < f["x"] + f["ch_w"] / 2:
        y = y0 + h / 2
        while y < y1:
            z = z0 + h / 2
            while z < z_top:
                if not in_roll((x, y, z), t, u, L, f["roll_r"]):
                    n += 1
                z += h
            y += h
        x += h
    return n * h ** 3


def check(f, label):
    ok_all = True
    t, u, L = roll_geom(f)
    th = math.degrees(math.asin((f["tip_z"] - f["end_z"]) / L))
    print("\n== %s ==  솜 기울기 %.1f°, 솜 길이 %.2f" % (label, th, L))

    def res(name, ok, txt):
        nonlocal ok_all
        ok_all &= ok
        print("  [%s] %s — %s" % ("통과" if ok else "실패", name, txt))
    mx, dose = pump_limits()
    zo = overflow_z(f)
    vol = trough_volume(f, zo - 0.5) / 1000.0
    worst = FLOW * mx / 60000.0 * 6 / 5            # 6 V 최대 유량으로 넉넉히
    res("1 펌프 고장", worst <= vol, "명령 최대 %d ms × 최대 100 mL/min = %.2f mL ≤ 물길이 넘침 높이 %.1f − 0.5까지 담는 양 %.2f mL (물빠짐 막혀도)" % (mx, worst, zo, vol))
    res("2 물빠짐", f["ch_y0"] + f["front_t"] < f["dr_y"] < f["ch_y1"] - f["ch_t"], "바닥 끝 y %.0f, 구멍 Ø2가 바닥 윗면 %.0f에서 아래로 (고인 물 → 프레임 밖)" % (f["dr_y"], f["floor_z"] + f["floor_t"]))
    s = (f["nz_y"] - t[1]) / u[1]
    za = t[2] + s * u[2]
    gap = (f["x"] + f["ch_w"] / 2) - (f["x"] + f["roll_r"])
    res("3 노즐 → 솜", gap <= 1.5 and abs(f["nz_z"] - za) <= 0.6 * f["roll_r"], "노즐 y %.0f z %.1f, 그 자리 솜 축 z %.1f (차 %.1f), 벽 안 면 ↔ 솜 틈 %.1f" % (f["nz_y"], f["nz_z"], za, f["nz_z"] - za, gap))
    need = 2 * f["roll_r"] / math.cos(math.radians(th)) + CH["wall"] * math.tan(math.radians(th))
    res("4 벽 구멍", need <= 2 * f["wall_hole_r"] + 0.2, "필요 높이 %.2f vs 구멍 Ø%.1f" % (need, 2 * f["wall_hole_r"]))
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
    res("5 바닥과 솜", not hits, "솜 안 끝 가장 안쪽 y %.2f (벽 안 면 %.0f, 바닥 끝 %.1f), 겹침 %s" % (yi, y_in, fe, hits[:3] if hits else "0"))
    zf = FLOOR["top_rest"] + F_FEED; mouth = zf + MOUTH_ABOVE_FLOOR
    face = (f["tip_z"] - f["roll_r"] / math.cos(math.radians(th)), f["tip_z"] + f["roll_r"] / math.cos(math.radians(th)))
    res("6 급이 높이", face[0] + 0.5 <= mouth <= face[1] - 0.5 and zf + HORNET_H < CH["z_grid_bot"],
        "F %.0f → 바닥 %.0f, 입 %.0f, 솜 끝 %.1f~%.1f, 말벌 위 %.1f < 격자 %.0f" % (F_FEED, zf, mouth, face[0], face[1], zf + HORNET_H, CH["z_grid_bot"]))
    res("7 젖어 가는 길", s <= 40.0, "노즐 자리 → 솜 끝 %.1f mm (면 심지 [가능성 높음 — 실물 시험])" % s)
    print("      한 번 양: %.0f ms × %.0f mL/min (5 V 추정) = %.2f mL [추측 — 실측으로 맞춤]" % (dose, FLOW, FLOW * dose / 60000.0))
    return ok_all


if __name__ == "__main__":
    ok = check(load_fd(), "지금 값 (D5g_feeder_uln.py)")
    print("\n결과:", "모두 통과" if ok else "실패 있음")
    sys.exit(0 if ok else 1)
